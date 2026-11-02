"""Offline, no-device assertions for the read-only PP-07 pilot preflight."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.check_post_preview_pilot import inspect


class PilotPreflightTest(unittest.TestCase):
    def test_missing_checkout_files_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch("tools.check_post_preview_pilot.subprocess.run") as run:
                run.return_value.returncode = 0
                run.return_value.stdout = "feature/post-preview-qris-checkout\n"
                result = inspect(Path(temp), check_imports=False)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any(c["name"].startswith("File:") and c["status"] == "BLOCKED"
                            for c in result["checks"]))

    def test_wrong_branch_is_blocked_even_if_files_exist(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            required = (
                "tools/run_post_preview_checkout_pilot.py",
                "requirements.txt",
                "requirements-post-preview.txt",
                "requirements-qris.txt",
                "docs/qa/portrait-v2-sandbox/PP07-SUPERVISED-WINDOWS-UAT.md",
            )
            for relative in required:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf8")
            with patch("tools.check_post_preview_pilot.subprocess.run") as run:
                run.return_value.returncode = 0
                run.return_value.stdout = "master\n"
                result = inspect(root, check_imports=False)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(next(c for c in result["checks"]
                              if c["name"] == "Authorized branch")["status"], "BLOCKED")


    def test_missing_checkout_dependency_is_not_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch("tools.check_post_preview_pilot.importlib.util.find_spec",
                       side_effect=lambda name: None if name == "fastapi" else object()):
                result = inspect(Path(temp), check_imports=True)
        check = next(c for c in result["checks"] if c["name"] == "Dependency: fastapi")
        self.assertEqual(check["status"], "BLOCKED")
        self.assertEqual(result["status"], "BLOCKED")

    def test_conflicting_paid_first_or_real_delivery_flag_is_blocked(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict("os.environ", {"PHOTOBOOTH_V2_CHECKOUT_SANDBOX": "1"}):
                result = inspect(Path(temp), check_imports=False)
        check = next(c for c in result["checks"]
                     if c["name"] == "Isolated synthetic launch profile")
        self.assertEqual(check["status"], "BLOCKED")
        self.assertIn("PHOTOBOOTH_V2_CHECKOUT_SANDBOX", check["detail"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_complete_source_and_dependencies_can_be_ready(self):
        from tools.check_post_preview_pilot import REQUIRED_FILES, CONFLICTING_PROFILES
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in REQUIRED_FILES:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf8")
            with patch.dict("os.environ", {flag: "0" for flag in CONFLICTING_PROFILES}):
                with patch("tools.check_post_preview_pilot.subprocess.run") as run:
                    run.return_value.returncode = 0
                    run.return_value.stdout = "feature/post-preview-qris-checkout\n"
                    with patch("tools.check_post_preview_pilot.importlib.util.find_spec",
                               return_value=object()):
                        result = inspect(root, check_imports=True)
        self.assertEqual(result["status"], "READY_FOR_SUPERVISED_SYNTHETIC_PILOT")
        self.assertTrue(all(c["status"] == "PASS" for c in result["checks"]))


if __name__ == "__main__":
    unittest.main()
