#!/usr/bin/env python3
"""Print one saved booth image with all supported dithering methods."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from photobooth.printer import DITHER_MODES, ThermalPrinter, PrinterConfig, dither_image


def main(argv: list[str] | None = None) -> int:
    """Send three labeled comparison prints and report each result."""
    parser = argparse.ArgumentParser(
        description=(
            "Print one saved photobooth image with Floyd–Steinberg, Bayer, "
            "and threshold dithering. This sends up to three real print jobs."
        )
    )
    parser.add_argument(
        "image",
        type=Path,
        help="path to a saved result PNG, used as the source for all three prints",
    )
    parser.add_argument("--mode", choices=DITHER_MODES,
                        help="Print only one selected dither mode.")
    parser.add_argument("--preview-dir", type=Path,
                        help="Export monochrome previews without printing.")
    args = parser.parse_args(argv)
    if not args.image.is_file():
        parser.error(f"image file not found: {args.image}")

    if args.preview_dir is not None:
        from PIL import Image
        config = PrinterConfig.from_environment()
        args.preview_dir.mkdir(parents=True, exist_ok=True)
        with Image.open(args.image) as source:
            rgba = source.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            gray = Image.alpha_composite(background, rgba).convert("L")
        if gray.width > config.print_width_dots:
            resampling = getattr(Image, "Resampling", Image)
            gray = gray.resize(
                (config.print_width_dots,
                 max(1, round(gray.height * config.print_width_dots / gray.width))),
                resampling.LANCZOS,
            )
        for mode in DITHER_MODES:
            output = args.preview_dir / f"{args.image.stem}-{mode}.png"
            dither_image(gray, mode, config.dither_threshold).save(output)
            print(f"{mode}: saved {output} (no paper printed)")
        return 0

    printer = ThermalPrinter()
    if args.mode is not None:
        result = printer.print_image(
            args.image, dither_mode=args.mode,
            header_label=f"DITHER TEST: {args.mode.upper()}"
        )
        print(f"{args.mode}: {result.transport}: {result.user_message}")
        return 0 if result.success else 1

    results = printer.print_comparison(args.image)
    for mode, result in zip(DITHER_MODES, results):
        print(f"{mode}: {result.transport}: {result.user_message}")
        if not result.success:
            return 1

    return 0 if len(results) == len(DITHER_MODES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
