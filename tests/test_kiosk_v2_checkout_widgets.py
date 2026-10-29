"""Real widget checks for opt-in MOCK mode, never payment-provider acceptance."""

from contextlib import contextmanager, closing
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import time
import unittest
from unittest.mock import patch

try:
    import kivy
except ImportError:
    HAS_KIVY = False
else:
    HAS_KIVY = True
    from kivy.base import EventLoop
    from kivy.clock import Clock
    from kivy.core.window import Window
    from photobooth.kiosk_v2.app import PortraitKioskV2App
    from photobooth.kiosk_v2.demo_game import GameJobs
    from photobooth.kiosk_v2.mock_checkout import MockCheckoutStore, MockCheckoutPresentation, MockCheckoutError
    from photobooth.kiosk_v2.flow import TEMPLATES, MOCK_CHECKOUT, PHOTO_CONFIRM
    from photobooth.kiosk_v2.theme import ArcadeButton


@unittest.skipUnless(HAS_KIVY, 'Native widget environment required')
class CheckoutWidgetTests(unittest.TestCase):
    @contextmanager
    def configured_print_booth(self):
        # Exercise the actual application factory, not injected checkout_jobs.
        # All device probes are separately replaced by each test's barrier.
        with (TemporaryDirectory() as temp,
              patch.dict(os.environ, {'PHOTOBOOTH_V2_CHECKOUT_MOCK':'1',
                  'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0', 'PHOTOBOOTH_V2_PRINT':'1',
                  'PHOTOBOOTH_V2_DRIVE':'0', 'PHOTOBOOTH_AUDIO':'0',
                  'PHOTOBOOTH_AD_VIDEO':'0', 'PHOTOBOOTH_CAMERA':'0',
                  'PHOTOBOOTH_FACE_TRIGGER':'0', 'PHOTOBOOTH_PALM_TRIGGER':'0'}),
              patch('photobooth.kiosk_v2.checkout_views.PROJECT_ROOT', Path(temp))):
            store = MockCheckoutStore(Path(temp)/'data'/'kiosk-v2-p4')
            app = PortraitKioskV2App()
            Window.add_widget(app.build())
            try: yield app, store
            finally:
                app.on_stop(); app._mock_jobs.wait_closed(); Window.remove_widget(app.stage)
                if app._photo_jobs: app._photo_jobs.wait_closed()

    def mock_orders(self, store):
        with closing(store._connect()) as db:
            return [dict(row) for row in db.execute('SELECT * FROM mock_orders ORDER BY rowid')]

    @contextmanager
    def booth(self, root=None, factory=None, enabled=True):
        with TemporaryDirectory() as temp, patch.dict(os.environ, {
                'PHOTOBOOTH_V2_CHECKOUT_MOCK':'1' if enabled else '0',
                'PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_AD_VIDEO':'0','PHOTOBOOTH_CAMERA':'0',
                'PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0'}):
            store=MockCheckoutStore(root or temp)
            jobs=GameJobs(factory or (lambda:MockCheckoutPresentation(store)),
                          actions={'open_checkout','status','transition','admit'})
            app=PortraitKioskV2App(checkout_jobs=jobs)
            Window.add_widget(app.build())
            try:yield app,store
            finally:
                app.on_stop();jobs.wait_closed();Window.remove_widget(app.stage)
                if app._photo_jobs:app._photo_jobs.wait_closed()

    def settle(self, app):
        deadline=time.monotonic()+3
        while app._mock_jobs.busy and time.monotonic()<deadline:
            app._poll_checkout();EventLoop.idle()
        # A native frame can use the last part of the wait budget while the
        # worker finishes. Drain that already-completed result before judging
        # busy; do not extend the deadline or accept an unfinished job.
        app._poll_checkout()
        self.assertFalse(app._mock_jobs.busy)

    def gallery(self, app):
        app._choose_photo();app._complete_tutorial();app._change_copies(1)

    def open(self, app):
        self.gallery(app);app._open_mock_checkout();app._open_mock_checkout();self.settle(app)
        self.assertEqual(app.navigation.page,MOCK_CHECKOUT)

    def buttons(self, app):
        return [w for w in app.stage.walk() if isinstance(w,ArcadeButton)]

    def test_default_mode_keeps_mock_off_and_payment_disabled(self):
        with self.booth(enabled=False) as (app,_):
            self.gallery(app);app._open_mock_checkout()
            self.assertEqual(app.navigation.page,TEMPLATES)
            self.assertFalse(any('UJI CHECKOUT MOCK' in w.text for w in self.buttons(app)))
            self.assertTrue(next(w for w in self.buttons(app) if 'PEMBAYARAN' in w.text).disabled)

    def test_ux07_configured_printer_probe_keeps_clock_live_and_retry_creates_one_mock_at_both_sizes(self):
        from photobooth.device_health import HealthCheck, READY, UNKNOWN
        original = Window.size
        try:
            for size in ((800,1280),(452,900)):
                with self.subTest(size=size):
                    entered, release = threading.Event(), threading.Event()
                    probe_threads = []
                    def probe(_config):
                        probe_threads.append(threading.get_ident())
                        if len(probe_threads) == 1:
                            entered.set()
                            if not release.wait(8): raise TimeoutError('synthetic barrier timeout')
                            return HealthCheck('printer', UNKNOWN, 'PRIVATE driver/address/path')
                        return HealthCheck('printer', READY, 'route only; paper unknown')
                    try:
                        with (patch('photobooth.device_health.check_printer', side_effect=probe) as observed,
                              patch('photobooth.printer.ThermalPrinter') as printer,
                              self.configured_print_booth() as (app,store)):
                            Window.size = size
                            self.gallery(app); app._open_mock_checkout()
                            self.assertTrue(entered.wait(2))
                            ticks = []
                            event = Clock.schedule_interval(lambda dt: ticks.append(dt), 0)
                            try:
                                deadline = time.monotonic()+2
                                while len(ticks)<3 and time.monotonic()<deadline: EventLoop.idle()
                                self.assertGreaterEqual(len(ticks), 3)
                                app._open_mock_checkout(); app._mock_status(); app._mock_without_promo()
                                self.assertTrue(app._mock_jobs.busy)
                                self.assertEqual(self.mock_orders(store), [])
                                self.assertIsNone(app._mock_view)
                            finally:
                                event.cancel(); release.set()
                            self.settle(app)
                            self.assertEqual(app.navigation.page, MOCK_CHECKOUT)
                            self.assertIsNone(app._mock_view)
                            self.assertIsNone(app._photo_jobs)
                            self.assertIn('Koneksi printer belum terkonfirmasi', app._mock_message.text)
                            texts = ' '.join(getattr(w,'text','') for w in app.stage.walk())
                            self.assertNotIn('PRIVATE', texts)
                            self.assertEqual(self.mock_orders(store), [])
                            app._mock_status(); self.settle(app)
                            view = app._mock_view
                            self.assertEqual(view['state'], 'PENDING')
                            self.assertTrue(view['qr_payload'].startswith('MEONG MOCK ONLY - NOT QRIS - '))
                            self.assertIsNotNone(app._mock_qr.texture)
                            self.assertIsNone(view['admission_id'])
                            self.assertIsNone(app._photo_jobs)
                            self.assertEqual(len(self.mock_orders(store)), 1)
                            app._mock_status(); self.settle(app)
                            self.assertEqual(app._mock_view['order_id'], view['order_id'])
                            self.assertEqual(observed.call_count, 2)
                            self.assertTrue(all(t != threading.get_ident() for t in probe_threads))
                            printer.assert_not_called()
                    finally: release.set()
        finally: Window.size = original

    def test_ux07_retired_printer_probe_result_stays_hidden_then_recovers_original_mock_at_both_sizes(self):
        from photobooth.device_health import HealthCheck, READY
        original = Window.size
        try:
            for size in ((800,1280),(452,900)):
                with self.subTest(size=size):
                    entered, release = threading.Event(), threading.Event()
                    def probe(_config):
                        entered.set()
                        if not release.wait(8): raise TimeoutError('synthetic barrier timeout')
                        return HealthCheck('printer', READY, 'route only; paper unknown')
                    try:
                        with (patch('photobooth.device_health.check_printer', side_effect=probe) as observed,
                              self.configured_print_booth() as (app,store)):
                            Window.size = size
                            self.gallery(app); app._open_mock_checkout()
                            self.assertTrue(entered.wait(2))
                            revision = app._view_revision
                            app._show()  # Real page retirement; old worker result must be fenced.
                            self.assertGreater(app._view_revision, revision)
                            release.set(); app._mock_jobs.wait_closed(); app._poll_checkout()
                            self.assertFalse(app._mock_jobs.busy)
                            self.assertIsNone(app._mock_view)
                            self.assertFalse(any('MEONG MOCK ONLY' in getattr(w,'text','') for w in app.stage.walk()))
                            rows = self.mock_orders(store)
                            self.assertEqual(len(rows), 1)
                            self.assertIsNone(rows[0]['admission_id'])
                            self.assertIsNone(app._photo_jobs)
                            app._mock_status(); self.settle(app)  # Explicit recovery, no new probe/order.
                            self.assertEqual(app._mock_view['order_id'], rows[0]['order_id'])
                            self.assertEqual(observed.call_count, 1)
                            self.assertEqual(len(self.mock_orders(store)), 1)
                    finally: release.set()
        finally: Window.size = original

    def test_pending_unknown_cancel_resolution_and_no_browse_timeout(self):
        with self.booth() as (app,store):
            self.open(app);oid=app._mock_view['order_id']
            self.assertEqual(app._mock_view['total'],10000)
            self.assertTrue(app._mock_view['qr_payload'].startswith('MEONG MOCK ONLY - NOT QRIS'))
            self.assertIsNone(app._photo_jobs)
            self.assertFalse(app.navigation.browse_timeout())
            app._last_activity-=1000;app._tick(1000)
            self.assertEqual(app.navigation.page,MOCK_CHECKOUT)
            app._mock_transition('unknown');self.settle(app)
            app._mock_leave();self.assertEqual(app.navigation.page,MOCK_CHECKOUT)
            app._mock_transition('cancel');self.settle(app)
            self.assertEqual(store.status(oid)['state'],'UNKNOWN')
            self.assertIsNone(app._photo_jobs)
            app._mock_transition('reject');self.settle(app)
            app._mock_leave();self.assertEqual(app.navigation.page,TEMPLATES)

    def test_one_admission_handoff_freezes_cart_and_retires_old_button(self):
        with self.booth() as (app,store):
            self.open(app);oid=app._mock_view['order_id'];original=dict(app._mock_view['quantities'])
            app._mock_transition('confirm');self.settle(app)
            self.assertIsNone(app._photo_jobs)
            button=next(w for w in self.buttons(app) if w.text=='LANJUT KE PERSETUJUAN UJI FOTO')
            app.quantities={t.template_id:9 for t in app.templates}
            with patch.object(app,'_enter_photo_test',side_effect=lambda:app.navigation.confirm_photo_test()) as enter:
                button.dispatch('on_release');button.dispatch('on_release');self.settle(app)
                self.assertEqual(enter.call_count,1)
                button.dispatch('on_release');self.assertEqual(enter.call_count,1)
            self.assertEqual(app.navigation.page,PHOTO_CONFIRM)
            self.assertEqual({k:v for k,v in app.quantities.items() if v},original)
            self.assertEqual(store.status(oid)['state'],'ADMITTED')
            with self.assertRaises(MockCheckoutError):store.admit(oid)

    def test_pending_restart_recovers_order_and_conflicting_cart_is_not_charged(self):
        with TemporaryDirectory() as root:
            with self.booth(root) as (app,_):
                self.open(app);oid=app._mock_view['order_id'];cart=app._mock_view['quantities']
            with self.booth(root) as (app,_):
                self.gallery(app);app._change_copies(2);app._open_mock_checkout();self.settle(app)
                self.assertEqual(app._mock_view['order_id'],oid)
                self.assertEqual(app._mock_view['quantities'],cart)
                self.assertIn('dipulihkan',app._mock_message.text)
                self.assertIsNone(app._photo_jobs)

    def test_real_catalog_win_is_7500_and_loss_stays_10000(self):
        for result in ('won','lost'):
            with self.subTest(result=result),self.booth() as (app,store):
                attempt=store.claim('DEMO-QUOTE')['attempt_id']
                store.finish(attempt,result,10 if result=='won' else 0)
                app._game_result=store.get(attempt)
                self.open(app)
                self.assertEqual(app._mock_view['total'],7500 if result=='won' else 10000)
                self.assertFalse(hasattr(app.navigation,'paid'))

    def test_slow_storage_suspend_resize_and_error_do_not_admit(self):
        entered,release=threading.Event(),threading.Event()
        def unavailable():
            entered.set();release.wait(2);raise OSError('readonly')
        original=Window.size
        try:
            with self.booth(factory=unavailable) as (app,_):
                self.gallery(app);app._open_mock_checkout();self.assertTrue(entered.wait(1))
                for size in ((800,1280),(452,900),(360,640)):
                    Window.size=size;EventLoop.idle()
                app.on_pause();release.set();app._mock_jobs.wait_closed()
                app._poll_checkout();self.assertTrue(app._mock_jobs.busy)
                app.on_resume();self.settle(app)
                self.assertIsNone(app._mock_view);self.assertIsNone(app._photo_jobs)
                self.assertIn('Belum berhasil',app._mock_message.text)
        finally:
            release.set();Window.size=original

    def test_consumed_admission_status_never_replays_photo_handoff(self):
        with self.booth() as (app,store):
            self.open(app);oid=app._mock_view['order_id']
            store.transition(oid,'confirm');store.admit(oid)
            with patch.object(app,'_enter_photo_test') as enter:
                app._mock_status();self.settle(app)
                self.assertEqual(app._mock_view['state'],'ADMITTED')
                self.assertFalse(any(w.text=='LANJUT KE PERSETUJUAN UJI FOTO' for w in self.buttons(app)))
                enter.assert_not_called()
                app._mock_leave();self.assertEqual(app.navigation.page,TEMPLATES)

    def test_expired_qr_is_not_admissible_and_returns_to_gallery(self):
        with self.booth() as (app,store):
            self.open(app);store.clock=lambda:time.time()+1000
            app._mock_status();self.settle(app)
            self.assertEqual(app._mock_view['state'],'EXPIRED')
            self.assertIsNone(app._photo_jobs)
            app._mock_leave();self.assertEqual(app.navigation.page,TEMPLATES)

    def test_nonpayable_qr_decodes_to_mock_text(self):
        import cv2
        import numpy as np
        from uuid import UUID
        from tools.ci_qr_pixels import decode_rendered_qr_pixels
        # Include the exact random pattern that failed native-scale OpenCV
        # decoding. The existing reader retries only unchanged pixel scales.
        for order_id in ('33517492cac0481daa1d7cb59af77d4b','0123456789abcdef0123456789abcdef'):
            with self.subTest(order_id=order_id),self.booth() as (app,_):
                with patch('photobooth.kiosk_v2.mock_checkout.uuid.uuid4',return_value=UUID(order_id)):
                    self.open(app)
                (width,height),pixels=app._mock_view['qr_rgb']
                image=np.frombuffer(pixels,dtype=np.uint8).reshape(height,width,3)
                decoded=decode_rendered_qr_pixels(cv2.cvtColor(image,cv2.COLOR_RGB2BGR))
                self.assertEqual(decoded,app._mock_view['qr_payload'])
                self.assertEqual(decoded,'MEONG MOCK ONLY - NOT QRIS - '+order_id)

    def test_pending_qr_quote_and_controls_stay_inside_at_all_portrait_sizes(self):
        original=Window.size
        try:
            with self.booth() as (app,_):
                self.open(app)
                for size in ((800,1280),(452,900),(360,640)):
                    Window.size=size
                    for _ in range(5):EventLoop.idle()
                    card=app._mock_card
                    for child in card.children:
                        self.assertGreaterEqual(child.y,card.y-1)
                        self.assertLessEqual(child.top,card.top+1)
                    self.assertGreaterEqual(app._mock_qr.height,120)
                    self.assertEqual(app._mock_view['state'],'PENDING')
        finally:Window.size=original

    def test_twenty_mock_visits_cancel_or_admit_once_without_stuck_jobs(self):
        with self.booth() as (app,store):
            for cycle in range(20):
                with self.subTest(cycle=cycle):
                    self.open(app)
                    oid=app._mock_view['order_id']
                    if cycle%2:
                        app._mock_transition('confirm');self.settle(app)
                        with patch.object(app,'_enter_photo_test',side_effect=lambda:app.navigation.confirm_photo_test()) as enter:
                            app._mock_admit();app._mock_admit();self.settle(app)
                            self.assertEqual(enter.call_count,1)
                        app.navigation.page=TEMPLATES
                        self.assertEqual(store.status(oid)['state'],'ADMITTED')
                    else:
                        app._mock_transition('cancel');self.settle(app);app._mock_leave()
                    app._return_ad()
                    self.assertFalse(app._mock_jobs.busy)
                    self.assertIsNone(app._mock_view)

    def test_mock_admission_enters_existing_consent_three_photos_and_local_result(self):
        import numpy as np
        from photobooth.kiosk_v2.photos import PhotoTest
        from photobooth.kiosk_v2.flow import CAPTURE, REVIEW, RESULT, ADVERT
        with TemporaryDirectory() as root, patch('photobooth.kiosk_v2.photos.configured_test',
                                                 return_value=PhotoTest(root)),self.booth() as (app,store):
            def settle_photo():
                deadline=time.monotonic()+3
                while app._photo_jobs.busy and time.monotonic()<deadline:
                    app._poll_photos();time.sleep(.005)
                self.assertFalse(app._photo_jobs.busy)
            self.open(app);oid=app._mock_view['order_id']
            app._mock_transition('confirm');self.settle(app)
            app._mock_admit();self.settle(app);settle_photo()
            self.assertEqual(app.navigation.page,PHOTO_CONFIRM)
            self.assertEqual(store.status(oid)['state'],'ADMITTED')
            frame=np.zeros((120,160,3),dtype=np.uint8)
            with patch.object(app.camera_device,'read',return_value=frame):
                app._admit_photo_test();settle_photo()
                self.assertEqual(app.navigation.page,CAPTURE)
                for _ in range(3):app._photo_submit('capture',frame);settle_photo()
                self.assertEqual(app.navigation.page,REVIEW)
                app._photo_submit('compose');settle_photo()
                self.assertEqual(app.navigation.page,RESULT)
                app._photo_submit('next');settle_photo()
                self.assertEqual(app.navigation.page,ADVERT)
            self.assertEqual(store.status(oid)['state'],'ADMITTED')


if __name__=='__main__':unittest.main()
