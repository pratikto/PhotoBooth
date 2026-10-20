"""Offline thermal-photo tuning lab built on the booth's existing dithering.

This module intentionally does NOT alter ThermalPrinter or any live customer
workflow. A saved JSON lab profile is experimental and is never auto-applied
to production print jobs. Defaults reproduce the current production raster.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import tempfile

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from photobooth.printer import DITHER_MODES, dither_image
from photobooth.dizzy_dither import (DEFAULT_DIZZY_SEED, DIZZY_VARIANTS,
                                     dizzy_dither)

# Four offline comparison lanes; do not expand production PrinterConfig modes.
LAB_DITHER_MODES = DITHER_MODES + ("dizzy",)


PROFILE_VERSION = 3


@dataclass(frozen=True)
class DitherProfile:
    """A bounded, serializable recipe for a one-bit 80/58 mm thermal raster."""

    mode: str = "floyd-steinberg"
    width_dots: int = 576
    brightness: float = 1.0
    contrast: float = 1.0
    gamma: float = 1.0
    sharpness: float = 1.0
    threshold: int = 128
    enhanced_floyd: bool = False
    dizzy_variant: str = "article-8"
    dizzy_seed: int = DEFAULT_DIZZY_SEED

    def __post_init__(self) -> None:
        if type(self.enhanced_floyd) is not bool or (self.enhanced_floyd and self.mode != 'floyd-steinberg'):
            raise ValueError('Enhanced preprocessing is available only for Floyd.')
        if self.mode not in LAB_DITHER_MODES:
            raise ValueError(f"Unsupported dithering mode: {self.mode!r}")
        if self.dizzy_variant not in DIZZY_VARIANTS:
            raise ValueError("Unknown Dizzy variant.")
        if type(self.dizzy_seed) is not int or not 0 <= self.dizzy_seed <= 0xFFFFFFFF:
            raise ValueError("Dizzy seed must be an integer in 0..2^32-1.")
        if self.mode != "dizzy" and (
            self.dizzy_variant != "article-8" or self.dizzy_seed != DEFAULT_DIZZY_SEED
        ):
            raise ValueError("Dizzy parameters are only valid for Dizzy mode.")
        if type(self.width_dots) is not int or self.width_dots not in (384, 576):
            raise ValueError("Print width must be 384 or 576 dots.")
        for key, minimum, maximum in (
            ("brightness", 0.5, 1.75),
            ("contrast", 0.5, 2.5),
            ("gamma", 0.3, 3.0),
            ("sharpness", 0.0, 3.0),
        ):
            value = getattr(self, key)
            if type(value) not in (float, int) or not math.isfinite(value):
                raise ValueError(f"{key} must be a finite number.")
            if not minimum <= value <= maximum:
                raise ValueError(f"{key} must be between {minimum} and {maximum}.")
        if type(self.threshold) is not int or not 0 <= self.threshold <= 255:
            raise ValueError("Threshold must be an integer between 0 and 255.")


def render_thermal_image(source: Image.Image, profile: DitherProfile) -> Image.Image:
    """Return the actual full-resolution one-bit raster, without UI scaling.

    Composite alpha on white, preserve the booth's native-width Lanczos
    downsampling, then perform tunable grayscale corrections BEFORE dithering.
    No second resize or secondary halftone is applied to this output.
    """
    rgba = source.convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    gray = Image.alpha_composite(white, rgba).convert("L")

    if gray.width > profile.width_dots:
        height = max(1, round(gray.height * profile.width_dots / gray.width))
        gray = gray.resize((profile.width_dots, height), Image.Resampling.LANCZOS)

    if profile.brightness != 1.0:
        gray = ImageEnhance.Brightness(gray).enhance(profile.brightness)
    if profile.contrast != 1.0:
        gray = ImageEnhance.Contrast(gray).enhance(profile.contrast)
    if profile.gamma != 1.0:
        # gamma > 1 brightens midtones; gamma < 1 darkens them. A grayscale
        # lookup table keeps the mapping bounded and independent of image size.
        lut = [round(255 * ((value / 255) ** (1 / profile.gamma)))
               for value in range(256)]
        gray = gray.point(lut)
    if profile.sharpness != 1.0:
        gray = ImageEnhance.Sharpness(gray).enhance(profile.sharpness)

    if profile.enhanced_floyd:
        # Lab-only conservative denoise, gentle tonal normalization and
        # restrained edge sharpening before 1-bit error diffusion.
        denoised = gray.filter(ImageFilter.MedianFilter(size=3))
        leveled = ImageOps.autocontrast(denoised, cutoff=1, preserve_tone=True)
        gray = Image.blend(denoised, leveled, 0.20)
        gray = gray.filter(ImageFilter.UnsharpMask(radius=1.1, percent=55, threshold=3))

    if profile.mode == "dizzy":
        return dizzy_dither(gray, variant=profile.dizzy_variant,
                            seed=profile.dizzy_seed)
    return dither_image(gray, profile.mode, profile.threshold)


def save_profile(path: str | Path, profile: DitherProfile) -> None:
    """Write a portable recipe atomically, never touching the kiosk settings."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"schema_version": PROFILE_VERSION, **asdict(profile)}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as output:
            temporary = Path(output.name)
            json.dump(data, output, indent=2, allow_nan=False)
            output.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_profile(path: str | Path) -> DitherProfile:
    """Load a lab-only profile, keeping v1/v2 Dizzy-disabled by default."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") not in (1, 2, 3):
        raise ValueError("Invalid or unsupported tuning profile version.")
    version = payload["schema_version"]
    keys = set(DitherProfile.__dataclass_fields__)
    missing = {1: {"enhanced_floyd", "dizzy_variant", "dizzy_seed"},
               2: {"dizzy_variant", "dizzy_seed"}, 3: set()}[version]
    if set(payload) != (keys - missing) | {"schema_version"}:
        raise ValueError("Profile fields do not match the supported schema.")
    values = {key: payload[key] for key in keys - missing}
    for key in missing:
        values[key] = getattr(DitherProfile(), key)
    return DitherProfile(**values)


# Comparison recipes are deliberately independent: syncing is a GUI action,
# never an implicit overwrite of an algorithm's tuned state.
COMPARISON_VERSION = 3


@dataclass(frozen=True)
class ComparisonProfiles:
    floyd: DitherProfile = DitherProfile(mode="floyd-steinberg")
    bayer: DitherProfile = DitherProfile(mode="bayer")
    threshold: DitherProfile = DitherProfile(mode="threshold")
    dizzy: DitherProfile = DitherProfile(mode="dizzy")

    def __post_init__(self):
        if (self.floyd.mode, self.bayer.mode, self.threshold.mode,
                self.dizzy.mode) != LAB_DITHER_MODES:
            raise ValueError("Each comparison lane must keep its own algorithm.")

    def by_mode(self, mode: str) -> DitherProfile:
        return {
            "floyd-steinberg": self.floyd,
            "bayer": self.bayer,
            "threshold": self.threshold,
            "dizzy": self.dizzy,
        }[mode]

    def replace_lane(self, profile: DitherProfile) -> "ComparisonProfiles":
        from dataclasses import replace
        key = {"floyd-steinberg": "floyd", "bayer": "bayer",
               "threshold": "threshold", "dizzy": "dizzy"}[profile.mode]
        return replace(self, **{key: profile})


def save_comparison(path: str | Path, profiles: ComparisonProfiles) -> None:
    """Atomic versioned JSON; does not modify production printer settings."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"schema_version": COMPARISON_VERSION,
            "lanes": {mode: asdict(profiles.by_mode(mode)) for mode in LAB_DITHER_MODES}}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def load_comparison(path: str | Path) -> ComparisonProfiles:
    """Read v1/v2 three-lane presets or v3 four-lane presets, fail closed."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or
            set(data) != {"schema_version", "lanes"} or
            data["schema_version"] not in (1, 2, 3) or
            not isinstance(data["lanes"], dict)):
        raise ValueError("Invalid comparison config schema.")
    version = data["schema_version"]
    modes = DITHER_MODES if version in (1, 2) else LAB_DITHER_MODES
    if set(data["lanes"]) != set(modes):
        raise ValueError("Invalid comparison lanes.")
    keys = set(DitherProfile.__dataclass_fields__)
    missing = {1: {"enhanced_floyd", "dizzy_variant", "dizzy_seed"},
               2: {"dizzy_variant", "dizzy_seed"}, 3: set()}[version]
    defaults = DitherProfile()
    lanes = {}
    for mode in modes:
        raw = data["lanes"][mode]
        if not isinstance(raw, dict) or set(raw) != keys - missing or raw["mode"] != mode:
            raise ValueError(f"Invalid {mode} profile.")
        values = dict(raw)
        for key in missing:
            values[key] = getattr(defaults, key)
        lanes[mode] = DitherProfile(**values)
    return ComparisonProfiles(
        lanes["floyd-steinberg"], lanes["bayer"], lanes["threshold"],
        lanes.get("dizzy", DitherProfile(mode="dizzy")))
