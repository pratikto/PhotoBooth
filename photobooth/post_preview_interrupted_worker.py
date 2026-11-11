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
from photobooth.post_preview_store import DraftHeld, DraftLease, ORDER_VERSION, PostPreviewStore
from photobooth.post_preview_visit_history import _regular
from photobooth.post_preview_worker_binding import verify_worker_generation_binding_from_db
from photobooth.post_preview_worker_custody import WorkerCustodyScope, restore_worker_key
from photobooth.post_preview_worker_escrow import _root, read_worker_escrow
from photobooth.post_preview_worker_fence import canonical, verify_worker_receipt_from_db, WorkerFenceKey, WorkerReceiptVerifier
from photobooth.post_preview_worker_start import read_worker_start

_HELD = 'Original interrupted worker evidence is held'


def _require(value):
    if not value: raise DraftHeld(_HELD)


def _receipt_digest(receipt):
    # Backend verification time is the sole once-updatable acknowledgement field.
    return hashlib.sha256(canonical({k:v for k,v in receipt.items()
                                    if k!='backend_verified_at'}).encode()).hexdigest()


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
                    _receipt_digest(receipt))
            finally:
                db.rollback()
    except Exception:
        raise DraftHeld(_HELD) from None


class OriginalRecoveryAuthority:
    """Private existing-receipt guardian; SAME original isolation writes ACK."""
    def __init__(self,ledger,native_owner,backend_owner,config,key,nonce,operation):
        try:
            _require(type(ledger) is PostPreviewStore and type(key) is WorkerFenceKey)
            review=read_interrupted_worker(native_owner,backend_owner,config,recovery_nonce=nonce)
            _require(review.operation_id==operation and review.scope.worker_epoch==key.key_id)
            stored=read_worker_escrow(native_owner,key.key_id)
            restored=restore_worker_key(stored.envelope,review.scope)
            import hmac
            vector={'kind':'RECOVERY_VERIFY_KEY_NO_RETIREMENT_AUTHORITY'}
            _require(hmac.compare_digest(restored.sign(vector),key.sign(vector)))
            bound=DraftLease(review.retired_lease.draft_id,review.retired_lease.booth_id,
                             review.retired_lease.visit_id,review.retired_lease.generation-1)
            with ledger.write(): verify_worker_generation_binding_from_db(ledger.db,bound,key,review.scope)
            self.ledger,self.key,self.review=ledger,key,review
            self._native,self._backend,self._config,self._nonce=native_owner,backend_owner,config,nonce
            self._witness=read_worker_start(native_owner,config,key)
            self._verifier=WorkerReceiptVerifier(ledger,key)
        except Exception:
            raise DraftHeld(_HELD) from None

    def __repr__(self):
        return '<OriginalRecoveryAuthority: private existing-receipt verification only>'

    def require(self,operation,lease):
        """Recheck before original ACK/replay; never publish a native receipt."""
        try:
            _require(operation==self.review.operation_id and type(lease) is DraftLease
                     and lease==self.review.retired_lease
                     and _root(self._native)==self._config.private_root
                     and _root(self._backend)==self._config.private_root/'backend-owner')
            from photobooth.post_preview_recovery_start import review_recovery_processes
            review_recovery_processes(self._native,self._config,current_nonce=self._nonce)
            scope=self.review.scope
            _require(original_process_exited(OriginalProcessIdentity(scope.owner_pid,scope.process_birth)))
            _require(original_process_exited(OriginalProcessIdentity(self._witness['child_pid'],self._witness['child_birth'])))
            with self.ledger.write():
                db=self.ledger.db
                stored=db.execute('SELECT * FROM pp_isolation_ops WHERE operation_id=?',(operation,)).fetchone()
                _require(stored and stored['draft_id']==lease.draft_id and stored['booth_id']==lease.booth_id
                         and stored['original_generation']==lease.generation
                         and stored['financial_class']==self.review.financial_class)
                bound=DraftLease(lease.draft_id,lease.booth_id,lease.visit_id,lease.generation-1)
                frame=verify_worker_generation_binding_from_db(db,bound,self.key,scope)
                _require(frame['worker_start_sha256']==hashlib.sha256(canonical(self._witness).encode()).hexdigest())
                receipt=self._verifier.verify(operation)
                _require(_receipt_digest(receipt)==self.review.receipt_sha256)
                if stored['state']=='ACKED':
                    from photobooth.post_preview_sandbox_handoff import require_acked_worker_receipt
                    require_acked_worker_receipt(self.ledger,stored)
                else:
                    _require(stored['state']=='PREPARED' and receipt['backend_verified_at'] is None)
                draft=db.execute('SELECT * FROM pp_drafts WHERE draft_id=?',(lease.draft_id,)).fetchone()
                _require(draft and draft['visit_id']==lease.visit_id
                         and original_financial_class(db,draft)==stored['financial_class'])
                group=db.execute('SELECT purchase_group_id FROM pp_checkout_intents WHERE draft_id=?',
                                 (lease.draft_id,)).fetchone()
                _require(group is None or not db.execute('SELECT 1 FROM pp_paid_services WHERE purchase_group_id=?',
                                                         (group[0],)).fetchone())
        except Exception:
            raise DraftHeld(_HELD) from None
