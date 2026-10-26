"""Durable startup review and native launch ownership, without service imports."""
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from photobooth.kiosk_v2.recovery import LaunchLease, review_recovery
from photobooth.kiosk_v2.watchdog import WatchdogMonitor, systemd_user_unit

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location('recovery_' + name, ROOT / 'tools' / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
        return path

    def review(self, **env):
        return review_recovery(self.root, environ=env)

    def manifest(self, **data):
        return self.write('data/Photobooth/PB001/PB001V2S2_00000001/manifest.json',
                          dict(status='COMPLETED', test_print_jobs={}, **data))

    def test_empty_install_is_clear_without_creating_files(self):
        self.assertEqual(self.review()['status'], 'CLEAR_FOR_MANUAL_START')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_completed_photos_with_pending_drive_and_empty_reserves_are_clear(self):
        self.manifest(upload_status='PENDING_DRIVE_BINDING')
        (self.root / 'data/Photobooth/PB001/PB001V2S2_00000002').mkdir()
        self.assertEqual(self.review()['status'], 'CLEAR_FOR_MANUAL_START')

    def test_incomplete_and_aborted_photo_records(self):
        path = self.manifest()
        for data, expected in [({'status': 'IN_PROGRESS'}, 'OPERATOR_REVIEW'),
                               ({'status': 'IN_PROGRESS', 'test_ended_early': True}, 'CLEAR_FOR_MANUAL_START'),
                               ({}, 'OPERATOR_REVIEW')]:
            path.write_text(json.dumps(data))
            self.assertEqual(self.review()['status'], expected)

    def test_every_uncertain_print_state_needs_review_until_explicit_ack(self):
        path = self.manifest()
        for state, checked, held in [('SENDING', False, True), ('SENDING', True, True),
                                     ('UNCERTAIN', False, True), ('UNCERTAIN', True, False),
                                     ('SUBMITTED', False, False)]:
            path.write_text(json.dumps({'status': 'COMPLETED', 'test_print_jobs': {
                'session_001': {'state': state, 'operator_checked': checked}}}))
            with self.subTest(state=state, checked=checked):
                report = self.review()
                self.assertEqual('PRINT_UNCERTAIN' in report['findings'], held)
                self.assertFalse(report['automatic_restart'])
                self.assertFalse(report['replay_allowed'])

    def test_malformed_journals_and_unknown_states_fail_closed(self):
        path = self.manifest()
        for text in ('not json', '[]', '{"test_print_jobs": []}',
                     '{"status":"COMPLETED","test_print_jobs":{"s":{"state":"NEW"}}}'):
            path.write_text(text)
            self.assertIn('LOCAL_STATE_UNREADABLE', self.review()['findings'])

    def test_all_nonterminal_sandbox_phases_hold_even_with_mode_off(self):
        path = self.write('data/kiosk-v2-sandbox/demo/PB001/visit.json', {})
        for phase in ('CREATING', 'WAITING', 'RESERVED', 'STARTING', 'STARTED',
                      'COMPLETING', 'CANCELLING', 'RECOVERY', 'COMPLETED', 'CANCELLED'):
            path.write_text(json.dumps({'version': 1, 'phase': phase,
                                        'context': {'endpoint': 'secret'}, 'checkout_key': 'private'}))
            result = self.review(PHOTOBOOTH_V2_CHECKOUT_SANDBOX='0')
            self.assertEqual('SANDBOX_UNRESOLVED' in result['findings'],
                             phase not in {'COMPLETED', 'CANCELLED'})
            self.assertNotIn('secret', json.dumps(result))
            self.assertNotIn('private', json.dumps(result))

    def test_explicit_sandbox_journal_is_checked_once_and_cannot_escape_scope(self):
        path = self.write('data/kiosk-v2-sandbox/demo/PB001/visit.json', {'version': 1, 'phase': 'STARTED'})
        result = self.review(MEONG_QRIS_JOURNAL=str(path))
        self.assertEqual(result['checked']['sandbox_journals'], 1)
        self.assertEqual(result['findings']['SANDBOX_UNRESOLVED'], 1)
        outside = self.write('private.json', {'version': 1, 'phase': 'COMPLETED'})
        self.assertIn('LOCAL_STATE_UNREADABLE', self.review(MEONG_QRIS_JOURNAL=str(outside))['findings'])

    def test_missing_sandbox_visit_with_existing_backend_is_held(self):
        self.write('data/kiosk-v2-sandbox/demo/PB001/orders.sqlite', {})
        self.assertIn('SANDBOX_JOURNAL_MISSING', self.review()['findings'])

    def test_missing_manifest_with_media_is_held_without_opening_images(self):
        self.write('data/Photobooth/PB001/PB001V2S2_00000001/Photo/01/raw/photo.jpg', {'never': 'read'})
        self.assertIn('MISSING_PHOTO_MANIFEST', self.review()['findings'])

    def test_legacy_photo_root_and_explicit_offline_storage_root_are_checked(self):
        self.write('data/kiosk-v2-p3/photos/PB001V2_00000001/manifest.json', {'status': 'IN_PROGRESS'})
        self.write('data/kiosk-v2-p3/photos/CUSTOMV2_100000000/manifest.json', {'status': 'IN_PROGRESS'})
        self.write('custom/PB002/PB002V2S2_00000002/manifest.json', {'status': 'IN_PROGRESS'})
        report = self.review(PHOTOBOOTH_V2_STORAGE_ROOT=str(self.root / 'custom'))
        self.assertEqual(report['findings']['PHOTO_INCOMPLETE'], 3)

    def test_old_is_pruned_and_linked_storage_is_rejected_before_descent(self):
        self.write('data/Photobooth/old/PB001/PB001V2S2_00000001/manifest.json', {'status': 'IN_PROGRESS'})
        self.assertEqual(self.review()['status'], 'CLEAR_FOR_MANUAL_START')
        target = self.root / 'data/Photobooth/PB001'
        try:
            target.symlink_to(self.root / 'data/Photobooth/old', target_is_directory=True)
        except OSError:
            self.skipTest('Creating a test symlink requires OS support')
        self.assertIn('LOCAL_STATE_UNREADABLE', self.review()['findings'])

    def test_old_configured_root_and_bounded_scanning_fail_closed(self):
        self.assertIn('LOCAL_STATE_UNREADABLE', self.review(PHOTOBOOTH_V2_STORAGE_ROOT=str(self.root/'old'))['findings'])
        self.manifest()
        self.assertIn('LOCAL_STATE_UNREADABLE', review_recovery(self.root, environ={}, limit=0)['findings'])

    def test_oversized_manifest_is_not_treated_as_empty(self):
        path = self.manifest()
        path.write_bytes(b' ' * (4 * 1024 * 1024 + 1))
        self.assertIn('LOCAL_STATE_UNREADABLE', self.review()['findings'])

    def test_mock_review_does_not_expire_or_mutate_pending_order(self):
        path = self.root / 'data/kiosk-v2-p4/demo-attempts.sqlite3'
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE mock_orders (state TEXT)')
            db.executemany('INSERT INTO mock_orders VALUES (?)', [('PENDING',), ('UNKNOWN',), ('ADMITTED',)])
        before = path.read_bytes()
        report = self.review()
        self.assertEqual(report['findings']['MOCK_UNRESOLVED'], 2)
        self.assertEqual(path.read_bytes(), before)

    def test_game_only_ledger_is_valid_but_corrupt_database_is_held(self):
        path = self.root / 'data/kiosk-v2-p4/demo-attempts.sqlite3'
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE attempts (token TEXT)')
        self.assertEqual(self.review()['status'], 'CLEAR_FOR_MANUAL_START')
        path.write_bytes(b'broken database')
        self.assertIn('LOCAL_STATE_UNREADABLE', self.review()['findings'])

    def test_review_does_not_modify_json_journals(self):
        paths = [self.manifest(), self.write('data/kiosk-v2-sandbox/demo/PB001/visit.json',
                                            {'version': 1, 'phase': 'STARTING'})]
        before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]
        self.review()
        self.assertEqual(before, [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths])

    def test_kernel_lock_prevents_duplicate_process_and_releases_on_exit(self):
        code = ('from photobooth.kiosk_v2.recovery import LaunchLease; import sys; '
                'lease=LaunchLease(sys.argv[1]); print("owned", flush=True); sys.stdin.read()')
        child = subprocess.Popen([sys.executable, '-S', '-c', code, str(self.root)], cwd=ROOT,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), 'owned')
            with self.assertRaises(OSError):
                LaunchLease(self.root)
            child.stdin.close()
            self.assertEqual(child.wait(timeout=5), 0)
            with LaunchLease(self.root):
                pass
        finally:
            if child.poll() is None:
                child.kill(); child.wait(timeout=5)
            child.stdout.close()

    def test_launcher_holds_lock_through_worker_teardown_and_releases_on_exception(self):
        launcher = module('run_portrait_v2')
        with patch.object(launcher, 'PROJECT_ROOT', self.root):
            def run():
                with self.assertRaises(OSError): LaunchLease(self.root)
                raise RuntimeError('fixture failure')
            with patch.object(launcher, 'run_app', side_effect=run):
                with self.assertRaisesRegex(RuntimeError, 'fixture failure'):
                    launcher.main()
        with LaunchLease(self.root): pass

    def test_recovery_hold_stops_before_native_import_or_app_build(self):
        self.manifest().write_text('{"status":"IN_PROGRESS"}')
        launcher = module('run_portrait_v2')
        with patch.object(launcher, 'PROJECT_ROOT', self.root), \
                patch.dict(os.environ, {'MEONG_WATCHDOG_RECOVERY_GATE': '1'}), \
                patch.object(launcher, 'run_app') as app, patch('builtins.print'):
            self.assertEqual(launcher.main(), 3)
            app.assert_not_called()

    def test_duplicate_launcher_does_not_start_any_services(self):
        launcher = module('run_portrait_v2')
        with LaunchLease(self.root), patch.object(launcher, 'PROJECT_ROOT', self.root), \
                patch.object(launcher, 'run_app') as app, patch('builtins.print'):
            self.assertEqual(launcher.main(), 2)
            app.assert_not_called()

    def test_watchdog_reports_recovery_and_ownership_holds_without_restart(self):
        monitor = WatchdogMonitor('run', 123)
        for code, status in [(2, 'STARTUP_BLOCKED'), (3, 'RECOVERY_HOLD')]:
            result = monitor.observe(exit_code=code)
            self.assertEqual(result['status'], status)
            self.assertTrue(result['operator_attention'])
            self.assertFalse(result['automatic_restart'])


