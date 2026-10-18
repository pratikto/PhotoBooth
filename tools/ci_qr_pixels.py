"""Strict independent reader for QR codes captured in synthetic GUI screenshots.

This reader NEVER uses the known source payload or a Kivy texture to determine
whether a QR passes. The input must be pixels cropped from the exported screen.
The one-bit/module layout cannot be repaired by nearest-neighbour enlargement;
the extra views only reduce OpenCV QRCodeDetector's scale-specific false negatives.

A fully blank, clipped, occluded, or genuinely undecodable QR still returns
an empty string so the calling test must FAIL as before. This module is used
exclusively by synthetic CI rendering, not the shipped payment or scanner.
"""

from __future__ import annotations

import cv2


def decode_rendered_qr_pixels(pixels):
    """Read exact QR text from screenshot BGR pixels at bounded camera scales."""
    if pixels is None or pixels.size == 0:
        return ""

    detector = cv2.QRCodeDetector()
    # Native pixels remain first choice. Scaling with nearest-neighbour
    # duplicates existing painted pixels instead of inventing missing modules,
    # correcting contrast, generating a fresh QR, or masking poor visual output.
    for scale in (1, 2, 3):
        candidate = pixels if scale == 1 else cv2.resize(
            pixels, None, fx=scale, fy=scale,
            interpolation=cv2.INTER_NEAREST,
        )
        decoded, _, _ = detector.detectAndDecode(candidate)
        if decoded:
            return decoded
    return ""
