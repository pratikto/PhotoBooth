"""Midtrans notification authenticity checks for FEAT-020 sandbox integration.

The caller must ALSO query Midtrans status server-to-server before marking
an order paid. This module alone never authorizes capture or credits money.
"""
import hashlib
import hmac
from decimal import Decimal, InvalidOperation


def verify_midtrans_notification(notification, server_key):
    """Return normalized evidence or raise ValueError; never trust HTTP body alone."""
    if not isinstance(notification, dict) or not isinstance(server_key, str) or not server_key:
        raise ValueError("Invalid notification or missing server key")
    fields = ("order_id", "status_code", "gross_amount", "signature_key", "transaction_status")
    if any(not isinstance(notification.get(key), str) or not notification[key] for key in fields):
        raise ValueError("Missing Midtrans notification fields")
    expected = hashlib.sha512((
        notification["order_id"] + notification["status_code"]
        + notification["gross_amount"] + server_key
    ).encode("utf-8")).hexdigest()
    if not hmac.compare_digest(expected, notification["signature_key"]):
        raise ValueError("Invalid Midtrans notification signature")
    try:
        amount = Decimal(notification["gross_amount"])
    except InvalidOperation as error:
        raise ValueError("Invalid amount") from error
    if not amount.is_finite() or amount <= 0 or amount != amount.to_integral_value():
        raise ValueError("Amount must be a positive whole IDR value")
    if notification["status_code"] != "200" or notification["transaction_status"] != "settlement":
        return None
    return {"order_id": notification["order_id"], "amount": int(amount),
            "transaction_status": "settlement"}


def reconcile_midtrans_status(notification, provider_status, server_key):
    """Accept settlement only if signed callback and independent provider status agree.

    provider_status MUST be fetched from Midtrans over authenticated TLS by
    the backend, not supplied by the kiosk or by the webhook request.
    """
    evidence = verify_midtrans_notification(notification, server_key)
    if evidence is None or not isinstance(provider_status, dict):
        return None
    if (provider_status.get("order_id") != evidence["order_id"]
            or provider_status.get("transaction_status") != "settlement"
            or provider_status.get("status_code") != "200"):
        return None
    try:
        amount = Decimal(str(provider_status["gross_amount"]))
    except (KeyError, InvalidOperation):
        return None
    if not amount.is_finite() or amount != evidence["amount"]:
        return None
    return evidence
