"""FEAT-020 durable sandbox order state; not a public payment API.

Only an authenticated server-side provider adapter may call confirm_provider_status.
This module does not verify provider signatures or transfer money.
"""
import json
import sqlite3
import uuid
import threading
from pathlib import Path


class OrderStore:
    """Persist orders and grant each paid order to its booth at most once."""

    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.db = sqlite3.connect(path, timeout=15, isolation_level=None,
                                  check_same_thread=False)
        self.db.execute('PRAGMA busy_timeout=15000')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY, booth_id TEXT NOT NULL,
            quantities TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>0),
            provider_ref TEXT UNIQUE, state TEXT NOT NULL,
            claimed INTEGER NOT NULL DEFAULT 0 CHECK(claimed IN (0,1))
        )''')

    def create(self, booth_id, quantities, amount):
        with self._lock:
            """Call only with server-validated pricing and template quantities."""
            if not isinstance(booth_id, str) or not booth_id.strip():
                raise ValueError('booth_id required')
            if type(amount) is not int or amount <= 0:
                raise ValueError('positive integer amount required')
            if not isinstance(quantities, dict) or not quantities:
                raise ValueError('validated quantities required')
            order_id = uuid.uuid4().hex
            self.db.execute('INSERT INTO orders(id,booth_id,quantities,amount,state) VALUES(?,?,?,?,?)',
                            (order_id, booth_id, json.dumps(quantities, sort_keys=True), amount, 'CREATED'))
            return order_id

    def attach_provider(self, order_id, provider_ref):
        with self._lock:
            """Bind one gateway transaction; no replacement of a pending QR."""
            if not isinstance(provider_ref, str) or not provider_ref.strip():
                raise ValueError('provider_ref required')
            with self.db:
                changed = self.db.execute('UPDATE orders SET provider_ref=?,state=? '
                                          'WHERE id=? AND state=? AND provider_ref IS NULL',
                                          (provider_ref, 'PENDING', order_id, 'CREATED'))
                if changed.rowcount != 1:
                    raise RuntimeError('Order cannot attach another provider transaction')

    def confirm_provider_status(self, order_id, provider_ref, amount, status):
        with self._lock:
            """INTERNAL ONLY: caller must independently verify provider response."""
            if status != 'settlement' or type(amount) is not int:
                return False
            with self.db:
                changed = self.db.execute('UPDATE orders SET state=? WHERE id=? '
                                          'AND provider_ref=? AND amount=? AND state=?',
                                          ('PAID', order_id, provider_ref, amount, 'PENDING'))
                if changed.rowcount == 1:
                    return True
                row = self.db.execute('SELECT state,amount,provider_ref FROM orders WHERE id=?',
                                      (order_id,)).fetchone()
                return row == ('PAID', amount, provider_ref)

    def claim(self, order_id, booth_id):
        with self._lock:
            """Atomic, one-time session claim; booth authentication is external."""
            with self.db:
                changed = self.db.execute('UPDATE orders SET claimed=1 WHERE id=? AND booth_id=? '
                                          'AND state=? AND claimed=0',
                                          (order_id, booth_id, 'PAID'))
                return changed.rowcount == 1

    def status(self, order_id, booth_id):
        with self._lock:
            row = self.db.execute('SELECT state,claimed FROM orders WHERE id=? AND booth_id=?',
                                  (order_id, booth_id)).fetchone()
            return {'state': row[0], 'claimed': bool(row[1])} if row else None

    def close(self):
        with self._lock:
            self.db.close()
