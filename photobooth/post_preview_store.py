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
        if self.db.execute('SELECT version FROM pp_schema').fetchone()[0] not in (1, 2, 3, 4, 5, 6):
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
        # Additive v1 -> v2: immutable original pre-provider-create contract.
        # No legacy checkout/grant tables or existing draft fields are changed.
        with self.write():
            self.db.execute('''CREATE TABLE IF NOT EXISTS pp_checkout_intents (
                purchase_group_id TEXT PRIMARY KEY,
                draft_id TEXT NOT NULL UNIQUE REFERENCES pp_drafts(draft_id),
                revision INTEGER NOT NULL, contract_json TEXT NOT NULL,
                contract_sha256 TEXT NOT NULL, phase TEXT NOT NULL
                  CHECK(phase='CREATE_PREPARED'), prepared_at REAL NOT NULL)''')
            self.db.execute('UPDATE pp_schema SET version=2 WHERE version=1')
        missing_credential_journal = False
        with self.write():
            version = self.db.execute('SELECT version FROM pp_schema').fetchone()[0]
            if version < 3:
                self.db.execute('''CREATE TABLE IF NOT EXISTS pp_ccp_credentials (
                    purchase_group_id TEXT PRIMARY KEY REFERENCES pp_checkout_intents(purchase_group_id),
                    booth_id TEXT NOT NULL, merchant_id TEXT NOT NULL,
                    scope_json TEXT NOT NULL, verifier TEXT NOT NULL UNIQUE,
                    protector_id TEXT NOT NULL, ciphertext BLOB NOT NULL,
                    issued_at REAL NOT NULL, expires_at REAL NOT NULL,
                    policy_version TEXT NOT NULL, offered_at REAL,
                    attempts INTEGER NOT NULL DEFAULT 0, window_at REAL NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0 CHECK(revoked IN (0,1)))''')
                self.db.execute('UPDATE pp_schema SET version=3')
            elif not self.db.execute("SELECT 1 FROM sqlite_master WHERE name='pp_ccp_credentials' AND type='table'").fetchone():
                missing_credential_journal = True
        if missing_credential_journal:
            self.db.close()
            raise DraftHeld('Original credential journal is unavailable')
        missing_payment_journal = False
        with self.write():
            version = self.db.execute('SELECT version FROM pp_schema').fetchone()[0]
            if version < 4:
                self.db.execute('''CREATE TABLE IF NOT EXISTS pp_purchase_finance (
                    purchase_group_id TEXT PRIMARY KEY REFERENCES pp_checkout_intents(purchase_group_id),
                    merchant_id TEXT NOT NULL, provider_mode TEXT NOT NULL,
                    amount INTEGER NOT NULL CHECK(amount>0), entitlement_id TEXT UNIQUE,
                    paid_first_observed_at REAL,
                    legitimate_paid_attempt TEXT, cancel_requested INTEGER NOT NULL DEFAULT 0,
                    review_required INTEGER NOT NULL DEFAULT 0)''')
                self.db.execute('''CREATE TABLE IF NOT EXISTS pp_payment_attempts (
                    attempt_id TEXT PRIMARY KEY,
                    purchase_group_id TEXT NOT NULL REFERENCES pp_purchase_finance(purchase_group_id),
                    ordinal INTEGER NOT NULL CHECK(ordinal BETWEEN 1 AND 3),
                    provider_order_id TEXT NOT NULL UNIQUE, provider_ref TEXT UNIQUE,
                    create_phase TEXT NOT NULL CHECK(create_phase IN
                      ('PREPARED','SENT','UNKNOWN','VERIFIED','WITHHELD')),
                    payment_state TEXT NOT NULL DEFAULT 'UNKNOWN',
                    last_provider_state TEXT, verified_at REAL, expires_at REAL, qr_url TEXT,
                    reconcile_token TEXT, lease_until REAL NOT NULL DEFAULT 0,
                    cancel_phase TEXT NOT NULL DEFAULT 'NONE' CHECK(cancel_phase IN
                      ('NONE','PREPARED','SENT','UNKNOWN','VERIFIED')),
                    next_check_at REAL NOT NULL DEFAULT 0,
                    priority_after REAL NOT NULL DEFAULT 0,
                    UNIQUE(purchase_group_id,ordinal))''')
                self.db.execute('''CREATE TABLE IF NOT EXISTS pp_payment_audit (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_group_id TEXT NOT NULL, attempt_id TEXT,
                    outcome TEXT NOT NULL, created_at REAL NOT NULL)''')
                self.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_frozen_contract_immutable
                    BEFORE UPDATE ON pp_checkout_intents BEGIN
                    SELECT RAISE(ABORT,'Original checkout contract is immutable'); END''')
                self.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_attempt_identity_immutable
                    BEFORE UPDATE OF purchase_group_id,ordinal,provider_order_id ON pp_payment_attempts
                    BEGIN SELECT RAISE(ABORT,'Original provider attempt is immutable'); END''')
                self.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_original_entitlement_immutable
                    BEFORE UPDATE OF entitlement_id ON pp_purchase_finance
                    WHEN OLD.entitlement_id IS NOT NULL AND NEW.entitlement_id IS NOT OLD.entitlement_id
                    BEGIN SELECT RAISE(ABORT,'Original entitlement is immutable'); END''')
                self.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_finance_context_immutable
                    BEFORE UPDATE OF purchase_group_id,merchant_id,provider_mode,amount ON pp_purchase_finance
                    BEGIN SELECT RAISE(ABORT,'Original payment context is immutable'); END''')
                self.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_paid_anchor_immutable
                    BEFORE UPDATE OF paid_first_observed_at,legitimate_paid_attempt ON pp_purchase_finance
                    WHEN OLD.entitlement_id IS NOT NULL
                    BEGIN SELECT RAISE(ABORT,'Original paid anchor is immutable'); END''')
                self.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_draft_identity_immutable
                    BEFORE UPDATE OF draft_id,version,booth_id,visit_id ON pp_drafts
                    BEGIN SELECT RAISE(ABORT,'Original draft identity is immutable'); END''')
                self.db.execute('UPDATE pp_schema SET version=4')
            else:
                for name in ('pp_purchase_finance', 'pp_payment_attempts', 'pp_payment_audit'):
                    if not self.db.execute("SELECT 1 FROM sqlite_master WHERE name=? AND type='table'", (name,)).fetchone():
                        missing_payment_journal = True
                if not missing_payment_journal:
                    columns = {r['name'] for r in self.db.execute('PRAGMA table_info(pp_payment_attempts)')}
                    finance_columns = {r['name'] for r in self.db.execute('PRAGMA table_info(pp_purchase_finance)')}
                    if not {'cancel_phase', 'priority_after', 'reconcile_token'} <= columns or 'paid_first_observed_at' not in finance_columns:
                        missing_payment_journal = True
        if missing_payment_journal:
            self.db.close()
            raise DraftHeld('Original payment journal is unavailable')

        missing_inbox = False
        with self.write():
            version = self.db.execute('SELECT version FROM pp_schema').fetchone()[0]
            if version < 5:
                self.db.execute("""CREATE TABLE pp_notification_inbox (
                    event_id TEXT PRIMARY KEY,
                    purchase_group_id TEXT NOT NULL REFERENCES pp_purchase_finance(purchase_group_id),
                    attempt_id TEXT NOT NULL REFERENCES pp_payment_attempts(attempt_id),
                    booth_id TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN
                      ('NEW','PROCESSING','RETRY','APPLIED','QUARANTINED')),
                    attempts INTEGER NOT NULL DEFAULT 0, next_at REAL NOT NULL,
                    token TEXT, lease_until REAL NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL, updated_at REAL NOT NULL)""")
                self.db.execute('UPDATE pp_schema SET version=5')
            elif not self.db.execute("SELECT 1 FROM sqlite_master WHERE name='pp_notification_inbox' AND type='table'").fetchone():
                missing_inbox = True
            else:
                columns = {r['name'] for r in self.db.execute('PRAGMA table_info(pp_notification_inbox)')}
                if not {'event_id', 'purchase_group_id', 'attempt_id', 'booth_id', 'state',
                        'attempts', 'next_at', 'token', 'lease_until', 'created_at', 'updated_at'} <= columns:
                    missing_inbox = True
        if missing_inbox:
            self.db.close()
            raise DraftHeld('Original notification journal is unavailable')

        missing_paid = False
        with self.write():
            version = self.db.execute('SELECT version FROM pp_schema').fetchone()[0]
            if version < 6:
                self.db.execute('''CREATE TABLE pp_ticket_credentials (
                    purchase_group_id TEXT PRIMARY KEY REFERENCES pp_purchase_finance(purchase_group_id),
                    booth_id TEXT NOT NULL, merchant_id TEXT NOT NULL,
                    scope_json TEXT NOT NULL, verifier TEXT NOT NULL UNIQUE,
                    protector_id TEXT NOT NULL, ciphertext BLOB NOT NULL,
                    issued_at REAL NOT NULL, expires_at REAL NOT NULL,
                    policy_version TEXT NOT NULL, offered_at REAL,
                    attempts INTEGER NOT NULL DEFAULT 0, window_at REAL NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0 CHECK(revoked IN (0,1)))''')
                self.db.execute('''CREATE TABLE pp_ticket_presentations (
                    purchase_group_id TEXT PRIMARY KEY REFERENCES pp_ticket_credentials(purchase_group_id),
                    presentation_id TEXT NOT NULL UNIQUE, receipt_job_id TEXT NOT NULL UNIQUE,
                    screen_state TEXT NOT NULL DEFAULT 'NOT_OFFERED'
                      CHECK(screen_state IN ('NOT_OFFERED','VISIBLE','DISMISSED')),
                    shown_at REAL, dismissed_at REAL, render_permit_id TEXT,
                    receipt_state TEXT NOT NULL DEFAULT 'PREPARED' CHECK(receipt_state IN
                      ('PREPARED','SENDING','SUBMITTED','NOT_SENT','FAILED','UNCERTAIN')),
                    receipt_updated_at REAL)''')
                self.db.execute('''CREATE TABLE pp_paid_services (
                    purchase_group_id TEXT PRIMARY KEY REFERENCES pp_purchase_finance(purchase_group_id),
                    service_id TEXT NOT NULL UNIQUE, entitlement_id TEXT NOT NULL UNIQUE,
                    contract_sha256 TEXT NOT NULL, retention_anchor REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'OWED' CHECK(status IN ('OWED','COMPLETED','REVIEW')),
                    transaction_id TEXT UNIQUE, folder_id TEXT UNIQUE, folder_url TEXT,
                    drive_state TEXT NOT NULL DEFAULT 'NONE'
                      CHECK(drive_state IN ('NONE','PREPARED','VERIFIED','UNKNOWN','UPLOADED')),
                    worker_generation INTEGER NOT NULL DEFAULT 1)''')
                self.db.execute('''CREATE TABLE pp_paid_strip_jobs (
                    purchase_group_id TEXT NOT NULL REFERENCES pp_paid_services(purchase_group_id),
                    template_id TEXT NOT NULL, job_id TEXT NOT NULL UNIQUE,
                    copies INTEGER NOT NULL CHECK(copies BETWEEN 1 AND 9),
                    output_path TEXT NOT NULL, output_sha256 TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'PREPARED' CHECK(state IN
                      ('PREPARED','SENDING','SUBMITTED','UNCERTAIN','NOT_SENT')),
                    updated_at REAL NOT NULL,
                    PRIMARY KEY(purchase_group_id,template_id))''')
                self.db.execute('''CREATE TRIGGER pp_ticket_identity_immutable
                    BEFORE UPDATE OF purchase_group_id,booth_id,merchant_id,scope_json,verifier,
                    protector_id,ciphertext,issued_at,expires_at,policy_version ON pp_ticket_credentials
                    BEGIN SELECT RAISE(ABORT,'Original paid ticket is immutable'); END''')
                self.db.execute('''CREATE TRIGGER pp_ticket_requires_paid
                    BEFORE INSERT ON pp_ticket_credentials WHEN NOT EXISTS (
                      SELECT 1 FROM pp_purchase_finance f JOIN pp_checkout_intents i USING(purchase_group_id)
                        JOIN pp_drafts d ON d.draft_id=i.draft_id
                      WHERE f.purchase_group_id=NEW.purchase_group_id AND f.entitlement_id IS NOT NULL
                        AND f.merchant_id=NEW.merchant_id AND d.booth_id=NEW.booth_id)
                    BEGIN SELECT RAISE(ABORT,'Original paid ticket entitlement required'); END''')
                self.db.execute('''CREATE TRIGGER pp_ticket_presentation_identity_immutable
                    BEFORE UPDATE OF purchase_group_id,presentation_id,receipt_job_id ON pp_ticket_presentations
                    BEGIN SELECT RAISE(ABORT,'Original ticket presentation is immutable'); END''')
                self.db.execute('''CREATE TRIGGER pp_ticket_screen_no_replay
                    BEFORE UPDATE OF screen_state ON pp_ticket_presentations
                    WHEN (OLD.screen_state='VISIBLE' AND NEW.screen_state='NOT_OFFERED')
                      OR (OLD.screen_state='DISMISSED' AND NEW.screen_state!='DISMISSED')
                    BEGIN SELECT RAISE(ABORT,'Original ticket screen cannot replay'); END''')
                self.db.execute('''CREATE TRIGGER pp_ticket_receipt_no_replay
                    BEFORE UPDATE OF receipt_state ON pp_ticket_presentations
                    WHEN (OLD.receipt_state!='PREPARED' AND NEW.receipt_state='PREPARED')
                      OR (OLD.receipt_state IN ('SUBMITTED','UNCERTAIN','NOT_SENT','FAILED')
                          AND NEW.receipt_state!=OLD.receipt_state)
                    BEGIN SELECT RAISE(ABORT,'Original ticket receipt cannot replay'); END''')
                self.db.execute('''CREATE TRIGGER pp_paid_strip_identity_immutable
                    BEFORE UPDATE OF purchase_group_id,template_id,job_id,copies,output_path,
                    output_sha256 ON pp_paid_strip_jobs
                    BEGIN SELECT RAISE(ABORT,'Original purchased strip intent is immutable'); END''')
                self.db.execute('''CREATE TRIGGER pp_paid_strip_no_replay
                    BEFORE UPDATE OF state ON pp_paid_strip_jobs
                    WHEN (OLD.state!='PREPARED' AND NEW.state='PREPARED')
                      OR (OLD.state IN ('SUBMITTED','UNCERTAIN','NOT_SENT') AND NEW.state!=OLD.state)
                    BEGIN SELECT RAISE(ABORT,'Original purchased strip cannot replay'); END''')
                self.db.execute('''CREATE TRIGGER pp_service_paid_binding
                    BEFORE INSERT ON pp_paid_services WHEN NOT EXISTS (
                      SELECT 1 FROM pp_purchase_finance f JOIN pp_checkout_intents i
                        ON i.purchase_group_id=f.purchase_group_id
                      WHERE f.purchase_group_id=NEW.purchase_group_id
                        AND f.entitlement_id=NEW.entitlement_id
                        AND i.contract_sha256=NEW.contract_sha256
                        AND f.paid_first_observed_at=NEW.retention_anchor)
                    BEGIN SELECT RAISE(ABORT,'Original verified entitlement required'); END''')
                self.db.execute('''CREATE TRIGGER pp_paid_service_identity_immutable
                    BEFORE UPDATE OF purchase_group_id,service_id,entitlement_id,contract_sha256,
                    retention_anchor ON pp_paid_services
                    BEGIN SELECT RAISE(ABORT,'Original paid service is immutable'); END''')
                self.db.execute('''CREATE TRIGGER pp_paid_transaction_immutable
                    BEFORE UPDATE OF transaction_id ON pp_paid_services
                    WHEN OLD.transaction_id IS NOT NULL AND NEW.transaction_id IS NOT OLD.transaction_id
                    BEGIN SELECT RAISE(ABORT,'Original paid transaction is immutable'); END''')
                self.db.execute('''CREATE TRIGGER pp_paid_folder_immutable
                    BEFORE UPDATE OF folder_id,folder_url ON pp_paid_services
                    WHEN OLD.folder_id IS NOT NULL AND
                      (NEW.folder_id IS NOT OLD.folder_id OR NEW.folder_url IS NOT OLD.folder_url)
                    BEGIN SELECT RAISE(ABORT,'Original paid folder is immutable'); END''')
                self.db.execute('UPDATE pp_schema SET version=6')
            else:
                required = {
                    'pp_ticket_credentials': {'purchase_group_id','scope_json','verifier','ciphertext','offered_at','expires_at'},
                    'pp_ticket_presentations': {'purchase_group_id','presentation_id','receipt_job_id','screen_state','receipt_state','render_permit_id'},
                    'pp_paid_services': {'purchase_group_id','service_id','entitlement_id','contract_sha256','status','worker_generation'},
                    'pp_paid_strip_jobs': {'purchase_group_id','template_id','job_id','copies','output_sha256','state'},
                }
                for table, columns in required.items():
                    actual = {r['name'] for r in self.db.execute('PRAGMA table_info('+table+')')}
                    if not columns <= actual:
                        missing_paid = True
        if missing_paid:
            self.db.close()
            raise DraftHeld('Original paid delivery journal is unavailable')

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

