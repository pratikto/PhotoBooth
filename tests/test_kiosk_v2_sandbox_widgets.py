"""Native GUI → real HTTP API/client → durable grant → real P3 synthetic photos."""
from contextlib import contextmanager
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import Mock, patch
import numpy as np
from kivy.base import EventLoop
from kivy.core.window import Window
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.flow import ADVERT, TEMPLATES, PHOTO_CONFIRM, SANDBOX_CHECKOUT, CAPTURE
from photobooth.kiosk_v2.photos import PhotoTest
from photobooth.kiosk_v2.theme import ArcadeButton
from tests.qris_v2_fixture import Fixture


class SandboxWidgetTests(unittest.TestCase):
    @contextmanager
    def booth(self):
        with TemporaryDirectory() as temp, patch.dict(os.environ,{
            'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'1','PHOTOBOOTH_V2_CHECKOUT_MOCK':'0',
            'MEONG_QRIS_MODE':'sandbox','MIDTRANS_SERVER_KEY':'','MIDTRANS_MERCHANT_ID':'',
            'PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_CAMERA':'0','PHOTOBOOTH_AD_VIDEO':'0',
            'PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0'}):
            fixture=Fixture(Path(temp))
            device=Mock();device.read.return_value=np.zeros((120,160,3),dtype=np.uint8)
            service=PhotoTest(Path(temp)/'photos')
            with patch('photobooth.kiosk_v2.photos.configured_test',return_value=service):
                app=PortraitKioskV2App(camera_device=device,sandbox_jobs=fixture.jobs)
                Window.add_widget(app.build())
                try:
                    self.settle(app)
                    yield app,fixture
                finally:
                    app.on_stop();fixture.jobs.wait_closed()
                    if app._photo_jobs:app._photo_jobs.wait_closed()
                    fixture.store.close();Window.remove_widget(app.stage)
    def settle(self,app):
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            app._poll_photos();app._poll_sandbox();EventLoop.idle()
            if not app._sandbox_jobs.busy and not (app._photo_jobs and app._photo_jobs.busy):return
            time.sleep(.005)
        self.fail('Worker did not settle')
    def quote(self,app):
        app._choose_photo();app._complete_tutorial();app._change_copies(1);app._open_sandbox()
    def pending(self,app):
        self.quote(app);app._sandbox_begin();self.settle(app)
    def reserve(self,app,fixture):
        self.pending(app);fixture.paid();app._sandbox_retry();self.settle(app)
        self.assertEqual(app._sandbox_view['phase'],'RESERVED')
    def test_unpaid_guard_and_explicit_quote_then_authoritative_cancel(self):
        with self.booth() as (app,f):
            self.assertEqual(app.navigation.page,ADVERT)
            self.quote(app);self.assertEqual(f.provider.charges,0)
            self.assertIn('TANPA PROMO',' '.join(w.text for w in app.stage.walk() if isinstance(w,ArcadeButton)))
            app._sandbox_begin();self.settle(app)
            self.assertEqual(app._sandbox_view['phase'],'WAITING')
            self.assertEqual(f.provider.charges,1)
            app._sandbox_photo_consent();app._enter_photo_test()
            self.assertEqual(app.navigation.page,SANDBOX_CHECKOUT)
            self.assertIsNone(app._photo_jobs)
            self.assertFalse(app.navigation.browse_timeout())
            app._sandbox_cancel();self.settle(app)
            self.assertEqual(app._sandbox_view['phase'],'CANCELLED')
            app._sandbox_leave();self.assertEqual(app.navigation.page,ADVERT)
    def test_real_photo_handoff_completion_and_duplicate_taps(self):
        with self.booth() as (app,f):
            self.reserve(app,f)
            app._sandbox_photo_consent();self.settle(app)
            self.assertEqual(app.navigation.page,PHOTO_CONFIRM)
            app._leave_photo_confirm();self.assertEqual(app.navigation.page,SANDBOX_CHECKOUT)
            app._sandbox_photo_consent();self.settle(app)
            app._admit_photo_test();app._admit_photo_test();self.settle(app)
            self.assertEqual(app.navigation.page,CAPTURE)
            self.assertTrue(app._sandbox_can_capture())
            self.assertEqual(f.flow.snapshot()['phase'],'STARTED')
            for _ in range(3):
                app._start_countdown();app._countdown_deadline=time.monotonic()-.1;app._countdown_tick(0);self.settle(app)
            app._photo_submit('compose');self.settle(app)
            app._photo_submit('next');self.settle(app)
            self.assertEqual(app.navigation.page,SANDBOX_CHECKOUT)
            self.assertEqual(f.flow.snapshot()['phase'],'COMPLETED')
            self.assertEqual(f.provider.charges,1)
            self.assertEqual(len(list((f.root/'photos'/'photos').glob('*/manifest.json'))),1)
            app._sandbox_leave();self.assertEqual(app.navigation.page,ADVERT)
    def test_resize_persists_reserved_order_and_abort_requires_recovery(self):
        with self.booth() as (app,f):
            self.reserve(app,f);before=f.flow.snapshot()['checkout_key'];size=Window.size
            try:
                for value in ((800,1280),(452,900),(360,640)):
                    Window.size=value
                    for _ in range(3):EventLoop.idle()
                    self.assertEqual(f.flow.snapshot()['checkout_key'],before)
            finally:Window.size=size
            app._sandbox_photo_consent();self.settle(app);app._admit_photo_test();self.settle(app)
            app._photo_submit('abort');self.settle(app)
            self.assertEqual(f.flow.snapshot()['phase'],'RECOVERY')
            app._sandbox_leave();self.assertEqual(app.navigation.page,SANDBOX_CHECKOUT)
            self.assertFalse(app._sandbox_can_capture())
    def test_lost_creation_reply_cannot_leave_or_create_second_charge(self):
        with self.booth() as (app,f):
            f.provider.lost_charge=True
            self.pending(app)
            self.assertEqual(app._sandbox_view['phase'],'UNCERTAIN')
            app._sandbox_leave();self.assertEqual(app.navigation.page,SANDBOX_CHECKOUT)
            f.provider.lost_charge=False
            app._sandbox_retry();self.settle(app)
            self.assertEqual(app._sandbox_view['phase'],'WAITING')
            self.assertEqual(f.provider.charges,1)

    def test_missing_started_ack_blocks_countdown_until_same_transaction_ack(self):
        with self.booth() as (app,f):
            self.reserve(app,f);app._sandbox_photo_consent();self.settle(app)
            with patch.object(f.backend,'service_transition',side_effect=TimeoutError('lost ACK')):
                app._admit_photo_test();self.settle(app)
            self.assertEqual(app.navigation.page,SANDBOX_CHECKOUT)
            self.assertFalse(app._sandbox_can_capture())
            app._start_countdown();self.assertIsNone(app._countdown_event)
            tx=app._photo_view['transaction_id']
            app._sandbox_retry();self.settle(app)
            self.assertEqual(app.navigation.page,CAPTURE)
            self.assertTrue(app._sandbox_can_capture())
            self.assertEqual(f.flow.snapshot()['transaction_id'],tx)
            self.assertEqual(f.provider.charges,1)

    def test_operator_health_in_recovery_never_changes_order_or_replays_service(self):
        from tests.test_kiosk_v2_operator_widgets import fixture_snapshot
        with self.booth() as (app,f):
            self.reserve(app,f);app._sandbox_photo_consent();self.settle(app)
            app._admit_photo_test();self.settle(app)
            app._photo_submit('abort');self.settle(app)
            before=f.flow.snapshot()
            with patch('photobooth.v1_health_controller.collect_health_snapshot',return_value=fixture_snapshot()):
                app._open_operator()
                deadline=time.monotonic()+3
                while app._operator_panel.snapshot is None and time.monotonic()<deadline:EventLoop.idle()
                self.assertIsNotNone(app._operator_panel.snapshot)
                self.assertEqual(f.flow.snapshot(),before)
                self.assertFalse(app._sandbox_can_capture())
                app._close_operator()
            self.assertEqual(f.flow.snapshot(),before)
            self.assertEqual(f.provider.charges,1)
