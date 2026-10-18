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

from PIL import Image, ImageEnhance

from photobooth.printer import DITHER_MODES, dither_image


PROFILE_VERSION = 1


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

    def __post_init__(self) -> None:
        if self.mode not in DITHER_MODES:
            raise ValueError(f"Unsupported dithering mode: {self.mode!r}")
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
    """Reject malformed/unknown presets instead of silently changing a print."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != PROFILE_VERSION:
        raise ValueError("Invalid or unsupported tuning profile version.")
    keys = set(DitherProfile.__dataclass_fields__)
    if set(payload) != keys | {"schema_version"}:
        raise ValueError("Profile fields do not match the supported schema.")
    return DitherProfile(**{key: payload[key] for key in keys})

# Comparison recipes are deliberately independent: syncing is a GUI action,
# never an implicit overwrite of an algorithm's tuned state.
COMPARISON_VERSION = 1


@dataclass(frozen=True)
class ComparisonProfiles:
    floyd: DitherProfile = DitherProfile(mode="floyd-steinberg")
    bayer: DitherProfile = DitherProfile(mode="bayer")
    threshold: DitherProfile = DitherProfile(mode="threshold")

    def __post_init__(self):
        if (self.floyd.mode, self.bayer.mode, self.threshold.mode) != (
            "floyd-steinberg", "bayer", "threshold"
        ):
            raise ValueError("Each comparison lane must keep its own algorithm.")

    def by_mode(self, mode: str) -> DitherProfile:
        return {
            "floyd-steinberg": self.floyd,
            "bayer": self.bayer,
            "threshold": self.threshold,
        }[mode]

    def replace_lane(self, profile: DitherProfile) -> "ComparisonProfiles":
        from dataclasses import replace
        key = {"floyd-steinberg": "floyd", "bayer": "bayer",
               "threshold": "threshold"}[profile.mode]
        return replace(self, **{key: profile})


def save_comparison(path: str | Path, profiles: ComparisonProfiles) -> None:
    """Atomic versioned JSON; does not modify production printer settings."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"schema_version": COMPARISON_VERSION,
            "lanes": {mode: asdict(profiles.by_mode(mode)) for mode in DITHER_MODES}}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2, allow_nan=False)
            stream.write("\\n")
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def load_comparison(path: str | Path) -> ComparisonProfiles:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or
            set(data) != {"schema_version", "lanes"} or
            data["schema_version"] != COMPARISON_VERSION or
            not isinstance(data["lanes"], dict) or
            set(data["lanes"]) != set(DITHER_MODES)):
        raise ValueError("Invalid comparison config schema.")
    lanes = {}
    keys = set(DitherProfile.__dataclass_fields__)
    for mode in DITHER_MODES:
        raw = data["lanes"][mode]
        if not isinstance(raw, dict) or set(raw) != keys or raw["mode"] != mode:
            raise ValueError(f"Invalid {mode} profile.")
        lanes[mode] = DitherProfile(**raw)
    return ComparisonProfiles(lanes["floyd-steinberg"], lanes["bayer"], lanes["threshold"])
