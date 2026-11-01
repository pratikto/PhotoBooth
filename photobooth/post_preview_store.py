"""Private post_preview_v1 drafts, independent of legacy paid-first records.

This local ledger never grants payment, printer, Drive or booth-release authority.
Only the trusted worker coordinator may hold a DraftLease; it is not a customer
credential. The new route is deliberately not mounted in the customer GUI yet.
"""
from contextlib import contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
import threading
import time
import uuid

from photobooth.booth_storage import checked_path
from photobooth.checkout_store import CheckoutConflict, identifier
from photobooth.payment_quote import quote_checkout


ORDER_VERSION = 'post_preview_v1'
MAX_COPIES = 9  # New-order policy matches the existing gallery; legacy stays 10.
LIFECYCLE_EVENTS = frozenset({'USER_CANCEL', 'APP_SUSPENDED',
                             'INACTIVITY_WARNING', 'INACTIVITY_EXPIRED',
                             'VISIT_ABANDONED'})


def quote_post_preview(quantities):
    quote = quote_checkout(quantities)
    if any(count > MAX_COPIES for count in quantities.values()):
        raise ValueError('Post-preview copies must be from 1 to 9')
    return quote


@dataclass(frozen=True)
class DraftLease:
    draft_id: str
    booth_id: str
    visit_id: str
    generation: int


class DraftHeld(CheckoutConflict):
    """No mutation or private access until original ownership is established."""


