"""Actual original lease/history/OS-envelope rotation seam; no device effects."""
from contextlib import nullcontext
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_bootstrap import backend_environment
from photobooth.post_preview_host import SandboxHostConfig, _original_context
from photobooth.post_preview_store import PostPreviewStore
from photobooth.post_preview_worker_epochs import write_eligible_worker_escrow
from photobooth.post_preview_worker_escrow import WorkerEscrowHeld
from photobooth.post_preview_worker_fence import WorkerFenceKey, install_worker_receipts
from photobooth.post_preview_worker_start import record_worker_start


class OriginalWorkerEpochTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.config = SandboxHostConfig(Path(temporary.name), 'MTEST', 'PB001',
            'Mid-server-EPOCH-FIXTURE', 'b'*48,
            'https://script.google.com/macros/s/EPOCH_FIXTURE/exec', 'fixture-drive')
        self.root = self.config.private_root
        self.launcher = LaunchLease(self.root); self.addCleanup(self.launcher.close)
        context = nullcontext() if os.name == 'nt' else patch(
            'photobooth.linux_credential_vault._read_key', return_value=b'k'*32)
        context.__enter__(); self.addCleanup(context.__exit__, None, None, None)
        self.key = WorkerFenceKey.create()
        self.children = []; self.addCleanup(self.close_children)

    def close_children(self):
        for child in self.children:
            if child.poll() is None: child.communicate('', timeout=10)
            else:
                child.stdin.close(); child.stdout.close()

    def child(self, key):
        child = subprocess.Popen([sys.executable, '-c',
            'import sys; print("READY",flush=True); sys.stdin.read()'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, env=backend_environment(os.environ))
        self.children.append(child); self.assertEqual('READY', child.stdout.readline().strip())
        record_worker_start(self.launcher, self.config, key, child)
        return child

    def history(self):
        _original_context(self.root, self.config)
        store = PostPreviewStore(self.root/'drafts.sqlite3')
        install_worker_receipts(store); self.addCleanup(store.close)
        return store

    def write(self, key=None):
        return write_eligible_worker_escrow(self.launcher, self.config, key or self.key)

    def held(self, action):
        with self.assertRaises(WorkerEscrowHeld) as caught: action()
        self.assertEqual('Original pre-work escrow is held', str(caught.exception))

    def files(self):
        return {folder+'/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for folder in ('worker-custody', 'worker-starts') if (self.root/folder).exists()
                for p in (self.root/folder).iterdir()}

    def test_actual_backend_kernel_lease_is_held_through_seal_write_and_sync(self):
        import photobooth.post_preview_worker_epochs as epochs
        original = epochs._write_worker_escrow; observed = []
        def while_owned(*args):
            with self.assertRaises(OSError): LaunchLease(self.root/'backend-owner')
            observed.append(True)
            return original(*args)
        with patch.object(epochs, '_write_worker_escrow', side_effect=while_owned): stored = self.write()
        self.assertEqual([True], observed); self.assertEqual(self.key.key_id, stored.scope.worker_epoch)
        with LaunchLease(self.root/'backend-owner'): pass

    def test_same_original_prestart_retry_keeps_ciphertext_bytes_and_timestamp(self):
        stored = self.write(); before = self.files(); stamp = stored.path.stat().st_mtime_ns
        self.write()
        self.assertEqual(before, self.files()); self.assertEqual(stamp, stored.path.stat().st_mtime_ns)
        self.assertFalse((self.root/'drafts.sqlite3').exists())

    def test_live_backend_owner_holds_before_os_protection_or_ciphertext(self):
        with LaunchLease(self.root/'backend-owner'), patch(
                'photobooth.post_preview_worker_escrow.protect_worker_key',
                side_effect=AssertionError('No protection before ownership')):
            self.held(self.write)
        self.assertFalse((self.root/'worker-custody').exists())

    def test_unresolved_original_history_holds_before_new_ciphertext(self):
        self.write(); store = self.history()
        lease = store.create('PB001', 'unresolved-original', {'template_a': 1})
        before = self.files(); draft = dict(store.db.execute('SELECT * FROM pp_drafts').fetchone())
        with patch('photobooth.post_preview_worker_escrow.protect_worker_key',
                   side_effect=AssertionError('No new ciphertext for unresolved history')):
            self.held(lambda: self.write(WorkerFenceKey.create()))
        self.assertEqual(before, self.files()); self.assertEqual(lease.draft_id, draft['draft_id'])
        self.assertEqual(draft, dict(store.db.execute('SELECT * FROM pp_drafts').fetchone()))

    def test_actual_live_old_child_holds_even_when_backend_kernel_lease_is_free(self):
        self.write(); self.history(); child = self.child(self.key); new = WorkerFenceKey.create()
        before = self.files()
        with LaunchLease(self.root/'backend-owner'): pass  # Child is not this kernel lock.
        self.held(lambda: self.write(new)); self.assertEqual(before, self.files())
        child.communicate('', timeout=10)
        self.write(new)
        self.assertTrue((self.root/'worker-custody'/(new.key_id+'.json')).is_file())

    def test_two_eligible_same_process_rotations_preserve_all_original_epochs(self):
        self.write(); self.history(); self.child(self.key).communicate('', timeout=10)
        before = self.files(); second = WorkerFenceKey.create(); self.write(second)
        for name, digest in before.items(): self.assertEqual(digest, self.files()[name])
        self.child(second).communicate('', timeout=10)
        before = self.files(); self.write(WorkerFenceKey.create())
        for name, digest in before.items(): self.assertEqual(digest, self.files()[name])

    def test_missing_db_after_original_start_never_creates_replacement_history(self):
        self.write(); self.child(self.key).communicate('', timeout=10)
        before = self.files(); self.held(lambda: self.write(WorkerFenceKey.create()))
        self.assertEqual(before, self.files()); self.assertFalse((self.root/'drafts.sqlite3').exists())

    def test_missing_original_escrow_or_partial_witness_is_preserved_and_held(self):
        stored = self.write(); self.history(); self.child(self.key).communicate('', timeout=10)
        witness = self.root/'worker-starts'/(self.key.key_id+'.json')
        witness.write_bytes(b'{')  # Deliberate public fault fixture only.
        self.held(lambda: self.write(WorkerFenceKey.create())); self.assertEqual(b'{', witness.read_bytes())
        stored.path.unlink()  # This isolated fixture models lost original custody.
        self.held(lambda: self.write(WorkerFenceKey.create()))
        self.assertFalse(stored.path.exists()); self.assertEqual(b'{', witness.read_bytes())

    def test_fresh_root_cannot_replace_prior_epoch_without_original_start(self):
        self.write(); before = self.files()
        self.held(lambda: self.write(WorkerFenceKey.create()))
        self.assertEqual(before, self.files())

    def test_foreign_unknown_or_oversized_metadata_scan_holds_without_pruning(self):
        self.write(); before = self.files()
        with patch('photobooth.post_preview_worker_epochs.MAX_EPOCHS', 0): self.held(self.write)
        self.assertEqual(before, self.files())
        (self.root/'worker-custody'/'unknown').mkdir()
        self.held(self.write)
        self.assertTrue((self.root/'worker-custody'/'unknown').is_dir())

    def test_sync_failure_keeps_original_bytes_and_same_key_can_resync(self):
        with patch('photobooth.post_preview_worker_escrow.os.fsync',
                   side_effect=OSError('PRIVATE SYNC ERROR')): self.held(self.write)
        before = self.files(); self.assertTrue(before)
        self.write(); self.assertEqual(before, self.files())

    def test_unknown_legacy_start_without_custody_is_not_retroactively_adopted(self):
        self.history(); self.child(self.key).communicate('', timeout=10)
        before = self.files(); self.held(self.write)
        self.assertEqual(before, self.files()); self.assertFalse((self.root/'worker-custody').exists())

    def test_same_original_manager_ack_history_and_signed_binding_allow_next_epoch(self):
        from tests import test_post_preview_sandbox_visits as original_tests
        from photobooth.catalog import get_templates
        from photobooth.post_preview_worker_binding import (
            bind_original_worker_generation, install_worker_generation_bindings)
        helper = original_tests.OriginalSandboxVisitTests(methodName='runTest')
        create = WorkerFenceKey.create
        def original_mint():
            key = create()
            write_eligible_worker_escrow(helper.visits._launcher, helper.config, key)
            return key
        # Test-only trusted pre-work interception. Production mounting and
        # native BEFORE-photo ordering are NOT claimed by this seam exercise.
        with patch.object(WorkerFenceKey, 'create', side_effect=original_mint):
            try:
                helper.setUp()
                manager = helper.visits; service = helper.binding.service
                install_worker_generation_bindings(service.ledger)
                service.start(get_templates(), {'template_a': 1})
                bind_original_worker_generation(service.ledger, service.lease,
                    manager._launcher, helper.config, manager._key)
                old = manager._key.key_id; old_scope = helper.config.private_root/'worker-custody'/(old+'.json')
                digest = hashlib.sha256(old_scope.read_bytes()).hexdigest()
                service.retire('USER_CANCEL')
                helper.retry(manager.ensure_new_visitor_ready)
                self.assertNotEqual(old, manager._key.key_id)
                self.assertEqual(digest, hashlib.sha256(old_scope.read_bytes()).hexdigest())
                self.assertEqual(1, manager.ledger.db.execute('SELECT COUNT(*) FROM pp_worker_generations').fetchone()[0])
                self.assertEqual('ACKED', manager.ledger.db.execute('SELECT state FROM pp_isolation_ops').fetchone()[0])
            finally:
                helper.doCleanups()


if __name__ == '__main__': unittest.main()
