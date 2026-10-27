"""Offline transport contract tests: no actual Midtrans requests."""
import base64
import io
import json
import unittest
from urllib.error import HTTPError
from photobooth.midtrans_sandbox import MidtransSandboxClient, SANDBOX_BASE


class Response:
    def __init__(self, payload):
        self.data = io.BytesIO(json.dumps(payload).encode())

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def read(self, n):
        return self.data.read(n)


class MidtransSandboxTests(unittest.TestCase):
    def setUp(self):
        self.requests = []

        def transport(req, timeout):
            self.requests.append((req, timeout))
            return Response({"status_code": "201", "transaction_status": "pending"})
        self.client = MidtransSandboxClient("dummy-sandbox-key", transport=transport)

    def test_charge_uses_sandbox_and_qris(self):
        self.client.create_qris("PB001-0001", 15000)
        req, timeout = self.requests[0]
        self.assertEqual(req.full_url, SANDBOX_BASE + "/v2/charge")
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(json.loads(req.data)["payment_type"], "qris")
        self.assertEqual(json.loads(req.data)["transaction_details"]["gross_amount"], 15000)
        self.assertEqual(req.get_header("Authorization"), "Basic " +
                         base64.b64encode(b"dummy-sandbox-key:").decode())
        self.assertEqual(timeout, 10)

    def test_status_url(self):
        self.client.get_status("PB001-0001")
        self.assertEqual(self.requests[0][0].full_url, SANDBOX_BASE + "/v2/PB001-0001/status")

    def test_server_key_spelling_never_selects_production_or_rewrites_auth(self):
        self.assertEqual(SANDBOX_BASE, 'https://api.sandbox.midtrans.com')
        for prefix in ('SB-Mid-server-', 'Mid-server-'):
            key = prefix + 'TEST-ONLY-NOT-A-CREDENTIAL'
            with self.subTest(prefix=prefix):
                self.requests.clear()
                client = MidtransSandboxClient(key, transport=self.client._transport)
                client.create_qris('PB001-0001', 10000)
                client.get_status('PB001-0001')
                client.cancel('PB001-0001')
                self.assertEqual([req.full_url for req, _ in self.requests], [
                    'https://api.sandbox.midtrans.com/v2/charge',
                    'https://api.sandbox.midtrans.com/v2/PB001-0001/status',
                    'https://api.sandbox.midtrans.com/v2/PB001-0001/cancel'])
                expected_auth = 'Basic ' + base64.b64encode((key + ':').encode()).decode()
                for req, _ in self.requests:
                    self.assertEqual(req.get_header('Authorization'), expected_auth)

    def test_rejected_key_has_no_production_fallback(self):
        requests = []
        def unauthorized(request, timeout):
            requests.append(request.full_url)
            raise HTTPError(request.full_url, 401, 'Unauthorized', {}, None)
        client = MidtransSandboxClient('Mid-server-TEST-ONLY-NOT-A-CREDENTIAL',
                                      transport=unauthorized)
        with self.assertRaises(HTTPError):
            client.create_qris('PB001-0001', 10000)
        self.assertEqual(requests, ['https://api.sandbox.midtrans.com/v2/charge'])

    def test_invalid_amount_rejected_before_network(self):
        for amount in (0, -1, True, 15.5):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.client.create_qris("PB001", amount)
        self.assertFalse(self.requests)

    def test_empty_key_rejected(self):
        with self.assertRaises(ValueError):
            MidtransSandboxClient("")

    def test_invalid_order_id_rejected(self):
        with self.assertRaises(ValueError):
            self.client.get_status("")
        self.assertFalse(self.requests)

    def test_cancel_uses_sandbox(self):
        self.client.cancel("PB001-0001")
        request = self.requests[0][0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, SANDBOX_BASE + "/v2/PB001-0001/cancel")

    def test_redirect_is_not_followed(self):
        from photobooth.midtrans_sandbox import NoRedirect
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.test"))

    def test_nonfinite_timeout_rejected(self):
        for timeout in (True, float('nan'), float('inf'), 0):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                MidtransSandboxClient("dummy", timeout=timeout)


if __name__ == "__main__":
    unittest.main()
