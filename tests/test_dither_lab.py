"""Safe offline tests for FEAT-011 tuning lab; no GUI display or printer needed."""
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from photobooth.dither_lab import (
    DitherProfile, load_profile, render_thermal_image, save_profile,
)
from photobooth.printer import DITHER_MODES, dither_image


class DitherLabTests(unittest.TestCase):
    def setUp(self):
        self.image = Image.new("RGB", (768, 384), (160, 160, 160))

    def test_defaults_match_existing_production_printer_raster(self):
        """The branch must not invent a fourth halftoning implementation."""
        expected_gray = self.image.convert("L").resize(
            (576, 288), Image.Resampling.LANCZOS
        )
        for mode in DITHER_MODES:
            with self.subTest(mode=mode):
                profile = DitherProfile(mode=mode)
                actual = render_thermal_image(self.image, profile)
                expected = dither_image(expected_gray, mode, 128)
                self.assertEqual(actual.mode, "1")
                self.assertEqual(actual.size, expected.size)
                self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_one_bit_output_and_native_width_with_alpha(self):
        source = Image.new("RGBA", (900, 450), (0, 0, 0, 0))
        source.putpixel((0, 0), (0, 0, 0, 255))
        for width in (384, 576):
            with self.subTest(width=width):
                result = render_thermal_image(source, DitherProfile(width_dots=width))
                self.assertEqual(result.mode, "1")
                self.assertEqual(result.size, (width, width // 2))
                self.assertEqual(result.getpixel((width - 1, 0)), 255)

    def test_small_source_is_never_upscaled(self):
        img = Image.new("RGB", (210, 330), "white")
        self.assertEqual(render_thermal_image(img, DitherProfile()).size, img.size)

    def test_controls_change_output_and_threshold_only_affects_threshold_mode(self):
        gradient = Image.new("L", (576, 128))
        gradient.putdata([x * 255 // 575 for _y in range(128) for x in range(576)])
        default = render_thermal_image(gradient, DitherProfile())
        tuned = render_thermal_image(gradient, DitherProfile(
            brightness=1.15, contrast=1.3, gamma=1.5, sharpness=2.0
        ))
        self.assertNotEqual(default.tobytes(), tuned.tobytes())
        low = render_thermal_image(gradient, DitherProfile(mode="threshold", threshold=80))
        high = render_thermal_image(gradient, DitherProfile(mode="threshold", threshold=175))
        self.assertNotEqual(low.tobytes(), high.tobytes())
        self.assertGreater(high.tobytes().count(b"\x00"), low.tobytes().count(b"\x00"))
        self.assertEqual(default.tobytes(),
                         render_thermal_image(gradient, DitherProfile(threshold=200)).tobytes())

    def test_bad_profiles_are_rejected_and_round_trip(self):
        examples = [
            {"mode": "unknown"}, {"width_dots": 512},
            {"gamma": 0}, {"gamma": float("nan")}, {"brightness": -1},
            {"contrast": 6}, {"sharpness": 5}, {"threshold": 256},
            {"threshold": True}, {"width_dots": True},
        ]
        for example in examples:
            with self.subTest(example=example), self.assertRaises(ValueError):
                DitherProfile(**example)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preset.json"
            profile = DitherProfile(mode="bayer", width_dots=384,
                                    contrast=1.4, gamma=1.3)
            save_profile(path, profile)
            self.assertEqual(load_profile(path), profile)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["extra"] = "not trusted"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)
            path.write_text(json.dumps({"schema_version": 999}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)

    def test_enhanced_floyd_is_opt_in_and_distinct(self):
        source = Image.new("L", (576, 180))
        source.putdata([(x * 211 // 575 + (17 if (x + y) % 7 == 0 else 0)) % 256
                        for y in range(180) for x in range(576)])
        baseline = render_thermal_image(source, DitherProfile())
        enhanced = render_thermal_image(source, DitherProfile(enhanced_floyd=True))
        self.assertEqual(enhanced.mode, "1")
        self.assertEqual(enhanced.size, baseline.size)
        self.assertNotEqual(enhanced.tobytes(), baseline.tobytes())
        with self.assertRaises(ValueError):
            DitherProfile(mode="bayer", enhanced_floyd=True)
        with self.assertRaises(ValueError):
            DitherProfile(enhanced_floyd=1)

    def test_legacy_profile_v1_loads_with_enhanced_off(self):
        from dataclasses import asdict
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.json"
            original = asdict(DitherProfile())
            original.pop("enhanced_floyd")
            original.pop("dizzy_variant")
            original.pop("dizzy_seed")
            path.write_text(json.dumps({"schema_version": 1, **original}), encoding="utf-8")
            loaded = load_profile(path)
            self.assertFalse(loaded.enhanced_floyd)
            self.assertEqual(loaded.mode, "floyd-steinberg")

    def test_preview_coverage_and_exact_raster(self):
        image = Image.new("1", (200, 200), 255)
        image.putdata([0 if (x + y) % 2 else 255 for y in range(200) for x in range(200)])
        original = image.tobytes()
        displayed = image.convert("L").resize((20, 20), Image.Resampling.BOX)
        self.assertTrue(all(110 <= p <= 145 for p in displayed.getdata()))
        self.assertEqual(image.tobytes(), original)
        path = Path(__file__).resolve().parents[1] / "tools" / "dither_compare_gui.py"
        code = path.read_text(encoding="utf-8")
        self.assertIn("preview.thumbnail((370, 268), Image.Resampling.BOX)", code)

    def test_compare_gui_has_enhanced_toggle_and_compiles(self):
        import ast
        path = Path(__file__).resolve().parents[1] / "tools" / "dither_compare_gui.py"
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
        self.assertIn("def toggle_enhanced(self):", source)
        self.assertIn("Enhanced Floyd (experimental)", source)

    def test_gui_module_compiles_without_importing_windows_printer(self):
        import ast
        target = Path(__file__).resolve().parents[1] / "tools" / "dither_tuning_gui.py"
        ast.parse(target.read_text(encoding="utf-8"), filename=str(target))


if __name__ == "__main__":
    unittest.main()
