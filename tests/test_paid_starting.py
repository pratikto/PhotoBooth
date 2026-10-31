"""Live original-allocation retry remains fenced, fresh and idempotent."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from tests.qris_v2_fixture import Fixture

class StartingRetryTests(TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.f=Fixture(Path(self.tmp.name));self.addCleanup(self.f.close)
        self.f.flow.qr_renewal_enabled=True;self.f.service.begin({'template_a':2})
        self.f.paid();self.f.service.check();self.f.service.print_recovery_receipt()
        self.oid=self.f.flow.snapshot()['order']['order_id']

    def interrupted(self,after=False):
        original=self.f.flow.client.allocate
        def lost(*args):
            if after:original(*args)
            raise RuntimeError('Synthetic allocation reply loss')
        with patch.object(self.f.flow.client,'allocate',side_effect=lost):
            with self.assertRaises(RuntimeError):self.f.flow.prepare_capture()
        return self.f.flow.snapshot()

    def assert_original_retry(self,after):
        before=self.interrupted(after);operation=before['allocation_operation_id']
        remote=self.f.store.fulfillment(self.oid,'PB001')['transaction_id']
        with patch.object(self.f.flow.client,'allocate',wraps=self.f.flow.client.allocate) as allocate:
            view=self.f.flow.refresh();allocate.assert_called_once_with(self.oid,before['order']['grant_id'],operation)
        self.assertEqual(view['phase'],'STARTING');self.assertFalse(view['allocation_ready'])
        self.assertEqual(view['transaction_id'],view['order']['fulfillment']['transaction_id'])
        if after:self.assertEqual(view['transaction_id'],remote)
        self.assertEqual(self.f.provider.charges,1)
        self.assertEqual(self.f.store.db.execute('SELECT count(*) FROM checkout_fulfillments').fetchone()[0],1)
        with patch.object(self.f.flow.client,'allocate') as allocate:
            again=self.f.flow.refresh();allocate.assert_not_called()
        self.assertEqual(again['transaction_id'],view['transaction_id'])

    def test_before_accept_retry_reuses_original_operation_and_allocation(self):
        self.assert_original_retry(False)

    def test_after_commit_retry_recovers_same_transaction_without_second_allocation(self):
        self.assert_original_retry(True)

    def test_missing_original_operation_cannot_invent_a_replacement_allocation(self):
        self.interrupted();self.f.flow.data.pop('allocation_operation_id');self.f.flow._save()
        with patch.object(self.f.flow.client,'allocate') as allocate:
            view=self.f.flow.refresh();allocate.assert_not_called()
        self.assertEqual(view['phase'],'STARTING');self.assertIsNone(view['transaction_id'])
        self.assertEqual(self.f.provider.charges,1)

    def test_outage_or_refund_cannot_allocate_from_cached_paid(self):
        before=self.interrupted();operation=before['allocation_operation_id']
        self.f.provider.outage=True
        with self.assertRaises(RuntimeError):self.f.flow.refresh()
        self.assertIsNone(self.f.flow.snapshot()['transaction_id'])
        self.f.provider.outage=False;self.f.provider.rows[self.oid]['transaction_status']='refund'
        with self.assertRaises(RuntimeError):self.f.flow.refresh()
        self.assertIsNone(self.f.flow.snapshot()['transaction_id'])
        self.assertEqual(self.f.flow.snapshot()['allocation_operation_id'],operation)
        self.assertEqual(self.f.provider.charges,1)
        self.assertEqual(self.f.store.fulfillment(self.oid,'PB001')['obligation_state'],'OWED')

    def test_privacy_lock_prevents_retry_and_retires_late_allocation_reply(self):
        self.interrupted();original=self.f.flow.client.allocate
        def retired(*args):
            result=original(*args);self.f.flow.lock_customer();return result
        with patch.object(self.f.flow.client,'allocate',side_effect=retired):
            with self.assertRaises(RuntimeError):self.f.flow.refresh()
        self.assertTrue(self.f.flow.customer_claim_required)
        self.assertIsNone(self.f.flow.snapshot()['transaction_id'])
        with patch.object(self.f.flow.client,'allocate') as allocate:
            self.f.flow.refresh();allocate.assert_not_called()
        self.assertEqual(self.f.provider.charges,1)
