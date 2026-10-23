"""Headless Tk runtime smoke tests for the experimental Enhanced Dizzy switch.

Run under Xvfb on Linux. This creates a GUI but never accesses hardware,
sets printer settings, or submits a print job.
"""
from dataclasses import replace
from pathlib import Path
import tempfile
from unittest.mock import patch
import time
import tkinter as tk
from tkinter import ttk
import unittest

from photobooth.dither_lab import ComparisonProfiles, load_comparison
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

    def test_auto_tune_dialog_save_then_apply_best_is_floyd_only(self):
        """Exercise the real async search, preview dialog and 1-bit Apply."""
        self.app.sync.set(True)
        prior_bayer = self.app.configs.bayer
        prior_dizzy = self.app.configs.dizzy
        previous_floyd = self.app.configs.floyd
        self.app.start_auto_tune()
        self.assertTrue(self.app.autotune_busy)
        self.assertEqual(self.app.autotune_button.cget("text"), "Cancel Tune")
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline and self.app.autotune_result is None:
            self.root.update()
            time.sleep(0.025)
        self.assertIsNotNone(self.app.autotune_result, "search did not finish")
        self.assertEqual(self.app.autotune_button.cget("text"), "Auto Tune")
        self.assertEqual(len(self.app.autotune_result.candidates), 3)
        self.assertIn("System neutral:", self.app.autotune_baseline_text)
        self.assertIsNotNone(self.app.autotune_dialog)
        self.assertTrue(self.app.autotune_dialog.winfo_exists())
        self.assertEqual(self.app.configs.floyd, previous_floyd)
        # Preset save must not silently modify the current kiosk/lab params.
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "auto-only.json"
            with patch(
                "tools.dither_compare_gui.filedialog.asksaveasfilename",
                return_value=str(target),
            ):
                self.app.save_auto_tune_preset()
            saved = load_comparison(target)
            self.assertTrue(saved.floyd.enhanced_floyd)
            self.assertEqual(saved.bayer, prior_bayer)
            self.assertEqual(saved.dizzy, prior_dizzy)
            self.assertEqual(self.app.configs.floyd, previous_floyd)

        expected = self.app.autotune_result.candidates[0]
        self.app.apply_auto_tune_candidate(0)
        self.assertEqual(self.app.configs.floyd, expected.profile)
        self.assertEqual(self.app.configs.bayer, prior_bayer)
        self.assertEqual(self.app.configs.dizzy, prior_dizzy)
        self.assertFalse(self.app.autotune_busy)
        self.assertIsNone(self.app.autotune_result)
        self.assertTrue(self.app.enhanced_floyd.get())
        actual = self._wait_for_ready("floyd-steinberg")
        self.assertEqual(actual.mode, "1")
        self.assertEqual(actual.tobytes(), expected.raster.tobytes())

    def test_all_visible_lanes_have_independent_buttons(self):
        self.assertEqual(set(self.app.autotune_buttons),
                         {"floyd-steinberg", "bayer", "dizzy"})
        self.app.sync.set(True)
        for mode in ("bayer", "dizzy"):
            with self.subTest(mode=mode):
                original = self.app.configs
                self.app.start_auto_tune(mode)
                self.assertTrue(self.app.autotune_busy)
                self.assertEqual(self.app.autotune_mode, mode)
                self.assertEqual(self.app.autotune_buttons[mode].cget("text"),
                                 "Cancel Tune")
                self.app.start_auto_tune(mode)
                self.assertFalse(self.app.autotune_busy)
                self.assertEqual(self.app.configs, original)

    def test_tuned_profile_applies_only_to_own_lane(self):
        # Avoid expensive GUI search: test exact candidate-to-lane application.
        from photobooth.dither_autotune import AutoTuneCandidate, AutoTuneResult
        from photobooth.dither_lab import DitherProfile, render_thermal_image
        for mode in ("bayer", "dizzy"):
            with self.subTest(mode=mode):
                original = self.app.configs
                p = DitherProfile(mode=mode, brightness=1.12, contrast=1.18,
                                  smart_enhance=True, clahe_strength=0.58,
                                  denoise_level=2, tone_strength=0.34,
                                  postprocess_enabled=True, dot_cleanup_level=2,
                                  edge_refine_level=2,
                                  enhanced_dizzy=(mode == "dizzy"),
                                  dizzy_variant="orthogonal-4" if mode == "dizzy"
                                  else "article-8")
                candidate = AutoTuneCandidate(p, render_thermal_image(self.app.source, p),
                                              90.0, 2.0, 3.0, 35.0)
                self.app.autotune_mode = mode
                self.app.autotune_result = AutoTuneResult((candidate,), 1, candidate)
                self.app.autotune_selected = tk.IntVar(value=0)
                self.app.sync.set(True)
                self.app.apply_auto_tune_candidate(0)
                self.assertEqual(self.app.configs.by_mode(mode), p)
                for other in ("floyd-steinberg", "bayer", "dizzy"):
                    if other != mode:
                        self.assertEqual(self.app.configs.by_mode(other),
                                         original.by_mode(other))
                self.assertTrue(self.app.pipeline_flags[mode]["smart_enhance"].get())
                self.assertTrue(self.app.pipeline_flags[mode]["postprocess_enabled"].get())
                self.assertAlmostEqual(
                    self.app.pipeline_controls[mode]["clahe_strength"][0].get(), 0.58)
                if mode == "dizzy":
                    self.assertTrue(self.app.enhanced_dizzy.get())
                    self.assertEqual(self.app.dizzy_variant.get(), "orthogonal-4")

    def test_opt_in_processing_controls_are_per_lane_even_with_sync(self):
        from photobooth.dither_lab import DitherProfile
        self.app.sync.set(True)
        for mode in ("floyd-steinberg", "bayer", "dizzy"):
            with self.subTest(mode=mode):
                original = self.app.configs
                old_versions = dict(self.app.versions)
                self.assertFalse(self.app.pipeline_flags[mode]["smart_enhance"].get())
                self.assertFalse(self.app.pipeline_flags[mode]["postprocess_enabled"].get())
                self.app.pipeline_flags[mode]["smart_enhance"].set(True)
                self.app.pipeline_toggle(mode, "smart_enhance")
                self.assertTrue(self.app.configs.by_mode(mode).smart_enhance)
                self.assertEqual(self.app.versions[mode], old_versions[mode] + 1)
                for other in ("floyd-steinberg", "bayer", "dizzy"):
                    if other != mode:
                        self.assertEqual(self.app.configs.by_mode(other),
                                         original.by_mode(other))
                        self.assertEqual(self.app.versions[other],
                                         old_versions[other])
                self.app.apply_configs(original)

    def test_quick_ab_modes_are_isolated_and_keep_manual_sliders(self):
        mode = "bayer"
        initial = self.app.configs
        self.app.sync.set(True)
        version = dict(self.app.versions)
        self.app.processing_presets[mode].set("Smart + Post")
        self.app.processing_preset_changed(mode)
        self.assertTrue(self.app.configs.bayer.smart_enhance)
        self.assertTrue(self.app.configs.bayer.postprocess_enabled)
        self.assertEqual(self.app.versions[mode], version[mode] + 1)
        self.assertEqual(self.app.configs.floyd, initial.floyd)
        self.assertEqual(self.app.configs.dizzy, initial.dizzy)
        self.assertEqual(self.app.configs.bayer.brightness, initial.bayer.brightness)
        self.assertIn("-smart-post.png", self.app.raster_filename(self.app.configs.bayer))
        self.app.processing_presets[mode].set("Original")
        self.app.processing_preset_changed(mode)
        self.assertEqual(self.app.configs.bayer, initial.bayer)
        self.assertIn("Original", self.app.processing_presets[mode].get())

    def test_advanced_processing_sliders_and_preset_refresh(self):
        from dataclasses import replace
        mode = "bayer"
        button, advanced = self.app.pipeline_sections[mode]
        self.assertFalse(advanced.winfo_manager())
        self.app.toggle_pipeline_options(mode)
        self.assertTrue(advanced.winfo_manager())
        self.app.toggle_pipeline_options(mode)
        self.assertFalse(advanced.winfo_manager())
        saved = self.app.configs.replace_lane(replace(
            self.app.configs.bayer, smart_enhance=True,
            clahe_strength=0.67, denoise_level=2,
            tone_strength=0.45, postprocess_enabled=True,
            dot_cleanup_level=3, edge_refine_level=2))
        self.app.apply_configs(saved)
        self.assertTrue(self.app.pipeline_flags[mode]["smart_enhance"].get())
        self.assertTrue(self.app.pipeline_flags[mode]["postprocess_enabled"].get())
        self.assertAlmostEqual(
            self.app.pipeline_controls[mode]["clahe_strength"][0].get(), 0.67)
        self.assertEqual(
            round(self.app.pipeline_controls[mode]["dot_cleanup_level"][0].get()), 3)
        self.app.reset()
        self.assertFalse(self.app.configs.bayer.smart_enhance)
        self.assertFalse(self.app.configs.bayer.postprocess_enabled)

    def test_processing_toggle_never_calls_print(self):
        with patch.object(self.app, "_start_print") as printer:
            mode = "bayer"
            self.app.pipeline_flags[mode]["postprocess_enabled"].set(True)
            self.app.pipeline_toggle(mode, "postprocess_enabled")
            self.app.pipeline_controls[mode]["edge_refine_level"][0].set(2.0)
            self.app.pipeline_changed(mode, "edge_refine_level")
            printer.assert_not_called()
            self.assertEqual(self.app.configs.bayer.edge_refine_level, 2)

    def test_auto_tune_cancel_invalidates_pending_results(self):
        self.app.start_auto_tune()
        self.assertTrue(self.app.autotune_busy)
        old_gen = self.app.autotune_generation
        self.app.controls["floyd-steinberg"]["contrast"][0].set(1.13)
        self.app.slider_changed("floyd-steinberg", "contrast")
        self.assertGreater(self.app.autotune_generation, old_gen)
        self.assertFalse(self.app.autotune_busy)
        self.assertIsNone(self.app.autotune_result)
        self.assertEqual(self.app.autotune_button.cget("text"), "Auto Tune")
        self.root.update()  # Pending events from the cancelled worker are stale.
        self.assertIsNone(self.app.autotune_result)

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
