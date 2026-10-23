"""FEAT-011 optional Smart Enhance / post-processing, no printer hardware."""
from __future__ import annotations

from dataclasses import asdict
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from photobooth.dither_lab import (
    DitherProfile, ComparisonProfiles, NEW_ENHANCEMENT_FIELDS,
    load_comparison, load_profile, render_thermal_image, save_comparison,
    save_profile,
)
from photobooth.dither_processing import (
    apply_smart_enhance, clahe_gray, refine_binary_raster,
)


def chart():
    gray = Image.new("L", (168, 144))
    gray.putdata([
        min(255, max(0, (x * 255 // 167) + (
            (y * 13 + x * 11) % 17 if 30 < x < 130 else 0)))
        for y in range(144) for x in range(168)
    ])
    return gray


class SmartEnhanceTests(unittest.TestCase):
    def test_clahe_preserves_dimensions_and_uniform_tiles(self):
        uniform = Image.new("L", (160, 100), 128)
        self.assertEqual(clahe_gray(uniform, 0.0).tobytes(), uniform.tobytes())
        self.assertEqual(clahe_gray(uniform, 0.8).tobytes(), uniform.tobytes())
        gradient = chart()
        before = gradient.tobytes()
        after = clahe_gray(gradient, 0.7)
        self.assertEqual(after.mode, "L")
        self.assertEqual(after.size, gradient.size)
        self.assertNotEqual(after.tobytes(), before)
        self.assertEqual(gradient.tobytes(), before)
        self.assertEqual(after.tobytes(), clahe_gray(gradient, 0.7).tobytes())

    def test_postprocess_preserves_halftone_midtone_pixels(self):
        raster = Image.new("1", (36, 30))
        raster.putdata([
            0 if (x + y) % 2 else 255
            for y in range(30) for x in range(36)
        ])
        reference = Image.new("L", raster.size, 128)
        result = refine_binary_raster(
            raster, reference, dot_cleanup_level=3, edge_refine_level=3)
        self.assertEqual(result.mode, "1")
        self.assertEqual(result.tobytes(), raster.tobytes())

    def test_selective_cleanup_only_removes_near_paper_speck(self):
        reference = Image.new("L", (24, 24), 255)
        raster = Image.new("1", reference.size, 255)
        raster.putpixel((12, 12), 0)
        result = refine_binary_raster(
            raster, reference, dot_cleanup_level=2, edge_refine_level=0)
        self.assertEqual(result.getpixel((12, 12)), 255)
        self.assertEqual(raster.getpixel((12, 12)), 0)
        self.assertEqual(result.mode, "1")

    def test_edge_refinement_uses_source_edges_only(self):
        reference = Image.new("L", (32, 24), 255)
        for y in range(24):
            for x in range(4, 16):
                reference.putpixel((x, y), 0)
        blank = Image.new("1", reference.size, 255)
        refined = refine_binary_raster(
            blank, reference, dot_cleanup_level=0, edge_refine_level=2)
        self.assertEqual(refined.getpixel((15, 12)), 0)
        self.assertEqual(refined.getpixel((27, 12)), 255)

    def test_all_three_modes_are_opt_in_and_remain_native_1bit(self):
        source = chart()
        for mode in ("floyd-steinberg", "bayer", "dizzy"):
            with self.subTest(mode=mode):
                baseline_profile = DitherProfile(mode=mode)
                baseline = render_thermal_image(source, baseline_profile)
                disabled = replace(
                    baseline_profile, smart_enhance=False,
                    postprocess_enabled=False, clahe_strength=0.9,
                    tone_strength=0.95, denoise_level=2,
                    dot_cleanup_level=3, edge_refine_level=3)
                self.assertEqual(
                    baseline.tobytes(), render_thermal_image(source, disabled).tobytes())
                experimental = replace(
                    baseline_profile, smart_enhance=True, clahe_strength=0.5,
                    denoise_level=1, tone_strength=0.25,
                    postprocess_enabled=True, dot_cleanup_level=1,
                    edge_refine_level=1)
                candidate = render_thermal_image(source, experimental)
                self.assertEqual(candidate.mode, "1")
                self.assertEqual(candidate.size, baseline.size)
                self.assertNotEqual(candidate.tobytes(), baseline.tobytes())

    def test_processing_parameters_validate_strictly(self):
        invalid = (
            {"smart_enhance": 1}, {"postprocess_enabled": "yes"},
            {"clahe_strength": -0.1}, {"clahe_strength": float("nan")},
            {"tone_strength": 1.01}, {"denoise_level": True},
            {"denoise_level": 3}, {"dot_cleanup_level": 4},
            {"edge_refine_level": -1}, {"edge_refine_level": 1.5},
        )
        for params in invalid:
            with self.subTest(params=params), self.assertRaises(ValueError):
                DitherProfile(**params)

    def test_old_v4_json_loads_disabled_v5_passes(self):
        configs = ComparisonProfiles()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            single = root / "single.json"
            all_modes = root / "comparison.json"
            original = asdict(configs.bayer)
            legacy = {k: v for k, v in original.items()
                      if k not in NEW_ENHANCEMENT_FIELDS}
            single.write_text(
                json.dumps({"schema_version": 4, **legacy}), encoding="utf-8")
            loaded = load_profile(single)
            self.assertEqual(loaded, configs.bayer)
            self.assertFalse(loaded.smart_enhance)
            self.assertFalse(loaded.postprocess_enabled)
            lanes = {}
            for mode in ("floyd-steinberg", "bayer", "threshold", "dizzy"):
                lanes[mode] = {
                    k: v for k, v in asdict(configs.by_mode(mode)).items()
                    if k not in NEW_ENHANCEMENT_FIELDS
                }
            all_modes.write_text(
                json.dumps({"schema_version": 4, "lanes": lanes}),
                encoding="utf-8")
            self.assertEqual(load_comparison(all_modes), configs)

    def test_v5_preset_roundtrip_keeps_lane_independence(self):
        configs = ComparisonProfiles().replace_lane(replace(
            DitherProfile(mode="dizzy"), smart_enhance=True,
            postprocess_enabled=True, clahe_strength=0.64,
            dot_cleanup_level=3, edge_refine_level=2))
        with tempfile.TemporaryDirectory() as folder:
            single, compare = Path(folder) / "single.json", Path(folder) / "compare.json"
            save_profile(single, configs.dizzy)
            save_comparison(compare, configs)
            self.assertEqual(load_profile(single), configs.dizzy)
            self.assertEqual(load_comparison(compare), configs)
            self.assertEqual(json.loads(single.read_text())["schema_version"], 5)
            self.assertEqual(json.loads(compare.read_text())["schema_version"], 5)
            self.assertFalse(configs.floyd.smart_enhance)


if __name__ == "__main__":
    unittest.main()
