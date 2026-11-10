"""Fresh-root ciphertext seam only; no mounted recovery/OS acceptance claim."""
from contextlib import nullcontext
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photobooth.credential_vault import VaultUnavailable
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_process_identity import observe_process
from photobooth.post_preview_worker_custody import WorkerCustodyScope, restore_worker_key
from photobooth.post_preview_worker_escrow import (
    WorkerEscrowHeld, read_worker_escrow, write_new_worker_escrow)
from photobooth.post_preview_worker_fence import WorkerFenceKey


class WorkerEscrowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)/'private'
        self.lease = LaunchLease(self.root)
        self.addCleanup(self.lease.close)
        self.scope = WorkerCustodyScope(self.root, 'fixture-merchant', 'PB001', 'a'*32,
                                       os.getpid(), observe_process(os.getpid()).birth)
        self.key = WorkerFenceKey.create()
        self.path = self.root/'worker-custody'/('a'*32+'.json')
        context = (nullcontext() if os.name == 'nt' else
                   patch('photobooth.linux_credential_vault._read_key', return_value=b'k'*32))
        context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)

    def held(self, action):
        with self.assertRaises(WorkerEscrowHeld) as caught:
            action()
        self.assertEqual(str(caught.exception), 'Original pre-work escrow is held')

    def write(self):
        return write_new_worker_escrow(self.lease, self.key, self.scope)

    def test_new_root_records_only_original_ciphertext_and_exact_scope(self):
        stored = self.write()
        raw = self.path.read_bytes()
        self.assertFalse(self.key.secret.hex().encode() in raw)
        loaded = read_worker_escrow(self.lease, self.scope.worker_epoch)
        self.assertEqual(loaded.scope, self.scope)
        restored = restore_worker_key(loaded.envelope, loaded.scope)
        self.assertTrue(restored.sign({'test': 1}) == self.key.sign({'test': 1}))
        self.assertFalse(str(self.path) in repr(stored))
        self.assertEqual({p.name for p in self.root.iterdir()}, {'data', 'worker-custody'})

    def test_retry_preserves_same_original_bytes_and_timestamp(self):
        self.write()
        raw, timestamp = self.path.read_bytes(), self.path.stat().st_mtime_ns
        with patch.object(WorkerFenceKey, 'create', side_effect=AssertionError('No replacement')):
            stored = self.write()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(timestamp, self.path.stat().st_mtime_ns)
        self.assertEqual(stored.envelope.key_id, self.key.key_id)

    def test_actual_kernel_contention_and_closed_or_foreign_lease_are_held(self):
        with self.assertRaises(OSError):
            LaunchLease(self.root)
        other = LaunchLease(Path(self.temporary.name)/'another')
        try:
            self.held(lambda: write_new_worker_escrow(other, self.key, self.scope))
        finally:
            other.close()
        self.held(lambda: write_new_worker_escrow(object(), self.key, self.scope))
        self.lease.close()
        self.held(self.write)
        self.assertFalse(self.path.exists())

    def test_dead_foreign_or_declared_process_identity_cannot_write(self):
        for scope in (replace(self.scope, owner_pid=self.scope.owner_pid+1),
                      replace(self.scope, process_birth='declared-only')):
            self.held(lambda: write_new_worker_escrow(self.lease, self.key, scope))
        self.assertFalse(self.path.exists())

    def test_wrong_key_including_same_id_never_replaces_original(self):
        self.write()
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        for key in (WorkerFenceKey.create(), WorkerFenceKey(self.key.key_id, os.urandom(32))):
            self.held(lambda: write_new_worker_escrow(self.lease, key, self.scope))
        self.assertEqual(digest, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_foreign_account_epoch_or_scope_never_rewrites_original(self):
        self.write()
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        for change in ({'merchant_id': 'foreign'}, {'booth_id': 'PB002'}, {'worker_epoch': 'b'*32}):
            self.held(lambda: write_new_worker_escrow(self.lease, self.key, replace(self.scope, **change)))
        self.assertEqual(digest, hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertFalse((self.path.parent/('b'*32+'.json')).exists())

    def test_existing_customer_or_orphan_history_holds_before_ciphertext_write(self):
        for name in ('drafts.sqlite3', 'drafts.sqlite3-wal', 'raw-photo.jpg', 'unknown'):
            path = self.root/name
            path.write_bytes(b'original-fixture-preserved')
            self.held(self.write)
            self.assertTrue(path.read_bytes() == b'original-fixture-preserved')
            self.assertFalse(self.path.exists())
            path.unlink()  # This test's own public fixture only.
        (self.root/'old').mkdir()
        self.held(self.write)
        self.assertFalse(self.path.exists())

    def test_partial_or_foreign_escrow_is_preserved_without_repair(self):
        self.path.parent.mkdir()
        for raw in (b'', b'{', b'null', b'{}', b'x'*100001):
            self.path.write_bytes(raw)  # Deliberate public corrupt fixture.
            self.held(self.write)
            self.held(lambda: read_worker_escrow(self.lease, 'a'*32))
            self.assertTrue(self.path.read_bytes() == raw)

    def test_unavailable_custody_holds_before_any_file_creation(self):
        with patch('photobooth.post_preview_worker_custody.platform_protector',
                   side_effect=VaultUnavailable('PRIVATE OS DETAIL')):
            self.held(self.write)
        self.assertFalse(self.path.parent.exists())

    def test_failed_sync_keeps_original_complete_file_and_same_key_retry(self):
        with patch('photobooth.post_preview_worker_escrow.os.fsync',
                   side_effect=OSError('PRIVATE DEVICE ERROR')):
            self.held(self.write)
        self.assertTrue(self.path.exists())
        digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.write()  # Validate and sync the same original bytes, not reseal.
        self.assertEqual(digest, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_strict_metadata_read_does_not_unseal_or_claim_worker_safety(self):
        self.write()
        with patch('photobooth.post_preview_worker_escrow.restore_worker_key',
                   side_effect=AssertionError('Read is ciphertext-only')):
            self.assertEqual(read_worker_escrow(self.lease, 'a'*32).scope, self.scope)
        value = json.loads(self.path.read_bytes())
        value['scope']['worker_epoch'] = 'b'*32
        self.path.write_text(json.dumps(value))  # Deliberate public corrupt fixture.
        self.held(lambda: read_worker_escrow(self.lease, 'a'*32))
        self.held(lambda: read_worker_escrow(self.lease, '../old'))

    def test_hardlinked_escrow_is_unknown_custody_and_never_accepted(self):
        self.write()
        raw = self.path.read_bytes()
        alias = Path(self.temporary.name)/'foreign-alias.json'
        os.link(self.path, alias)
        self.held(lambda: read_worker_escrow(self.lease, 'a'*32))
        self.held(self.write)
        self.assertTrue(self.path.read_bytes() == raw and alias.read_bytes() == raw)

    def test_nonregular_escrow_holds_before_opening_or_reading_it(self):
        self.path.parent.mkdir()
        # Actual named pipe on Linux; a directory on Windows. Neither is opened.
        if os.name == 'nt':
            self.path.mkdir()
        else:
            os.mkfifo(self.path)
        with patch('photobooth.post_preview_worker_escrow.os.open',
                   side_effect=AssertionError('Do not open a special file')):
            self.held(lambda: read_worker_escrow(self.lease, 'a'*32))
            self.held(self.write)
        self.assertTrue(self.path.exists())
