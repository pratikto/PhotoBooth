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
from kivy.uix.image import Image as KivyImage
from PIL import Image as PILImage
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
        if (app._sandbox_view or {}).get('ticket_required'):
            app._sandbox_ticket_saved();self.settle(app)
    def reserve(self,app,fixture):
        self.pending(app);fixture.paid();app._sandbox_retry();self.settle(app)
        self.assertEqual(app._sandbox_view['phase'],'RESERVED')

    def test_recovery_ticket_gate_precedes_payment_and_never_copies_secret_to_clipboard(self):
        with self.booth() as (app,f):
            self.quote(app);app._sandbox_begin();self.settle(app)
            self.assertTrue(app._sandbox_view['ticket_required'])
            ticket=f.flow.customer_ticket()
            self.assertTrue(any('SIMPAN TIKET PEMULIHAN' in getattr(w,'text','') for w in app.stage.walk()))
            self.assertFalse(any(getattr(w,'text','')=='SALIN LINK QRIS' for w in app.stage.walk()))
            with patch('photobooth.kiosk_v2.sandbox_views.Clipboard.copy') as copy:
                app._sandbox_copy_link();copy.assert_not_called()
            self.assertNotIn(ticket.split(':')[-1],f.flow.path.read_text())
            app._sandbox_ticket_saved();self.settle(app)
            self.assertIsNone(f.flow.customer_ticket())
            self.assertTrue(any(getattr(w,'text','')=='SALIN LINK QRIS' for w in app.stage.walk()))

    def test_privacy_locked_order_never_displays_payment_or_old_media(self):
        with self.booth() as (app,f):
            self.pending(app);f.flow.lock_customer()
            app._sandbox_view=f.service.view();app._show()
            self.assertTrue(app._sandbox_view['customer_claim_required'])
            self.assertFalse(any(getattr(w,'text','')=='SALIN LINK QRIS' for w in app.stage.walk()))
            self.assertFalse(any(getattr(w,'text','')=='LANJUT KE PERSETUJUAN FOTO' for w in app.stage.walk()))

    def test_copy_current_image_action_without_changing_order_and_retire_old_button(self):
        with self.booth() as (app,f):
            self.pending(app)
            before = f.flow.snapshot()
            url = before['order']['qr_url']
            button = next(w for w in app.stage.walk()
                          if isinstance(w,ArcadeButton) and w.text == 'SALIN LINK QRIS')
            with patch('photobooth.kiosk_v2.sandbox_views.Clipboard.copy') as copy:
                button.dispatch('on_release')
                copy.assert_called_once_with(url)
                self.assertTrue(any('Link QRIS tersalin' in getattr(w,'text','') for w in app.stage.walk()))
                self.assertEqual(f.flow.snapshot(),before)
                self.assertEqual(f.provider.charges,1)
                button.dispatch('on_release')  # Old page callback cannot write again.
                copy.assert_called_once()
                f.paid();app._sandbox_retry();self.settle(app)
                self.assertFalse(any(getattr(w,'text','') == 'SALIN LINK QRIS' for w in app.stage.walk()))
                app._sandbox_copy_link();button.dispatch('on_release')
                copy.assert_called_once()

    def test_copy_handles_clipboard_error_and_works_without_qr_pixels(self):
        with self.booth() as (app,f):
            f.service.image_loader = Mock(side_effect=OSError('image offline'))
            self.pending(app)
            self.assertIsNone(app._sandbox_view['qr_rgb'])
            with patch('photobooth.kiosk_v2.sandbox_views.Clipboard.copy',side_effect=RuntimeError('clipboard unavailable')):
                app._sandbox_copy_link()
            self.assertTrue(any('Gagal menyalin' in getattr(w,'text','') for w in app.stage.walk()))
            self.assertEqual(f.provider.charges,1)
            self.assertEqual(f.flow.snapshot()['phase'],'WAITING')
            with patch('photobooth.kiosk_v2.sandbox_views.Clipboard.copy') as copy:
                app._sandbox_copy_link()
                copy.assert_called_once_with(f.flow.snapshot()['order']['qr_url'])

    def test_copy_guard_blocks_busy_suspended_and_unverified_views(self):
        with self.booth() as (app,f):
            self.pending(app)
            view = app._sandbox_view
            with patch('photobooth.kiosk_v2.sandbox_views.Clipboard.copy') as copy:
                with patch.object(f.jobs,'busy',True):
                    app._sandbox_copy_link()
                app._suspended=True;app._sandbox_copy_link();app._suspended=False
                app._sandbox_view=dict(view,order=dict(view['order'],verification_pending=True))
                app._sandbox_copy_link()
                app._sandbox_view=dict(view,order=dict(view['order'],qr_url='https://example.com/qr'))
                app._sandbox_copy_link()
                copy.assert_not_called()
            app._sandbox_view=view

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

    def test_center_logo_payload_and_cached_order_survive_resizing_and_status_checks(self):
        import cv2
        from photobooth.kiosk_v2.qr_branding import with_meong_logo
        from photobooth.qr_code import create_qr_image
        from tools.ci_qr_pixels import decode_rendered_qr_pixels
        payload = 'MEONG TEST ONLY - NOT PAYABLE | ' + '0123456789' * 16
        previous_size = Window.size
        try:
            with self.booth() as (app, fixture):
                fixture.service.image_loader = Mock(side_effect=lambda order: with_meong_logo(
                    create_qr_image(payload, with_logo=False)))
                self.pending(app)
                order_id = app._sandbox_view['order']['order_id']
                checkout_key = fixture.flow.snapshot()['checkout_key']
                for size in ((800, 1280), (452, 900), (640, 880)):
                    Window.size = size
                    app._sandbox_retry()
                    self.settle(app)
                    for _ in range(3):
                        EventLoop.idle()
                    native_size, pixels = app._sandbox_view['qr_rgb']
                    widgets = [w for w in app.stage.walk() if isinstance(w, KivyImage)
                               and w.texture is not None and tuple(w.texture.size) == native_size]
                    self.assertEqual(len(widgets), 1)
                    widget = widgets[0]
                    self.assertEqual((widget.texture.min_filter, widget.texture.mag_filter),
                                     ('nearest', 'nearest'))
                    image = PILImage.frombytes('RGB', native_size, pixels)
                    width, height = map(round, widget.norm_image_size)
                    displayed = image.resize((width, height), PILImage.Resampling.NEAREST)
                    pixels_bgr = cv2.cvtColor(np.asarray(displayed), cv2.COLOR_RGB2BGR)
                    self.assertEqual(decode_rendered_qr_pixels(pixels_bgr), payload,
                                     f'Window {size}, displayed QR {(width, height)}, source {native_size}')
                    array = np.asarray(displayed)
                    self.assertTrue(np.any(array[:, :, 0] != array[:, :, 1]))
                    self.assertEqual(app._sandbox_view['order']['order_id'], order_id)
                    self.assertEqual(fixture.flow.snapshot()['checkout_key'], checkout_key)
                    self.assertEqual(fixture.provider.charges, 1)
                fixture.service.image_loader.assert_called_once()
        finally:
            Window.size = previous_size

    def test_automatic_pending_polls_keep_verified_image_until_provider_expiry(self):
        with self.booth() as (app, fixture):
            original_create = fixture.provider.create_qris
            image_url = 'https://api.sandbox.midtrans.com/v4/qris/fixture-image/qr-code'
            def create(order_id, amount):
                data = original_create(order_id, amount)
                # Include the action through initial display, then omit it on polls.
                actions = [{'name': 'generate-qr-code', 'method': 'GET', 'url': image_url}]
                fixture.provider.rows[order_id]['actions'] = actions
                return dict(data, actions=actions)
            fixture.provider.create_qris = create
            original_loader = fixture.service.image_loader
            def load(order):
                if order['qr_url'] != image_url:
                    raise RuntimeError('Fixture image exists only at the supplied action URL')
                return original_loader(order)
            fixture.service.image_loader = Mock(side_effect=load)
            self.pending(app)
            before = app._sandbox_view
            self.assertIsNotNone(before['qr_rgb'])
            order_id = before['order']['order_id']
            checkout_key = fixture.flow.snapshot()['checkout_key']
            del fixture.provider.rows[order_id]['actions']
            for _ in range(5):
                reads = fixture.provider.reads
                fixture.store.db.execute('UPDATE checkouts SET check_after=0')
                app._sandbox_refresh_at = 0
                app._poll_sandbox()  # Actual automatic-poll path, no status-button tap.
                self.settle(app)
                view = app._sandbox_view
                self.assertGreater(fixture.provider.reads, reads)
                self.assertEqual(view['phase'], 'WAITING')
                self.assertEqual(view['order']['state'], 'PENDING')
                self.assertEqual(view['order']['order_id'], order_id)
                self.assertEqual(fixture.flow.snapshot()['checkout_key'], checkout_key)
                self.assertIsNotNone(view['qr_rgb'])
                self.assertEqual(view['qr_rgb'], before['qr_rgb'])
                images = [w for w in app.stage.walk() if isinstance(w, KivyImage)
                          and w.texture is not None and tuple(w.texture.size) == before['qr_rgb'][0]]
                self.assertEqual(len(images), 1)
            fixture.service.image_loader.assert_called_once()
            self.assertEqual(fixture.provider.charges, 1)
            fixture.provider.rows[order_id].update(transaction_status='expire', status_code='407')
            fixture.store.db.execute('UPDATE checkouts SET check_after=0')
            app._sandbox_refresh_at = 0
            app._poll_sandbox()
            self.settle(app)
            self.assertEqual(app._sandbox_view['phase'], 'CANCELLED')
            self.assertIsNone(app._sandbox_view['qr_rgb'])
            self.assertEqual(fixture.provider.charges, 1)

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
