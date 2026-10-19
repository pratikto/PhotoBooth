"""Offline sandbox checkout orchestration tests."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from photobooth.checkout_service import SandboxCheckoutService
from photobooth.payment_orders import OrderStore

KEY = "sandbox-test-only"


class FakeProvider:
    def __init__(self):
        self.status_data = {}
        self.order_id = None

    def create_qris(self, order_id, amount):
        self.order_id = order_id
        self.status_data = {"order_id": order_id, "gross_amount": str(amount),
                            "transaction_status": "pending", "status_code": "201"}
        return {"order_id": order_id, "transaction_status": "pending",
                "payment_type": "qris", "actions": [
                    {"name": "generate-qr-code", "url": "https://example.test/qr"}]}

    def get_status(self, order_id):
        return self.status_data


class CheckoutServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = OrderStore(Path(self.temp.name) / "orders.db")
        self.provider = FakeProvider()
        self.service = SandboxCheckoutService(self.store, self.provider, KEY)
        self.order = self.service.create_order("PB001", {"template_a": 2})

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def signed_callback(self, amount="15000", status="settlement", code="200"):
        data = {"order_id": self.order["order_id"], "gross_amount": amount,
                "status_code": code, "transaction_status": status}
        data["signature_key"] = hashlib.sha512(
            (data["order_id"] + code + amount + KEY).encode()).hexdigest()
        return data

    def test_quote_and_pending(self):
        self.assertEqual(self.order["amount"], 15000)
        self.assertEqual(self.service.status(self.order["order_id"], "PB001")["state"], "PENDING")
        self.assertFalse(self.service.claim(self.order["order_id"], "PB001"))

    def test_signed_notification_requires_provider_settlement(self):
        self.assertFalse(self.service.process_notification(self.signed_callback()))
        self.assertFalse(self.service.claim(self.order["order_id"], "PB001"))

    def test_verified_payment_claim_once(self):
        self.provider.status_data.update(transaction_status="settlement", status_code="200")
        self.assertTrue(self.service.process_notification(self.signed_callback()))
        self.assertTrue(self.service.process_notification(self.signed_callback()))
        self.assertTrue(self.service.claim(self.order["order_id"], "PB001"))
        self.assertFalse(self.service.claim(self.order["order_id"], "PB001"))

    def test_wrong_amount_denied(self):
        self.provider.status_data.update(transaction_status="settlement", status_code="200")
        self.assertFalse(self.service.process_notification(self.signed_callback(amount="10000")))
        self.assertFalse(self.service.claim(self.order["order_id"], "PB001"))

    def test_tampered_signature_denied(self):
        callback = self.signed_callback()
        callback["signature_key"] = "invalid"
        with self.assertRaises(ValueError):
            self.service.process_notification(callback)

    def test_other_booth_denied(self):
        self.assertIsNone(self.service.status(self.order["order_id"], "PB002"))
        self.assertFalse(self.service.claim(self.order["order_id"], "PB002"))


if __name__ == "__main__":
    unittest.main()
