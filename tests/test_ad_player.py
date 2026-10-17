"""Real-widget lifecycle and accounting checks; no webcam or external media."""

import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from PIL import Image


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class AdvertisementPlayerTests(unittest.TestCase):
    def setUp(self):
        from kivy.core.window import Window
        from photobooth.advertising import AdCatalog
        from photobooth.ui_ads import AdvertisementPlayer
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        Image.new('RGB', (120, 80), 'blue').save(root / 'good.png')
        (root / 'broken.png').write_bytes(b'not a picture')
        self.path = root / 'playlist.json'
        self.path.write_text(json.dumps({'ads': [
            {'id': 'broken', 'file': 'broken.png', 'placements': ['idle', 'payment']},
            {'id': 'good', 'file': 'good.png', 'placements': ['idle', 'payment']},
        ]}))
        self.events = Mock()
        self.player = AdvertisementPlayer(AdCatalog(self.path), 'payment', self.events)
        Window.add_widget(self.player)
        self.addCleanup(Window.remove_widget, self.player)
        self.addCleanup(self.player.close)

    def settle(self, seconds=.1):
        from kivy.base import EventLoop
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            EventLoop.idle()

    def test_corrupt_media_is_skipped_and_still_playback_is_recorded_on_retirement(self):
        self.settle()
        self.assertEqual(self.player.ad_id, 'good')
        self.assertTrue(self.player._ready)
        self.player.close()
        self.assertTrue(self.player._closed)
        self.assertIsNone(self.player._tick_event)
        self.assertEqual(self.events.write.call_args.kwargs['ad_id'], 'good')
        self.assertGreater(self.events.write.call_args.kwargs['seconds'], 0)

    def test_coarse_decoder_updates_count_all_played_time_and_payment_remains_muted(self):
        self.settle()
        player = self.player
        player._seconds = player._last_position = 0
        player.video = SimpleNamespace(state='play', position=0, volume=0)
        try:
            # Provider updates every other UI tick: 2 seconds must count as 2.
            for index in range(20):
                player.video.position = (index + 1) // 2 * .2
                player._measure_video(.1)
            self.assertAlmostEqual(player._seconds, 2)
            player.set_volume(1)
            self.assertEqual(player.video.volume, 0)
            player.pause()
            player._measure_video(60)
            self.assertAlmostEqual(player._seconds, 2)
        finally:
            player.video = None

    def test_retiring_before_next_frame_prevents_an_invisible_decoder_load(self):
        from photobooth.ui_ads import GuardedVideo
        video = GuardedVideo(self.fail, source=str(self.path.with_suffix('.mp4')), state='play')
        video.retire()
        self.settle()
        self.assertIsNone(video._video)
        self.assertEqual(video.volume, 0)

    def test_empty_playlist_has_a_branded_fallback_and_no_fabricated_play_count(self):
        self.player.catalog.items = []
        self.settle()
        self.assertEqual(self.player.ad_id, 'meong-fallback')
        self.player.close()
        self.events.write.assert_not_called()
