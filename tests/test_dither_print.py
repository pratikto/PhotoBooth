"""Test that a physical comparison reuses preview bytes without re-dithering."""
import unittest
from PIL import Image
from photobooth.dither_lab import DitherProfile
from photobooth.dither_print import annotated_raster, printable_destination
from photobooth.printer import PrinterConfig


class DitherPhysicalSafetyTests(unittest.TestCase):
    def test_header_does_not_change_original_raster(self):
        source = Image.new("1", (576, 180), 1)
        for y in range(0, 180, 3):
            source.putpixel((y, y), 0)
        original = source.tobytes()
        tagged = annotated_raster(source, DitherProfile())
        self.assertEqual(source.tobytes(), original)
        self.assertEqual(tagged.width, source.width)
        self.assertEqual(tagged.crop((0, tagged.height - source.height,
                                      source.width, tagged.height)).tobytes(), original)

    def test_enhancement_print_header_does_not_mutate_native_raster(self):
        image = Image.new("1", (384, 96), 255)
        image.putpixel((18, 35), 0)
        initial = image.tobytes()
        normal = annotated_raster(image, DitherProfile(mode="bayer", width_dots=384))
        enhanced = annotated_raster(image, DitherProfile(
            mode="bayer", width_dots=384, smart_enhance=True,
            postprocess_enabled=True, clahe_strength=0.4,
            dot_cleanup_level=2))
        self.assertGreater(enhanced.height, normal.height)
        self.assertEqual(enhanced.crop((0, enhanced.height - 96, 384,
                                        enhanced.height)).tobytes(), initial)
        self.assertEqual(image.tobytes(), initial)

    def test_requires_binary_image_and_native_width(self):
        with self.assertRaises(ValueError):
            annotated_raster(Image.new("RGB", (576, 40)), DitherProfile())
        with self.assertRaises(ValueError):
            annotated_raster(Image.new("1", (600, 40)), DitherProfile())

    def test_route_must_be_configured(self):
        self.assertFalse(printable_destination(PrinterConfig(
            usb_device_path=None, windows_printer_name="")))
        self.assertTrue(printable_destination(PrinterConfig(
            usb_device_path=None, windows_printer_name="POS80 Printer")))


if __name__ == "__main__":
    unittest.main()
