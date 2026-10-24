"""Regression checks for full-range Dizzy CPU grayscale fidelity reporting."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from tools.dizzy_fidelity import measure_fidelity, plot_svg, write_fidelity_report


class DizzyFidelityTests(unittest.TestCase):
    def test_measured_tones_include_digital_response_for_both_variants(self):
        levels = (0, 16, 32, 96, 128, 192, 224, 240, 255)
        report = measure_fidelity(width=96, height=96, seed=42, tones=levels)
        self.assertEqual(report["metadata"]["tones"], list(levels))
        self.assertFalse(report["metadata"]["paper_calibrated"])
        self.assertEqual(len(report["rows"]), len(levels) * 2)
        for variant in ("article-8", "orthogonal-4"):
            stats = report["summary"][variant]
            self.assertEqual(stats["levels_measured"], len(levels))
            self.assertLess(stats["mae_after_pp"], stats["mae_before_pp"])
            self.assertGreater(stats["improvement_pct"], 0)
        for row in report["rows"]:
            self.assertTrue(0 <= row["target_white_pct"] <= 100)
            self.assertTrue(0 <= row["baseline_white_pct"] <= 100)
            self.assertTrue(0 <= row["calibrated_white_pct"] <= 100)

    def test_export_csv_json_svg_is_valid_and_offline(self):
        report = measure_fidelity(
            width=32, height=32, tones=(0, 64, 128, 255))
        with tempfile.TemporaryDirectory() as folder:
            csv_path, json_path, svg_path = write_fidelity_report(report, Path(folder))
            with csv_path.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 8)
            saved = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["metadata"]["width"], 32)
            self.assertEqual(len(saved["rows"]), 8)
            root = ET.parse(svg_path).getroot()
            self.assertTrue(root.tag.endswith("svg"))
            self.assertIn("orthogonal-4", svg_path.read_text(encoding="utf-8"))
            self.assertIn("article-8", plot_svg(report))

    def test_invalid_audit_inputs_rejected(self):
        kwargs = (
            {"width": 0}, {"height": 4000}, {"seed": -1},
            {"seed": True}, {"tones": []}, {"tones": (0, 300)},
            {"tones": (0, 0)}, {"variants": ("unknown",)},
        )
        for params in kwargs:
            with self.subTest(params=params), self.assertRaises(ValueError):
                measure_fidelity(**params)


if __name__ == "__main__":
    unittest.main()
