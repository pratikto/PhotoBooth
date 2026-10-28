"""Meong presentation for verified Sandbox QR pixels; no payment authority."""
from photobooth.qris_images import payment_qr_image


def with_meong_logo(original):
    """Reuse the Drive renderer only when the original payload stays identical.

    The shared renderer checks its centered logo at full resolution and at
    180px. A presentation failure retains the downloaded image; it must never
    discard an existing order or manufacture a QR from its image URL.
    """
    try:
        import cv2
        import numpy as np
        from photobooth.qr_code import create_qr_image

        reader = cv2.QRCodeDetector()
        payload, _, _ = reader.detectAndDecode(np.asarray(original.convert('RGB')))
        # The Drive helper trims its input. Never let that alter payment data.
        if not payload or payload != payload.strip():
            return original
        branded = create_qr_image(payload)
        decoded, _, _ = reader.detectAndDecode(np.asarray(branded))
        return branded if decoded == payload else original
    except Exception:
        # No QR data, URLs or raw decoder exceptions belong in logs/UI errors.
        return original


def branded_sandbox_qr_image(order):
    """Keep the original bounded downloader and its errors; brand Sandbox only."""
    original = payment_qr_image(order)
    return with_meong_logo(original) if order['mode'] == 'sandbox' else original
