"""Native existing card + timer -> original authenticated ticket HTTP routes."""
import unittest
from unittest.mock import patch
from kivy.base import EventLoop
from kivy.core.window import Window
from photobooth.kiosk_v2.post_preview_remote_ticket import RemoteRecoveryTicketSession
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_proof_client import PostPreviewRecoveryClient
from photobooth.post_preview_store import DraftHeld
from tests import test_post_preview_ticket_presentation as fixtures
from tests.test_post_preview_api import TOKEN,HEADERS

class RemoteTicketViewTests(unittest.TestCase):
    def fixture(self):
        fixture=fixtures.RecoveryPresentationTests();fixture.setUp()
        self.addCleanup(fixture.doCleanups);fixture.paid()
        payments=PostPreviewClient('https://example.invalid','PB001',TOKEN,expected_mode='mock')
        self.addCleanup(payments.close)
        def transport(method,path,*,payload):
            response=fixture.http.request(method,path,json=payload,headers=HEADERS)
            if response.status_code!=200:raise RuntimeError('fixture held')
            return response.json()
        patcher=patch.object(payments._transport,'_call',side_effect=transport)
        patcher.start();self.addCleanup(patcher.stop)
        tick=[100.]
        session=RemoteRecoveryTicketSession(PostPreviewRecoveryClient(payments),fixture.group,
            fixture.lease,monotonic=lambda:tick[0])
        self.addCleanup(session.hide_private)
        session.prepare();card=session.create_card()
        Window.add_widget(card)
        self.addCleanup(lambda:Window.remove_widget(card) if card.parent else None)
        return fixture,session,card,tick
    def render(self,session,card):
        card._ready_at=0
        for _ in range(6):EventLoop.idle()
        card._rendered(0)
        session.acknowledge_visible()
    def test_actual_original_api_card_and_exact_30_seconds_at_both_sizes(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size):
                Window.size=size
                fixture,session,card,tick=self.fixture()
                with self.assertRaises(DraftHeld):session.acknowledge_visible()
                self.assertFalse(session.window.active)
                self.render(session,card)
                self.assertEqual('VISIBLE',fixture.row()['screen_state'])
                self.assertEqual('PREPARED',fixture.row()['receipt_state'])
                tick[0]=129.999
                self.assertEqual(1,session.poll());self.assertIsNotNone(card.qr_image.texture)
                tick[0]=130.
                self.assertEqual(0,session.poll())
                self.assertIsNone(card.qr_image.texture);self.assertEqual('',card.code.text)
                session.dismiss()
                self.assertEqual('DISMISSED',fixture.row()['screen_state'])
                self.assertIsNone(fixture.presentation._pending)
                self.assertIsNone(session._offer)
                self.assertEqual(1,fixture.fixture.provider.charges)
                self.doCleanups()
    def test_next_wipes_immediately_even_if_backend_dismiss_fails(self):
        Window.size=(452,900)
        fixture,session,card,tick=self.fixture();self.render(session,card)
        self.assertTrue(session.finish(next_pressed=True))
        self.assertIsNone(card.qr_image.texture);self.assertEqual('',card.code.text)
        with patch.object(session.client,'dismiss',side_effect=DraftHeld('fixture outage')):
            with self.assertRaises(DraftHeld):session.dismiss()
        self.assertEqual('VISIBLE',fixture.row()['screen_state'])
        self.assertFalse(session.window.active)
        session.dismiss()
        self.assertEqual('DISMISSED',fixture.row()['screen_state'])
    def test_hide_before_render_never_claims_offer_or_restarts(self):
        Window.size=(452,900)
        fixture,session,card,tick=self.fixture()
        session.hide_private()
        for _ in range(4):EventLoop.idle()
        self.assertIsNone(card.qr_image.texture);self.assertEqual('',card.code.text)
        self.assertEqual('NOT_OFFERED',fixture.row()['screen_state'])
        with self.assertRaises(DraftHeld):session.acknowledge_visible()
        with self.assertRaises(DraftHeld):session.prepare()

    def test_actual_backend_child_settlement_to_native_original_card(self):
        import requests
        from tests import test_post_preview_host as hosts
        helper=hosts.SandboxHostTests();self.addCleanup(helper.doCleanups)
        with helper.temporary() as directory:
            config=helper.config(directory,server_key='Mid-server-RECEIPT-FIXTURE')
            process=helper.launch(config)
            ledger,lease,group=helper.prepare_original_checkout(config)
            transport=requests.Session();transport.trust_env=False
            payments=PostPreviewClient(process.endpoint,'PB001',config.booth_token,
                allow_local_http=True,session=transport)
            self.addCleanup(payments.close)
            payments.begin(group,lease)
            self.assertTrue(helper.fresh_paid(payments,group,'connectivity')['paid_verified'])
            tick=[100.]
            session=RemoteRecoveryTicketSession(PostPreviewRecoveryClient(payments),group,lease,
                monotonic=lambda:tick[0])
            self.addCleanup(session.hide_private)
            session.prepare();Window.size=(452,900)
            card=session.create_card();Window.add_widget(card)
            self.addCleanup(lambda:Window.remove_widget(card) if card.parent else None)
            self.render(session,card)
            self.assertEqual('VISIBLE',ledger.db.execute('SELECT screen_state FROM pp_ticket_presentations').fetchone()[0])
            receipt=session.send_receipt_once()
            self.assertEqual('SUBMITTED',receipt['receipt_state'])
            self.assertFalse(receipt['physical_paper_verified'])
            self.assertEqual('1',(config.private_root/'fixture-ticket-send-count').read_text())
            self.assertTrue(session.finish(next_pressed=True))
            self.assertIsNone(card.qr_image.texture);self.assertEqual('',card.code.text)
            session.dismiss()
            self.assertEqual('DISMISSED',ledger.db.execute('SELECT screen_state FROM pp_ticket_presentations').fetchone()[0])
            self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_ticket_credentials').fetchone()[0])
            self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
            self.assertTrue(process.stop())

    def test_privacy_hide_does_not_wait_for_delayed_visible_ack(self):
        import threading
        Window.size=(452,900)
        fixture,session,card,tick=self.fixture()
        card._ready_at=0
        for _ in range(6):EventLoop.idle()
        card._rendered(0)
        entered,release=threading.Event(),threading.Event()
        errors=[]
        def held(*args):entered.set();release.wait(3)
        def acknowledge():
            try:session.acknowledge_visible()
            except DraftHeld:errors.append('held')
        with patch.object(session.client,'mark_visible',side_effect=held):
            thread=threading.Thread(target=acknowledge);thread.start()
            try:
                self.assertTrue(entered.wait(2));session.hide_private()
                self.assertTrue(thread.is_alive())
                self.assertIsNone(card.qr_image.texture);self.assertEqual('',card.code.text)
            finally:release.set();thread.join(3)
        self.assertEqual(['held'],errors)
        self.assertFalse(session.window.active);self.assertIsNone(session._offer)

    def test_genuine_screen_deadline_does_not_wait_for_backend_visible_ack(self):
        import threading
        Window.size=(452,900)
        fixture,session,card,tick=self.fixture()
        card._ready_at=0
        for _ in range(6):EventLoop.idle()
        card._rendered(0)
        entered,release=threading.Event(),threading.Event()
        original=session.client.mark_visible
        errors=[]
        def held(*args):
            entered.set();release.wait(3);return original(*args)
        def acknowledge():
            try:session.acknowledge_visible()
            except Exception as error:errors.append(type(error).__name__)
        with patch.object(session.client,'mark_visible',side_effect=held):
            thread=threading.Thread(target=acknowledge);thread.start()
            try:
                self.assertTrue(entered.wait(2))
                self.assertTrue(session.window.active)
                tick[0]=130.
                self.assertEqual(0,session.poll())
                self.assertIsNone(card.qr_image.texture);self.assertEqual('',card.code.text)
                self.assertTrue(thread.is_alive())
            finally:release.set();thread.join(3)
        self.assertEqual([],errors);self.assertFalse(session.window.active)
        session.dismiss()
        self.assertEqual('DISMISSED',fixture.row()['screen_state'])