class UbuntuStartupTests(unittest.TestCase):
    def test_windows_developer_can_generate_explicit_ubuntu_target_paths(self):
        unit = systemd_user_unit('/opt/Meong Booth', '/opt/Meong Booth/.venv/bin/python', ['--print'])
        self.assertIn('WorkingDirectory=/opt/Meong Booth\n', unit)
        self.assertIn('ExecStart="/opt/Meong Booth/.venv/bin/python"', unit)
        self.assertIn('Restart=no', unit)
        self.assertIn('WantedBy=graphical-session.target', unit)
        self.assertIn('SendSIGKILL=no', unit)
        self.assertNotIn('MIDTRANS', unit)
        self.assertNotIn('sudo', unit)

    def test_systemd_paths_reject_injection_relative_windows_and_traversal(self):
        for root in ('relative', 'C:\\booth', '/tmp/../private', '/tmp/%h', '/tmp/$HOME', '/tmp/x\nExecStart=x'):
            with self.subTest(root=root), self.assertRaises(ValueError):
                systemd_user_unit(root, '/usr/bin/python3')
        with self.assertRaises(ValueError): systemd_user_unit('/opt/booth', '/usr/bin/python3', ['--manual-print'])
        with self.assertRaises(ValueError): systemd_user_unit('/opt/booth', '/usr/bin/python3', ['--key=secret'])

    def test_cli_generates_unit_without_site_packages_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'meong.service'
            command = [sys.executable, '-S', str(ROOT/'tools/run_portrait_v2_watchdog.py'),
                       '--write-startup', str(path), '--startup-format', 'systemd',
                       '--target-root', '/opt/Meong', '--target-python', '/opt/Meong/.venv/bin/python']
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(b'\r', path.read_bytes())
            before = path.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True, timeout=5).returncode, 0)
            self.assertEqual(path.read_bytes(), before)

    def test_cli_recovery_check_does_not_launch_any_child(self):
        launcher = module('run_portrait_v2_watchdog')
        with tempfile.TemporaryDirectory() as folder, patch.object(launcher, 'ROOT', Path(folder)), \
                patch.object(launcher.subprocess, 'Popen') as child, patch('builtins.print'):
            self.assertEqual(launcher.main(['--check-recovery']), 0)
            child.assert_not_called()
            self.assertEqual(list(Path(folder).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
