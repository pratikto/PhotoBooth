"""Minimal Midtrans Core API sandbox transport; server-side only.

Credentials must be loaded from server environment, never shipped with Kivy.
No live endpoint support; this module deliberately fails closed.
"""
import base64
import json
from urllib.request import Request, urlopen
from urllib.parse import quote

SANDBOX_BASE = "https://api.sandbox.midtrans.com"


class MidtransSandboxClient:
    def __init__(self, server_key, *, timeout=10, transport=None):
        if not isinstance(server_key, str) or not server_key:
            raise ValueError("MIDTRANS_SERVER_KEY required")
        if not 0 < timeout <= 30:
            raise ValueError("Timeout must be between 0 and 30 seconds")
        self._key = server_key
        self.timeout = timeout
        self._transport = transport or urlopen

    def _request(self, method, path, body=None):
        auth = base64.b64encode((self._key + ":").encode("utf-8")).decode("ascii")
        headers = {"Authorization": "Basic " + auth, "Accept": "application/json"}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        request = Request(SANDBOX_BASE + path, data=data, headers=headers, method=method)
        with self._transport(request, timeout=self.timeout) as response:
            payload = response.read(65537)
        if len(payload) > 65536:
            raise ValueError("Provider response too large")
        result = json.loads(payload)
        if not isinstance(result, dict):
            raise ValueError("Unexpected provider response")
        return result

    def create_qris(self, order_id, amount):
        if not isinstance(order_id, str) or not order_id or len(order_id) > 50:
            raise ValueError("Invalid order ID")
        if type(amount) is not int or amount <= 0:
            raise ValueError("Invalid IDR amount")
        return self._request("POST", "/v2/charge", {
            "payment_type": "qris",
            "transaction_details": {"order_id": order_id, "gross_amount": amount},
        })

    def get_status(self, order_id):
        if not isinstance(order_id, str) or not order_id or len(order_id) > 50:
            raise ValueError("Invalid order ID")
        return self._request("GET", "/v2/" + quote(order_id, safe="") + "/status")
