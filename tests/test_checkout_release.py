"""AR-09 release race, lost ACK and returning original customer ownership."""
import unittest
from contextlib import closing
import hashlib,secrets
from photobooth.checkout_store import CheckoutStore,CheckoutConflict
from photobooth import checkout_release
import tests.test_checkout_fulfillment as fixture

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        fixture.FulfillmentTests.setUp(self)
        self.capability=secrets.token_urlsafe(32)
        self.store.db.execute('INSERT INTO checkout_customer_capabilities (order_id,booth_id,capability_hash,created_at,expires_at) VALUES (?,?,?,?,?)',
            (self.oid,'PB001',hashlib.sha256(self.capability.encode()).hexdigest(),self.store.now(),self.store.now()+86400))
        fixture.FulfillmentTests.paid(self)
        self.grant=self.backend.claim(self.oid,'PB001',self.key)['grant_id']
        self.tx=self.backend.allocate(self.oid,'PB001',self.grant,'d'*32)['fulfillment']['transaction_id']

    def prepare(self):return checkout_release.prepare(self.store,self.oid,'PB001','e'*32,'operator-fixture')
    def ack(self):return checkout_release.acknowledge(self.store,self.oid,'PB001','e'*32,'f'*32)
    def claim(self):return self.backend.customer_claim(self.oid,'PB001',self.capability,'b'*32)

    def test_prepare_holds_booth_and_ack_releases_only_occupancy(self):
        before=self.store.get(self.oid);self.prepare()
        with self.assertRaises(CheckoutConflict):self.backend.create_order('PB001',{'template_a':1},'9'*32)
        self.ack();after=self.store.get(self.oid)
        for key in ('state','grant_id','service_state','local_transaction_id'):self.assertEqual(after[key],before[key])
        self.assertEqual(self.store.fulfillment(self.oid,'PB001')['obligation_state'],'OWED')
        self.backend.create_order('PB001',{'template_a':1},'9'*32)
        with self.assertRaises(CheckoutConflict):self.claim()

    def test_same_operations_survive_restart_and_mismatched_receipt_denied(self):
        first=self.prepare();self.assertEqual(self.prepare(),first)
        ack=self.ack()
        with closing(CheckoutStore(self.path)) as reopened:
            self.assertEqual(checkout_release.acknowledge(reopened,self.oid,'PB001','e'*32,'f'*32),ack)
            with self.assertRaises(CheckoutConflict):checkout_release.acknowledge(reopened,self.oid,'PB001','e'*32,'0'*32)

    def test_customer_reacquires_original_grant_and_allocation_with_new_fence(self):
        self.prepare();old=self.store.service_fence(self.oid,'PB001')['token'];self.ack()
        view=self.claim()
        self.assertFalse(view['closed']);self.assertEqual(view['grant_id'],self.grant)
        self.assertEqual(view['fulfillment']['transaction_id'],self.tx)
        self.assertNotEqual(view['service_fence']['token'],old)
        with self.assertRaises(CheckoutConflict):self.backend.service_transition(self.oid,'PB001',self.grant,'STARTED',self.tx,service_fence=old)
        self.backend.service_transition(self.oid,'PB001',self.grant,'STARTED',self.tx,service_fence=view['service_fence']['token'])

    def test_invalid_claim_and_legacy_operator_cannot_reactivate_suspended_rights(self):
        self.prepare();self.ack()
        with self.assertRaises(PermissionError):self.backend.customer_claim(self.oid,'PB001','x'*43,'b'*32)
        with self.assertRaises(CheckoutConflict):self.store.recovery_action(self.oid,'PB001','c'*32,'resume','fixture',self.tx,'operator-fixture')
        self.assertTrue(self.store.get(self.oid)['closed'])

    def test_http_release_requires_operator_and_exact_two_phase_receipts(self):
        from fastapi.testclient import TestClient
        from photobooth.qris_api import create_app
        from photobooth.booth_auth import BoothAuthenticator
        self.provider.mode='sandbox'
        http=TestClient(create_app(self.backend,BoothAuthenticator({'PB001':'x'*48}),recovery_pin='12345678'))
        self.addCleanup(http.close)
        url='/api/orders/'+self.oid+'/recovery/release'
        headers={'x-booth-id':'PB001','authorization':'Bearer '+'x'*48}
        body={'operation_id':'e'*32}
        self.assertEqual(http.post(url,json=body,headers=headers).status_code,401)
        headers['x-recovery-pin']='12345678'
        response=http.post(url,json=body,headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertFalse(response.json()['closed'])
        response=http.post(url,json=dict(body,isolation_id='f'*32),headers=headers)
        self.assertEqual(response.status_code,200);self.assertTrue(response.json()['closed'])
        current=self.claim()['service_fence']['token']
        service='/api/orders/'+self.oid+'/service'
        update={'grant_id':self.grant,'state':'STARTED','transaction_id':self.tx}
        self.assertEqual(http.post(service,json=update,headers=headers).status_code,409)
        self.assertEqual(http.post(service,json=dict(update,service_fence=current),headers=headers).status_code,200)

    def test_legacy_without_ticket_requires_explicit_sandbox_audited_two_phase_release(self):
        from fastapi.testclient import TestClient
        from photobooth.qris_api import create_app
        from photobooth.booth_auth import BoothAuthenticator
        # A separate order is issued by the pre-ticket client, without deleting
        # credentials from any existing order (all data here is disposable).
        oid=self.backend.create_order('PB002',{'template_b':1},'8'*32)['order_id']
        self.provider.rows[oid].update(transaction_status='settlement',status_code='200')
        self.backend._apply(self.store.get(oid),self.provider.get_status(oid))
        grant=self.backend.claim(oid,'PB002','8'*32)['grant_id']
        self.backend.service_transition(oid,'PB002',grant,'STARTED','legacy-photo-fixture')
        before=self.store.get(oid);contract=self.store.frozen_order(oid)
        self.provider.mode='sandbox'
        with TestClient(create_app(self.backend,BoothAuthenticator({'PB002':'x'*48}),recovery_pin='12345678')) as http:
            url='/api/orders/'+oid+'/recovery/release'
            headers={'x-booth-id':'PB002','authorization':'Bearer '+'x'*48,'x-recovery-pin':'12345678'}
            body={'operation_id':'7'*32,'legacy_without_ticket':True}
            self.assertEqual(http.post(url,json={'operation_id':'7'*32},headers=headers).status_code,409)
            self.assertEqual(http.post(url,json=body,headers=dict(headers,**{'x-recovery-pin':'00000000'})).status_code,401)
            result=http.post(url,json=body,headers=headers)
            self.assertEqual(result.status_code,200,result.text)
            prepared=result.json();self.assertFalse(prepared['closed'])
            self.assertEqual(prepared['release']['reason'],'SANDBOX_LEGACY_NO_TICKET')
            self.assertFalse(prepared['customer_capability_bound'])
            self.assertTrue(prepared['service_fence']['suspended'])
            self.assertEqual(http.post(url,json=body,headers=headers).json()['release'],prepared['release'])
            self.assertEqual(http.post(url,json={'operation_id':'7'*32},headers=headers).status_code,409)
            with self.assertRaises(CheckoutConflict):self.backend.create_order('PB002',{'template_a':1},'6'*32)
            self.assertEqual(http.post(url,json={'operation_id':'7'*32,'isolation_id':'5'*32},headers=headers).status_code,200)
        after=self.store.get(oid)
        for key in ('state','grant_id','service_state','local_transaction_id','checkout_key','quantities','amount'):
            self.assertEqual(after[key],before[key],key)
        self.assertTrue(after['closed']);self.assertEqual(self.store.frozen_order(oid),contract)
        self.assertEqual(self.store.fulfillment(oid,'PB002')['obligation_state'],'OWED')
        self.assertFalse(self.store.has_customer_capability(oid))
        with self.assertRaises(CheckoutConflict):self.backend.service_transition(oid,'PB002',grant,'STARTED','legacy-photo-fixture')
        self.backend.create_order('PB002',{'template_a':1},'6'*32)

    def test_legacy_exception_rejects_existing_capability_expired_or_revoked_and_wrong_mode(self):
        from fastapi.testclient import TestClient
        from photobooth.qris_api import create_app
        from photobooth.booth_auth import BoothAuthenticator
        self.provider.mode='sandbox'
        with TestClient(create_app(self.backend,BoothAuthenticator({'PB001':'x'*48}),recovery_pin='12345678')) as http:
            url='/api/orders/'+self.oid+'/recovery/release'
            headers={'x-booth-id':'PB001','authorization':'Bearer '+'x'*48,'x-recovery-pin':'12345678'}
            body={'operation_id':'7'*32,'legacy_without_ticket':True}
            for revoked,expiry in [(0,self.store.now()+3600),(1,self.store.now()+3600),(0,self.store.now()-1)]:
                self.store.db.execute('UPDATE checkout_customer_capabilities SET revoked=?,expires_at=? WHERE order_id=?',(revoked,expiry,self.oid))
                self.assertEqual(http.post(url,json=body,headers=headers).status_code,409)
            for mode in ('mock','production'):
                self.provider.mode=mode
                self.assertEqual(http.post(url,json=body,headers=headers).status_code,404)
            self.provider.mode='sandbox'
            for value in ('true',1,None):
                self.assertEqual(http.post(url,json=dict(body,legacy_without_ticket=value),headers=headers).status_code,422)
        self.assertIsNone(checkout_release.latest(self.store,self.oid,'PB001'))
        self.assertFalse(self.store.get(self.oid)['closed'])
