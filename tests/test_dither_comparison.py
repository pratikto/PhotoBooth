"""Offline tests for independently tunable three-algorithm comparisons."""
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from PIL import Image
from photobooth.dither_lab import (ComparisonProfiles, DitherProfile,
                                   save_comparison, load_comparison, render_thermal_image)


class ComparisonTests(unittest.TestCase):
    def test_each_lane_is_independent(self):
        all_three = ComparisonProfiles()
        newer = all_three.replace_lane(replace(all_three.bayer, contrast=1.7))
        self.assertEqual(newer.bayer.contrast, 1.7)
        self.assertEqual(newer.floyd, all_three.floyd)
        self.assertEqual(newer.threshold, all_three.threshold)

    def test_save_load_round_trip_preserves_each_lane(self):
        p = ComparisonProfiles(
            DitherProfile(mode="floyd-steinberg", gamma=1.2),
            DitherProfile(mode="bayer", brightness=1.3),
            DitherProfile(mode="threshold", threshold=170))
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "comparison.json"
            save_comparison(target, p)
            self.assertEqual(load_comparison(target), p)

    def test_malformed_mode_cannot_be_swapped(self):
        with self.assertRaises(ValueError):
            ComparisonProfiles(bayer=DitherProfile(mode="threshold"))
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "bad.json"
            target.write_text('{"schema_version":1,"lanes":{}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_comparison(target)

    def test_three_modes_generate_distinct_one_bit_outputs(self):
        gray = Image.new("L", (576, 256))
        gray.putdata([(x + y) % 256 for y in range(256) for x in range(576)])
        modes = ComparisonProfiles()
        output = [render_thermal_image(gray, modes.by_mode(mode)) for mode in
                  ("floyd-steinberg", "bayer", "threshold")]
        self.assertTrue(all(image.mode == "1" for image in output))
        self.assertEqual(len({image.tobytes() for image in output}), 3)


if __name__ == "__main__":
    unittest.main()
