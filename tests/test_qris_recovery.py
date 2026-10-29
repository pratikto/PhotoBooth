"""Sandbox operator recovery through the real HTTP/client/SQLite boundary.

All provider responses are fixtures. No PIN, merchant key or bearer is logged.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore, CheckoutConflict
from photobooth.qris_api import create_app
from photobooth.qris_kiosk_client import QrisKioskClient
from tests.test_checkout_backend import FakeProvider, KEY, MERCHANT


PIN = '12578934'
TOKEN = 'a' * 48
HEADERS = {'X-Booth-ID':'PB001', 'Authorization':'Bearer '+TOKEN,
           'Idempotency-Key':'a'*32}
OPERATOR = dict(HEADERS, **{'X-Recovery-PIN':PIN})


class SandboxProvider(FakeProvider):
    mode = 'sandbox'


class ClientResponse:
    def __init__(self, response):
        self.response, self.status_code = response, response.status_code
    def iter_content(self, size):
        yield self.response.content
    def close(self):
        self.response.close()


class InProcessSession:
    def __init__(self, client):
        self.client = client
        self.last_headers = None
    def request(self, method, url, **kwargs):
        kwargs.pop('stream'); kwargs.pop('allow_redirects')
        self.last_headers = dict(kwargs['headers'])
        return ClientResponse(self.client.request(method, url, **kwargs))
    def close(self):
        pass


class SandboxRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CheckoutStore(Path(self.temp.name)/'orders.sqlite')
        self.provider = SandboxProvider()
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        self.auth = BoothAuthenticator({'PB001':TOKEN, 'PB002':'b'*48})
        self.app = create_app(self.backend, self.auth, recovery_pin=PIN)
        self.http = TestClient(self.app)
        response = self.http.post('/api/orders', headers=HEADERS,
                                  json={'quantities':{'template_a':1}})
        self.assertEqual(response.status_code, 201)
        self.oid = response.json()['order_id']
        self.session = InProcessSession(self.http)
        self.client = QrisKioskClient('http://127.0.0.1:8000', 'PB001', TOKEN,
                                      allow_local_http=True, session=self.session)

    def tearDown(self):
        self.http.close(); self.store.close(); self.temp.cleanup()

    def inspect(self, **headers):
        return self.http.post('/api/orders/'+self.oid+'/recovery/inspect',
                              headers=dict(OPERATOR, **headers))

    def resolve(self, action, *, action_id='b'*32, reason='Operator resumes test', transaction_id=None):
        return self.http.post('/api/orders/'+self.oid+'/recovery/resolve', headers=OPERATOR,
            json={'action_id':action_id, 'action':action, 'reason':reason,
                  'transaction_id':transaction_id})

    def paid(self):
        self.provider.rows[self.oid].update(transaction_status='settlement', status_code='200')
        response = self.inspect()
        self.assertEqual(response.status_code, 200)
        return response.json()

    def count_actions(self):
        return self.store.db.execute('SELECT COUNT(*) FROM checkout_recovery_actions').fetchone()[0]

    def test_recovery_is_disabled_without_explicit_pin_or_sandbox_provider(self):
        with TestClient(create_app(self.backend, self.auth)) as http:
            self.assertEqual(http.post('/api/orders/'+self.oid+'/recovery/inspect', headers=OPERATOR).status_code, 404)
        for mode in ('mock', 'production'):
            self.provider.mode = mode
            self.assertEqual(self.inspect().status_code, 404)
        self.assertEqual(self.provider.reads, 0)

    def test_pin_and_booth_credentials_are_both_required(self):
        for headers in (HEADERS, dict(OPERATOR, **{'Authorization':'Bearer wrong'}),
                        dict(OPERATOR, **{'X-Recovery-PIN':'00000000'})):
            response = self.http.post('/api/orders/'+self.oid+'/recovery/inspect', headers=headers)
            self.assertEqual(response.status_code, 401)
            self.assertNotIn(PIN, response.text)
        self.assertEqual(self.provider.reads, 0)
        other = dict(OPERATOR, **{'X-Booth-ID':'PB002', 'Authorization':'Bearer '+'b'*48})
        self.assertEqual(self.http.post('/api/orders/'+self.oid+'/recovery/inspect', headers=other).status_code, 404)

    def test_independent_pin_attempt_limit_cannot_block_regular_status(self):
        for _ in range(8):
            self.assertEqual(self.inspect(**{'X-Recovery-PIN':'00000000'}).status_code, 401)
        self.assertEqual(self.inspect().status_code, 429)
        self.assertEqual(self.http.get('/api/orders/'+self.oid, headers=HEADERS).status_code, 200)

    def test_all_operator_routes_persist_pin_and_rate_denials_without_request_data(self):
        for route in ('inspect', 'resolve', 'release'):
            with TestClient(create_app(self.backend, self.auth, recovery_pin=PIN)) as http:
                url = '/api/orders/' + self.oid + '/recovery/' + route
                for _ in range(8):
                    response = http.post(url, headers=dict(OPERATOR, **{'X-Recovery-PIN':'00000000'}),
                                         content=b'private-unparsed-ticket')
                    self.assertEqual(response.status_code, 401)
                self.assertEqual(http.post(url, headers=OPERATOR).status_code, 429)
        rows = [dict(r) for r in self.store.db.execute('SELECT * FROM checkout_operator_denials')]
        self.assertEqual(len(rows), 27)
        for route in ('inspect', 'resolve', 'release'):
            self.assertEqual(sum(r['route']==route and r['reason']=='INVALID_PIN' for r in rows), 8)
            self.assertEqual(sum(r['route']==route and r['reason']=='RATE_LIMITED' for r in rows), 1)
        encoded = json.dumps(rows)
        for secret in (PIN, TOKEN, self.oid, '00000000', 'private-unparsed-ticket'):
            self.assertNotIn(secret, encoded)
        self.assertEqual(self.provider.reads, 0)
        self.assertEqual(self.count_actions(), 0)

    def test_pin_audit_failure_returns_generic_unavailable_without_authority(self):
        from unittest.mock import patch
        before = self.store.get(self.oid)
        for route in ('inspect', 'resolve', 'release'):
            with patch.object(self.store, 'record_operator_denial', side_effect=OSError('private-secret-path')):
                response = self.http.post('/api/orders/'+self.oid+'/recovery/'+route,
                    headers=dict(OPERATOR, **{'X-Recovery-PIN':'00000000'}))
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('private-secret-path', response.text)
        self.assertEqual(self.provider.reads, 0)
        self.assertEqual(self.store.get(self.oid), before)

    def test_rate_audit_failure_does_not_block_ordinary_status_or_unlock_operator(self):
        from unittest.mock import patch
        for _ in range(8):
            self.assertEqual(self.inspect(**{'X-Recovery-PIN':'00000000'}).status_code, 401)
        with patch.object(self.store, 'record_operator_denial', side_effect=OSError('private-storage')):
            self.assertEqual(self.inspect().status_code, 503)
        self.assertEqual(self.inspect().status_code, 429)
        self.assertEqual(self.http.get('/api/orders/'+self.oid, headers=HEADERS).status_code, 200)

    def test_pin_denial_survives_reopen_and_pre_auth_requests_do_not_write_it(self):
        self.assertEqual(self.inspect(**{'Authorization':'Bearer wrong'}).status_code, 401)
        with TestClient(create_app(self.backend, self.auth)) as http:
            self.assertEqual(http.post('/api/orders/'+self.oid+'/recovery/inspect', headers=OPERATOR).status_code, 404)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM checkout_operator_denials').fetchone()[0], 0)
        self.assertEqual(self.inspect(**{'X-Recovery-PIN':'00000000'}).status_code, 401)
        self.http.close(); self.store.close()
        self.store = CheckoutStore(Path(self.temp.name)/'orders.sqlite')
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        self.http = TestClient(create_app(self.backend, self.auth, recovery_pin=PIN))
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM checkout_operator_denials').fetchone()[0], 1)

    def test_inspection_rechecks_cached_paid_and_detects_refund(self):
        self.paid()
        reads = self.provider.reads
        self.provider.rows[self.oid].update(transaction_status='refund')
        result = self.inspect().json()
        self.assertEqual(self.provider.reads, reads+1)
        self.assertTrue(result['recovery_checked'])
        self.assertEqual(result['recovery_provider_state'], 'refund')
        self.assertEqual(result['state'], 'REVIEW_REQUIRED')
        self.assertEqual(self.resolve('resume').status_code, 409)
        self.assertEqual(self.count_actions(), 0)

    def test_provider_failure_blocks_decision_and_leaves_original_visit(self):
        self.paid(); before = self.store.get(self.oid)
        self.provider.outage = True
        self.assertEqual(self.inspect().status_code, 503)
        self.assertEqual(self.resolve('abandon').status_code, 503)
        self.assertEqual(self.count_actions(), 0)
        self.assertEqual(self.store.get(self.oid), before)

    def test_resume_without_allocation_reuses_one_grant_and_audits_once(self):
        self.paid()
        first = self.resolve('resume').json()
        retry = self.resolve('resume').json()
        self.assertEqual(first['grant_id'], retry['grant_id'])
        self.assertEqual(retry['service_state'], 'RESERVED')
        self.assertEqual(self.count_actions(), 1)
        self.assertEqual(first['recovery_action'], retry['recovery_action'])
        self.assertEqual(retry['recovery_action']['prior_service_state'], 'NONE')
        self.assertNotIn(PIN, json.dumps(retry))
        self.assertEqual(self.provider.charges, 1)

    def test_changed_action_payload_or_order_cannot_reuse_old_action_id(self):
        self.paid(); self.assertEqual(self.resolve('resume').status_code, 200)
        self.assertEqual(self.resolve('abandon').status_code, 409)
        self.assertEqual(self.resolve('resume', reason='Changed reason').status_code, 409)
        self.assertEqual(self.count_actions(), 1)

    def test_resume_reattaches_same_transaction_and_never_starts_another(self):
        self.paid(); self.resolve('resume')
        first = self.resolve('resume', action_id='c'*32, transaction_id='PB001_00000001')
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()['local_transaction_id'], 'PB001_00000001')
        self.assertEqual(first.json()['service_state'], 'STARTED')
        self.assertEqual(self.resolve('resume', action_id='d'*32, transaction_id='PB001_00000002').status_code, 409)
        self.assertEqual(self.resolve('resume', action_id='e'*32).status_code, 409)

    def test_abandon_preserves_paid_service_and_unblocks_next_booth_visit(self):
        self.paid(); self.resolve('resume')
        before = self.store.get(self.oid)
        response = self.resolve('abandon', action_id='c'*32)
        self.assertEqual(response.status_code, 200)
        view = response.json()
        self.assertTrue(view['closed']); self.assertTrue(view['recovery_abandoned'])
        self.assertEqual(view['state'], 'PAID')
        self.assertEqual(view['service_state'], 'RESERVED')
        self.assertEqual(view['grant_id'], before['grant_id'])
        new, _ = self.store.begin('PB001', {'template_a':1}, 10000, 'z'*32)
        self.assertNotEqual(new['id'], self.oid)
        with self.assertRaises(CheckoutConflict):
            self.store.grant(self.oid, 'PB001', 'a'*32)
        with self.assertRaises(CheckoutConflict):
            self.store.service_transition(self.oid, 'PB001', before['grant_id'], 'STARTED', 'PB001_00000001')
        retry = self.resolve('abandon', action_id='c'*32)
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(retry.json()['order_id'], self.oid)
        self.assertEqual(self.store.get(new['id'])['state'], 'CREATED')

    def test_pending_abandon_hides_qr_without_faking_a_provider_cancellation(self):
        response = self.resolve('abandon')
        self.assertEqual(response.status_code, 200)
        view = response.json()
        self.assertEqual(view['state'], 'PENDING')
        self.assertEqual(view['service_state'], 'NONE')
        self.assertTrue(view['closed']); self.assertTrue(view['recovery_abandoned'])
        self.assertIsNone(view['qr_url'])
        self.assertEqual(self.provider.rows[self.oid]['transaction_status'], 'pending')

    def test_concurrent_resolution_has_one_grant_and_one_audit_record(self):
        self.paid()
        def resume(index):
            return self.backend.recovery_resolve(self.oid, 'PB001', 'b'*32, 'resume',
                                                 'Operator resumes test', None, 'operator-'+str(index))
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(resume, range(8)))
        self.assertEqual(len({x['grant_id'] for x in results}), 1)
        self.assertEqual(len({x['recovery_action']['actor'] for x in results}), 1)
        self.assertEqual(self.count_actions(), 1)

    def test_old_success_replay_returns_current_refund_state_without_new_permission(self):
        self.paid(); first = self.resolve('resume').json()
        self.provider.rows[self.oid].update(transaction_status='refund')
        retry = self.resolve('resume')
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(retry.json()['state'], 'REVIEW_REQUIRED')
        self.assertEqual(retry.json()['recovery_action'], first['recovery_action'])
        self.assertEqual(self.count_actions(), 1)
        self.assertEqual(self.resolve('resume', action_id='c'*32).status_code, 409)

    def test_completion_requires_same_started_transaction_and_cannot_be_replayed_as_capture(self):
        self.paid(); self.resolve('resume')
        self.resolve('resume', action_id='c'*32, transaction_id='PB001_00000001')
        self.assertEqual(self.resolve('complete', action_id='d'*32, transaction_id='PB001_00000002').status_code, 409)
        result = self.resolve('complete', action_id='e'*32, transaction_id='PB001_00000001')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['service_state'], 'COMPLETED')
        self.assertEqual(self.resolve('abandon', action_id='f'*32).status_code, 409)
        self.assertEqual(self.resolve('resume', action_id='g'*32, transaction_id='PB001_00000001').status_code, 409)

    def test_restart_and_new_operator_pin_replay_original_actor_and_decision(self):
        self.paid(); result = self.resolve('resume').json()
        self.http.close(); self.store.close()
        self.store = CheckoutStore(Path(self.temp.name)/'orders.sqlite')
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        self.http = TestClient(create_app(self.backend, self.auth, recovery_pin='98765432'))
        request = {'action_id':'b'*32, 'action':'resume', 'reason':'Operator resumes test', 'transaction_id':None}
        response = self.http.post('/api/orders/'+self.oid+'/recovery/resolve',
            headers=dict(HEADERS, **{'X-Recovery-PIN':'98765432'}), json=request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['recovery_action'], result['recovery_action'])
        self.assertEqual(response.json()['grant_id'], result['grant_id'])
        self.assertEqual(self.count_actions(), 1)

    def test_client_sends_pin_transiently_and_validates_exact_recovery_ack(self):
        self.paid()
        view = self.client.recovery_inspect(self.oid, PIN)
        self.assertTrue(view['recovery_checked'])
        self.assertEqual(self.session.last_headers['X-Recovery-PIN'], PIN)
        self.assertNotIn('X-Recovery-PIN', self.client.headers)
        result = self.client.recovery_resolve(self.oid, PIN, 'b'*32, 'resume', 'Operator resumes test')
        self.assertEqual(result['service_state'], 'RESERVED')
        self.client.status(self.oid)
        self.assertNotIn('X-Recovery-PIN', self.session.last_headers)

    def test_schema_rejects_paid_flags_empty_reason_and_unknown_action(self):
        for update in ({'action':'reset'}, {'reason':' '}, {'reason':'line\nbreak'},
                       {'transaction_id':'../other'}, {'state':'PAID'}):
            body = {'action_id':'b'*32, 'action':'abandon', 'reason':'Operator ends test'}
            body.update(update)
            response = self.http.post('/api/orders/'+self.oid+'/recovery/resolve', headers=OPERATOR, json=body)
            self.assertEqual(response.status_code, 422, update)
        self.assertEqual(self.count_actions(), 0)


if __name__ == '__main__':
    unittest.main()
