"""AR-06 customer secret is hashed, bound, expiring and separate from operators."""
from contextlib import closing
import hashlib
from pathlib import Path
import secrets
import tempfile
import unittest

from photobooth.checkout_backend import CheckoutBackend,ProviderUnavailable
from photobooth.checkout_store import CheckoutConflict,CheckoutStore
from tests.test_checkout_backend import FakeProvider,KEY,MERCHANT


class CustomerCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'orders.db';self.now=[1000.0]
        self.store=CheckoutStore(self.path,now=lambda:self.now[0]);self.addCleanup(self.store.close)
        self.provider=FakeProvider();self.backend=CheckoutBackend(self.store,self.provider,KEY,MERCHANT)
        self.capability=secrets.token_urlsafe(32)
        self.digest=hashlib.sha256(self.capability.encode()).hexdigest();self.key='a'*32
        result=self.backend.create_order('PB001',{'template_a':2},self.key,customer_capability_hash=self.digest)
        self.oid=result['order_id']

    def paid(self):
        self.provider.rows[self.oid].update(transaction_status='settlement',status_code='200')

    def redeem(self,capability=None,operation='b'*32):
        return self.backend.customer_claim(self.oid,'PB001',self.capability if capability is None else capability,operation)

    def test_only_hash_is_persisted_and_never_return_raw_secret_from_backend(self):
        row=dict(self.store.db.execute('SELECT * FROM checkout_customer_capabilities').fetchone())
        self.assertEqual(row['capability_hash'],self.digest)
        self.assertNotIn(self.capability,str(row))
        self.assertNotIn(self.capability,str(self.backend.status(self.oid,'PB001')))
        with self.assertRaises(CheckoutConflict):
            self.backend.create_order('PB001',{'template_a':2},self.key,customer_capability_hash='0'*64)

    def test_valid_customer_proof_needs_current_settlement_and_replays_only_same_action(self):
        self.paid();result=self.redeem()
        self.assertTrue(result['customer_claim']['verified'])
        self.assertEqual(result['customer_claim']['operation_id'],'b'*32)
        grant=result['grant_id'];again=self.redeem()
        self.assertEqual(again['grant_id'],grant)
        with self.assertRaises(PermissionError):self.redeem(operation='c'*32)
        self.assertEqual(self.provider.charges,1)

    def test_wrong_short_expired_and_wrong_booth_proofs_cannot_grant(self):
        self.paid()
        for token in ('123456',secrets.token_urlsafe(32)):
            with self.assertRaises(PermissionError):self.redeem(token)
        self.assertIsNone(self.store.get(self.oid)['grant_id'])
        self.now[0]+=86401
        with self.assertRaises(PermissionError):self.redeem()

    def test_offline_or_refunded_provider_never_consumes_valid_claim(self):
        self.paid();self.provider.outage=True
        with self.assertRaises(ProviderUnavailable):self.redeem()
        self.assertIsNone(self.store.db.execute('SELECT claim_operation_id FROM checkout_customer_capabilities').fetchone()[0])
        self.provider.outage=False
        self.provider.rows[self.oid].update(transaction_status='refund')
        with self.assertRaises(CheckoutConflict):self.redeem()
        self.assertIsNone(self.store.get(self.oid)['grant_id'])

    def test_attempt_budget_survives_backend_restart_without_leaking_provider_state(self):
        for _ in range(8):
            with self.assertRaises(PermissionError):self.redeem(secrets.token_urlsafe(32))
        reads=self.provider.reads
        with closing(CheckoutStore(self.path,now=lambda:self.now[0])) as reopened:
            backend=CheckoutBackend(reopened,self.provider,KEY,MERCHANT)
            with self.assertRaises(PermissionError):backend.customer_claim(self.oid,'PB001',self.capability,'b'*32)
        self.assertEqual(self.provider.reads,reads)

    def test_legacy_upgrade_has_no_fabricated_customer_credential(self):
        path=Path(self.tmp.name)/'legacy.db'
        with closing(CheckoutStore(path,now=lambda:self.now[0])) as old:
            row,_=old.begin('PB001',{'template_a':2},15000,'c'*32)
            before=old.get(row['id'])
            old.db.execute('DROP TABLE checkout_customer_capabilities')
        with closing(CheckoutStore(path,now=lambda:self.now[0])) as upgraded:
            self.assertEqual(upgraded.get(row['id']),before)
            self.assertEqual(upgraded.db.execute('SELECT count(*) FROM checkout_customer_capabilities').fetchone()[0],0)

    def test_http_customer_proof_is_booth_scoped_and_does_not_bypass_operator_api(self):
        from fastapi.testclient import TestClient
        from photobooth.booth_auth import BoothAuthenticator
        from photobooth.qris_api import create_app
        auth=BoothAuthenticator({'PB001':'x'*48,'PB002':'y'*48})
        headers={'X-Booth-ID':'PB001','Authorization':'Bearer '+'x'*48}
        url='/api/orders/'+self.oid+'/customer-claim'
        body={'capability':self.capability,'operation_id':'b'*32}
        with TestClient(create_app(self.backend,auth)) as http:
            self.assertEqual(http.post(url,json=body).status_code,401)
            self.assertEqual(http.post(url,json=body,headers={
                'X-Booth-ID':'PB002','Authorization':'Bearer '+'y'*48}).status_code,404)
            self.assertEqual(http.post(url,json=dict(body,capability='123456'),headers=headers).status_code,422)
            self.assertEqual(http.post(url,json=dict(body,capability=secrets.token_urlsafe(32)),headers=headers).status_code,403)
            self.paid();result=http.post(url,json=body,headers=headers)
            self.assertEqual(result.status_code,200)
            self.assertNotIn(self.capability,result.text)
            self.assertEqual(http.post('/api/orders/'+self.oid+'/recovery/resolve',headers=headers,json={}).status_code,404)

    def test_clock_rollback_cannot_extend_customer_credential_validity(self):
        self.paid();self.now[0]-=300
        with self.assertRaises(PermissionError):self.redeem()
        self.assertIsNone(self.store.get(self.oid)['grant_id'])
