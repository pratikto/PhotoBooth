"""FEAT-021 Batch A pixel-art static layout and interaction guard tests.

Pillow tests remain runnable without Kivy. They check that the exact Hitbox
constants and painted controls remain aligned, and preserve the demo warning.
"""
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from photobooth.meong_fly_painter import ACTIONS, DEMO_ENTRY, H, W, paint_static_screen
from photobooth.meong_fly_polish import paint_polished_menu, arcade_card


class BatchAVisualTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.logo = Path(self.tempdir.name) / "approved_demo_logo.png"
        Image.new("RGBA", (120, 90), (16, 25, 74, 255)).save(self.logo)

    def test_start_and_scan_keep_stage_dimensions_and_unique_art(self):
        first = paint_static_screen("start", self.logo)
        second = paint_static_screen("scan", self.logo)
        self.assertEqual(first.size, (W, H))
        self.assertEqual(second.size, (W, H))
        self.assertNotEqual(first.tobytes(), second.tobytes())
        self.assertEqual(first.mode, "RGBA")
        self.assertEqual(second.mode, "RGBA")

    def test_polish_only_targeted_pages(self):
        with self.assertRaises(ValueError):
            paint_polished_menu("game", self.logo)
        for page in ("game", "won", "lost"):
            self.assertEqual(paint_static_screen(page, self.logo).size, (W, H))

    def test_promo_ticket_stays_above_start_cta(self):
        self.assertLess(519, ACTIONS["start"]["game"][1])
        self.assertLess(ACTIONS["start"]["game"][1] + ACTIONS["start"]["game"][3],
                        ACTIONS["start"]["photo"][1])

    def test_scan_input_is_outside_scanner_and_buttons(self):
        input_x, input_y, input_w, input_h = DEMO_ENTRY
        self.assertGreaterEqual(input_y, 478)
        self.assertGreaterEqual(input_y - 450, 20)
        for key, (x, y, w, h) in ACTIONS["scan"].items():
            with self.subTest(action=key):
                self.assertFalse((input_x < x + w and x < input_x + input_w)
                                 and (input_y < y + h and y < input_y + input_h))

    def test_input_region_has_light_contrasting_field(self):
        frame = paint_static_screen("scan", self.logo)
        color = frame.getpixel((180, 499))
        self.assertGreater(min(color[:3]), 210)
        dark = frame.getpixel((25, 460))
        self.assertLess(max(dark[:3]), 150)

    def test_buttons_are_visibly_distinct_and_tall_enough(self):
        frame = paint_static_screen("start", self.logo)
        self.assertGreaterEqual(ACTIONS["start"]["game"][3], 48)
        self.assertGreaterEqual(ACTIONS["start"]["photo"][3], 48)
        pink = frame.getpixel((50, 569))
        cyan = frame.getpixel((50, 639))
        self.assertGreater(pink[0], pink[2])
        self.assertGreater(cyan[2], cyan[0])

    def test_polish_card_handles_normal_and_accent_fills(self):
        img = Image.new("RGB", (120, 100), (5, 12, 47))
        from PIL import ImageDraw
        arcade_card(ImageDraw.Draw(img), (20, 10, 90, 80), (11, 21, 67), (87, 73, 154))
        self.assertNotEqual(img.getpixel((55, 30)), img.getpixel((0, 0)))


if __name__ == "__main__":
    unittest.main()
