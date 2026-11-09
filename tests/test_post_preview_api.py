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

    def test_result_timeout_preserves_paid_entitlement_without_cancel_or_release(self):
        self.begin()
        self.fixture.provider.state(self.fixture.order(), 'settlement')
        paid = self.post('reconcile', {'trigger': 'connectivity'}).json()
        response = self.post('lifecycle', dict(self.owner, event='RESULT_TIMEOUT'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, self.fixture.provider.cancels)
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(paid['entitlement_id'], response.json()['entitlement_id'])
        row = self.ledger.db.execute('SELECT lifecycle,closed FROM pp_drafts').fetchone()
        self.assertEqual(('RESULT_TIMEOUT', 0), tuple(row))
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
        for table in ('pp_paid_strip_jobs','pp_paid_services','pp_ticket_presentations','pp_ticket_credentials'):
            self.ledger.db.execute('DROP TABLE '+table)
        self.ledger.db.execute('DROP TABLE pp_notification_inbox')
        self.ledger.db.execute('UPDATE pp_schema SET version=4')
        other = PostPreviewStore(self.fixture.fixture.root/'drafts.db')
        self.addCleanup(other.close)
        self.assertEqual(8, other.db.execute('SELECT version FROM pp_schema').fetchone()[0])
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


class SandboxBackendAssemblyTests(unittest.TestCase):
    """Actual PP API/transport; Linux OS adapter is explicitly fixture plumbing."""
    def setUp(self):
        import os
        import socket
        from types import SimpleNamespace
        from unittest.mock import patch
        from photobooth.booth_storage import BoothWorkspace
        from photobooth.credential_vault import (
            WindowsDPAPIProtector, ProtectedCredential, SyntheticAeadProtector,
            VaultUnavailable, platform_protector)
        from photobooth.post_preview_checkout import PrivateDraftCheckout
        from photobooth.post_preview_photos import PrivateDraftPhotos
        from photobooth.post_preview_readiness import ReadOnlyDriveReadiness
        from photobooth.post_preview_readiness_bridge import WorkerReadinessClient, WorkerReadinessServer
        from photobooth.post_preview_server import build_sandbox_app
        from tests import test_post_preview_ccp as ccp_cases
        from tests import test_post_preview_payments as payment_cases
        from tests.test_post_preview_readiness import _bridge_ready
        self.fixture = ccp_cases.OriginalCCPTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.ledger, self.lease = self.fixture.ledger, self.fixture.lease
        self.group = self.fixture.intent['purchase_group_id']
        self.clock = self.fixture.clock
        if os.name == 'nt':
            self.protector = platform_protector()  # Actual current-user DPAPI on Windows CI.
        else:
            # Fixture only: exercise assembly/control flow without claiming OS
            # protection on Linux. The production factory has no such opt-in.
            synthetic = SyntheticAeadProtector(os.urandom(32), fixture=True)
            self.protector = object.__new__(WindowsDPAPIProtector)
            self.protector.protect = lambda value, scope: ProtectedCredential(
                self.protector.protector_id, synthetic.protect(value, scope).ciphertext)
            def unprotect(envelope, scope):
                if envelope.protector_id != self.protector.protector_id:
                    raise VaultUnavailable('Original OS protector is unavailable')
                return synthetic.unprotect(ProtectedCredential(synthetic.protector_id, envelope.ciphertext), scope)
            self.protector.unprotect = unprotect
        self.fixture.service.protector = self.protector
        offer = self.fixture.offer()
        self.fixture.service.mark_visible(self.lease, offer)
        self.checkout = PrivateDraftCheckout(PrivateDraftPhotos(self.ledger, self.fixture.root/'private'))
        self.templates = __import__('photobooth.catalog', fromlist=['get_templates']).get_templates()
        self.workspace = BoothWorkspace(self.fixture.root/'storage', 'PB001V2S2')
        self.workspace.prepare()
        drive = SimpleNamespace(booth_id='PB001V2S2', storage_readiness=lambda slots: {
            'drive_api':'READY','drive_sharing':'READY','capacity_state':'READY'})
        self.drive = ReadOnlyDriveReadiness(drive, self.workspace, now=self.ledger.now)
        backend, worker = socket.socketpair()
        self.server = WorkerReadinessServer(worker, lambda scope: _bridge_ready(scope, self.clock[0]))
        self.server.start()
        self.bridge = WorkerReadinessClient(backend, timeout=2)
        self.addCleanup(self.server.stop)
        self.addCleanup(self.bridge.close)
        self.remote = payment_cases.SyntheticProvider()
        self.requests = []
        self.create_reports_paid = False
        self.transport = payment_cases.MidtransPostPreviewContractTests.transport.__get__(self)
        self.key = 'SB-Mid-server-SYNTHETIC-NOT-A-MERCHANT'
        self.token = 'SYNTHETIC-BOOTH-'+('a'*48)
        self.factory_args = dict(merchant_id='MTEST', server_key=self.key,
                                booth_id='PB001', booth_token=self.token,
                                provider_transport=self.transport, background_worker=False)
        with patch('photobooth.post_preview_server.platform_protector', return_value=self.protector):
            self.app = build_sandbox_app(self.checkout, self.templates, self.bridge, self.drive,
                                         **self.factory_args)
        self.http = TestClient(self.app)
        self.http.__enter__()
        self.addCleanup(self.http.__exit__, None, None, None)
        self.headers = {'X-Booth-Id':'PB001','Authorization':'Bearer '+self.token}

    def call(self, suffix, payload=None):
        body = payload if payload is not None else {
            'visit_id':self.lease.visit_id,'generation':self.lease.generation}
        return self.http.post('/api/postpay/groups/'+self.group+suffix,
                              headers=self.headers, json=body)

    @staticmethod
    def order(view):
        return view['attempts'][-1]['provider_order_id']

    def test_factory_has_no_io_and_no_legacy_or_synthetic_paid_endpoint(self):
        self.assertEqual([], self.requests)
        response = self.http.get('/api/postpay/health')
        self.assertEqual('sandbox', response.json()['mode'])
        self.assertFalse(response.json()['fulfillment_enabled'])
        for path in ('/api/orders', '/api/postpay/simulate-paid'):
            self.assertEqual(404, self.http.post(path).status_code)
        self.assertNotIn(self.key, response.text)
        self.assertNotIn(self.token, response.text)
        denied = self.http.post('/api/postpay/groups/'+self.group+'/begin', json={})
        self.assertEqual(401, denied.status_code)
        self.assertEqual([], self.requests)

    def test_authentic_original_charge_requires_independent_get_and_grants_once(self):
        self.create_reports_paid = True
        first = self.call('/begin').json()
        self.assertEqual('PENDING', first['state'])
        self.assertIsNone(first['entitlement_id'])
        self.remote.state(self.order(first), 'settlement')
        self.clock[0] += 10
        paid = self.call('/reconcile', {'trigger':'connectivity'}).json()
        self.assertEqual(('PAID_LIVE', 'OWED'), (paid['state'], paid['obligation_state']))
        self.assertTrue(paid['paid_verified'])
        self.assertFalse(paid['fulfillment_authorized'])
        self.clock[0] += 10
        again = self.call('/reconcile', {'trigger':'connectivity'}).json()
        self.assertEqual(paid['entitlement_id'], again['entitlement_id'])
        self.assertEqual(1, self.remote.charges)

    def test_corrupt_original_escrow_before_charge_holds_without_reissuing(self):
        self.ledger.db.execute("UPDATE pp_ccp_credentials SET ciphertext=?", (b'corrupt',))
        before = list(self.ledger.db.execute('SELECT * FROM pp_events'))
        self.assertEqual(503, self.call('/begin').status_code)
        self.assertEqual([], self.requests)
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_payment_attempts').fetchone()[0])
        self.assertEqual(before, list(self.ledger.db.execute('SELECT * FROM pp_events')))
        self.assertEqual(1, self.ledger.db.execute('SELECT count(*) FROM pp_ccp_credentials').fetchone()[0])

    def test_lost_create_http404_then_escrow_fault_still_reconciles_original(self):
        self.remote.lost_create = True
        self.remote.not_found = 1
        first = self.call('/begin').json()
        self.assertEqual('UNKNOWN', first['state'])
        original = self.order(first)
        self.ledger.db.execute('UPDATE pp_ccp_credentials SET ciphertext=?', (b'corrupt',))
        self.clock[0] += 10
        recovered = self.call('/begin').json()
        self.assertEqual('PENDING', recovered['state'])
        self.assertEqual(original, self.order(recovered))
        self.remote.state(original, 'settlement')
        self.clock[0] += 10
        paid = self.call('/reconcile', {'trigger':'connectivity'}).json()
        self.assertEqual('OWED', paid['obligation_state'])
        self.assertEqual(1, self.remote.charges)
        self.assertEqual([('POST','/v2/charge')], [r for r in self.requests if r[1]=='/v2/charge'])

    def test_expiry_late_and_duplicate_settlement_share_one_original_entitlement(self):
        first = self.call('/begin').json()
        self.remote.state(self.order(first), 'expire')
        self.clock[0] += 10
        owner = {'visit_id':self.lease.visit_id,'generation':self.lease.generation,
                 'actively_continuing':True}
        second = self.call('/continue', owner).json()
        self.assertEqual(2, len(second['attempts']))
        self.remote.state(self.order(first), 'settlement')
        self.clock[0] += 10
        original_paid = self.call('/reconcile', {'trigger':'connectivity'}).json()
        self.remote.state(self.order(second), 'settlement')
        self.clock[0] += 10
        excess = self.call('/reconcile', {'trigger':'connectivity'}).json()
        self.assertEqual(original_paid['entitlement_id'], excess['entitlement_id'])
        self.assertEqual(1, len(excess['excess_paid_attempts']))
        self.assertEqual('OWED', excess['obligation_state'])
        self.assertEqual(2, self.remote.charges)
        self.assertFalse(excess['fulfillment_authorized'])

    def test_cancel_late_paid_is_original_unclaimed_owed_without_replacement(self):
        first = self.call('/begin').json()
        self.clock[0] += 10
        cancelled = self.call('/lifecycle', {'visit_id':self.lease.visit_id,
            'generation':self.lease.generation,'event':'USER_CANCEL'}).json()
        self.assertEqual('CANCELLED_UNPAID', cancelled['state'])
        self.remote.state(self.order(first), 'settlement')
        self.clock[0] += 10
        paid = self.call('/reconcile', {'trigger':'connectivity'}).json()
        self.assertEqual(('PAID_UNCLAIMED','OWED'), (paid['state'],paid['obligation_state']))
        self.assertEqual(1, self.remote.charges)
        self.assertEqual(1, self.remote.cancels)

    def test_foreign_or_synthetic_ledger_is_refused_before_provider_io(self):
        from unittest.mock import patch
        from photobooth.post_preview_server import build_sandbox_app
        from photobooth.post_preview_store import DraftHeld
        for sql, value in (("UPDATE pp_ccp_credentials SET merchant_id=?", 'OTHER'),
                           ("UPDATE pp_ccp_credentials SET protector_id=?", 'synthetic-aesgcm-fixture-v1')):
            with self.subTest(change=sql):
                self.ledger.db.execute(sql, (value,))
                with patch('photobooth.post_preview_server.platform_protector', return_value=self.protector), self.assertRaises(DraftHeld):
                    build_sandbox_app(self.checkout, self.templates, self.bridge, self.drive, **self.factory_args)
                self.ledger.db.execute('UPDATE pp_ccp_credentials SET merchant_id=?,protector_id=?',
                                       ('MTEST',self.protector.protector_id))
        self.assertEqual([], self.requests)

    def test_missing_platform_custody_has_no_synthetic_fallback(self):
        from unittest.mock import patch
        from photobooth.credential_vault import VaultUnavailable
        from photobooth.post_preview_server import build_sandbox_app
        with patch('photobooth.post_preview_server.platform_protector', side_effect=VaultUnavailable('Unsupported OS')), self.assertRaises(VaultUnavailable):
            build_sandbox_app(self.checkout, self.templates, self.bridge, self.drive, **self.factory_args)
        self.assertEqual([], self.requests)

    def test_lost_worker_or_drive_health_cannot_be_replaced_by_caller_flags(self):
        self.bridge.close()
        response = self.call('/begin')
        self.assertEqual(409, response.status_code)
        self.assertEqual([], self.requests)
        forged = self.call('/begin', {'visit_id':self.lease.visit_id,
            'generation':self.lease.generation, 'ready':True, 'paid':True})
        self.assertEqual(422, forged.status_code)
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_payment_attempts').fetchone()[0])

    def test_backend_drive_failure_holds_even_with_healthy_original_worker(self):
        self.drive.client.storage_readiness = lambda slots: {
            'drive_api':'READY','drive_sharing':'NOT_READY','capacity_state':'NOT_READY'}
        self.assertEqual(409, self.call('/begin').status_code)
        self.assertEqual([], self.requests)
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_payment_attempts').fetchone()[0])


if __name__ == '__main__': unittest.main()
