"""Actual original process metadata witness; never recovery/retirement proof."""
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_bootstrap import backend_environment
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_process_identity import observe_process, original_process_exited
from photobooth.post_preview_worker_fence import WorkerFenceKey, canonical
from photobooth.post_preview_worker_start import WorkerStartHeld, record_worker_start, read_worker_start


class WorkerStartWitnessTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.config = SandboxHostConfig(Path(temporary.name), 'MTEST', 'PB001',
            'Mid-server-WITNESS-FIXTURE', 'b'*48,
            'https://script.google.com/macros/s/WITNESS_FIXTURE/exec', 'fixture-drive')
        self.launcher = LaunchLease(self.config.private_root); self.addCleanup(self.launcher.close)
        self.key = WorkerFenceKey.create()
        self.child = subprocess.Popen([sys.executable, '-c',
            'import sys; print("READY", flush=True); sys.stdin.read()'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, env=backend_environment(os.environ))
        self.addCleanup(self.stop_child)
        self.assertEqual('READY', self.child.stdout.readline().strip())
        self.path = self.config.private_root/'worker-starts'/(self.key.key_id+'.json')

    def stop_child(self):
        if self.child.poll() is None: self.child.communicate('', timeout=10)
        else:
            if self.child.stdin is not None: self.child.stdin.close()
            if self.child.stdout is not None: self.child.stdout.close()

    def held(self, action):
        with self.assertRaises(WorkerStartHeld) as caught: action()
        self.assertEqual('Original worker start witness is held', str(caught.exception))

    def record(self):
        return record_worker_start(self.launcher, self.config, self.key, self.child)

    def read(self):
        return read_worker_start(self.launcher, self.config, self.key)

    def test_actual_child_parent_birth_original_key_and_scope_are_bound(self):
        frame = self.record()
        self.assertEqual('ORIGINAL_WORKER_START', frame['kind'])
        self.assertEqual(self.child.pid, frame['child_pid'])
        self.assertEqual(observe_process(self.child.pid).birth, frame['child_birth'])
        self.assertEqual(observe_process(os.getpid()).birth, frame['parent_birth'])
        self.assertEqual(self.key.key_id, frame['worker_epoch'])
        self.assertEqual(frame, self.read())
        raw = self.path.read_text()
        for value in (self.key.secret.hex(), self.config.server_key,
                      self.config.booth_token, self.config.drive_token, self.config.drive_url):
            self.assertFalse(value in raw)

    def test_same_live_owner_child_and_key_retry_preserves_bytes_and_timestamp(self):
        self.record()
        before, stamp = self.path.read_bytes(), self.path.stat().st_mtime_ns
        with patch.object(WorkerFenceKey, 'create', side_effect=AssertionError('No replacement')):
            self.record()
        self.assertEqual(hashlib.sha256(before).hexdigest(), hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(stamp, self.path.stat().st_mtime_ns)

    def test_new_or_same_id_replacement_key_and_foreign_root_are_held(self):
        self.record()
        for key in (WorkerFenceKey.create(), WorkerFenceKey(self.key.key_id, os.urandom(32))):
            self.held(lambda: read_worker_start(self.launcher, self.config, key))
        self.held(lambda: read_worker_start(self.launcher, replace(self.config, merchant_id='FOREIGN'), self.key))
        self.held(lambda: record_worker_start(object(), self.config, self.key, self.child))
        self.launcher.close()
        self.held(self.record)

    def test_role_tamper_even_with_valid_mac_is_not_a_retirement_receipt(self):
        self.record()
        value = json.loads(self.path.read_bytes())
        value['frame']['kind'] = 'ORIGINAL_WORKER_RETIRED'
        value['mac'] = self.key.sign(value['frame'])
        raw = canonical(value).encode(); self.path.write_bytes(raw)  # Public fault fixture.
        self.held(self.read); self.held(self.record)
        self.assertTrue(raw == self.path.read_bytes())

    def test_corrupt_partial_or_linked_original_record_is_never_replaced(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b'{')
        self.held(self.record); self.held(self.read)
        self.assertTrue(self.path.read_bytes() == b'{')

    def test_hardlinked_record_and_alias_are_preserved_and_held(self):
        self.record()
        alias = self.path.parent/'alias.json'; os.link(self.path, alias)
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.held(self.record); self.held(self.read)
        self.assertEqual(before, hashlib.sha256(alias.read_bytes()).hexdigest())

    def test_failed_sync_preserves_original_bytes_and_same_owner_can_resync(self):
        with patch('photobooth.post_preview_worker_start.os.fsync', side_effect=OSError('PRIVATE IO DETAIL')):
            self.held(self.record)
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.record()
        self.assertEqual(before, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_dead_child_cannot_be_retroactively_signed(self):
        self.stop_child()
        self.held(self.record)
        self.assertFalse(self.path.exists())

    def test_closed_native_owner_prevents_bootstrap_popen(self):
        import socket
        from photobooth.post_preview_bootstrap import SandboxBackendProcess
        from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment
        from photobooth.printer import PrinterConfig
        bundle = SandboxHostFulfillment(PrinterConfig(lan_host='fixture-printer', usb_device_path=None), self.key)
        backend = SandboxBackendProcess(self.config, fulfillment=bundle, worker_launcher=self.launcher)
        peer, channel = socket.socketpair()
        self.addCleanup(peer.close); self.addCleanup(channel.close)
        self.launcher.close()
        with patch('photobooth.post_preview_bootstrap.subprocess.Popen') as spawn:
            self.held(lambda: backend.start(channel))
            self.assertEqual(0, spawn.call_count)
        self.assertIsNone(backend.process)

    def test_authenticated_old_metadata_is_not_current_live_or_dead_worker_authority(self):
        identity = observe_process(self.child.pid)
        frame = self.record()
        self.assertFalse(original_process_exited(identity))
        self.stop_child()
        self.assertTrue(original_process_exited(identity))
        self.assertEqual(frame, self.read())  # Metadata is retained, not a release.
        self.held(self.record)  # Cannot sign again for the exited original child.
