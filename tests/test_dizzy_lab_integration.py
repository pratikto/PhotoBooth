"""Integration tests for a lab-only fourth (Dizzy) comparison lane."""
import ast
from dataclasses import asdict, replace
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from photobooth.dither_lab import (
    LAB_DITHER_MODES, ComparisonProfiles, DitherProfile,
    load_comparison, load_profile, render_thermal_image,
    save_comparison, save_profile,
)
from photobooth.printer import DITHER_MODES


class DizzyLabIntegrationTests(unittest.TestCase):
    def test_production_modes_unchanged_and_new_lab_mode(self):
        self.assertEqual(DITHER_MODES,
                         ("floyd-steinberg", "bayer", "threshold"))
        self.assertEqual(LAB_DITHER_MODES, DITHER_MODES + ("dizzy",))

    def test_dizzy_lane_independent_and_one_bit(self):
        profiles = ComparisonProfiles()
        newer = profiles.replace_lane(replace(
            profiles.dizzy, dizzy_variant="orthogonal-4", gamma=1.15))
        self.assertEqual(newer.floyd, profiles.floyd)
        self.assertEqual(newer.bayer, profiles.bayer)
        self.assertEqual(newer.threshold, profiles.threshold)
        gray = Image.new("L", (72, 49))
        gray.putdata([(x * 3 + y * 5) % 256
                      for y in range(49) for x in range(72)])
        a = render_thermal_image(gray, profiles.dizzy)
        b = render_thermal_image(gray, newer.dizzy)
        self.assertEqual(a.mode, "1")
        self.assertEqual(a.size, gray.size)
        self.assertNotEqual(a.tobytes(), b.tobytes())

    def test_v3_profile_and_four_lane_roundtrip(self):
        configs = ComparisonProfiles().replace_lane(
            DitherProfile(mode="dizzy", dizzy_seed=7, dizzy_variant="orthogonal-4"))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            json_path = root / "four.json"
            profile_path = root / "profile.json"
            save_comparison(json_path, configs)
            self.assertEqual(load_comparison(json_path), configs)
            save_profile(profile_path, configs.dizzy)
            self.assertEqual(load_profile(profile_path), configs.dizzy)

    def test_legacy_v2_comparison_loads_dizzy_disabled(self):
        # Old saved configs had precisely three lanes, without Dizzy options.
        profiles = ComparisonProfiles()
        lanes = {}
        for mode in DITHER_MODES:
            values = asdict(profiles.by_mode(mode))
            values.pop("dizzy_seed")
            values.pop("dizzy_variant")
            lanes[mode] = values
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "v2.json"
            path.write_text(json.dumps({"schema_version": 2, "lanes": lanes}),
                            encoding="utf-8")
            loaded = load_comparison(path)
            self.assertEqual(loaded.dizzy.dizzy_variant, "article-8")
            self.assertEqual(loaded.dizzy.dizzy_seed, 42)
            self.assertEqual(loaded.floyd, profiles.floyd)

    def test_dizzy_validation(self):
        for kwargs in ({"dizzy_variant": "bad", "mode": "dizzy"},
                       {"dizzy_seed": True, "mode": "dizzy"},
                       {"dizzy_seed": -3, "mode": "dizzy"},
                       {"mode": "bayer", "dizzy_seed": 10}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                DitherProfile(**kwargs)

    def test_gui_syntax_has_dizzy_lane_and_selection(self):
        file = Path(__file__).resolve().parents[1] / "tools" / "dither_compare_gui.py"
        source = file.read_text(encoding="utf-8")
        ast.parse(source, filename=str(file))
        self.assertIn("LAB_DITHER_MODES", source)
        self.assertIn("def change_dizzy_variant(self,", source)
        self.assertIn("Export 4 PNG", source)


if __name__ == "__main__":
    unittest.main()
