"""Local MOCK authority. No network, payable QRIS, production PAID or money.

The SQLite ledger is the authority only inside this simulation. A real merchant
backend must independently validate receipts/results and calculate its quote.
"""

from contextlib import closing
import json
import os
from pathlib import Path
import re
import time
import uuid

from .demo_game import DemoClaimError, DemoGameStore
from .game_offer import demo_amount, is_demo_winner


class MockCheckoutError(DemoClaimError):
    pass


class MockCheckoutStore(DemoGameStore):
    def __init__(self, root, *, templates=None, pricing=None, clock=time.time):
        super().__init__(root)
        if templates is None:
            from photobooth.catalog import get_templates
            templates = get_templates()
        self.template_ids = {t if isinstance(t, str) else t.template_id for t in templates}
        if pricing is None:
            from photobooth.workflow import quote_order
            pricing = lambda quantities: quote_order(templates, quantities).total_amount
        self.pricing, self.clock = pricing, clock
        with closing(self._connect()) as db, db:
            db.execute('''CREATE TABLE IF NOT EXISTS mock_orders (
                order_id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL,
                payload TEXT NOT NULL, quantities TEXT NOT NULL,
                subtotal INTEGER NOT NULL, discount INTEGER NOT NULL, total INTEGER NOT NULL,
                attempt_id TEXT, state TEXT NOT NULL, expires REAL NOT NULL,
                admission_id TEXT UNIQUE)''')
            db.execute('''CREATE UNIQUE INDEX IF NOT EXISTS mock_promo_once
                ON mock_orders(attempt_id) WHERE attempt_id IS NOT NULL
                AND state NOT IN ('CANCELLED','EXPIRED')''')

    def _quantities(self, quantities):
        if (not isinstance(quantities, dict) or not quantities or
                any(key not in self.template_ids or type(value) is not int or not 0 <= value <= 9
                    for key, value in quantities.items())):
            raise MockCheckoutError('invalid-cart')
        result = {key: value for key, value in sorted(quantities.items()) if value}
        if not result:
            raise MockCheckoutError('empty-cart')
        return result

    def _expire(self, db):
        # UNKNOWN is deliberately not expired/cancelled without resolution.
        db.execute("UPDATE mock_orders SET state='EXPIRED' WHERE state='PENDING' AND expires<=?",
                   (self.clock(),))

    @staticmethod
    def _view(row):
        if row is None:
            raise MockCheckoutError('unknown-order')
        view = dict(row)
        view.pop('payload', None)
        view['quantities'] = json.loads(view['quantities'])
        view['mode'] = 'MOCK'
        view['qr_payload'] = 'MEONG MOCK ONLY - NOT QRIS - ' + view['order_id']
        return view

    def create(self, quantities, request_key, attempt_id=None):
        quantities = self._quantities(quantities)
        if not isinstance(request_key, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{16,80}', request_key):
            raise MockCheckoutError('invalid-key')
        if attempt_id is not None and not isinstance(attempt_id, str):
            raise MockCheckoutError('invalid-attempt')
        payload = json.dumps([quantities, attempt_id], sort_keys=True, separators=(',', ':'))
        with closing(self._connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self._expire(db)
            old = db.execute('SELECT * FROM mock_orders WHERE request_key=?', (request_key,)).fetchone()
            if old:
                if old['payload'] != payload:
                    raise MockCheckoutError('key-conflict')
                return self._view(old)
            if db.execute("SELECT 1 FROM mock_orders WHERE state IN ('PENDING','UNKNOWN','CONFIRMED')").fetchone():
                raise MockCheckoutError('outstanding-order')
            subtotal = self.pricing(quantities)
            if type(subtotal) is not int or subtotal <= 0:
                raise MockCheckoutError('invalid-quote')
            eligible = None
            if attempt_id:
                attempt = db.execute('SELECT * FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
                if attempt is None:
                    raise MockCheckoutError('invalid-attempt')
                if is_demo_winner(dict(attempt)):
                    eligible = attempt_id
            if eligible and db.execute("SELECT 1 FROM mock_orders WHERE attempt_id=? AND state NOT IN ('CANCELLED','EXPIRED')",
                                       (eligible,)).fetchone():
                raise MockCheckoutError('promo-used')
            amount = demo_amount(subtotal, eligible is not None)
            order_id = uuid.uuid4().hex
            db.execute('INSERT INTO mock_orders VALUES (?,?,?,?,?,?,?,?,?,?,NULL)',
                       (order_id, request_key, payload, json.dumps(quantities, sort_keys=True),
                        amount.subtotal, amount.discount, amount.total, eligible, 'PENDING', self.clock()+180))
            return self._view(db.execute('SELECT * FROM mock_orders WHERE order_id=?', (order_id,)).fetchone())

    def recover(self):
        with closing(self._connect()) as db, db:
            self._expire(db)
            row = db.execute("SELECT * FROM mock_orders WHERE state IN ('PENDING','UNKNOWN','CONFIRMED') ORDER BY rowid LIMIT 1").fetchone()
            return self._view(row) if row else None

    def open_checkout(self, quantities, request_key, attempt_id=None):
        old = self.recover()
        if old and old['request_key'] != request_key:
            return old  # Show the frozen outstanding cart; never create another order.
        try:
            return self.create(quantities, request_key, attempt_id)
        except MockCheckoutError as error:
            if str(error) == 'outstanding-order':
                old = self.recover()
                if old:
                    return old
            raise

    def status(self, order_id):
        with closing(self._connect()) as db, db:
            self._expire(db)
            return self._view(db.execute('SELECT * FROM mock_orders WHERE order_id=?', (order_id,)).fetchone())

    def transition(self, order_id, action):
        with closing(self._connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            self._expire(db)
            row = db.execute('SELECT * FROM mock_orders WHERE order_id=?', (order_id,)).fetchone()
            if row is None:
                raise MockCheckoutError('unknown-order')
            state = row['state']
            targets = {'confirm': 'CONFIRMED', 'unknown': 'UNKNOWN', 'reject': 'CANCELLED', 'cancel': 'CANCELLED'}
            if action not in targets:
                raise MockCheckoutError('invalid-action')
            target = targets[action]
            if state == target:
                return self._view(row)
            allowed = state == 'PENDING' or (state == 'UNKNOWN' and action in {'confirm', 'reject'})
            if not allowed:
                raise MockCheckoutError('unresolved' if state == 'UNKNOWN' else 'terminal-order')
            db.execute('UPDATE mock_orders SET state=? WHERE order_id=?', (target, order_id))
            return self._view(db.execute('SELECT * FROM mock_orders WHERE order_id=?', (order_id,)).fetchone())

    def admit(self, order_id):
        with closing(self._connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM mock_orders WHERE order_id=?', (order_id,)).fetchone()
            if row is None or row['state'] != 'CONFIRMED':
                raise MockCheckoutError('not-admissible')
            db.execute("UPDATE mock_orders SET state='ADMITTED',admission_id=? WHERE order_id=?",
                       (uuid.uuid4().hex, order_id))
            return self._view(db.execute('SELECT * FROM mock_orders WHERE order_id=?', (order_id,)).fetchone())


class MockCheckoutPresentation:
    """Worker-only QR encoding, separate from the pure persistence API."""

    def __init__(self, store, *, before_create=None):
        self.store = store
        self.before_create = before_create
        self._qr_cache = None

    def _present(self, view):
        if view and view['state'] == 'PENDING':
            if not self._qr_cache or self._qr_cache[0] != view['order_id']:
                import qrcode
                image = qrcode.make(view['qr_payload'], box_size=5, border=4).convert('RGB')
                self._qr_cache = (view['order_id'], (image.size, image.tobytes()))
            view['qr_rgb'] = self._qr_cache[1]
        return view

    def open_checkout(self, *args):
        # Health gates apply only to a new nonpayable simulation. Recover the
        # original outstanding cart even when today's printer is unavailable.
        # Store.open_checkout still owns idempotency, quote and cart validation.
        if self.before_create is not None and self.store.recover() is None:
            self.before_create()
        return self._present(self.store.open_checkout(*args))

    def status(self, *args):
        return self._present(self.store.status(*args))

    def transition(self, *args):
        return self._present(self.store.transition(*args))

    def admit(self, *args):
        return self._present(self.store.admit(*args))


def configured_mock_checkout(root, *, configuration_root):
    """Worker-only ordinary MOCK adapter; never a purchased QRIS payment path."""
    def check_new_order_printer():
        if os.environ.get('PHOTOBOOTH_V2_PRINT') != '1':
            return
        # No printer probes may be enabled through the isolated merchant trial.
        if os.environ.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX') == '1':
            raise MockCheckoutError('printer-not-ready')
        try:
            from photobooth.device_health import check_printer, READY
            from photobooth.printer_settings import load_printer_config
            config = load_printer_config(Path(configuration_root)/'data'/'printer_settings.json')
            if check_printer(config).status != READY:
                raise MockCheckoutError('printer-not-ready')
        except Exception:
            # Original platform adapters/configuration can fail with driver-
            # specific exception classes. Do not export/log their private text.
            raise MockCheckoutError('printer-not-ready') from None

    return MockCheckoutPresentation(MockCheckoutStore(root), before_create=check_new_order_printer)
