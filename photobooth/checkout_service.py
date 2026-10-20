"""FEAT-020 backend orchestration for Midtrans Sandbox.

Server-only service. Caller must authenticate booth identity before invoking
create_order/status/claim; never expose this object directly to kiosk clients.
"""
from urllib.parse import urlsplit

from photobooth.payment_quote import quote_checkout
from photobooth.midtrans_verify import reconcile_midtrans_status


class SandboxCheckoutService:
    def __init__(self, store, provider, server_key):
        if not server_key:
            raise ValueError("Server key required")
        self.store = store
        self.provider = provider
        self.server_key = server_key

    def create_order(self, booth_id, quantities):
        quote = quote_checkout(quantities)
        order_id = self.store.create(booth_id, dict(quantities), quote.total_amount)
        # Network failures leave a CREATED order; do not grant a photo session.
        response = self.provider.create_qris(order_id, quote.total_amount)
        if (not isinstance(response, dict)
                or response.get("order_id") != order_id
                or response.get("transaction_status") != "pending"
                or response.get("payment_type") != "qris"):
            raise ValueError("Unexpected Midtrans QRIS response")
        actions = response.get("actions", [])
        qr_url = next((a.get("url") for a in actions
                       if isinstance(a, dict) and a.get("name") == "generate-qr-code"), None)
        if not isinstance(qr_url, str):
            raise ValueError("Missing QRIS action")
        parsed = urlsplit(qr_url)
        if (parsed.scheme != "https" or parsed.hostname != "api.sandbox.midtrans.com"
                or parsed.username or parsed.password or parsed.fragment):
            raise ValueError("Untrusted Midtrans QRIS action URL")
        # Validate every externally supplied field before moving CREATED to PENDING.
        self.store.attach_provider(order_id, order_id)
        return {"order_id": order_id, "amount": quote.total_amount,
                "state": "PENDING", "qr_url": qr_url}

    def process_notification(self, notification):
        """Signed callback + independent authenticated Midtrans status query."""
        if not isinstance(notification, dict):
            raise ValueError("Invalid notification")
        # Validate signature before issuing provider status lookup.
        from photobooth.midtrans_verify import verify_midtrans_notification
        signed = verify_midtrans_notification(notification, self.server_key)
        if signed is None:
            return False
        order_id = signed["order_id"]
        provider_status = self.provider.get_status(order_id)
        evidence = reconcile_midtrans_status(notification, provider_status, self.server_key)
        if evidence is None:
            return False
        return self.store.confirm_provider_status(order_id, order_id,
                                                  evidence["amount"], "settlement")

    def status(self, order_id, booth_id):
        return self.store.status(order_id, booth_id)

    def claim(self, order_id, booth_id):
        return self.store.claim(order_id, booth_id)
