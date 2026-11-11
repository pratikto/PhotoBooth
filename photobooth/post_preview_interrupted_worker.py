"""Read ONLY original interrupted worker evidence; no boot/ACK authority.

No new key, binding, receipt or DB is created. Paid delivery/Drive histories are
initially held pending independent upload/manifest reconciliation. Old customer
access still requires original proof and fresh legitimate payment verification.
"""
from contextlib import closing
from dataclasses import dataclass, field
import hashlib
import sqlite3
import time

from photobooth.post_preview_financial_history import original_financial_class
from photobooth.post_preview_host import SandboxHostConfig, require_original_host_context
from photobooth.post_preview_process_identity import OriginalProcessIdentity, original_process_exited
from photobooth.post_preview_store import DraftHeld, DraftLease, ORDER_VERSION
from photobooth.post_preview_visit_history import _regular
from photobooth.post_preview_worker_binding import verify_worker_generation_binding_from_db
from photobooth.post_preview_worker_custody import WorkerCustodyScope, restore_worker_key
from photobooth.post_preview_worker_escrow import _root, read_worker_escrow
from photobooth.post_preview_worker_fence import canonical, verify_worker_receipt_from_db
from photobooth.post_preview_worker_start import read_worker_start

_HELD = 'Original interrupted worker evidence is held'


def _require(value):
    if not value: raise DraftHeld(_HELD)


@dataclass(frozen=True, repr=False)
class InterruptedWorkerReview:
    scope: WorkerCustodyScope = field(repr=False)
    retired_lease: DraftLease = field(repr=False)
    operation_id: str
    financial_class: str
    receipt_sha256: str

    def __repr__(self):
        return '<InterruptedWorkerReview: original metadata, not admission or ACK>'


def read_interrupted_worker(native_owner, backend_owner, config, *, recovery_nonce=None):
    """Caller retains actual ORIGINAL global owner separately; HOLD-only read."""
    try:
        _require(type(config) is SandboxHostConfig and _root(native_owner) == config.private_root
                 and _root(backend_owner) == config.private_root/'backend-owner')
        from photobooth.post_preview_recovery_start import review_recovery_processes
        review_recovery_processes(native_owner,config,current_nonce=recovery_nonce)
        root = config.private_root
        path = _regular(root/'drafts.sqlite3')
        _regular(root/'host-context.json'); require_original_host_context(root,config)
        for suffix in ('-wal','-shm'):
            side = root/(path.name+suffix)
            if side.exists(): _regular(side)
        with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=.2)) as db:
            db.row_factory=sqlite3.Row
            db.execute('PRAGMA query_only=ON'); db.execute('BEGIN')
            try:
                _require([tuple(row) for row in db.execute('SELECT singleton,version FROM pp_schema')] == [(1,8)])
                _require(not db.execute('SELECT 1 FROM pp_drafts WHERE booth_id!=? OR version!=? LIMIT 1',
                                        (config.booth_id,ORDER_VERSION)).fetchone())
                drafts=db.execute('SELECT * FROM pp_drafts WHERE closed=0').fetchall()
                _require(len(drafts)==1)
                draft=drafts[0]
                _require(draft['lifecycle'] not in {'ACTIVE','ISOLATED'} and draft['generation']>1)
                operation=db.execute('SELECT * FROM pp_isolation_ops WHERE draft_id=? AND booth_id=? '
                    'AND original_generation=? AND state=\'PREPARED\'',
                    (draft['draft_id'],config.booth_id,draft['generation'])).fetchone()
                _require(operation is not None)
                bound=DraftLease(draft['draft_id'],config.booth_id,draft['visit_id'],draft['generation']-1)
                row=db.execute('SELECT key_id FROM pp_worker_generations WHERE draft_id=? AND generation=?',
                               (bound.draft_id,bound.generation)).fetchone()
                _require(row is not None)
                stored=read_worker_escrow(native_owner,row['key_id']); scope=stored.scope
                _require(scope.private_root==root and scope.merchant_id==config.merchant_id
                         and scope.booth_id==config.booth_id and stored.envelope.key_id==scope.worker_epoch==row['key_id'])
                key=restore_worker_key(stored.envelope,scope)
                witness=read_worker_start(native_owner,config,key)
                _require(witness['parent_pid']==scope.owner_pid and witness['parent_birth']==scope.process_birth)
                _require(original_process_exited(OriginalProcessIdentity(scope.owner_pid,scope.process_birth)))
                _require(original_process_exited(OriginalProcessIdentity(witness['child_pid'],witness['child_birth'])))
                frame=verify_worker_generation_binding_from_db(db,bound,key,scope)
                _require(frame['worker_start_sha256']==hashlib.sha256(canonical(witness).encode()).hexdigest())
                receipt=verify_worker_receipt_from_db(db,key,operation['operation_id'],now=time.time())
                _require(receipt['backend_verified_at'] is None)
                financial=original_financial_class(db,draft)
                _require(financial==operation['financial_class'])
                group=db.execute('SELECT purchase_group_id FROM pp_checkout_intents WHERE draft_id=?',
                                 (bound.draft_id,)).fetchone()
                if group is not None:
                    _require(not db.execute('SELECT 1 FROM pp_paid_services WHERE purchase_group_id=?',
                                            (group[0],)).fetchone())
                return InterruptedWorkerReview(scope,DraftLease(bound.draft_id,bound.booth_id,
                    bound.visit_id,bound.generation+1),operation['operation_id'],financial,
                    hashlib.sha256(canonical(receipt).encode()).hexdigest())
            finally:
                db.rollback()
    except Exception:
        raise DraftHeld(_HELD) from None
