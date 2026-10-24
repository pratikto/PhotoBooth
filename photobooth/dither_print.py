"""Physical comparison test jobs using exactly the validated preview raster.

The printer's transport logic is reused; a one-bit raster is never passed
through the thermal dithering algorithm a second time. Only an explicit GUI
confirmation triggers these functions. No automatic retry follows uncertainty.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from photobooth.dither_lab import DitherProfile
from photobooth.printer import (PrinterConfig, PrintResult, ThermalPrinter,
                               _add_binary_header)


def printable_destination(config: PrinterConfig) -> bool:
    """A chosen route is needed; the app must not silently print elsewhere."""
    return bool(config.windows_printer_name or config.lan_host or
                config.wifi_host or
                (config.usb_vendor_id is not None and
                 config.usb_product_id is not None) or
                (config.usb_device_path and
                 Path(config.usb_device_path).exists()))


def annotated_raster(raster: Image.Image, profile: DitherProfile) -> Image.Image:
    """Prepend metadata outside the original dot raster for paper comparison."""
    if raster.mode != "1":
        raise ValueError("Print requires a native 1-bit preview raster.")
    if raster.width > profile.width_dots:
        raise ValueError("Preview exceeds the selected printhead width.")
    parts = [
        "MEONG DITHER LAB / TEST ONLY",
        f"MODE: {profile.mode} | WIDTH: {profile.width_dots}",
        f"B {profile.brightness:.2f} C {profile.contrast:.2f} "
        f"G {profile.gamma:.2f} S {profile.sharpness:.2f}",
        f"THRESHOLD: {profile.threshold}",
    ]
    if profile.mode == "dizzy":
        parts.append(
            f"DIZZY: {profile.dizzy_variant} | SEED: {profile.dizzy_seed}")
        parts.append(
            "PREPROCESS: ENHANCED" if profile.enhanced_dizzy
            else "PREPROCESS: BASELINE"
        )
        parts.append("CPU TONE LUT: ON" if profile.dizzy_contrast_correction
                     else "CPU TONE LUT: OFF")
    if profile.smart_enhance:
        parts.append(
            f"SMART: CLAHE {profile.clahe_strength:.2f} "
            f"MED {profile.denoise_level} TONE {profile.tone_strength:.2f}")
    if profile.postprocess_enabled:
        parts.append(
            f"POST: DOTS {profile.dot_cleanup_level} "
            f"EDGES {profile.edge_refine_level}")
    output = raster.copy()
    # Header is a separate 1-bit strip; original preview bytes stay untouched.
    for line in reversed(parts):
        output = _add_binary_header(output, line)
    return output


def build_native_payload(raster: Image.Image, profile: DitherProfile) -> bytes:
    """ESC/POS bitImageRaster of the SAME 1-bit pixels shown on screen."""
    from escpos.printer import Dummy
    image = annotated_raster(raster, profile)
    spool = Dummy()
    spool.image(image, impl="bitImageRaster", fragment_height=960)
    spool.cut()
    return spool.output


def print_native_raster(raster: Image.Image, profile: DitherProfile,
                        config: PrinterConfig) -> PrintResult:
    """Submit a single test through the existing reliable route selection.

    A temporary PNG satisfies ThermalPrinter's validated path contract.
    Injecting already-rendered bytes avoids the normal grayscale/dither pass.
    LAN/Wi-Fi failure fallback is exactly ThermalPrinter's existing behavior;
    printer-send uncertainty is never retried automatically.
    """
    if not printable_destination(config):
        return PrintResult(False, "none", "Printer destination not configured.")
    payload = build_native_payload(raster, profile)
    with TemporaryDirectory(prefix="meong-dither-test-") as folder:
        temp = Path(folder) / "already-dithered.png"
        raster.save(temp)
        printer = ThermalPrinter(config, payload_builder=lambda _path: payload)
        return printer.print_image(temp)
