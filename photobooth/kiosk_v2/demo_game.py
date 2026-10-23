"""Durable, isolated DEMO attempts. No scanner, merchant validation or money."""

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from pathlib import Path
import queue
import re
import sqlite3
import threading
import uuid

from .game_engine import TARGET_SCORE

LOG = logging.getLogger(__name__)


class DemoClaimError(ValueError):
    pass


class DemoGameStore:
    def __init__(self, root):
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / 'demo-attempts.sqlite3'
        with closing(self._connect()) as db, db:
            db.execute('''CREATE TABLE IF NOT EXISTS attempts (
                token TEXT PRIMARY KEY, attempt_id TEXT UNIQUE NOT NULL,
                result TEXT NOT NULL, score INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL, ended_at TEXT)''')

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=2)
        db.row_factory = sqlite3.Row
        return db

    def claim(self, token):
        if not isinstance(token, str) or not re.fullmatch(r'DEMO-[A-Z0-9][A-Z0-9-]{0,63}', token.strip().upper()):
            raise DemoClaimError('invalid')
        token = token.strip().upper()
        attempt = uuid.uuid4().hex
        with closing(self._connect()) as db, db:
            changed = db.execute(
                "INSERT OR IGNORE INTO attempts VALUES (?, ?, 'started', 0, ?, NULL)",
                (token, attempt, datetime.now(timezone.utc).isoformat())).rowcount
            if changed != 1:
                raise DemoClaimError('used')
        return self.get(attempt)

    def get(self, attempt_id):
        with closing(self._connect()) as db:
            row = db.execute('SELECT * FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
        if row is None:
            raise DemoClaimError('unknown')
        return dict(row)

    def finish(self, attempt_id, result, score):
        if (result not in {'won', 'lost', 'abandoned'} or type(score) is not int or not 0 <= score <= 10000 or
                (result == 'won' and score < TARGET_SCORE) or (result == 'lost' and score >= TARGET_SCORE)):
            raise DemoClaimError('invalid-result')
        with closing(self._connect()) as db, db:
            changed = db.execute(
                "UPDATE attempts SET result=?,score=?,ended_at=? WHERE attempt_id=? AND result='started'",
                (result, score, datetime.now(timezone.utc).isoformat(), attempt_id)).rowcount
            row = db.execute('SELECT * FROM attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            if row is None or (not changed and (row['result'], row['score']) != (result, score)):
                raise DemoClaimError('conflicting-result')
        return dict(row)


@dataclass(frozen=True)
class GameOutcome:
    action: str
    revision: int
    value: dict | None = None
    error: str | None = None


class GameJobs:
    """Single-flight I/O; results are polled, never delivered into retired pages."""

    def __init__(self, factory):
        self._factory, self.store = factory, None
        self._results = queue.Queue(maxsize=1)
        self._thread = None
        self._closed = False
        self.busy = False

    def submit(self, action, revision, *args):
        if self._closed or self.busy or action not in {'claim', 'finish'}:
            return False
        self.busy = True
        def run():
            try:
                if self.store is None:
                    self.store = self._factory()
                value = getattr(self.store, action)(*args)
                result = GameOutcome(action, revision, value)
            except DemoClaimError as error:
                result = GameOutcome(action, revision, error=str(error))
            except Exception:
                LOG.warning('DEMO game storage unavailable action=%s', action, exc_info=True)
                result = GameOutcome(action, revision, error='unavailable')
            if not self._closed:
                self._results.put(result)
        self._thread = threading.Thread(target=run, name='portrait-v2-game-io', daemon=True)
        self._thread.start()
        return True

    def poll(self):
        try:
            result = self._results.get_nowait()
        except queue.Empty:
            return None
        self.busy = False
        return result

    def close(self):
        self._closed = True

    def wait_closed(self, timeout=3):
        if self._thread is not None:
            self._thread.join(timeout=timeout)
