"""Negative and positive screenshot-only QR regression checks for CI."""

import unittest

import cv2
import numpy as np
from PIL import Image
import qrcode

from tools.ci_qr_pixels import decode_rendered_qr_pixels


class RenderedQRPixelTests(unittest.TestCase):
    @staticmethod
    def qr_pixels(text, displayed_width):
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                           box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        rgb = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        displayed = rgb.resize((displayed_width, displayed_width),
                               Image.Resampling.NEAREST)
        # Same BGR convention as cv2.imread() on exported Kivy screenshots.
        return cv2.cvtColor(np.array(displayed), cv2.COLOR_RGB2BGR)

    def test_displayed_demo_qr_payload_is_exact_at_multiple_screen_sizes(self):
        # Different amounts/IDs exercise distinct QR matrices without touching
        # production's uuid4 payment attempts or external payment providers.
        for amount, suffix in ((10000, "0000000001"),
                               (15000, "0000000002"),
                               (180000, "0000000003")):
            attempt_id = "DEMO-CI" + suffix
            payload = (f"PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR {amount} "
                       f"- {attempt_id}")
            for width in (150, 240, 320):
                with self.subTest(amount=amount, width=width):
                    pixels = self.qr_pixels(payload, width)
                    self.assertEqual(decode_rendered_qr_pixels(pixels), payload)

    def test_blank_or_empty_screenshot_is_not_accepted(self):
        self.assertEqual(decode_rendered_qr_pixels(None), "")
        self.assertEqual(
            decode_rendered_qr_pixels(np.zeros((0, 0, 3), dtype=np.uint8)), "")
        self.assertEqual(
            decode_rendered_qr_pixels(np.full((240, 240, 3), 255, dtype=np.uint8)),
            "",
        )

    def test_obscured_qr_cannot_be_passed_by_resizing(self):
        text = "PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR 15000 - DEMO-CI0000000002"
        pixels = self.qr_pixels(text, 240)
        # Opaque cover destroys the majority of QR modules and finders.
        cv2.rectangle(pixels, (16, 16), (223, 223), (255, 255, 255), -1)
        self.assertEqual(decode_rendered_qr_pixels(pixels), "")


if __name__ == "__main__":
    unittest.main()
