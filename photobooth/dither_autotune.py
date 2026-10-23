"""Offline, deterministic auto-tuning for Enhanced Floyd in Meong's test lab.

This is a **heuristic** visual-fidelity search, not a physical thermal-printer
calibration or an AI face-quality classifier. No data leaves this process, no
printer is accessed, and the caller must explicitly apply a candidate.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from PIL import Image, ImageChops, ImageFilter, ImageStat

from photobooth.dither_lab import DitherProfile, render_thermal_image

# Keep the candidate budget bounded so the desktop GUI remains responsive.
SEARCH_STEPS = (
    (0.17, 0.30, 0.32, 0.55),
    (0.085, 0.16, 0.16, 0.28),
    (0.042, 0.08, 0.08, 0.14),
)
TUNING_FIELDS = ("brightness", "contrast", "gamma", "sharpness")
BOUNDS = ((0.5, 1.75), (0.5, 2.5), (0.3, 3.0), (0.0, 3.0))
SHORTLIST_SIZE = 8
PROXY_MAX_SIZE = (384, 520)


class AutoTuneCancelled(Exception):
    """The GUI changed input/parameters or the user cancelled the search."""


@dataclass(frozen=True)
class AutoTuneCandidate:
    profile: DitherProfile
    raster: Image.Image
    score: float
    tone_error: float  # Perceptual proxy in 0-255 gray units, lower is better.
    edge_error: float  # Simplified local structure error, lower is better.
    black_coverage: float


@dataclass(frozen=True)
class AutoTuneResult:
    candidates: tuple[AutoTuneCandidate, ...]
    trials: int
    baseline: AutoTuneCandidate  # Exact original settings, including enhancement flag.
    # No network, trained AI, facial recognition or automatic printer actions.


def _photo_gray(source: Image.Image, width_dots: int) -> Image.Image:
    """Mirror the production lab's white-alpha/grayscale/resize baseline."""
    rgba = source.convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    gray = Image.alpha_composite(white, rgba).convert("L")
    if gray.width > width_dots:
        height = max(1, round(gray.height * width_dots / gray.width))
        gray = gray.resize((width_dots, height), Image.Resampling.LANCZOS)
    return gray


