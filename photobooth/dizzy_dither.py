"""Experimental CPU Dizzy dithering aligned with Liam Appelbe's articles.

Article (8-neighbor, axial 1.0 / diagonal 0.1):
https://liamappelbe.medium.com/dizzy-dithering-2ae76dbceba1
Follow-up (4 orthogonal neighbors, including GPU discussion):
https://liamappelbe.medium.com/dizzy-dithering-on-the-gpu-84f2d2c12a82

This module is lab-only. It is not part of the production ESC/POS printer
pipeline. It deliberately excludes an uncalibrated contrast-correction LUT.
"""
from __future__ import annotations

from array import array
import random
from typing import Iterator

from PIL import Image

DIZZY_VARIANTS = ("article-8", "orthogonal-4")
DEFAULT_DIZZY_SEED = 42


def _permuted_pixel_indices(count: int, seed: int) -> Iterator[int]:
    """Visit each valid index once using the article's five-round permutation.

    Each round multiplies by an odd number and xors a mask modulo 2**k;
    both operations are bijections. Skipping the padded indices therefore
    visits every pixel exactly once without materializing a shuffled list.
    """
    if count < 1:
        raise ValueError("Dizzy requires at least one pixel.")
    bits = (count - 1).bit_length()
    padded = 1 << bits
    mask = padded - 1
    rng = random.Random(seed)
    rounds = tuple((rng.getrandbits(bits) | 1, rng.getrandbits(bits))
                   for _ in range(5))
    for index in range(padded):
        shuffled = index
        for multiplier, xor in rounds:
            shuffled = ((shuffled * multiplier) & mask) ^ xor
        if shuffled < count:
            yield shuffled


def dizzy_dither(image: Image.Image, *, variant: str = "article-8",
                 seed: int = DEFAULT_DIZZY_SEED) -> Image.Image:
    """Return native-sized mode-1 raster using randomized error diffusion.

    'article-8' distributes quantization error to all unprocessed neighboring
    pixels, axial weight 1.0 and diagonal weight 0.1, normalized only over
    eligible neighbors. 'orthogonal-4' evenly weights the four axial neighbors
    from the follow-up article and Python Gist. The working gray buffer is
    float-valued to avoid per-step 8-bit rounding of propagated errors.
    """
    if variant not in DIZZY_VARIANTS:
        raise ValueError(f"Unknown Dizzy variant: {variant!r}")
    if type(seed) is not int or not 0 <= seed <= 0xFFFFFFFF:
        raise ValueError("Dizzy seed must be an integer from 0 to 2^32-1.")
    gray = image.convert("L")
    width, height = gray.size
    count = width * height
    if not count:
        raise ValueError("Dizzy requires at least one pixel.")

    # The float buffer retains the fractional errors that would be lost by
    # modifying an 8-bit PIL pixel buffer directly (unlike the minimal Gist).
    values = array("f", (value / 255.0 for value in gray.tobytes()))
    processed = bytearray(count)
    result = bytearray(count)
    diagonal = variant == "article-8"

    for p in _permuted_pixel_indices(count, seed):
        old = values[p]
        new = 255 if old >= 0.5 else 0
        result[p] = new
        processed[p] = 1
        error = old - (new / 255.0)
        if error == 0:
            continue

        x = p % width
        y = p // width
        adjacent = []
        if x > 0 and not processed[p - 1]:
            adjacent.append((p - 1, 1.0))
        if x + 1 < width and not processed[p + 1]:
            adjacent.append((p + 1, 1.0))
        if y > 0 and not processed[p - width]:
            adjacent.append((p - width, 1.0))
        if y + 1 < height and not processed[p + width]:
            adjacent.append((p + width, 1.0))
        if diagonal:
            if x > 0 and y > 0 and not processed[p - width - 1]:
                adjacent.append((p - width - 1, 0.1))
            if x + 1 < width and y > 0 and not processed[p - width + 1]:
                adjacent.append((p - width + 1, 0.1))
            if x > 0 and y + 1 < height and not processed[p + width - 1]:
                adjacent.append((p + width - 1, 0.1))
            if x + 1 < width and y + 1 < height and not processed[p + width + 1]:
                adjacent.append((p + width + 1, 0.1))

        if adjacent:
            total_weight = sum(weight for _, weight in adjacent)
            scaled_error = error / total_weight
            for neighbor, weight in adjacent:
                values[neighbor] += scaled_error * weight

    # The conversion uses no secondary halftone; bytes are already 0 or 255.
    return Image.frombytes("L", (width, height), bytes(result)).convert(
        "1", dither=Image.Dither.NONE)
