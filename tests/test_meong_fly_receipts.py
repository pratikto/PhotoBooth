import tempfile
import unittest
from pathlib import Path
from photobooth.meong_fly_receipts import DemoReceiptLedger


class ReceiptTests(unittest.TestCase):
    def test_single_use_persists_across_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "attempts.sqlite3"
            first = DemoReceiptLedger(path)
            self.assertTrue(first.claim("DEMO-ABC"))
            first.finish("DEMO-ABC", False)
            self.assertFalse(DemoReceiptLedger(path).claim("DEMO-ABC"))

    def test_invalid_codes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = DemoReceiptLedger(Path(tmp) / "attempts.sqlite3")
            for value in ("", "CAFE-1", "DEMO-" + "x"*200):
                self.assertFalse(ledger.claim(value))


if __name__ == "__main__":
    unittest.main()
