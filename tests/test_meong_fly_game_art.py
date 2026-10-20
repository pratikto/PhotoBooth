"""FEAT-021 Batch B artwork/hitbox consistency tests; no Kivy required."""
import unittest

from PIL import Image

from photobooth.meong_fly import (
    HEIGHT, CAT_LEFT, CAT_RIGHT, CAT_TOP, CAT_BOTTOM,
    GAP_HEIGHT, PIPE_WIDTH, WIDTH,
)
from photobooth.meong_fly_game_art import (
    GAME_FIELD_TOP, GAME_FIELD_BOTTOM, ROCK_VARIANTS, CAT_POSES,
    paint_game_background, make_rock_tile, camera_cat_poses,
    asteroid_screen_rects, camera_screen_rect,
)


class GameArtTests(unittest.TestCase):
    def test_painted_hud_and_playfield_bounds(self):
        im = paint_game_background()
        self.assertEqual(im.size, (360, 720))
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(GAME_FIELD_BOTTOM-GAME_FIELD_TOP, HEIGHT*360/WIDTH)
        self.assertNotEqual(im.getpixel((112, 28)), im.getpixel((112, 145)))
        self.assertNotEqual(im.getpixel((310, 39)), im.getpixel((310, 230)))

    def test_unique_five_rocks_and_alpha_margins(self):
        variants = [make_rock_tile(i) for i in range(ROCK_VARIANTS)]
        self.assertEqual(len({v.tobytes() for v in variants}), ROCK_VARIANTS)
        for image in variants:
            self.assertEqual(image.size, (64, 64))
            self.assertEqual(image.mode, "RGBA")
            self.assertEqual(image.getpixel((0, 0))[3], 0)
            self.assertGreater(image.getpixel((32, 32))[3], 0)

    def test_logo_poses_stay_contained_inside_physics_rectangle(self):
        logo = Image.new("RGBA", (250, 170), (160, 165, 180, 255))
        poses = camera_cat_poses(logo)
        self.assertEqual(set(poses), set(CAT_POSES))
        self.assertNotEqual(poses["climb"].tobytes(), poses["dive"].tobytes())
        for name, image in poses.items():
            with self.subTest(name=name):
                self.assertEqual(image.size, (78, 58))
                x0, y0, x1, y1 = image.getbbox()
                self.assertGreater(x0, 0)
                self.assertGreater(y0, 0)
                self.assertLess(x1, 78)
                self.assertLess(y1, 58)
                self.assertEqual(image.getpixel((0, 0))[3], 0)

    def test_asteroid_belts_cover_exact_engine_boxes(self):
        x, gap = 230, 322
        ((lower, lb), (upper, ub)) = asteroid_screen_rects(x, gap)
        self.assertEqual((lower, upper), ("lower", "upper"))
        self.assertAlmostEqual(lb[0], x*360/WIDTH)
        self.assertAlmostEqual(ub[0], lb[0])
        self.assertAlmostEqual(lb[2], PIPE_WIDTH*360/WIDTH)
        self.assertAlmostEqual(ub[2], lb[2])
        self.assertAlmostEqual(lb[1]+lb[3], GAME_FIELD_BOTTOM)
        self.assertAlmostEqual(ub[1], GAME_FIELD_TOP)
        self.assertAlmostEqual(lb[1]-(ub[1]+ub[3]), GAP_HEIGHT*360/WIDTH)

    def test_camera_box_matches_engine_boundaries_at_every_height(self):
        scale = 360/WIDTH
        for y in (95, 320, 538):
            with self.subTest(y=y):
                x, top, w, h = camera_screen_rect(y)
                self.assertAlmostEqual(w, (CAT_LEFT+CAT_RIGHT)*scale)
                self.assertAlmostEqual(h, (CAT_BOTTOM+CAT_TOP)*scale)
                self.assertAlmostEqual(top, GAME_FIELD_BOTTOM-(y+CAT_TOP)*scale)

    def test_collision_geometry_unchanged(self):
        self.assertEqual(GAP_HEIGHT, 195)
        self.assertEqual(PIPE_WIDTH, 65)
        self.assertEqual(WIDTH, 480)
        self.assertEqual(HEIGHT, 640)


if __name__ == "__main__":
    unittest.main()
