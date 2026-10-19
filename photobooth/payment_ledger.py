"""Crash-safe local payment session claims for FEAT-020 mock development.

This module never confirms a bank payment. Only a future trusted backend may
supply verified=True after checking provider identity, amount and transaction.
"""

import sqlite3
from pathlib import Path


class PaymentLedger:
    """Persist an immutable paid order and claim its photo session once."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path), timeout=10)
        self.connection.execute('PRAGMA busy_timeout=10000')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS payment_claims (
            order_id TEXT PRIMARY KEY, amount INTEGER NOT NULL,
            provider_ref TEXT NOT NULL UNIQUE, session_claimed INTEGER NOT NULL DEFAULT 0,
            CHECK(amount > 0), CHECK(session_claimed IN (0,1))
        )''')
        self.connection.commit()

    def record_verified(self, order_id, amount, provider_ref, *, verified=False):
        """Mock-only seam: caller must eventually be a trusted backend, never UI."""
        if verified is not True:
            raise PermissionError('Trusted backend verification is required')
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError('order_id required')
        if type(amount) is not int or amount <= 0:
            raise ValueError('positive integer amount required')
        if not isinstance(provider_ref, str) or not provider_ref.strip():
            raise ValueError('provider_ref required')
        with self.connection:
            existing = self.connection.execute(
                'SELECT amount, provider_ref FROM payment_claims WHERE order_id=?',
                (order_id,)).fetchone()
            if existing:
                if existing != (amount, provider_ref):
                    raise ValueError('Conflicting payment evidence')
                return False
            self.connection.execute(
                'INSERT INTO payment_claims(order_id,amount,provider_ref) VALUES(?,?,?)',
                (order_id, amount, provider_ref))
            return True

    def claim_session(self, order_id):
        """Atomically grant one photo session; repeat calls cannot grant another."""
        with self.connection:
            cursor = self.connection.execute(
                'UPDATE payment_claims SET session_claimed=1 '
                'WHERE order_id=? AND session_claimed=0', (order_id,))
            return cursor.rowcount == 1

    def close(self):
        self.connection.close()
