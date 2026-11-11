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

    @property
    def mode(self):
        return self._transport.expected_mode

    @property
    def booth_id(self):
        return self._transport.booth_id

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

    def freeze_checkout(self,lease,*,revision,expected_amount):
        from photobooth.post_preview_store import DraftLease
        if (type(lease) is not DraftLease or lease.booth_id!=self.booth_id
                or type(lease.draft_id) is not str or re.fullmatch(r'[a-f0-9]{32}',lease.draft_id) is None
                or any(type(v) is not int or not 1<=v<=2147483647 for v in (revision,expected_amount))):
            raise ValueError('Exact original preview owner and quote required')
        payload=dict(self._owner(lease),revision=revision,expected_amount=expected_amount)
        result=self._transport._call('POST','/api/postpay/drafts/'+lease.draft_id+'/freeze',payload=payload)
        expected=dict(kind='FROZEN_CHECKOUT',draft_id=lease.draft_id,booth_id=self.booth_id,
            visit_id=lease.visit_id,generation=lease.generation,revision=revision,amount=expected_amount,
            mode=self.mode,order_version=ORDER_VERSION,phase='CREATE_PREPARED',fulfillment_authorized=False)
        if (type(result) is not dict or set(result)!=set(expected)|{'purchase_group_id','contract_sha256'}
                or any(type(result[k]) is not type(v) or result[k]!=v for k,v in expected.items())
                or type(result['purchase_group_id']) is not str
                or re.fullmatch(r'[a-f0-9]{32}',result['purchase_group_id']) is None
                or type(result['contract_sha256']) is not str
                or re.fullmatch(r'[a-f0-9]{64}',result['contract_sha256']) is None):
            raise ValueError('Unexpected original freeze observation')
        return result

    def begin(self, group, lease):
        return self._request('POST', group, '/begin', self._owner(lease))

    def bind_worker_generation(self, lease):
        from photobooth.post_preview_store import DraftLease
        if (type(lease) is not DraftLease or lease.booth_id != self.booth_id
                or type(lease.draft_id) is not str or re.fullmatch(r'[a-f0-9]{32}',lease.draft_id) is None):
            raise ValueError('Exact original draft owner required')
        result=self._transport._call('POST','/api/postpay/drafts/'+lease.draft_id+'/worker-binding',
                                    payload=self._owner(lease))
        expected=dict(kind='ORIGINAL_WORKER_BOUND',draft_id=lease.draft_id,booth_id=self.booth_id,
            visit_id=lease.visit_id,generation=lease.generation,mode=self.mode,
            order_version=ORDER_VERSION,fulfillment_authorized=False)
        if (type(result) is not dict or set(result)!=set(expected)
                or any(type(result[k]) is not type(v) or result[k]!=v for k,v in expected.items())):
            raise ValueError('Unexpected original worker binding observation')
        return result

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