def score_print_proxy(
    raster: Image.Image, reference_gray: Image.Image, profile: DitherProfile,
) -> tuple[float, float, float, float]:
    """Estimate fidelity after black/white dots blend at viewing distance.

    Compare a box-averaged *native 1-bit print raster* with the same image's
    source grayscale. This avoids the monitor's nearest-neighbor dot aliasing.
    The score has no absolute clinical/perceptual meaning; different papers,
    printheads and viewing conditions can reverse its ranking.
    """
    if raster.mode != "1" or raster.size != reference_gray.size:
        raise ValueError("Scoring requires same-sized 1-bit raster and grayscale input.")

    width, height = raster.size
    small_width = max(1, min(192, width // 3))
    small_height = max(1, round(height * small_width / width))
    box_size = (small_width, small_height)

    original = reference_gray.resize(box_size, Image.Resampling.BOX)
    reconstructed = raster.convert("L").resize(box_size, Image.Resampling.BOX)
    tone_error = ImageStat.Stat(ImageChops.difference(
        original, reconstructed)).mean[0]

    # A little blurring makes this a coarse edge-structure proxy rather than
    # an unhelpful comparison of isolated error-diffusion dot boundaries.
    original_edges = original.filter(
        ImageFilter.GaussianBlur(0.5)).filter(ImageFilter.FIND_EDGES)
    print_edges = reconstructed.filter(
        ImageFilter.GaussianBlur(0.5)).filter(ImageFilter.FIND_EDGES)
    edge_error = ImageStat.Stat(ImageChops.difference(
        original_edges, print_edges)).mean[0]

    black_coverage = 100 * raster.histogram()[0] / (width * height)
    reference_blackness = 100 * (255 - ImageStat.Stat(
        reference_gray).mean[0]) / 255
    coverage_deviation = abs(black_coverage - reference_blackness)

    # Discourage extreme slider settings even when the dot-averaging metric
    # rewards them on a noisy image; do not impose a universal ink-coverage %.
    penalty = sum(abs(getattr(profile, field) - 1.0) / span
                  for field, span in zip(TUNING_FIELDS, (0.75, 1.5, 2.0, 2.0)))
    score = max(0.0, min(
        100.0,
        100.0 - (0.72 * tone_error + 0.16 * edge_error +
                 0.11 * coverage_deviation + 0.65 * penalty),
    ))
    return score, tone_error, edge_error, black_coverage


def _signature(profile: DitherProfile) -> tuple[float, ...]:
    return tuple(getattr(profile, field) for field in TUNING_FIELDS)


def _search_neighbor(profile: DitherProfile, field: str,
                     amount: float, bounds: tuple[float, float]) -> DitherProfile:
    value = max(bounds[0], min(bounds[1], getattr(profile, field) + amount))
    return replace(profile, **{field: round(value, 3)})


def tune_enhanced_floyd(
    source: Image.Image,
    starting_profile: DitherProfile,
    *,
    should_cancel: Callable[[], bool] | None = None,
    on_progress: Callable[[int, str], None] | None = None,
) -> AutoTuneResult:
    """Return three ranked native-size candidates; never alter caller state.

    Two coarse-to-fine searches evaluate at most 50 settings at reduced
    resolution, then rerank at most 8 finalists plus the exact original profile.
    The neutral Enhanced Floyd profile is also always a native finalist.
    The current manual settings are ALWAYS a finalist as a safety baseline.
    Both passes use real Floyd/Enhanced Floyd rendering, not a fake halftone.
    """
    if not isinstance(starting_profile, DitherProfile):
        raise TypeError("Expected DitherProfile.")
    if starting_profile.mode != "floyd-steinberg":
        raise ValueError("Auto Tune supports Floyd–Steinberg only.")
    if source.width < 1 or source.height < 1:
        raise ValueError("Auto Tune needs a non-empty image.")
    cancel = should_cancel or (lambda: False)
    if cancel():
        raise AutoTuneCancelled("Auto Tune cancelled before starting.")

    start = replace(starting_profile, enhanced_floyd=True)
    proxy = source.copy()
    proxy.thumbnail(PROXY_MAX_SIZE, Image.Resampling.LANCZOS)
    proxy_ref = _photo_gray(proxy, start.width_dots)
    scores: dict[tuple[float, ...], tuple[float, DitherProfile]] = {}

    def evaluate(profile: DitherProfile) -> float:
        if cancel():
            raise AutoTuneCancelled("Auto Tune was cancelled.")
        key = _signature(profile)
        if key not in scores:
            raster = render_thermal_image(proxy, profile)
            value, _, _, _ = score_print_proxy(raster, proxy_ref, profile)
            scores[key] = (value, profile)
            if on_progress:
                on_progress(len(scores), "Searching")
        return scores[key][0]

    # A neutral restart can escape poor manual settings without discarding them.
    neutral = replace(start, brightness=1.0, contrast=1.0, gamma=1.0, sharpness=1.0)
    for seed in (start, neutral):
        center = seed
        evaluate(center)
        for step_set in SEARCH_STEPS:
            for field, step, bounds in zip(TUNING_FIELDS, step_set, BOUNDS):
                candidates = [
                    _search_neighbor(center, field, -step, bounds),
                    _search_neighbor(center, field, step, bounds),
                ]
                for proposal in candidates:
                    evaluate(proposal)
                # Ties keep the current settings rather than drifting arbitrarily.
                center = max((center, *candidates), key=evaluate)

    if cancel():
        raise AutoTuneCancelled("Auto Tune cancelled before full-resolution ranking.")

    shortlisted = [profile for _, profile in sorted(
        scores.values(), key=lambda item: (-item[0], _signature(item[1]))
    )[:SHORTLIST_SIZE]]
    # Reserve native-resolution slots for both anchors, even when proxy ranks differ.
    anchors = { _signature(p) for p in (start, neutral) }
    shortlisted = [p for p in shortlisted if _signature(p) not in anchors]
    shortlisted = shortlisted[:SHORTLIST_SIZE - len(anchors)]
    shortlisted += [start] if start == neutral else [start, neutral]
    full_ref = _photo_gray(source, start.width_dots)
    final: list[AutoTuneCandidate] = []
    for profile in shortlisted:
        if cancel():
            raise AutoTuneCancelled("Auto Tune cancelled during final validation.")
        raster = render_thermal_image(source, profile)
        score, tone, edges, black = score_print_proxy(raster, full_ref, profile)
        final.append(AutoTuneCandidate(
            profile=profile, raster=raster, score=round(score, 3),
            tone_error=round(tone, 3), edge_error=round(edges, 3),
            black_coverage=round(black, 2),
        ))
        if on_progress:
            on_progress(len(scores) + len(final), "Validating native dots")

    if cancel():
        raise AutoTuneCancelled("Auto Tune cancelled before baseline comparison.")
    baseline = next((c for c in final if c.profile == starting_profile), None)
    baseline_trials = 0
    if baseline is None:
        raster = render_thermal_image(source, starting_profile)
        score, tone, edges, black = score_print_proxy(raster, full_ref, starting_profile)
        baseline = AutoTuneCandidate(starting_profile, raster, round(score, 3),
                                     round(tone, 3), round(edges, 3), round(black, 2))
        baseline_trials = 1
    trials = len(scores) + len(final) + baseline_trials
    if on_progress:
        on_progress(trials, "Compared original settings")
    if cancel():
        raise AutoTuneCancelled("Auto Tune cancelled after baseline comparison.")

    ranked = sorted(final, key=lambda item: (
        -item.score, item.tone_error, _signature(item.profile)
    ))
    return AutoTuneResult(candidates=tuple(ranked[:3]),
                          trials=trials, baseline=baseline)
