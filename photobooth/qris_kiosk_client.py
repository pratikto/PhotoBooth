"""Kiosk HTTP v2 client; merchant/provider secrets never enter this process."""
import json
import math
import re
from urllib.parse import urlsplit
import requests

from photobooth.checkout_store import identifier

STATES = {'CREATED', 'PENDING', 'PAID', 'EXPIRED', 'FAILED', 'CANCELLED', 'REVIEW_REQUIRED'}


class QrisKioskClient:
    customer_capability_supported = True
    def __init__(self, base_url, booth_id, booth_token, *, timeout=8, session=None,
                 allow_local_http=False, expected_mode='sandbox'):
        if expected_mode not in {'sandbox', 'mock'}:
            raise ValueError('Invalid payment environment')
        self.expected_mode = expected_mode
        parsed = urlsplit(base_url)
        local = parsed.hostname in {'127.0.0.1', 'localhost'}
        if parsed.scheme != 'https' and not (allow_local_http and local and parsed.scheme == 'http'):
            raise ValueError('HTTPS required except explicit loopback preview')
        if parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.netloc:
            raise ValueError('Invalid backend URL')
        if re.fullmatch(r'PB[0-9]{3,8}', booth_id or '') is None:
            raise ValueError('Invalid booth identity')
        if (not isinstance(booth_token, str) or not 32 <= len(booth_token) <= 512
                or any(c.isspace() or ord(c) < 32 for c in booth_token)):
            raise ValueError('Invalid booth token')
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 30:
            raise ValueError('Invalid timeout')
        self.base_url, self.booth_id = base_url.rstrip('/'), booth_id
        self.headers = {'x-booth-id': booth_id, 'Authorization': 'Bearer ' + booth_token}
        self.timeout, self.session = timeout, session or requests.Session()

    def _call(self, method, path, *, payload=None, checkout_key=None, operator_pin=None, reconciliation_trigger=None):
        headers = dict(self.headers)
        if reconciliation_trigger is not None:
            headers['X-Reconciliation-Trigger'] = reconciliation_trigger
        if operator_pin is not None:
            if not isinstance(operator_pin, str) or re.fullmatch(r'[0-9]{8}', operator_pin) is None:
                raise ValueError('An eight-digit operator PIN is required')
            headers['X-Recovery-PIN'] = operator_pin
        if checkout_key is not None:
            headers['Idempotency-Key'] = identifier(checkout_key, minimum=16)
        response = self.session.request(method, self.base_url + path, headers=headers,
            json=payload, timeout=self.timeout, allow_redirects=False, stream=True)
        try:
            if not 200 <= response.status_code < 300:
                raise RuntimeError('Backend request rejected: HTTP ' + str(response.status_code))
            content = bytearray()
            for chunk in response.iter_content(4096):
                if len(content) + len(chunk) > 65536:
                    raise ValueError('Backend response too large')
                content.extend(chunk)
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError('Invalid backend response')
            return result
        finally:
            response.close()

    def _order(self, result, order_id=None):
        identifier(result.get('order_id'), maximum=50)
        if (result.get('state') not in STATES or result.get('mode') != self.expected_mode
                or (order_id is not None and result['order_id'] != order_id)
                or type(result.get('amount')) is not int or result['amount'] <= 0):
            raise ValueError('Unexpected checkout response')
        return result

    def create_order(self, quantities, checkout_key, *, customer_capability_hash=None):
        payload = {'quantities': quantities}
        if customer_capability_hash is not None:
            if not isinstance(customer_capability_hash,str) or re.fullmatch(r'[a-f0-9]{64}',customer_capability_hash) is None:
                raise ValueError('Invalid customer credential binding')
            payload['customer_capability_hash'] = customer_capability_hash
        result = self._order(self._call('POST', '/api/orders',
            payload=payload, checkout_key=checkout_key))
        if result.get('checkout_key') != checkout_key or result.get('quantities') != quantities:
            raise ValueError('Checkout identity mismatch')
        return result

    def customer_claim(self, order_id, capability, operation_id):
        identifier(order_id,maximum=50)
        identifier(operation_id,minimum=16)
        if not isinstance(capability,str) or re.fullmatch(r'[A-Za-z0-9_-]{43}',capability) is None:
            raise ValueError('Original customer ticket required')
        result = self._order(self._call('POST','/api/orders/'+order_id+'/customer-claim',
            payload={'capability':capability,'operation_id':operation_id}),order_id)
        proof = result.get('customer_claim') or {}
        if (proof.get('verified') is not True or proof.get('operation_id') != operation_id
                or type(proof.get('payment_verified')) is not bool or result.get('closed')
                or (proof['payment_verified'] and (result.get('state')!='PAID' or not result.get('grant_id')))
                or (not proof['payment_verified'] and result.get('state')!='PENDING')):
            raise ValueError('Customer proof acknowledgement mismatch')
        return result

    def report_fulfillment_issue(self, order_id, operation_id, reason):
        from photobooth.checkout_store import FULFILLMENT_ISSUE_REASONS
        identifier(order_id,maximum=50);identifier(operation_id,minimum=16)
        if reason not in FULFILLMENT_ISSUE_REASONS:
            raise ValueError('Allowlisted issue reason required')
        result=self._order(self._call('POST','/api/orders/'+order_id+'/fulfillment-issue',
            payload={'operation_id':operation_id,'reason':reason}),order_id)
        if (result.get('issue_ack')!={'recorded':True,'operation_id':operation_id,'reason':reason}
                or (result.get('fulfillment_issue') or {}).get('status')!='PAID_UNFULFILLED'):
            raise ValueError('Fulfillment issue acknowledgment mismatch')
        return result

    def status(self, order_id):
        identifier(order_id, maximum=50)
        return self._order(self._call('GET', '/api/orders/' + order_id), order_id)

    def reconcile(self, order_id, *, trigger='poll'):
        identifier(order_id, maximum=50)
        if trigger not in {'poll', 'restart', 'connectivity'}:
            raise ValueError('Invalid reconciliation trigger')
        result = self._order(self._call('POST', '/api/orders/' + order_id + '/reconcile',
                                        reconciliation_trigger=trigger), order_id)
        observation = result.get('reconciliation')
        if (not isinstance(observation, dict) or type(observation.get('checked')) is not bool
                or observation.get('outcome') not in
                {'unknown', 'pending', 'terminal', 'paid', 'review', 'provider_not_found_unproven'}):
            raise ValueError('Invalid payment reconciliation')
        return result

    def claim(self, order_id, checkout_key):
        identifier(order_id, maximum=50)
        result = self._order(self._call('POST', '/api/orders/' + order_id + '/claim',
                                        checkout_key=checkout_key), order_id)
        if (result.get('state') != 'PAID' or not result.get('grant_id')
                or result.get('checkout_key') != checkout_key):
            raise ValueError('No verified service permit')
        return result

    def service_transition(self, order_id, grant_id, state, transaction_id, *, service_fence=None):
        identifier(order_id, maximum=50)
        payload={'grant_id':grant_id,'state':state,'transaction_id':transaction_id}
        if service_fence is not None:
            payload['service_fence']=identifier(service_fence,minimum=32,maximum=32)
        result = self._order(self._call('POST', '/api/orders/' + order_id + '/service',
            payload=payload), order_id)
        if (result.get('grant_id') != grant_id or result.get('service_state') != state
                or result.get('local_transaction_id') != transaction_id):
            raise ValueError('Service acknowledgement does not match this capture')
        return result

    def release(self, order_id, pin, operation_id, *, isolation_id=None, legacy_without_ticket=False):
        identifier(order_id,maximum=50);identifier(operation_id,minimum=32,maximum=32)
        payload={'operation_id':operation_id}
        if type(legacy_without_ticket) is not bool or (legacy_without_ticket and isolation_id):
            raise ValueError('Explicit legacy preparation intent required')
        if legacy_without_ticket:
            if self.expected_mode!='sandbox':
                raise ValueError('Legacy test archival is restricted to Sandbox')
            payload['legacy_without_ticket']=True
        if isolation_id is not None:
            payload['isolation_id']=identifier(isolation_id,minimum=32,maximum=32)
        result=self._order(self._call('POST','/api/orders/'+order_id+'/recovery/release',
            operator_pin=pin,payload=payload),order_id)
        receipt=result.get('release_ack') if isolation_id else result.get('release')
        if (not receipt or receipt.get('operation_id')!=operation_id
                or receipt.get('state') not in ({'ACKED'} if isolation_id else {'PREPARED','ACKED'})
                or (isolation_id and (receipt.get('isolation_id')!=isolation_id or not result.get('closed')))
                or not (result.get('service_fence') or {}).get('suspended')):
            raise ValueError('Original release acknowledgment required')
        return result

    def allocate(self, order_id, grant_id, operation_id):
        identifier(order_id, maximum=50)
        identifier(operation_id, minimum=16)
        result = self._order(self._call('POST', '/api/orders/'+order_id+'/allocate',
            payload={'grant_id': grant_id, 'operation_id': operation_id}), order_id)
        allocation = result.get('fulfillment') or {}
        if (result.get('grant_id') != grant_id or allocation.get('allocation_operation_id') != operation_id
                or result.get('local_transaction_id') != allocation.get('transaction_id')):
            raise ValueError('Allocation acknowledgement mismatch')
        identifier(allocation.get('transaction_id'))
        return result

    def cancel(self, order_id):
        identifier(order_id, maximum=50)
        return self._order(self._call('POST', '/api/orders/' + order_id + '/cancel'), order_id)

    def recovery_inspect(self, order_id, pin):
        identifier(order_id, maximum=50)
        if self.expected_mode != 'sandbox':
            raise ValueError('Recovery is restricted to Sandbox')
        result = self._order(self._call('POST', '/api/orders/' + order_id + '/recovery/inspect',
                                       operator_pin=pin), order_id)
        if result.get('recovery_checked') is not True or result.get('verification_pending'):
            raise ValueError('Recovery requires fresh provider evidence')
        return result

    def recovery_resolve(self, order_id, pin, action_id, action, reason, transaction_id=None):
        identifier(order_id, maximum=50)
        identifier(action_id, minimum=16)
        if self.expected_mode != 'sandbox':
            raise ValueError('Recovery is restricted to Sandbox')
        result = self._order(self._call('POST', '/api/orders/' + order_id + '/recovery/resolve',
            operator_pin=pin, payload={'action_id':action_id, 'action':action,
                                      'reason':reason, 'transaction_id':transaction_id}), order_id)
        decision = result.get('recovery_action') or {}
        if (result.get('recovery_checked') is not True or result.get('verification_pending')
                or decision.get('action_id') != action_id or decision.get('action') != action
                or decision.get('transaction_id') != transaction_id or decision.get('reason') != reason):
            raise ValueError('Recovery acknowledgement mismatch')
        return result

    def close(self):
        self.session.close()
