"""Regression tests for FEAT-021 demo receipt input and canvas layering.

Static checks run without Kivy. Interactive widget checks run when Kivy and its
window provider are installed (for example on the owner's Windows machine).
"""
import ast
import importlib.util
import tempfile
import unittest
from pathlib import Path

from photobooth.meong_fly_painter import ACTIONS, DEMO_ENTRY


SOURCE = Path(__file__).resolve().parents[1] / "photobooth" / "meong_fly_gui.py"


class DemoInputLayoutTests(unittest.TestCase):
    def test_input_does_not_overlap_scan_buttons(self):
        x, y, w, h = DEMO_ENTRY
        for action, (bx, by, bw, bh) in ACTIONS["scan"].items():
            with self.subTest(action=action):
                overlap = (x < bx + bw and bx < x + w
                           and y < by + bh and by < y + h)
                self.assertFalse(overlap)

    def test_refresh_does_not_delete_child_canvases(self):
        """Guard against clearing TextInput's text/caret with the stage canvas."""
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        stage = next(node for node in tree.body
                     if isinstance(node, ast.ClassDef)
                     and node.name == "MeongFlyStage")
        refresh = next(node for node in stage.body
                       if isinstance(node, ast.FunctionDef)
                       and node.name == "_refresh")
        calls = [ast.unparse(node.func) for node in ast.walk(refresh)
                 if isinstance(node, ast.Call)]
        self.assertIn("self.canvas.before.clear", calls)
        self.assertNotIn("self.canvas.clear", calls)


@unittest.skipUnless(importlib.util.find_spec("kivy"), "Kivy not installed")
class KivyDemoInputTests(unittest.TestCase):
    """Execute with the real Kivy window provider on Windows."""

    def setUp(self):
        from photobooth.meong_fly_flow import MeongFlyFlow
        from photobooth.meong_fly_gui import MeongFlyStage
        from photobooth.meong_fly_receipts import DemoReceiptLedger

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.flow = MeongFlyFlow(
            DemoReceiptLedger(Path(self.tmp.name) / "receipts.sqlite3")
        )
        self.stage = MeongFlyStage(self.flow, size=(450, 900),
                                   size_hint=(None, None))
        self.addCleanup(self._unschedule)
        self.flow.open_scan()
        self.stage._refresh()

    def _unschedule(self):
        from kivy.clock import Clock
        Clock.unschedule(self.stage.update)

    def test_scan_input_canvas_survives_refresh(self):
        """Text/caret drawing instructions stay parented after every redraw."""
        self.assertFalse(self.stage.receipt.disabled)
        self.assertEqual(self.stage.receipt.opacity, 1)
        self.assertIn(self.stage.receipt.canvas, self.stage.canvas.children)
        self.stage._refresh()
        self.assertIn(self.stage.receipt.canvas, self.stage.canvas.children)

    def test_typed_demo_code_survives_refresh_and_starts_game(self):
        self.stage.receipt.text = "DEMO-INPUT-001"
        self.stage._refresh()
        self.assertEqual(self.stage.receipt.text, "DEMO-INPUT-001")
        self.stage.validate_receipt()
        self.assertEqual(self.flow.screen, "game")
        self.assertEqual(self.flow.active_receipt, "DEMO-INPUT-001")

    def test_visible_input_position_matches_touch_hitbox(self):
        self.stage.pos = (0, 0)
        self.stage.size = (450, 900)
        self.stage._resize()
        (x, y), (w, h) = self.stage._rect(DEMO_ENTRY)
        self.assertAlmostEqual(self.stage.receipt.x, x)
        self.assertAlmostEqual(self.stage.receipt.y, y)
        self.assertAlmostEqual(self.stage.receipt.width, w)
        self.assertAlmostEqual(self.stage.receipt.height, h)
        self.assertTrue(self.stage.receipt.collide_point(x + w / 2,
                                                         y + h / 2))


if __name__ == "__main__":
    unittest.main()
