"""Disposable schema/identity fixtures; no delivery issuer or transport."""
from contextlib import closing
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from photobooth.checkout_store import CheckoutStore, CheckoutConflict, CheckoutMissing
from photobooth.fulfillment_contract import frozen_contract


class DeliveryRequirementTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'orders.sqlite'
        self.store=CheckoutStore(self.path);self.addCleanup(self.store.close)
        self.contract=frozen_contract({'template_a':2})
        self.order,_=self.store.begin('PB001',{'template_a':2},15000,'a'*32,
            creation_context=('MERCHANT','sandbox'),frozen_contract=self.contract)

    def adapter(self):
        from photobooth.delivery_requirements import DeliveryRequirements
        return DeliveryRequirements(self.store)

    def snapshot(self):
        return {name:[tuple(r) for r in self.store.db.execute('SELECT * FROM '+name)]
                for name in ('checkouts','checkout_create_attempts','checkout_frozen_orders',
                             'checkout_fulfillments','checkout_events')}

    def seed(self):
        digest=self.store.db.execute('SELECT contract_hash FROM checkout_frozen_orders').fetchone()[0]
        self.store.db.execute('INSERT INTO checkout_delivery_requirements VALUES(?,?,?,?,?,?,?,?,?)',
            (self.order['id'],'requirement-1',1,'PRINT_REQUIRED_V1','PB001','MERCHANT',digest,
             json.dumps({'template_a':2}),100))

    def test_explicit_migration_preserves_all_original_rows_and_absence_is_unspecified(self):
        self.assertIsNone(self.store.db.execute("SELECT name FROM sqlite_master WHERE name='checkout_delivery_requirements'").fetchone())
        before=self.snapshot();adapter=self.adapter()
        self.assertEqual(self.snapshot(),before)
        self.assertIsNone(adapter.get(self.order['id'],'PB001','MERCHANT'))
        self.assertEqual(self.snapshot(),before)

    def test_seeded_requirement_reopens_with_same_identity_copies_and_original_bytes(self):
        adapter=self.adapter();self.seed();before=self.snapshot()
        first=adapter.get(self.order['id'],'PB001','MERCHANT')
        self.assertEqual(first['copies'],{'template_a':2})
        with closing(CheckoutStore(self.path)) as second:
            from photobooth.delivery_requirements import DeliveryRequirements
            self.assertEqual(DeliveryRequirements(second).get(self.order['id'],'PB001','MERCHANT'),first)
        self.assertEqual(self.snapshot(),before)

    def test_wrong_tenant_never_discloses_requirement(self):
        adapter=self.adapter();self.seed()
        for booth,merchant in [('OTHER','MERCHANT'),('PB001','OTHER')]:
            with self.subTest(booth=booth,merchant=merchant),self.assertRaises(CheckoutMissing):
                adapter.get(self.order['id'],booth,merchant)

    def test_tampered_binding_copies_or_frozen_bytes_hold_without_financial_mutation(self):
        adapter=self.adapter();self.seed();before=self.snapshot()
        for column,value in [('copies_json','{"template_a":true}'),('copies_json','{"template_a":3}'),
                             ('copies_json','invalid'),('contract_hash','bad'),('booth_id','OTHER'),
                             ('merchant_id','OTHER')]:
            with self.subTest(column=column):
                old=self.store.db.execute('SELECT '+column+' FROM checkout_delivery_requirements').fetchone()[0]
                self.store.db.execute('UPDATE checkout_delivery_requirements SET '+column+'=?',(value,))
                with self.assertRaises(CheckoutConflict):adapter.get(self.order['id'],'PB001','MERCHANT')
                self.store.db.execute('UPDATE checkout_delivery_requirements SET '+column+'=?',(old,))
        self.assertEqual(self.snapshot(),before)
        self.store.db.execute("UPDATE checkout_frozen_orders SET contract_json='{}'")
        with self.assertRaises(CheckoutConflict):adapter.get(self.order['id'],'PB001','MERCHANT')

    def test_existing_paid_owed_order_is_not_backfilled_or_satisfied(self):
        self.store.apply_evidence(self.order['id'],dict(order_id=self.order['id'],amount=15000,
            merchant_id='MERCHANT',transaction_id='provider-ref',transaction_status='settlement'))
        before=self.snapshot();adapter=self.adapter()
        self.assertIsNone(adapter.get(self.order['id'],'PB001','MERCHANT'))
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(self.store.fulfillment(self.order['id'],'PB001')['obligation_state'],'OWED')

    def test_conflicting_record_rolls_back_without_replacing_original(self):
        adapter=self.adapter();self.seed();original=adapter.get(self.order['id'],'PB001','MERCHANT')
        before=self.snapshot()
        with self.assertRaises(sqlite3.IntegrityError),self.store.write():
            self.seed()
        self.assertEqual(adapter.get(self.order['id'],'PB001','MERCHANT'),original)
        self.assertEqual(self.snapshot(),before)
