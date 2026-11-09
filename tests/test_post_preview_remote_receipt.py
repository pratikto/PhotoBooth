"""Original ticket receipt over authenticated API, fake printer transport only."""
import threading
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from photobooth.booth_auth import BoothAuthenticator
from photobooth.post_preview_api import create_app
from photobooth.post_preview_ticket_presentation import OriginalRecoveryPresentation
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_proof_client import PostPreviewRecoveryClient
from photobooth.printer import PrinterConfig,ThermalPrinter,NetworkSendError
from photobooth.post_preview_store import DraftHeld
from tests import test_post_preview_ticket_presentation as fixtures
from tests.test_post_preview_api import TOKEN,HEADERS

class RemoteReceiptTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.RecoveryPresentationTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups);self.fixture.paid()
        self.sent=[];self.entered=self.release=None;self.uncertain=False
        self.lane=threading.Lock()
        def send(host,port,payload):
            self.assertTrue(self.lane.locked());self.assertEqual('fixture-printer',host)
            self.assertEqual('SENDING',self.fixture.row()['receipt_state'])
            self.sent.append(payload)
            if self.entered:self.entered.set();self.release.wait(4)
            if self.uncertain:raise NetworkSendError('synthetic partial write')
        self.printer=ThermalPrinter(PrinterConfig(lan_host='fixture-printer'),network_sender=send,
            usb_sender=lambda payload:self.fail('No fallback after a sent/uncertain original receipt'))
        self.presenter=OriginalRecoveryPresentation(self.fixture.ticket,
            printer=self.printer,shared_lane=self.lane)
        self.http=TestClient(create_app(self.fixture.fixture.service,
            BoothAuthenticator({'PB001':TOKEN}),ticket_presentation=self.presenter,background_worker=False))
        self.addCleanup(self.http.close)
        self.owner=self.fixture.owner;self.path=self.fixture.path
        self.offer=self.post('offer').json()
        self.permit=dict(presentation_id=self.offer['presentation_id'])
    def post(self,action,**extra):
        return self.http.post(self.path+action,json=dict(self.owner,**extra),headers=HEADERS)
    def test_receipt_requires_genuine_visibility_then_sends_once_in_original_lane(self):
        self.assertEqual(409,self.post('receipt',**self.permit).status_code)
        self.assertEqual([],self.sent)
        self.post('visible',**self.permit)
        from photobooth.post_preview_ticket_receipt import render_post_preview_receipt
        matches=[]
        def render(payload,**kwargs):
            matches.append(payload==self.offer['qr_payload'])
            return render_post_preview_receipt(payload,**kwargs)
        with patch('photobooth.post_preview_ticket_receipt.render_post_preview_receipt',side_effect=render):
            first=self.post('receipt',**self.permit)
        self.assertEqual([True],matches)
        self.assertEqual(200,first.status_code)
        self.assertEqual('SUBMITTED',first.json()['receipt_state'])
        self.assertFalse(first.json()['physical_paper_verified'])
        self.assertEqual('no-store',first.headers['cache-control'])
        self.assertEqual(first.json(),self.post('receipt',**self.permit).json())
        self.assertEqual(1,len(self.sent))
        self.assertEqual('VISIBLE',self.fixture.row()['screen_state'])
        self.post('dismiss',**self.permit)
        self.assertEqual(first.json(),self.post('receipt',**self.permit).json())
        self.assertEqual(1,len(self.sent))

    def test_auth_scope_and_strict_body_precede_printer_effect(self):
        self.post('visible',**self.permit)
        response=self.http.post(self.path+'receipt',json=dict(self.owner,**self.permit))
        self.assertEqual(401,response.status_code)
        for extra,status in (({'generation':2},409),({'visit_id':'visitorB'},409),
                             ({'presentation_id':'0'*32},409),({'copies':2},422),
                             ({'printer':'PRIVATE-DO-NOT-ECHO'},422)):
            response=self.post('receipt',**dict(self.permit,**extra))
            self.assertEqual(status,response.status_code)
            self.assertFalse('PRIVATE-DO-NOT-ECHO' in response.text)
        self.assertEqual([],self.sent)
        self.assertEqual('PREPARED',self.fixture.row()['receipt_state'])

    def test_only_exact_original_printer_and_shared_lane_are_accepted(self):
        for printer,lane in ((object(),self.lane),(self.printer,None),(self.printer,object())):
            with self.assertRaises(ValueError):
                OriginalRecoveryPresentation(self.fixture.ticket,printer=printer,shared_lane=lane)
    def test_uncertain_paper_never_retries_or_becomes_success(self):
        self.uncertain=True;self.post('visible',**self.permit)
        self.assertEqual('UNCERTAIN',self.post('receipt',**self.permit).json()['receipt_state'])
        self.assertEqual('UNCERTAIN',self.post('receipt',**self.permit).json()['receipt_state'])
        self.assertEqual(1,len(self.sent))
    def test_restart_sending_is_observation_only_without_raw_offer_or_replay(self):
        self.post('visible',**self.permit)
        self.fixture.ledger.db.execute("UPDATE pp_ticket_presentations SET receipt_state='SENDING'")
        restarted=OriginalRecoveryPresentation(self.fixture.new_ticket(),printer=self.printer,shared_lane=self.lane)
        view=restarted.receipt(self.fixture.group,self.fixture.lease,self.offer['presentation_id'])
        self.assertEqual('SENDING',view['receipt_state']);self.assertEqual([],self.sent)
    def test_no_route_is_not_sent_and_never_replayed_when_config_later_exists(self):
        no_route=OriginalRecoveryPresentation(self.fixture.new_ticket())
        offer=no_route.offer(self.fixture.group,self.fixture.lease)
        no_route.visible(self.fixture.group,self.fixture.lease,offer.presentation_id)
        first=no_route.receipt(self.fixture.group,self.fixture.lease,offer.presentation_id)
        self.assertEqual('NOT_SENT',first['receipt_state'])
        self.assertEqual('NOT_SENT',self.post('receipt',presentation_id=offer.presentation_id).json()['receipt_state'])
        self.assertEqual([],self.sent)
    def test_client_receipt_reply_is_scoped_and_cannot_authorize_physical_success(self):
        payments=PostPreviewClient('https://example.invalid','PB001',TOKEN,expected_mode='mock')
        self.addCleanup(payments.close);client=PostPreviewRecoveryClient(payments)
        def transport(method,path,*,payload):
            response=self.http.request(method,path,json=payload,headers=HEADERS)
            if response.status_code!=200:raise RuntimeError('fixture held')
            return response.json()
        with patch.object(payments._transport,'_call',side_effect=transport):
            offer=client.private_offer(self.fixture.group,self.fixture.lease)
            client.mark_visible(self.fixture.lease,offer)
            view=client.send_receipt_once(self.fixture.lease,offer)
            self.assertEqual('SUBMITTED',view['receipt_state'])
        for change in ({'physical_paper_verified':True},{'receipt_state':'PAID'},
                       {'receipt_state':{}},{'generation':True}):
            with patch.object(payments._transport,'_call',return_value=dict(view,**change)):
                with self.assertRaises(DraftHeld):client.send_receipt_once(self.fixture.lease,offer)

    def test_concurrent_receipt_requests_cannot_double_send(self):
        self.post('visible',**self.permit)
        self.entered,self.release=threading.Event(),threading.Event()
        results=[]
        def request():results.append(self.post('receipt',**self.permit))
        first=threading.Thread(target=request);second=threading.Thread(target=request)
        first.start()
        try:
            self.assertTrue(self.entered.wait(2));second.start()
            self.assertEqual('SENDING',self.fixture.row()['receipt_state'])
        finally:
            self.release.set();first.join(5)
            if second.ident is not None:second.join(5)
        self.assertEqual(2,len(results))
        self.assertTrue(all(r.status_code==200 for r in results))
        self.assertEqual(results[0].json(),results[1].json())
        self.assertEqual(1,len(self.sent))
