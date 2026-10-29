"""Atomic mock-only requirement issuance, never paper or real provider I/O."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from photobooth.checkout_store import CheckoutStore, CheckoutConflict, CheckoutMissing
from photobooth.delivery_requirements import DeliveryRequirements
from photobooth.fulfillment_contract import frozen_contract

POLICY='PRINT_REQUIRED_V1'


class RequirementIssuanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'orders.sqlite'
        self.store=CheckoutStore(self.path);self.addCleanup(self.store.close)
        self.contract=frozen_contract({'template_a':2})

    def begin(self, store=None, **overrides):
        args=dict(creation_context=('MERCHANT','mock'),frozen_contract=self.contract,
                  delivery_policy=POLICY,customer_capability_hash='c'*64)
        args.update(overrides)
        return (store or self.store).begin('PB001',{'template_a':2},15000,'k'*32,**args)

    def counts(self):
        return [self.store.db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in
                ('checkouts','checkout_frozen_orders','checkout_create_attempts','checkout_customer_capabilities')]

    def test_new_order_freezes_original_copies_before_any_send_and_replays_exactly(self):
        order,first=self.begin();self.assertTrue(first)
        before=[tuple(r) for r in self.store.db.execute('SELECT * FROM checkout_frozen_orders')]
        requirement=DeliveryRequirements(self.store).get(order['id'],'PB001','MERCHANT')
        self.assertEqual(requirement['copies'],{'template_a':2})
        self.assertEqual(self.counts(),[1,1,1,1])
        with closing(CheckoutStore(self.path)) as second:
            replay,first=self.begin(second)
            self.assertFalse(first);self.assertEqual(replay,order)
            self.assertEqual(DeliveryRequirements(second).get(order['id'],'PB001','MERCHANT'),requirement)
        self.assertEqual([tuple(r) for r in self.store.db.execute('SELECT * FROM checkout_frozen_orders')],before)

    def test_policy_omission_change_or_wrong_merchant_cannot_rebind_an_order(self):
        order,_=self.begin();before=dict(order)
        for overrides in ({'delivery_policy':None},{'delivery_policy':'OTHER'},
                          {'creation_context':('OTHER','mock')}):
            with self.subTest(overrides=overrides),self.assertRaises((CheckoutConflict,CheckoutMissing,ValueError)):
                self.begin(**overrides)
        self.assertEqual(self.store.get(order['id']),before)
        self.assertEqual(self.counts(),[1,1,1,1])

    def test_legacy_order_cannot_gain_policy_and_default_does_not_initialize_table(self):
        order,_=self.begin(delivery_policy=None)
        self.assertIsNone(self.store.db.execute("SELECT name FROM sqlite_master WHERE name='checkout_delivery_requirements'").fetchone())
        with self.assertRaises(CheckoutConflict):self.begin()
        self.assertEqual(self.store.get(order['id']),order)
        self.assertIsNone(DeliveryRequirements(self.store).get(order['id'],'PB001','MERCHANT'))

    def test_sandbox_missing_contract_and_invalid_policy_reject_before_new_order(self):
        for args in ({'creation_context':('MERCHANT','sandbox')},{'frozen_contract':None},
                     {'creation_context':None},{'delivery_policy':True},{'customer_capability_hash':None}):
            with self.subTest(args=args),self.assertRaises(ValueError):self.begin(**args)
        self.assertEqual(self.counts(),[0,0,0,0])

    def test_sql_failure_rolls_back_order_frozen_attempt_and_capability(self):
        DeliveryRequirements(self.store)
        self.store.db.execute("CREATE TRIGGER fail_requirement BEFORE INSERT ON checkout_delivery_requirements BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.begin()
        self.assertEqual(self.counts(),[0,0,0,0])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkout_delivery_requirements').fetchone()[0],0)

    def test_invalid_frozen_delivery_shape_rolls_back_without_partial_identity(self):
        for field,value in [('version',2),('print_copy_count',3),('templates',[])]:
            contract=json.loads(json.dumps(self.contract));contract[field]=value
            with self.subTest(field=field),self.assertRaises(CheckoutConflict):
                self.begin(frozen_contract=contract)
            self.assertEqual(self.counts(),[0,0,0,0])

    def test_concurrent_connections_issue_one_original_requirement(self):
        with closing(CheckoutStore(self.path)) as second,ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(self.begin,[self.store,second]))
        self.assertEqual(sum(first for _,first in results),1)
        self.assertEqual(len({order['id'] for order,_ in results}),1)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkout_delivery_requirements').fetchone()[0],1)

    def test_real_child_exit_before_commit_rolls_back_and_after_commit_replays(self):
        script='''import os,sys
from photobooth.checkout_store import CheckoutStore
from photobooth.delivery_requirements import DeliveryRequirements
from photobooth.fulfillment_contract import frozen_contract
s=CheckoutStore(sys.argv[1])
if sys.argv[2]=='before':
 original=DeliveryRequirements._freeze_new
 def stop(self,*args):
  original(self,*args)
  os._exit(91)
 DeliveryRequirements._freeze_new=stop
s.begin('PB001',{'template_a':2},15000,'k'*32,creation_context=('MERCHANT','mock'),frozen_contract=frozen_contract({'template_a':2}),delivery_policy='PRINT_REQUIRED_V1',customer_capability_hash='c'*64)
os._exit(92)
'''
        for stage,code in [('before',91),('after',92)]:
            result=subprocess.run([sys.executable,'-c',script,str(self.path),stage],capture_output=True,timeout=20)
            self.assertEqual(result.returncode,code,result.stderr.decode(errors='replace'))
            self.assertEqual(self.counts(),[0,0,0,0] if stage=='before' else [1,1,1,1])
        order,first=self.begin();self.assertFalse(first)
        self.assertEqual(DeliveryRequirements(self.store).get(order['id'],'PB001','MERCHANT')['copies'],{'template_a':2})
