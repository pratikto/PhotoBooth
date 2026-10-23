"""Optional Pillow-only image enhancement and safe 1-bit post-processing.

This is strictly an offline dither-lab experiment. Both passes are opt-in,
operate only on photo rasters, and never issue printer commands. All operators
preserve native pixel dimensions. The post-processor outputs mode-1 raster
without another dithering pass.
"""
from __future__ import annotations

from math import ceil, floor

from PIL import Image, ImageChops, ImageFilter, ImageOps


def _clahe_tile_lut(tile: Image.Image, clip_limit: float) -> list[int]:
    """Build a clipped local cumulative-histogram LUT for one grayscale tile."""
    counts = tile.histogram()
    present = [value for value, count in enumerate(counts) if count]
    # Don't amplify camera noise in a nearly flat patch.
    if not present or present[-1] - present[0] < 12:
        return list(range(256))
    pixels = tile.width * tile.height
    cap = max(2, int(ceil(clip_limit * pixels / 256.0)))
    excess = sum(max(0, count - cap) for count in counts)
    counts = [min(count, cap) for count in counts]
    whole, remainder = divmod(excess, 256)
    # Spread the clipped mass across all bins without biasing dark bins.
    if whole or remainder:
        counts = [n + whole + (1 if (i * 73) % 256 < remainder else 0)
                  for i, n in enumerate(counts)]
    cdf = 0
    first = next((n for n in counts if n), 0)
    denominator = max(1, pixels - first)
    result = []
    for count in counts:
        cdf += count
        result.append(max(0, min(255, round(255 * (cdf - first) / denominator))))
    return result


def clahe_gray(gray: Image.Image, strength: float) -> Image.Image:
    """Contrast-limited adaptive histogram equalization with tile interpolation.

    Pixels are interpolated between local clipped histograms to avoid
    checkerboard tile boundaries. All steps use Pillow/Python, without OpenCV
    or NumPy. Strength 0 returns an unchanged image.
    """
    if not 0 <= strength <= 1:
        raise ValueError("CLAHE strength must be between 0 and 1.")
    gray = gray.convert("L")
    if strength == 0:
        return gray
    width, height = gray.size
    nx = min(8, max(1, ceil(width / 96)))
    ny = min(12, max(1, ceil(height / 128)))
    tile_w, tile_h = ceil(width / nx), ceil(height / ny)
    luts = []
    for iy in range(ny):
        row = []
        for ix in range(nx):
            tile = gray.crop((ix * tile_w, iy * tile_h,
                              min(width, (ix + 1) * tile_w),
                              min(height, (iy + 1) * tile_h)))
            row.append(_clahe_tile_lut(tile, 2.0 + 1.5 * strength))
        luts.append(row)

    xcoords = []
    for x in range(width):
        position = (x + 0.5) / tile_w - 0.5
        lo = floor(position)
        hi = lo + 1
        t = position - lo
        xcoords.append((max(0, min(nx - 1, lo)),
                        max(0, min(nx - 1, hi)), t))

    source = gray.tobytes()
    mapped = bytearray(len(source))
    offset = 0
    for y in range(height):
        position = (y + 0.5) / tile_h - 0.5
        lo = floor(position)
        hi = lo + 1
        ty = position - lo
        top = luts[max(0, min(ny - 1, lo))]
        bottom = luts[max(0, min(ny - 1, hi))]
        for ix, (left, right, tx) in enumerate(xcoords):
            shade = source[offset + ix]
            upper = top[left][shade] * (1 - tx) + top[right][shade] * tx
            lower = bottom[left][shade] * (1 - tx) + bottom[right][shade] * tx
            mapped[offset + ix] = max(0, min(255, round(
                upper * (1 - ty) + lower * ty)))
        offset += width
    return Image.blend(
        gray, Image.frombytes("L", gray.size, bytes(mapped)), strength)


def apply_smart_enhance(
    gray: Image.Image, *, clahe_strength: float,
    denoise_level: int, tone_strength: float,
) -> Image.Image:
    """Median-denoise, adaptive local contrast, then restrained tonal balance."""
    if not 0 <= denoise_level <= 2:
        raise ValueError("Denoise level must be 0..2.")
    if not 0 <= tone_strength <= 1:
        raise ValueError("Tone strength must be 0..1.")
    output = gray.convert("L")
    for _ in range(denoise_level):
        output = output.filter(ImageFilter.MedianFilter(size=3))
    if clahe_strength:
        output = clahe_gray(output, clahe_strength)
    if tone_strength:
        balanced = ImageOps.autocontrast(output, cutoff=1, preserve_tone=True)
        output = Image.blend(output, balanced, tone_strength)
    return output


def refine_binary_raster(
    raster: Image.Image, reference_gray: Image.Image, *,
    dot_cleanup_level: int, edge_refine_level: int,
) -> Image.Image:
    """Restrained, content-aware cleanup of native one-bit photo dots.

    Cleanup is *only* allowed in near-white/near-black flat source patches:
    isolated halftone pixels in genuine midtones are intentionally preserved.
    Edge anchors act only at strong grayscale edges and near-extreme tones.
    """
    if raster.mode != "1" or raster.size != reference_gray.size:
        raise ValueError("Expected matched grayscale reference and 1-bit raster.")
    if not 0 <= dot_cleanup_level <= 3 or not 0 <= edge_refine_level <= 3:
        raise ValueError("Post-processing levels must be 0..3.")
    if dot_cleanup_level == 0 and edge_refine_level == 0:
        return raster.copy()
    gray = reference_gray.convert("L")
    result = raster.convert("L")
    # Gradients from the pre-dither grayscale guide, not individual dither dots.
    local_range = ImageChops.difference(
        gray.filter(ImageFilter.MaxFilter(3)),
        gray.filter(ImageFilter.MinFilter(3)),
    )
    if dot_cleanup_level:
        flat = local_range.point(
            lambda value: 255 if value <= 6 + dot_cleanup_level * 2 else 0)
        near_paper = gray.point(
            lambda value: 255 if value <= 3 + dot_cleanup_level * 3
            or value >= 252 - dot_cleanup_level * 3 else 0)
        mask = ImageChops.multiply(flat, near_paper)
        majority = result.filter(ImageFilter.ModeFilter(3))
        result = Image.composite(majority, result, mask)
    if edge_refine_level:
        strong_edge = local_range.point(
            lambda value: 255 if value >= 90 - edge_refine_level * 12 else 0)
        extreme = gray.point(
            lambda value: 255 if value <= 35 + edge_refine_level * 12
            or value >= 220 - edge_refine_level * 12 else 0)
        mask = ImageChops.multiply(strong_edge, extreme)
        anchored = gray.point(lambda value: 0 if value < 128 else 255)
        result = Image.composite(anchored, result, mask)
    return result.convert("1", dither=Image.Dither.NONE)
