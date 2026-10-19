"""Decode branded QR pixels, including the size used in saved compositions.

These tests use OpenCV as an independent reader. Matching dimensions alone
would miss a misplaced logo or a real URL made unreadable by its overlay.
No test connects to Drive, a payment provider, a webcam, or a physical printer.
"""

import unittest

import cv2
import numpy as np
from PIL import Image, ImageChops
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
        # Synthetic destination whose automatic mask becomes unreadable to
        # OpenCV after a centered insert; another permitted mask must work.
        "https://drive.google.com/drive/folders/AC0aHap-ztwDxJcb7jlVU4rDzyWI767ijEFgb-?usp=sharing",
    )

    def assert_decodes(self, image, expected):
        """Check the pixels a GUI/printer receives, not the encoder's payload."""
        decoded, points, _ = cv2.QRCodeDetector().detectAndDecode(np.asarray(image))
        self.assertIsNotNone(points)
        self.assertEqual(decoded, expected)

    def test_logo_is_at_the_geometric_center_for_short_and_drive_urls(self):
        """Measure changed output pixels instead of trusting layout metadata.

        The previous implementation decoded successfully but moved the logo
        72 pixels upwards for a typical Drive link. A scan-only regression
        therefore passed despite the visible placement bug. Reconstruct the
        unbranded matrix and locate the actual overlaid rectangle in its delta.
        """
        for url in self.URLS:
            for maximum in (None, 210, 384):
                for monochrome in (False, True):
                    with self.subTest(url=url, size=maximum, monochrome=monochrome):
                        image = create_qr_image(url, max_size=maximum, monochrome=monochrome)
                        reference = qrcode.QRCode(
                            version=image.info.get('qr_version', 4),
                            error_correction=qrcode.constants.ERROR_CORRECT_H,
                            mask_pattern=image.info.get('qr_mask_pattern'),
                            box_size=8, border=4)
                        reference.add_data(url)
                        reference.make(fit=True)
                        reference.box_size = image.width // (reference.modules_count + 8)
                        bounds = ImageChops.difference(
                            image, reference.make_image().convert('RGB')).getbbox()
                        self.assertIsNotNone(bounds)
                        left, top, right, bottom = bounds
                        self.assertLessEqual(abs(left + right - image.width), 2)
                        self.assertLessEqual(abs(top + bottom - image.height), 2)

    def test_realistic_folder_urls_decode_at_display_and_footer_sizes(self):
        for url in self.URLS:
            for max_size in (None, 210, 384):
                for monochrome in (False, True):
                    with self.subTest(url=url, size=max_size, monochrome=monochrome):
                        image = create_qr_image(url, max_size=max_size, monochrome=monochrome)
                        self.assertEqual(image.mode, "RGB")
                        self.assertEqual(image.width, image.height)
                        if max_size is not None:
                            self.assertLessEqual(image.width, max_size)
                        self.assert_decodes(image, url)
                        if max_size is None:
                            self.assert_decodes(image.resize((180, 180), Image.Resampling.NEAREST), url)
                        pixels = np.asarray(image)
                        if monochrome:
                            # One-bit artwork must not leave hidden gray/color
                            # pixels for a future thermal adapter to reinterpret.
                            self.assertTrue(np.isin(pixels, (0, 255)).all())
                        else:
                            # A plain QR also decodes: require actual approved
                            # color artwork, so an omitted logo cannot pass.
                            self.assertTrue(np.any(pixels[:, :, 0] != pixels[:, :, 2]))

    def test_overlay_preserves_finders_uncovered_alignment_marks_and_the_white_margin(self):
        for url in self.URLS:
            with self.subTest(url=url):
                # Build an unmodified reference with the same encoder settings.
                # The centered code may select another valid mask. Rebuild
                # that matrix before checking pixels; a different mask would
                # otherwise look like changes outside the actual logo plate.
                branded = create_qr_image(url)
                reference = qrcode.QRCode(version=branded.info['qr_version'],
                                          mask_pattern=branded.info['qr_mask_pattern'],
                                          error_correction=qrcode.constants.ERROR_CORRECT_H,
                                          box_size=8, border=4)
                reference.add_data(url)
                reference.make(fit=True)
                plain = reference.make_image().convert("RGB")
                self.assertEqual(branded.size, plain.size)
                delta = ImageChops.difference(branded, plain).getbbox()
                self.assertIsNotNone(delta)
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
                        pattern = tuple((v + 4) * 8 for v in
                                        (column - 2, row - 2, column + 3, row + 3))
                        if (pattern[0] < delta[2] and pattern[2] > delta[0]
                                and pattern[1] < delta[3] and pattern[3] > delta[1]):
                            # A central alignment mark may be intentionally
                            # hidden by the logo. Final native/preview decoding
                            # above checks readability; all other marks stay.
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
