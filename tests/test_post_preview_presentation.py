"""Original CCP API/renderer boundaries; synthetic provider/custody only."""
from dataclasses import replace
import threading
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from photobooth.booth_auth import BoothAuthenticator
from photobooth.post_preview_api import create_app
from photobooth.post_preview_ccp import PendingCCPOffer
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_presentation import OriginalCCPPresentation
from photobooth.post_preview_proof_client import PostPreviewCCPClient
from photobooth.post_preview_store import DraftHeld
from tests.test_post_preview_api import TOKEN, HEADERS
from tests import test_post_preview_payments as payment_fixtures


class OriginalPresentationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = payment_fixtures.PostPreviewPaymentTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.ledger = self.fixture.ledger
        self.lease, self.group = self.fixture.lease, self.fixture.group
        self.credentials = self.fixture.fixture.service
        self.presenter = OriginalCCPPresentation(self.credentials)
        self.app = create_app(self.fixture.service, BoothAuthenticator({'PB001':TOKEN}),
                              ccp_presentation=self.presenter, background_worker=False)
        self.http = TestClient(self.app)
        self.addCleanup(self.http.close)
        self.path = '/api/postpay/groups/'+self.group+'/ccp/'
        self.owner = dict(visit_id=self.lease.visit_id, generation=self.lease.generation)
        self.payments = PostPreviewClient('https://example.invalid','PB001',TOKEN,expected_mode='mock')
        self.addCleanup(self.payments.close)
        self.client = PostPreviewCCPClient(self.payments)

    def post(self, action, **extra):
        return self.http.post(self.path+action,json=dict(self.owner,**extra),headers=HEADERS)

    def transport(self, method, path, *, payload):
        response = self.http.request(method,path,json=payload,headers=HEADERS)
        if response.status_code != 200:
            raise RuntimeError('Synthetic HTTP rejected')
        return response.json()

    def test_offer_is_original_private_and_does_not_claim_visible_or_paid(self):
        first = self.post('offer')
        self.assertEqual(200,first.status_code)
        self.assertEqual('no-store',first.headers['cache-control'])
        self.assertEqual('no-referrer',first.headers['referrer-policy'])
        offer = first.json()
        self.assertEqual(offer,self.post('offer').json())
        row = self.ledger.db.execute('SELECT * FROM pp_ccp_credentials').fetchone()
        self.assertIsNone(row['offered_at'])
        self.assertNotIn(offer['qr_payload'].encode(),bytes(row['ciphertext']))
        self.assertEqual(0,self.fixture.provider.charges)
        with self.assertRaises(DraftHeld): self.fixture.service.begin(self.lease)

    def test_auth_owner_generation_and_strict_body_precede_custody(self):
        for headers,status in (({},401),(HEADERS,409)):
            response = self.http.post(self.path+'offer',json=dict(self.owner,generation=2),headers=headers)
            self.assertEqual(status,response.status_code)
            self.assertEqual('no-store',response.headers['cache-control'])
        for extra in ({'paid':True},{'qr_payload':'PRIVATE-DO-NOT-ECHO'},{'generation':True}):
            response = self.post('offer',**extra)
            self.assertEqual(422,response.status_code)
            self.assertNotIn('PRIVATE-DO-NOT-ECHO',response.text)
        self.assertEqual(0,self.ledger.db.execute('SELECT COUNT(*) FROM pp_ccp_credentials').fetchone()[0])

    def test_only_exact_original_visible_permit_enables_payment(self):
        offer = self.post('offer').json()
        self.assertEqual(409,self.post('visible',presentation_id='0'*32).status_code)
        self.assertEqual(200,self.post('visible',presentation_id=offer['presentation_id']).status_code)
        self.assertEqual(200,self.post('visible',presentation_id=offer['presentation_id']).status_code)
        first = self.fixture.service.begin(self.lease)
        self.assertEqual('PENDING',first['state'])
        self.assertEqual(1,self.fixture.provider.charges)
        self.assertEqual(1,self.ledger.db.execute("SELECT COUNT(*) FROM pp_events WHERE event='CCP_OFFERED'").fetchone()[0])

    def test_retire_rejects_late_callback_and_reuses_original_ciphertext(self):
        first = self.post('offer').json()
        before = dict(self.ledger.db.execute('SELECT * FROM pp_ccp_credentials').fetchone())
        self.assertEqual(200,self.post('retire',presentation_id=first['presentation_id']).status_code)
        self.assertEqual(409,self.post('visible',presentation_id=first['presentation_id']).status_code)
        later = self.post('offer').json()
        self.assertEqual(first['qr_payload'],later['qr_payload'])
        self.assertNotEqual(first['presentation_id'],later['presentation_id'])
        after = dict(self.ledger.db.execute('SELECT * FROM pp_ccp_credentials').fetchone())
        self.assertEqual(before,after)

    def test_expired_permit_and_retired_generation_do_not_offer(self):
        first = self.post('offer').json()
        self.fixture.fixture.monotonic[0] += 61
        self.assertEqual(503,self.post('visible',presentation_id=first['presentation_id']).status_code)
        self.ledger.lifecycle_event(self.lease,'VISIT_ABANDONED')
        self.assertEqual(409,self.post('offer').status_code)
        self.assertEqual(409,self.post('visible',presentation_id=first['presentation_id']).status_code)

    def test_paid_order_cannot_use_checkout_offer_to_redisplay_proof(self):
        first = self.post('offer').json()
        self.post('visible',presentation_id=first['presentation_id'])
        self.fixture.service.begin(self.lease)
        self.fixture.provider.state(self.fixture.order(),'settlement')
        paid = self.fixture.service.reconcile_all(self.group,'PB001',force=True)
        self.assertTrue(paid['paid_verified'])
        self.assertEqual(409,self.post('offer').status_code)
        self.assertEqual('OWED',paid['obligation_state'])

    def test_native_adapter_uses_existing_offer_renderer_type_and_exact_identity(self):
        with patch.object(self.payments._transport,'_call',side_effect=self.transport):
            offer = self.client.private_offer(self.group,self.lease)
            self.assertIs(type(offer),PendingCCPOffer)
            self.assertNotIn(offer.qr_payload,repr(offer)+str(offer))
            with self.assertRaises(DraftHeld): self.client.mark_visible(self.lease,replace(offer))
            self.client.mark_visible(self.lease,offer)
            self.client.retire_offer(self.lease,offer)
            with self.assertRaises(DraftHeld):self.client.mark_visible(self.lease,offer)

    def test_native_adapter_rejects_foreign_scope_mode_kind_and_generation(self):
        correct = self.post('offer').json()
        for changes in ({'mode':'sandbox'},{'kind':'RECOVERY'},{'generation':True},
                        {'booth_id':'PB002'},{'purchase_group_id':'0'*32},
                        {'qr_payload':correct['qr_payload'].replace(':CCP:',':RECOVERY:')},
                        {'presentation_id':'../bad'},{'unexpected':True}):
            with self.subTest(changes=tuple(changes)),patch.object(
                    self.payments._transport,'_call',return_value=dict(correct,**changes)):
                with self.assertRaises(DraftHeld):self.client.private_offer(self.group,self.lease)

    def test_privacy_hide_fences_delayed_offer_without_waiting_for_network(self):
        entered,release = threading.Event(),threading.Event()
        errors = []
        correct = self.post('offer').json()
        def delayed(*args,**kwargs):
            entered.set();release.wait(3)
            return correct
        def request():
            try:self.client.private_offer(self.group,self.lease)
            except DraftHeld:errors.append('held')
        with patch.object(self.payments._transport,'_call',side_effect=delayed):
            thread=threading.Thread(target=request)
            thread.start()
            try:
                self.assertTrue(entered.wait(2))
                self.client.hide_private()
                self.assertTrue(thread.is_alive())
            finally:
                release.set();thread.join(3)
        self.assertEqual(['held'],errors)
        self.assertIsNone(self.client._pending)

    def test_proof_routes_are_absent_without_original_backend_authority(self):
        with TestClient(create_app(self.fixture.service,BoothAuthenticator({'PB001':TOKEN}),background_worker=False)) as other:
            self.assertEqual(404,other.post(self.path+'offer',json=self.owner,headers=HEADERS).status_code)


if __name__ == '__main__':
    unittest.main()
