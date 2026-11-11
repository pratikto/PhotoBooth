"""Trusted eligible-history ciphertext writer, initially UNMOUNTED.

Retains original native/backend kernel ownership and read-only history snapshot.
No new key, old retirement, ACK, financial remedy or customer access is created.
Unknown legacy start records without original escrow remain held, never adopted.
"""
import os
import re

from photobooth.kiosk_v2.recovery import checked_path
from photobooth.post_preview_process_identity import (
    OriginalProcessIdentity, observe_process, original_process_exited)
from photobooth.post_preview_store import DraftLease
from photobooth.post_preview_visit_history import original_prework_history
from photobooth.post_preview_worker_binding import verify_worker_generation_binding_from_db
from photobooth.post_preview_worker_custody import WorkerCustodyScope, restore_worker_key
from photobooth.post_preview_worker_escrow import (
    WorkerEscrowHeld, _write_worker_escrow, read_worker_escrow)
from photobooth.post_preview_worker_fence import WorkerFenceKey
from photobooth.post_preview_worker_start import read_worker_start

_HELD = 'Original pre-work escrow is held'
MAX_EPOCHS = 10000  # Fail closed, never prune or silently omit older metadata.


def _require(value):
    if not value: raise WorkerEscrowHeld(_HELD)


def _epochs(folder):
    folder = checked_path(folder)
    if not folder.exists(): return set()
    result = set()
    # Immediate metadata names only. Never resolve/open unknown or old entries.
    for entry in folder.iterdir():
        _require(re.fullmatch(r'[a-f0-9]{32}\.json', entry.name) is not None)
        _require(len(result) < MAX_EPOCHS)
        result.add(entry.name[:-5])
    return result


def _policy(launcher, config, current, db):
    root = config.private_root
    from photobooth.post_preview_recovery_start import review_recovery_processes
    review_recovery_processes(launcher,config)
    custody = _epochs(root/'worker-custody')
    starts = _epochs(root/'worker-starts')
    _require(starts <= custody)  # Missing original capability is not legacy adoption.
    if db is None:
        _require(custody <= ({current.worker_epoch} if current is not None else set()) and not starts)
    keys = {}
    for epoch in custody:
        stored = read_worker_escrow(launcher, epoch)
        scope = stored.scope
        _require(scope.merchant_id == config.merchant_id and scope.booth_id == config.booth_id
                 and scope.private_root == root and stored.envelope.key_id == epoch)
        original = restore_worker_key(stored.envelope, scope)
        keys[epoch] = (original, scope)
        if current is not None and epoch == current.worker_epoch:
            _require(scope == current)
            continue  # SAME original writer's complete pre-START sync retry.
        _require(epoch in starts)
        witness = read_worker_start(launcher, config, original)
        _require(witness['parent_pid'] == scope.owner_pid
                 and witness['parent_birth'] == scope.process_birth)
        child = OriginalProcessIdentity(witness['child_pid'], witness['child_birth'])
        _require(original_process_exited(child))
        parent = OriginalProcessIdentity(scope.owner_pid, scope.process_birth)
        if parent.pid == os.getpid():
            _require(observe_process(os.getpid()) == parent)
        else:
            _require(original_process_exited(parent))
    if db is not None and db.execute(
            "SELECT 1 FROM sqlite_master WHERE name='pp_worker_generations'").fetchone():
        for row in db.execute('SELECT draft_id,generation,key_id FROM pp_worker_generations'):
            _require(row['key_id'] in keys)
            key, scope = keys[row['key_id']]
            draft = db.execute('SELECT * FROM pp_drafts WHERE draft_id=?', (row['draft_id'],)).fetchone()
            _require(draft is not None)
            lease = DraftLease(row['draft_id'], draft['booth_id'], draft['visit_id'], row['generation'])
            frame = verify_worker_generation_binding_from_db(db, lease, key, scope)
            # Bindings authenticate the SAME retained original start witness.
            import hashlib
            from photobooth.post_preview_worker_fence import canonical
            witness = read_worker_start(launcher, config, key)
            _require(frame['worker_start_sha256'] == hashlib.sha256(canonical(witness).encode()).hexdigest())


def review_eligible_worker_history(launcher,config):
    """Same original history/provenance policy BEFORE minting a fresh epoch."""
    try:
        with original_prework_history(launcher,config,allow_custody=True) as db:
            _policy(launcher,config,None,db)
    except Exception:
        raise WorkerEscrowHeld(_HELD) from None


def write_eligible_worker_escrow(launcher, config, key):
    """Persist supplied ORIGINAL key before work under actual original locks.

    Shared original history policy denies unresolved/uncertain visitors. Older
    start/escrow pairs must authenticate and show actual process exit. This is
    not a boot-recovery writer: it never fills missing bindings or old receipts.
    """
    try:
        _require(type(key) is WorkerFenceKey)
        with original_prework_history(launcher, config, allow_custody=True) as db:
            identity = observe_process(os.getpid())
            scope = WorkerCustodyScope(config.private_root, config.merchant_id, config.booth_id,
                                       key.key_id, identity.pid, identity.birth)
            def policy(root, path):
                _require(root == scope.private_root)
                _policy(launcher, config, scope, db)
            return _write_worker_escrow(launcher, key, scope, policy)
    except Exception:
        raise WorkerEscrowHeld(_HELD) from None
