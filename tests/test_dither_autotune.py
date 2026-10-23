"""Headless, hardware-free FEAT-011 Auto Tune quality/search tests."""
from dataclasses import replace
import unittest

from PIL import Image, ImageChops, ImageFilter

from photobooth.dither_autotune import (
    AutoTuneCancelled, _photo_gray, score_print_proxy, tune_dither, tune_enhanced_floyd,
)
from photobooth.dither_lab import DitherProfile, render_thermal_image


def portrait_fixture():
    """Synthetic image with gradients, dark hair, edge/detail and skin midtones."""
    image = Image.new("RGB", (112, 144))
    image.putdata([
        (
            min(255, int(200 - y * 0.9 + ((x * 11 + y * 7) % 9))),
            min(255, int(168 - y * 0.7 + ((x * 3 + y * 13) % 13))),
            min(255, int(140 - y * 0.55 + ((x + y * 3) % 11))),
        ) if 17 < x < 98 and 22 < y < 115 else (
            25 if (x // 8 + y // 9) % 5 == 0 else
            239 if x > 52 else 78,
        ) * 3
        for y in range(144) for x in range(112)
    ])
    return image


class AutoTuneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = portrait_fixture()

    def test_native_candidates_are_ranked_distinct_and_enhanced(self):
        baseline = DitherProfile(
            brightness=0.87, contrast=1.36, gamma=1.09, sharpness=1.12)
        source_before = self.source.tobytes()
        progress = []
        report = tune_enhanced_floyd(
            self.source, baseline,
            on_progress=lambda n, phase: progress.append((n, phase)))
        self.assertEqual(len(report.candidates), 3)
        self.assertGreaterEqual(report.trials, 3)
        self.assertLessEqual(report.trials, 115)
        self.assertEqual(report.trials, progress[-1][0])
        self.assertEqual([c.score for c in report.candidates],
                         sorted((c.score for c in report.candidates), reverse=True))
        signatures = set()
        for candidate in report.candidates:
            p = candidate.profile
            self.assertEqual(p.mode, "floyd-steinberg")
            self.assertTrue(p.enhanced_floyd)
            self.assertEqual(p.width_dots, 576)
            self.assertEqual(candidate.raster.mode, "1")
            self.assertEqual(candidate.raster.size, self.source.size)
            self.assertEqual(
                candidate.raster.tobytes(),
                render_thermal_image(self.source, p).tobytes())
            self.assertGreaterEqual(candidate.score, 0)
            self.assertLessEqual(candidate.score, 100)
            self.assertGreaterEqual(candidate.black_coverage, 0)
            self.assertLessEqual(candidate.black_coverage, 100)
            signatures.add(p)
        self.assertEqual(len(signatures), 3)
        self.assertEqual(self.source.tobytes(), source_before)
        self.assertFalse(baseline.enhanced_floyd)  # no implicit apply

    def test_manual_parameters_do_not_influence_candidates(self):
        reports = []
        for enhanced in (False, True):
            original = DitherProfile(brightness=0.5, contrast=2.5, gamma=0.3,
                                     sharpness=3.0, enhanced_floyd=enhanced)
            result = tune_enhanced_floyd(self.source, original)
            reports.append(result)
            self.assertEqual(result.baseline.profile, DitherProfile(enhanced_floyd=True))
            self.assertEqual(result.baseline.raster.tobytes(),
                             render_thermal_image(self.source, DitherProfile(enhanced_floyd=True)).tobytes())
            neutral = DitherProfile(enhanced_floyd=True)
            neutral_score = score_print_proxy(
                render_thermal_image(self.source, neutral),
                _photo_gray(self.source, neutral.width_dots), neutral)[0]
            self.assertGreaterEqual(result.candidates[0].score, round(neutral_score, 3))
            self.assertLessEqual(result.trials, 115)

        reports.append(tune_enhanced_floyd(self.source, DitherProfile(
            brightness=1.75, contrast=0.5, gamma=3.0, sharpness=0.0)))
        expected = [(c.profile, c.score, c.raster.tobytes()) for c in reports[0].candidates]
        for result in reports[1:]:
            self.assertEqual(expected, [(c.profile, c.score, c.raster.tobytes())
                                        for c in result.candidates])

    def test_small_midtone_is_scored_as_blended_dots(self):
        source = Image.new("L", (96, 96), 128)
        p = DitherProfile()
        raster = render_thermal_image(source, p)
        score, tone, _, _ = score_print_proxy(raster, source, p)
        # A faithful 50% halftone must not incur raw per-dot error near 127.
        self.assertLess(tone, 20)
        self.assertGreater(score, 80)

    def test_invalid_profile_type_has_clear_error(self):
        with self.assertRaises(TypeError):
            tune_enhanced_floyd(self.source, None)

    def test_repeatable_search_and_rankings(self):
        profile = DitherProfile(width_dots=384, enhanced_floyd=True)
        first = tune_enhanced_floyd(self.source, profile)
        second = tune_enhanced_floyd(self.source, profile)
        self.assertEqual(
            [(c.profile, c.score, c.raster.tobytes()) for c in first.candidates],
            [(c.profile, c.score, c.raster.tobytes()) for c in second.candidates],
        )

    def test_mode_restricted_to_floyd(self):
        with self.assertRaises(ValueError):
            tune_enhanced_floyd(self.source, DitherProfile(mode="dizzy"))
        with self.assertRaises(ValueError):
            tune_enhanced_floyd(self.source, DitherProfile(mode="bayer"))

    def test_each_algorithm_has_independent_neutral_search(self):
        photo = self.source.resize((42, 55))
        for mode in ("bayer", "dizzy", "threshold"):
            with self.subTest(mode=mode):
                manual = DitherProfile(
                    mode=mode, width_dots=384, brightness=1.7,
                    contrast=2.0, gamma=2.2, sharpness=2.8,
                    enhanced_dizzy=(mode == "dizzy"),
                    dizzy_variant="orthogonal-4" if mode == "dizzy" else "article-8",
                    threshold=180 if mode == "threshold" else 128,
                )
                report = tune_dither(photo, manual)
                self.assertEqual(len(report.candidates), 3)
                self.assertEqual(report.baseline.profile.mode, mode)
                self.assertEqual(report.baseline.profile.width_dots, 384)
                self.assertEqual(report.baseline.profile.brightness, 1.0)
                self.assertEqual(report.baseline.profile.contrast, 1.0)
                self.assertEqual(report.baseline.profile.gamma, 1.0)
                self.assertEqual(report.baseline.profile.sharpness, 1.0)
                if mode == "dizzy":
                    self.assertFalse(report.baseline.profile.enhanced_dizzy)
                    self.assertEqual(report.baseline.profile.dizzy_variant, "article-8")
                for candidate in report.candidates:
                    self.assertEqual(candidate.profile.mode, mode)
                    self.assertEqual(candidate.raster.mode, "1")
                    self.assertEqual(candidate.raster.size, photo.size)
                    self.assertEqual(
                        candidate.raster.tobytes(),
                        render_thermal_image(photo, candidate.profile).tobytes(),
                    )
                neutral = tune_dither(photo, DitherProfile(mode=mode, width_dots=384))
                self.assertEqual(
                    [(c.profile, c.score) for c in report.candidates],
                    [(c.profile, c.score) for c in neutral.candidates],
                )

    def test_all_mode_cancellation_and_floyd_compatibility(self):
        for mode in ("bayer", "dizzy", "threshold"):
            with self.subTest(mode=mode):
                with self.assertRaises(AutoTuneCancelled):
                    tune_dither(self.source, DitherProfile(mode=mode),
                                should_cancel=lambda: True)
        photo = self.source.resize((44, 60))
        p = DitherProfile()
        old = tune_enhanced_floyd(photo, p)
        new = tune_dither(photo, p)
        self.assertEqual([(x.profile, x.score) for x in old.candidates],
                         [(x.profile, x.score) for x in new.candidates])

    def test_cancel_before_start_and_during_search(self):
        with self.assertRaises(AutoTuneCancelled):
            tune_enhanced_floyd(
                self.source, DitherProfile(), should_cancel=lambda: True)
        state = {"n": 0}
        def on_progress(n, _phase):
            state["n"] = n
        with self.assertRaises(AutoTuneCancelled):
            tune_enhanced_floyd(
                self.source, DitherProfile(),
                should_cancel=lambda: state["n"] >= 3,
                on_progress=on_progress)
        self.assertGreaterEqual(state["n"], 3)

    def test_relative_score_prefers_faithful_tones_over_inversion(self):
        source = Image.new("L", (120, 80))
        source.putdata([int((x / 119) * 255)
                        for y in range(80) for x in range(120)])
        p = DitherProfile()
        reference = _photo_gray(source, p.width_dots)
        good = render_thermal_image(source, p)
        bad = good.convert("L").point(lambda color: 255 - color).convert(
            "1", dither=Image.Dither.NONE)
        good_score, _, _, _ = score_print_proxy(good, reference, p)
        bad_score, _, _, _ = score_print_proxy(bad, reference, p)
        self.assertGreater(good_score, bad_score)

    def test_bad_score_shape_rejected(self):
        image = Image.new("1", (30, 20))
        with self.assertRaises(ValueError):
            score_print_proxy(image, Image.new("L", (29, 20)), DitherProfile())
        with self.assertRaises(ValueError):
            score_print_proxy(image.convert("RGB"), Image.new("L", (30, 20)),
                              DitherProfile())

    def test_no_global_optimum_claim_uses_only_local_metrics(self):
        # No network, trainable weights, face recognition or thermal darkness
        # changes. The result is a reproducible offline proxy, not an oracle.
        p = DitherProfile()
        report = tune_enhanced_floyd(Image.new("L", (60, 80), 255), p)
        self.assertEqual(len(report.candidates), 3)
        self.assertEqual(report.candidates[0].raster.mode, "1")
        for candidate in report.candidates:
            self.assertTrue(candidate.profile.enhanced_floyd)
            self.assertTrue(all(
                0 <= candidate.raster.getpixel((x, y)) <= 255
                for x, y in ((0, 0), (40, 20), (59, 79))
            ))


if __name__ == "__main__":
    unittest.main()
