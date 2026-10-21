"""FEAT-022: pure design-contract regression (no Kivy or camera required)."""
import unittest

from photobooth.kiosk_v2 import design_tokens as d


class PixelArcadeTokensTests(unittest.TestCase):
    def test_game_palette_matches_audited_source(self):
        self.assertEqual(d.SPACE, "#050C2F")
        self.assertEqual(d.PANEL, "#0B1543")
        self.assertEqual(d.PINK, "#FF55AB")
        self.assertEqual(d.CYAN, "#58D1FF")
        self.assertEqual(d.GOLD, "#FFDC78")
        self.assertEqual(d.PURPLE, "#B385FF")

    def test_button_faces_match_existing_game_polish(self):
        self.assertEqual(d.BUTTON_COLORS["primary"], "#FF53A9")
        self.assertEqual(d.BUTTON_COLORS["secondary"], "#4DCCFA")
        self.assertEqual(d.BUTTON_COLORS["tertiary"], "#1B295B")
        self.assertEqual(d.BUTTON_EDGES["primary"], "#FFA5DA")
        self.assertEqual(d.BUTTON_EDGES["secondary"], "#AFF1FF")

    def test_stepped_rectangles_fit_original_bounds(self):
        for width, height in ((320, 70), (80, 48), (12, 12), (2, 1)):
            pieces = d.stepped_rects(10, 20, width, height, 6)
            self.assertEqual(len(pieces), 2)
            for x, y, w, h in pieces:
                self.assertGreaterEqual(x, 10)
                self.assertGreaterEqual(y, 20)
                self.assertGreaterEqual(w, 0)
                self.assertGreaterEqual(h, 0)
                self.assertLessEqual(x + w, 10 + width)
                self.assertLessEqual(y + h, 20 + height)

    def test_zero_and_negative_dimensions_have_no_drawable_area(self):
        for dimensions in ((0, 10), (10, 0), (-1, 8), (5, -2)):
            self.assertEqual(d.stepped_rects(0, 0, *dimensions, 6), ())

    def test_oversized_notch_stays_within_panel(self):
        pieces = d.stepped_rects(0, 0, 20, 10, 999)
        self.assertEqual(pieces, ((5.0, 0, 10.0, 10), (0, 5.0, 20, 0.0)))

    def test_button_palette_has_all_variants(self):
        self.assertEqual(set(d.BUTTON_COLORS), set(d.BUTTON_EDGES))
        self.assertEqual(set(d.BUTTON_COLORS),
                         {"primary", "secondary", "tertiary", "muted"})

    def test_clipped_corner_geometry_has_no_outside_pixels(self):
        pieces = d.stepped_rects(10, 20, 100, 60, 6)
        def inside(px, py):
            return any(x <= px < x + w and y <= py < y + h
                       for x, y, w, h in pieces)
        self.assertFalse(inside(10, 20))
        self.assertFalse(inside(109, 20))
        self.assertFalse(inside(10, 79))
        self.assertFalse(inside(109, 79))
        self.assertTrue(inside(16, 20))
        self.assertTrue(inside(10, 26))
        self.assertTrue(inside(60, 50))

    def test_negative_notch_is_clamped(self):
        self.assertEqual(
            d.stepped_rects(1, 2, 10, 20, -3),
            ((1, 2, 10, 20), (1, 2, 10, 20)),
        )


if __name__ == "__main__":
    unittest.main()
