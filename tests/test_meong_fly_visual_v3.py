"""Poster v3 regression: newest logo, legible screens and falling photo motion.

Runs without Kivy; does not claim real QR, photo printing or GIF deployment.
"""
import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from photobooth.meong_fly_painter import ACTIONS, paint_static_screen, W, H
from photobooth.meong_fly_visual_v3 import (
    animation_gif_path, meong_animation_frames, camera_cat_from_latest_logo,
    printed_photo_tile, falling_photo_positions, paint_poster_screen,
)


class PosterV3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.logo = Path(self.temp.name) / "older_logo.png"
        Image.new("RGBA", (256, 256), (85, 110, 220, 255)).save(self.logo)

    def test_latest_gif_derived_logo_is_bundled_and_readable(self):
        frames = meong_animation_frames(self.logo)
        self.assertGreater(len(frames), 1)  # Full GIF or synthesized print-drop loop
        frame = frames[0]
        self.assertGreater(frame.width, 80)
        self.assertEqual(frame.mode, "RGBA")
        self.assertTrue(frame.getbbox())
        self.assertNotEqual(frames[0].tobytes(), frames[-1].tobytes())
        self.assertGreater(frame.getpixel((frame.width//2, frame.height//2))[3], 0)

    def test_new_camera_cat_crop_is_bounded(self):
        cat = camera_cat_from_latest_logo(self.logo)
        self.assertLess(cat.width, meong_animation_frames(self.logo)[0].width)
        self.assertGreater(cat.width, 35)
        self.assertGreater(cat.height, 35)

    def test_latest_screens_keep_full_portrait_bounds(self):
        for screen in ("start", "won", "lost"):
            with self.subTest(screen=screen):
                image = paint_static_screen(screen, self.logo)
                self.assertEqual(image.size, (W, H))
                self.assertEqual(image.mode, "RGBA")
                self.assertNotEqual(image.getpixel((180, 330)),
                                    image.getpixel((0, 0)))

    def test_new_screens_have_no_retry_and_no_payment_cta(self):
        self.assertEqual(set(ACTIONS["won"]), {"continue"})
        self.assertEqual(set(ACTIONS["lost"]), {"continue"})
        self.assertNotIn("retry", str(ACTIONS).lower())
        import inspect
        source = inspect.getsource(paint_poster_screen)
        self.assertIn("PILIH LAYOUT FOTO", source)
        self.assertNotIn("LANJUT KE PEMBAYARAN", source)

    def test_printed_photos_are_real_rgba_pixel_sprites(self):
        cards = [printed_photo_tile(i) for i in range(4)]
        self.assertTrue(all(c.mode == "RGBA" for c in cards))
        self.assertTrue(all(c.size == (32, 41) for c in cards))
        self.assertTrue(all(c.getpixel((0, 0))[3] != 0 for c in cards))

    def test_falling_photo_motion_changes_positions(self):
        a = falling_photo_positions(0)
        b = falling_photo_positions(.6)
        self.assertEqual(len(a), 6)
        self.assertNotEqual(a, b)
        self.assertTrue(all(0 <= size < 64 for _, _, size, _ in a))


if __name__ == "__main__":
    unittest.main()
