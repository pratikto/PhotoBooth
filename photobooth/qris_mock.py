"""Persistent, explicitly non-payable provider for main-GUI offline trials.

No network, bank account or merchant API is used. Simulation is available only
when the server and kiosk BOTH explicitly select mock mode.
"""
from datetime import datetime, timezone
import sqlite3
import threading
import time
from pathlib import Path


class MockQrisProvider:
    mode = 'mock'
    merchant_id = 'MOCK'

    def __init__(self, path, *, settle_after=8, scenario='settlement', now=time.time):
        if not 0 <= settle_after <= 300 or scenario not in {'settlement', 'expire', 'deny', 'pending'}:
            raise ValueError('Invalid mock scenario')
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.db.execute('CREATE TABLE IF NOT EXISTS mock_orders(id TEXT PRIMARY KEY,amount INTEGER,created REAL,state TEXT)')
        self.lock = threading.RLock()
        self.delay, self.scenario, self.now = settle_after, scenario, now

    def create_qris(self, order_id, amount):
        with self.lock:
            self.db.execute('INSERT OR IGNORE INTO mock_orders VALUES(?,?,?,?)',
                            (order_id, amount, self.now(), 'pending'))
            return self.get_status(order_id)

    def get_status(self, order_id):
        with self.lock:
            row = self.db.execute('SELECT amount,created,state FROM mock_orders WHERE id=?', (order_id,)).fetchone()
            if row is None:
                raise ValueError('Mock order not found')
            amount, created, state = row
            if state == 'pending' and self.now() - created >= self.delay:
                state = self.scenario
                self.db.execute('UPDATE mock_orders SET state=? WHERE id=?', (state, order_id))
            return {'order_id': order_id, 'gross_amount': str(amount), 'currency': 'IDR',
                    'payment_type': 'qris', 'merchant_id': 'MOCK', 'transaction_id': 'mock-' + order_id,
                    'transaction_status': state, 'status_code': '200' if state == 'settlement' else '201',
                    'fraud_status': 'accept',
                    'expiry_time': datetime.fromtimestamp(created + 300, timezone.utc).isoformat()}

    def cancel(self, order_id):
        with self.lock:
            status = self.get_status(order_id)
            if status['transaction_status'] == 'pending':
                self.db.execute("UPDATE mock_orders SET state='cancel' WHERE id=?", (order_id,))
            return self.get_status(order_id)

    def close(self):
        with self.lock:
            self.db.close()
