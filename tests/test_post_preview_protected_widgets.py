"""Original native controls with protected API/facade; external effects fake."""
from contextlib import contextmanager
import os
from pathlib import Path
import threading
import time
import unittest
from unittest.mock import Mock, patch

from kivy.base import EventLoop
from kivy.core.window import Window

from photobooth.kiosk_v2.flow import ADVERT, RESULT
from photobooth.kiosk_v2.post_preview_protected_app import ProtectedCheckoutApp
from photobooth.kiosk_v2.post_preview_checkout_app import PrivateCheckoutFixtureApp
from tests.post_preview_protected_fixture import ProtectedNativeHarness


class ProtectedNativeWidgetTests(unittest.TestCase):
    @contextmanager
    def booth(self, size=(452,900)):
        with patch.dict(os.environ,{'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0',
                'PHOTOBOOTH_V2_CHECKOUT_MOCK':'0','PHOTOBOOTH_V2_PRINT':'0',
                'PHOTOBOOTH_V2_DRIVE':'0','PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_AD_VIDEO':'0',
                'PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0'}):
            harness=unittest.TestCase()
            f=ProtectedNativeHarness(harness)
            Window.size=size
            camera=Mock();camera.read.return_value=f.frame;camera.preview.return_value=None
            app=ProtectedCheckoutApp(f.root,private_service=f.service,camera_device=camera)
            try:
                app.build();app.root=app.stage
                Window.add_widget(app.stage)
                # The harness already captured/approved the original draft;
                # resume its actual all-design view, not a fabricated phase.
                app._photo_view=f.preview_view
                app.navigation.page=RESULT
                app._show()
                self.idle(app)
                yield app,f
            finally:
                if f.receipt_release is not None:f.receipt_release.set()
                app._photo_jobs.wait_closed(12)
                app.on_stop()
                if app.stage.parent:Window.remove_widget(app.stage)
                app._photo_jobs.wait_closed(12);f.service.wait_closed(12)
                harness.doCleanups()

    def idle(self, app, predicate=None, timeout=10):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            EventLoop.idle();app._poll_photos()
            if predicate is not None and predicate():return
            if predicate is None and not app._photo_jobs.busy:return
            time.sleep(.005)
        self.fail('Native original worker/control did not reach expected state: '+
                  str(app._photo_view.get('phase'))+' '+app._photo_error)

    def click(self, app, title):
        buttons=[w for w in app.stage.walk() if getattr(w,'text',None)==title]
        self.assertEqual(1,len(buttons),title)
        self.assertFalse(buttons[0].disabled,title)
        buttons[0].dispatch('on_release')

    def paid(self, app, f):
        app._photo_submit('accept_frozen_checkout',f.group)
        self.idle(app,lambda:app._photo_view.get('phase')=='checkout_ready')
        self.click(app,'SUDAH SIMPAN BUKTI • LANJUT QRIS')
        self.idle(app,lambda:app._photo_view.get('phase')=='payment_pending')
        self.assertFalse(any('SIMULASI PAID' in str(getattr(w,'text','')) for w in app.stage.walk()))
        self.assertEqual(1,f.remote.charges)
        order=app._photo_view['payment']['attempts'][-1]['provider_order_id']
        f.remote.state(order,'settlement');f.clock[0]+=10
        self.click(app,'PERIKSA STATUS')
        self.idle(app,lambda:app._photo_view.get('phase')=='ticket_offer')

    def visible(self, app):
        self.idle(app,lambda:app._photo_view.get('phase')=='ticket_visible')
        self.assertTrue(app._ticket_window.active)
        self.assertIsNotNone(app._ticket_card)

    def test_native_original_ticket_then_automatic_2_1_delivery_and_protected_result_return(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size),self.booth(size) as (app,f):
                self.paid(app,f);self.visible(app)
                self.click(app,'LANJUT • SIMPAN TIKET')
                self.idle(app,lambda:bool((app._photo_view.get('delivery') or {}).get('print_all_submitted')))
                self.assertEqual('paid_delivery',app._photo_view['phase'])
                self.assertEqual(3,len(f.sends));self.assertEqual(1,len(f.binds))
                self.assertEqual(1,f.remote.charges)
                texts=[str(getattr(w,'text','')) for w in app.stage.walk()]
                self.assertTrue(any('file terverifikasi' in t for t in texts))
                self.assertTrue(any('Kertas fisik harus diperiksa' in t for t in texts))
                self.assertFalse(any('SIMULASI PAID' in t for t in texts))
                self.assertFalse(app._photo_view['delivery']['drive_verified'])
                target=os.environ.get('MEONG_PROTECTED_DELIVERY_SCREENSHOTS')
                if target:
                    folder=Path(target);folder.mkdir(parents=True,exist_ok=True)
                    for _ in range(4):EventLoop.idle()
                    Window.screenshot(name=str(folder/('paid-status-%sx%s.png'%size)))
                original=f.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0]
                app._paid_result_deadline=time.monotonic()-1
                app._poll_photos()
                self.assertEqual(ADVERT,app.navigation.page)
                self.assertEqual({'phase':'hold'},app._photo_view)
                app._choose_photo();app._choose_game()
                self.assertEqual(ADVERT,app.navigation.page)
                self.idle(app)
                self.assertEqual(0,f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
                self.assertEqual(original,f.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0])
                self.assertEqual('OWED',f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
                self.assertEqual(3,len(f.sends))

    def test_next_and_exact_30_seconds_wipe_ticket_while_receipt_http_is_blocked(self):
        for next_pressed in (True,False):
            with self.subTest(next_pressed=next_pressed),self.booth() as (app,f):
                f.receipt_entered=threading.Event();f.receipt_release=threading.Event()
                self.paid(app,f);self.visible(app)
                self.idle(app,lambda:f.receipt_entered.is_set())
                card=app._ticket_card
                if next_pressed:
                    self.click(app,'LANJUT • SIMPAN TIKET')
                else:
                    origin=app._ticket_window._started_at
                    app._ticket_window._clock=lambda:origin+29.999
                    app._poll_photos();self.assertIsNotNone(card.qr_image.texture)
                    app._ticket_window._clock=lambda:origin+30.
                    app._poll_photos()
                self.assertIsNone(card.qr_image.texture);self.assertEqual('',card.code.text)
                self.assertTrue(app._photo_jobs.busy)
                self.assertEqual([],f.binds)
                f.receipt_release.set()
                self.idle(app,lambda:app._photo_view.get('phase')=='paid_delivery')
                self.idle(app)
                self.assertEqual(3,len(f.sends))

    def test_slow_visible_ack_cannot_delay_genuine_native_timer_or_next(self):
        with self.booth() as (app,f):
            self.paid(app,f)
            entered=threading.Event();release=threading.Event()
            presentation=f.actor.binder.presentation
            original=presentation.visible
            def blocked(*args):
                entered.set();release.wait(10);return original(*args)
            try:
                with patch.object(presentation,'visible',side_effect=blocked):
                    self.idle(app,lambda:entered.is_set())
                    self.assertEqual('ticket_offer',app._photo_view['phase'])
                    self.assertTrue(app._ticket_window.active)
                    card=app._ticket_card
                    self.click(app,'LANJUT • SIMPAN TIKET')
                    self.assertIsNone(card.qr_image.texture)
                    self.assertTrue(app._photo_jobs.busy)
                    release.set()
                    self.idle(app,lambda:app._photo_view.get('phase')=='paid_delivery')
                    self.idle(app)
                self.assertEqual(3,len(f.sends))
            finally:release.set()

    def test_uncertain_first_photo_prevents_every_later_native_automatic_batch(self):
        with self.booth() as (app,f):
            self.paid(app,f);self.visible(app)
            self.idle(app) # original receipt has safely finished
            f.uncertain=True
            self.click(app,'LANJUT • SIMPAN TIKET')
            self.idle(app,lambda:bool((app._photo_view.get('delivery') or {}).get('needs_operator_review')))
            for _ in range(10):EventLoop.idle();app._poll_photos()
            self.assertEqual(2,len(f.sends))
            self.assertEqual('PREPARED',app._photo_view['delivery']['print_states']['template_b'])
            self.assertEqual('OWED',app._photo_view['delivery']['service_status'])

    def test_result_timeout_wipes_during_blocked_original_strip_and_late_reply_stays_private(self):
        with self.booth() as (app,f):
            self.paid(app,f);self.visible(app);self.idle(app)
            f.receipt_entered=threading.Event();f.receipt_release=threading.Event()
            self.click(app,'LANJUT • SIMPAN TIKET')
            self.idle(app,lambda:f.receipt_entered.is_set())
            self.assertEqual('paid_delivery',app._photo_view['phase'])
            self.assertTrue(app._photo_jobs.busy)
            app._paid_result_deadline=time.monotonic()-1
            app._poll_photos()
            self.assertEqual(ADVERT,app.navigation.page)
            self.assertEqual({'phase':'hold'},app._photo_view)
            self.assertIsNone(f.service._delivery_state)
            f.receipt_release.set();self.idle(app)
            self.assertEqual(ADVERT,app.navigation.page)
            self.assertEqual({'phase':'hold'},app._photo_view)
            self.assertEqual(2,len(f.sends))
            self.assertEqual('PREPARED',f.ledger.db.execute(
                "SELECT state FROM pp_paid_strip_jobs WHERE template_id='template_b'").fetchone()[0])
            self.assertEqual(0,f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_original_fixture_guard_and_protected_profile_reject_cross_authority(self):
        with self.booth() as (app,f):
            with self.assertRaises(TypeError):
                PrivateCheckoutFixtureApp(f.root,private_service=f.service)
            with self.assertRaises(TypeError):app.attach_synthetic_pilot_admission(object())
            with self.assertRaises(TypeError):
                ProtectedCheckoutApp(f.root,private_service=f.service,synthetic_pay_callback=lambda _:None)
            self.assertFalse(f.http.get('/api/postpay/health').json()['fulfillment_enabled'])

    def test_actual_separate_backend_child_to_native_original_paid_delivery(self):
        import hashlib
        import requests
        import numpy as np
        from photobooth.catalog import get_templates
        from photobooth.post_preview_checkout import ChargeReadiness
        from photobooth.post_preview_client import PostPreviewClient
        from photobooth.kiosk_v2.post_preview_protected_checkout import ProtectedCheckoutService
        from tests.test_post_preview_host import SandboxHostTests
        helper=SandboxHostTests(methodName='runTest');self.addCleanup(helper.doCleanups)
        with helper.temporary() as directory,patch.dict(os.environ,{
                'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0','PHOTOBOOTH_V2_CHECKOUT_MOCK':'0',
                'PHOTOBOOTH_V2_PRINT':'0','PHOTOBOOTH_V2_DRIVE':'0',
                'PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_AD_VIDEO':'0'}):
            config=helper.config(directory,server_key='Mid-server-DELIVERY-FIXTURE')
            process=helper.launch(config)
            http=requests.Session();http.trust_env=False
            client=PostPreviewClient(process.endpoint,'PB001',config.booth_token,
                                    allow_local_http=True,session=http)
            self.addCleanup(client.close)
            service=ProtectedCheckoutService(config.private_root,payment_client=client,
                                              qr_loader=lambda _:None)
            self.addCleanup(service.ledger.close)
            templates=get_templates()
            service.start(templates,{'template_a':2})
            frame=np.zeros((32,48,3),dtype=np.uint8)
            def shot():
                view=service.snapshot()
                service.capture(frame,view['capture_slot'],view['revision'],view['retake'],view['generation'])
            for _ in range(3):shot()
            service.retake(1);frame[:,:,1]=200;shot()
            service.compose();service.next()
            preview=service.snapshot()
            intent=service.checkout.freeze(service.lease,templates,revision=preview['revision'],
                expected_amount=15000,readiness=ChargeReadiness(True,True,True,True,True,True,True,25))
            group=intent['purchase_group_id']
            hashes={str(p.relative_to(service.root)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in service.photos.root.rglob('*.jpg')}
            Window.size=(452,900)
            camera=Mock();camera.read.return_value=frame;camera.preview.return_value=None
            app=ProtectedCheckoutApp(service.root,private_service=service,camera_device=camera)
            try:
                app.build();app.root=app.stage;Window.add_widget(app.stage)
                app._photo_view=preview;app.navigation.page=RESULT;app._show()
                app._photo_submit('accept_frozen_checkout',group)
                self.idle(app,lambda:app._photo_view.get('phase')=='checkout_ready')
                self.click(app,'SUDAH SIMPAN BUKTI • LANJUT QRIS')
                # This existing child transport settles on its independent GET,
                # including the GET performed immediately after CREATE. Do not
                # invent a mandatory intervening PENDING screen.
                self.idle(app,lambda:app._photo_view.get('phase')=='ticket_visible')
                self.assertEqual('settlement',service.ledger.db.execute(
                    'SELECT last_provider_state FROM pp_payment_attempts').fetchone()[0])
                self.click(app,'LANJUT • SIMPAN TIKET')
                self.idle(app,lambda:bool((app._photo_view.get('delivery') or {}).get('print_all_submitted')))
                self.idle(app)
                self.assertEqual('2',(config.private_root/'fixture-output-send-count').read_text())
                self.assertFalse(app._photo_view['delivery']['physical_paper_verified'])
                self.assertFalse(app._photo_view['delivery']['drive_verified'])
                self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
                self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_ticket_credentials').fetchone()[0])
                self.assertEqual(1,service.ledger.db.execute('SELECT retake_consumed FROM pp_templates').fetchone()[0])
                self.assertEqual(hashes,{str(p.relative_to(service.root)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in service.photos.root.rglob('*.jpg')})
                self.assertEqual(intent['contract_sha256'],service.ledger.db.execute(
                    'SELECT contract_sha256 FROM pp_checkout_intents').fetchone()[0])
                self.assertTrue(process.stop(timeout=10))
                self.assertEqual('OWED',service.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
            finally:
                app._photo_jobs.wait_closed(12);app.on_stop()
                if app.stage.parent:Window.remove_widget(app.stage)
                app._photo_jobs.wait_closed(12);service.wait_closed(12)


if __name__=='__main__':unittest.main()
