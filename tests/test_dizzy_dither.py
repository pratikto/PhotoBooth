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

    def test_reject_bad_variant_and_seed(self):
        image = Image.new("L", (3, 3), 128)
        for args in ({"variant": "unknown"}, {"seed": -1},
                     {"seed": True}, {"seed": 2 ** 32}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                dizzy_dither(image, **args)


if __name__ == "__main__":
    unittest.main()
