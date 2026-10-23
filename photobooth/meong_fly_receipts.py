"""Local demo-only one-attempt-per-receipt ledger; NOT merchant POS validation."""
import sqlite3
from contextlib import closing
from pathlib import Path


class DemoReceiptLedger:
    def __init__(self, path):
        self.path = str(Path(path))
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS attempts (receipt TEXT PRIMARY KEY, result TEXT NOT NULL)")

    def claim(self, receipt):
        """Atomically consume a demo voucher before gameplay; never allow replay."""
        if not receipt or not receipt.startswith("DEMO-") or len(receipt) > 100:
            return False
        with closing(sqlite3.connect(self.path, timeout=5)) as db, db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO attempts(receipt,result) VALUES (?, 'started')",
                (receipt,))
            return cursor.rowcount == 1

    def finish(self, receipt, won):
        """Store terminal result only; never issue a redeemable discount."""
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute(
                "UPDATE attempts SET result=? WHERE receipt=? AND result='started'",
                ("won" if won else "lost", receipt))
