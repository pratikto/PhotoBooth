"""Original pre-START process witness, NOT retirement/boot/media authority.

The same existing worker key authenticates only observed parent/child metadata.
No plaintext key/config/token is persisted. A new key/witness cannot stand in
for old work; OS escrow and draft/generation epoch binding remain separate.
"""
import hmac
import json
import os
import subprocess

from photobooth.capture_journal import sync_directory
from photobooth.kiosk_v2.recovery import checked_path
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_process_identity import OriginalProcessIdentity, observe_process
from photobooth.post_preview_store import ORDER_VERSION
from photobooth.post_preview_worker_escrow import _root, _regular_file, _unique
from photobooth.post_preview_worker_fence import WorkerFenceKey, canonical

_HELD = 'Original worker start witness is held'
_KIND = 'ORIGINAL_WORKER_START'


class WorkerStartHeld(RuntimeError):
    """Fixed failure, never expose original private bootstrap contents."""


def _require(value):
    if not value:
        raise WorkerStartHeld(_HELD)


def require_worker_start_owner(launcher, config, key):
    """Original native root ownership only; no global/backend/finance grant."""
    try:
        _require(type(config) is SandboxHostConfig and type(key) is WorkerFenceKey)
        _require(_root(launcher) == config.private_root)
    except Exception:
        raise WorkerStartHeld(_HELD) from None


def _binding(config, key):
    return dict(version=1, kind=_KIND, mode='sandbox', order_version=ORDER_VERSION,
                private_root=str(config.private_root), merchant_id=config.merchant_id,
                booth_id=config.booth_id, worker_epoch=key.key_id, key_id=key.key_id)


def _path(config, key):
    return checked_path(config.private_root/'worker-starts'/(key.key_id+'.json'))


def _read(path, config, key):
    with _regular_file(path, 'rb') as stream:
        raw = stream.read(4097)
    _require(1 <= len(raw) <= 4096)
    value = json.loads(raw, object_pairs_hook=_unique)
    _require(type(value) is dict and set(value) == {'version', 'kind', 'frame', 'mac'})
    _require(type(value['version']) is int and value['version'] == 1
             and value['kind'] == 'ORIGINAL_WORKER_START_ENVELOPE')
    frame = value['frame']
    binding = _binding(config, key)
    _require(type(frame) is dict and set(frame) == set(binding) | {
        'parent_pid', 'parent_birth', 'child_pid', 'child_birth'})
    _require(type(frame['version']) is int
             and all(frame[name] == expected for name, expected in binding.items()))
    OriginalProcessIdentity(frame['parent_pid'], frame['parent_birth'])
    OriginalProcessIdentity(frame['child_pid'], frame['child_birth'])
    _require(frame['child_pid'] != frame['parent_pid'])
    _require(type(value['mac']) is str and len(value['mac']) == 64
             and hmac.compare_digest(value['mac'], key.sign(frame)))
    _require(canonical(value).encode('utf-8') == raw)
    return frame


def read_worker_start(launcher, config, key):
    """Same-key authenticated METADATA only; not live/dead/ACK evidence."""
    try:
        require_worker_start_owner(launcher, config, key)
        return _read(_path(config, key), config, key)
    except Exception:
        raise WorkerStartHeld(_HELD) from None


def record_worker_start(launcher, config, key, child):
    """Observe actual Popen child and persist before original config START.

    The caller must withhold START until this returns. Failure retains partial
    bytes and original handles. Never kill/recreate or retroactively sign for
    a dead old worker. No OS key is created, provisioned, stored or restored.
    """
    try:
        require_worker_start_owner(launcher, config, key)
        _require(type(child) is subprocess.Popen and child.poll() is None)
        parent_identity = observe_process(os.getpid())
        child_identity = observe_process(child.pid)
        _require(child_identity.pid != parent_identity.pid)
        frame = dict(_binding(config, key), parent_pid=parent_identity.pid,
                     parent_birth=parent_identity.birth, child_pid=child_identity.pid,
                     child_birth=child_identity.birth)
        value = dict(version=1, kind='ORIGINAL_WORKER_START_ENVELOPE',
                     frame=frame, mac=key.sign(frame))
        raw = canonical(value).encode('utf-8')
        _require(len(raw) <= 4096)
        path = _path(config, key)
        if not path.exists():
            checked_path(path.parent).mkdir(mode=0o700, exist_ok=True)
            descriptor = os.open(checked_path(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL
                                 | getattr(os, 'O_NOFOLLOW', 0), 0o600)
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        # Original same-process/live-child retry can re-sync exact bytes only.
        _require(_read(path, config, key) == frame)
        with _regular_file(path, 'r+b') as stream:
            os.fsync(stream.fileno())
        sync_directory(path.parent)
        sync_directory(config.private_root)
        require_worker_start_owner(launcher, config, key)
        _require(child.poll() is None and observe_process(child.pid) == child_identity)
        return frame
    except Exception:
        raise WorkerStartHeld(_HELD) from None
