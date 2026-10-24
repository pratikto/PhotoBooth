#!/usr/bin/env python3
"""Offline reference experiment for Meong's CPU Dizzy variants.

Author's Python Gist: https://gist.github.com/liamappelbe/c2c76ad1ba655aa1caae5da40bcadc7e
Original article: https://liamappelbe.medium.com/dizzy-dithering-2ae76dbceba1

This is an independently written adaptation of the algorithm, not a verbatim
copy or pixel-equivalence certification. The author's gist uses shuffled
column-major order, rounded/clamped 8-bit updates and FOUR orthogonal neighbors.
Meong instead uses a stateless five-round permutation and float32 accumulation.
The eight-neighbor test is an independent article-pseudocode implementation,
NOT published author Python code. Neither is GPU Layered Dizzy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import sys

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from photobooth.dizzy_dither import dizzy_dither, _permuted_pixel_indices


def _validate(gray: Image.Image, seed: int):
    if type(seed) is not int or not 0 <= seed <= 0xFFFFFFFF:
        raise ValueError("Seed must be an integer in 0..2^32-1.")
    width, height = gray.size
    if width < 1 or height < 1:
        raise ValueError("Source image must be non-empty.")
    return width, height


def gist_style_orthogonal(gray: Image.Image, *, seed=42, same_order=False):
    """Author-Gist-style 8-bit update, with a reproducible local shuffle.

    With same_order=True use Meong's index permutation, isolating the numeric
    precision/clamping difference from visitation-order differences.
    """
    width, height = _validate(gray, seed)
    values = bytearray(gray.convert("L").tobytes())
    visited = bytearray(width * height)
    if same_order:
        order = list(_permuted_pixel_indices(width * height, seed))
    else:
        # The author's Python Gist constructs coordinates column-major.
        order = [x + y * width for x in range(width) for y in range(height)]
        random.Random(seed).shuffle(order)
    for p in order:
        x, y = p % width, p // width
        old = values[p]
        new = 0 if old < 128 else 255
        values[p] = new
        error = old - new
        neighbors = []
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            xx, yy = x + dx, y + dy
            if 0 <= xx < width and 0 <= yy < height:
                other = xx + yy * width
                if not visited[other]:
                    neighbors.append(other)
        if neighbors:
            share = error / len(neighbors)
            for other in neighbors:
                values[other] = max(0, min(255, round(values[other] + share)))
        visited[p] = 1
    return Image.frombytes("L", (width, height), bytes(values)).convert(
        "1", dither=Image.Dither.NONE)


def independent_article8(gray: Image.Image, *, seed=42):
    """Independent double-precision interpretation of the 2024 article.

    Unlike Meong, uses a seeded full shuffled list instead of the 5-round
    memory-saving permutation. No author's 8-neighbor Python Gist exists.
    """
    width, height = _validate(gray, seed)
    values = [v / 255.0 for v in gray.convert("L").tobytes()]
    visited = bytearray(width * height)
    result = bytearray(width * height)
    order = list(range(width * height))
    random.Random(seed).shuffle(order)
    offsets = (
        (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
        (-1, -1, 0.1), (1, -1, 0.1), (-1, 1, 0.1), (1, 1, 0.1),
    )
    for p in order:
        x, y = p % width, p // width
        old = values[p]
        new = 1.0 if old >= 0.5 else 0.0
        result[p] = 255 if new else 0
        visited[p] = 1
        error = old - new
        if error == 0:
            continue
        neighbors = []
        for dx, dy, weight in offsets:
            xx, yy = x + dx, y + dy
            if 0 <= xx < width and 0 <= yy < height:
                other = xx + yy * width
                if not visited[other]:
                    neighbors.append((other, weight))
        denominator = sum(weight for _, weight in neighbors)
        if denominator:
            for other, weight in neighbors:
                values[other] += error * weight / denominator
    return Image.frombytes("L", (width, height), bytes(result)).convert(
        "1", dither=Image.Dither.NONE)


def _white_pct(raster: Image.Image):
    return raster.convert("L").histogram()[255] * 100 / (
        raster.width * raster.height)


def _stats(meong: Image.Image, reference: Image.Image):
    if meong.mode != "1" or reference.mode != "1" or meong.size != reference.size:
        raise ValueError("Compare identical native-sized 1-bit rasters only.")
    diff = ImageChops.difference(meong.convert("L"), reference.convert("L"))
    pixels = meong.width * meong.height
    mismatched = diff.histogram()[255]
    return {
        "different_pixels": mismatched,
        "different_pixels_pct": 100 * mismatched / pixels,
        "meong_white_pct": _white_pct(meong),
        "reference_white_pct": _white_pct(reference),
        "white_coverage_delta_pp": _white_pct(meong) - _white_pct(reference),
    }, diff


def sample_source(width=144, height=168):
    if not 16 <= width <= 384 or not 16 <= height <= 384:
        raise ValueError("Synthetic sample dimensions must be 16..384.")
    image = Image.new("L", (width, height))
    image.putdata([round(x * 255 / (width - 1))
                   for y in range(height) for x in range(width)])
    draw = ImageDraw.Draw(image)
    draw.ellipse((width//5, height//5, 4*width//5, 3*height//5),
                 fill=144, outline=30, width=2)
    draw.line((0, height//2, width-1, height//2), fill=12, width=2)
    return image


def compare_references(source: Image.Image, *, seed=42):
    """Return JSON-safe comparison metrics and images (not a printer job)."""
    gray = source.convert("L")
    _validate(gray, seed)
    results = {}
    images = {"original_gray": gray}
    for variant in ("orthogonal-4", "article-8"):
        actual = dizzy_dither(gray, variant=variant, seed=seed,
                              contrast_correction=False)
        reference = (gist_style_orthogonal(gray, seed=seed)
                     if variant == "orthogonal-4"
                     else independent_article8(gray, seed=seed))
        stats, diff = _stats(actual, reference)
        images[f"{variant}_meong"] = actual
        images[f"{variant}_reference"] = reference
        images[f"{variant}_difference"] = diff
        if variant == "orthogonal-4":
            equal_order = gist_style_orthogonal(
                gray, seed=seed, same_order=True)
            held, held_diff = _stats(actual, equal_order)
            images[f"{variant}_gist_equal_order"] = equal_order
            images[f"{variant}_gist_equal_order_difference"] = held_diff
            stats["equal_order_numeric_comparison"] = held
            stats["reference_kind"] = "author gist math with seeded shuffle"
        else:
            stats["reference_kind"] = "independent 2024 article 8-neighbor pseudocode"
        results[variant] = stats
    return {
        "metadata": {"source_width": gray.width, "source_height": gray.height,
                     "seed": seed, "tone_lut_enabled": False,
                     "paper_calibrated": False, "pixel_identical_expected": False,
                     "author_gist": "https://gist.github.com/liamappelbe/c2c76ad1ba655aa1caae5da40bcadc7e",
                     "notes": ("Differences include traversal, clamping and precision; "
                               "Layered GPU mode is not compared.")},
        "results": results,
    }, images


def write_comparison(report, images, output_dir: Path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = []
    for name, image in images.items():
        path = output_dir / f"{name}.png"
        image.save(path, format="PNG")
        generated.append(path)
    path = output_dir / "dizzy_reference_comparison.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    generated.append(path)
    return generated


def main(argv=None):
    parser = argparse.ArgumentParser(description="Dizzy offline author reference A/B")
    parser.add_argument("--image", type=Path, help="Optional grayscale/photo input")
    parser.add_argument("--width", type=int, default=144)
    parser.add_argument("--height", type=int, default=168)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path,
                        default=Path("data/dizzy_reference"))
    args = parser.parse_args(argv)
    if not 16 <= args.width <= 384 or not 16 <= args.height <= 384:
        parser.error("--width and --height must be 16..384.")
    if args.image is None:
        gray = sample_source(args.width, args.height)
    else:
        with Image.open(args.image) as source:
            gray = source.convert("L")
        gray.thumbnail((args.width, args.height), Image.Resampling.LANCZOS)
    report, images = compare_references(gray, seed=args.seed)
    generated = write_comparison(report, images, args.output_dir)
    for variant, metrics in report["results"].items():
        print(f"{variant}: {metrics['different_pixels_pct']:.2f}% pixel difference; "
              f"white-dot coverage delta {metrics['white_coverage_delta_pp']:+.2f}pp")
        if variant == "orthogonal-4":
            x = metrics["equal_order_numeric_comparison"]
            print(f"  holding visit order: {x['different_pixels_pct']:.2f}% pixel difference")
    for path in generated:
        print("saved", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
