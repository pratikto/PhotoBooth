"""Native synthetic checkout through real API; never save proof screenshots."""
from contextlib import contextmanager
from dataclasses import replace
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

    def test_native_precreate_readiness_hold_can_explicitly_retry_original_checkout(self):
        with self.booth() as (app, fixture):
            Window.size = (452, 900)
            self.proof(app)
            group = fixture.service.group
            originals = sorted(str(p) for p in fixture.service.root.rglob('*.jpg'))
            ready = fixture.ready
            fixture.ready = replace(ready, unclaimed_ready_capacity=0)
            self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
            self.settle(app)
            self.assertEqual('payment_hold', app._photo_view['phase'])
            self.assertEqual(0, fixture.provider.charges)
            fixture.ready = ready
            # Status reconciliation alone cannot create an unsent attempt.
            self.click(app, 'PERIKSA STATUS')
            self.settle(app)
            self.assertEqual('payment_hold', app._photo_view['phase'])
            self.assertEqual(0, fixture.provider.charges)
            self.click(app, 'COBA LAGI CHECKOUT ASLI')
            self.settle(app)
            self.assertEqual('payment_pending', app._photo_view['phase'])
            self.assertEqual(group, app._photo_view['payment']['purchase_group_id'])
            self.assertEqual(1, fixture.provider.charges)
            self.assertEqual(1, len(app._photo_view['payment']['attempts']))
            self.assertEqual(originals, sorted(str(p) for p in fixture.service.root.rglob('*.jpg')))

    def test_native_explicit_retry_after_lost_create_reply_never_reposts(self):
        with self.booth() as (app, fixture):
            Window.size = (452, 900)
            self.proof(app)
            group = fixture.service.group
            fixture.session.lose_response = True
            self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
            self.settle(app)
            self.assertEqual('payment_hold', app._photo_view['phase'])
            self.assertEqual(1, fixture.provider.charges)
            original = fixture.service.ledger.db.execute(
                'SELECT attempt_id,provider_order_id FROM pp_payment_attempts').fetchone()
            self.click(app, 'COBA LAGI CHECKOUT ASLI')
            self.settle(app)
            self.assertEqual('payment_pending', app._photo_view['phase'])
            self.assertEqual(group, app._photo_view['payment']['purchase_group_id'])
            self.assertEqual(1, fixture.provider.charges)
            self.assertEqual(original, fixture.service.ledger.db.execute(
                'SELECT attempt_id,provider_order_id FROM pp_payment_attempts').fetchone())

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


    def test_ticket_countdown_and_auto_wipe_continue_during_blocked_receipt(self):
        """PP-042/051: printer I/O cannot extend private QR visibility."""
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size), self.booth(paid_ticket=True) as (app,fixture):
                Window.size=size
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
                    began=app._ticket_window._started_at
                    with patch.object(app._ticket_window,'_clock',return_value=began+20):
                        app._poll_photos()
                        self.assertIn('10 detik',app._ticket_countdown.text)
                    with patch.object(app._ticket_window,'_clock',return_value=began+31):
                        app._poll_photos()
                    self.assertTrue(app._ticket_dismiss_pending)
                    self.assertIsNone(card.qr_image.texture)
                    self.assertEqual('',card.code.text)
                    self.assertIsNone(app._ticket_card)
                    self.assertFalse(app._ticket_window.active)
                    self.assertTrue(app._photo_jobs.busy)
                    self.assertEqual('SENDING',fixture.service.ledger.db.execute(
                        'SELECT receipt_state FROM pp_ticket_presentations').fetchone()[0])
                    self.assertEqual(1,fixture.provider.charges)
                    self.assertEqual([],fixture.receipt_sizes)
                finally:
                    fixture.receipt_release.set()
                deadline=time.monotonic()+10
                while time.monotonic()<deadline and app._photo_view.get('phase')!='paid_hold':
                    app._poll_photos(); EventLoop.idle(); time.sleep(.01)
                self.assertEqual('paid_hold',app._photo_view['phase'])
                self.assertEqual(1,len(fixture.receipt_sizes))
                self.assertEqual(('SUBMITTED','DISMISSED'),tuple(
                    fixture.service.ledger.db.execute(
                        'SELECT receipt_state,screen_state FROM pp_ticket_presentations'
                    ).fetchone()))
                self.assertEqual('OWED',fixture.service.ledger.db.execute(
                    'SELECT status FROM pp_paid_services').fetchone()[0])
                self.assertIsNone(app._ticket_card)

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


    def test_native_two_templates_pay_once_and_print_exact_original_copies(self):
        """Full native mock flow: two approved designs, one purchase, two safe batches."""
        with self.booth(paid_delivery=True) as (app,fixture):
            Window.size=(452,900)
            self.paid_ticket_screen(app,fixture)
            self.assertEqual(1,fixture.provider.charges)
            self.click(app,'LANJUT • SIMPAN TIKET')
            deadline=time.monotonic()+15
            while time.monotonic()<deadline and app._photo_view.get('phase')!='paid_delivery':
                app._poll_photos();EventLoop.idle();time.sleep(.01)
            self.assertEqual('paid_delivery',app._photo_view['phase'],app._photo_error)
            self.assertTrue(any(
                isinstance(getattr(w,'text',None),str)
                and 'QR DEMO' in w.text and 'BUKAN LINK DOWNLOAD' in w.text
                for w in app.stage.walk()))
            self.assertEqual({'template_a':'PREPARED','template_b':'PREPARED'},
                             app._photo_view['delivery']['print_states'])
            for number in (1,2):
                self.click(app,'CETAK FOTO YANG SUDAH DIBAYAR')
                deadline=time.monotonic()+10
                while time.monotonic()<deadline and len(fixture.paid_print_sends)<number:
                    app._poll_photos();EventLoop.idle();time.sleep(.01)
                self.assertEqual(number,len(fixture.paid_print_sends))
                self.settle(app)
            self.assertEqual([2,1],[copies for _path,copies in fixture.paid_print_sends])
            self.assertEqual({'template_a':'SUBMITTED','template_b':'SUBMITTED'},
                             app._photo_view['delivery']['print_states'])
            self.assertEqual(1,fixture.provider.charges)
            self.assertEqual(1,len(fixture.receipt_sizes))
            self.assertEqual('OWED',fixture.service.ledger.db.execute(
                'SELECT status FROM pp_paid_services').fetchone()[0])
            self.assertFalse(app._photo_view['delivery']['physical_paper_verified'])
            self.assertFalse(any(
                getattr(w,'text',None)=='CETAK FOTO YANG SUDAH DIBAYAR'
                and not w.disabled for w in app.stage.walk()))

    def test_native_late_qr1_paid_while_qr2_active_never_grants_twice(self):
        """A late PAID from expired QR1 overrides QR2's pending public QR."""
        with self.booth() as (app, fixture):
            Window.size = (452, 900)
            self.proof(app)
            original_group = fixture.service.group
            originals = sorted(str(p) for p in fixture.service.root.rglob('*.jpg'))
            self.assertEqual(6, len(originals))
            self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
            self.settle(app)
            first = app._photo_view['payment']['attempts'][0]['provider_order_id']
            fixture.provider.state(first, 'expire')
            self.click(app, 'PERIKSA STATUS')
            self.settle(app)
            self.assertEqual('EXPIRED_UNPAID', app._photo_view['payment']['state'])
            self.click(app, 'LANJUTKAN PESANAN ASLI')
            self.settle(app)
            self.assertEqual('payment_pending', app._photo_view['phase'])
            second = app._photo_view['payment']['attempts'][-1]['provider_order_id']
            self.assertNotEqual(first, second)
            self.assertEqual(2, fixture.provider.charges)

            # The first charge can settle late even after QR2 was displayed.
            fixture.provider.state(first, 'settlement')
            self.click(app, 'PERIKSA STATUS')
            self.settle(app)
            self.assertEqual('paid_hold', app._photo_view['phase'])
            payment = app._photo_view['payment']
            original_entitlement = payment['entitlement_id']
            self.assertIsNotNone(original_entitlement)
            self.assertEqual('OWED', payment['obligation_state'])
            self.assertIsNone(app._photo_view.get('payment_qr'))
            self.assertFalse(app._photo_view['fulfillment_authorized'])

            # An eventual second settlement is a finance excess, not a second
            # customer service or a new ticket/print/download entitlement.
            fixture.provider.state(second, 'settlement')
            app._photo_submit('check_payment', 'connectivity')
            self.settle(app)
            payment = app._photo_view['payment']
            self.assertEqual('paid_hold', app._photo_view['phase'])
            self.assertEqual(original_group, payment['purchase_group_id'])
            self.assertEqual(original_entitlement, payment['entitlement_id'])
            self.assertEqual(1, len(payment['excess_paid_attempts']))
            self.assertEqual(1, fixture.service.ledger.db.execute(
                'SELECT count(*) FROM pp_purchase_finance WHERE entitlement_id IS NOT NULL'
            ).fetchone()[0])
            self.assertEqual(2, fixture.provider.charges)
            self.assertEqual(0, fixture.provider.cancels)
            self.assertEqual(originals, sorted(
                str(p) for p in fixture.service.root.rglob('*.jpg')))

    def test_native_expiry_qr1_qr2_qr3_never_offers_qr4_or_recaptures(self):
        """A live original visitor can renew only verified expired QR1/2."""
        with self.booth() as (app, fixture):
            Window.size = (452, 900)
            self.proof(app)
            original_group = fixture.service.group
            self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
            self.settle(app)
            self.assertEqual('payment_pending', app._photo_view['phase'])
            original_amount = app._photo_view['payment']['amount']
            original_images = sorted(str(p) for p in fixture.service.root.rglob('*.jpg'))
            self.assertEqual(6, len(original_images))
            orders = []
            for expected_ordinal in (2, 3, 4):
                view = app._photo_view['payment']
                order = view['attempts'][-1]['provider_order_id']
                orders.append(order)
                fixture.provider.state(order, 'expire')
                self.click(app, 'PERIKSA STATUS')
                self.settle(app)
                self.assertEqual('payment_hold', app._photo_view['phase'])
                self.assertEqual('EXPIRED_UNPAID', app._photo_view['payment']['state'])
                if expected_ordinal <= 3:
                    self.click(app, 'LANJUTKAN PESANAN ASLI')
                    self.settle(app)
                    next_view = app._photo_view['payment']
                    self.assertEqual(expected_ordinal, next_view['attempts'][-1]['ordinal'])
                    self.assertEqual('payment_pending', app._photo_view['phase'])
                    self.assertEqual(original_amount, next_view['amount'])
                    self.assertEqual(original_group, next_view['purchase_group_id'])
                else:
                    # QR3 is the terminal attempt; no actionable QR4 button.
                    actions = [w for w in app.stage.walk()
                               if getattr(w, 'text', None) == 'LANJUTKAN PESANAN ASLI']
                    self.assertFalse(actions)
                    self.assertFalse(any(getattr(w, 'text', None) == 'COBA LAGI CHECKOUT ASLI'
                                         for w in app.stage.walk()))
                self.assertEqual(original_images, sorted(
                    str(p) for p in fixture.service.root.rglob('*.jpg')))
            self.assertEqual(3, fixture.provider.charges)
            self.assertEqual(3, len(set(orders)))
            self.assertEqual('NONE', app._photo_view['payment']['obligation_state'])

    def test_native_uncertain_design_print_quarantines_remaining_batches(self):
        """Printer timeout must not cause automatic continuation of B after A."""
        from photobooth.post_preview_store import DraftHeld
        with self.booth(paid_delivery=True) as (app, fixture):
            Window.size = (452, 900)
            self.paid_ticket_screen(app, fixture)
            self.click(app, 'LANJUT • SIMPAN TIKET')
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline and app._photo_view.get('phase') != 'paid_delivery':
                app._poll_photos(); EventLoop.idle(); time.sleep(.01)
            self.assertEqual('paid_delivery', app._photo_view['phase'], app._photo_error)
            sends = []
            def uncertain_send(path, *, copies):
                sends.append(copies)
                raise TimeoutError('synthetic: bytes may have left the printer')
            fixture.service._paid_printer.print_image = uncertain_send
            self.click(app, 'CETAK FOTO YANG SUDAH DIBAYAR')
            self.settle(app)
            delivery = app._photo_view['delivery']
            self.assertEqual({'template_a': 'UNCERTAIN', 'template_b': 'PREPARED'},
                             delivery['print_states'])
            self.assertTrue(delivery['needs_operator_review'])
            self.assertEqual([2], sends)
            buttons = [w for w in app.stage.walk()
                       if getattr(w, 'text', None) == 'CETAK FOTO YANG SUDAH DIBAYAR']
            self.assertEqual(1, len(buttons))
            self.assertTrue(buttons[0].disabled)
            self.click(app, 'CEK STATUS UPLOAD')
            self.settle(app)
            with self.assertRaises(DraftHeld):
                fixture.service.paid_print_next()
            self.assertEqual([2], sends)
            self.assertEqual(1, fixture.provider.charges)
            self.assertEqual(1, len(fixture.receipt_sizes))
            self.assertEqual('OWED', fixture.service.ledger.db.execute(
                'SELECT status FROM pp_paid_services').fetchone()[0])
            self.assertFalse(app._photo_view['delivery']['physical_paper_verified'])

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

