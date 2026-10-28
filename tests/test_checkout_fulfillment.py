"""AR-03 payment obligation and unique immutable fulfillment/allocation mapping."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import tempfile
import unittest

from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore, CheckoutConflict
from tests.test_checkout_backend import FakeProvider, KEY, MERCHANT


class FulfillmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'orders.sqlite'
        self.store=CheckoutStore(self.path);self.addCleanup(self.store.close)
        self.provider=FakeProvider();self.backend=CheckoutBackend(self.store,self.provider,KEY,MERCHANT)
        self.key='a'*32
        self.oid=self.backend.create_order('PB001',{'template_a':2},self.key)['order_id']

    def paid(self):
        self.provider.rows[self.oid].update(transaction_status='settlement',status_code='200')
        self.backend._apply(self.store.get(self.oid),self.provider.get_status(self.oid))

    def test_order_contract_is_frozen_before_provider_call_and_cannot_be_rewritten(self):
        contract=self.store.frozen_order(self.oid)
        self.assertEqual(contract['quantities'],{'template_a':2})
        self.assertEqual(contract['amount'],15000)
        self.assertEqual(len(contract['templates']),1)
        self.assertEqual(len(contract['templates'][0]['artwork_sha256']),64)
        self.assertEqual(len(contract['templates'][0]['apertures']),3)
        before=self.store.db.execute('SELECT contract_json,contract_hash FROM checkout_frozen_orders WHERE order_id=?',(self.oid,)).fetchone()
        self.backend.create_order('PB001',{'template_a':2},self.key)
        after=self.store.db.execute('SELECT contract_json,contract_hash FROM checkout_frozen_orders WHERE order_id=?',(self.oid,)).fetchone()
        self.assertEqual(tuple(before),tuple(after))

    def test_lost_claim_response_and_concurrent_replay_keep_one_fulfillment(self):
        self.paid()
        with closing(CheckoutStore(self.path)) as second,ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda s:s.grant(self.oid,'PB001',self.key),(self.store,second)))
        self.assertEqual(results[0]['grant_id'],results[1]['grant_id'])
        one=self.store.fulfillment(self.oid,'PB001')
        with closing(CheckoutStore(self.path)) as reopened:
            self.assertEqual(reopened.fulfillment(self.oid,'PB001'),one)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkout_fulfillments').fetchone()[0],1)
        self.assertEqual(one['obligation_state'],'OWED')

    def test_abandon_preserves_paid_obligation_and_no_fabricated_refund(self):
        self.paid();self.backend.claim(self.oid,'PB001',self.key)
        self.store.recovery_action(self.oid,'PB001','b'*32,'abandon','Synthetic test end',None,'operator')
        record=self.store.fulfillment(self.oid,'PB001')
        self.assertEqual(record['obligation_state'],'OWED')
        self.assertEqual(self.store.get(self.oid)['state'],'PAID')

    def test_composition_ack_does_not_silently_satisfy_service_obligation(self):
        self.paid();grant=self.backend.claim(self.oid,'PB001',self.key)['grant_id']
        self.store.service_transition(self.oid,'PB001',grant,'STARTED','PB001_00000001')
        self.store.service_transition(self.oid,'PB001',grant,'COMPLETED','PB001_00000001')
        record=self.store.fulfillment(self.oid,'PB001')
        self.assertEqual(record['obligation_state'],'OWED')
        self.assertEqual(record['state'],'COMPOSED')

    def test_migration_preserves_legacy_grant_bytes_and_marks_missing_snapshot_held(self):
        path=Path(self.tmp.name)/'legacy.sqlite'
        with closing(CheckoutStore(path)) as old:
            row,_=old.begin('PB001',{'template_a':2},15000,self.key)
            old.apply_evidence(row['id'],dict(order_id=row['id'],amount=15000,merchant_id=MERCHANT,
                                             transaction_id='legacy-ref',transaction_status='settlement'))
            old.grant(row['id'],'PB001',self.key)
            before=old.get(row['id'])
            old.db.execute('DROP TABLE checkout_fulfillments')
        with closing(CheckoutStore(path)) as upgraded:
            self.assertEqual(upgraded.get(row['id']),before)
            record=upgraded.fulfillment(row['id'],'PB001')
            self.assertEqual(record['state'],'LEGACY_REVIEW')
            self.assertEqual(record['obligation_state'],'OWED')
            self.assertIsNone(record['contract_hash'])

    def test_legacy_duplicate_local_binding_holds_both_orders_without_guessing_owner(self):
        self.paid();self.backend.claim(self.oid,'PB001',self.key)
        self.store.db.execute("UPDATE checkouts SET local_transaction_id='PB001_00000001',service_state='COMPLETED' WHERE id=?",(self.oid,))
        other,_=self.store.begin('PB002',{'template_a':2},15000,'c'*32)
        self.store.db.execute("UPDATE checkouts SET state='PAID',grant_id=?,local_transaction_id='PB001_00000001' WHERE id=?",('d'*32,other['id']))
        self.store.db.execute('DROP TABLE checkout_fulfillments')
        with closing(CheckoutStore(self.path)) as upgraded:
            for oid,booth in ((self.oid,'PB001'),(other['id'],'PB002')):
                record=upgraded.fulfillment(oid,booth)
                self.assertEqual(record['state'],'LEGACY_REVIEW')
                self.assertIsNone(record['transaction_id'])
                self.assertEqual(upgraded.get(oid)['local_transaction_id'],'PB001_00000001')
