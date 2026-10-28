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
        self.now = [1000.0]
        self.store = CheckoutStore(Path(self.tmp.name)/'orders.sqlite', now=lambda:self.now[0])
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
                self.now[0] += 61
                result = self.backend.reconcile(self.oid, 'PB001')
                self.assertEqual(result['reconciliation']['outcome'], outcome)
                self.assertFalse(result['reconciliation']['checked'])
                self.assertEqual(self.store.get(self.oid)['state'], 'PAID')

    def test_reconciliation_never_allocates_grant_but_fresh_claim_replays_same_one(self):
        self.paid()
        for _ in range(3):
            self.now[0] += 11
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

    def test_retry_backoff_is_durable_bounded_and_not_bypassed_by_duplicate_calls(self):
        self.provider.outage=True
        for base in (10,20,40,60,60):
            result=self.backend.reconcile(self.oid,'PB001')
            delay=result['reconciliation']['retry_after']
            self.assertGreaterEqual(delay,base)
            self.assertLessEqual(delay,min(base*1.1+1,60))
            reads=self.provider.reads
            duplicate=self.backend.reconcile(self.oid,'PB001')
            self.assertFalse(duplicate['reconciliation']['checked'])
            self.assertEqual(self.provider.reads,reads)
            with closing(CheckoutStore(self.store.db.execute('PRAGMA database_list').fetchone()[2],now=lambda:self.now[0])) as reopened:
                backend=CheckoutBackend(reopened,self.provider,KEY,MERCHANT)
                backend.reconcile(self.oid,'PB001')
                self.assertEqual(self.provider.reads,reads)
            self.now[0]+=delay+1
        self.provider.outage=False
        result=self.backend.reconcile(self.oid,'PB001')
        self.assertTrue(result['reconciliation']['checked'])
        self.assertEqual(result['reconciliation']['retry_after'],10)

    def test_competing_workers_have_one_inflight_read_and_no_cached_permission(self):
        entered,release=threading.Event(),threading.Event()
        original=self.provider.get_status
        def slow(oid):
            entered.set(); release.wait(3); return original(oid)
        self.provider.get_status=slow
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as pool:
            first=pool.submit(self.backend.reconcile,self.oid,'PB001')
            try:
                self.assertTrue(entered.wait(1))
                duplicate=self.backend.reconcile(self.oid,'PB001')
                self.assertFalse(duplicate['reconciliation']['checked'])
                self.assertTrue(duplicate['verification_pending'])
            finally:
                release.set()
            self.assertTrue(first.result(3)['reconciliation']['checked'])

    def test_expired_worker_cannot_overwrite_newer_refund_evidence(self):
        self.paid()
        old=dict(self.provider.rows[self.oid])
        entered,release=threading.Event(),threading.Event()
        def slow(_oid):
            entered.set(); release.wait(3); return old
        from concurrent.futures import ThreadPoolExecutor
        with patch.object(self.provider,'get_status',side_effect=slow),ThreadPoolExecutor(max_workers=1) as pool:
            stale=pool.submit(self.backend.reconcile,self.oid,'PB001')
            try:
                self.assertTrue(entered.wait(1))
                refund=dict(old,transaction_status='refund')
                self.backend._apply(self.store.get(self.oid),refund)
            finally:
                release.set()
            result=stale.result(3)
        self.assertFalse(result['reconciliation']['checked'])
        self.assertEqual(result['state'],'REVIEW_REQUIRED')
        self.assertIsNone(result['grant_id'])

    def test_expired_reservation_is_fenced_after_a_new_worker_commits(self):
        old=self.store.begin_reconciliation(self.oid)
        self.now[0]+=46
        new=self.store.begin_reconciliation(self.oid)
        self.assertIsNotNone(new)
        evidence={'order_id':self.oid,'amount':15000,'merchant_id':MERCHANT,
                  'transaction_id':'txn-'+self.oid,'transaction_status':'refund'}
        self.assertTrue(self.store.finish_reconciliation(self.oid,new,evidence=evidence,outcome='review'))
        self.assertFalse(self.store.finish_reconciliation(self.oid,old,evidence=dict(evidence,transaction_status='settlement'),outcome='paid'))
        self.assertEqual(self.store.get(self.oid)['state'],'REVIEW_REQUIRED')

    def test_clock_rollback_holds_without_extending_deadline_indefinitely(self):
        self.backend.reconcile(self.oid,'PB001')
        self.now[0]-=300
        result=self.backend.reconcile(self.oid,'PB001')
        self.assertFalse(result['reconciliation']['checked'])
        self.assertEqual(result['reconciliation']['retry_after'],10)
        self.now[0]+=11
        self.assertTrue(self.backend.reconcile(self.oid,'PB001')['reconciliation']['checked'])

    def test_additive_scheduler_upgrade_preserves_existing_financial_bytes(self):
        self.paid()
        grant=self.backend.claim(self.oid,'PB001',self.key)['grant_id']
        before=self.store.get(self.oid)
        # Simulate the exact absence of the new additive table on upgrade.
        self.store.db.execute('DROP TABLE checkout_reconciliation')
        path=self.store.db.execute('PRAGMA database_list').fetchone()[2]
        with closing(CheckoutStore(path,now=lambda:self.now[0])) as upgraded:
            self.assertEqual(upgraded.get(self.oid),before)
            reservation=upgraded.begin_reconciliation(self.oid)
            self.assertIsNotNone(reservation)
            self.assertEqual(upgraded.get(self.oid)['grant_id'],grant)
