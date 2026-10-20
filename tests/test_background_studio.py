"""FEAT-021 isolated background processing tests: no ONNX/network/hardware."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photobooth.background_studio import (
    BackgroundProcessingError, BackgroundStudio, CLEAN_STUDIO, ORIGINAL,
    STUDIO_COLOR, cached_model_path, composite_clean_studio,
)


class BackgroundStudioTests(unittest.TestCase):
    def test_cache_detection_never_downloads_and_obeys_legacy_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(cached_model_path({}, root))
            new = root / ".rembg" / "models" / "birefnet-portrait" / "birefnet-portrait.onnx"
            new.parent.mkdir(parents=True)
            new.write_bytes(b"cached-fixture")
            self.assertEqual(cached_model_path({}, root), new)
            custom = root / "configured"
            custom.mkdir()
            old = custom / "birefnet-portrait.onnx"
            old.write_bytes(b"cached-legacy")
            self.assertEqual(cached_model_path({"U2NET_HOME": str(custom)}, root), old)

    def test_alpha_composite_preserves_source_and_expected_background(self):
        source = Image.new("RGB", (4, 2), (200, 5, 10))
        before = source.tobytes()
        cutout = source.convert("RGBA")
        alpha = Image.new("L", source.size, 0)
        alpha.putpixel((1, 0), 255)
        alpha.putpixel((2, 0), 128)
        cutout.putalpha(alpha)
        result = composite_clean_studio(source, cutout)
        self.assertEqual(result.getpixel((0, 0)), STUDIO_COLOR)
        self.assertEqual(result.getpixel((1, 0)), (200, 5, 10))
        self.assertEqual(result.getpixel((2, 0))[0], (200 * 128 + 248 * 127 + 127) // 255)
        self.assertEqual(source.tobytes(), before)
        self.assertEqual(result.mode, "RGB")

    def test_rejects_invalid_or_unusable_masks(self):
        source = Image.new("RGB", (4, 3), (100, 50, 30))
        for cutout in (
            source,
            Image.new("RGBA", (1, 1)),
            Image.new("RGBA", source.size, (1, 2, 3, 0)),
            Image.new("RGBA", source.size, (1, 2, 3, 255)),
        ):
            with self.subTest(mode=cutout.mode, size=cutout.size), self.assertRaises(BackgroundProcessingError):
                composite_clean_studio(source, cutout)

    def test_three_photo_inference_reuses_one_session_and_keeps_raw_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photos = []
            for index in range(3):
                path = root / f"photo-{index}.jpg"
                Image.new("RGB", (10, 8), (30 + index * 20, 70, 90)).save(path)
                photos.append(path)
            original = [p.read_bytes() for p in photos]
            created = []
            calls = []

            def factory(name):
                created.append(name)
                return object()

            def remove(source, *, session):
                calls.append((source.size, session))
                mask = source.convert("RGBA")
                alpha = Image.new("L", source.size, 0)
                alpha.paste(255, (3, 1, 7, 7))
                mask.putalpha(alpha)
                return mask

            service = BackgroundStudio(session_factory=factory, remove_function=remove,
                                       model_locator=lambda: root / "preseeded.onnx")
            results = service.process_three(photos)
            self.assertEqual(len(results), 3)
            self.assertEqual(created, ["birefnet-portrait"])
            self.assertEqual(len(calls), 3)
            self.assertEqual(results[0].getpixel((0, 0)), STUDIO_COLOR)
            self.assertEqual([p.read_bytes() for p in photos], original)
            service.process_three(photos)
            self.assertEqual(len(created), 1)

    def test_missing_model_refuses_inference_and_falls_back_to_original(self):
        called = []
        service = BackgroundStudio(
            session_factory=lambda name: called.append("factory"),
            remove_function=lambda image, *, session: called.append("remove"),
            model_locator=lambda: None,
        )
        self.assertFalse(service.available_offline())
        with self.assertRaisesRegex(BackgroundProcessingError, "Model BiRefNet"):
            service.process_three([Path("missing")] * 3)
        self.assertEqual(called, [])

    def test_bad_second_mask_rejects_entire_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photos = []
            for i in range(3):
                p = root / f"{i}.png"
                Image.new("RGB", (5, 5), "red").save(p)
                photos.append(p)
            count = []

            def remove(source, *, session):
                count.append(1)
                image = source.convert("RGBA")
                alpha = Image.new("L", source.size, 0)
                if len(count) != 2:
                    alpha.putpixel((0, 0), 255)
                image.putalpha(alpha)
                return image

            service = BackgroundStudio(session_factory=lambda name: object(),
                                       remove_function=remove,
                                       model_locator=lambda: root,
                                       )
            with self.assertRaises(BackgroundProcessingError):
                service.process_three(photos)
            self.assertEqual(len(count), 2)


if __name__ == "__main__":
    unittest.main()
