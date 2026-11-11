"""Explicit original draft/epoch journal core; initially UNMOUNTED.

A binding is historical metadata, never retirement, ACK, finance or admission.
Only the actual live original worker may record it; recovery may only verify an
already recorded binding. No capability is minted or persisted in plaintext.
"""
import hashlib
import hmac
import json
import os
from pathlib import Path

from photobooth.kiosk_v2.recovery import checked_path
from photobooth.post_preview_process_identity import observe_process
from photobooth.post_preview_store import DraftHeld, DraftLease, ORDER_VERSION, PostPreviewStore
from photobooth.post_preview_worker_custody import WorkerCustodyScope, restore_worker_key
from photobooth.post_preview_worker_escrow import read_worker_escrow
from photobooth.post_preview_worker_fence import WorkerFenceKey, canonical
from photobooth.post_preview_worker_start import read_worker_start

_HELD = 'Original worker generation binding is held'
_TABLE = '''CREATE TABLE pp_worker_generations (
    draft_id TEXT NOT NULL REFERENCES pp_drafts(draft_id),
    generation INTEGER NOT NULL CHECK(generation>=1),
    key_id TEXT NOT NULL UNIQUE CHECK(length(key_id)=32),
    frame_json TEXT NOT NULL CHECK(length(frame_json) BETWEEN 1 AND 4096),
    mac TEXT NOT NULL CHECK(length(mac)=64),
    PRIMARY KEY(draft_id,generation))'''


def _require(value):
    if not value: raise DraftHeld(_HELD)


def _sql(value):
    return ' '.join(value.split()).casefold().rstrip(';')


def install_worker_generation_bindings(ledger):
    """Trusted additive setup only; refuse foreign schemas/triggers unchanged."""
    try:
        _require(type(ledger) is PostPreviewStore)
        definitions = [('pp_worker_generations', _TABLE)]
        for action in ('UPDATE', 'DELETE'):
            name = 'pp_worker_generation_no_'+action.lower()
            definitions.append((name, f'''CREATE TRIGGER {name}
                BEFORE {action} ON pp_worker_generations
                BEGIN SELECT RAISE(ABORT,'Original worker binding is immutable'); END'''))
        definitions.append(('pp_worker_generation_no_replace', '''CREATE TRIGGER pp_worker_generation_no_replace
            BEFORE INSERT ON pp_worker_generations
            WHEN EXISTS(SELECT 1 FROM pp_worker_generations
                WHERE key_id=NEW.key_id OR (draft_id=NEW.draft_id AND generation=NEW.generation))
            BEGIN SELECT RAISE(ABORT,'Original worker binding is immutable'); END'''))
        with ledger.write():
            # Validate every existing definition before creating anything.
            for name, definition in definitions:
                saved = ledger.db.execute('SELECT sql FROM sqlite_master WHERE name=?', (name,)).fetchone()
                _require(saved is None or type(saved['sql']) is str and _sql(saved['sql']) == _sql(definition))
            for name, definition in definitions:
                if not ledger.db.execute('SELECT 1 FROM sqlite_master WHERE name=?', (name,)).fetchone():
                    ledger.db.execute(definition)
    except Exception:
        raise DraftHeld(_HELD) from None


def _context(ledger, lease, key, scope):
    _require(type(ledger) is PostPreviewStore)
    _context_db(ledger.db, lease, key, scope)


def _context_db(db, lease, key, scope):
    _require(type(lease) is DraftLease
             and type(key) is WorkerFenceKey and type(scope) is WorkerCustodyScope)
    _require(type(lease.generation) is int and 1 <= lease.generation <= 2147483647
             and key.key_id == scope.worker_epoch and lease.booth_id == scope.booth_id)
    files = list(db.execute('PRAGMA database_list'))
    _require(len(files) >= 1 and files[0]['name'] == 'main' and files[0]['file']
             and checked_path(Path(files[0]['file'])) == scope.private_root/'drafts.sqlite3')
    row = db.execute('SELECT * FROM pp_drafts WHERE draft_id=?', (lease.draft_id,)).fetchone()
    _require(row and row['version'] == ORDER_VERSION and row['booth_id'] == lease.booth_id
             and row['visit_id'] == lease.visit_id and row['generation'] >= lease.generation)


