"""Authoritative Sandbox checkout service with retry-safe visit identity.

The old checkout_service.py/OrderStore remain isolated historical prototypes.
Only this service plus CheckoutStore is used by the current server entrypoint.
"""
from photobooth.checkout_store import CheckoutConflict, CheckoutMissing, identifier
from photobooth.payment_quote import quote_checkout
from photobooth.fulfillment_contract import frozen_contract
from photobooth.qris_evidence import (authenticated_notification, provider_evidence,
                                     qr_url_from_status, idr_amount)


class ProviderUnavailable(RuntimeError):
    """Keep the order; do not invent a decline, success or replacement QR."""


class CheckoutBackend:
    def __init__(self, store, provider, server_key, merchant_id):
        if not isinstance(server_key, str) or not server_key:
            raise ValueError('Sandbox server key required')
        identifier(merchant_id)
        self.store, self.provider = store, provider
        self.server_key, self.merchant_id = server_key, merchant_id

    @property
    def provider_mode(self):
        return getattr(self.provider, 'mode', 'sandbox')

    def _creation_context(self, order_id):
        return self.store.validate_creation_context(order_id, self.merchant_id, self.provider_mode)

    def _fresh_payment(self, order_id, booth_id):
        order, checked, state, _outcome = self._observe_payment(order_id, booth_id, urgent=True)
        if not checked:
            raise ProviderUnavailable('Current provider evidence required')
        return order, state

    def _require_settlement(self, order_id, booth_id):
        order, provider_state = self._fresh_payment(order_id, booth_id)
        if provider_state != 'settlement' or order['state'] != 'PAID' or order['closed']:
            raise CheckoutConflict('Current verified settlement required')
        return order

    def _observe_payment(self, order_id, booth_id, *, urgent=False, immediate=False):
        identifier(order_id, maximum=50)
        order = self.store.get(order_id, booth_id)
        self._creation_context(order_id)
        reservation = self.store.begin_reconciliation(order_id, urgent=urgent, immediate=immediate)
        if reservation is None:
            return order, False, None, 'unknown'
        outcome, state, evidence, qr_url, display_valid = 'unknown', None, None, None, True
        try:
            data = self.provider.get_status(order_id)
            if isinstance(data, dict) and data.get('status_code') == '404':
                outcome = 'provider_not_found_unproven'
            else:
                evidence = provider_evidence(data, order, self.merchant_id)
                state = evidence['transaction_status']
                if state == 'pending':
                    try:
                        qr_url = qr_url_from_status(data, evidence, existing_url=order.get('qr_url'))
                    except (ValueError, TypeError):
                        display_valid = False
                outcome = ('review' if state in {'refund', 'partial_refund'} else
                           'paid' if state == 'settlement' else
                           'pending' if state == 'pending' else 'terminal')
        except Exception as error:
            if getattr(error, 'code', None) == 404:
                outcome = 'provider_not_found_unproven'
        accepted = self.store.finish_reconciliation(order_id, reservation,
            evidence=evidence, outcome=outcome, qr_url=qr_url)
        order = self.store.get(order_id, booth_id)
        checked = accepted and evidence is not None and display_valid
        if not checked:
            return order, False, None, outcome if accepted else 'unknown'
        if order['state'] == 'REVIEW_REQUIRED':
            outcome = 'review'
        return order, True, state, outcome

    def reconcile(self, order_id, booth_id, trigger='poll'):
        """Provider GET observation only; no grant, disposition or photo effects.

        A throttled/in-flight response is explicitly unchecked. Its historical
        PAID row never becomes fresh evidence just because a prior poll passed.
        """
        if trigger not in {'poll', 'restart', 'connectivity'}:
            raise ValueError('Invalid reconciliation trigger')
        order, checked, state, outcome = self._observe_payment(order_id, booth_id,
                                                              immediate=trigger != 'poll')
        result = self.view(order, verification_pending=not checked)
        result['reconciliation'] = {'checked': checked, 'outcome': outcome,
            'provider_state': state, 'retry_after': self.store.reconciliation_delay(order_id)}
        return result

    @property
    def sandbox_recovery_supported(self):
        from photobooth.midtrans_sandbox import MidtransSandboxClient
        mode = getattr(self.provider, 'mode', None)
        return (getattr(self, 'mode', 'sandbox') == 'sandbox'
                and (mode == 'sandbox' or (mode is None and isinstance(self.provider, MidtransSandboxClient))))

    def _fresh_recovery(self, order_id, booth_id):
        if not self.sandbox_recovery_supported:
            raise CheckoutConflict('Recovery is restricted to Sandbox')
        order = self.store.get(order_id, booth_id)
        self._creation_context(order_id)
        try:
            data = self.provider.get_status(order_id)
            evidence = provider_evidence(data, order, self.merchant_id)
            order = self._apply(order, data)
        except Exception as error:
            raise ProviderUnavailable('Recovery requires current provider evidence') from error
        return order, evidence['transaction_status']

    def recovery_inspect(self, order_id, booth_id):
        order, provider_state = self._fresh_recovery(order_id, booth_id)
        result = self.view(order)
        result.update(recovery_checked=True, recovery_provider_state=provider_state)
        return result

    def recovery_resolve(self, order_id, booth_id, action_id, action, reason, transaction_id, actor):
        order, provider_state = self._fresh_recovery(order_id, booth_id)
        # Monotonic PAID caching must not replace fresh settlement evidence.
        replay = self.store.recovery_action_applied(order_id, booth_id, action_id, action, reason, transaction_id)
        if action in {'resume', 'complete'} and provider_state != 'settlement' and not replay:
            raise CheckoutConflict('Recovery requires current verified settlement')
        order, record = self.store.recovery_action(order_id, booth_id, action_id, action,
                                                  reason, transaction_id, actor)
        result = self.view(order)
        result.update(recovery_checked=True, recovery_provider_state=provider_state,
                      recovery_action={key:record[key] for key in
                          ('action_id', 'action', 'reason', 'transaction_id', 'actor', 'created_at',
                           'prior_payment_state', 'prior_service_state')})
        return result

    def view(self, order, *, verification_pending=False):
        fields = ('id', 'checkout_key', 'quantities', 'amount', 'state', 'expires_at',
                  'qr_url', 'grant_id', 'service_state', 'local_transaction_id', 'closed')
        result = {key: order[key] for key in fields}
        result['order_id'] = result.pop('id')
        result['recovery_abandoned'] = self.store.recovery_abandoned(order['id'])
        result['customer_capability_bound'] = self.store.has_customer_capability(order['id'])
        try:
            record = self.store.fulfillment(order['id'], order['booth_id'])
            result['fulfillment'] = {key: record[key] for key in
                ('fulfillment_id', 'contract_hash', 'state', 'obligation_state', 'transaction_id',
                 'allocation_operation_id', 'booth_id', 'merchant_id')}
        except CheckoutMissing:
            result['fulfillment'] = None
        result['mode'] = getattr(self.provider, 'mode', 'sandbox')
        if result['mode'] == 'mock':
            result['qr_url'] = None
            result['qr_payload'] = 'MEONG MOCK ONLY - NOT QRIS - ' + order['id']
        result['verification_pending'] = verification_pending
        if order['state'] != 'PENDING' or order['closed']:
            result['qr_url'] = None
        return result

    def _apply(self, order, data):
        evidence = provider_evidence(data, order, self.merchant_id)
        # A valid payment must still be retained even when displaying its QR
        # fails. QR validation cannot turn a received settlement into nothing.
        updated = self.store.apply_evidence(order['id'], evidence)
        if updated['state'] == 'PENDING':
            self.store.save_qr(order['id'], qr_url_from_status(
                data, evidence, existing_url=updated.get('qr_url')))
        return self.store.get(order['id'])

    def create_order(self, booth_id, quantities, checkout_key, *, customer_capability_hash=None):
        quote = quote_checkout(quantities)
        order, first = self.store.begin(booth_id, dict(quantities), quote.total_amount, checkout_key,
                                       creation_context=(self.merchant_id, self.provider_mode),
                                       frozen_contract=frozen_contract(quantities),
                                       customer_capability_hash=customer_capability_hash)
        self._creation_context(order['id'])
        if not first:
            return self.status(order['id'], booth_id)
        if not self.store.mark_creation_sent(order['id'], self.merchant_id, self.provider_mode):
            return self.status(order['id'], booth_id)
        try:
            return self.view(self._apply(order, self.provider.create_qris(order['id'], order['amount'])))
        except Exception as error:
            self.store.mark_creation_uncertain(order['id'])
            # The persisted key survives an ambiguous response. Retrying does
            # GET Status for the SAME order; never another charge/order ID.
            raise ProviderUnavailable('Checkout verification unavailable; retry the same visit') from error

    def status(self, order_id, booth_id):
        identifier(order_id, maximum=50)
        order = self.store.get(order_id, booth_id)
        self._creation_context(order_id)
        if order['state'] in {'CREATED', 'PENDING'} and self.store.reserve_check(order_id):
            try:
                order = self._apply(order, self.provider.get_status(order_id))
            except Exception:
                return self.view(self.store.get(order_id), verification_pending=True)
        return self.view(order, verification_pending=order['state'] == 'CREATED')

    def process_notification(self, notification):
        order_id = authenticated_notification(notification, self.server_key)
        self.store.event(notification, 'RECEIVED')
        try:
            order = self.store.get(order_id)
        except CheckoutMissing:
            self.store.event(notification, 'IGNORED_UNKNOWN_ORDER')
            return True
        self._creation_context(order_id)
        if idr_amount(notification['gross_amount']) != order['amount']:
            self.store.event(notification, 'REJECTED_AMOUNT')
            raise ValueError('Notification amount mismatch')
        try:
            # Even an old pending callback reconciles the latest status. Do
            # not assume that unsigned callback status fields are authentic.
            self._apply(order, self.provider.get_status(order_id))
        except Exception as error:
            self.store.event(notification, 'RETRY')
            raise ProviderUnavailable('Provider verification unavailable') from error
        self.store.event(notification, 'APPLIED')
        return True

    def claim(self, order_id, booth_id, checkout_key):
        order = self.store.get(order_id, booth_id)
        if order['checkout_key'] != checkout_key or order['state'] != 'PAID' or order['closed']:
            raise CheckoutConflict('Checkout identity mismatch')
        self._creation_context(order_id)
        self._require_settlement(order_id, booth_id)
        return self.view(self.store.grant(order_id, booth_id, checkout_key))

    def allocate(self, order_id, booth_id, grant_id, operation_id):
        self.store.get(order_id, booth_id)
        self._require_settlement(order_id, booth_id)
        return self.view(self.store.allocate_fulfillment(order_id, booth_id, grant_id, operation_id))

    def customer_claim(self, order_id, booth_id, capability, operation_id):
        self.store.get(order_id,booth_id)
        self._creation_context(order_id)
        self.store.verify_customer_capability(order_id,booth_id,capability,operation_id)
        order,provider_state = self._fresh_payment(order_id,booth_id)
        paid = provider_state=='settlement' and order['state']=='PAID'
        pending = provider_state=='pending' and order['state']=='PENDING'
        if (not paid and not pending) or order['closed']:
            raise CheckoutConflict('Current verified payment state required')
        order = self.store.redeem_customer_capability(order_id,booth_id,capability,operation_id,payment_verified=paid)
        result = self.view(order)
        result['customer_claim'] = {'verified':True,'payment_verified':paid,'operation_id':operation_id}
        return result

    def service_transition(self, order_id, booth_id, grant_id, state, transaction_id):
        order = self.store.get(order_id, booth_id)
        self._creation_context(order_id)
        if state == 'STARTED':
            if (not grant_id or order['grant_id'] != grant_id
                    or order['local_transaction_id'] not in (None, transaction_id)):
                raise CheckoutConflict('Service permit mismatch')
            self._require_settlement(order_id, booth_id)
        return self.view(self.store.service_transition(order_id, booth_id, grant_id, state, transaction_id))

    def cancel(self, order_id, booth_id):
        order = self.store.get(order_id, booth_id)
        self._creation_context(order_id)
        if order['state'] in {'CREATED', 'PENDING'}:
            try:
                # Provider cancel and payment may race. Independent final
                # status decides whether the customer may leave or must take
                # the paid session; a local button never overrides settlement.
                self.provider.cancel(order_id)
                order = self._apply(order, self.provider.get_status(order_id))
            except Exception as error:
                raise ProviderUnavailable('Cancellation not confirmed') from error
        self.store.close_visit(order_id, booth_id)
        return self.view(self.store.get(order_id, booth_id))
