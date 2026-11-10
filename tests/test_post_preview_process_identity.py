"""Actual read-only process birth/exit, no worker/device/recovery acceptance."""
from dataclasses import replace
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from photobooth.post_preview_bootstrap import backend_environment
from photobooth.post_preview_process_identity import (
    OriginalProcessIdentity, ProcessObservationHeld, observe_process, original_process_exited)


class ProcessIdentityTests(unittest.TestCase):
    def test_actual_current_process_live_identity_stable(self):
        first = observe_process(os.getpid())
        self.assertEqual(first, observe_process(os.getpid()))
        self.assertFalse(original_process_exited(first))
        self.assertTrue(first.birth.startswith('windows-filetime-' if os.name == 'nt' else 'linux-'))

    def test_actual_child_is_live_then_exits_cooperatively(self):
        child = subprocess.Popen([sys.executable, '-c',
            'import sys; print("READY", flush=True); sys.stdin.read()'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=Path(__file__).resolve().parents[1], env=backend_environment(os.environ))
        try:
            self.assertEqual(child.stdout.readline().strip(), 'READY')
            identity = observe_process(child.pid)
            self.assertFalse(original_process_exited(identity))
            child.communicate('', timeout=10)  # Original cooperative exit, no terminate/kill.
            self.assertEqual(child.returncode, 0)
            self.assertTrue(original_process_exited(identity))
            with self.assertRaises(ProcessObservationHeld):
                observe_process(child.pid)
        finally:
            if child.poll() is None:
                child.communicate('', timeout=10)

    def test_pid_reuse_or_foreign_birth_does_not_authorize_exit(self):
        identity = observe_process(os.getpid())
        prefix = 'windows-filetime-' if os.name == 'nt' else 'linux-'
        other = prefix + ('a'*16 if os.name == 'nt' else 'a'*32+'-123')
        with self.assertRaises(ProcessObservationHeld):
            original_process_exited(replace(identity, birth=other))

    def test_invalid_pid_identity_and_wrong_platform_are_held(self):
        for value in (True, False, 0, -1, 2**32, '123', 1.5, None):
            with self.assertRaises(ProcessObservationHeld):
                observe_process(value)
        for birth in ('', 'declared-only', 'x'*129):
            with self.assertRaises(ProcessObservationHeld):
                OriginalProcessIdentity(os.getpid(), birth)
        with self.assertRaises(ProcessObservationHeld):
            original_process_exited(object())
        foreign = 'linux-'+'a'*32+'-1' if os.name == 'nt' else 'windows-filetime-'+'a'*16
        with self.assertRaises(ProcessObservationHeld):
            original_process_exited(OriginalProcessIdentity(os.getpid(), foreign))

    def test_access_failure_is_redacted_and_never_treated_as_death(self):
        target = ('_windows_snapshot' if os.name == 'nt' else '_linux_snapshot')
        identity = observe_process(os.getpid())
        with patch('photobooth.post_preview_process_identity.'+target,
                   side_effect=PermissionError('PRIVATE OS DETAIL')):
            for action in (lambda: observe_process(identity.pid), lambda: original_process_exited(identity)):
                with self.assertRaises(ProcessObservationHeld) as caught:
                    action()
                self.assertEqual(str(caught.exception), 'Original process observation is unavailable')

    def test_claimed_birth_cannot_replace_fresh_os_observation(self):
        identity = observe_process(os.getpid())
        target = ('_windows_snapshot' if os.name == 'nt' else '_linux_snapshot')
        with patch('photobooth.post_preview_process_identity.'+target, return_value=(identity.birth, True)):
            self.assertTrue(original_process_exited(identity))
            with self.assertRaises(ProcessObservationHeld):
                observe_process(identity.pid)
