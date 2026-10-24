#!/usr/bin/env python3
"""Offline 0..255 white-dot fidelity audit for Meong CPU Dizzy tone LUT.

Only synthetic uniform grayscale patches are generated. No camera, network,
printer or customer files. Outputs JSON + CSV + standalone SVG without adding
matplotlib, OpenCV or other runtime dependencies.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from photobooth.dizzy_calibration import CALIBRATION_ID
from photobooth.dizzy_dither import DIZZY_VARIANTS, dizzy_dither


def measure_fidelity(*, width=96, height=96, seed=42,
                     tones=range(256), variants=DIZZY_VARIANTS):
    """Return measured fraction of WHITE dots for all requested input tones."""
    if not (16 <= width <= 256 and 16 <= height <= 256):
        raise ValueError("Audit width/height must be between 16 and 256.")
    if type(seed) is not int or not 0 <= seed <= 0xFFFFFFFF:
        raise ValueError("Seed must be an integer from 0 to 2^32-1.")
    requested = tuple(tones)
    if not requested or any(type(t) is not int or not 0 <= t <= 255 for t in requested):
        raise ValueError("Tones must be grayscale integers from 0 to 255.")
    if len(set(requested)) != len(requested):
        raise ValueError("Tones must not repeat.")
    if not variants or any(v not in DIZZY_VARIANTS for v in variants):
        raise ValueError("Unsupported Dizzy CPU variant.")

    rows = []
    summary = {}
    for variant in variants:
        entries = []
        for tone in sorted(requested):
            original = Image.new("L", (width, height), tone)
            raw = dizzy_dither(original, variant=variant, seed=seed,
                               contrast_correction=False)
            corrected = dizzy_dither(original, variant=variant, seed=seed,
                                     contrast_correction=True)
            # Mode 1 histogram bins are [black dots, white dots].
            if raw.mode != "1" or corrected.mode != "1":
                raise AssertionError("Dizzy must return a native 1-bit raster.")
            total = width * height
            target = tone / 255.0
            white_before = raw.histogram()[1] / total
            white_after = corrected.histogram()[1] / total
            item = {
                "variant": variant, "gray": tone,
                "target_white_pct": target * 100,
                "baseline_white_pct": white_before * 100,
                "calibrated_white_pct": white_after * 100,
                "baseline_error_pp": (white_before - target) * 100,
                "calibrated_error_pp": (white_after - target) * 100,
            }
            entries.append(item)
            rows.append(item)
        before = [abs(r["baseline_error_pp"]) for r in entries]
        after = [abs(r["calibrated_error_pp"]) for r in entries]
        summary[variant] = {
            "levels_measured": len(entries),
            "mae_before_pp": sum(before) / len(entries),
            "mae_after_pp": sum(after) / len(entries),
            "max_before_pp": max(before),
            "max_after_pp": max(after),
            "improvement_pct": (100 * (sum(before) - sum(after)) / sum(before)
                                if sum(before) else 0.0),
        }
    return {
        "metadata": {"algorithm": "Meong CPU Dizzy", "calibration_id": CALIBRATION_ID,
                     "width": width, "height": height, "seed": seed,
                     "tones": list(sorted(requested)), "paper_calibrated": False},
        "summary": summary, "rows": rows,
    }


def plot_svg(report):
    """Two stacked, readable response charts (baseline vs LUT vs ideal)."""
    width = 980
    panel_height = 325
    height = 80 + panel_height * len(report["summary"])
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"'
        ' role="img" aria-label="Dizzy CPU grayscale tone fidelity">'
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="58" y="29" font-size="21" font-weight="bold" '
        'fill="#202c39">Meong Dizzy | Grayscale fidelity</text>',
        '<text x="58" y="49" font-size="13" fill="#4a5568">'
        '256 gray levels; Y axis = white-dot coverage; DIGITAL ONLY</text>',
    ]
    colors = (
        ("target_white_pct", "#64748b", "Ideal", "5 3"),
        ("baseline_white_pct", "#d97706", "Original Dizzy", ""),
        ("calibrated_white_pct", "#0284c7", "With CPU tone LUT", ""),
    )
    for index, (variant, stats) in enumerate(report["summary"].items()):
        top = 74 + index * panel_height
        left, right = 80, 919
        chart_top, chart_bottom = top + 45, top + 247
        body.append(
            f'<text x="58" y="{top+19}" font-size="17" fill="#17212c"'
            f' font-weight="bold">{escape(variant)}</text>'
            f'<text x="350" y="{top+19}" font-size="12" fill="#4a5568">'
            f'MAE {stats["mae_before_pp"]:.3f}pp to'
            f' {stats["mae_after_pp"]:.3f}pp</text>')
        for fraction in (0, .25, .5, .75, 1):
            yy = chart_bottom - fraction * (chart_bottom - chart_top)
            body.append(
                f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}"'
                ' stroke="#e2e8f0"/>'
                f'<text x="36" y="{yy+4:.1f}" font-size="11" fill="#64748b">'
                f'{fraction*100:.0f}%</text>')
        for x in (0, 64, 128, 192, 255):
            xx = left + (right-left) * x / 255
            body.append(
                f'<text x="{xx:.1f}" y="{chart_bottom+19}" text-anchor="middle"'
                f' font-size="11" fill="#64748b">{x}</text>')
        points = [r for r in report["rows"] if r["variant"] == variant]
        for key, color, label, dash in colors:
            pts = " ".join(
                f'{left + (right-left)*r["gray"]/255:.1f},'
                f'{chart_bottom - (chart_bottom-chart_top)*r[key]/100:.1f}'
                for r in points)
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            body.append(
                f'<polyline points="{pts}" fill="none" stroke="{color}"'
                f' stroke-width="2.0"{dash_attr}/>')
        for j, (_, color, label, dash) in enumerate(colors):
            xx = 90 + j * 255
            yy = chart_bottom + 43
            body.append(
                f'<line x1="{xx}" y1="{yy}" x2="{xx+25}" y2="{yy}"'
                f' stroke="{color}" stroke-width="3"/>'
                f'<text x="{xx+32}" y="{yy+4}" fill="#334155" font-size="12">'
                f'{escape(label)}</text>')
    body.append("</svg>")
    return "\n".join(body) + "\n"


def write_fidelity_report(report, directory: Path):
    """Create verifiable human-readable data and plot; never print on paper."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    csv_file = directory / "dizzy_grayscale_0-255.csv"
    json_file = directory / "dizzy_fidelity_summary.json"
    plot_file = directory / "dizzy_fidelity.svg"
    with csv_file.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=tuple(report["rows"][0]))
        writer.writeheader()
        for row in report["rows"]:
            writer.writerow({k: round(v, 7) if isinstance(v, float) else v
                             for k, v in row.items()})
    json_file.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    plot_file.write_text(plot_svg(report), encoding="utf-8")
    return csv_file, json_file, plot_file


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline Meong CPU Dizzy tone audit")
    parser.add_argument("--output-dir", type=Path, default=Path("data/dizzy_fidelity"))
    parser.add_argument("--width", type=int, default=96)
    parser.add_argument("--height", type=int, default=96)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tone-step", type=int, default=1,
                        help="1 evaluates every gray level 0..255 (recommended)")
    parser.add_argument("--assert-improvement", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.tone_step <= 255:
        parser.error("--tone-step must be between 1 and 255")
    tones = sorted(set((*range(0, 256, args.tone_step), 255)))
    report = measure_fidelity(
        width=args.width, height=args.height, seed=args.seed, tones=tones)
    paths = write_fidelity_report(report, args.output_dir)
    for variant, s in report["summary"].items():
        print(f"{variant}: MAE {s['mae_before_pp']:.4f} -> "
              f"{s['mae_after_pp']:.4f} percentage points"
              f" ({s['improvement_pct']:+.1f}% improvement)")
        if args.assert_improvement and not s["mae_after_pp"] < s["mae_before_pp"]:
            return 1
    for path in paths:
        print("saved", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
