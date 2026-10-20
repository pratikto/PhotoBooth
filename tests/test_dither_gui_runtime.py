"""Headless Tk runtime smoke tests for the experimental Enhanced Dizzy switch.

Run under Xvfb on Linux. This creates a GUI but never accesses hardware,
sets printer settings, or submits a print job.
"""
from dataclasses import replace
import time
import tkinter as tk
from tkinter import ttk
import unittest

from photobooth.dither_lab import ComparisonProfiles
from tools.dither_compare_gui import ComparisonApp


def _descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from _descendants(child)


class EnhancedDizzyTkTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = ComparisonApp(self.root)

    def tearDown(self):
        self.app.close()

    def _wait_for_ready(self, mode="dizzy", timeout=20):
        limit = time.monotonic() + timeout
        while time.monotonic() < limit:
            self.root.update()
            if self.app.ready(mode):
                return self.app.results[mode].copy()
            time.sleep(0.025)
        self.fail(f"GUI did not finish {mode} rendering within {timeout}s")

    def test_checkbox_is_present_and_only_changes_dizzy_lane(self):
        names = [
            child.cget("text")
            for child in _descendants(self.root)
            if isinstance(child, ttk.Checkbutton)
        ]
        self.assertIn("Enhanced Dizzy (experimental)", names)
        self.assertIn("Enhanced Floyd (experimental)", names)
        self.assertEqual(set(self.app.controls), {"floyd-steinberg", "bayer", "dizzy"})
        prior = dict(self.app.versions)
        self.app.enhanced_dizzy.set(True)
        self.app.toggle_enhanced_dizzy()
        self.assertTrue(self.app.configs.dizzy.enhanced_dizzy)
        self.assertFalse(self.app.configs.floyd.enhanced_floyd)
        self.assertEqual(self.app.versions["dizzy"], prior["dizzy"] + 1)
        for mode in ("floyd-steinberg", "bayer"):
            self.assertEqual(self.app.versions[mode], prior[mode])
        self.assertIn("-enhanced.png", self.app.raster_filename(self.app.configs.dizzy))
        self.app.apply_configs(ComparisonProfiles())
        self.assertFalse(self.app.enhanced_dizzy.get())
        self.assertFalse(self.app.configs.dizzy.enhanced_dizzy)

    def test_enhancement_switches_are_in_respective_panels(self):
        # This checks actual widget ancestry, not just matching source text.
        checks = [
            widget for widget in _descendants(self.root)
            if isinstance(widget, ttk.Checkbutton)
        ]
        for label, panel_label in (
            ("Enhanced Floyd (experimental)", "Floyd–Steinberg"),
            ("Enhanced Dizzy (experimental)", "Dizzy Dithering"),
        ):
            with self.subTest(label=label):
                matches = [w for w in checks if w.cget("text") == label]
                self.assertEqual(len(matches), 1)
                self.assertIsInstance(matches[0].master, ttk.LabelFrame)
                self.assertEqual(matches[0].master.cget("text"), panel_label)

        # Sync Parameters must never synchronize per-algorithm enhancement.
        self.app.sync.set(True)
        prior = dict(self.app.versions)
        floyd_check = next(
            w for w in checks if w.cget("text") == "Enhanced Floyd (experimental)")
        floyd_check.invoke()
        self.assertTrue(self.app.enhanced_floyd.get())
        self.assertTrue(self.app.configs.floyd.enhanced_floyd)
        self.assertFalse(self.app.configs.dizzy.enhanced_dizzy)
        self.assertEqual(self.app.versions["floyd-steinberg"],
                         prior["floyd-steinberg"] + 1)
        self.assertEqual(self.app.versions["bayer"], prior["bayer"])
        self.assertEqual(self.app.versions["dizzy"], prior["dizzy"])

        self.app.apply_configs(ComparisonProfiles())
        self.assertFalse(self.app.enhanced_floyd.get())
        self.assertFalse(self.app.enhanced_dizzy.get())

    def test_actual_gui_worker_renders_distinct_baseline_enhanced_rasters(self):
        baseline = self._wait_for_ready()
        self.assertEqual(baseline.mode, "1")
        self.assertEqual(baseline.width, 576)
        before = self.app.ready_profiles["dizzy"]
        self.app.enhanced_dizzy.set(True)
        self.app.toggle_enhanced_dizzy()
        self.assertFalse(self.app.ready("dizzy"))
        enhanced = self._wait_for_ready()
        self.assertNotEqual(baseline.tobytes(), enhanced.tobytes())
        self.assertFalse(before.enhanced_dizzy)
        self.assertTrue(self.app.ready_profiles["dizzy"].enhanced_dizzy)
        self.assertIn("enhanced", self.app.statuses["dizzy"].cget("text"))
        # The 1-bit result remains print-ready without secondary dithering.
        self.assertEqual(enhanced.mode, "1")
        self.assertEqual(enhanced.size, baseline.size)


if __name__ == "__main__":
    unittest.main()
