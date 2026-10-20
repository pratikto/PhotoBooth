"""FEAT-021 standalone navigation and one-attempt regression tests."""

import tempfile
import unittest
from pathlib import Path

from photobooth.meong_fly_flow import MeongFlyFlow
from photobooth.meong_fly_receipts import DemoReceiptLedger


class MeongFlyFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "ledger.sqlite3"
        self.flow = MeongFlyFlow(DemoReceiptLedger(self.db))

    def test_start_scan_back_without_claim(self):
        self.assertEqual(self.flow.screen, "start")
        self.assertTrue(self.flow.open_scan())
        self.assertTrue(self.flow.back())
        self.assertTrue(self.flow.open_scan())
        self.assertTrue(self.flow.claim_and_start("DEMO-BACK"))
        self.assertEqual(self.flow.screen, "game")

    def test_direct_photo_exits_without_receipt(self):
        self.assertTrue(self.flow.direct_photo())
        self.assertEqual(self.flow.screen, "exit")
        self.assertFalse(self.flow.open_scan())

    def test_invalid_demo_code_does_not_claim(self):
        self.flow.open_scan()
        for code in ("", "CAFE-1", "DEMO-", "DEMO-" + "X" * 100):
            self.assertFalse(self.flow.claim_and_start(code))
        self.assertTrue(self.flow.claim_and_start("DEMO-VALID"))

    def test_reuse_after_relaunch_fails(self):
        self.flow.open_scan()
        self.assertTrue(self.flow.claim_and_start("DEMO-ONCE"))
        another = MeongFlyFlow(DemoReceiptLedger(self.db))
        another.open_scan()
        self.assertFalse(another.claim_and_start("DEMO-ONCE"))
        self.assertEqual(another.screen, "scan")

    def test_no_restart_or_back_once_claimed(self):
        self.flow.open_scan()
        self.flow.claim_and_start("DEMO-CLAIMED")
        self.assertFalse(self.flow.back())
        self.assertFalse(self.flow.open_scan())
        self.assertFalse(self.flow.claim_and_start("DEMO-OTHER"))

    def test_pause_freezes_simulation_and_blocks_flap(self):
        self.flow.open_scan()
        self.flow.claim_and_start("DEMO-PAUSE")
        t0 = self.flow.game.elapsed
        self.assertTrue(self.flow.toggle_pause())
        self.flow.tick(0.02)
        self.assertEqual(self.flow.game.elapsed, t0)
        self.assertFalse(self.flow.flap())
        self.assertTrue(self.flow.toggle_pause())
        self.flow.tick(0.02)
        self.assertGreater(self.flow.game.elapsed, t0)

    def test_win_saves_once_and_never_retries(self):
        self.flow.open_scan()
        self.flow.claim_and_start("DEMO-WIN")
        self.flow.game.status = "won"
        self.flow.tick(0.02)
        self.flow.tick(0.02)
        self.assertEqual(self.flow.screen, "won")
        self.assertTrue(self.flow.result_recorded)
        self.assertFalse(self.flow.open_scan())
        self.assertFalse(self.flow.flap())
        self.assertTrue(self.flow.continue_from_result())
        self.assertEqual(self.flow.screen, "exit")
        other = MeongFlyFlow(DemoReceiptLedger(self.db))
        other.open_scan()
        self.assertFalse(other.claim_and_start("DEMO-WIN"))

    def test_loss_never_has_second_attempt(self):
        self.flow.open_scan()
        self.flow.claim_and_start("DEMO-LOSS")
        self.flow.game.status = "lost"
        self.flow.tick(0.02)
        self.assertEqual(self.flow.screen, "lost")
        self.assertFalse(self.flow.toggle_pause())
        self.assertFalse(self.flow.back())
        self.assertTrue(self.flow.continue_from_result())

    def test_continue_not_allowed_before_terminal(self):
        self.assertFalse(self.flow.continue_from_result())
        self.flow.open_scan()
        self.assertFalse(self.flow.continue_from_result())

    def test_receipt_failure_does_not_call_game_start(self):
        self.flow.open_scan()
        self.assertFalse(self.flow.claim_and_start("DEMO-"))
        self.assertEqual(self.flow.game.status, "ready")


if __name__ == "__main__":
    unittest.main()
