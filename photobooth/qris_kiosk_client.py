"""Kiosk-side HTTP adapter for FEAT-020 sandbox orders.

Only use with an operator-controlled HTTPS backend. Never send Midtrans server
keys from the kiosk. This client does not decide whether a payment is settled.
"""
from urllib.parse import urlsplit
import requests


class QrisKioskClient:
    def __init__(self, base_url, booth_id, booth_token, *, timeout=8, session=None,
                 allow_local_http=False):
        parsed = urlsplit(base_url)
        local = parsed.hostname in {"127.0.0.1", "localhost"}
        if (parsed.scheme != "https" and not
                (allow_local_http and local and parsed.scheme == "http")):
            raise ValueError("HTTPS required (except explicit loopback preview)")
        if parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.netloc:
            raise ValueError("Invalid backend URL")
        if not isinstance(booth_id, str) or not booth_id.startswith("PB"):
            raise ValueError("Invalid booth identity")
        if not isinstance(booth_token, str) or len(booth_token) < 32:
            raise ValueError("Booth token required")
        self.base_url = base_url.rstrip("/")
        self.headers = {"x-booth-id": booth_id, "Authorization": "Bearer " + booth_token}
        self.timeout = timeout
        self.session = session or requests.Session()

    def _call(self, method, path, *, payload=None):
        response = self.session.request(
            method, self.base_url + path, headers=self.headers,
            json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Invalid backend response")
        return data

    def create_order(self, quantities):
        result = self._call("POST", "/api/orders", payload={"quantities": quantities})
        if result.get("state") != "PENDING" or not isinstance(result.get("order_id"), str):
            raise ValueError("Unexpected checkout response")
        return result

    def status(self, order_id):
        if not isinstance(order_id, str) or not order_id.isalnum() or len(order_id) > 50:
            raise ValueError("Invalid order ID")
        result = self._call("GET", "/api/orders/" + order_id)
        if result.get("state") not in {"CREATED", "PENDING", "PAID", "EXPIRED", "FAILED", "CANCELLED"}:
            raise ValueError("Unknown payment state")
        return result

    def claim(self, order_id):
        self.status(order_id)  # validate identifier and confirm backend availability
        result = self._call("POST", "/api/orders/" + order_id + "/claim")
        return result.get("claimed") is True
