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
            fixture = Path(__file__).with_name('post_preview_process_fault_fixture.py')
            result = subprocess.run(
                [sys.executable, str(fixture), folder, stage],
                text=True, capture_output=True, timeout=50)
            self.assertEqual(73, result.returncode, result.stderr[-3000:])
            reopened = subprocess.run(
                [sys.executable, str(fixture), folder, 'inspect-' + stage],
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


if __name__ == '__main__':
    unittest.main()
