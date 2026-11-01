"""Restricted PP kiosk client, reusing original TLS/bounded HTTP transport.

Only booth credentials enter this client. Responses are financial observations,
never local media, printer, customer identity or machine-release capabilities.
"""
import re

from photobooth.checkout_store import identifier
from photobooth.post_preview_store import ORDER_VERSION
from photobooth.qris_kiosk_client import QrisKioskClient


STATES = frozenset({'NOT_CREATED', 'UNKNOWN', 'PENDING', 'PAID_LIVE', 'PAID_UNCLAIMED',
                   'REVIEW_REQUIRED', 'EXPIRED_UNPAID', 'CANCELLED_UNPAID', 'TERMINAL_UNPAID'})


class PostPreviewClient:
    def __init__(self, *args, **kwargs):
        self._transport = QrisKioskClient(*args, **kwargs)

    def _request(self, method, group, suffix='', payload=None):
        if not isinstance(group, str) or re.fullmatch(r'[a-f0-9]{32}', group) is None:
            raise ValueError('Original purchase group required')
        result = self._transport._call(method, '/api/postpay/groups/'+group+suffix, payload=payload)
        if (result.get('purchase_group_id') != group
                or result.get('booth_id') != self._transport.booth_id
                or result.get('order_version') != ORDER_VERSION
                or result.get('mode') != self._transport.expected_mode
                or result.get('state') not in STATES
                or type(result.get('amount')) is not int or result['amount'] <= 0
                or result.get('fulfillment_authorized') is not False
                or type(result.get('fresh_checked')) is not bool
                or type(result.get('paid_verified')) is not bool):
            raise ValueError('Unexpected original payment observation')
        return result

    @staticmethod
    def _owner(lease):
        identifier(lease.visit_id)
        if type(lease.generation) is not int or lease.generation < 1:
            raise ValueError('Original generation required')
        return {'visit_id': lease.visit_id, 'generation': lease.generation}

    def inspect(self, group):
        return self._request('GET', group)

    def begin(self, group, lease):
        return self._request('POST', group, '/begin', self._owner(lease))

    def continue_expired(self, group, lease, *, actively_continuing):
        if type(actively_continuing) is not bool:
            raise ValueError('Explicit continuation required')
        return self._request('POST', group, '/continue', dict(self._owner(lease), actively_continuing=actively_continuing))

    def reconcile(self, group, *, trigger='poll'):
        if trigger not in {'poll', 'restart', 'connectivity'}:
            raise ValueError('Bounded reconciliation trigger required')
        return self._request('POST', group, '/reconcile', {'trigger': trigger})

    def lifecycle(self, group, lease, event):
        from photobooth.post_preview_store import LIFECYCLE_EVENTS
        if event not in LIFECYCLE_EVENTS:
            raise ValueError('Exact lifecycle event required')
        return self._request('POST', group, '/lifecycle', dict(self._owner(lease), event=event))

    def close(self):
        self._transport.close()
