"""Real HTTP + service + SQLite integration and bounded-I/O regression."""
import asyncio
import hashlib
from pathlib import Path
import tempfile
import threading
import unittest
import httpx
from fastapi.testclient import TestClient
from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.qris_api import create_app, bounded_json
from test_checkout_backend import FakeProvider, KEY, MERCHANT

TOKEN = 'a' * 48
HEADERS = {'X-Booth-ID': 'PB001', 'Authorization': 'Bearer ' + TOKEN, 'Idempotency-Key': 'a' * 32}


class QrisHttpIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = CheckoutStore(Path(self.tmp.name) / 'store.db')
        self.provider = FakeProvider()
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        self.auth = BoothAuthenticator({'PB001': TOKEN, 'PB002': 'b' * 48})
        self.client = TestClient(create_app(self.backend, self.auth))

    def tearDown(self):
        self.client.close(); self.store.close(); self.tmp.cleanup()

    def create(self):
        response = self.client.post('/api/orders', json={'quantities': {'template_a': 2}}, headers=HEADERS)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()['order_id']

    def test_strict_input_rejects_coercion_and_overflow(self):
        for count in [True, '2', 1.0, 0, -1, 11]:
            with self.subTest(count=count):
                r = self.client.post('/api/orders', json={'quantities': {'template_a': count}}, headers=HEADERS)
                self.assertEqual(r.status_code, 422)
        self.assertEqual(self.provider.charges, 0)

    def test_key_required_before_checkout(self):
        headers = dict(HEADERS); headers.pop('Idempotency-Key')
        self.assertEqual(self.client.post('/api/orders', json={'quantities': {'template_a': 1}}, headers=headers).status_code, 422)

    def test_retry_poll_claim_and_service_lifecycle(self):
        oid = self.create(); self.assertEqual(self.create(), oid)
        self.provider.rows[oid].update(transaction_status='settlement', status_code='200')
        # Force the test's clock beyond the persisted poll throttle.
        self.store.db.execute('UPDATE checkouts SET check_after=0')
        self.assertEqual(self.client.get('/api/orders/' + oid, headers=HEADERS).json()['state'], 'PAID')
        a = self.client.post('/api/orders/' + oid + '/claim', headers=HEADERS).json()
        b = self.client.post('/api/orders/' + oid + '/claim', headers=HEADERS).json()
        self.assertEqual(a['grant_id'], b['grant_id'])
        for state in ['STARTED', 'STARTED', 'COMPLETED']:
            r = self.client.post('/api/orders/' + oid + '/service', headers=HEADERS,
                json={'grant_id': a['grant_id'], 'state': state, 'transaction_id': 'PB001_00000001'})
            self.assertEqual(r.status_code, 200)
        self.assertEqual(self.provider.charges, 1)

    def test_other_booth_cannot_read_or_claim(self):
        oid = self.create()
        headers = dict(HEADERS, **{'X-Booth-ID': 'PB002', 'Authorization': 'Bearer ' + 'b' * 48})
        self.assertEqual(self.client.get('/api/orders/' + oid, headers=headers).status_code, 404)
        self.assertEqual(self.client.post('/api/orders/' + oid + '/claim', headers=headers).status_code, 404)

    def test_unapplied_webhook_is_not_acknowledged(self):
        class Rejector:
            def process_notification(self, data): return False
        client = TestClient(create_app(Rejector(), self.auth))
        try: self.assertEqual(client.post('/api/webhooks/midtrans', json={}).status_code, 503)
        finally: client.close()

    def test_provider_outage_webhook_retry_then_success(self):
        oid = self.create()
        data = dict(order_id=oid, gross_amount='15000.00', status_code='200', transaction_status='settlement')
        data['signature_key'] = hashlib.sha512((oid + '20015000.00' + KEY).encode()).hexdigest()
        self.provider.outage = True
        self.assertEqual(self.client.post('/api/webhooks/midtrans', json=data).status_code, 503)
        self.provider.outage = False
        self.provider.rows[oid].update(transaction_status='settlement', status_code='200')
        self.assertEqual(self.client.post('/api/webhooks/midtrans', json=data).status_code, 200)

    def test_duplicate_json_member_is_rejected(self):
        self.assertEqual(self.client.post('/api/orders', content=b'{"quantities":{},"quantities":{}}', headers=HEADERS).status_code, 400)

    def test_rate_limit_is_bounded_and_explicit(self):
        client = TestClient(create_app(self.backend, self.auth, rate_limit=1))
        try:
            client.get('/api/orders/missing', headers=HEADERS)
            self.assertEqual(client.get('/api/orders/missing', headers=HEADERS).status_code, 429)
        finally: client.close()

    def test_status_reconciliation_runs_off_event_loop(self):
        started, release = threading.Event(), threading.Event()
        class SlowService:
            def status(self, *_):
                started.set(); release.wait(2); return {'state':'PENDING'}
        app = create_app(SlowService(), self.auth)
        async def scenario():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
                slow = asyncio.create_task(client.get('/api/orders/abc', headers=HEADERS))
                try:
                    self.assertTrue(await asyncio.to_thread(started.wait, 1))
                    health = await asyncio.wait_for(client.get('/api/health'), 0.5)
                    self.assertEqual(health.status_code, 200)
                finally:
                    release.set(); await slow
        asyncio.run(scenario())

    def test_chunked_body_stops_before_reading_whole_request(self):
        from fastapi import HTTPException
        class Stream:
            headers = {}
            count = 0
            async def stream(self):
                for _ in range(100):
                    self.count += 1
                    yield b'x' * 1024
        stream = Stream()
        async def run():
            with self.assertRaises(HTTPException) as caught: await bounded_json(stream, 2048)
            self.assertEqual(caught.exception.status_code, 413)
        asyncio.run(run())
        self.assertEqual(stream.count, 3)
