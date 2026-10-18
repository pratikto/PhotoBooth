"""Face invitation/controller boundaries without opening a camera or account."""

from contextlib import ExitStack
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class KioskControllerTests(unittest.TestCase):
    def setUp(self):
        from photobooth.app import PhotoBoothApp
        from photobooth.face_presence import FacePresenceTrigger
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        directory = self.stack.enter_context(tempfile.TemporaryDirectory())
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        camera = SimpleNamespace(open=lambda: True, read=lambda: frame, close=lambda: None)
        self.stack.enter_context(patch('photobooth.app.PROJECT_ROOT', Path(directory)))
        self.stack.enter_context(patch('photobooth.app.Camera', return_value=camera))
        self.stack.enter_context(patch('photobooth.app.AppsScriptDriveClient.from_configuration', return_value=None))
        self.stack.enter_context(patch('photobooth.app.GoogleDriveClient.from_environment', return_value=None))
        self.stack.enter_context(patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY': '1',
                                  'PHOTOBOOTH_PALM_TRIGGER': '0', 'PHOTOBOOTH_FACE_TRIGGER': '0'}))
        self.stack.enter_context(patch('photobooth.app.KivyHost.after',
                                      return_value=SimpleNamespace(cancel=lambda: None)))
        self.app = PhotoBoothApp()
        self.addCleanup(self.app.close)
        self.app._connect_camera()

        class Worker:
            result = None
            def start(self):
                pass
            def submit(self, *_args):
                pass
            def poll(self):
                result, self.result = self.result, None
                return result
            def pause(self):
                self.result = None
            def close(self):
                pass

        self.app.face_worker.close()
        self.app.face_worker = Worker()
        self.app.face_trigger = FacePresenceTrigger()
        self.now = 100
        self.stack.enter_context(patch('photobooth.app.time', SimpleNamespace(monotonic=lambda: self.now)))

    def sample(self, timestamp, *, context=None, age=0):
        from photobooth.palm_gesture import PalmObservation
        self.now = timestamp
        self.app.face_worker.result = PalmObservation(
            self.app.ui.screen_revision if context is None else context, timestamp - age, 1)
        self.app._update_face_presence(self.app.current_frame)

    def test_five_second_invitation_timeout_cooldown_and_manual_entry_share_the_real_flow(self):
        self.assertEqual(self.app.ui.current_screen, 'advert')
        for timestamp in np.arange(100, 105, .2):
            self.sample(float(timestamp))
            self.assertIsNone(self.app.ui._inline_offer)
        self.sample(105.01)
        self.assertEqual(self.app.ui._offer_kind, 'face')
        with patch('photobooth.ui_kiosk.time.monotonic', return_value=self.app.ui._offer_deadline + .01):
            self.app.ui._kiosk_tick()
        self.assertIsNone(self.app.ui._inline_offer)
        for timestamp in np.arange(106, 150, .2):
            self.sample(float(timestamp))
            self.assertIsNone(self.app.ui._inline_offer)
        self.app.ui.advert_start_button.dispatch('on_release')
        self.assertEqual(self.app.ui.current_screen, 'welcome')
        self.app.ui.home_start_button.dispatch('on_release')
        self.assertEqual(self.app.ui.current_screen, 'templates')
        self.assertIsNone(self.app.transaction)

    def test_stale_observations_and_background_presence_cannot_invite_or_reset_browsing_idle(self):
        for timestamp in np.arange(100, 107, .2):
            self.sample(float(timestamp), context=self.app.ui.screen_revision - 1)
            self.sample(float(timestamp), age=2)
        self.assertIsNone(self.app.ui._inline_offer)
        self.app.ui.pause_media()
        for timestamp in np.arange(108, 115, .2):
            self.sample(float(timestamp))
        self.assertIsNone(self.app.ui._inline_offer)
        self.app.ui.resume_media()
        self.app._open_template_selection()
        last_activity = time.monotonic() - 181
        self.app.ui._last_activity = last_activity
        self.sample(116)
        self.assertEqual(self.app.ui._last_activity, last_activity)
        self.app.ui._kiosk_tick()
        self.assertEqual(self.app.ui.current_screen, 'advert')
