"""Abrupt external child termination at original PAID print journal boundary.

No physical paper or merchant network is used. The Python process actually
exits without cleanup and its WAL-backed SQLite state is reopened by a second
independent Python process for inspection.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class OriginalPrintProcessCrashTests(unittest.TestCase):
    def run_hard_exit_and_reopen(self, stage):
        with tempfile.TemporaryDirectory() as folder:
            repo_root = Path(__file__).resolve().parents[1]
            command = [sys.executable, '-m', 'tests.post_preview_process_fault_fixture']
            result = subprocess.run(
                command + [folder, stage], cwd=repo_root,
                text=True, capture_output=True, timeout=50)
            self.assertEqual(73, result.returncode, result.stderr[-3000:])
            reopened = subprocess.run(
                command + [folder, 'inspect-' + stage], cwd=repo_root,
                text=True, capture_output=True, timeout=15)
            self.assertEqual(0, reopened.returncode, reopened.stderr[-3000:])
            return json.loads(reopened.stdout)

    def test_p01_actual_process_exit_during_recovery_receipt_preserves_owed(self):
        state = self.run_hard_exit_and_reopen('receipt')
        self.assertEqual('OWED', state['owed'])
        self.assertEqual('SENDING', state['receipt'])
        self.assertEqual(1, state['paid_attempts'])
        self.assertEqual([], state['jobs'])

    def test_p02_actual_process_exit_during_paid_strip_preserves_sending(self):
        state = self.run_hard_exit_and_reopen('strip')
        self.assertEqual('OWED', state['owed'])
        self.assertEqual('SUBMITTED', state['receipt'])
        self.assertEqual(1, state['paid_attempts'])
        self.assertEqual([['SENDING', 2]], state['jobs'])

    def assert_isolation_crash(self, stage, *, acked):
        state = self.run_hard_exit_and_reopen(stage)
        self.assertEqual('OWED', state['owed'])
        self.assertEqual(1, state['paid_attempts'])
        self.assertEqual('SUBMITTED', state['receipt'])
        self.assertEqual([], state['jobs'])
        self.assertRegex(state['operation_id'], r'^[a-f0-9]{32}$')
        self.assertEqual('PAID_OWED', state['financial_class'])
        self.assertEqual('ACKED' if acked else 'PREPARED', state['operation_state'])
        self.assertEqual(int(acked), state['original_closed'])
        self.assertEqual(state['operation_generation']+int(acked), state['original_generation'])
        self.assertEqual(acked, state['new_local_admission'])
        self.assertEqual(int(acked), state['ack_events'])

    def test_p03_process_death_after_prepare_keeps_original_owed_and_blocks_B(self):
        self.assert_isolation_crash('isolation-prepared', acked=False)

    def test_p04_ack_commit_then_reply_loss_keeps_one_durable_local_release(self):
        self.assert_isolation_crash('isolation-acked', acked=True)

    def test_p05_prepare_then_worker_failure_cannot_commit_ack_or_admit_B(self):
        self.assert_isolation_crash('isolation-worker-failed', acked=False)

    def test_p06_archive_event_failure_rolls_back_ack_before_hard_exit(self):
        self.assert_isolation_crash('isolation-rollback', acked=False)


if __name__ == '__main__':
    unittest.main()
