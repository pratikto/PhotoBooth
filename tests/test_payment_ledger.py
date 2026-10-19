"""Mock-only FEAT-020 regression: no provider, funds or QRIS involved."""
import tempfile
import unittest
from pathlib import Path
from photobooth.payment_ledger import PaymentLedger


class PaymentLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'ledger.sqlite'
        self.ledger = PaymentLedger(self.path)

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def test_unverified_cannot_credit_order(self):
        with self.assertRaises(PermissionError):
            self.ledger.record_verified('PB001', 15000, 'mock-1')
        self.assertFalse(self.ledger.claim_session('PB001'))

    def test_verified_order_claims_once(self):
        self.assertTrue(self.ledger.record_verified('PB001', 15000, 'mock-1', verified=True))
        self.assertFalse(self.ledger.record_verified('PB001', 15000, 'mock-1', verified=True))
        self.assertTrue(self.ledger.claim_session('PB001'))
        self.assertFalse(self.ledger.claim_session('PB001'))

    def test_conflicting_evidence_rejected(self):
        self.ledger.record_verified('PB001', 15000, 'mock-1', verified=True)
        with self.assertRaises(ValueError):
            self.ledger.record_verified('PB001', 20000, 'mock-1', verified=True)
        with self.assertRaises(Exception):
            self.ledger.record_verified('PB002', 15000, 'mock-1', verified=True)

    def test_restart_preserves_claim(self):
        self.ledger.record_verified('PB001', 15000, 'mock-1', verified=True)
        self.assertTrue(self.ledger.claim_session('PB001'))
        self.ledger.close()
        self.ledger = PaymentLedger(self.path)
        self.assertFalse(self.ledger.claim_session('PB001'))

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.ledger.record_verified('PB001', 0, 'mock-1', verified=True)


if __name__ == '__main__':
    unittest.main()
