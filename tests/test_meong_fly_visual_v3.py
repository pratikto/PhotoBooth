"""Poster v3 regression: newest logo, legible screens and falling photo motion.

Runs without Kivy; does not claim real QR, photo printing or GIF deployment.
"""
import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from photobooth.meong_fly_painter import ACTIONS, paint_static_screen, W, H
from photobooth.meong_fly_print_fx import InstantPhotoEmitter
from photobooth.meong_fly_visual_v3 import (
    animation_gif_path, meong_animation_frames, camera_cat_from_latest_logo,
    printed_photo_tile, photo_feed_frames, paint_poster_screen,
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

    def test_falling_photo_motion_starts_at_meong_not_random(self):
        emitter = InstantPhotoEmitter()
        for _ in range(8):
            emitter.update(.1, (180, 230), bottom=450)
        (paper,) = emitter.poses()
        self.assertAlmostEqual(paper.x + paper.width/2, 180)
        self.assertAlmostEqual(paper.y, 230)
        self.assertTrue(paper.attached)

    def test_photo_feed_previews_reveal_pixels_without_squashing(self):
        tile = printed_photo_tile(0)
        steps = photo_feed_frames(tile)
        self.assertEqual(len(steps), 8)
        self.assertTrue(all(image.size == tile.size for image in steps))
        self.assertEqual(steps[0].getpixel((10, 40))[3], 0)
        self.assertEqual(steps[-1].tobytes(), tile.tobytes())


if __name__ == "__main__":
    unittest.main()
