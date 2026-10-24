"""Regression tests for optional shared Floyd/Dizzy preprocessing (FEAT-011).

No Tk display or physical printer is needed. The previous Enhanced Floyd
processing operations are reproduced independently to catch visual drift.
"""
from dataclasses import asdict, replace
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from photobooth.dither_lab import (
    ComparisonProfiles, DitherProfile, load_comparison, load_profile,
    render_thermal_image, save_comparison, save_profile,
)
from photobooth.dizzy_dither import dizzy_dither
from photobooth.dither_print import annotated_raster
from photobooth.printer import dither_image


def _old_enhanced_grayscale(source, profile):
    """Independent reference for the exact previous Enhanced Floyd recipe."""
    rgba = source.convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    gray = Image.alpha_composite(white, rgba).convert("L")
    if gray.width > profile.width_dots:
        height = max(1, round(gray.height * profile.width_dots / gray.width))
        gray = gray.resize((profile.width_dots, height), Image.Resampling.LANCZOS)
    if profile.brightness != 1.0:
        gray = ImageEnhance.Brightness(gray).enhance(profile.brightness)
    if profile.contrast != 1.0:
        gray = ImageEnhance.Contrast(gray).enhance(profile.contrast)
    if profile.gamma != 1.0:
        gray = gray.point([
            round(255 * ((value / 255) ** (1 / profile.gamma)))
            for value in range(256)
        ])
    if profile.sharpness != 1.0:
        gray = ImageEnhance.Sharpness(gray).enhance(profile.sharpness)
    denoised = gray.filter(ImageFilter.MedianFilter(size=3))
    leveled = ImageOps.autocontrast(denoised, cutoff=1, preserve_tone=True)
    gray = Image.blend(denoised, leveled, 0.20)
    return gray.filter(
        ImageFilter.UnsharpMask(radius=1.1, percent=55, threshold=3)
    )


class EnhancedDitherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Colored photo-like edges, gradients, transparent border and noise
        # reveal denoise/tonal changes without using customer images.
        cls.photo = Image.new("RGBA", (98, 74))
        cls.photo.putdata([
            (
                (x * 11 + y * 2 + (60 if (x + y) % 11 == 0 else 0)) % 256,
                (x * 4 + y * 5 + (95 if (x * y) % 17 == 0 else 0)) % 256,
                (x * 3 + y * 7) % 256,
                0 if x == 0 or y == 0 else 255,
            )
            for y in range(74) for x in range(98)
        ])

    def test_enhanced_floyd_is_byte_identical_to_previous_recipe(self):
        for brightness, contrast, gamma, sharpness in (
            (1.0, 1.0, 1.0, 1.0),
            (0.87, 1.36, 1.45, 1.60),
        ):
            with self.subTest(tuning=(brightness, contrast, gamma, sharpness)):
                p = DitherProfile(
                    enhanced_floyd=True, brightness=brightness,
                    contrast=contrast, gamma=gamma, sharpness=sharpness,
                )
                expected = dither_image(
                    _old_enhanced_grayscale(self.photo, p),
                    "floyd-steinberg", p.threshold,
                )
                actual = render_thermal_image(self.photo, p)
                self.assertEqual(actual.mode, "1")
                self.assertEqual(actual.size, expected.size)
                self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_enhanced_dizzy_reuses_same_recipe_for_both_variants(self):
        for variant in ("article-8", "orthogonal-4"):
            with self.subTest(variant=variant):
                p = DitherProfile(
                    mode="dizzy", dizzy_variant=variant, dizzy_seed=19,
                    enhanced_dizzy=True, brightness=0.92, contrast=1.21,
                    gamma=1.26, sharpness=1.32,
                )
                expected = dizzy_dither(
                    _old_enhanced_grayscale(self.photo, p),
                    variant=variant, seed=19,
                )
                result = render_thermal_image(self.photo, p)
                self.assertEqual(result.mode, "1")
                self.assertEqual(result.size, expected.size)
                self.assertEqual(result.tobytes(), expected.tobytes())
                self.assertEqual(
                    result.tobytes(), render_thermal_image(self.photo, p).tobytes())
                baseline = render_thermal_image(
                    self.photo, replace(p, enhanced_dizzy=False))
                self.assertNotEqual(baseline.tobytes(), result.tobytes())

    def test_dizzy_baseline_remains_unchanged(self):
        gray = Image.alpha_composite(
            Image.new("RGBA", self.photo.size, "white"),
            self.photo,
        ).convert("L")
        for variant in ("article-8", "orthogonal-4"):
            baseline = DitherProfile(mode="dizzy", dizzy_variant=variant)
            expected = dizzy_dither(gray, variant=variant)
            self.assertEqual(
                render_thermal_image(self.photo, baseline).tobytes(),
                expected.tobytes())

    def test_flags_are_strictly_boolean_and_lane_specific(self):
        for flag in (1, "true", None):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                DitherProfile(mode="dizzy", enhanced_dizzy=flag)
        for mode in ("floyd-steinberg", "bayer", "threshold"):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                DitherProfile(mode=mode, enhanced_dizzy=True)
        with self.assertRaises(ValueError):
            DitherProfile(mode="dizzy", enhanced_floyd=True)

    def test_v6_round_trip_persists_independent_enhanced_flags(self):
        configs = ComparisonProfiles()
        configs = configs.replace_lane(
            replace(configs.floyd, enhanced_floyd=True))
        configs = configs.replace_lane(
            replace(configs.dizzy, enhanced_dizzy=True,
                    dizzy_variant="orthogonal-4", dizzy_seed=123))
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "lab.json"
            single = Path(folder) / "single.json"
            save_comparison(target, configs)
            stored = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(stored["schema_version"], 6)
            self.assertTrue(stored["lanes"]["dizzy"]["enhanced_dizzy"])
            self.assertFalse(stored["lanes"]["bayer"]["enhanced_dizzy"])
            self.assertIn("threshold", stored["lanes"])
            self.assertEqual(load_comparison(target), configs)
            save_profile(single, configs.dizzy)
            self.assertEqual(load_profile(single), configs.dizzy)
            self.assertEqual(
                json.loads(single.read_text(encoding="utf-8"))["schema_version"], 6)

    def test_v3_preset_loads_with_dizzy_enhancement_off(self):
        # v3 may contain tuned Floyd, hidden Threshold, or changed Dizzy seed.
        old = ComparisonProfiles()
        old = old.replace_lane(replace(old.floyd, enhanced_floyd=True))
        old = old.replace_lane(replace(old.threshold, threshold=165))
        old = old.replace_lane(replace(
            old.dizzy, dizzy_variant="orthogonal-4", dizzy_seed=7))
        payload = {
            "schema_version": 3,
            "lanes": {},
        }
        for mode in ("floyd-steinberg", "bayer", "threshold", "dizzy"):
            raw = asdict(old.by_mode(mode))
            raw.pop("enhanced_dizzy")
            raw.pop("dizzy_contrast_correction")
            for key in ("smart_enhance", "clahe_strength", "denoise_level",
                        "tone_strength", "postprocess_enabled",
                        "dot_cleanup_level", "edge_refine_level"):
                raw.pop(key)
            payload["lanes"][mode] = raw
        with tempfile.TemporaryDirectory() as folder:
            compare = Path(folder) / "v3-lab.json"
            compare.write_text(json.dumps(payload), encoding="utf-8")
            loaded = load_comparison(compare)
            self.assertEqual(loaded, old)
            self.assertFalse(loaded.dizzy.enhanced_dizzy)
            self.assertTrue(loaded.floyd.enhanced_floyd)
            self.assertEqual(loaded.threshold.threshold, 165)
            single = Path(folder) / "v3-dizzy.json"
            single.write_text(json.dumps({
                "schema_version": 3,
                **payload["lanes"]["dizzy"],
            }), encoding="utf-8")
            self.assertFalse(load_profile(single).enhanced_dizzy)

    def test_invalid_extra_v6_field_rejected(self):
        old = asdict(DitherProfile(mode="dizzy"))
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "invalid.json"
            target.write_text(json.dumps({
                "schema_version": 6, **old, "unapproved_option": True,
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(target)

    def test_test_print_uses_original_native_dots_and_labeled_header(self):
        # A proper 384-dot-width strip ensures both header labels fit,
        # so their binary metadata can be compared without clipping.
        image = Image.new("1", (384, 48), 255)
        image.putpixel((0, 0), 0)
        profile = DitherProfile(mode="dizzy", width_dots=384,
                               enhanced_dizzy=True)
        baseline = replace(profile, enhanced_dizzy=False)
        orig = image.tobytes()
        tagged = annotated_raster(image, profile)
        other = annotated_raster(image, baseline)
        self.assertEqual(image.tobytes(), orig)
        self.assertEqual(tagged.size, other.size)
        self.assertNotEqual(tagged.tobytes(), other.tobytes())
        self.assertEqual(
            tagged.crop((0, tagged.height - image.height,
                         image.width, tagged.height)).tobytes(), orig)

    def test_gui_exposes_dizzy_checkbox_and_distinct_filenames(self):
        import ast
        src_path = (Path(__file__).resolve().parents[1] /
                    "tools" / "dither_compare_gui.py")
        src = src_path.read_text(encoding="utf-8")
        ast.parse(src, filename=str(src_path))
        for marker in (
            "Enhanced Dizzy (experimental)",
            "def toggle_enhanced_dizzy(self):",
            "variable=self.enhanced_dizzy",
            "self.enhanced_dizzy.set(configs.dizzy.enhanced_dizzy)",
            "self.schedule(\"dizzy\")",
            "meong-dither-lab-v6.json",
            "enhanced\" if profile.enhanced_dizzy else \"baseline",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, src)


if __name__ == "__main__":
    unittest.main()
