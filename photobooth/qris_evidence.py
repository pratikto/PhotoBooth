"""Validate Midtrans Core QRIS evidence against the server's frozen order.

Reference: docs.midtrans.com/reference/qris and best-practices-to-handle-notification.
A callback signature authenticates only its documented signed fields. Its
status is NEVER sufficient; the service always fetches the current status.
"""
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import re
from urllib.parse import urlsplit

from photobooth.checkout_store import identifier

SANDBOX_ORIGIN = 'https://api.sandbox.midtrans.com'
PROVIDER_STATES = {'pending', 'settlement', 'expire', 'deny', 'cancel', 'failure',
                   'refund', 'partial_refund'}


def idr_amount(value):
    if type(value) is int:
        value = str(value)
    if not isinstance(value, str) or re.fullmatch(r'[0-9]{1,12}(?:\.0{1,2})?', value) is None:
        raise ValueError('Invalid whole-IDR amount')
    amount = int(value.split('.')[0])
    if amount <= 0:
        raise ValueError('Amount must be positive')
    return amount


def authenticated_notification(data, server_key):
    if not isinstance(data, dict) or not server_key:
        raise ValueError('Invalid notification')
    for key in ('order_id', 'status_code', 'gross_amount', 'signature_key'):
        if not isinstance(data.get(key), str):
            raise ValueError('Missing signed notification field')
    identifier(data['order_id'], maximum=50)
    idr_amount(data['gross_amount'])
    signature = data['signature_key']
    if re.fullmatch(r'[0-9a-f]{128}', signature) is None:
        raise ValueError('Invalid notification signature')
    expected = hashlib.sha512((data['order_id'] + data['status_code'] +
                               data['gross_amount'] + server_key).encode()).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError('Invalid notification signature')
    return data['order_id']


def expiry_timestamp(value):
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > 40:
        raise ValueError('Invalid provider expiry')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone(timedelta(hours=7)))
    return result.timestamp()


def provider_evidence(data, order, merchant_id):
    if not isinstance(data, dict):
        raise ValueError('Invalid provider response')
    amount = idr_amount(data.get('gross_amount'))
    status = data.get('transaction_status')
    if (data.get('order_id') != order['id'] or amount != order['amount']
            or data.get('currency') != 'IDR' or data.get('payment_type') != 'qris'
            or data.get('merchant_id') != merchant_id
            or data.get('fraud_status', 'accept') != 'accept'
            or status not in PROVIDER_STATES
            or data.get('status_code') not in {'200', '201', '202'}
            or (status == 'settlement' and data.get('status_code') != '200')):
        raise ValueError('Provider response does not match checkout')
    reference = identifier(data.get('transaction_id'), maximum=128)
    if order.get('provider_ref') and reference != order['provider_ref']:
        raise ValueError('Provider transaction changed')
    return {'order_id': order['id'], 'amount': amount, 'transaction_status': status,
            'transaction_id': reference, 'merchant_id': merchant_id,
            'expires_at': expiry_timestamp(data.get('expiry_time'))}


def sandbox_qr_url(url):
    if not isinstance(url, str) or len(url) > 512:
        raise ValueError('Invalid QR URL')
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname != 'api.sandbox.midtrans.com'
            or parsed.port not in (None, 443) or parsed.username or parsed.password
            or parsed.query or parsed.fragment
            or re.fullmatch(r'/v[24]/qris/[A-Za-z0-9_-]{1,128}/qr-code', parsed.path) is None):
        raise ValueError('Untrusted Sandbox QR URL')
    return url


def qr_url_from_status(data, evidence):
    for action in data.get('actions', []) or []:
        if isinstance(action, dict) and action.get('name') == 'generate-qr-code':
            if action.get('method', 'GET') != 'GET':
                raise ValueError('Unexpected QR action method')
            return sandbox_qr_url(action.get('url'))
    # GET Status need not repeat actions; the official v2 QR endpoint is keyed
    # by the independently verified transaction ID, not a URL from the kiosk.
    return sandbox_qr_url(SANDBOX_ORIGIN + '/v2/qris/' + evidence['transaction_id'] + '/qr-code')
