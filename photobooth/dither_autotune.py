"""Offline, deterministic auto-tuning for each Meong lab dithering algorithm.

This is a **heuristic** visual-fidelity search, not a physical thermal-printer
calibration or an AI face-quality classifier. No data leaves this process, no
printer is accessed, and the caller must explicitly apply a candidate.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable
import random

from PIL import Image, ImageChops, ImageFilter, ImageStat

from photobooth.dither_lab import DitherProfile, LAB_DITHER_MODES, render_thermal_image
from photobooth.dizzy_dither import DIZZY_VARIANTS

# Keep the candidate budget bounded so the desktop GUI remains responsive.
SEARCH_STEPS = (
    (0.17, 0.30, 0.32, 0.55),
    (0.085, 0.16, 0.16, 0.28),
    (0.042, 0.08, 0.08, 0.14),
)
TUNING_FIELDS = ("brightness", "contrast", "gamma", "sharpness")
BOUNDS = ((0.5, 1.75), (0.5, 2.5), (0.3, 3.0), (0.0, 3.0))
SHORTLIST_SIZE = 8
PROXY_MAX_SIZE = (256, 320)
# Dizzy is a CPU-heavy per-pixel algorithm: use a smaller bounded search.
DIZZY_PROXY_MAX_SIZE = (160, 200)
THRESHOLD_BOUNDS = (64, 200)
THRESHOLD_STEPS = (28, 14, 7)
# Deliberately short, bounded combinations; these are photo-heuristic trials,
# not trained printer calibration or a promise that paper quality improves.
PROCESSING_PRESETS = (
    {"smart_enhance": True, "clahe_strength": 0.20,
     "denoise_level": 1, "tone_strength": 0.12},
    {"smart_enhance": True, "clahe_strength": 0.48,
     "denoise_level": 1, "tone_strength": 0.25},
    {"postprocess_enabled": True, "dot_cleanup_level": 2,
     "edge_refine_level": 1},
    {"smart_enhance": True, "clahe_strength": 0.34,
     "denoise_level": 1, "tone_strength": 0.18,
     "postprocess_enabled": True, "dot_cleanup_level": 1,
     "edge_refine_level": 1},
)
PROCESSING_FIELDS = (
    "smart_enhance", "clahe_strength", "denoise_level", "tone_strength",
    "postprocess_enabled", "dot_cleanup_level", "edge_refine_level",
)


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
    baseline: AutoTuneCandidate  # System-neutral algorithm-specific reference.
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
    if profile.mode == "threshold":
        penalty += abs(profile.threshold - 128) / 127
    if profile.smart_enhance:
        penalty += 0.18 + 0.3 * profile.clahe_strength + 0.1 * profile.denoise_level
    if profile.postprocess_enabled:
        penalty += 0.15 + 0.08 * (
            profile.dot_cleanup_level + profile.edge_refine_level)
    score = max(0.0, min(
        100.0,
        100.0 - (0.72 * tone_error + 0.16 * edge_error +
                 0.11 * coverage_deviation + 0.65 * penalty),
    ))
    return score, tone_error, edge_error, black_coverage


def _signature(profile: DitherProfile) -> tuple:
    """Key includes algorithm-specific controls to keep distinct presets."""
    key = tuple(getattr(profile, field) for field in
                (*TUNING_FIELDS, *PROCESSING_FIELDS))
    if profile.mode == "threshold":
        return (*key, profile.threshold)
    if profile.mode == "dizzy":
        return (*key, profile.enhanced_dizzy, profile.dizzy_variant,
                profile.dizzy_seed, profile.dizzy_contrast_correction)
    return key


def _search_neighbor(profile: DitherProfile, field: str,
                     amount: float, bounds: tuple[float, float]) -> DitherProfile:
    value = max(bounds[0], min(bounds[1], getattr(profile, field) + amount))
    return replace(profile, **{field: int(round(value)) if field == "threshold"
                               else round(value, 3)})


def tune_dither(
    source: Image.Image,
    starting_profile: DitherProfile,
    *,
    should_cancel: Callable[[], bool] | None = None,
    on_progress: Callable[[int, str], None] | None = None,
) -> AutoTuneResult:
    """Search the selected algorithm from system-neutral parameters.

    Only the selected mode and print width are inherited from the live GUI,
    never the current manual sliders, enhancement flags, Dizzy seed/variant,
    or threshold. Searches and outputs are separate for each algorithm.
    Floyd keeps the existing Enhanced Floyd search for compatibility; Bayer
    uses its fixed 8x8 matrix; Dizzy tries both article variants and both
    preprocessing states; Threshold can be tuned via the backend even though
    its comparison-GUI lane is intentionally hidden.
    """
    if not isinstance(starting_profile, DitherProfile):
        raise TypeError("Expected DitherProfile.")
    if starting_profile.mode not in LAB_DITHER_MODES:
        raise ValueError("Unsupported algorithm for Auto Tune.")
    if source.width < 1 or source.height < 1:
        raise ValueError("Auto Tune needs a non-empty image.")
    cancel = should_cancel or (lambda: False)
    if cancel():
        raise AutoTuneCancelled("Auto Tune cancelled before starting.")

    mode = starting_profile.mode
    neutral = DitherProfile(
        mode=mode, width_dots=starting_profile.width_dots,
        enhanced_floyd=(mode == "floyd-steinberg"),
    )
    anchors = [neutral]
    if mode == "dizzy":
        # Assess the variants independently, rather than copying the
        # operator's manual selection into an automatic recommendation.
        anchors = [
            replace(neutral, dizzy_variant=variant, enhanced_dizzy=enhanced,
                    dizzy_contrast_correction=corrected)
            for variant in DIZZY_VARIANTS for enhanced in (False, True)
            for corrected in (False, True)
        ]
    fields = TUNING_FIELDS + (("threshold",) if mode == "threshold" else ())
    bounds = BOUNDS + ((THRESHOLD_BOUNDS,) if mode == "threshold" else ())
    proxy = source.copy()
    proxy.thumbnail(
        DIZZY_PROXY_MAX_SIZE if mode == "dizzy" else PROXY_MAX_SIZE,
        Image.Resampling.LANCZOS,
    )
    proxy_ref = _photo_gray(proxy, neutral.width_dots)
    scores: dict[tuple, tuple[float, DitherProfile]] = {}

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

    # Evaluate opt-in enhancement alternatives explicitly, even when the
    # manual GUI happens to have all processing options disabled.
    for options in PROCESSING_PRESETS:
        anchors.append(replace(neutral, **options))
    for anchor in anchors:
        evaluate(anchor)
    rng = random.Random(42)
    for _ in range(8 if mode == "dizzy" else 16):
        base = anchors[rng.randrange(len(anchors))]
        values = {
            field: (rng.randint(int(low), int(high))
                    if field == "threshold" else round(rng.uniform(low, high), 3))
            for field, (low, high) in zip(fields, bounds)
        }
        evaluate(replace(base, **values))

    best_probe = max(scores.values(), key=lambda item: item[0])[1]
    seeds = (best_probe,) if mode == "dizzy" else (neutral, best_probe)
    steps = SEARCH_STEPS[:2] if mode == "dizzy" else SEARCH_STEPS
    for seed in seeds:
        center = seed
        for stage, step_set in enumerate(steps):
            for field, bounds_pair, step in zip(
                fields, bounds,
                (*step_set, THRESHOLD_STEPS[stage]) if mode == "threshold"
                else step_set,
            ):
                neighbors = (
                    _search_neighbor(center, field, -step, bounds_pair),
                    _search_neighbor(center, field, step, bounds_pair),
                )
                for proposal in neighbors:
                    evaluate(proposal)
                center = max((center, *neighbors), key=evaluate)

    # Fine-tune the strongest enhanced proposal, independently of tonal
    # coordinates. Limit evaluations and keep integer post levels discrete.
    enhanced_profiles = [profile for _, profile in scores.values()
                         if profile.smart_enhance]
    if enhanced_profiles:
        best_enhanced = max(enhanced_profiles, key=evaluate)
        for field, step in (("clahe_strength", 0.12), ("tone_strength", 0.1)):
            for direction in (-1, 1):
                evaluate(_search_neighbor(best_enhanced, field, step * direction,
                                          (0.0, 1.0)))
        for level in (0, 2):
            evaluate(replace(best_enhanced, denoise_level=level))
    post_profiles = [profile for _, profile in scores.values()
                     if profile.postprocess_enabled]
    if post_profiles:
        best_post = max(post_profiles, key=evaluate)
        for field in ("dot_cleanup_level", "edge_refine_level"):
            for direction in (-1, 1):
                evaluate(_search_neighbor(best_post, field, direction, (0, 3)))

    if cancel():
        raise AutoTuneCancelled("Auto Tune cancelled before full-resolution ranking.")

    shortlist_size = 5 if mode == "dizzy" else SHORTLIST_SIZE
    shortlisted = [profile for _, profile in sorted(
        scores.values(), key=lambda item: (-item[0], _signature(item[1]))
    )[:shortlist_size]]
    # Always evaluate the neutral algorithm baseline at true native resolution,
    # even if its reduced-proxy score was not in the best shortlist.
    # Reserve native verification for a smart candidate and a post candidate,
    # even when digital proxy scores favor only unprocessed images.
    finalists = [p for _, p in sorted(
        scores.values(), key=lambda item: (-item[0], _signature(item[1]))
    )]
    reserved = [neutral]
    for predicate in (lambda p: p.smart_enhance,
                      lambda p: p.postprocess_enabled):
        eligible = next((p for p in finalists if predicate(p)), None)
        if eligible is not None and eligible not in reserved:
            reserved.append(eligible)
    for item in reserved:
        if item not in shortlisted:
            # Replace the lowest-ranked unreserved result, preserving space.
            for idx in range(len(shortlisted) - 1, -1, -1):
                if shortlisted[idx] not in reserved:
                    shortlisted[idx] = item
                    break
    full_ref = _photo_gray(source, neutral.width_dots)
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
        raise AutoTuneCancelled("Auto Tune cancelled after native validation.")
    baseline = next(c for c in final if c.profile == neutral)
    ranked = sorted(final, key=lambda item: (
        -item.score, item.tone_error, _signature(item.profile)
    ))
    # Offer a meaningful human-review comparison: best digital score plus
    # an opt-in Smart option and (when distinct) a post-processing option.
    selected = [ranked[0]]
    for predicate in (lambda p: p.smart_enhance,
                      lambda p: p.postprocess_enabled):
        option = next((c for c in ranked if predicate(c.profile)
                       and c not in selected), None)
        if option is not None and len(selected) < 3:
            selected.append(option)
    for candidate in ranked:
        if len(selected) == 3:
            break
        if candidate not in selected:
            selected.append(candidate)
    selected.sort(key=lambda c: (-c.score, c.tone_error, _signature(c.profile)))
    return AutoTuneResult(
        candidates=tuple(selected), trials=len(scores) + len(final),
        baseline=baseline,
    )


def tune_enhanced_floyd(
    source: Image.Image,
    starting_profile: DitherProfile,
    *,
    should_cancel: Callable[[], bool] | None = None,
    on_progress: Callable[[int, str], None] | None = None,
) -> AutoTuneResult:
    """Backward-compatible Enhanced Floyd-only entry point."""
    if not isinstance(starting_profile, DitherProfile):
        raise TypeError("Expected DitherProfile.")
    if starting_profile.mode != "floyd-steinberg":
        raise ValueError("Auto Tune supports Floyd–Steinberg only.")
    return tune_dither(
        source, starting_profile, should_cancel=should_cancel,
        on_progress=on_progress,
    )
