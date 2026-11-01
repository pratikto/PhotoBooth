"""Native private-preview screens, synthetic camera only, no payment or output."""
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

import numpy as np
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.base import EventLoop

from photobooth.kiosk_v2.flow import CAPTURE, RESULT, REVIEW
from photobooth.kiosk_v2.post_preview_app import PrivatePreviewApp
from photobooth.kiosk_v2.post_preview_photos import PrivatePhotoService


class PrivateWidgetTests(unittest.TestCase):
    @contextmanager
    def booth(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'PHOTOBOOTH_V2_CHECKOUT_SANDBOX': '0', 'PHOTOBOOTH_V2_CHECKOUT_MOCK': '0',
                'PHOTOBOOTH_V2_PRINT': '0', 'PHOTOBOOTH_V2_DRIVE': '0',
                'PHOTOBOOTH_AUDIO': '0', 'PHOTOBOOTH_AD_VIDEO': '0',
                'PHOTOBOOTH_FACE_TRIGGER': '0', 'PHOTOBOOTH_PALM_TRIGGER': '0'}):
            root = Path(directory)
            service = PrivatePhotoService(root)
            camera = Mock()
            camera.read.return_value = np.zeros((32, 48, 3), dtype=np.uint8)
            camera.preview.return_value = None
            app = PrivatePreviewApp(root, private_service=service, camera_device=camera)
            app.build()
            app.root = app.stage
            Window.add_widget(app.stage)
            try:
                yield app, service, camera
            finally:
                app.on_stop()
                Window.remove_widget(app.stage)
                app._photo_jobs.wait_closed(10)
                service.wait_closed(10)

    def settle(self, app, *, allow_warning=False):
        deadline = time.monotonic()+10
        while app._photo_jobs.busy and time.monotonic()<deadline:
            app._poll_photos()
            Clock.tick()
            time.sleep(.005)
        self.assertFalse(app._photo_jobs.busy)
        if allow_warning:
            self.assertTrue(app._photo_error.startswith('Sesi tidak aktif.'))
        else:
            self.assertFalse(app._photo_error, app._photo_error)

    def start(self, app):
        app._choose_photo()
        app._complete_tutorial()
        app.quantities.update(template_a=2, template_b=1)
        app._enter_photo_test()
        self.settle(app)
        app._admit_photo_test()
        self.settle(app)
        self.assertEqual(CAPTURE, app.navigation.page)

    def shot(self, app):
        app._start_countdown()
        self.assertIsNotNone(app._countdown_event)
        self.assertGreater(app._countdown_deadline-time.monotonic(), 4)
        app._countdown_deadline = time.monotonic()-1
        app._countdown_tick(0)
        self.settle(app)

    def capture_screen(self, app, name, size):
        target = os.environ.get('MEONG_PRIVATE_PREVIEW_SCREENSHOTS')
        if not target:
            return
        folder = Path(target)
        folder.mkdir(parents=True, exist_ok=True)
        for _ in range(4): EventLoop.idle()
        self.assertEqual(tuple(app.stage.size), size)
        Window.screenshot(name=str(folder/(name+f'-{size[0]}x{size[1]}.png')))

    def test_native_capture_review_and_all_designs_preview_at_both_portrait_sizes(self):
        sizes = ((800, 1280), (452, 900))
        requested = os.environ.get('MEONG_PRIVATE_PREVIEW_SIZE')
        if requested:
            sizes = (tuple(int(v) for v in requested.split('x')),)
        for size in sizes:
            with self.subTest(size=size), self.booth() as (app, service, camera):
                Window.size = size
                self.start(app)
                self.capture_screen(app, 'private-capture', size)
                for _ in range(2):
                    for _ in range(3): self.shot(app)
                    self.assertEqual(REVIEW, app.navigation.page)
                    self.capture_screen(app, 'private-review', size)
                    app._photo_submit('compose')
                    self.settle(app)
                    self.assertEqual(RESULT, app.navigation.page)
                    app._photo_submit('next')
                    self.settle(app)
                self.assertEqual('final_preview', app._photo_view['phase'])
                self.capture_screen(app, 'private-all-designs', size)
                self.assertEqual(2, len(app._photo_view['designs']))
                self.assertEqual(6, len(list(service.root.rglob('*.jpg'))))
                labels = [getattr(w, 'text', '') for w in app.stage.walk()]
                self.assertIn('TOTAL Rp25.000', labels)
                self.assertIn('PEMBAYARAN BELUM TERHUBUNG', labels)
                self.assertFalse(app._photo_view['print_available'])
                app._photo_submit('edit')
                self.settle(app)
                app.quantities.update(template_a=3, template_b=0)
                app._enter_photo_test()
                self.settle(app)
                app._admit_photo_test()
                self.settle(app)
                self.assertEqual(REVIEW, app.navigation.page)
                self.assertEqual(3, app._photo_view['copies'])
                self.assertEqual(6, len(list(service.root.rglob('*.jpg'))))

    def test_disconnect_cancels_countdown_without_shutter_and_suspend_hides_pixels(self):
        with self.booth() as (app, service, camera):
            self.start(app)
            app._start_countdown()
            camera.read.return_value = None
            app._countdown_tick(0)
            self.assertIsNone(app._countdown_event)
            self.assertFalse(list(service.root.rglob('*.jpg')))
            camera.read.return_value = np.zeros((32, 48, 3), dtype=np.uint8)
            self.shot(app)
            old = dict(app._photo_view)
            app.on_pause()
            self.assertEqual({'phase': 'hold'}, app._photo_view)
            self.assertEqual({'phase': 'hold'}, service.snapshot())
            app.on_resume()
            self.assertIn('SESI DILINDUNGI', [getattr(w, 'text', '') for w in app.stage.walk()])
            self.assertFalse(app._photo_capture_allowed())
            self.assertEqual(1, len(list(service.root.rglob('*.jpg'))))

    def test_mixed_delivery_or_payment_profile_is_rejected_before_app_build(self):
        for flag in ('PHOTOBOOTH_V2_PRINT', 'PHOTOBOOTH_V2_DRIVE',
                     'PHOTOBOOTH_V2_CHECKOUT_SANDBOX', 'PHOTOBOOTH_V2_CHECKOUT_MOCK'):
            with self.subTest(flag=flag), patch.dict(os.environ, {flag: '1'}):
                with self.assertRaises(ValueError): PrivatePreviewApp('unused-private-test-root')

    def test_minimize_during_initial_draft_write_fences_its_late_reply(self):
        with self.booth() as (app, service, camera):
            app._choose_photo()
            app._complete_tutorial()
            app.quantities.update(template_a=1)
            app._enter_photo_test()
            self.settle(app)
            entered, release = threading.Event(), threading.Event()
            original = service.ledger.create
            def blocked(*args):
                entered.set()
                release.wait(3)
                return original(*args)
            with patch.object(service.ledger, 'create', side_effect=blocked):
                app._admit_photo_test()
                self.assertTrue(entered.wait(3))
                self.assertIsNone(service.lease)
                app.on_pause()
                self.assertEqual({'phase': 'hold'}, app._photo_view)
                release.set()
                app.on_resume()
                self.settle(app)
            self.assertEqual({'phase': 'hold'}, app._photo_view)
            self.assertEqual({'phase': 'hold'}, service.snapshot())
            self.assertEqual('APP_SUSPENDED', service.ledger.db.execute(
                'SELECT lifecycle FROM pp_drafts').fetchone()[0])

    def test_true_inactivity_warns_then_holds_but_active_countdown_is_not_abandoned(self):
        with self.booth() as (app, service, camera):
            self.start(app)
            app._last_activity = time.monotonic()-1000
            app._tick(0)
            self.settle(app, allow_warning=True)
            self.assertEqual('ACTIVE', service.ledger.db.execute(
                'SELECT lifecycle FROM pp_drafts').fetchone()[0])
            self.assertIn('Sesi tidak aktif.', app._photo_error)
            self.assertEqual(CAPTURE, app.navigation.page)
            app._start_countdown()
            app._tick(0)
            self.assertIsNone(app._private_warning_at)
            self.assertIsNotNone(app._countdown_event)
            self.assertLess(time.monotonic()-app._last_activity, 1)
            app._cancel_countdown()
            app._last_activity = time.monotonic()-1000
            app._private_warning_at = time.monotonic()-16
            app._tick(0)
            self.settle(app)
            self.assertEqual({'phase': 'hold'}, app._photo_view)
            self.assertEqual('INACTIVITY_EXPIRED', service.ledger.db.execute(
                'SELECT lifecycle FROM pp_drafts').fetchone()[0])
            self.assertFalse(list(service.root.rglob('*.jpg')))


if __name__ == '__main__': unittest.main()
