"""FEAT-020 sandbox order state tests; no real payment involved."""
import tempfile
import unittest
from pathlib import Path
from photobooth.payment_orders import OrderStore


class OrderStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'orders.sqlite'
        self.store = OrderStore(self.path)
        self.order = self.store.create('PB001', {'template_a': 2}, 15000)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_unpaid_cannot_claim(self):
        self.assertFalse(self.store.claim(self.order, 'PB001'))

    def test_settlement_once(self):
        self.store.attach_provider(self.order, 'sandbox-1')
        self.assertTrue(self.store.confirm_provider_status(self.order, 'sandbox-1', 15000, 'settlement'))
        self.assertTrue(self.store.confirm_provider_status(self.order, 'sandbox-1', 15000, 'settlement'))
        self.assertTrue(self.store.claim(self.order, 'PB001'))
        self.assertFalse(self.store.claim(self.order, 'PB001'))

    def test_wrong_amount_or_reference_rejected(self):
        self.store.attach_provider(self.order, 'sandbox-1')
        self.assertFalse(self.store.confirm_provider_status(self.order, 'sandbox-1', 10000, 'settlement'))
        self.assertFalse(self.store.confirm_provider_status(self.order, 'wrong', 15000, 'settlement'))
        self.assertFalse(self.store.confirm_provider_status(self.order, 'sandbox-1', 15000, 'pending'))

    def test_other_booth_cannot_claim_or_read(self):
        self.store.attach_provider(self.order, 'sandbox-1')
        self.store.confirm_provider_status(self.order, 'sandbox-1', 15000, 'settlement')
        self.assertFalse(self.store.claim(self.order, 'PB002'))
        self.assertIsNone(self.store.status(self.order, 'PB002'))

    def test_restart_preserves_claim(self):
        self.store.attach_provider(self.order, 'sandbox-1')
        self.store.confirm_provider_status(self.order, 'sandbox-1', 15000, 'settlement')
        self.assertTrue(self.store.claim(self.order, 'PB001'))
        self.store.close()
        self.store = OrderStore(self.path)
        self.assertFalse(self.store.claim(self.order, 'PB001'))

    def test_cannot_replace_provider_reference(self):
        self.store.attach_provider(self.order, 'sandbox-1')
        with self.assertRaises(RuntimeError):
            self.store.attach_provider(self.order, 'sandbox-2')


if __name__ == '__main__':
    unittest.main()
