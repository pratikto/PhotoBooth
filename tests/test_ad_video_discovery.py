"""Regression tests for filename-independent local advertising discovery."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from photobooth import advertising


class LocalAdDiscoveryTests(unittest.TestCase):
    def test_video_names_are_discovered_sorted_for_both_placements(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for name in ("Z promo.MP4", "alpha campaign.webm", "promo (1).mov"):
                (directory / name).write_bytes(b"test fixture")
            (directory / "ignore.txt").write_text("not a video")
            with patch.object(advertising, "DEFAULT_VIDEO_DIR", directory):
                catalog = advertising.AdCatalog()
            names = [item.path.name for item in catalog.items if item.video]
            self.assertEqual(names, ["alpha campaign.webm", "promo (1).mov", "Z promo.MP4"])
            for placement in ("idle", "payment"):
                self.assertEqual(
                    [item.path.name for item in catalog.available(placement) if item.video],
                    names,
                )
            self.assertEqual(len({item.ad_id for item in catalog.items}), len(catalog.items))

    def test_empty_or_missing_directory_preserves_still_image_playlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(advertising, "DEFAULT_VIDEO_DIR", Path(tmp) / "missing"):
                catalog = advertising.AdCatalog()
            self.assertTrue(any(not item.video for item in catalog.available("idle")))
            self.assertTrue(any(not item.video for item in catalog.available("payment")))

    def test_custom_playlist_does_not_auto_append_local_videos(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "other.mp4").write_bytes(b"video")
            custom = directory / "custom.json"
            custom.write_text('{"ads":[]}', encoding="utf-8")
            with patch.object(advertising, "DEFAULT_VIDEO_DIR", directory):
                catalog = advertising.AdCatalog(custom)
            self.assertFalse(catalog.items)


if __name__ == "__main__":
    unittest.main()
