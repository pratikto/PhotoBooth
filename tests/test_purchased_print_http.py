"""Original API/client/controller integration; only in-process mock provider."""
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.qris_api import create_app
from photobooth.qris_kiosk_client import QrisKioskClient
from photobooth.qris_session import KioskCheckout
from tests.qris_v2_fixture import InProcessSession
from tests.test_checkout_backend import FakeProvider,KEY,MERCHANT


class PaidPrintHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.store=CheckoutStore(self.root/'orders.sqlite');self.addCleanup(self.store.close)
        self.provider=FakeProvider();self.provider.mode='mock'
        self.backend=CheckoutBackend(self.store,self.provider,KEY,MERCHANT,delivery_policy='PRINT_REQUIRED_V1')
        self.app=create_app(self.backend,BoothAuthenticator({'PB001':'a'*48,'PB002':'b'*48}))
        self.client=self.make_client();self.token='C'*43;self.digest=hashlib.sha256(self.token.encode()).hexdigest()

    def make_client(self,booth='PB001',token='a'*48):
        client=QrisKioskClient('http://127.0.0.1:8765',booth,token,session=InProcessSession(self.app),
                               allow_local_http=True,expected_mode='mock')
        self.addCleanup(client.close);return client

    def test_original_controller_ticket_and_restart_claim_preserve_requirement(self):
        flow=KioskCheckout(self.root/'visit.json',self.client,mode='mock',booth_id='PB001',endpoint=self.client.base_url)
        self.addCleanup(flow.close);flow.begin({'template_a':2});flow.refresh()
        ticket=flow.customer_ticket();self.assertTrue(ticket.startswith('MEONG-RECOVERY-V1:PB001:'))
        first=flow.snapshot()['order'];oid=first['order_id'];requirement=first['delivery_requirement']
        self.assertEqual(requirement['copies'],{'template_a':2});self.assertIsNone(first['qr_url'])
        flow.acknowledge_ticket()
        self.provider.rows[oid].update(transaction_status='settlement',status_code='200')
        self.store.db.execute('UPDATE checkouts SET check_after=0');flow.refresh()
        self.assertEqual(flow.snapshot()['order']['state'],'PAID');flow.close()
        client=self.make_client();reopened=KioskCheckout(self.root/'visit.json',client,mode='mock',booth_id='PB001',endpoint=client.base_url)
        self.addCleanup(reopened.close);self.assertTrue(reopened.customer_claim_required)
        bad=ticket.rsplit(':',1)[0]+':'+'B'*43
        with self.assertRaises(RuntimeError):reopened.customer_claim(bad)
        reopened.customer_claim(ticket)
        self.assertFalse(reopened.customer_claim_required)
        self.assertEqual(reopened.snapshot()['order']['delivery_requirement'],requirement)
        self.assertEqual(self.provider.charges,1)
        self.assertEqual(self.store.fulfillment(oid,'PB001')['obligation_state'],'OWED')

    def test_http_replay_uses_original_snapshot_and_refuses_changed_cart(self):
        first=self.client.create_order({'template_a':2},'k'*32,customer_capability_hash=self.digest)
        with patch('photobooth.checkout_backend.frozen_contract',side_effect=AssertionError('No current artwork reads')):
            replay=self.client.create_order({'template_a':2},'k'*32,customer_capability_hash=self.digest)
            self.assertEqual(replay['delivery_requirement'],first['delivery_requirement'])
            with self.assertRaises(RuntimeError):self.client.create_order({'template_a':3},'k'*32,customer_capability_hash=self.digest)
        self.assertEqual(self.provider.charges,1)

    def test_client_policy_injection_missing_ticket_and_foreign_booth_are_rejected(self):
        http=self.client.session.http
        headers={'X-Booth-ID':'PB001','Authorization':'Bearer '+'a'*48,'Idempotency-Key':'k'*32}
        response=http.post('/api/orders',headers=headers,json={'quantities':{'template_a':2},
            'customer_capability_hash':self.digest,'delivery_policy':'PRINT_REQUIRED_V1'})
        self.assertEqual(response.status_code,422)
        with self.assertRaises(RuntimeError):self.client.create_order({'template_a':2},'k'*32)
        self.assertEqual(self.provider.charges,0)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkouts').fetchone()[0],0)
        first=self.client.create_order({'template_a':2},'k'*32,customer_capability_hash=self.digest)
        other=self.make_client('PB002','b'*48)
        with self.assertRaises(RuntimeError):other.status(first['order_id'])
        self.assertEqual(self.provider.charges,1)
