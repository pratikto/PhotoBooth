"""Child-only AR fixtures; synthetic SQLite, never network or operator settings."""
import os
from pathlib import Path
import sys

from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.qris_mock import MockQrisProvider


def crash_checkout(root, boundary):
    root = Path(root)
    provider = MockQrisProvider(root / 'provider.sqlite', scenario='pending', now=lambda: 1000)
    store = CheckoutStore(root / 'orders.sqlite', now=lambda: 1000)
    original = provider.create_qris
    if boundary == 'prepared':
        def stop_before_send(*_args):
            os._exit(73)
        store.mark_creation_sent = stop_before_send

    def interrupted(order_id, amount):
        if boundary == 'before_send':
            os._exit(71)
        original(order_id, amount)
        os._exit(72)

    provider.create_qris = interrupted
    CheckoutBackend(store, provider, 'offline-fixture', 'MOCK').create_order(
        'PB001', {'template_a': 2}, 'a' * 32)
    raise AssertionError('Crash boundary was not reached')


if __name__ == '__main__':
    crash_checkout(*sys.argv[1:])
