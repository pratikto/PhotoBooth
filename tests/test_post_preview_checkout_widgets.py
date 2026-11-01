"""Native synthetic checkout through real API; never save proof screenshots."""
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

import numpy as np
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window

from photobooth.kiosk_v2.post_preview_checkout_app import PrivateCheckoutFixtureApp
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests import test_post_preview_widgets as widget_helpers


class PrivateCheckoutWidgetTests(unittest.TestCase):
    settle = widget_helpers.PrivateWidgetTests.settle
    start = widget_helpers.PrivateWidgetTests.start
    shot = widget_helpers.PrivateWidgetTests.shot

    @contextmanager
    def booth(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0', 'PHOTOBOOTH_V2_CHECKOUT_MOCK':'0',
                'PHOTOBOOTH_V2_PRINT':'0', 'PHOTOBOOTH_V2_DRIVE':'0', 'PHOTOBOOTH_AUDIO':'0',
                'PHOTOBOOTH_AD_VIDEO':'0', 'PHOTOBOOTH_FACE_TRIGGER':'0', 'PHOTOBOOTH_PALM_TRIGGER':'0'}):
            root = Path(directory)
            fixture = CheckoutFixture(root)
            camera = Mock()
            camera.read.return_value = np.zeros((32,48,3), dtype=np.uint8)
            camera.preview.return_value = None
            app = PrivateCheckoutFixtureApp(root, private_service=fixture.service, camera_device=camera)
            app.build(); app.root = app.stage
            fixture.bind_app(app)
            Window.add_widget(app.stage)
            try:
                yield app, fixture
            finally:
                app.on_stop()
                Window.remove_widget(app.stage)
                app._photo_jobs.wait_closed(10)
                fixture.close()

    def click(self, app, text):
        candidates = [w for w in app.stage.walk() if getattr(w,'text',None) == text]
        self.assertEqual(1, len(candidates))
        self.assertFalse(candidates[0].disabled)
        candidates[0].dispatch('on_release')

    def final(self, app):
        self.start(app)
        for _ in range(2):
            for _ in range(3): self.shot(app)
            app._photo_submit('compose'); self.settle(app)
            app._photo_submit('next'); self.settle(app)
        self.assertEqual('final_preview', app._photo_view['phase'])

    def proof(self, app):
        self.final(app)
        self.click(app, 'LANJUT CHECKOUT SIMULASI')
        self.settle(app)
        self.assertEqual('claim_proof', app._photo_view['phase'])
        deadline = time.monotonic()+4
        while app._photo_view['phase'] != 'checkout_ready' and time.monotonic() < deadline:
            app._poll_photos(); EventLoop.idle(); time.sleep(.01)
        self.settle(app)
        self.assertEqual('checkout_ready', app._photo_view['phase'])

    def test_full_native_proof_to_http_payment_and_paid_owed_at_both_portrait_sizes(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size), self.booth() as (app, fixture):
                Window.size = size
                self.proof(app)
                self.assertIsNotNone(fixture.service.ledger.db.execute('SELECT offered_at FROM pp_ccp_credentials').fetchone()[0])
                self.assertEqual(0, fixture.provider.charges)
                self.assertIsNotNone(app._claim_card.qr_image.texture)
                self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
                self.settle(app)
                self.assertEqual('payment_pending', app._photo_view['phase'])
                self.assertEqual(1, fixture.provider.charges)
                self.assertIsNone(app._claim_card)
                self.assertFalse(any('MEONG:CCP:' in getattr(w,'text','') for w in app.stage.walk()))
                view = app._photo_view['payment']
                fixture.provider.state(view['attempts'][0]['provider_order_id'], 'settlement')
                self.click(app, 'PERIKSA STATUS'); self.settle(app)
                self.assertEqual('paid_hold', app._photo_view['phase'])
                self.assertFalse(app._photo_view['fulfillment_authorized'])
                self.assertEqual(6, len(list(fixture.service.root.rglob('*.jpg'))))

    def test_minimize_during_provider_create_retires_proof_and_late_reply(self):
        with self.booth() as (app, fixture):
            Window.size = (452,900)
            self.proof(app)
            old_card = app._claim_card
            entered, release = threading.Event(), threading.Event()
            fixture.provider.create_entered, fixture.provider.create_release = entered, release
            self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
            self.assertTrue(entered.wait(3))
            app.on_pause()
            self.assertEqual({'phase':'hold'}, app._photo_view)
            self.assertIsNone(old_card.qr_image.texture)
            self.assertFalse(bool(old_card.code.text))
            release.set(); app.on_resume(); self.settle(app)
            self.assertEqual({'phase':'hold'}, fixture.service.snapshot())
            self.assertEqual(1, fixture.provider.charges)
            self.assertEqual(0, fixture.provider.cancels)
            self.assertEqual('APP_SUSPENDED', fixture.service.ledger.db.execute('SELECT lifecycle FROM pp_drafts').fetchone()[0])

    def test_background_payment_poll_does_not_reset_true_inactivity(self):
        with self.booth() as (app, fixture):
            Window.size = (452,900)
            self.proof(app)
            self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI'); self.settle(app)
            old_activity = time.monotonic()-200
            app._last_activity = old_activity
            # Simulate a currently blocked automatic status GET. Timer work
            # must not be interpreted as customer activity.
            app._photo_jobs.busy = True
            app._photo_jobs.current_action = 'check_payment'
            app._tick(0)
            self.assertEqual(old_activity, app._last_activity)
            self.assertIsNotNone(app._private_warning_at)
            app._photo_jobs.busy = False
            app._photo_jobs.current_action = None
            app._private_warning_at = time.monotonic()-16
            app._tick(0); self.settle(app)
            self.assertEqual({'phase':'hold'}, app._photo_view)
            self.assertEqual('INACTIVITY_EXPIRED', fixture.service.ledger.db.execute('SELECT lifecycle FROM pp_drafts').fetchone()[0])
            self.assertEqual(0, fixture.provider.cancels)