class PostPreviewStore:
    def __init__(self, path, *, now=time.time):
        path = checked_path(Path(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        self.now = now
        self.lock = threading.RLock()
        self.db = sqlite3.connect(path, timeout=10, isolation_level=None,
                                  check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS pp_schema (
            singleton INTEGER PRIMARY KEY CHECK(singleton=1), version INTEGER NOT NULL);
          INSERT OR IGNORE INTO pp_schema VALUES(1,1);
        ''')
        if self.db.execute('SELECT version FROM pp_schema').fetchone()[0] != 1:
            self.db.close()
            raise DraftHeld('Unsupported private draft schema')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS pp_drafts (
            draft_id TEXT PRIMARY KEY, version TEXT NOT NULL,
            booth_id TEXT NOT NULL, visit_id TEXT NOT NULL,
            generation INTEGER NOT NULL DEFAULT 1,
            revision INTEGER NOT NULL DEFAULT 1,
            state TEXT NOT NULL DEFAULT 'OPEN',
            lifecycle TEXT NOT NULL DEFAULT 'ACTIVE',
            closed INTEGER NOT NULL DEFAULT 0 CHECK(closed IN (0,1)),
            created_at REAL NOT NULL, updated_at REAL NOT NULL,
            UNIQUE(booth_id,visit_id));
          CREATE UNIQUE INDEX IF NOT EXISTS pp_one_local_owner
            ON pp_drafts(booth_id) WHERE closed=0;
          CREATE TABLE IF NOT EXISTS pp_templates (
            draft_id TEXT NOT NULL REFERENCES pp_drafts(draft_id),
            template_id TEXT NOT NULL, lineage_id TEXT NOT NULL UNIQUE,
            selected INTEGER NOT NULL CHECK(selected IN (0,1)),
            copies INTEGER NOT NULL CHECK(copies BETWEEN 1 AND 9),
            retake_slot INTEGER CHECK(retake_slot BETWEEN 0 AND 2),
            retake_consumed INTEGER NOT NULL DEFAULT 0 CHECK(retake_consumed IN (0,1)),
            approved INTEGER NOT NULL DEFAULT 0 CHECK(approved IN (0,1)),
            PRIMARY KEY(draft_id,template_id));
          CREATE TABLE IF NOT EXISTS pp_events (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id TEXT NOT NULL REFERENCES pp_drafts(draft_id),
            event TEXT NOT NULL, created_at REAL NOT NULL);
        ''')

    def close(self):
        with self.lock:
            self.db.close()

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

    def create(self, booth_id, visit_id, quantities):
        identifier(booth_id)
        identifier(visit_id)
        quote_post_preview(quantities)
        with self.write():
            existing = self.db.execute('SELECT * FROM pp_drafts WHERE booth_id=? AND visit_id=?',
                                       (booth_id, visit_id)).fetchone()
            if existing:
                # Creation replay must not become a new capability after restart.
                raise DraftHeld('Original visit already has a private draft')
            if self.db.execute('SELECT 1 FROM pp_drafts WHERE booth_id=? AND closed=0',
                               (booth_id,)).fetchone():
                raise DraftHeld('Original local owner is unresolved')
            draft_id = uuid.uuid4().hex
            stamp = self.now()
            self.db.execute('''INSERT INTO pp_drafts
                (draft_id,version,booth_id,visit_id,created_at,updated_at) VALUES(?,?,?,?,?,?)''',
                (draft_id, ORDER_VERSION, booth_id, visit_id, stamp, stamp))
            self._cart(draft_id, quantities)
            self._event(draft_id, 'DRAFT_CREATED')
            return DraftLease(draft_id, booth_id, visit_id, 1)

    def _owned(self, lease, *, editable=False, revision=None):
        if not isinstance(lease, DraftLease):
            raise DraftHeld('Exact trusted worker lease required')
        row = self.db.execute('SELECT * FROM pp_drafts WHERE draft_id=?',
                              (lease.draft_id,)).fetchone()
        if (not row or row['version'] != ORDER_VERSION or row['closed']
                or row['booth_id'] != lease.booth_id or row['visit_id'] != lease.visit_id
                or row['generation'] != lease.generation or row['lifecycle'] != 'ACTIVE'):
            raise DraftHeld('Private draft owner has retired or changed')
        if editable and row['state'] != 'OPEN':
            raise DraftHeld('Provider-create boundary is immutable')
        if revision is not None and (type(revision) is not int or row['revision'] != revision):
            raise DraftHeld('Draft revision changed; refresh original state')
        return row

    def _event(self, draft_id, event):
        self.db.execute('INSERT INTO pp_events(draft_id,event,created_at) VALUES(?,?,?)',
                        (draft_id, event, self.now()))

    def _cart(self, draft_id, quantities):
        self.db.execute('UPDATE pp_templates SET selected=0 WHERE draft_id=?', (draft_id,))
        for template_id, copies in sorted(quantities.items()):
            self.db.execute('''INSERT INTO pp_templates
                (draft_id,template_id,lineage_id,selected,copies) VALUES(?,?,?,1,?)
                ON CONFLICT(draft_id,template_id) DO UPDATE SET selected=1,copies=excluded.copies''',
                (draft_id, template_id, uuid.uuid4().hex, copies))

    def edit(self, lease, quantities, *, revision):
        quote_post_preview(quantities)
        with self.write():
            self._owned(lease, editable=True, revision=revision)
            self._cart(lease.draft_id, quantities)
            self.db.execute('UPDATE pp_drafts SET revision=revision+1,updated_at=? WHERE draft_id=?',
                            (self.now(), lease.draft_id))
            self._event(lease.draft_id, 'CART_EDITED')
        return self.inspect(lease)

    def inspect(self, lease):
        # Consistent snapshot even when another connection attempts a cart edit.
        with self.write():
            row = dict(self._owned(lease))
            row['templates'] = [dict(r) for r in self.db.execute(
                'SELECT * FROM pp_templates WHERE draft_id=? ORDER BY template_id', (lease.draft_id,))]
            quantities = {r['template_id']: r['copies'] for r in row['templates'] if r['selected']}
            row['quantities'] = quantities
            row['amount'] = quote_post_preview(quantities).total_amount
            return row

    def lifecycle_event(self, lease, event):
        if event not in LIFECYCLE_EVENTS:
            raise ValueError('Unknown lifecycle event')
        with self.write():
            self._owned(lease)
            self._event(lease.draft_id, event)
            if event == 'INACTIVITY_WARNING':
                return  # Warning neither cancels nor abandons the visit.
            self.db.execute('''UPDATE pp_drafts SET lifecycle=?,generation=generation+1,
                updated_at=? WHERE draft_id=?''', (event, self.now(), lease.draft_id))
            # No release/FREE assertion here: exact worker fencing comes in PP-06.

