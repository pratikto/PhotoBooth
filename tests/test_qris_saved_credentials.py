"""Offline saved-Sandbox settings tests; never read the owner's private file."""
import contextlib
import io
import os
from pathlib import Path
import tempfile
import traceback
import unittest
from unittest.mock import Mock, patch

from tools.run_qris_sandbox import LocalSandboxSettingsError, local_sandbox_credentials
from tools.run_qris_sandbox import main as shared_main
from tools.run_portrait_v2_sandbox import main as portrait_main

KEY = 'Mid-server-TEST-ONLY-NOT-A-CREDENTIAL'
ENV_KEY = 'SB-Mid-server-ENV-TEST-ONLY-NOT-A-CREDENTIAL'


class SavedSandboxCredentialsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'photobooth' / 'local_settings.py'

    def write(self, source, *, encoding='utf-8'):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(source, encoding=encoding)

    def save(self, merchant='MFILE', key=KEY):
        self.write(f'MIDTRANS_SANDBOX_MERCHANT_ID = {merchant!r}\n'
                   f'MIDTRANS_SANDBOX_SERVER_KEY = {key!r}\n')

    def launch(self, parent=None, *, entry=portrait_main):
        recorded = []
        server, gui = Mock(), Mock()
        server.poll.return_value = None
        gui.poll.return_value = 0
        gui.returncode = 0

        def spawn(command, **kwargs):
            recorded.append((command, dict(kwargs['env'])))
            return server if len(recorded) == 1 else gui

        output = io.StringIO()
        original = self.path.read_bytes() if self.path.exists() else None
        with patch.dict(os.environ, parent or {}, clear=True), \
             patch('tools.run_qris_sandbox.ROOT', self.root), \
             patch('importlib.util.find_spec', return_value=object()), \
             patch('tools.run_qris_sandbox.socket.socket'), \
             patch('tools.run_qris_sandbox.wait_ready'), \
             patch('tools.run_qris_sandbox.subprocess.Popen', side_effect=spawn), \
             patch('builtins.input', return_value='MPROMPT') as merchant_prompt, \
             patch('tools.run_qris_sandbox.getpass.getpass', return_value=ENV_KEY) as key_prompt, \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = entry([])
            self.assertEqual(dict(os.environ), parent or {})
        if original is not None:
            self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse((self.root / 'data').exists())
        for secret in (KEY, ENV_KEY):
            self.assertNotIn(secret, output.getvalue())
            self.assertNotIn(secret, str([command for command, _ in recorded]))
        if recorded:
            self.assertFalse(any(name.startswith('MIDTRANS_') for name in recorded[1][1]))
        return result, recorded, merchant_prompt, key_prompt, output.getvalue()

    def test_missing_file_keeps_interactive_fallback_and_is_not_created(self):
        self.assertEqual(local_sandbox_credentials(self.path), ('', ''))
        result, recorded, merchant, key, _ = self.launch()
        self.assertEqual(result, 0)
        merchant.assert_called_once()
        key.assert_called_once()
        self.assertEqual(recorded[0][1]['MIDTRANS_MERCHANT_ID'], 'MPROMPT')
        self.assertEqual(recorded[0][1]['MIDTRANS_SERVER_KEY'], ENV_KEY)
        self.assertFalse(self.path.exists())

    def test_only_sandbox_literals_are_read_without_executing_drive_settings(self):
        marker = self.root / 'must-not-exist'
        self.write("from pathlib import Path\n"
                   f"Path({str(marker)!r}).write_text('executed')\n"
                   "WEB_APP_URL = unknown_drive_expression()\n"
                   "UPLOAD_TOKEN = 'DUMMY-DRIVE-TOKEN'\n"
                   f"MIDTRANS_SANDBOX_MERCHANT_ID = 'MFILE'\n"
                   f"MIDTRANS_SANDBOX_SERVER_KEY = {KEY!r}\n")
        before = self.path.read_bytes()
        self.assertEqual(local_sandbox_credentials(self.path), ('MFILE', KEY))
        self.assertFalse(marker.exists())
        self.assertEqual(self.path.read_bytes(), before)

    def test_utf8_bom_and_annotated_string_assignments_work(self):
        self.write("MIDTRANS_SANDBOX_MERCHANT_ID: str = 'MFILE'\n"
                   f"MIDTRANS_SANDBOX_SERVER_KEY: str = {KEY!r}\n",
                   encoding='utf-8-sig')
        self.assertEqual(local_sandbox_credentials(self.path), ('MFILE', KEY))

    def test_generic_midtrans_names_are_not_adopted_from_file(self):
        self.write("MIDTRANS_MERCHANT_ID = 'MGENERIC'\n"
                   f"MIDTRANS_SERVER_KEY = {KEY!r}\n")
        self.assertEqual(local_sandbox_credentials(self.path), ('', ''))

    def test_empty_and_partial_defaults_keep_missing_values_empty(self):
        for merchant, key in (('', ''), ('MFILE', ''), ('', KEY)):
            with self.subTest(has_merchant=bool(merchant), has_key=bool(key)):
                self.save(merchant, key)
                self.assertEqual(local_sandbox_credentials(self.path), (merchant, key))

    def test_computed_or_non_text_values_are_rejected_without_execution(self):
        for expression in ("str('MFILE')", "123", "None", "['MFILE']", "f'MFILE'"):
            with self.subTest(expression_type=expression.split('(')[0]):
                self.write(f"MIDTRANS_SANDBOX_MERCHANT_ID = {expression}\n")
                with self.assertRaises(LocalSandboxSettingsError):
                    local_sandbox_credentials(self.path)

    def test_syntax_error_traceback_cannot_echo_secret_source(self):
        self.write(f'MIDTRANS_SANDBOX_SERVER_KEY = "{KEY}\n')
        try:
            local_sandbox_credentials(self.path)
        except LocalSandboxSettingsError as error:
            formatted = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            self.assertNotIn(KEY, formatted)
            self.assertNotIn('SyntaxError', formatted)
        else:
            self.fail('Malformed saved settings must stop before prompting or spawning')

    def test_unreadable_and_non_utf8_settings_fail_with_sanitized_error(self):
        with patch.object(Path, 'read_text', side_effect=OSError('PRIVATE-DETAIL')):
            with self.assertRaises(LocalSandboxSettingsError) as caught:
                local_sandbox_credentials(self.path)
            self.assertNotIn('PRIVATE-DETAIL', str(caught.exception))
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b'\xff\xfeinvalid')
        with self.assertRaises(LocalSandboxSettingsError):
            local_sandbox_credentials(self.path)

    def test_shared_and_v2_launchers_use_saved_pair_without_prompts(self):
        for entry in (shared_main, portrait_main):
            with self.subTest(entry=entry.__module__):
                self.save()
                result, recorded, merchant, key, _ = self.launch(entry=entry)
                self.assertEqual(result, 0)
                merchant.assert_not_called()
                key.assert_not_called()
                self.assertEqual(recorded[0][1]['MIDTRANS_MERCHANT_ID'], 'MFILE')
                self.assertEqual(recorded[0][1]['MIDTRANS_SERVER_KEY'], KEY)
                for _, env in recorded:
                    self.assertEqual(env['MEONG_QRIS_MODE'], 'sandbox')
                if entry is portrait_main:
                    self.assertIn('tools/run_portrait_v2.py', recorded[1][0])
                    for _, env in recorded:
                        self.assertEqual(env['PHOTOBOOTH_V2_PRINT'], '0')
                        self.assertEqual(env['PHOTOBOOTH_V2_DRIVE'], '0')

    def test_complete_environment_pair_overrides_file_without_reading_it(self):
        self.save()
        parent = {'MIDTRANS_MERCHANT_ID': 'MENV', 'MIDTRANS_SERVER_KEY': ENV_KEY}
        with patch('tools.run_qris_sandbox.local_sandbox_credentials') as read:
            result, recorded, merchant, key, _ = self.launch(parent)
        read.assert_not_called()
        self.assertEqual(result, 0)
        self.assertEqual(recorded[0][1]['MIDTRANS_MERCHANT_ID'], 'MENV')
        self.assertEqual(recorded[0][1]['MIDTRANS_SERVER_KEY'], ENV_KEY)
        merchant.assert_not_called()
        key.assert_not_called()

    def test_partial_environment_does_not_silently_mix_with_saved_account(self):
        self.save()
        for parent in ({'MIDTRANS_MERCHANT_ID': 'MENV'}, {'MIDTRANS_SERVER_KEY': ENV_KEY}):
            with self.subTest(environment_field=next(iter(parent))):
                with patch('tools.run_qris_sandbox.local_sandbox_credentials') as read:
                    result, recorded, merchant, key, _ = self.launch(parent)
                read.assert_not_called()
                self.assertEqual(result, 0)
                if 'MIDTRANS_MERCHANT_ID' in parent:
                    merchant.assert_not_called()
                    key.assert_called_once()
                    self.assertEqual(recorded[0][1]['MIDTRANS_MERCHANT_ID'], 'MENV')
                else:
                    merchant.assert_called_once()
                    key.assert_not_called()
                    self.assertEqual(recorded[0][1]['MIDTRANS_MERCHANT_ID'], 'MPROMPT')
                self.assertEqual(recorded[0][1]['MIDTRANS_SERVER_KEY'], ENV_KEY)

    def test_partial_saved_pair_prompts_only_for_missing_field(self):
        for merchant_value, key_value in (('MFILE', ''), ('', KEY)):
            with self.subTest(missing='key' if merchant_value else 'merchant'):
                self.save(merchant_value, key_value)
                result, recorded, merchant, key, _ = self.launch()
                self.assertEqual(result, 0)
                if merchant_value:
                    merchant.assert_not_called()
                    key.assert_called_once()
                    self.assertEqual(recorded[0][1]['MIDTRANS_MERCHANT_ID'], 'MFILE')
                    self.assertEqual(recorded[0][1]['MIDTRANS_SERVER_KEY'], ENV_KEY)
                else:
                    merchant.assert_called_once()
                    key.assert_not_called()
                    self.assertEqual(recorded[0][1]['MIDTRANS_MERCHANT_ID'], 'MPROMPT')
                    self.assertEqual(recorded[0][1]['MIDTRANS_SERVER_KEY'], KEY)

    def test_invalid_saved_settings_stop_before_prompts_or_child_start(self):
        self.write(f'MIDTRANS_SANDBOX_SERVER_KEY = "{KEY}\n')
        result, recorded, merchant, key, output = self.launch()
        self.assertEqual(result, 2)
        self.assertEqual(recorded, [])
        merchant.assert_not_called()
        key.assert_not_called()
        self.assertIn('photobooth/local_settings.py', output)
        self.assertNotIn('Traceback', output)

    def test_help_never_reads_private_settings_or_starts_children(self):
        with patch('tools.run_qris_sandbox.local_sandbox_credentials') as read, \
             patch('tools.run_qris_sandbox.subprocess.Popen') as spawn, \
             patch('tools.run_qris_sandbox.getpass.getpass') as secret, \
             contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
            portrait_main(['--help'])
        self.assertEqual(result.exception.code, 0)
        read.assert_not_called()
        spawn.assert_not_called()
        secret.assert_not_called()

    def test_published_example_has_blank_defaults_and_target_remains_ignored(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(local_sandbox_credentials(root / 'photobooth/local_settings.example.py'),
                         ('', ''))
        self.assertIn('photobooth/local_settings.py', (root / '.gitignore').read_text().splitlines())


if __name__ == '__main__':
    unittest.main()
