"""Unstaged epoch-binding core; actual DB/process/custody, no external effects."""
from contextlib import nullcontext
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_bootstrap import backend_environment
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_process_identity import observe_process
from photobooth.post_preview_store import DraftHeld, PostPreviewStore
from photobooth.post_preview_worker_binding import (
    bind_original_worker_generation, install_worker_generation_bindings,
    verify_worker_generation_binding)
from photobooth.post_preview_worker_custody import WorkerCustodyScope
from photobooth.post_preview_worker_escrow import write_new_worker_escrow
from photobooth.post_preview_worker_fence import WorkerFenceKey
from photobooth.post_preview_worker_fence import canonical
from photobooth.post_preview_worker_start import record_worker_start


class OriginalWorkerBindingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.config = SandboxHostConfig(Path(temporary.name), 'MTEST', 'PB001',
            'Mid-server-BINDING-FIXTURE', 'b'*48,
            'https://script.google.com/macros/s/BINDING_FIXTURE/exec', 'fixture-drive')
        self.root = self.config.private_root
        self.launcher = LaunchLease(self.root); self.addCleanup(self.launcher.close)
        context = nullcontext() if os.name == 'nt' else patch(
            'photobooth.linux_credential_vault._read_key', return_value=b'k'*32)
        context.__enter__(); self.addCleanup(context.__exit__, None, None, None)
        self.key = WorkerFenceKey.create()
        self.scope = WorkerCustodyScope(self.root, 'MTEST', 'PB001', self.key.key_id,
                                       os.getpid(), observe_process(os.getpid()).birth)
        write_new_worker_escrow(self.launcher, self.key, self.scope)
        self.child = subprocess.Popen([sys.executable, '-c',
            'import sys; print("READY",flush=True); sys.stdin.read()'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, env=backend_environment(os.environ))
        self.addCleanup(self.stop_child)
        self.assertEqual('READY', self.child.stdout.readline().strip())
        self.witness = record_worker_start(self.launcher, self.config, self.key, self.child)
        self.store = PostPreviewStore(self.root/'drafts.sqlite3'); self.addCleanup(self.store.close)
        install_worker_generation_bindings(self.store)
        self.lease = self.store.create('PB001', 'binding-fixture-visit', {'template_a': 1})

    def stop_child(self):
        if self.child.poll() is None: self.child.communicate('', timeout=10)
        else:
            self.child.stdin.close(); self.child.stdout.close()

    def bind(self, **changes):
        args = dict(ledger=self.store, lease=self.lease, launcher=self.launcher,
                    config=self.config, key=self.key); args.update(changes)
        return bind_original_worker_generation(**args)

    def verify(self, **changes):
        args = dict(ledger=self.store, lease=self.lease, key=self.key, scope=self.scope)
        args.update(changes)
        with self.store.write(): return verify_worker_generation_binding(**args)

    def held(self, action):
        with self.assertRaises(DraftHeld) as caught: action()
        self.assertEqual('Original worker generation binding is held', str(caught.exception))

    def rows(self):
        return [tuple(row) for row in self.store.db.execute('SELECT * FROM pp_worker_generations')]

    def test_same_original_escrow_witness_lease_and_capability_bind_without_private_bytes(self):
        frame = self.bind()
        self.assertEqual(frame, self.verify())
        self.assertEqual(hashlib.sha256(json.dumps(self.witness, sort_keys=True,
            separators=(',', ':')).encode()).hexdigest(), frame['worker_start_sha256'])
        self.assertEqual(self.lease.generation, frame['generation'])
        raw = str(self.rows())
        for private in (self.key.secret.hex(), str(self.root), self.config.server_key,
                        self.config.booth_token, self.config.drive_token):
            self.assertNotIn(private, raw)
        self.assertEqual(1, self.store.db.execute('SELECT COUNT(*) FROM pp_drafts').fetchone()[0])

    def test_exact_retry_does_not_mint_replace_or_append(self):
        self.bind(); before = self.rows(); events = self.store.db.total_changes
        with patch.object(WorkerFenceKey, 'create', side_effect=AssertionError('No replacement')):
            install_worker_generation_bindings(self.store)
            self.bind()
        self.assertEqual(before, self.rows()); self.assertEqual(events, self.store.db.total_changes)

    def test_update_delete_and_insert_replace_cannot_rewrite_original(self):
        self.bind(); before = self.rows()
        for query in ('UPDATE pp_worker_generations SET mac=mac',
                      'DELETE FROM pp_worker_generations',
                      'INSERT OR REPLACE INTO pp_worker_generations SELECT * FROM pp_worker_generations'):
            with self.store.write(), self.assertRaises(sqlite3.IntegrityError): self.store.db.execute(query)
        self.assertEqual(before, self.rows())

    def test_missing_binding_is_never_reconstructed_by_reader(self):
        self.held(self.verify); self.assertEqual([], self.rows())
        self.assertEqual('ACTIVE', self.store.inspect(self.lease)['lifecycle'])

    def test_unsealed_key_or_declared_witness_without_original_files_is_held(self):
        path = self.root/'worker-starts'/(self.key.key_id+'.json')
        raw = path.read_bytes(); path.write_bytes(b'{')  # Isolated public corrupt fixture.
        self.held(self.bind); self.assertEqual([], self.rows()); self.assertEqual(b'{', path.read_bytes())
        path.write_bytes(raw)
        escrow = self.root/'worker-custody'/(self.key.key_id+'.json')
        escrow.write_bytes(b'{'); self.held(self.bind)
        self.assertEqual([], self.rows()); self.assertEqual(b'{', escrow.read_bytes())

    def test_dead_child_closed_owner_and_unavailable_os_key_hold_before_insert(self):
        with patch('photobooth.post_preview_worker_custody.platform_protector',
                   side_effect=RuntimeError('PRIVATE OS DETAIL')): self.held(self.bind)
        self.stop_child(); self.held(self.bind)
        self.launcher.close(); self.held(self.bind); self.assertEqual([], self.rows())

    def test_stale_foreign_or_boolean_generation_cannot_bind(self):
        for lease in (replace(self.lease, generation=2), replace(self.lease, generation=True),
                      replace(self.lease, visit_id='foreign'), replace(self.lease, booth_id='PB002')):
            self.held(lambda: self.bind(lease=lease))
        self.assertEqual([], self.rows())

    def test_wrong_or_same_id_replacement_key_and_foreign_root_cannot_bind(self):
        self.bind(); before = self.rows()
        for key in (WorkerFenceKey.create(), WorkerFenceKey(self.key.key_id, os.urandom(32))):
            self.held(lambda: self.bind(key=key)); self.held(lambda: self.verify(key=key))
        other = PostPreviewStore(self.config.storage_root/'foreign'/'drafts.sqlite3')
        try: self.held(lambda: self.bind(ledger=other))
        finally: other.close()
        self.assertEqual(before, self.rows())

    def test_epoch_cannot_be_reassigned_to_a_second_generation(self):
        self.bind(); before = self.rows()
        # Public test-only transition, not a claim/ACK/payment implementation.
        with self.store.write(): self.store.db.execute('UPDATE pp_drafts SET generation=generation+1')
        self.held(lambda: self.bind(lease=replace(self.lease, generation=2)))
        self.assertEqual(before, self.rows())
        self.assertEqual(self.lease.generation, self.verify()['generation'])

    def test_retired_generation_is_readable_but_cannot_be_retroactively_bound(self):
        self.bind(); before = self.rows()
        self.store.lifecycle_event(self.lease, 'USER_CANCEL')
        self.assertEqual(self.lease.generation, self.verify()['generation'])
        self.held(self.bind); self.assertEqual(before, self.rows())
        self.assertEqual(0, self.store.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])

    def test_wrong_account_scope_or_version_does_not_verify(self):
        self.bind(); before = self.rows()
        for scope in (replace(self.scope, merchant_id='FOREIGN'),
                      replace(self.scope, booth_id='PB002'), replace(self.scope, process_birth='declared-only')):
            self.held(lambda: self.verify(scope=scope))
        self.assertEqual(before, self.rows())

    def test_unknown_schema_or_weakened_existing_trigger_is_preserved_and_held(self):
        with self.store.write():
            self.store.db.execute('DROP TRIGGER pp_worker_generation_no_delete')
            self.store.db.execute('CREATE TRIGGER pp_worker_generation_no_delete BEFORE DELETE ON pp_worker_generations BEGIN SELECT 1; END')
        before = [tuple(row) for row in self.store.db.execute("SELECT name,sql FROM sqlite_master WHERE name LIKE 'pp_worker_generation%'")]
        self.held(lambda: install_worker_generation_bindings(self.store))
        self.assertEqual(before, [tuple(row) for row in self.store.db.execute("SELECT name,sql FROM sqlite_master WHERE name LIKE 'pp_worker_generation%'")])

    def test_valid_mac_cannot_change_role_version_or_custody_scope(self):
        frame = self.bind()
        # Deliberate offline corruption fixture: bypass immutable SQL trigger
        # only to exercise the independent reader's authenticated shape checks.
        with self.store.write(): self.store.db.execute('DROP TRIGGER pp_worker_generation_no_update')
        for changes in ({'kind':'ORIGINAL_WORKER_RETIRED'}, {'mode':'mock'},
                        {'generation':True}, {'version':True}, {'order_version':'foreign'},
                        {'worker_start_sha256':'z'*64}, {'private_proof':'must-never-appear'}):
            changed = dict(frame, **changes)
            with self.store.write(): self.store.db.execute(
                'UPDATE pp_worker_generations SET frame_json=?,mac=?',
                (canonical(changed), self.key.sign(changed)))
            self.held(self.verify)

    def test_postinsert_verification_failure_rolls_back_without_discarding_customer(self):
        before = dict(self.store.db.execute('SELECT * FROM pp_drafts').fetchone())
        with patch('photobooth.post_preview_worker_binding.verify_worker_generation_binding',
                   side_effect=DraftHeld('PRIVATE DIAGNOSTIC')): self.held(self.bind)
        self.assertEqual([], self.rows())
        self.assertEqual(before, dict(self.store.db.execute('SELECT * FROM pp_drafts').fetchone()))


if __name__ == '__main__': unittest.main()
