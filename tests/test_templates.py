"""Check real receipt artwork, shaped photo placement, and input preservation.

These tests inspect saved pixels rather than checking that a renderer was
called. Synthetic solid colors make photo order, mask leaks, and a wrong
template selection visible without using any customer images or account.
"""

from pathlib import Path
import tempfile
import unittest

import cv2
import numpy as np
from PIL import Image, ImageOps

from photobooth.catalog import (
    CANVAS_SIZE, compose_result, create_template_preview, fit_result_photo, get_templates,
)


class ReceiptTemplateTests(unittest.TestCase):
    def test_every_design_places_three_ordered_photos_and_preserves_ink_and_margins(self):
        """All 36 apertures must fill, with zero edits outside the clip masks."""
        colors = ((221, 43, 60), (39, 154, 82), (37, 99, 221))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photos = []
            for index, color in enumerate(colors):
                path = root / f"capture-{index}.png"
                Image.new("RGB", (800, 600), color).save(path)
                photos.append(path)
            originals = [path.read_bytes() for path in photos]
            self.assertEqual(len(get_templates()), 12)
            for template in get_templates():
                with self.subTest(template=template.name):
                    result_path = compose_result(photos, template, root / "result.png",
                                                 "PB001_00000001", "session_001")
                    with Image.open(template.artwork_path) as source, Image.open(result_path) as result:
                        master = np.asarray(source.convert("RGB"))
                        pixels = np.asarray(result.convert("RGB"))
                    self.assertEqual(pixels.shape[:2], CANVAS_SIZE[::-1])
                    # The original 1 mm (eight-dot) margin on every side stays
                    # byte-identical, so photos cannot widen the receipt art.
                    for area in (np.s_[:8], np.s_[-8:], np.s_[:, :8], np.s_[:, -8:]):
                        np.testing.assert_array_equal(pixels[area], master[area])
                    for index, frame in enumerate(template.apertures):
                        left, top, right, bottom = frame.box
                        crop = pixels[top:bottom, left:right]
                        original = master[top:bottom, left:right]
                        with Image.open(frame.mask_path) as mask_image:
                            mask = np.asarray(mask_image) > 0
                        self.assertGreater(mask.mean(), .45)
                        np.testing.assert_array_equal(crop[mask],
                                                      np.broadcast_to(colors[index], crop[mask].shape))
                        np.testing.assert_array_equal(crop[~mask], original[~mask])
            self.assertEqual([path.read_bytes() for path in photos], originals)

    def test_irregular_apertures_retain_their_distinctive_cutouts(self):
        """A rectangular paste would fill the heart's top center and corners."""
        templates = get_templates()
        heart = templates[1].apertures[0]
        with Image.open(heart.mask_path) as image:
            pixels = np.asarray(image)
        self.assertEqual(pixels[0, 0], 0)
        self.assertEqual(pixels[0, pixels.shape[1] // 2], 0)
        self.assertEqual(pixels[pixels.shape[0] // 2, pixels.shape[1] // 2], 255)
        self.assertLess(np.count_nonzero(pixels) / pixels.size, .85)
        for index in (6, 8):  # Vintage cafe labels and arcade pixel corners.
            frame = templates[index].apertures[0]
            with Image.open(frame.mask_path) as mask:
                self.assertEqual(mask.getpixel((0, 0)), 0)

    def test_landscape_portrait_and_exif_sources_cover_each_aperture_without_mutation(self):
        """The exact selected frame, rather than a global aspect, sets the crop."""
        for size in ((640, 480), (480, 640), (480, 480)):
            source = Image.new("RGB", size, "#759c82")
            # Put a contrasting stripe near one edge to detect crop/rotation.
            source.paste("#d13849", (0, 0, size[0] // 4, size[1]))
            source.getexif()[274] = 6
            before = source.tobytes()
            for template in get_templates():
                for index, frame in enumerate(template.apertures):
                    expected = ImageOps.fit(ImageOps.exif_transpose(source), frame.size,
                                            method=Image.Resampling.LANCZOS)
                    actual = fit_result_photo(source, template, index)
                    self.assertEqual(actual.tobytes(), expected.tobytes())
            self.assertEqual(source.tobytes(), before)
            self.assertEqual(source.getexif()[274], 6)

    def test_local_result_has_no_dummy_or_file_system_qr(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photo = root / "raw.png"
            Image.new("RGB", (640, 480), "#659877").save(photo)
            for template in get_templates():
                path = compose_result([photo] * 3, template, root / "result.png",
                                      "PB001_00000001", "session_001")
                with Image.open(path) as result:
                    crop = np.asarray(result.crop(template.qr_box))
                decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(crop)
                self.assertEqual(decoded, "")

    def test_each_preview_uses_the_selected_master_and_returns_an_independent_image(self):
        signatures = set()
        for template in get_templates():
            preview = create_template_preview(template, (100, 300))
            signatures.add(preview.tobytes())
            before = preview.tobytes()
            preview.paste("red", (0, 0, 100, 300))
            self.assertEqual(create_template_preview(template, (100, 300)).tobytes(), before)
        self.assertEqual(len(signatures), 12)

    def test_invalid_folder_link_cannot_replace_an_existing_result(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "existing.png"
            output.write_bytes(b"existing result")
            for url in ("", "http://example.com", "file:///tmp/photos", "C:/photos"):
                with self.subTest(url=url), self.assertRaises(ValueError):
                    compose_result([Path("missing.jpg")] * 3, get_templates()[0], output,
                                   "PB001_00000001", "session_001", url)
                self.assertEqual(output.read_bytes(), b"existing result")


if __name__ == "__main__":
    unittest.main()