def _frame(lease, key, scope, witness):
    return dict(version=1, kind='ORIGINAL_WORKER_GENERATION', mode='sandbox',
                order_version=ORDER_VERSION, draft_id=lease.draft_id,
                booth_id=lease.booth_id, visit_id=lease.visit_id, generation=lease.generation,
                worker_epoch=scope.worker_epoch, key_id=key.key_id,
                scope_sha256=hashlib.sha256(scope.entropy()).hexdigest(),
                worker_start_sha256=hashlib.sha256(canonical(witness).encode()).hexdigest())


def verify_worker_generation_binding(ledger, lease, key, scope):
    """Caller owns original DB transaction; read ONLY an existing binding.

    Old generations can be inspected after retirement. This never proves that
    any worker stopped, that a receipt exists or that customer access is valid.
    """
    try:
        _context(ledger, lease, key, scope)
        return verify_worker_generation_binding_from_db(ledger.db, lease, key, scope)
    except Exception:
        raise DraftHeld(_HELD) from None


def verify_worker_generation_binding_from_db(db, lease, key, scope):
    """SAME read algorithm in original read-only snapshot; never opens/migrates."""
    try:
        _context_db(db, lease, key, scope)
        row = db.execute('SELECT * FROM pp_worker_generations WHERE draft_id=? AND generation=?',
                                (lease.draft_id, lease.generation)).fetchone()
        _require(row and row['key_id'] == key.key_id)
        # Duplicate keys and noncanonical or extra JSON are rejected by exact
        # canonical equality below, even if someone also supplies a valid MAC.
        frame = json.loads(row['frame_json'])
        expected = _frame(lease, key, scope, {})
        _require(type(frame) is dict and set(frame) == set(expected)
                 and type(frame['version']) is int and type(frame['generation']) is int
                 and all(frame[k] == v for k, v in expected.items() if k != 'worker_start_sha256'))
        digest = frame['worker_start_sha256']
        _require(type(digest) is str and len(digest) == 64
                 and all(c in '0123456789abcdef' for c in digest)
                 and canonical(frame) == row['frame_json']
                 and hmac.compare_digest(row['mac'], key.sign(frame)))
        return frame
    except Exception:
        raise DraftHeld(_HELD) from None


def bind_original_worker_generation(ledger, lease, launcher, config, key):
    """Record SAME live original capability before work; no recovery writer."""
    try:
        _require(type(key) is WorkerFenceKey)
        stored = read_worker_escrow(launcher, key.key_id)
        scope = stored.scope
        _require(scope.private_root == config.private_root and scope.merchant_id == config.merchant_id
                 and scope.booth_id == config.booth_id and scope.owner_pid == os.getpid()
                 and observe_process(os.getpid()).birth == scope.process_birth)
        restored = restore_worker_key(stored.envelope, scope)
        vector = {'kind': 'BINDING_KEY_TEST_NO_AUTHORITY'}
        _require(restored.key_id == key.key_id
                 and hmac.compare_digest(restored.sign(vector), key.sign(vector)))
        witness = read_worker_start(launcher, config, key)
        _require(witness['parent_pid'] == scope.owner_pid and witness['parent_birth'] == scope.process_birth
                 and observe_process(witness['child_pid']).birth == witness['child_birth'])
        frame = _frame(lease, key, scope, witness)
        with ledger.write():
            _context(ledger, lease, key, scope)
            ledger._owned(lease)  # Historical rows cannot be bound retroactively.
            existing = ledger.db.execute('SELECT 1 FROM pp_worker_generations WHERE draft_id=? AND generation=?',
                                         (lease.draft_id, lease.generation)).fetchone()
            if not existing:
                ledger.db.execute('INSERT INTO pp_worker_generations VALUES(?,?,?,?,?)',
                    (lease.draft_id, lease.generation, key.key_id, canonical(frame), key.sign(frame)))
            _require(verify_worker_generation_binding(ledger, lease, key, scope) == frame)
        return frame
    except Exception:
        raise DraftHeld(_HELD) from None
