"""Safety regression: invalid pilot roots fail before Kivy/device imports."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.run_post_preview_checkout_pilot import main


class PilotEarlyRootValidationTest(unittest.TestCase):
    def test_reused_occupied_root_refused_without_runtime_import(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "used"
            root.mkdir()
            (root / "original-customer-ledger.sqlite").write_text("preserve", encoding="utf8")
            with patch.dict("os.environ", {
                "PHOTOBOOTH_V2_CHECKOUT_SANDBOX": "0",
                "PHOTOBOOTH_V2_CHECKOUT_MOCK": "0",
                "PHOTOBOOTH_V2_PRINT": "0",
                "PHOTOBOOTH_V2_DRIVE": "0",
            }):
                with self.assertRaises(SystemExit) as result:
                    main(["--private-root", str(root), "--synthetic-payment-only"])
            self.assertEqual(result.exception.code, 2)
            self.assertEqual((root / "original-customer-ledger.sqlite").read_text(encoding="utf8"),
                             "preserve")

    def test_regular_file_root_refused_before_runtime_import(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "not-a-folder"
            root.write_text("do not replace", encoding="utf8")
            with patch.dict("os.environ", {
                "PHOTOBOOTH_V2_CHECKOUT_SANDBOX": "0",
                "PHOTOBOOTH_V2_CHECKOUT_MOCK": "0",
                "PHOTOBOOTH_V2_PRINT": "0",
                "PHOTOBOOTH_V2_DRIVE": "0",
            }):
                with self.assertRaises(SystemExit) as result:
                    main(["--private-root", str(root), "--synthetic-payment-only"])
            self.assertEqual(result.exception.code, 2)
            self.assertEqual(root.read_text(encoding="utf8"), "do not replace")


if __name__ == "__main__":
    unittest.main()
