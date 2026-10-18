"""Regression tests for the owner-approved Floyd photo printing profile."""
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from photobooth.dither_lab import DitherProfile, render_thermal_image
from photobooth.printer import PrinterConfig, ThermalPrinter, dither_image


class OwnerFloydPhotoDefaultTests(unittest.TestCase):
    def payload_raster(self, image, config=None, *, override=None, legacy=False):
        class Dummy:
            output = b"dummy"
            bitmap = None
            def image(self, bitmap, **_kwargs):
                self.bitmap = bitmap.copy()
            def cut(self):
                pass
        instance = Dummy()
        printer_mod = types.ModuleType("escpos.printer")
        printer_mod.Dummy = lambda: instance
        escpos_mod = types.ModuleType("escpos")
        escpos_mod.printer = printer_mod
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "input.png"
            image.save(path)
            with patch.dict(sys.modules, {"escpos": escpos_mod, "escpos.printer": printer_mod}):
                env = {"PHOTOBOOTH_PHOTO_TUNING": "legacy"} if legacy else {}
                with patch.dict(os.environ, env, clear=False):
                    if not legacy:
                        os.environ.pop("PHOTOBOOTH_PHOTO_TUNING", None)
                    ThermalPrinter(config or PrinterConfig())._build_payload(
                        path, dither_mode=override
                    )
        return instance.bitmap

    def setUp(self):
        self.image = Image.new("RGB", (576, 64))
        self.image.putdata([(x * 255 // 575, y * 255 // 63, (x+y)%256)
                            for y in range(64) for x in range(576)])

    def test_normal_photo_uses_owner_exact_preset(self):
        actual = self.payload_raster(self.image)
        expected = render_thermal_image(self.image, DitherProfile(
            mode="floyd-steinberg", width_dots=576,
            brightness=0.652, contrast=2.104, gamma=2.352,
            sharpness=2.073, threshold=128
        ))
        self.assertEqual(actual.mode, "1")
        self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_legacy_rollback_retains_original_floyd(self):
        actual = self.payload_raster(self.image, legacy=True)
        self.assertEqual(actual.tobytes(),
                         dither_image(self.image.convert("L"), "floyd-steinberg").tobytes())

    def test_bayer_and_threshold_keep_old_path(self):
        for mode in ("bayer", "threshold"):
            with self.subTest(mode=mode):
                cfg = PrinterConfig(dither_mode=mode)
                actual = self.payload_raster(self.image, cfg)
                expected = dither_image(self.image.convert("L"), mode)
                self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_comparison_override_stays_legacy(self):
        actual = self.payload_raster(self.image, override="floyd-steinberg")
        self.assertEqual(actual.tobytes(),
                         dither_image(self.image.convert("L"), "floyd-steinberg").tobytes())

    def test_qr_receipts_use_separate_module(self):
        # QR payment slip is independently encoded by qris_print.py.
        # Check source without importing qrcode, which is not installed by
        # the lightweight Pillow-only Dither Lab CI job.
        source = (Path(__file__).resolve().parents[1]
                  / "photobooth" / "qris_print.py").read_text(encoding="utf-8")
        self.assertIn("def render_payment_slip(", source)
        self.assertIn("def escpos_raster(", source)
        self.assertNotIn("render_thermal_image", source)
        self.assertNotIn("from photobooth.dither_lab", source)


if __name__ == "__main__":
    unittest.main()
