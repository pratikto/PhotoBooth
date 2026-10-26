"""Liveness/recovery boundaries tested without payment, hardware or customer files."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from photobooth.kiosk_v2.watchdog import (
    AppHeartbeat, HeartbeatWriter, WatchdogMonitor, attach_heartbeat,
    read_heartbeat, supervise, windows_startup_script,
)


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.monitor = WatchdogMonitor('visit-free-run', 123, clock=lambda: self.now,
                                       startup_timeout=90, stale_timeout=30)

    def pulse(self, sequence=1, phase='running', **changes):
        return dict(schema_version=1, run_id='visit-free-run', pid=123,
                    sequence=sequence, phase=phase, **changes)

    def test_startup_has_own_grace_even_with_starting_pulses(self):
        self.assertEqual(self.monitor.observe()['status'], 'STARTING')
        self.now = 89
        self.assertEqual(self.monitor.observe(self.pulse(1, 'starting'))['status'], 'STARTING')
        self.now = 90
        self.assertEqual(self.monitor.observe(self.pulse(2, 'starting'))['status'], 'STARTUP_TIMEOUT')
        self.assertEqual(self.monitor.observe(self.pulse(3))['status'], 'RUNNING')

    def test_frozen_event_loop_detected_and_recovers_only_on_new_pulse(self):
        payload = self.pulse()
        self.monitor.observe(payload)
        self.now = 30
        report = self.monitor.observe(payload)
        self.assertEqual(report['status'], 'UNRESPONSIVE')
        self.assertTrue(report['operator_attention'])
        self.assertFalse(report['automatic_restart'])
        self.assertEqual(self.monitor.observe(self.pulse(2))['status'], 'RUNNING')

    def test_suspension_is_visible_but_does_not_mask_a_later_hang(self):
        self.assertEqual(self.monitor.observe(self.pulse(1, 'suspended'))['status'], 'SUSPENDED')
        self.now = 31
        self.assertEqual(self.monitor.observe()['status'], 'UNRESPONSIVE')
        self.assertEqual(self.monitor.observe(self.pulse(2))['status'], 'RUNNING')

    def test_malformed_foreign_replayed_and_stale_messages_do_not_refresh(self):
        self.monitor.observe(self.pulse(5))
        invalid = [None, [], 1, {'phase': 'running'}, self.pulse(4), self.pulse(5)]
        for key, value in [('pid', 999), ('run_id', 'previous'), ('sequence', True),
                           ('phase', []), ('phase', 'secret-value'), ('schema_version', 2)]:
            item = self.pulse(6)
            item[key] = value
            invalid.append(item)
        self.now = 31
        for item in invalid:
            with self.subTest(payload=item):
                self.assertEqual(self.monitor.observe(item)['status'], 'UNRESPONSIVE')

    def test_exit_is_authoritative_even_after_stopping_heartbeat(self):
        self.monitor.observe(self.pulse(1, 'stopping'))
        self.now = 31
        self.assertEqual(self.monitor.observe()['status'], 'UNRESPONSIVE')
        for code, status in [(0, 'EXITED'), (1, 'CRASHED'), (-11, 'CRASHED')]:
            report = self.monitor.observe(exit_code=code)
            self.assertEqual(report['status'], status)
            self.assertEqual(report['exit_code'], code)
            self.assertFalse(report['automatic_restart'])

    def test_invalid_timeout_rejected(self):
        for value in [0, -1, float('inf'), float('nan')]:
            with self.assertRaises(ValueError):
                WatchdogMonitor('run', 1, stale_timeout=value)

    def test_writer_is_redacted_and_uses_atomic_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'heartbeat.json'
            writer = HeartbeatWriter(path, 'run', pid=123)
            writer.pulse('running')
            writer.pulse('suspended')
            data = read_heartbeat(path)
            self.assertEqual(data, dict(schema_version=1, run_id='run', pid=123,
                                        sequence=2, phase='suspended'))
            self.assertFalse(path.with_suffix('.tmp').exists())
            path.write_text('x' * 3000)
            self.assertIsNone(read_heartbeat(path))
            path.write_bytes(b'\xff')
            self.assertIsNone(read_heartbeat(path))
            path.unlink()
            self.assertIsNone(read_heartbeat(path))

    def test_unwritable_heartbeat_does_not_interrupt_application(self):
        with tempfile.TemporaryDirectory() as folder:
            writer = HeartbeatWriter(Path(folder) / 'absent' / 'heartbeat', 'run')
            writer.pulse('running')
            writer.pulse('running')

    def test_ui_hook_has_no_business_actions_and_cancels_its_clock(self):
        clock, writer = Mock(), Mock()
        app = SimpleNamespace(_suspended=False, _closed=False)
        hook = AppHeartbeat(app, clock, writer)
        self.assertEqual(writer.pulse.call_args.args, ('starting',))
        hook.tick(2)
        self.assertEqual(writer.pulse.call_args.args, ('running',))
        app._suspended = True
        hook.tick(2)
        self.assertEqual(writer.pulse.call_args.args, ('suspended',))
        app._closed = True
        hook.tick(2)
        hook.close()
        clock.schedule_interval.return_value.cancel.assert_called_once()
        self.assertEqual(writer.pulse.call_args.args, ('stopping',))
        self.assertIsNone(attach_heartbeat(app, clock, environ={}))

    def test_supervision_records_hang_recovery_and_exit_without_process_mutations(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'pulse.json'
            report = Path(folder) / 'report.json'
            writer = HeartbeatWriter(path, 'visit-free-run', pid=123)
            writer.pulse('running')
            process = Mock()
            process.poll.side_effect = [None, None, None, None, 7]
            def wait(_seconds):
                self.now += 31
                if self.now == 62:
                    writer.pulse('running')
            states = []
            self.assertEqual(supervise(process, path, report, self.monitor,
                                       wait=wait, announce=states.append), 7)
            self.assertEqual(states, ['MEONG watchdog: RUNNING', 'MEONG watchdog: UNRESPONSIVE',
                                     'MEONG watchdog: RUNNING', 'MEONG watchdog: UNRESPONSIVE',
                                     'MEONG watchdog: CRASHED'])
            self.assertTrue(json.loads(report.read_text())['operator_attention'])
            self.assertEqual({call[0] for call in process.mock_calls}, {'poll'})

    def test_ctrl_c_and_disk_failure_do_not_terminate_an_uncertain_visit(self):
        process = Mock()
        process.poll.side_effect = [None, None, 0]
        wait = Mock(side_effect=[KeyboardInterrupt(), None])
        with patch('photobooth.kiosk_v2.watchdog.write_json_atomic', side_effect=OSError('disk full')):
            result = supervise(process, 'absent', 'report', self.monitor, wait=wait, announce=Mock())
        self.assertEqual(result, 0)
        process.terminate.assert_not_called()
        process.kill.assert_not_called()

    def test_actual_child_exit_and_crash_are_observed_without_relaunch(self):
        with tempfile.TemporaryDirectory() as folder:
            for code in (0, 9):
                child = subprocess.Popen([sys.executable, '-c', f'raise SystemExit({code})'])
                try:
                    result = supervise(child, Path(folder) / 'absent', Path(folder) / 'report',
                                       WatchdogMonitor('child', child.pid), wait=lambda _: child.wait(timeout=5),
                                       announce=lambda _: None)
                    self.assertEqual(result, code)
                finally:
                    child.wait(timeout=5)

    def test_startup_script_is_reviewable_and_has_no_restart_loop_or_secret_dump(self):
        script = windows_startup_script('/workspace/My Booth', sys.executable, ['--print', '--drive'])
        self.assertIn('cd /d "', script)
        self.assertIn('run_portrait_v2_watchdog.py" --print --drive', script)
        self.assertNotIn('goto', script.lower())
        self.assertNotIn('schtasks', script.lower())
        self.assertNotIn('MIDTRANS', script)
        for fragment in ['x%PATH%', 'x&echo', 'x!secret!', 'x\ncommand']:
            with self.assertRaises(ValueError):
                windows_startup_script(fragment, sys.executable)
        with self.assertRaises(ValueError):
            windows_startup_script('.', sys.executable, ['--manual-print'])
        with self.assertRaises(ValueError):
            windows_startup_script('.', sys.executable, ['--token=secret'])

    def test_launcher_help_does_not_import_kivy_or_open_a_device(self):
        path = Path(__file__).resolve().parents[1] / 'tools/run_portrait_v2_watchdog.py'
        result = subprocess.run([sys.executable, '-S', str(path), '--help'], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertIn('--write-startup', result.stdout)
        self.assertNotIn('[Kivy', result.stderr)

    def test_launcher_heartbeat_is_closed_even_when_app_run_raises(self):
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('watchdog_launcher_test', root / 'tools/run_portrait_v2.py')
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        app = Mock()
        app.return_value.run.side_effect = RuntimeError('native event loop failed')
        modules = {'kivy.config': SimpleNamespace(Config=Mock()),
                   'kivy.clock': SimpleNamespace(Clock=Mock()),
                   'photobooth.kiosk_v2.app': SimpleNamespace(PortraitKioskV2App=app)}
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, modules), \
                patch.dict(os.environ, {'MEONG_WATCHDOG_HEARTBEAT': str(Path(folder) / 'pulse'),
                                        'MEONG_WATCHDOG_RUN_ID': 'test'}), \
                patch('builtins.print'), patch.object(launcher, 'PROJECT_ROOT', Path(folder)), \
                patch('photobooth.kiosk_v2.watchdog.attach_heartbeat') as attach:
            with self.assertRaisesRegex(RuntimeError, 'native event loop failed'):
                launcher.main()
            attach.return_value.close.assert_called_once_with()
            app.return_value._photo_jobs.wait_closed.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
