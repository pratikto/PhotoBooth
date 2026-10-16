#!/usr/bin/env python3
"""Print one saved booth image with all supported dithering methods."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from photobooth.printer import DITHER_MODES, ThermalPrinter


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
    args = parser.parse_args(argv)
    if not args.image.is_file():
        parser.error(f"image file not found: {args.image}")

    results = ThermalPrinter().print_comparison(args.image)
    for mode, result in zip(DITHER_MODES, results):
        print(f"{mode}: {result.transport}: {result.user_message}")
        if not result.success:
            return 1

    return 0 if len(results) == len(DITHER_MODES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
