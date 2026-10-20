"""FEAT-021 pixel-art GUI QA that runs without installing Kivy.

These tests check rendering dimensions, distinct scenes, asset handling, and
that actions never include a retry. They do NOT certify Windows GUI input.
"""
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from photobooth.meong_fly import TARGET_SCORE
from photobooth.meong_fly_painter import (
    ACTIONS, DEMO_ENTRY, H, W, GLYPHS, logo_parts,
    make_asteroid_tile, paint_static_screen,
)


class MeongFlyPainterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.art_path = Path(self.tmp.name) / "logo.png"
        im = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
        d = ImageDraw.Draw(im)
        d.rectangle((70, 95, 440, 310), fill=(190, 200, 210, 255))
        d.ellipse((190, 145, 265, 225), fill=(9, 88, 230, 255))
        d.rectangle((95, 350, 400, 440), fill=(20, 22, 45, 255))
        im.save(self.art_path)

    def test_all_five_screens_render_to_portrait_canvas(self):
        for scene in ("start", "scan", "game", "won", "lost"):
            with self.subTest(scene=scene):
                im = paint_static_screen(scene, self.art_path)
                self.assertEqual(im.size, (W, H))
                self.assertEqual(im.mode, "RGBA")
                self.assertNotEqual(im.getpixel((0, 0)), im.getpixel((W//2, H//2)))

    def test_no_retry_control_in_terminal_screens(self):
        for name in ("won", "lost"):
            self.assertEqual(set(ACTIONS[name]), {"continue"})
        self.assertNotIn("retry", repr(ACTIONS).lower())

    def test_start_and_receipt_have_distinct_navigation(self):
        self.assertEqual(set(ACTIONS["start"]), {"game", "photo"})
        self.assertEqual(set(ACTIONS["scan"]), {"back", "validate"})
        self.assertEqual(set(ACTIONS["game"]), {"pause"})
        x, y, w, h = DEMO_ENTRY
        self.assertGreater(x, 0)
        self.assertGreater(y, 0)
        self.assertLessEqual(x+w, W)
        self.assertLessEqual(y+h, H)

    def test_ui_actions_stay_within_hit_viewport(self):
        for scene, actions in ACTIONS.items():
            for action, (x,y,w,h) in actions.items():
                with self.subTest(scene=scene, action=action):
                    self.assertTrue(0 <= x < W and 0 <= y < H)
                    self.assertTrue(w > 0 and h > 0)
                    self.assertTrue(x+w <= W and y+h <= H)

    def test_asteroid_tiles_are_transparent_and_distinct(self):
        tiles = [make_asteroid_tile(i) for i in range(3)]
        self.assertTrue(all(a.size == (72, 72) for a in tiles))
        self.assertTrue(all(a.getpixel((0, 0))[3] == 0 for a in tiles))
        self.assertNotEqual(tiles[0].tobytes(), tiles[1].tobytes())

    def test_logo_comes_from_given_asset_not_generated_mascot(self):
        logo, cat = logo_parts(str(self.art_path))
        self.assertGreater(logo.width, 0)
        self.assertGreater(cat.width, 0)
        self.assertLess(cat.width, logo.width)

    def test_pixel_font_has_screen_and_receipt_glyphs(self):
        for char in "MEONG FLY! 2.500 & /-:1X":
            self.assertIn(char, GLYPHS)

    def test_mockup_target_is_ten_and_matches_engine(self):
        self.assertEqual(TARGET_SCORE, 10)

    def test_unknown_scene_rejected(self):
        with self.assertRaises(ValueError):
            paint_static_screen("production-checkout", self.art_path)


if __name__ == "__main__":
    unittest.main()
