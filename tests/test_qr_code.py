"""Decode branded QR pixels, including the size used in saved compositions.

These tests use OpenCV as an independent reader. Matching dimensions alone
would miss a logo that hides a recognition pattern or makes a real URL unreadable.
No test connects to Drive, a payment provider, a webcam, or a physical printer.
"""

import unittest

import cv2
import numpy as np
from PIL import ImageChops
import qrcode
from qrcode.util import pattern_position

from photobooth.qr_code import create_qr_image


class BrandedQRTests(unittest.TestCase):
    # The short link uses an ordinary central plate. Longer folder links force
    # higher QR versions, including versions with a central alignment marker.
    URLS = (
        "https://example.com/",
        "https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz123456",
        "https://drive.google.com/drive/folders/" + "aB3xY7" * 7 + "?usp=sharing",
    )

    def assert_decodes(self, image, expected):
        """Check the pixels a GUI/printer receives, not the encoder's payload."""
        decoded, points, _ = cv2.QRCodeDetector().detectAndDecode(np.asarray(image))
        self.assertIsNotNone(points)
        self.assertEqual(decoded, expected)

    def test_realistic_folder_urls_decode_at_display_and_footer_sizes(self):
        for url in self.URLS:
            for max_size in (None, 210):
                for monochrome in (False, True):
                    with self.subTest(url=url, size=max_size, monochrome=monochrome):
                        image = create_qr_image(url, max_size=max_size, monochrome=monochrome)
                        self.assertEqual(image.mode, "RGB")
                        self.assertEqual(image.width, image.height)
                        if max_size is not None:
                            self.assertLessEqual(image.width, max_size)
                        self.assert_decodes(image, url)
                        pixels = np.asarray(image)
                        if monochrome:
                            # One-bit artwork must not leave hidden gray/color
                            # pixels for a future thermal adapter to reinterpret.
                            self.assertTrue(np.isin(pixels, (0, 255)).all())
                        else:
                            # A plain QR also decodes: require actual approved
                            # color artwork, so an omitted logo cannot pass.
                            self.assertTrue(np.any(pixels[:, :, 0] != pixels[:, :, 2]))

    def test_overlay_preserves_finders_alignment_marks_and_the_white_margin(self):
        for url in self.URLS:
            with self.subTest(url=url):
                # Build an unmodified reference with the same encoder settings.
                # Compare recognition cells directly; successful decoding alone
                # could hide accidental damage repaired by error correction.
                reference = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H,
                                          box_size=8, border=4)
                reference.add_data(url)
                reference.make(fit=True)
                plain = reference.make_image().convert("RGB")
                branded = create_qr_image(url)
                self.assertEqual(branded.size, plain.size)
                self.assertIsNotNone(ImageChops.difference(branded, plain).getbbox())
                cells = reference.modules_count

                def compare_grid_box(left, top, right, bottom):
                    # Grid coordinates exclude the quiet zone, while image
                    # coordinates include four extra modules at each edge.
                    box = tuple((value + 4) * 8 for value in (left, top, right, bottom))
                    self.assertIsNone(ImageChops.difference(
                        branded.crop(box), plain.crop(box)).getbbox())

                for box in ((0, 0, 9, 9), (cells - 9, 0, cells, 9),
                            (0, cells - 9, 9, cells), (6, 0, 7, cells),
                            (0, 6, cells, 7)):
                    compare_grid_box(*box)
                for row in pattern_position(reference.version):
                    for column in pattern_position(reference.version):
                        if ((row == 6 and column in (6, cells - 7))
                                or (column == 6 and row == cells - 7)):
                            continue
                        compare_grid_box(column - 2, row - 2, column + 3, row + 3)
                pixels = np.asarray(branded)
                for edge in (pixels[:32], pixels[-32:], pixels[:, :32], pixels[:, -32:]):
                    self.assertTrue(np.all(edge == 255))

    def test_payment_demo_can_stay_plain_and_cached_images_are_independent(self):
        demo = "PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR 5000"
        plain = create_qr_image(demo, with_logo=False)
        self.assertTrue(np.isin(np.asarray(plain), (0, 255)).all())
        self.assert_decodes(plain, demo)

        # A consumer may draw into its own image. A later session using the
        # same cached URL must still receive the original, readable artwork.
        first = create_qr_image(self.URLS[0])
        original = first.tobytes()
        first.paste("black", (0, 0, first.width, first.height))
        second = create_qr_image(self.URLS[0])
        self.assertEqual(second.tobytes(), original)
        self.assert_decodes(second, self.URLS[0])

    def test_empty_destinations_and_impossible_sizes_fail_clearly(self):
        for content in (None, "", " \n\t"):
            with self.subTest(content=content), self.assertRaises(ValueError):
                create_qr_image(content)
        for size in (0, -1, True, 10.5, 20):
            with self.subTest(size=size), self.assertRaises(ValueError):
                create_qr_image(self.URLS[0], max_size=size)


if __name__ == "__main__":
    unittest.main()
