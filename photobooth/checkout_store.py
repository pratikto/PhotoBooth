"""Durable FEAT-020 checkout and service-grant ledger (server-side only).

A checkout key identifies one visit, not an amount. All multi-statement writes
use BEGIN IMMEDIATE so independent server connections obey the same rules.
Only the trusted provider service may call apply_evidence; no HTTP request is
allowed to supply payment evidence directly.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import threading
import time
import uuid


class CheckoutConflict(ValueError):
    """The visit or service is already bound to different immutable data."""


class CheckoutMissing(LookupError):
    """Do not disclose another booth's order."""


def identifier(value, *, minimum=1, maximum=64):
    if (not isinstance(value, str) or not minimum <= len(value) <= maximum
            or re.fullmatch(r'[A-Za-z0-9_-]+', value) is None):
        raise ValueError('Invalid identifier')
    return value


class CheckoutStore:
    def __init__(self, path, *, now=time.time):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.now = now
        self.lock = threading.RLock()
        self.db = sqlite3.connect(path, timeout=10, isolation_level=None,
                                  check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS checkouts (
            id TEXT PRIMARY KEY, booth_id TEXT NOT NULL, checkout_key TEXT NOT NULL,
            quantities TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>0),
            state TEXT NOT NULL DEFAULT 'CREATED', created_at REAL NOT NULL,
            expires_at REAL, qr_url TEXT, provider_ref TEXT UNIQUE, merchant_id TEXT,
            grant_id TEXT UNIQUE, service_state TEXT NOT NULL DEFAULT 'NONE',
            local_transaction_id TEXT, closed INTEGER NOT NULL DEFAULT 0,
            check_after REAL NOT NULL DEFAULT 0, verified_at REAL,
            UNIQUE(booth_id,checkout_key));
          CREATE TABLE IF NOT EXISTS checkout_events (
            event_id TEXT PRIMARY KEY, order_id TEXT NOT NULL,
            provider_state TEXT NOT NULL, outcome TEXT NOT NULL,
            received_at REAL NOT NULL, updated_at REAL NOT NULL);
          CREATE TABLE IF NOT EXISTS checkout_recovery_actions (
            action_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, booth_id TEXT NOT NULL,
            request_hash TEXT NOT NULL, action TEXT NOT NULL, reason TEXT NOT NULL,
            transaction_id TEXT, actor TEXT NOT NULL, created_at REAL NOT NULL,
            prior_payment_state TEXT NOT NULL, prior_service_state TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS checkout_recovery_order_action
            ON checkout_recovery_actions(order_id,action);
        ''')
        # Never silently forget unresolved orders from the earlier prototype.
        if self.db.execute("SELECT 1 FROM sqlite_master WHERE name='orders'").fetchone():
            with self.write():
                for old in self.db.execute('SELECT * FROM orders').fetchall():
                    self.db.execute('''INSERT OR IGNORE INTO checkouts
                        (id,booth_id,checkout_key,quantities,amount,state,created_at,service_state)
                        VALUES(?,?,?,?,?,'REVIEW_REQUIRED',?,'REVIEW_REQUIRED')''',
                        (old['id'], old['booth_id'], 'legacy-' + old['id'],
                         old['quantities'], old['amount'], self.now()))

    @contextmanager
    def write(self):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                yield
            except BaseException:
                self.db.rollback()
                raise
            else:
                self.db.commit()

    @staticmethod
    def _record(row):
        if row is None:
            raise CheckoutMissing('Order not found')
        result = dict(row)
        result['quantities'] = json.loads(result['quantities'])
        return result

    def _row(self, order_id, booth_id=None):
        query, args = 'SELECT * FROM checkouts WHERE id=?', [order_id]
        if booth_id is not None:
            query += ' AND booth_id=?'
            args.append(booth_id)
        return self._record(self.db.execute(query, args).fetchone())

    def get(self, order_id, booth_id=None):
        with self.lock:
            return self._row(order_id, booth_id)

    def recovery_abandoned(self, order_id):
        with self.lock:
            return self.db.execute("SELECT 1 FROM checkout_recovery_actions WHERE order_id=? AND action='abandon'",
                                   (order_id,)).fetchone() is not None

    def recovery_action_applied(self, order_id, booth_id, action_id, action, reason, transaction_id):
        """Acknowledge only the exact previously committed decision, never reapply it."""
        payload = json.dumps([order_id, booth_id, action, reason, transaction_id], separators=(',', ':'))
        digest = hashlib.sha256(payload.encode()).hexdigest()
        with self.lock:
            self._row(order_id, booth_id)
            old = self.db.execute('SELECT request_hash FROM checkout_recovery_actions WHERE action_id=?',
                                  (action_id,)).fetchone()
            if old is not None and old['request_hash'] != digest:
                raise CheckoutConflict('Recovery action identity mismatch')
            return old is not None

    def begin(self, booth_id, quantities, amount, checkout_key):
        identifier(booth_id)
        identifier(checkout_key, minimum=16)
        if type(amount) is not int or amount <= 0 or not isinstance(quantities, dict):
            raise ValueError('Server-validated quote required')
        encoded = json.dumps(quantities, sort_keys=True, separators=(',', ':'))
        with self.write():
            old = self.db.execute('SELECT * FROM checkouts WHERE booth_id=? AND checkout_key=?',
                                  (booth_id, checkout_key)).fetchone()
            if old:
                if old['quantities'] != encoded or old['amount'] != amount:
                    raise CheckoutConflict('Checkout key cannot change its order')
                return self._record(old), False
            active = self.db.execute('''SELECT 1 FROM checkouts WHERE booth_id=?
                AND closed=0 AND state NOT IN ('EXPIRED','CANCELLED','FAILED')
                AND service_state!='COMPLETED' ''', (booth_id,)).fetchone()
            if active:
                raise CheckoutConflict('Resolve the previous checkout before another visit')
            order_id = uuid.uuid4().hex
            self.db.execute('''INSERT INTO checkouts
                (id,booth_id,checkout_key,quantities,amount,created_at) VALUES(?,?,?,?,?,?)''',
                (order_id, booth_id, checkout_key, encoded, amount, self.now()))
            return self._row(order_id), True

    def apply_evidence(self, order_id, evidence):
        """Apply independently fetched evidence, never a kiosk/body PAID flag."""
        mapping = {'pending': 'PENDING', 'settlement': 'PAID', 'expire': 'EXPIRED',
                   'cancel': 'CANCELLED', 'deny': 'FAILED', 'failure': 'FAILED',
                   'refund': 'REVIEW_REQUIRED', 'partial_refund': 'REVIEW_REQUIRED'}
        state = mapping[evidence['transaction_status']]
        with self.write():
            old = self._row(order_id)
            if (evidence['order_id'] != order_id or evidence['amount'] != old['amount']
                    or (old['provider_ref'] and old['provider_ref'] != evidence['transaction_id'])
                    or (old['merchant_id'] and old['merchant_id'] != evidence['merchant_id'])):
                raise CheckoutConflict('Provider evidence does not match this order')
            # A late success belongs to the old visit, never the next customer.
            if state == 'PAID' and (old['closed'] or old['state'] in
                                    {'EXPIRED', 'CANCELLED', 'FAILED', 'REVIEW_REQUIRED'}):
                state = 'REVIEW_REQUIRED'
            if old['state'] == 'REVIEW_REQUIRED':
                state = 'REVIEW_REQUIRED'
            elif old['state'] == 'PAID' and state != 'REVIEW_REQUIRED':
                state = 'PAID'
            elif old['state'] in {'EXPIRED', 'CANCELLED', 'FAILED'} and state == 'PENDING':
                state = old['state']
            self.db.execute('''UPDATE checkouts SET state=?,provider_ref=?,merchant_id=?,
                expires_at=COALESCE(?,expires_at),verified_at=? WHERE id=?''',
                (state, evidence['transaction_id'], evidence['merchant_id'],
                 evidence.get('expires_at'), self.now(), order_id))
            return self._row(order_id)

    def save_qr(self, order_id, url):
        with self.write():
            self.db.execute('UPDATE checkouts SET qr_url=? WHERE id=?', (url, order_id))

    def reserve_check(self, order_id, *, interval=3):
        with self.write():
            changed = self.db.execute('UPDATE checkouts SET check_after=? WHERE id=? AND check_after<=?',
                                      (self.now() + interval, order_id, self.now()))
            return changed.rowcount == 1

    def grant(self, order_id, booth_id, checkout_key):
        """Replay the SAME durable permit after a lost response or restart."""
        with self.write():
            order = self._row(order_id, booth_id)
            if (order['checkout_key'] != checkout_key or order['state'] != 'PAID'
                    or order['closed']):
                raise CheckoutConflict('Order is not eligible for this visit')
            if not order['grant_id']:
                self.db.execute('''UPDATE checkouts SET grant_id=?,service_state='RESERVED'
                                   WHERE id=?''', (uuid.uuid4().hex, order_id))
            return self._row(order_id, booth_id)

    def service_transition(self, order_id, booth_id, grant_id, state, local_transaction_id):
        identifier(local_transaction_id)
        with self.write():
            order = self._row(order_id, booth_id)
            if (not grant_id or order['grant_id'] != grant_id or order['state'] != 'PAID' or order['closed']
                    or (order['local_transaction_id'] and
                        order['local_transaction_id'] != local_transaction_id)):
                raise CheckoutConflict('Service permit mismatch')
            allowed = {'STARTED': {'RESERVED', 'STARTED'},
                       'COMPLETED': {'STARTED', 'COMPLETED'}}
            if state not in allowed or order['service_state'] not in allowed[state]:
                raise CheckoutConflict('Invalid service transition')
            self.db.execute('''UPDATE checkouts SET service_state=?,local_transaction_id=?
                               WHERE id=?''', (state, local_transaction_id, order_id))
            return self._row(order_id, booth_id)

    def recovery_action(self, order_id, booth_id, action_id, action, reason, transaction_id, actor):
        """Apply one operator decision atomically; retries never allocate another visit.

        The backend must fetch fresh provider evidence before entering here.
        Archival is a separate closed flag, not a fabricated payment/service end.
        """
        identifier(action_id, minimum=16)
        identifier(actor, maximum=96)
        if action not in {'reconcile', 'resume', 'abandon', 'complete'}:
            raise ValueError('Invalid recovery action')
        if (not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 160
                or any(ord(c) < 32 or ord(c) == 127 for c in reason)):
            raise ValueError('Recovery reason required')
        if transaction_id is not None:
            identifier(transaction_id)
        payload = json.dumps([order_id, booth_id, action, reason, transaction_id], separators=(',', ':'))
        digest = hashlib.sha256(payload.encode()).hexdigest()
        with self.write():
            order = self._row(order_id, booth_id)
            old = self.db.execute('SELECT * FROM checkout_recovery_actions WHERE action_id=?',
                                  (action_id,)).fetchone()
            if old:
                if old['request_hash'] != digest:
                    raise CheckoutConflict('Recovery action identity mismatch')
                return order, dict(old)
            if action == 'resume':
                if order['closed'] or order['state'] != 'PAID':
                    raise CheckoutConflict('Recovery cannot resume this payment')
                if order['service_state'] not in {'NONE', 'RESERVED', 'STARTED'}:
                    raise CheckoutConflict('Recovery cannot replay a completed service')
                if transaction_id is None:
                    if order['local_transaction_id'] or order['service_state'] == 'STARTED':
                        raise CheckoutConflict('Recovery must retain the existing capture')
                    grant = order['grant_id'] or uuid.uuid4().hex
                    self.db.execute("UPDATE checkouts SET grant_id=?,service_state='RESERVED' WHERE id=?",
                                    (grant, order_id))
                else:
                    if (not order['grant_id'] or order['service_state'] not in {'RESERVED', 'STARTED'}
                            or order['local_transaction_id'] not in (None, transaction_id)):
                        raise CheckoutConflict('Recovery capture identity mismatch')
                    self.db.execute("UPDATE checkouts SET service_state='STARTED',local_transaction_id=? WHERE id=?",
                                    (transaction_id, order_id))
            elif action == 'complete':
                if (order['closed'] or order['state'] != 'PAID' or not order['grant_id']
                        or order['service_state'] not in {'STARTED', 'COMPLETED'}
                        or not transaction_id or order['local_transaction_id'] != transaction_id):
                    raise CheckoutConflict('Recovery completion identity mismatch')
                self.db.execute("UPDATE checkouts SET service_state='COMPLETED' WHERE id=?", (order_id,))
            elif action == 'abandon':
                if order['closed'] or order['service_state'] == 'COMPLETED':
                    raise CheckoutConflict('This test visit already ended')
                self.db.execute('UPDATE checkouts SET closed=1 WHERE id=?', (order_id,))
            self.db.execute('''INSERT INTO checkout_recovery_actions
                (action_id,order_id,booth_id,request_hash,action,reason,transaction_id,actor,
                 created_at,prior_payment_state,prior_service_state) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
                (action_id, order_id, booth_id, digest, action, reason, transaction_id, actor,
                 self.now(), order['state'], order['service_state']))
            record = dict(self.db.execute('SELECT * FROM checkout_recovery_actions WHERE action_id=?',
                                         (action_id,)).fetchone())
            return self._row(order_id, booth_id), record

    def close_visit(self, order_id, booth_id):
        with self.write():
            order = self._row(order_id, booth_id)
            if order['state'] not in {'EXPIRED', 'CANCELLED', 'FAILED'}:
                raise CheckoutConflict('Provider has not confirmed the end of payment')
            self.db.execute('UPDATE checkouts SET closed=1 WHERE id=?', (order_id,))

    def event(self, payload, outcome):
        """Store only a digest/correlation/status, not credentials or raw PII."""
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        with self.write():
            self.db.execute('''INSERT INTO checkout_events VALUES(?,?,?,?,?,?)
                ON CONFLICT(event_id) DO UPDATE SET outcome=excluded.outcome,
                updated_at=excluded.updated_at''',
                (digest, payload['order_id'], payload.get('transaction_status', 'unknown'),
                 outcome, self.now(), self.now()))
        return digest

    def close(self):
        with self.lock:
            self.db.close()
