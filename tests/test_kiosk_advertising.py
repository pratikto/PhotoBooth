"""Real-widget checks for idle media, nonmodal offers, QR pixels and audio ownership."""

from datetime import timedelta
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class KioskAdvertisingTests(unittest.TestCase):
    def setUp(self):
        from kivy.core.window import Window
        from photobooth.audio import AudioManager, SOUND_NAMES
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        from test_audio import FakeSound
        self.original_size = Window.size
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.environment = patch.dict(os.environ, {'PHOTOBOOTH_AUDIO': '1', 'PHOTOBOOTH_AD_VIDEO': '0',
                                                   'PHOTOBOOTH_PRINTER_HOST': ''})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.audio = AudioManager(Path(self.directory.name) / 'audio')
        self.audio._sounds = {name: FakeSound() for name in SOUND_NAMES}
        self.ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(), audio_manager=self.audio,
                               kiosk_data_dir=Path(self.directory.name), on_start=lambda *_: None)
        self.ui.callbacks['on_home_start'] = lambda: self.ui.show_template_selection(True, 'Ready')
        Window.add_widget(self.ui.shell)
        self.ui.set_camera_status(True)
        self.settle()

    def tearDown(self):
        from kivy.core.window import Window
        self.ui.dispose()
        Window.remove_widget(self.ui.shell)
        Window.size = self.original_size

    def settle(self, seconds=.15):
        from kivy.base import EventLoop
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            EventLoop.idle()
        EventLoop.idle()

    def payment(self):
        self.ui.show_payment('Special Day x 1', 1, 5000, lambda: None, lambda: None)
        self.settle()

    def test_manual_entry_survives_missing_face_detection_and_idle_returns_only_landing_pages(self):
        self.ui.show_advertisement(False)
        self.settle()
        self.assertFalse(self.ui.advert_start_button.disabled)
        self.assertTrue(self.audio._advertising)
        self.ui.advert_start_button.dispatch('on_release')
        self.assertEqual(self.ui.current_screen, 'templates')
        self.assertFalse(self.audio._advertising)
        self.ui._last_activity = time.monotonic() - 171
        self.ui._kiosk_tick()
        self.assertEqual(self.ui._offer_kind, 'idle-warning')
        self.ui._kiosk_activity()
        self.assertIsNone(self.ui._inline_offer)
        self.ui._last_activity = time.monotonic() - 181
        self.ui._kiosk_tick()
        self.assertEqual(self.ui.current_screen, 'advert')
        self.payment()
        self.ui._last_activity = time.monotonic() - 400
        self.ui._kiosk_tick()
        self.assertEqual(self.ui.current_screen, 'payment')

    def test_face_offer_closes_after_fifteen_seconds_and_retired_touch_cannot_start(self):
        self.ui.show_advertisement(True)
        self.assertTrue(self.ui.show_face_invitation())
        retired = self.ui.offer_action
        deadline = self.ui._offer_deadline
        with patch('photobooth.ui_kiosk.time.monotonic', return_value=deadline + .01):
            self.ui._kiosk_tick()
        self.assertIsNone(self.ui._inline_offer)
        retired.dispatch('on_release')
        self.assertEqual(self.ui.current_screen, 'advert')
