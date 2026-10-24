"""Regression: author-Gist-style baseline and independent 8-neighbor reference."""
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from photobooth.dizzy_dither import dizzy_dither
from tools.dizzy_reference_compare import (
    compare_references, gist_style_orthogonal,
    independent_article8, sample_source, write_comparison,
)


class DizzyAuthorReferenceTests(unittest.TestCase):
    def test_pure_black_white_and_binary_shapes_match_references(self):
        for color in (0, 255):
            image = Image.new("L", (27, 23), color)
            candidates = (
                gist_style_orthogonal(image, seed=99),
                gist_style_orthogonal(image, seed=99, same_order=True),
                independent_article8(image, seed=99),
                dizzy_dither(image, variant="orthogonal-4", seed=99),
                dizzy_dither(image, variant="article-8", seed=99),
            )
            for raster in candidates:
                with self.subTest(color=color, method=raster.mode):
                    self.assertEqual(raster.mode, "1")
                    self.assertEqual(raster.size, image.size)
                    self.assertEqual(set(raster.convert("L").tobytes()), {color})

    def test_gist_seed_is_repeatable_and_source_not_changed(self):
        image = sample_source(75, 68)
        original = image.tobytes()
        a = gist_style_orthogonal(image, seed=42).tobytes()
        self.assertEqual(a, gist_style_orthogonal(image, seed=42).tobytes())
        self.assertNotEqual(a, gist_style_orthogonal(image, seed=43).tobytes())
        self.assertEqual(image.tobytes(), original)

    def test_article8_pseudocode_is_repeatable_and_binary(self):
        source = sample_source(63, 54)
        a = independent_article8(source, seed=4)
        self.assertEqual(a.mode, "1")
        self.assertEqual(a.size, source.size)
        self.assertEqual(a.tobytes(), independent_article8(source, seed=4).tobytes())

    def test_comparison_discloses_non_identity_and_equal_order_numeric_delta(self):
        source = sample_source(48, 53)
        report, images = compare_references(source, seed=17)
        self.assertFalse(report["metadata"]["pixel_identical_expected"])
        self.assertFalse(report["metadata"]["tone_lut_enabled"])
        self.assertEqual(set(report["results"]), {"article-8", "orthogonal-4"})
        self.assertIn("gist_equal_order", " ".join(images))
        for name, metrics in report["results"].items():
            self.assertTrue(0 <= metrics["different_pixels_pct"] <= 100)
            self.assertTrue(-100 <= metrics["white_coverage_delta_pp"] <= 100)
            self.assertGreater(metrics["different_pixels"], 0)
            self.assertTrue(images[f"{name}_meong"].mode == "1")
            self.assertTrue(images[f"{name}_reference"].mode == "1")
        held = report["results"]["orthogonal-4"]["equal_order_numeric_comparison"]
        self.assertTrue(0 <= held["different_pixels_pct"] <= 100)

    def test_comparison_exports_reviewable_png_and_json(self):
        report, images = compare_references(sample_source(32, 40), seed=6)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_comparison(report, images, Path(directory))
            self.assertEqual(len(paths), len(images) + 1)
            self.assertTrue(all(p.exists() for p in paths))
            data = json.loads(
                (Path(directory) / "dizzy_reference_comparison.json").read_text())
            self.assertEqual(set(data["results"]), {"article-8", "orthogonal-4"})
            difference = Image.open(
                Path(directory) / "orthogonal-4_difference.png")
            self.assertEqual(difference.mode, "L")

    def test_bad_seed_and_size_rejected(self):
        with self.assertRaises(ValueError):
            gist_style_orthogonal(Image.new("L", (10, 10)), seed=-1)
        with self.assertRaises(ValueError):
            independent_article8(Image.new("L", (10, 10)), seed=True)
        with self.assertRaises(ValueError):
            sample_source(1, 12)


if __name__ == "__main__":
    unittest.main()
