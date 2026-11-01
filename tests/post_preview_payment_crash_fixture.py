"""Persistent synthetic provider + abrupt child exits; never a network transport."""
import json
import os
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_store import DraftLease, PostPreviewStore


class PersistentSyntheticProvider:
    mode = 'mock'

    def __init__(self, path, *, fault=None):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS remote_orders
            (order_id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS remote_calls (kind TEXT NOT NULL);''')
        self.fault = fault

    def close(self):
        self.db.close()

    def crash(self, point):
        if self.fault == point:
            os._exit(73)

    def create_qris(self, order, amount):
        self.crash('before_remote_create')
        row = dict(order_id=order, gross_amount=str(amount), transaction_status='pending',
                   status_code='201', currency='IDR', payment_type='qris', merchant_id='MTEST',
                   transaction_id='fixture_'+order, fraud_status='accept')
        self.db.execute('BEGIN IMMEDIATE')
        self.db.execute('INSERT INTO remote_orders VALUES(?,?)', (order, json.dumps(row)))
        self.db.execute("INSERT INTO remote_calls VALUES('create')")
        self.db.commit()
        self.crash('after_remote_create')
        return row

    def get_status(self, order):
        row = self.db.execute('SELECT payload FROM remote_orders WHERE order_id=?', (order,)).fetchone()
        self.crash('after_remote_get')
        return json.loads(row[0]) if row else {'status_code': '404'}

    def state(self, order, state):
        row = self.get_status(order)
        row.update(transaction_status=state, status_code='200')
        self.db.execute('UPDATE remote_orders SET payload=? WHERE order_id=?', (json.dumps(row), order))

    def cancel(self, order):
        self.db.execute('BEGIN IMMEDIATE')
        self.state(order, 'cancel')
        self.db.execute("INSERT INTO remote_calls VALUES('cancel')")
        self.db.commit()
        self.crash('after_remote_cancel')
        return self.get_status(order)

    def count(self, kind):
        return self.db.execute('SELECT count(*) FROM remote_calls WHERE kind=?', (kind,)).fetchone()[0]


def main():
    db, provider_db, group, fault = sys.argv[1:]
    ledger = PostPreviewStore(db, now=lambda: 1000.0)
    provider = PersistentSyntheticProvider(provider_db, fault=fault)
    ready = ChargeReadiness(True, True, True, True, True, True, True, 25)
    payments = PostPreviewPayments(ledger, provider, 'MTEST', readiness=lambda _: ready, poll_seconds=0)
    with ledger.write():
        row, _ = payments._group(group, 'PB001')
        lease = DraftLease(row['draft_id'], 'PB001', row['visit_id'], row['generation'])
    if fault == 'after_prepare':
        payments._prepare(lease, observation=ready)
        os._exit(73)
    elif fault == 'after_remote_cancel':
        payments.signal_lifecycle(lease, 'USER_CANCEL')
    elif fault == 'after_remote_get':
        payments.reconcile(group, 'PB001', force=True)
    elif fault == 'after_inbox_claim':
        from photobooth.post_preview_inbox import PostPreviewNotificationInbox
        assert PostPreviewNotificationInbox(payments).claim() is not None
        os._exit(73)
    else:
        payments.begin(lease)
    raise RuntimeError('Fault point was not reached')


if __name__ == '__main__':
    main()
