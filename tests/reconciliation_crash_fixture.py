"""Child-only PAY-06 probe against a disposable checkout database; no network."""
import os
import sys

from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from tests.test_checkout_backend import FakeProvider, KEY, MERCHANT


def crash_reconciliation(path, order_id, boundary):
    store = CheckoutStore(path, now=lambda: 2000.0)
    order = store.get(order_id, 'PB001')
    provider = FakeProvider()
    provider.rows[order_id] = {
        'order_id': order_id, 'gross_amount': str(order['amount']),
        'currency': 'IDR', 'payment_type': 'qris', 'merchant_id': MERCHANT,
        'transaction_id': order['provider_ref'], 'transaction_status': 'settlement',
        'status_code': '200', 'fraud_status': 'accept',
    }

    def no_charge(*_args):
        raise AssertionError('Reconciliation must never POST a charge')

    provider.create_qris = no_charge
    if boundary == 'validated':
        def before_transaction(_order_id, _reservation, *, evidence, outcome, **_kwargs):
            assert provider.reads == 1 and evidence['transaction_status'] == 'settlement'
            assert outcome == 'paid' and not store.db.in_transaction
            assert store.get(order_id) == order
            os._exit(71)
        store.finish_reconciliation = before_transaction
    elif boundary == 'uncommitted':
        original = store._apply_evidence

        def after_sql(*args, **kwargs):
            result = original(*args, **kwargs)
            assert provider.reads == 1 and store.db.in_transaction
            assert result['state'] == 'PAID'
            assert store.fulfillment(order_id, 'PB001')['obligation_state'] == 'OWED'
            os._exit(72)
        store._apply_evidence = after_sql
    else:
        raise ValueError('Unknown crash boundary')
    CheckoutBackend(store, provider, KEY, MERCHANT).reconcile(order_id, 'PB001')
    raise AssertionError('Crash boundary was not reached')


if __name__ == '__main__':
    crash_reconciliation(*sys.argv[1:])
