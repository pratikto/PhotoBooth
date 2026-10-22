"""Persistent failure evidence, independent of Kivy and physical devices."""

import faulthandler
import importlib.util
import logging
from pathlib import Path
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from photobooth.kiosk_v2.diagnostics import DiagnosticSession, source_head


class DiagnosticSessionTests(unittest.TestCase):
    def test_exception_is_flushed_to_file_and_not_swallowed(self):
        root_logger = logging.getLogger()
        previous_handlers = list(root_logger.handlers)
        previous_hook = threading.excepthook
        with tempfile.TemporaryDirectory() as folder, \
                patch('photobooth.kiosk_v2.diagnostics.source_head', return_value='tested123'):
            with self.assertRaisesRegex(ValueError, 'return-to-advert failure'):
                with DiagnosticSession(folder) as session:
                    logging.getLogger('photobooth.kiosk_v2.app').info('Return to advertising requested')
                    raise ValueError('return-to-advert failure')
            text = session.path.read_text(encoding='utf-8')
            self.assertIn('HEAD=tested123', text)
            self.assertIn('Return to advertising requested', text)
            self.assertIn('Traceback (most recent call last)', text)
            self.assertIn('ValueError: return-to-advert failure', text)
            self.assertIn('Session end', text)
            session.close()  # Idempotent cleanup.
            self.assertTrue(session.stream.closed)
        self.assertEqual(root_logger.handlers, previous_handlers)
        self.assertIs(threading.excepthook, previous_hook)

    def test_native_fatal_destination_stays_open_through_session_then_releases_ownership(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch('photobooth.kiosk_v2.diagnostics.source_head', return_value='test'), \
                patch('photobooth.kiosk_v2.diagnostics.faulthandler.is_enabled', return_value=False), \
                patch('photobooth.kiosk_v2.diagnostics.faulthandler.enable') as enable, \
                patch('photobooth.kiosk_v2.diagnostics.faulthandler.disable') as disable:
            with DiagnosticSession(folder) as session:
                enable.assert_called_once_with(file=session.stream, all_threads=True)
                self.assertFalse(session.stream.closed)
                # Exercise a real Python stack dump into the same live file.
                faulthandler.dump_traceback(file=session.stream, all_threads=False)
                self.assertIn('test_native_fatal_destination', session.path.read_text())
                disable.assert_not_called()
            disable.assert_called_once_with()
            self.assertTrue(session.stream.closed)

    def test_existing_explicit_fatal_handler_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch('photobooth.kiosk_v2.diagnostics.source_head', return_value='test'), \
                patch('photobooth.kiosk_v2.diagnostics.faulthandler.is_enabled', return_value=True), \
                patch('photobooth.kiosk_v2.diagnostics.faulthandler.enable') as enable, \
                patch('photobooth.kiosk_v2.diagnostics.faulthandler.disable') as disable:
            with DiagnosticSession(folder):
                enable.assert_not_called()
            disable.assert_not_called()

    def test_worker_exception_records_context_and_delegates_to_previous_hook(self):
        previous = Mock()
        with tempfile.TemporaryDirectory() as folder, \
                patch('threading.excepthook', previous), \
                patch('photobooth.kiosk_v2.diagnostics.source_head', return_value='test'):
            with DiagnosticSession(folder) as session:
                args = SimpleNamespace(exc_type=RuntimeError, exc_value=RuntimeError('decoder worker failed'),
                                       exc_traceback=None, thread=SimpleNamespace(name='decoder-worker'))
                threading.excepthook(args)
                previous.assert_called_once_with(args)
                text = session.path.read_text()
                self.assertIn('thread=decoder-worker', text)
                self.assertIn('RuntimeError: decoder worker failed', text)
            self.assertIs(threading.excepthook, previous)

    def test_source_head_is_local_bounded_and_tolerates_missing_git(self):
        fixture = Path('/fixture')
        with patch('photobooth.kiosk_v2.diagnostics.subprocess.run',
                   return_value=SimpleNamespace(stdout='abcdef123456\n')) as read:
            self.assertEqual(source_head(fixture), 'abcdef123456')
            self.assertEqual(read.call_args.args[0],
                             ['git', '-C', str(fixture), 'rev-parse', '--short=12', 'HEAD'])
            self.assertEqual(read.call_args.kwargs['timeout'], 2)
        for error in (FileNotFoundError('git'), subprocess.TimeoutExpired('git', 2),
                      subprocess.CalledProcessError(128, 'git')):
            with self.subTest(error=type(error).__name__), \
                    patch('photobooth.kiosk_v2.diagnostics.subprocess.run', side_effect=error):
                self.assertEqual(source_head(fixture), 'unknown')

    @staticmethod
    def _launcher():
        path = Path(__file__).resolve().parents[1] / 'tools' / 'run_portrait_v2.py'
        spec = importlib.util.spec_from_file_location('portrait_launcher_test', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_launcher_runs_with_configured_window_and_a_persistent_log(self):
        launcher = self._launcher()
        config, app = Mock(), Mock()
        modules = {'kivy.config': SimpleNamespace(Config=config),
                   'photobooth.kiosk_v2.app': SimpleNamespace(PortraitKioskV2App=app)}
        with tempfile.TemporaryDirectory() as folder, patch.dict('sys.modules', modules), \
                patch('builtins.print'), patch.object(launcher, 'PROJECT_ROOT', Path(folder)), \
                patch('photobooth.kiosk_v2.diagnostics.source_head', return_value='test-head'):
            launcher.main()
            self.assertEqual(config.set.call_args_list[0].args, ('graphics', 'width', '800'))
            self.assertEqual(config.set.call_args_list[1].args, ('graphics', 'height', '1280'))
            app.return_value.run.assert_called_once_with()
            paths = list((Path(folder) / 'data' / 'diagnostics').glob('portrait-v2-*.log'))
            self.assertEqual(len(paths), 1)
            self.assertIn('Window startup', paths[0].read_text())

    def test_launcher_still_runs_if_diagnostic_directory_cannot_be_created(self):
        launcher = self._launcher()
        app = Mock()
        modules = {'kivy.config': SimpleNamespace(Config=Mock()),
                   'photobooth.kiosk_v2.app': SimpleNamespace(PortraitKioskV2App=app)}
        with patch.dict('sys.modules', modules), patch('builtins.print') as output, \
                patch('photobooth.kiosk_v2.diagnostics.DiagnosticSession',
                      side_effect=OSError('directory read-only')):
            launcher.main()
            app.return_value.run.assert_called_once_with()
            self.assertIn('diagnostic file unavailable', output.call_args_list[0].args[0])


if __name__ == '__main__':
    unittest.main()
