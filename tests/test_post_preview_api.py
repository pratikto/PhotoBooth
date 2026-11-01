"""Authenticated HTTP/SQLite/provider integration; synthetic money only."""
import asyncio
import hashlib
import threading
import unittest
from dataclasses import replace
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from photobooth.booth_auth import BoothAuthenticator
from photobooth.post_preview_api import create_app
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_inbox import PostPreviewNotificationInbox
from photobooth.post_preview_store import DraftHeld, PostPreviewStore
from tests import test_post_preview_payments as payment_fixtures

TOKEN = 'SYNTHETIC-BOOTH-ONLY-'+'a'*32
HEADERS = {'X-Booth-ID': 'PB001', 'Authorization': 'Bearer '+TOKEN}


class PostPreviewApiTests(unittest.TestCase):
    def setUp(self):
        self.fixture = payment_fixtures.PostPreviewPaymentTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.service = self.fixture.service
        self.ledger, self.group = self.fixture.ledger, self.fixture.group
        self.auth = BoothAuthenticator({'PB001': TOKEN, 'PB002': 'b'*48})
        self.inbox = PostPreviewNotificationInbox(self.service)
        self.app = create_app(self.service, self.auth, inbox=self.inbox)
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)
        self.path = '/api/postpay/groups/'+self.group
        self.owner = {'visit_id': self.fixture.lease.visit_id, 'generation': self.fixture.lease.generation}

    def post(self, action, data=None, headers=HEADERS):
        return self.client.post(self.path+'/'+action, json=self.owner if data is None else data, headers=headers)

    def begin(self):
        self.fixture.offered()
        response = self.post('begin')
        self.assertEqual(200, response.status_code)
        return response.json()

    def notification(self, **changes):
        order = self.fixture.order()
        data = dict(order_id=order, gross_amount='10000.00', status_code='200', transaction_status='settlement')
        data.update(changes)
        data['signature_key'] = hashlib.sha512((data['order_id']+data['status_code']+data['gross_amount']+self.fixture.key).encode()).hexdigest()
        return data

    def webhook(self, data):
        return self.client.post('/api/postpay/webhooks/midtrans', json=data)

    def test_booth_authentication_and_scope_precede_provider_calls(self):
        self.assertEqual(401, self.post('begin', headers={}).status_code)
        other = {'X-Booth-ID': 'PB002', 'Authorization': 'Bearer '+'b'*48}
        self.assertEqual(409, self.post('begin', headers=other).status_code)
        self.assertEqual(409, self.post('begin', dict(self.owner, visit_id='visitB')).status_code)
        self.assertEqual(409, self.post('begin', dict(self.owner, generation=2)).status_code)
        self.assertEqual(0, self.fixture.provider.charges)

    def test_strict_input_does_not_accept_amount_or_evidence_or_echo_credentials(self):
        for extra in ({'amount': 1}, {'paid': True}, {'ready': True}, {'qr_url': 'http://attacker'}, {'server_key': 'secret-fixture'}):
            r = self.post('begin', dict(self.owner, **extra))
            self.assertEqual(422, r.status_code)
            self.assertNotIn('secret-fixture', r.text)
        for generation in (True, '1', 1.0, 0):
            self.assertEqual(422, self.post('begin', dict(self.owner, generation=generation)).status_code)
        self.assertEqual(0, self.fixture.provider.charges)

    def test_duplicate_large_or_malformed_json_fails_before_charge(self):
        for body, status in ((b'{"generation":1,"generation":2}',400), (b'x'*16385,413), (b'[1]',400)):
            r = self.client.post(self.path+'/begin', content=body, headers=HEADERS)
            self.assertEqual(status, r.status_code)
        self.assertEqual(0, self.fixture.provider.charges)

    def test_original_begin_replay_and_fresh_paid_are_financial_only(self):
        first = self.begin()
        second = self.post('begin').json()
        self.assertEqual(first['attempts'], second['attempts'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.fixture.provider.state(self.fixture.order(), 'settlement')
        paid = self.post('reconcile', {'trigger': 'connectivity'}).json()
        self.assertTrue(paid['paid_verified'])
        self.assertFalse(paid['fulfillment_authorized'])
        cached = self.client.get(self.path, headers=HEADERS).json()
        self.assertFalse(cached['paid_verified'])
        self.assertFalse(cached['fresh_checked'])
        self.assertEqual(paid['entitlement_id'], cached['entitlement_id'])
        self.assertEqual('post_preview_v1', cached['order_version'])

    def test_only_expired_explicit_original_continuation_creates_qr2(self):
        self.begin()
        self.fixture.provider.state(self.fixture.order(), 'expire')
        self.assertEqual(409, self.post('continue', dict(self.owner, actively_continuing=False)).status_code)
        self.assertEqual(422, self.post('continue', dict(self.owner, actively_continuing='true')).status_code)
        r = self.post('continue', dict(self.owner, actively_continuing=True))
        self.assertEqual(200, r.status_code)
        self.assertEqual(2, len(r.json()['attempts']))

    def test_lifecycle_distinguishes_suspension_from_cancellation(self):
        self.begin()
        r = self.post('lifecycle', dict(self.owner, event='APP_SUSPENDED'))
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, self.fixture.provider.cancels)
        self.assertIsNone(r.json()['qr_url'])
        self.assertEqual(409, self.post('begin').status_code)

    def test_webhook_ack_is_durable_deduplicated_and_contains_no_provider_get(self):
        self.begin()
        data = self.notification()
        before = self.fixture.provider.reads
        for _ in range(2):
            self.assertEqual(200, self.webhook(data).status_code)
        self.assertEqual(before, self.fixture.provider.reads)
        self.assertEqual(1, self.ledger.db.execute('SELECT count(*) FROM pp_notification_inbox').fetchone()[0])
        self.assertEqual('PENDING', self.service.inspect(self.group, 'PB001')['state'])
        # Signed "settlement" cannot override independent pending provider status.
        self.assertTrue(self.inbox.process_one())
        self.assertEqual('PENDING', self.service.inspect(self.group, 'PB001')['state'])
        self.assertEqual('APPLIED', self.ledger.db.execute('SELECT state FROM pp_notification_inbox').fetchone()[0])
        for row in self.ledger.db.execute('SELECT * FROM pp_notification_inbox'):
            self.assertNotIn(data['signature_key'], str(tuple(row)))

    def test_invalid_signature_or_amount_cannot_allocate_inbox(self):
        self.begin()
        data = self.notification(); data['signature_key'] = '0'*128
        self.assertEqual(400, self.webhook(data).status_code)
        self.assertEqual(400, self.webhook(self.notification(gross_amount='1.00')).status_code)
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_notification_inbox').fetchone()[0])

    def test_outage_after_ack_retries_after_restart_then_independently_settles(self):
        self.begin()
        self.assertEqual(200, self.webhook(self.notification()).status_code)
        self.fixture.provider.outage = True
        self.inbox.process_one()
        self.assertEqual('RETRY', self.ledger.db.execute('SELECT state FROM pp_notification_inbox').fetchone()[0])
        self.fixture.fixture.clock[0] += 11
        self.fixture.provider.outage = False
        self.fixture.provider.state(self.fixture.order(), 'settlement')
        restarted = PostPreviewNotificationInbox(self.service)
        restarted.process_one()
        self.assertEqual('PAID_LIVE', self.service.inspect(self.group, 'PB001')['state'])

    def test_lease_reclaim_rejects_late_worker_completion(self):
        self.begin(); self.webhook(self.notification())
        first = self.inbox.claim()
        self.fixture.fixture.clock[0] += 46
        second = self.inbox.claim()
        self.assertNotEqual(first['token'], second['token'])
        self.assertFalse(self.inbox.finish(first, True))
        self.assertTrue(self.inbox.finish(second, True))

    def test_failed_notifications_quarantine_bounded_and_capacity_fails_closed(self):
        self.begin(); self.webhook(self.notification())
        self.fixture.provider.outage = True
        for _ in range(5):
            self.inbox.process_one()
            self.fixture.fixture.clock[0] += 61
        self.assertEqual('QUARANTINED', self.ledger.db.execute('SELECT state FROM pp_notification_inbox').fetchone()[0])
        bounded = PostPreviewNotificationInbox(self.service, capacity=1)
        with self.assertRaises(RuntimeError):
            bounded.accept(self.notification(transaction_status='pending'))

    def test_missing_inbox_on_current_schema_holds_without_recreation(self):
        self.ledger.db.execute('DROP TABLE pp_notification_inbox')
        with self.assertRaises(DraftHeld):
            PostPreviewStore(self.fixture.fixture.root/'drafts.db')

    def test_additive_v4_inbox_upgrade_preserves_original_finance(self):
        before = self.begin()
        self.ledger.db.execute('DROP TABLE pp_notification_inbox')
        self.ledger.db.execute('UPDATE pp_schema SET version=4')
        other = PostPreviewStore(self.fixture.fixture.root/'drafts.db')
        self.addCleanup(other.close)
        self.assertEqual(5, other.db.execute('SELECT version FROM pp_schema').fetchone()[0])
        row = other.db.execute('SELECT * FROM pp_payment_attempts').fetchone()
        self.assertEqual(before['attempts'][0]['attempt_id'], row['attempt_id'])
        self.assertEqual('PENDING', row['payment_state'])

    def test_partial_current_inbox_schema_fails_closed(self):
        self.ledger.db.execute('ALTER TABLE pp_notification_inbox RENAME COLUMN token TO damaged_token')
        with self.assertRaises(DraftHeld):
            PostPreviewStore(self.fixture.fixture.root/'drafts.db')

    def test_provider_call_cannot_block_health_event_loop(self):
        started, release = threading.Event(), threading.Event()
        self.fixture.offered()
        self.fixture.provider.create_entered = started
        self.fixture.provider.create_release = release
        async def scenario():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url='http://test') as client:
                pending = asyncio.create_task(client.post(self.path+'/begin', json=self.owner, headers=HEADERS))
                try:
                    await asyncio.wait_for(asyncio.to_thread(started.wait, 2), 3)
                    health = await asyncio.wait_for(client.get('/api/postpay/health'), 1)
                    self.assertEqual(200, health.status_code)
                finally:
                    release.set()
                    self.assertEqual(200, (await pending).status_code)
        asyncio.run(scenario())

    def test_client_reuses_bounded_transport_and_rejects_scope_mode_or_authority(self):
        view = self.begin()
        client = PostPreviewClient('https://example.invalid', 'PB001', TOKEN, expected_mode='mock')
        self.addCleanup(client.close)
        with patch.object(client._transport, '_call', return_value=view) as call:
            self.assertEqual(view, client.begin(self.group, self.fixture.lease))
            self.assertEqual(self.path+'/begin', call.call_args.args[1])
            self.assertEqual(self.owner, call.call_args.kwargs['payload'])
        for change in ({'booth_id':'PB002'}, {'mode':'sandbox'}, {'fulfillment_authorized':True}, {'paid_verified':'true'}, {'amount':True}):
            with patch.object(client._transport, '_call', return_value=dict(view, **change)):
                with self.assertRaises(ValueError): client.inspect(self.group)
        with self.assertRaises(ValueError): client.inspect('../escape')

    def test_rate_limit_is_explicit_and_legacy_routes_are_absent(self):
        client = TestClient(create_app(self.service, self.auth, rate_limit=1))
        self.addCleanup(client.close)
        self.assertEqual(200, client.get(self.path, headers=HEADERS).status_code)
        self.assertEqual(429, client.get(self.path, headers=HEADERS).status_code)
        self.assertEqual(404, self.client.post('/api/orders', json={}, headers=HEADERS).status_code)
