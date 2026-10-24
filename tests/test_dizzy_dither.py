"""Safety and correctness regression tests for experimental Dizzy dithering."""
import unittest
from PIL import Image
from photobooth.dizzy_dither import dizzy_dither, _permuted_pixel_indices


class DizzyDitherTests(unittest.TestCase):
    def test_permutation_is_complete_without_repeats(self):
        for count in (1, 2, 3, 7, 8, 10, 31, 64, 100, 577):
            with self.subTest(count=count):
                indices = list(_permuted_pixel_indices(count, 42))
                self.assertEqual(set(indices), set(range(count)))
                self.assertEqual(len(indices), count)

    def test_white_black_exact_and_binary_no_resize(self):
        for variant in ("article-8", "orthogonal-4"):
            for color in (0, 255):
                with self.subTest(variant=variant, color=color):
                    src = Image.new("L", (31, 17), color)
                    dst = dizzy_dither(src, variant=variant)
                    self.assertEqual(dst.mode, "1")
                    self.assertEqual(dst.size, src.size)
                    self.assertEqual(set(dst.convert("L").tobytes()), {color})

    def test_deterministic_seed_and_source_unchanged(self):
        source = Image.new("L", (91, 49))
        source.putdata([(x * 13 + y * 5) % 256 for y in range(49) for x in range(91)])
        original = source.tobytes()
        for variant in ("article-8", "orthogonal-4"):
            first = dizzy_dither(source, variant=variant, seed=9).tobytes()
            self.assertEqual(first, dizzy_dither(source, variant=variant, seed=9).tobytes())
            self.assertNotEqual(first, dizzy_dither(source, variant=variant, seed=10).tobytes())
        self.assertEqual(original, source.tobytes())

    def test_variants_distinct_and_coverage_reasonable(self):
        image = Image.new("L", (101, 81), 128)
        a = dizzy_dither(image, variant="article-8")
        b = dizzy_dither(image, variant="orthogonal-4")
        self.assertNotEqual(a.tobytes(), b.tobytes())
        for dest in (a, b):
            white_frac = sum(1 for p in dest.convert("L").tobytes() if p == 255) / 8181
            self.assertGreater(white_frac, 0.39)
            self.assertLess(white_frac, 0.61)

    def test_cpu_tone_lut_reduces_uniform_gray_error(self):
        from photobooth.dizzy_calibration import dizzy_cpu_lut
        for variant in ("article-8", "orthogonal-4"):
            lut = dizzy_cpu_lut(variant)
            self.assertEqual(len(lut), 256)
            self.assertEqual((lut[0], lut[-1]), (0.0, 1.0))
            self.assertTrue(all(a <= b for a, b in zip(lut, lut[1:])))
            for g in (16, 32, 224, 240):
                with self.subTest(variant=variant, gray=g):
                    image = Image.new("L", (96, 96), g)
                    base = dizzy_dither(image, variant=variant)
                    tuned = dizzy_dither(image, variant=variant,
                                        contrast_correction=True)
                    ideal = g / 255.0
                    def error(raster):
                        return abs(raster.convert("L").tobytes().count(255) / 9216 - ideal)
                    self.assertLess(error(tuned), error(base) + 0.002)

    def test_opt_in_tone_lut_preserves_defaults_and_extremes(self):
        image = Image.new("L", (41, 37))
        image.putdata([(x * 19 + y * 7) % 256 for y in range(37) for x in range(41)])
        for variant in ("article-8", "orthogonal-4"):
            self.assertEqual(
                dizzy_dither(image, variant=variant, seed=123).tobytes(),
                dizzy_dither(image, variant=variant, seed=123,
                             contrast_correction=False).tobytes())
            for color in (0, 255):
                flat = Image.new("L", (30, 35), color)
                tuned = dizzy_dither(flat, variant=variant, contrast_correction=True)
                self.assertEqual(set(tuned.convert("L").tobytes()), {color})

    def test_reject_bad_variant_and_seed(self):
        image = Image.new("L", (3, 3), 128)
        for args in ({"variant": "unknown"}, {"seed": -1},
                     {"seed": True}, {"seed": 2 ** 32}, {"contrast_correction": 1}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                dizzy_dither(image, **args)


if __name__ == "__main__":
    unittest.main()
