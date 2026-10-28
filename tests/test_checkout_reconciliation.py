"""AR-02 fresh provider evidence, authenticated observations and no replay."""
import asyncio
from contextlib import closing
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_backend import CheckoutBackend, ProviderUnavailable
from photobooth.checkout_store import CheckoutConflict, CheckoutStore
from photobooth.qris_api import create_app
from tests.test_checkout_backend import FakeProvider, KEY, MERCHANT


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = CheckoutStore(Path(self.tmp.name)/'orders.sqlite')
        self.addCleanup(self.store.close)
        self.provider = FakeProvider()
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        self.key = 'a'*32
        self.oid = self.backend.create_order('PB001', {'template_a': 2}, self.key)['order_id']

    def paid(self):
        self.provider.rows[self.oid].update(transaction_status='settlement', status_code='200')
        self.backend._apply(self.store.get(self.oid), self.provider.get_status(self.oid))

    def test_cached_paid_refund_reconciles_without_grant_or_service(self):
        self.paid()
        self.provider.rows[self.oid].update(transaction_status='refund')
        result = self.backend.reconcile(self.oid, 'PB001')
        self.assertEqual(result['reconciliation']['outcome'], 'review')
        self.assertTrue(result['reconciliation']['checked'])
        self.assertEqual(result['state'], 'REVIEW_REQUIRED')
        self.assertIsNone(result['grant_id'])
        self.assertEqual(result['service_state'], 'NONE')
        self.assertEqual(self.provider.charges, 1)

    def test_cached_paid_outage_is_unknown_never_permission(self):
        self.paid(); self.provider.outage = True
        result = self.backend.reconcile(self.oid, 'PB001')
        self.assertEqual(result['state'], 'PAID')  # historical liability retained
        self.assertTrue(result['verification_pending'])
        self.assertFalse(result['reconciliation']['checked'])
        self.assertEqual(result['reconciliation']['outcome'], 'unknown')
        with self.assertRaises(ProviderUnavailable):
            self.backend.claim(self.oid, 'PB001', self.key)
        self.assertIsNone(self.store.get(self.oid)['grant_id'])

    def test_pending_after_cached_paid_cannot_authorize_claim(self):
        self.paid()
        self.provider.rows[self.oid].update(transaction_status='pending')
        result = self.backend.reconcile(self.oid, 'PB001')
        self.assertEqual(result['state'], 'PAID')
        self.assertEqual(result['reconciliation']['outcome'], 'pending')
        with self.assertRaises(CheckoutConflict):
            self.backend.claim(self.oid, 'PB001', self.key)

    def test_invalid_identity_and_404_leave_old_liability_held(self):
        self.paid()
        original = dict(self.provider.rows[self.oid])
        for data, outcome in (({'status_code': '404'}, 'provider_not_found_unproven'),
                              (dict(original, merchant_id='OTHER'), 'unknown'),
                              (dict(original, fraud_status='challenge'), 'unknown')):
            with self.subTest(outcome=outcome), patch.object(self.provider, 'get_status', return_value=data):
                result = self.backend.reconcile(self.oid, 'PB001')
                self.assertEqual(result['reconciliation']['outcome'], outcome)
                self.assertFalse(result['reconciliation']['checked'])
                self.assertEqual(self.store.get(self.oid)['state'], 'PAID')

    def test_reconciliation_never_allocates_grant_but_fresh_claim_replays_same_one(self):
        self.paid()
        for _ in range(3):
            result = self.backend.reconcile(self.oid, 'PB001')
            self.assertEqual(result['reconciliation']['outcome'], 'paid')
            self.assertIsNone(result['grant_id'])
        a = self.backend.claim(self.oid, 'PB001', self.key)
        b = self.backend.claim(self.oid, 'PB001', self.key)
        self.assertEqual(a['grant_id'], b['grant_id'])
        self.assertEqual(self.provider.charges, 1)

    def test_start_requires_fresh_settlement_even_with_previously_issued_grant(self):
        self.paid()
        grant = self.backend.claim(self.oid, 'PB001', self.key)['grant_id']
        self.provider.outage = True
        with self.assertRaises(ProviderUnavailable):
            self.backend.service_transition(self.oid, 'PB001', grant, 'STARTED', 'PB001_00000001')
        self.assertEqual(self.store.get(self.oid)['service_state'], 'RESERVED')

    def test_wrong_checkout_key_is_rejected_before_provider_read(self):
        self.paid()
        with patch.object(self.provider, 'get_status', side_effect=AssertionError('No I/O')):
            with self.assertRaises(CheckoutConflict):
                self.backend.claim(self.oid, 'PB001', 'b'*32)

    def test_http_observation_does_not_need_pin_but_operator_mutation_still_does(self):
        auth = BoothAuthenticator({'PB001':'x'*48, 'PB002':'y'*48})
        headers = {'X-Booth-ID':'PB001', 'Authorization':'Bearer '+'x'*48}
        with TestClient(create_app(self.backend, auth)) as http:
            url='/api/orders/'+self.oid
            self.assertEqual(http.post(url+'/reconcile').status_code, 401)
            self.assertEqual(http.post(url+'/reconcile', headers={
                'X-Booth-ID':'PB002', 'Authorization':'Bearer '+'y'*48}).status_code, 404)
            result=http.post(url+'/reconcile', headers=headers)
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json()['reconciliation']['outcome'], 'pending')
            self.assertEqual(http.post(url+'/recovery/resolve', headers=headers,json={}).status_code, 404)
        self.assertIsNone(self.store.get(self.oid)['grant_id'])

    def test_http_reconciliation_runs_off_event_loop(self):
        started, release = threading.Event(), threading.Event()
        original=self.provider.get_status
        def slow(oid):
            started.set(); release.wait(3); return original(oid)
        self.provider.get_status=slow
        app=create_app(self.backend,BoothAuthenticator({'PB001':'x'*48}))
        async def scenario():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as http:
                task=asyncio.create_task(http.post('/api/orders/'+self.oid+'/reconcile',headers={
                    'X-Booth-ID':'PB001','Authorization':'Bearer '+'x'*48}))
                try:
                    self.assertTrue(await asyncio.to_thread(started.wait,1))
                    self.assertEqual((await asyncio.wait_for(http.get('/api/health'),.5)).status_code,200)
                finally:
                    release.set(); await task
        asyncio.run(scenario())
