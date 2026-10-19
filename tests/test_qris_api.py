"""HTTP route tests for the staging-only QRIS backend."""
import unittest

try:
    from fastapi.testclient import TestClient
    from photobooth.qris_api import create_app
    from photobooth.booth_auth import BoothAuthenticator
except ImportError:
    TestClient = None


class StubService:
    def create_order(self, booth, quantities):
        return {"order_id": "order-1", "booth": booth, "quantities": quantities}

    def status(self, order_id, booth):
        return {"state": "PAID", "claimed": False} if booth == "PB001" and order_id == "order-1" else None

    def claim(self, order_id, booth):
        return booth == "PB001" and order_id == "order-1"

    def process_notification(self, data):
        return False


@unittest.skipIf(TestClient is None, "FastAPI and httpx required")
class QRISApiTests(unittest.TestCase):
    def setUp(self):
        auth = BoothAuthenticator({"PB001": "sample-booth-secret-at-least-32-characters"})
        self.client = TestClient(create_app(StubService(), auth))
        self.headers = {"x-booth-id": "PB001",
                        "Authorization": "Bearer sample-booth-secret-at-least-32-characters"}

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)

    def test_unauthenticated_order_denied(self):
        self.assertEqual(self.client.post("/api/orders", json={"quantities": {"template_a": 1}}).status_code, 401)

    def test_authenticated_order(self):
        result = self.client.post("/api/orders", json={"quantities": {"template_a": 1}},
                                  headers=self.headers)
        self.assertEqual(result.status_code, 201)

    def test_status_is_booth_scoped(self):
        self.assertEqual(self.client.get("/api/orders/order-1", headers=self.headers).status_code, 200)
        self.assertEqual(self.client.get("/api/orders/missing", headers=self.headers).status_code, 404)

    def test_claim_requires_auth(self):
        self.assertEqual(self.client.post("/api/orders/order-1/claim").status_code, 401)

    def test_invalid_webhook_rejected(self):
        self.assertEqual(self.client.post("/api/webhooks/midtrans", content=b"not-json").status_code, 400)

    def test_webhook_large_body_rejected(self):
        result = self.client.post("/api/webhooks/midtrans",
                                  content=b"x" * 16385)
        self.assertEqual(result.status_code, 413)

    def test_webhook_bad_content_length_rejected(self):
        result = self.client.post("/api/webhooks/midtrans",
                                  content=b"{}", headers={"content-length": "bad"})
        self.assertEqual(result.status_code, 400)

    def test_checkout_provider_outage_is_503(self):
        class OutageService(StubService):
            def create_order(self, booth, quantities):
                raise RuntimeError("provider unavailable")
        auth = BoothAuthenticator({"PB001": "sample-booth-secret-at-least-32-characters"})
        client = TestClient(create_app(OutageService(), auth))
        result = client.post("/api/orders",
                             json={"quantities": {"template_a": 1}},
                             headers=self.headers)
        self.assertEqual(result.status_code, 503)

    def test_webhook_provider_outage_is_503(self):
        class OutageService(StubService):
            def process_notification(self, data):
                raise RuntimeError("provider unavailable")
        auth = BoothAuthenticator({"PB001": "sample-booth-secret-at-least-32-characters"})
        client = TestClient(create_app(OutageService(), auth))
        self.assertEqual(client.post("/api/webhooks/midtrans",
                                     json={"order_id": "test"}).status_code, 503)


if __name__ == "__main__":
    unittest.main()
