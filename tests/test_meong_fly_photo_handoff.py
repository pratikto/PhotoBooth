"""FEAT-021 standalone tutorial and layout preview contract tests."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from photobooth.meong_fly_painter import ACTIONS, W, H, paint_static_screen
from photobooth.meong_fly_photo_handoff import layout_hitboxes


class PhotoHandoffTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.logo = Path(self.folder.name) / "placeholder.png"
        Image.new("RGBA", (256, 256), (200, 210, 230, 255)).save(self.logo)

    def test_tutorial_and_layouts_paint_in_original_viewport(self):
        for name in ("tutorial", "layouts"):
            with self.subTest(name=name):
                result = paint_static_screen(name, self.logo)
                self.assertEqual(result.size, (W, H))
                self.assertEqual(result.mode, "RGBA")

    def test_twelve_nonoverlapping_layout_buttons(self):
        boxes = list(layout_hitboxes().values())
        self.assertEqual(len(boxes), 12)
        self.assertEqual(ACTIONS["layouts"], layout_hitboxes())
        for i, (x, y, w, h) in enumerate(boxes):
            self.assertGreater(w, 0)
            self.assertGreater(h, 0)
            self.assertLessEqual(x+w, W)
            self.assertLessEqual(y+h, H)
            for j, (xx, yy, ww, hh) in enumerate(boxes):
                if i == j:
                    continue
                overlap = x < xx+ww and xx < x+w and y < yy+hh and yy < y+h
                self.assertFalse(overlap, f"Overlap: {i+1}, {j+1}")

    def test_result_has_only_one_layout_cta_no_retry(self):
        self.assertEqual(set(ACTIONS["won"]), {"continue"})
        self.assertEqual(set(ACTIONS["lost"]), {"continue"})
        self.assertEqual(set(ACTIONS["tutorial"]), {"tutorial_done"})
        self.assertNotIn("retry", str(ACTIONS).lower())


if __name__ == "__main__":
    unittest.main()
