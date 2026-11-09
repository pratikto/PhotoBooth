"""Original backend ticket/typed-client integration, synthetic accounts only."""
from dataclasses import replace
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from photobooth.booth_auth import BoothAuthenticator
from photobooth.post_preview_api import create_app
from photobooth.post_preview_ticket import OriginalRecoveryTicketService,PendingRecoveryOffer
from photobooth.post_preview_ticket_presentation import OriginalRecoveryPresentation
from photobooth.post_preview_proof_client import PostPreviewRecoveryClient
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_store import DraftHeld
from photobooth.credential_vault import VaultUnavailable
from tests import test_post_preview_payments as fixtures
from tests.test_post_preview_api import TOKEN,HEADERS

class RecoveryPresentationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.PostPreviewPaymentTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.ledger,self.lease,self.group=self.fixture.ledger,self.fixture.lease,self.fixture.group
        self.ticket=self.new_ticket()
        self.presentation=OriginalRecoveryPresentation(self.ticket)
        self.http=TestClient(create_app(self.fixture.service,BoothAuthenticator({'PB001':TOKEN}),
            ticket_presentation=self.presentation,background_worker=False))
        self.addCleanup(self.http.close)
        self.owner=dict(visit_id=self.lease.visit_id,generation=self.lease.generation)
        self.path='/api/postpay/groups/'+self.group+'/ticket/'
    def new_ticket(self):
        return OriginalRecoveryTicketService(self.fixture.service,self.fixture.fixture.protector,
            allow_synthetic=True,monotonic=lambda:self.fixture.fixture.monotonic[0])
    def paid(self):
        self.fixture.begin();self.fixture.provider.state(self.fixture.order(),'settlement')
        return self.fixture.service.reconcile_all(self.group,'PB001',force=True)
    def post(self,action,**extra):
        return self.http.post(self.path+action,json=dict(self.owner,**extra),headers=HEADERS)
    def row(self):return self.ledger.db.execute('SELECT * FROM pp_ticket_presentations').fetchone()
    def test_auth_strict_owner_and_unpaid_precede_secret_issue(self):
        self.assertEqual(401,self.http.post(self.path+'offer',json=self.owner).status_code)
        self.assertEqual(409,self.post('offer').status_code)
        self.paid()
        for extra in ({'generation':2},{'visit_id':'visitorB'}):
            self.assertEqual(409,self.post('offer',**extra).status_code)
        self.assertEqual(422,self.post('offer',paid=True).status_code)
        self.assertEqual(0,self.ledger.db.execute('SELECT COUNT(*) FROM pp_ticket_credentials').fetchone()[0])
    def test_original_offer_retry_visibility_dismiss_and_no_redisplay(self):
        paid=self.paid()
        first=self.post('offer');self.assertEqual(200,first.status_code)
        self.assertEqual('no-store',first.headers['cache-control'])
        offer=first.json();self.assertEqual(offer,self.post('offer').json())
        self.assertEqual('NOT_OFFERED',self.row()['screen_state'])
        self.assertEqual('PREPARED',self.row()['receipt_state'])
        permit=dict(presentation_id=offer['presentation_id'])
        self.assertEqual(409,self.post('visible',presentation_id='0'*32).status_code)
        self.assertEqual(200,self.post('visible',**permit).status_code)
        self.assertEqual(200,self.post('visible',**permit).status_code)
        self.assertEqual(409,self.post('offer').status_code)
        self.assertEqual(200,self.post('dismiss',**permit).status_code)
        self.assertEqual(200,self.post('dismiss',**permit).status_code)
        self.assertEqual('DISMISSED',self.row()['screen_state'])
        self.assertEqual(409,self.post('offer').status_code)
        service=self.ledger.db.execute('SELECT * FROM pp_paid_services').fetchone()
        self.assertEqual(paid['entitlement_id'],service['entitlement_id']);self.assertEqual('OWED',service['status'])
        self.assertEqual(1,self.fixture.provider.charges)
    def test_stale_paid_and_retired_owner_hold_without_new_credential(self):
        self.paid();self.fixture.fixture.clock[0]+=31
        self.assertEqual(409,self.post('offer').status_code)
        self.fixture.service.reconcile_all(self.group,'PB001',force=True)
        offer=self.post('offer').json()
        self.fixture.service.signal_lifecycle(self.lease,'APP_SUSPENDED')
        self.assertEqual(409,self.post('visible',presentation_id=offer['presentation_id']).status_code)
        self.assertEqual('NOT_OFFERED',self.row()['screen_state'])
    def test_restart_preserves_ciphertext_and_cannot_replay_visible_ticket(self):
        self.paid();first=self.presentation.offer(self.group,self.lease)
        row=dict(self.ledger.db.execute('SELECT * FROM pp_ticket_credentials').fetchone())
        restarted=OriginalRecoveryPresentation(self.new_ticket())
        with self.assertRaises(DraftHeld):restarted.visible(self.group,self.lease,first.presentation_id)
        later=restarted.offer(self.group,self.lease)
        self.assertEqual(first.qr_payload,later.qr_payload)
        self.assertNotEqual(first.presentation_id,later.presentation_id)
        self.assertEqual(row,dict(self.ledger.db.execute('SELECT * FROM pp_ticket_credentials').fetchone()))
        restarted.visible(self.group,self.lease,later.presentation_id)
        with self.assertRaises(DraftHeld):OriginalRecoveryPresentation(self.new_ticket()).offer(self.group,self.lease)
    def test_retirement_and_expired_permit_refuse_late_visible(self):
        self.paid();offer=self.presentation.offer(self.group,self.lease)
        self.fixture.fixture.monotonic[0]+=61
        with self.assertRaises(VaultUnavailable):self.presentation.visible(self.group,self.lease,offer.presentation_id)
        self.presentation.retire(self.group,self.lease,offer.presentation_id)
        with self.assertRaises(DraftHeld):self.presentation.visible(self.group,self.lease,offer.presentation_id)
    def test_typed_client_reuses_original_recovery_offer_and_rejects_cross_role(self):
        self.paid()
        client=PostPreviewClient('https://example.invalid','PB001',TOKEN,expected_mode='mock')
        self.addCleanup(client.close);ticket=PostPreviewRecoveryClient(client)
        def transport(method,path,*,payload):
            response=self.http.request(method,path,json=payload,headers=HEADERS)
            if response.status_code!=200:raise RuntimeError('fixture rejected')
            return response.json()
        with patch.object(client._transport,'_call',side_effect=transport):
            offer=ticket.private_offer(self.group,self.lease)
            self.assertIs(type(offer),PendingRecoveryOffer)
            self.assertNotIn(offer.qr_payload,repr(offer)+str(offer))
            with self.assertRaises(DraftHeld):ticket.mark_visible(self.lease,replace(offer))
            ticket.mark_visible(self.lease,offer);ticket.dismiss(self.lease,offer)
        response=self.post('dismiss',presentation_id=offer.presentation_id).json()
        response.update(kind='CCP')
        with patch.object(client._transport,'_call',return_value=response):
            with self.assertRaises(DraftHeld):ticket.dismiss(self.lease,offer)
    def test_ticket_routes_absent_without_original_authority(self):
        with TestClient(create_app(self.fixture.service,BoothAuthenticator({'PB001':TOKEN}),background_worker=False)) as http:
            self.assertEqual(404,http.post(self.path+'offer',json=self.owner,headers=HEADERS).status_code)

    def test_native_client_rejects_foreign_generation_role_and_response_authority(self):
        self.paid();response=self.post('offer').json()
        payments=PostPreviewClient('https://example.invalid','PB001',TOKEN,expected_mode='mock')
        self.addCleanup(payments.close);client=PostPreviewRecoveryClient(payments)
        for changes in ({'booth_id':'PB002'},{'generation':True},{'generation':2},
                        {'kind':'CCP'},{'mode':'sandbox'},{'fulfillment_authorized':True},
                        {'qr_payload':response['qr_payload'].replace(':RECOVERY:',':CCP:')}):
            with self.subTest(changes=tuple(changes)),patch.object(
                    payments._transport,'_call',return_value=dict(response,**changes)):
                with self.assertRaises(DraftHeld):client.private_offer(self.group,self.lease)
