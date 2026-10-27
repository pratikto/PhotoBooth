"""Offline trial-tool tests. None of these contacts or pays Midtrans."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from tools.run_qris_sandbox import (current_simulator_qr, main, stop,
                                    trial_environments, wait_ready)

KEY = 'SB-Mid-server-TEST-ONLY-NOT-A-CREDENTIAL'


class SandboxLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def config(self, **overrides):
        args = dict(parent={}, merchant='MTEST', key=KEY, booth='PB001', port=8000, root=self.root)
        args.update(overrides)
        return trial_environments(**args)

    def test_midtrans_secrets_never_enter_gui_environment(self):
        backend, gui = self.config(parent={'MIDTRANS_SERVER_KEY': 'old', 'MIDTRANS_OTHER_SECRET': 'hidden'})
        self.assertEqual(backend['MIDTRANS_SERVER_KEY'], KEY)
        self.assertEqual(backend['MIDTRANS_MERCHANT_ID'], 'MTEST')
        self.assertFalse(any(k.startswith('MIDTRANS_') for k in gui))

    def test_same_generated_booth_token_without_logging(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            backend, gui = self.config()
        self.assertEqual(backend['MEONG_QRIS_BOOTH_TOKEN'], gui['MEONG_QRIS_BOOTH_TOKEN'])
        self.assertGreaterEqual(len(gui['MEONG_QRIS_BOOTH_TOKEN']), 32)
        self.assertEqual(output.getvalue(), '')

    def test_inherited_mock_and_production_settings_cannot_select_mode(self):
        _, gui = self.config(parent={'MEONG_QRIS_MODE': 'mock', 'MEONG_PAYMENT_MODE': 'production',
            'MEONG_QRIS_MOCK_DELAY': '0', 'MEONG_QRIS_API_URL': 'https://foreign.example'})
        self.assertEqual(gui['MEONG_QRIS_MODE'], 'sandbox')
        self.assertEqual(gui['MEONG_PAYMENT_MODE'], 'qris-sandbox')
        self.assertEqual(gui['MEONG_QRIS_API_URL'], 'http://127.0.0.1:8000')
        self.assertNotIn('MEONG_QRIS_MOCK_DELAY', gui)

    def test_parent_environment_is_not_mutated(self):
        parent = {'MIDTRANS_SERVER_KEY': 'old', 'PHOTOBOOTH_CAMERA_INDEX': '2'}
        original = dict(parent)
        self.config(parent=parent)
        self.assertEqual(parent, original)

    def test_camera_and_existing_operator_configuration_retained(self):
        _, gui = self.config(parent={'PHOTOBOOTH_CAMERA_INDEX': '2', 'PHOTOBOOTH_AUDIO': '0'})
        self.assertEqual(gui['PHOTOBOOTH_CAMERA_INDEX'], '2')
        self.assertEqual(gui['PHOTOBOOTH_AUDIO'], '0')

    def test_paths_are_persistent_and_separate_from_mock(self):
        _, first = self.config()
        _, second = self.config()
        self.assertEqual(first['MEONG_QRIS_DB_PATH'], second['MEONG_QRIS_DB_PATH'])
        self.assertEqual(Path(first['MEONG_QRIS_DB_PATH']).parent,
                         self.root / 'data/qris-sandbox-trial/MTEST/PB001')
        self.assertFalse(self.root.joinpath('data').exists())

    def test_dashboard_server_key_formats_preserve_sandbox_isolation(self):
        for prefix in ('SB-Mid-server-', 'Mid-server-'):
            key = prefix + 'TEST-ONLY-NOT-A-CREDENTIAL'
            parent = {'MEONG_QRIS_MODE': 'production',
                      'MEONG_QRIS_API_URL': 'https://api.midtrans.com',
                      'MIDTRANS_SERVER_KEY': 'inherited-secret'}
            original = dict(parent)
            with self.subTest(prefix=prefix):
                backend, gui = self.config(parent=parent, key=key)
                self.assertEqual(backend['MIDTRANS_SERVER_KEY'], key)
                self.assertFalse(any(name.startswith('MIDTRANS_') for name in gui))
                for env in (backend, gui):
                    self.assertEqual(env['MEONG_QRIS_MODE'], 'sandbox')
                    self.assertEqual(env['MEONG_PAYMENT_MODE'], 'qris-sandbox')
                    self.assertEqual(env['MEONG_QRIS_API_URL'], 'http://127.0.0.1:8000')
                self.assertEqual(parent, original)
                self.assertFalse(self.root.joinpath('data').exists())

    def test_client_empty_and_malformed_keys_are_rejected(self):
        for key in ('Mid-client-test', 'SB-Mid-client-test', '', 'SB-Mid-server-',
                    'Mid-server-', 'arbitrary-key', KEY + '\n', KEY + ' space',
                    KEY + '\x00', KEY + '\x7f', True, 'SB-Mid-server-' + '\u00e9',
                    'Mid-server-' + '\u00e9', 'Mid-server-' + 'x' * 512):
            with self.subTest(key_type=type(key).__name__), self.assertRaises(ValueError):
                self.config(key=key)

    def test_invalid_merchant_booth_and_ports_rejected(self):
        for values in ({'merchant': '../bad'}, {'merchant': ''}, {'booth': '../PB001'},
                       {'booth': 'PB1'}, {'port': True}, {'port': 80}, {'port': 65536}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.config(**values)

    def journal(self, **changes):
        data = {'version': 1, 'context': {'mode': 'sandbox', 'endpoint': 'http://127.0.0.1:8000',
                'booth_id': 'PB001'}, 'phase': 'WAITING',
                'order': {'mode': 'sandbox', 'state': 'PENDING', 'order_id': 'a' * 32,
                          'qr_url': 'https://api.sandbox.midtrans.com/v2/qris/tx-test/qr-code'}}
        data.update(changes)
        path = self.root / 'visit.json'
        path.write_text(json.dumps(data))
        return path, data

    def read(self, path, **kwargs):
        return current_simulator_qr(path, 'http://127.0.0.1:8000', 'PB001', **kwargs)

    def test_current_sandbox_qr_can_be_shown(self):
        path, data = self.journal()
        self.assertEqual(self.read(path), ('a' * 32, data['order']['qr_url']))

    def test_mock_paid_recovery_and_other_booth_qr_not_shown(self):
        for changes in ({'phase': 'RECOVERY'}, {'phase': 'STARTED'},
                        {'context': {'mode': 'mock'}}, {'context': {'booth_id': 'PB002'}},
                        {'order': {'state': 'PAID'}}, {'order': {'state': 'PENDING', 'mode': 'mock'}}):
            path, _ = self.journal(**changes)
            self.assertIsNone(self.read(path))

    def test_untrusted_and_malformed_qr_urls_not_shown(self):
        urls = ('https://foreign.example/qr', 'https://api.sandbox.midtrans.com.evil/v2/qris/t/qr-code',
                'https://user@api.sandbox.midtrans.com/v2/qris/t/qr-code',
                'http://api.sandbox.midtrans.com/v2/qris/t/qr-code',
                'https://api.sandbox.midtrans.com:8443/v2/qris/t/qr-code',
                'https://api.sandbox.midtrans.com/v2/qris/t/qr-code?secret=x',
                'https://api.sandbox.midtrans.com/v2/qris/t/qr-code#fragment',
                'https://api.sandbox.midtrans.com/v2/charge', None)
        for url in urls:
            path, data = self.journal()
            data['order']['qr_url'] = url
            path.write_text(json.dumps(data))
            self.assertIsNone(self.read(path))

    def test_oversized_or_malformed_journal_never_used(self):
        path = self.root / 'visit.json'
        for value in ('x' * 65537, '{', '[]'):
            path.write_text(value)
            self.assertIsNone(self.read(path))

    def test_journal_from_before_gui_launch_is_not_shown(self):
        path, _ = self.journal()
        self.assertIsNone(self.read(path, after_ns=path.stat().st_mtime_ns + 1))

    def test_verification_pending_is_not_presented_as_current(self):
        path, data = self.journal()
        data['order']['verification_pending'] = True
        path.write_text(json.dumps(data))
        self.assertIsNone(self.read(path))

    def test_missing_journal_is_ignored(self):
        self.assertIsNone(self.read(self.root / 'missing'))

    def test_stopped_backend_is_not_ready(self):
        server = Mock()
        server.poll.return_value = 1
        with self.assertRaises(RuntimeError):
            wait_ready(server, 'http://127.0.0.1:8000', seconds=.1)

    def test_stop_waits_and_does_not_touch_files(self):
        marker = self.root / 'orders.sqlite'
        marker.write_text('preserve payment state')
        process = Mock()
        process.poll.return_value = None
        stop(process)
        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=10)
        self.assertEqual(marker.read_text(), 'preserve payment state')

    def test_stop_kills_only_child_after_timeout(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired('test', 10), 0]
        stop(process)
        process.kill.assert_called_once()

    def test_launch_separates_environments_and_never_prints_key(self):
        for key in (KEY, KEY.removeprefix('SB-')):
            with self.subTest(prefix=key.split('TEST')[0]):
                self.check_launch(key)

    def check_launch(self, key):
        recorded = []
        server, gui = Mock(), Mock()
        server.poll.return_value = None
        gui.poll.return_value = 0
        gui.returncode = 0
        def spawn(command, **kwargs):
            recorded.append((command, dict(kwargs['env'])))
            return server if len(recorded) == 1 else gui
        output = io.StringIO()
        with patch.dict('os.environ', {'MIDTRANS_SERVER_KEY': key,
                                      'MIDTRANS_MERCHANT_ID': 'MTEST'}, clear=True), \
             patch('importlib.util.find_spec', return_value=object()), \
             patch('tools.run_qris_sandbox.socket.socket'), \
             patch('tools.run_qris_sandbox.wait_ready'), \
             patch('tools.run_qris_sandbox.subprocess.Popen', side_effect=spawn), \
             contextlib.redirect_stdout(output):
            self.assertEqual(main([]), 0)
        self.assertEqual(len(recorded), 2)
        self.assertIn('uvicorn', recorded[0][0])
        self.assertEqual(recorded[0][1]['MIDTRANS_SERVER_KEY'], key)
        self.assertNotIn('MIDTRANS_SERVER_KEY', recorded[1][1])
        self.assertNotIn(key, str(recorded[0][0]))
        self.assertNotIn(key, output.getvalue())
        server.terminate.assert_called_once()

    def test_help_has_no_process_or_credential_side_effects(self):
        with patch('tools.run_qris_sandbox.subprocess.Popen') as start, \
             patch('tools.run_qris_sandbox.getpass.getpass') as secret, \
             contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(['--help'])
        self.assertEqual(error.exception.code, 0)
        start.assert_not_called()
        secret.assert_not_called()


if __name__ == '__main__':
    unittest.main()
