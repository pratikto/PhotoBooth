"""Offline kiosk HTTP contract tests; no live provider or network."""
import unittest
from photobooth.qris_kiosk_client import QrisKioskClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []
        self.payload = {"state": "PENDING", "order_id": "abc123", "qr_url": "https://example.test/qr"}

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse(self.payload)


class KioskClientTests(unittest.TestCase):
    def setUp(self):
        self.session = FakeSession()
        self.client = QrisKioskClient("https://booth.example.test", "PB001", "x" * 32,
                                      session=self.session)

    def test_checkout_sends_server_priced_quantities(self):
        result = self.client.create_order({"template_a": 2})
        self.assertEqual(result["order_id"], "abc123")
        method, url, options = self.session.calls[0]
        self.assertEqual(method, "POST")
        self.assertEqual(url, "https://booth.example.test/api/orders")
        self.assertEqual(options["json"], {"quantities": {"template_a": 2}})
        self.assertEqual(options["headers"]["x-booth-id"], "PB001")

    def test_status_never_claims_pending_as_paid(self):
        self.assertEqual(self.client.status("abc123")["state"], "PENDING")

    def test_claim_requires_server_ack(self):
        self.session.payload = {"state": "PAID"}
        def request(method, url, **kwargs):
            return FakeResponse({"claimed": True} if method == "POST" else {"state": "PAID"})
        self.session.request = request
        self.assertTrue(self.client.claim("abc123"))

    def test_public_http_refused(self):
        with self.assertRaises(ValueError):
            QrisKioskClient("http://example.test", "PB001", "x" * 32)

    def test_loopback_http_explicit_preview_only(self):
        with self.assertRaises(ValueError):
            QrisKioskClient("http://localhost:8000", "PB001", "x" * 32)
        QrisKioskClient("http://localhost:8000", "PB001", "x" * 32,
                        allow_local_http=True)

    def test_invalid_order_id_rejected(self):
        with self.assertRaises(ValueError):
            self.client.status("../orders")


if __name__ == "__main__":
    unittest.main()
