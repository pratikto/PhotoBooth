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
    def booth(self, *, paid_ticket=False, paid_delivery=False, unattended=False):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
                'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0', 'PHOTOBOOTH_V2_CHECKOUT_MOCK':'0',
                'PHOTOBOOTH_V2_PRINT':'0', 'PHOTOBOOTH_V2_DRIVE':'0', 'PHOTOBOOTH_AUDIO':'0',
                'PHOTOBOOTH_AD_VIDEO':'0', 'PHOTOBOOTH_FACE_TRIGGER':'0', 'PHOTOBOOTH_PALM_TRIGGER':'0'}):
            root = Path(directory)
            fixture = CheckoutFixture(root)
            if paid_ticket or paid_delivery: fixture.enable_paid_ticket()
            if paid_delivery: fixture.enable_paid_delivery()
            camera = Mock()
            camera.read.return_value = np.zeros((32,48,3), dtype=np.uint8)
            camera.preview.return_value = None
            app = PrivateCheckoutFixtureApp(root, private_service=fixture.service, camera_device=camera)
            app.build(); app.root = app.stage
            fixture.bind_app(app)
            if unattended:
                from photobooth.post_preview_isolation import OriginalMockIsolation
                from photobooth.post_preview_claim import OriginalMockClaim
                from photobooth.post_preview_ccp import OriginalCCPService
                from photobooth.post_preview_ticket import OriginalRecoveryTicketService
                from photobooth.post_preview_pilot_admission import OriginalPilotAdmission
                isolate=OriginalMockIsolation(
                    fixture.service.ledger,fixture.backend,app._photo_jobs,
                    fixture.launch_lease,printer_lane=fixture.service._receipt_lane,
                    delivery=getattr(fixture,'paid_monitor',None),
                    allow_incomplete_fixture=True)
                proof=OriginalMockClaim(
                    fixture.backend,
                    OriginalCCPService(fixture.service.ledger,fixture.protector,'MTEST',
                                       allow_synthetic=True),
                    OriginalRecoveryTicketService(fixture.backend,fixture.protector,
                                                  allow_synthetic=True),
                    allow_incomplete_fixture=True)
                app.attach_synthetic_pilot_admission(
                    OriginalPilotAdmission(isolate,proof,allow_synthetic_pilot=True))
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

    def paid_ticket_screen(self, app, fixture):
        self.proof(app)
        self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
        self.settle(app)
        view = app._photo_view['payment']
        fixture.provider.state(view['attempts'][0]['provider_order_id'], 'settlement')
        self.click(app, 'PERIKSA STATUS')
        deadline = time.monotonic()+10
        while time.monotonic()<deadline and app._photo_view.get('phase') != 'ticket_offer':
            app._poll_photos(); EventLoop.idle(); time.sleep(.01)
        self.assertEqual('ticket_offer', app._photo_view['phase'])
        self.assertIsNotNone(app._ticket_card)
        app._ticket_card._ready_at = 0
        deadline = time.monotonic()+10
        while time.monotonic()<deadline and app._photo_view.get('phase') != 'ticket_visible':
            EventLoop.idle()
            if app._ticket_card is not None: app._ticket_card._rendered(0)
            app._poll_photos()
            time.sleep(.01)
        self.assertEqual('ticket_visible', app._photo_view['phase'])
        self.assertTrue(app._ticket_window.active)
        self.assertFalse(app._ticket_next_button.disabled)

    def test_native_original_paid_ticket_30_seconds_and_one_receipt_at_both_sizes(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size), self.booth(paid_ticket=True) as (app,fixture):
                Window.size=size
                self.paid_ticket_screen(app, fixture)
                deadline=time.monotonic()+10
                while time.monotonic()<deadline and not fixture.receipt_sizes:
                    app._poll_photos(); EventLoop.idle(); time.sleep(.01)
                self.assertEqual(1,len(fixture.receipt_sizes))
                self.assertGreaterEqual(app._ticket_window.remaining(),1)
                card=app._ticket_card
                self.click(app, 'LANJUT • SIMPAN TIKET')
                self.assertIsNone(card.qr_image.texture)
                self.assertEqual('',card.code.text)
                deadline=time.monotonic()+10
                while time.monotonic()<deadline and app._photo_view.get('phase')!='paid_hold':
                    app._poll_photos(); EventLoop.idle(); time.sleep(.01)
                self.assertEqual('paid_hold',app._photo_view['phase'])
                self.assertTrue(app._photo_view['ticket_dismissed'])
                self.assertEqual(1,len(fixture.receipt_sizes))
                self.assertEqual('DISMISSED',fixture.service.ledger.db.execute(
                    'SELECT screen_state FROM pp_ticket_presentations').fetchone()[0])
                self.assertFalse(app._photo_view['fulfillment_authorized'])

    def test_next_wipes_qr_while_original_receipt_sender_is_blocked(self):
        with self.booth(paid_ticket=True) as (app,fixture):
            Window.size=(452,900)
            fixture.receipt_entered=threading.Event()
            fixture.receipt_release=threading.Event()
            try:
                self.paid_ticket_screen(app,fixture)
                deadline=time.monotonic()+5
                while not fixture.receipt_entered.is_set() and time.monotonic()<deadline:
                    app._poll_photos(); EventLoop.idle(); time.sleep(.01)
                self.assertTrue(fixture.receipt_entered.is_set())
                self.assertTrue(app._photo_jobs.busy)
                card=app._ticket_card
                self.click(app,'LANJUT • SIMPAN TIKET')
                self.assertIsNone(card.qr_image.texture)
                self.assertFalse(card.code.text)
                self.assertEqual('ticket_visible',app._photo_view['phase'])
            finally:
                fixture.receipt_release.set()
            deadline=time.monotonic()+10
            while time.monotonic()<deadline and app._photo_view.get('phase')!='paid_hold':
                app._poll_photos(); EventLoop.idle(); time.sleep(.01)
            self.assertEqual('paid_hold',app._photo_view['phase'])
            self.assertEqual(1,len(fixture.receipt_sizes))
            self.assertEqual('SUBMITTED',fixture.service.ledger.db.execute(
                'SELECT receipt_state FROM pp_ticket_presentations').fetchone()[0])


    def test_native_paid_ticket_to_verified_drive_qr_and_original_single_print(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size), self.booth(paid_delivery=True) as (app,fixture):
                Window.size=size
                self.paid_ticket_screen(app,fixture)
                self.click(app,'LANJUT • SIMPAN TIKET')
                deadline=time.monotonic()+15
                while time.monotonic()<deadline and app._photo_view.get('phase')!='paid_delivery':
                    app._poll_photos();EventLoop.idle();time.sleep(.01)
                self.assertEqual('paid_delivery',app._photo_view['phase'],app._photo_error)
                self.assertEqual('PENDING_UPLOAD',app._photo_view['delivery']['upload_status'])
                self.assertEqual('https://drive.google.com/drive/folders/syntheticPaidFolder123',
                                 app._photo_view['delivery']['folder_url'])
                self.assertEqual('OWED',app._photo_view['delivery']['service_status'])
                self.click(app,'CETAK FOTO YANG SUDAH DIBAYAR')
                deadline=time.monotonic()+10
                while time.monotonic()<deadline and not fixture.paid_print_sends:
                    app._poll_photos();EventLoop.idle();time.sleep(.01)
                self.assertEqual(1,len(fixture.paid_print_sends))
                self.settle(app)
                self.assertEqual('SUBMITTED',app._photo_view['delivery']['print_states']['template_a'])
                self.assertEqual(1,fixture.provider.charges)
                self.assertFalse(app._photo_view['delivery']['physical_paper_verified'])
                self.assertFalse(app._photo_view['fulfillment_authorized'])
                self.click(app,'CEK STATUS UPLOAD')
                self.settle(app)
                self.assertEqual(1,len(fixture.paid_print_sends))
                self.assertEqual('OWED',fixture.service.ledger.db.execute(
                    'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_native_paid_drive_failure_does_not_offer_print_button(self):
        with self.booth(paid_delivery=True) as (app,fixture):
            Window.size=(452,900)
            self.paid_ticket_screen(app,fixture)
            fixture.drive.bind_transaction=lambda _: (_ for _ in ()).throw(OSError('offline'))
            self.click(app,'LANJUT • SIMPAN TIKET')
            deadline=time.monotonic()+10
            while time.monotonic()<deadline:
                app._poll_photos();EventLoop.idle();time.sleep(.01)
                if app._photo_error:break
            self.assertEqual('paid_hold',app._photo_view['phase'])
            self.assertEqual([],fixture.paid_print_sends)
            self.assertEqual('OWED',fixture.service.ledger.db.execute(
                'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_synthetic_unattended_ads_handoff_gate_at_small_portrait(self):
        with self.booth(paid_ticket=True,unattended=True) as (app,fixture):
            Window.size=(452,900)
            self.click(app,'PUNYA TIKET PEMULIHAN • SIMULASI')
            self.assertIsNotNone(app._pilot_popup)
            app._close_pilot_popup()
            self.start(app)
            old=fixture.service.lease
            app._photo_submit('abort')
            deadline=time.monotonic()+8
            while time.monotonic()<deadline:
                app._poll_photos()
                EventLoop.idle()
                if not app._photo_jobs.busy and app.navigation.page=='advert':
                    break
                time.sleep(.01)
            self.assertEqual('advert',app.navigation.page)
            self.assertTrue(fixture.service._hidden.is_set())
            self.click(app,'MULAI FOTO')
            self.assertNotEqual('advert',app.navigation.page)
            self.assertFalse(fixture.service._hidden.is_set())
            self.assertIsNone(fixture.service.lease)
            self.assertEqual('ISOLATED',fixture.service.ledger.db.execute(
                'SELECT lifecycle FROM pp_drafts WHERE draft_id=?',
                (old.draft_id,)).fetchone()[0])

    def test_synthetic_unattended_wrong_ticket_denied_at_large_portrait(self):
        with self.booth(paid_ticket=True,unattended=True) as (app,fixture):
            Window.size=(800,1280)
            app._pilot_submit_claim('MEONG:PAYMENT:1:PB001:invalid')
            self.assertEqual('advert',app.navigation.page)
            self.assertIn('Tiket tidak dapat diverifikasi',app._pilot_note)
            self.assertEqual(0,fixture.provider.charges)


    def test_native_paid_A_reclaims_original_ccp_after_protected_advert(self):
        """Kivy → original PAID → privacy lock → proof claim, no duplicate charge."""
        with self.booth(paid_ticket=True,unattended=True) as (app,fixture):
            Window.size=(452,900)
            self.proof(app)
            original_proof=app._photo_view['ccp_offer'].qr_payload
            original_lease=fixture.service.lease
            self.click(app,'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
            self.settle(app)
            payment=app._photo_view['payment']
            fixture.provider.state(
                payment['attempts'][0]['provider_order_id'],'settlement')
            self.click(app,'PERIKSA STATUS')
            deadline=time.monotonic()+10
            while time.monotonic()<deadline and (
                    app._photo_view.get('phase') not in {'ticket_offer','ticket_visible'}
                    or app._photo_jobs.busy):
                app._poll_photos()
                EventLoop.idle()
                time.sleep(.01)
            self.assertIn(app._photo_view['phase'],('ticket_offer','ticket_visible'))
            self.assertEqual(1,fixture.provider.charges)
            app._sandbox_lock_customer()
            deadline=time.monotonic()+10
            while time.monotonic()<deadline:
                app._poll_photos()
                EventLoop.idle()
                if (app.navigation.page=='advert' and not app._photo_jobs.busy
                        and fixture.service._hidden.is_set()):
                    break
                time.sleep(.01)
            self.assertEqual('advert',app.navigation.page)
            self.assertTrue(fixture.service._hidden.is_set())
            self.assertFalse(any(
                getattr(widget,'text','').startswith('MEONG:CCP:')
                for widget in app.stage.walk()))
            app._pilot_submit_claim(original_proof)
            self.assertEqual(original_lease.draft_id,fixture.service.lease.draft_id)
            self.assertGreater(fixture.service.lease.generation,original_lease.generation)
            self.assertEqual(1,fixture.provider.charges)
            self.assertEqual('OWED',fixture.service.ledger.db.execute(
                'SELECT status FROM pp_paid_services').fetchone()[0])
            self.assertEqual(1,fixture.service.ledger.db.execute(
                "SELECT count(*) FROM pp_isolation_ops WHERE state='ACKED'").fetchone()[0])
            self.assertEqual('result',app.navigation.page)
            self.assertIn(app._photo_view.get('phase'),
                          ('paid_hold','ticket_offer','ticket_visible'))

