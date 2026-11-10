"""Unmounted NEW-root-only pre-work ciphertext storage, never boot admission.

No customer history is accepted, no key is minted and no existing bytes are
replaced. Original process/lease and original key are required for a writer's
same-process retry. Readers receive protected metadata, never an unsealed key.
Manager mounting, safe-history rotation and backend-child custody are separate.
"""
from dataclasses import dataclass, field
from contextlib import contextmanager
import hmac
import json
import os
from pathlib import Path
import stat

from photobooth.capture_journal import sync_directory
from photobooth.kiosk_v2.recovery import LaunchLease, checked_path
from photobooth.post_preview_process_identity import observe_process
from photobooth.post_preview_worker_custody import (ProtectedWorkerKey,
    WorkerCustodyScope, protect_worker_key, restore_worker_key)
from photobooth.post_preview_worker_fence import WorkerFenceKey, canonical

_HELD = 'Original pre-work escrow is held'


class WorkerEscrowHeld(RuntimeError):
    """Fixed error; preserve every original/partial artifact."""


def _require(value):
    if not value:
        raise WorkerEscrowHeld(_HELD)


@dataclass(frozen=True)
class StoredWorkerEscrow:
    scope: WorkerCustodyScope
    envelope: ProtectedWorkerKey
    path: Path = field(repr=False)


def _root(lease):
    _require(type(lease) is LaunchLease and not lease.stream.closed)
    path = checked_path(Path(lease.stream.name))
    _require(path.name == 'kiosk-v2-launch.lock' and path.parent.name == 'data')
    return checked_path(path.parent.parent)


def _path(root, epoch):
    import re
    _require(type(epoch) is str and re.fullmatch(r'[a-f0-9]{32}', epoch) is not None)
    return checked_path(root/'worker-custody'/(epoch+'.json'))


def _record(scope, envelope):
    return dict(version=1, kind='ORIGINAL_WORKER_ESCROW',
                scope=scope.to_record(), envelope=envelope.to_record())


def _unique(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


@contextmanager
def _regular_file(path, mode):
    path = checked_path(path)
    before = path.lstat()
    _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
             and 1 <= before.st_size <= 100000)
    flags = os.O_RDWR if mode == 'r+b' else os.O_RDONLY
    descriptor = os.open(path, flags | getattr(os, 'O_NOFOLLOW', 0)
                         | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0))
    try:
        actual = os.fstat(descriptor)
        _require(stat.S_ISREG(actual.st_mode) and actual.st_nlink == 1
                 and 1 <= actual.st_size <= 100000
                 and (actual.st_dev, actual.st_ino) == (before.st_dev, before.st_ino))
        stream = os.fdopen(descriptor, mode)
        descriptor = None
        with stream:
            yield stream
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _read(path, root, epoch):
    with _regular_file(path, 'rb') as stream:
        raw = stream.read(100001)
    _require(1 <= len(raw) <= 100000)
    value = json.loads(raw, object_pairs_hook=_unique)
    _require(type(value) is dict and set(value) == {'version', 'kind', 'scope', 'envelope'})
    _require(type(value['version']) is int and value['version'] == 1
             and value['kind'] == 'ORIGINAL_WORKER_ESCROW')
    scope = WorkerCustodyScope.from_record(value['scope'])
    envelope = ProtectedWorkerKey.from_record(value['envelope'])
    _require(scope.private_root == root and scope.worker_epoch == epoch)
    import hashlib
    _require(hashlib.sha256(scope.entropy()).hexdigest() == envelope.scope_sha256)
    _require(canonical(value).encode('utf-8') == raw)
    return StoredWorkerEscrow(scope, envelope, path)


def read_worker_escrow(lease, epoch):
    """Read ciphertext only under original root lease; NO unseal/admission."""
    try:
        root = _root(lease)
        return _read(_path(root, epoch), root, epoch)
    except Exception:
        raise WorkerEscrowHeld(_HELD) from None


def _new_root_only(root, path):
    # Inspect immediate known names only, never descend into old/customer data.
    _require({p.name for p in root.iterdir()} <= {'data', 'worker-custody'})
    data = checked_path(root/'data')
    _require({p.name for p in data.iterdir()} == {'kiosk-v2-launch.lock'})
    folder = checked_path(path.parent)
    if folder.exists():
        _require({p.name for p in folder.iterdir()} <= {path.name})


def write_new_worker_escrow(lease, key, scope):
    """Fresh-root writer only; does not authorize starting any worker.

    Same original live writer/key can validate and re-sync a complete prior
    file. Partial/foreign history is never rewritten or removed. A restart
    cannot write under a dead owner's identity. No safe-history rotation yet.
    """
    try:
        root = _root(lease)
        _require(type(key) is WorkerFenceKey and type(scope) is WorkerCustodyScope
                 and scope.private_root == root and scope.owner_pid == os.getpid())
        _require(observe_process(os.getpid()).birth == scope.process_birth)
        path = _path(root, scope.worker_epoch)
        _new_root_only(root, path)
        if path.exists():
            stored = _read(path, root, scope.worker_epoch)
            _require(stored.scope == scope and stored.envelope.key_id == key.key_id)
        else:
            envelope = protect_worker_key(key, scope)
            # OS custody must actually restore this original key before a file
            # can be created. The MAC is a local test vector, never a receipt.
            restored = restore_worker_key(envelope, scope)
            _require(hmac.compare_digest(restored.sign({'kind': 'ESCROW_TEST_NO_AUTHORITY'}),
                                         key.sign({'kind': 'ESCROW_TEST_NO_AUTHORITY'})))
            path.parent.mkdir(exist_ok=True, mode=0o700)
            _new_root_only(root, path)
            descriptor = os.open(checked_path(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL
                                 | getattr(os, 'O_NOFOLLOW', 0), 0o600)
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(canonical(_record(scope, envelope)).encode('utf-8'))
                stream.flush()
                os.fsync(stream.fileno())
            stored = _read(path, root, scope.worker_epoch)
        restored = restore_worker_key(stored.envelope, scope)
        _require(hmac.compare_digest(restored.sign({'kind': 'ESCROW_TEST_NO_AUTHORITY'}),
                                     key.sign({'kind': 'ESCROW_TEST_NO_AUTHORITY'})))
        # Retrying a complete but previously unsynced write retains every byte.
        with _regular_file(path, 'r+b') as stream:
            os.fsync(stream.fileno())
        sync_directory(path.parent)
        sync_directory(root)
        return stored
    except Exception:
        raise WorkerEscrowHeld(_HELD) from None
