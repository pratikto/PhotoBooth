"""Signed Midtrans notification verification regression, entirely offline."""
import hashlib
import unittest
from photobooth.midtrans_verify import verify_midtrans_notification, reconcile_midtrans_status


KEY = "test-server-key-not-a-secret"


def notification(amount="15000.00", status="settlement", code="200"):
    data = {"order_id": "PB001-001", "status_code": code,
            "gross_amount": amount, "transaction_status": status}
    data["signature_key"] = hashlib.sha512(
        (data["order_id"] + code + amount + KEY).encode()).hexdigest()
    return data


class MidtransVerifyTests(unittest.TestCase):
    def test_valid_signed_settlement(self):
        self.assertEqual(verify_midtrans_notification(notification(), KEY)["amount"], 15000)

    def test_tampered_amount_fails(self):
        data = notification()
        data["gross_amount"] = "1.00"
        with self.assertRaises(ValueError):
            verify_midtrans_notification(data, KEY)

    def test_bad_signature_fails(self):
        data = notification()
        data["signature_key"] = "0" * 128
        with self.assertRaises(ValueError):
            verify_midtrans_notification(data, KEY)

    def test_pending_does_not_credit(self):
        self.assertIsNone(verify_midtrans_notification(notification(status="pending", code="201"), KEY))

    def test_non_integer_amount_fails(self):
        with self.assertRaises(ValueError):
            verify_midtrans_notification(notification(amount="15000.50"), KEY)

    def test_independent_status_required(self):
        data = notification()
        self.assertIsNone(reconcile_midtrans_status(data, None, KEY))
        self.assertIsNone(reconcile_midtrans_status(data, {"order_id": "wrong"}, KEY))
        self.assertEqual(reconcile_midtrans_status(data, {
            "order_id": data["order_id"], "gross_amount": "15000.00",
            "status_code": "200", "transaction_status": "settlement"}, KEY)["amount"], 15000)


if __name__ == "__main__":
    unittest.main()
