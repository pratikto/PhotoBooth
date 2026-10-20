"""FEAT-021 Batch B rendering regressions, optional Kivy Windows checks."""
import ast
import importlib.util
import tempfile
import unittest
from pathlib import Path

from photobooth.meong_fly_game_art import (
    ROCK_VARIANTS, CAT_POSES, paint_game_background,
)
from photobooth.meong_fly import (
    CAT_BOTTOM, CAT_LEFT, CAT_X, PIPE_WIDTH, AsteroidGap,
)

SOURCE = Path(__file__).resolve().parents[1] / "photobooth" / "meong_fly_gui.py"


class GameRenderSourceTests(unittest.TestCase):
    def test_kivy_gameplay_does_not_upload_pillow_images_each_frame(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        stage = next(c for c in tree.body if isinstance(c, ast.ClassDef)
                     and c.name == "MeongFlyStage")
        draw_game = next(c for c in stage.body if isinstance(c, ast.FunctionDef)
                         and c.name == "_draw_game")
        calls = [ast.unparse(node.func) for node in ast.walk(draw_game)
                 if isinstance(node, ast.Call)]
        self.assertNotIn("Image.new", calls)
        self.assertNotIn("kivy_texture", calls)
        self.assertNotIn("make_rock_tile", calls)
        self.assertNotIn("game.step", calls)
        self.assertIn("asteroid_screen_rects", calls)
        self.assertIn("camera_screen_rect", calls)

    def test_gameplay_preserves_painted_pause_hitbox(self):
        from photobooth.meong_fly_painter import ACTIONS
        self.assertEqual(ACTIONS["game"]["pause"], (15, 18, 48, 46))
        self.assertEqual(ROCK_VARIANTS, 5)
        self.assertEqual(set(CAT_POSES), {"climb", "level", "dive"})
        self.assertEqual(paint_game_background().size, (360, 720))


@unittest.skipUnless(importlib.util.find_spec("kivy"), "Kivy unavailable")
class KivyBatchBGameplayTests(unittest.TestCase):
    def setUp(self):
        from photobooth.meong_fly_gui import MeongFlyStage
        from photobooth.meong_fly_flow import MeongFlyFlow
        from photobooth.meong_fly_receipts import DemoReceiptLedger
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.flow = MeongFlyFlow(
            DemoReceiptLedger(Path(self.tmp.name) / "receipt.sqlite3"))
        self.stage = MeongFlyStage(self.flow, size=(450, 900),
                                   size_hint=(None, None))
        self.addCleanup(self.stage.dispose)
        self.flow.open_scan()
        self.assertTrue(self.flow.claim_and_start("DEMO-BATCHB-GUI"))
        self.stage._refresh()

    def test_prepared_textures_and_actual_game_screen(self):
        self.assertEqual(len(self.stage._asteroids), 5)
        self.assertEqual(set(self.stage._cat_poses), set(CAT_POSES))
        self.assertEqual(self.stage._screen_seen, "game")
        self.assertIsNotNone(self.stage._backdrops["game"])

    def test_pause_and_unpause_do_not_advance_physics(self):
        self.assertTrue(self.flow.toggle_pause())
        before = self.flow.game.elapsed
        self.stage.update(.03)
        self.stage.update(.03)
        self.assertEqual(self.flow.game.elapsed, before)
        self.assertTrue(self.flow.toggle_pause())
        self.stage.update(.01)
        self.assertGreater(self.flow.game.elapsed, before)

    def test_score_event_does_not_create_another_attempt(self):
        game = self.flow.game
        game.y = 300
        game.pipes = [AsteroidGap(CAT_X-CAT_LEFT-PIPE_WIDTH-4, 300)]
        self.stage.update(.01)
        self.assertEqual(game.score, 1)
        self.assertGreaterEqual(self.stage._score_fx_since, 0)
        self.assertFalse(self.flow.can_play)

    def test_terminal_impact_shows_game_then_final_result(self):
        game = self.flow.game
        game.y = CAT_BOTTOM-1
        self.stage.update(.02)
        self.assertEqual(self.flow.screen, "lost")
        self.assertTrue(self.flow.result_recorded)
        self.assertEqual(self.stage._screen_seen, "game")
        self.assertFalse(self.flow.open_scan())
        self.stage._time = self.stage._impact_until + .01
        self.stage.update(.01)
        self.assertEqual(self.stage._screen_seen, "lost")
        self.assertEqual(self.flow.screen, "lost")


if __name__ == "__main__":
    unittest.main()
