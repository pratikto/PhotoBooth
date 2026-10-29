"""Explicit, unmounted delivery schema/read adapter; no issuance or effects."""
import json

from photobooth.checkout_store import CheckoutConflict, CheckoutMissing, identifier


class DeliveryRequirements:
    """Missing requirements are unspecified, never permission or fulfillment.

    Initialization is explicit; ordinary CheckoutStore/HTTP/GUI never calls it.
    Issuance must later join original new-order creation in one transaction.
    """
    def __init__(self, store):
        self.store = store
        with store.write():
            store.db.execute('''CREATE TABLE IF NOT EXISTS checkout_delivery_requirements (
                order_id TEXT PRIMARY KEY, requirement_id TEXT UNIQUE NOT NULL,
                version INTEGER NOT NULL CHECK(version=1),
                policy TEXT NOT NULL CHECK(policy='PRINT_REQUIRED_V1'),
                booth_id TEXT NOT NULL, merchant_id TEXT NOT NULL,
                contract_hash TEXT NOT NULL, copies_json TEXT NOT NULL,
                created_at REAL NOT NULL)''')

    def get(self, order_id, booth_id, merchant_id):
        identifier(merchant_id)
        with self.store.lock:
            order = self.store.get(order_id, booth_id)
            context = self.store.db.execute(
                'SELECT merchant_id FROM checkout_create_attempts WHERE order_id=?',
                (order_id,)).fetchone()
            if (context is None or context['merchant_id'] != merchant_id
                    or order['merchant_id'] not in (None, merchant_id)):
                raise CheckoutMissing('Order not found')
            row = self.store.db.execute(
                'SELECT * FROM checkout_delivery_requirements WHERE order_id=?',
                (order_id,)).fetchone()
            if row is None:
                return None
            record = dict(row)
            try:
                contract = self.store.frozen_order(order_id)
                frozen = self.store.db.execute(
                    'SELECT contract_hash FROM checkout_frozen_orders WHERE order_id=?',
                    (order_id,)).fetchone()
                copies = json.loads(record['copies_json'])
                quantities = contract['quantities']
                templates = contract['templates']
                valid = (record['version'] == 1 and record['policy'] == 'PRINT_REQUIRED_V1'
                    and record['booth_id'] == booth_id and record['merchant_id'] == merchant_id
                    and record['contract_hash'] == frozen['contract_hash']
                    and type(contract['version']) is int and contract['version'] == 1
                    and quantities == order['quantities']
                    and contract['amount'] == order['amount'] and copies == quantities
                    and isinstance(copies, dict) and bool(copies)
                    and all(type(n) is int and n > 0 for n in copies.values())
                    and type(contract['print_copy_count']) is int
                    and contract['print_copy_count'] == sum(copies.values())
                    and len(templates) == len(copies)
                    and all(type(t['copies']) is int for t in templates)
                    and {t['template_id']:t['copies'] for t in templates} == copies)
                if not valid:
                    raise ValueError('Requirement mismatch')
            except (ValueError, TypeError, KeyError, CheckoutConflict) as error:
                raise CheckoutConflict('Delivery requirement needs review') from error
            record.pop('copies_json')
            record['copies'] = copies
            return record
