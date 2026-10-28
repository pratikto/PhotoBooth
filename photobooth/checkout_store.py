"""Durable FEAT-020 checkout and service-grant ledger (server-side only).

A checkout key identifies one visit, not an amount. All multi-statement writes
use BEGIN IMMEDIATE so independent server connections obey the same rules.
Only the trusted provider service may call apply_evidence; no HTTP request is
allowed to supply payment evidence directly.
"""
from contextlib import contextmanager
import hashlib
import json
import math
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
          CREATE TABLE IF NOT EXISTS checkout_create_attempts (
            order_id TEXT PRIMARY KEY, version INTEGER NOT NULL DEFAULT 1,
            merchant_id TEXT, provider_mode TEXT, request_hash TEXT,
            phase TEXT NOT NULL CHECK(phase IN
              ('PREPARED','SENT','UNCERTAIN','VERIFIED','LEGACY_UNCERTAIN')),
            prepared_at REAL, sent_at REAL, verified_at REAL, updated_at REAL NOT NULL);
          CREATE TABLE IF NOT EXISTS checkout_reconciliation (
            order_id TEXT PRIMARY KEY, generation INTEGER NOT NULL DEFAULT 0,
            token TEXT, lease_until REAL NOT NULL DEFAULT 0,
            next_at REAL NOT NULL DEFAULT 0, failures INTEGER NOT NULL DEFAULT 0,
            evidence_revision INTEGER NOT NULL DEFAULT 0,
            checked_at REAL, outcome TEXT NOT NULL DEFAULT 'unknown',
            provider_state TEXT, observed_at REAL NOT NULL DEFAULT 0);
        ''')
        # AR-02.c is additive for the already published scheduler schema.
        with self.write():
            columns = {row['name'] for row in self.db.execute('PRAGMA table_info(checkout_reconciliation)')}
            if 'priority_after' not in columns:
                self.db.execute('ALTER TABLE checkout_reconciliation ADD COLUMN priority_after REAL NOT NULL DEFAULT 0')
        # Never silently forget unresolved orders from the earlier prototype.
        if self.db.execute("SELECT 1 FROM sqlite_master WHERE name='orders'").fetchone():
            with self.write():
                for old in self.db.execute('SELECT * FROM orders').fetchall():
                    self.db.execute('''INSERT OR IGNORE INTO checkouts
                        (id,booth_id,checkout_key,quantities,amount,state,created_at,service_state)
                        VALUES(?,?,?,?,?,'REVIEW_REQUIRED',?,'REVIEW_REQUIRED')''',
                        (old['id'], old['booth_id'], 'legacy-' + old['id'],
                         old['quantities'], old['amount'], self.now()))
        # Additive migration: absence of an attempt never proves POST was not
        # sent. Keep old payment/service bytes and IDs intact, including rows
        # written by older source during a rollback. Never synthesize PREPARED.
        with self.write():
            self.db.execute('''INSERT OR IGNORE INTO checkout_create_attempts
                (order_id,merchant_id,phase,updated_at)
                SELECT id,merchant_id,'LEGACY_UNCERTAIN',? FROM checkouts''', (self.now(),))

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

    @staticmethod
    def _creation_hash(order, merchant_id, provider_mode):
        identifier(merchant_id)
        if provider_mode not in {'sandbox', 'mock'}:
            raise ValueError('Only test payment environments are supported')
        # Freeze both the exact Legacy charge body and its local ownership.
        # This internal fingerprint is not a speculative provider header/key.
        payload = {'version': 1, 'merchant_id': merchant_id, 'provider_mode': provider_mode,
                   'booth_id': order['booth_id'], 'checkout_key': order['checkout_key'],
                   'quantities': order['quantities'], 'currency': 'IDR',
                   'charge': {'payment_type': 'qris', 'transaction_details':
                              {'order_id': order['id'], 'gross_amount': order['amount']}}}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def creation_attempt(self, order_id):
        with self.lock:
            row = self.db.execute('SELECT * FROM checkout_create_attempts WHERE order_id=?',
                                  (order_id,)).fetchone()
            if row is None:
                raise CheckoutMissing('Creation attempt not found')
            return dict(row)

    def validate_creation_context(self, order_id, merchant_id, provider_mode):
        with self.write():
            order = self._row(order_id)
            digest = self._creation_hash(order, merchant_id, provider_mode)
            if order['merchant_id'] and order['merchant_id'] != merchant_id:
                raise CheckoutConflict('Checkout merchant mismatch')
            self.db.execute('''INSERT OR IGNORE INTO checkout_create_attempts
                (order_id,merchant_id,phase,updated_at) VALUES(?,?,'LEGACY_UNCERTAIN',?)''',
                (order_id, order['merchant_id'], self.now()))
            attempt = self.creation_attempt(order_id)
            if (attempt['version'] != 1
                    or attempt['merchant_id'] not in (None, merchant_id)
                    or attempt['provider_mode'] not in (None, provider_mode)
                    or (attempt['request_hash'] is not None and attempt['request_hash'] != digest)):
                raise CheckoutConflict('Creation request identity mismatch')
            return attempt

    def mark_creation_sent(self, order_id, merchant_id, provider_mode):
        # Only the original new-order request may call this CAS. Restarts and
        # duplicate checkout requests reconcile via GET, even for PREPARED.
        self.validate_creation_context(order_id, merchant_id, provider_mode)
        with self.write():
            order = self._row(order_id)
            digest = self._creation_hash(order, merchant_id, provider_mode)
            changed = self.db.execute('''UPDATE checkout_create_attempts
                SET phase='SENT',sent_at=?,updated_at=?
                WHERE order_id=? AND phase='PREPARED' AND request_hash=?
                AND merchant_id=? AND provider_mode=?''',
                (self.now(), self.now(), order_id, digest, merchant_id, provider_mode))
            return changed.rowcount == 1

    def mark_creation_uncertain(self, order_id):
        with self.write():
            # A QR/display error after verified evidence cannot undo that proof.
            self.db.execute('''UPDATE checkout_create_attempts SET phase='UNCERTAIN',updated_at=?
                WHERE order_id=? AND phase='SENT' ''', (self.now(), order_id))

    def begin(self, booth_id, quantities, amount, checkout_key, *, creation_context=None):
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
            if creation_context is not None:
                merchant_id, provider_mode = creation_context
                digest = self._creation_hash(self._row(order_id), merchant_id, provider_mode)
                self.db.execute('''INSERT INTO checkout_create_attempts
                    (order_id,merchant_id,provider_mode,request_hash,phase,prepared_at,updated_at)
                    VALUES(?,?,?,?,'PREPARED',?,?)''',
                    (order_id, merchant_id, provider_mode, digest, self.now(), self.now()))
            return self._row(order_id), True

    def apply_evidence(self, order_id, evidence):
        """Apply independently fetched evidence, never a kiosk/body PAID flag."""
        with self.write():
            return self._apply_evidence(order_id, evidence)

    def _apply_evidence(self, order_id, evidence):
        """Caller owns write transaction; reconciliation can commit proof atomically."""
        mapping = {'pending': 'PENDING', 'settlement': 'PAID', 'expire': 'EXPIRED',
                   'cancel': 'CANCELLED', 'deny': 'FAILED', 'failure': 'FAILED',
                   'refund': 'REVIEW_REQUIRED', 'partial_refund': 'REVIEW_REQUIRED'}
        state = mapping[evidence['transaction_status']]
        old = self._row(order_id)
        if (evidence['order_id'] != order_id or evidence['amount'] != old['amount']
                or (old['provider_ref'] and old['provider_ref'] != evidence['transaction_id'])
                or (old['merchant_id'] and old['merchant_id'] != evidence['merchant_id'])):
            raise CheckoutConflict('Provider evidence does not match this order')
        attempt = self.db.execute('SELECT merchant_id FROM checkout_create_attempts WHERE order_id=?',
                                  (order_id,)).fetchone()
        if attempt and attempt['merchant_id'] not in (None, evidence['merchant_id']):
            raise CheckoutConflict('Provider evidence merchant mismatch')
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
        self.db.execute('''UPDATE checkout_create_attempts
            SET phase='VERIFIED',verified_at=?,updated_at=? WHERE order_id=?''',
            (self.now(), self.now(), order_id))
        self.db.execute('INSERT OR IGNORE INTO checkout_reconciliation(order_id) VALUES(?)', (order_id,))
        self.db.execute('''UPDATE checkout_reconciliation
            SET evidence_revision=evidence_revision+1 WHERE order_id=?''', (order_id,))
        return self._row(order_id)

    def begin_reconciliation(self, order_id, *, urgent=False, immediate=False):
        """Reserve bounded GET outside the DB transaction; never reserve a charge."""
        with self.write():
            self._row(order_id)
            self.db.execute('INSERT OR IGNORE INTO checkout_reconciliation(order_id) VALUES(?)', (order_id,))
            row = dict(self.db.execute('SELECT * FROM checkout_reconciliation WHERE order_id=?',
                                       (order_id,)).fetchone())
            now = self.now()
            if now < row['observed_at']:
                # Wall-clock rollback cannot make a distant deadline hold for
                # hours or turn a previous proof into a new permission.
                self.db.execute('''UPDATE checkout_reconciliation SET next_at=?,
                    lease_until=?,observed_at=? WHERE order_id=?''',
                    (now+10, now+45 if row['token'] else 0, now, order_id))
                return None
            priority = immediate and row['priority_after'] <= now
            if ((row['token'] and row['lease_until'] > now)
                    or (not urgent and not priority and row['next_at'] > now)
                    or (immediate and not priority)):
                return None
            token = uuid.uuid4().hex
            self.db.execute('''UPDATE checkout_reconciliation SET token=?,lease_until=?,
                generation=generation+1,observed_at=? WHERE order_id=?''', (token, now+45, now, order_id))
            if immediate:
                self.db.execute('UPDATE checkout_reconciliation SET priority_after=? WHERE order_id=?',
                                (now+10, order_id))
            return {'token': token, 'revision': row['evidence_revision']}

    def reconciliation_delay(self, order_id):
        with self.lock:
            row = self.db.execute('SELECT next_at,lease_until,token FROM checkout_reconciliation WHERE order_id=?',
                                  (order_id,)).fetchone()
            if row is None:
                return 0
            deadline = max(row['next_at'], row['lease_until'] if row['token'] else 0)
            return max(0, min(60, int(math.ceil(deadline-self.now()))))

    def finish_reconciliation(self, order_id, reservation, *, evidence=None, outcome='unknown', qr_url=None):
        with self.write():
            row = dict(self.db.execute('SELECT * FROM checkout_reconciliation WHERE order_id=?',
                                       (order_id,)).fetchone())
            if row['token'] != reservation['token'] or row['lease_until'] < self.now():
                return False
            if row['evidence_revision'] != reservation['revision']:
                # A notification/other verified read won while this GET was
                # in flight. Discard its stale result, including permission.
                evidence, outcome = None, 'unknown'
                accepted = False
            else:
                accepted = True
            if evidence is not None:
                self._apply_evidence(order_id, evidence)
                if qr_url is not None:
                    self.db.execute('UPDATE checkouts SET qr_url=? WHERE id=?', (qr_url, order_id))
                failures, delay = 0, 10
            else:
                failures = min(row['failures']+1, 1000)
                base = (10,20,40,60)[min(failures-1,3)]
                jitter = int(hashlib.sha256((order_id+str(row['generation'])).encode()).hexdigest()[:2],16)/255
                delay = min(60, base + jitter*base*.1)
            self.db.execute('''UPDATE checkout_reconciliation SET token=NULL,lease_until=0,
                next_at=?,failures=?,checked_at=?,outcome=?,provider_state=?,observed_at=? WHERE order_id=?''',
                (self.now()+delay, failures, self.now() if evidence is not None else None, outcome,
                 evidence['transaction_status'] if evidence is not None else None, self.now(), order_id))
            return accepted

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
