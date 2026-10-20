"""Offline v2 kiosk contract and credential redirect boundary tests."""
import json
import unittest
from photobooth.qris_kiosk_client import QrisKioskClient

VISIT = 'a' * 32


class FakeResponse:
    status_code = 200
    def __init__(self, payload): self.payload = payload
    def iter_content(self, size): yield json.dumps(self.payload).encode()
    def close(self): pass


class FakeSession:
    def __init__(self):
        self.calls = []
        self.payload = {'state':'PENDING', 'order_id':'abc123', 'mode':'sandbox',
            'amount':15000, 'quantities':{'template_a':2}, 'checkout_key':VISIT}
    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse(self.payload)
    def close(self): pass


class KioskClientTests(unittest.TestCase):
    def setUp(self):
        self.session = FakeSession()
        self.client = QrisKioskClient('https://booth.example.test', 'PB001', 'x' * 32, session=self.session)

    def test_checkout_sends_server_priced_quantities(self):
        result = self.client.create_order({'template_a':2}, VISIT)
        self.assertEqual(result['order_id'], 'abc123')
        method, url, opts = self.session.calls[0]
        self.assertEqual(method, 'POST')
        self.assertEqual(opts['json'], {'quantities':{'template_a':2}})
        self.assertEqual(opts['headers']['Idempotency-Key'], VISIT)
        self.assertFalse(opts['allow_redirects'])

    def test_status_never_claims_pending_as_paid(self):
        self.assertEqual(self.client.status('abc123')['state'], 'PENDING')

    def test_claim_requires_server_ack(self):
        self.session.payload.update(state='PAID', grant_id='b' * 32)
        self.assertEqual(self.client.claim('abc123', VISIT)['grant_id'], 'b' * 32)

    def test_public_http_refused(self):
        with self.assertRaises(ValueError): QrisKioskClient('http://example.test', 'PB001', 'x' * 32)

    def test_loopback_http_explicit_preview_only(self):
        with self.assertRaises(ValueError): QrisKioskClient('http://localhost:8000', 'PB001', 'x' * 32)
        QrisKioskClient('http://localhost:8000', 'PB001', 'x' * 32, allow_local_http=True)

    def test_invalid_order_id_rejected(self):
        with self.assertRaises(ValueError): self.client.status('../orders')

    def test_wrong_order_response_rejected(self):
        self.session.payload['order_id'] = 'another'
        with self.assertRaises(ValueError): self.client.status('abc123')

    def test_non_sandbox_response_rejected(self):
        self.session.payload['mode'] = 'production'
        with self.assertRaises(ValueError): self.client.status('abc123')

    def test_missing_idempotency_identity_rejected(self):
        with self.assertRaises(ValueError): self.client.create_order({'template_a':2}, '')

    def test_redirect_rejected_without_second_request(self):
        class Redirect(FakeResponse): status_code = 302
        self.session.request = lambda *_a, **_k: Redirect({})
        with self.assertRaises(RuntimeError): self.client.status('abc123')
