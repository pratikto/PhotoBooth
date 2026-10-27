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


class DeliveryLoggingTests(unittest.TestCase):
    def test_timing_bypasses_root_and_file_handler_is_released(self):
        from photobooth.delivery_timing import LOG as delivery, event
        class RootBomb(logging.Handler):
            def emit(self,record):
                if record.name=='photobooth.delivery':raise AssertionError('timing leaked into root')
        bomb=RootBomb();root=logging.getLogger();root.addHandler(bomb)
        previous=list(delivery.handlers)
        try:
            with tempfile.TemporaryDirectory() as folder:
                with DiagnosticSession(folder) as session:
                    event('queued','PB001V2S2_00000008',queue_depth=1)
                    text=session.path.read_text()
                    self.assertIn('delivery_timing ',text);self.assertIn('monotonic_ms',text)
                    self.assertEqual(text.count('"stage": "queued"'),1)
                self.assertEqual(delivery.handlers,previous)
        finally:root.removeHandler(bomb)

    def test_broken_sink_and_recursive_callback_do_not_escape_or_hide_business_error(self):
        from photobooth.delivery_timing import LOG as delivery, event, span
        class Broken(logging.Handler):
            def emit(self,record):raise RecursionError('synthetic broken logging sink')
        class Reentrant(logging.Handler):
            calls=0
            def emit(self,record):
                self.calls+=1;event('nested','PB001V2S2_00000008')
        for handler in (Broken(),Reentrant()):
            delivery.addHandler(handler)
            try:
                event('queued','PB001V2S2_00000008')
                with span('request','PB001V2S2_00000008'):pass
                with self.assertRaisesRegex(ValueError,'real business failure'):
                    with span('request','PB001V2S2_00000008'):raise ValueError('real business failure')
                if isinstance(handler,Reentrant):self.assertEqual(handler.calls,3)
            finally:delivery.removeHandler(handler)

    @unittest.skipUnless(importlib.util.find_spec('kivy'), 'Real Kivy logging integration needs Kivy')
    def test_real_launcher_console_active_keeps_stderr_and_records_native_and_delivery_once(self):
        import json
        import os
        import sys
        import textwrap
        root=Path(__file__).resolve().parents[1]
        code=textwrap.dedent('''
            import json,logging,runpy,sys,tempfile
            from pathlib import Path
            from types import SimpleNamespace
            initial_stderr=sys.stderr
            launcher=runpy.run_path('tools/run_portrait_v2.py',run_name='logging_fixture')
            from photobooth.delivery_timing import event
            class App:
                def run(self):
                    import kivy.logger as native
                    assert native.KIVY_LOG_MODE=='MIXED'
                    assert sys.stderr is initial_stderr
                    late=logging.StreamHandler(sys.stderr)
                    logging.getLogger().addHandler(late)
                    try:
                        logging.getLogger('fixture').warning('ordinary console path')
                        native.Logger.warning('fixture native path')
                        event('queued','PB001V2S2_00000008',queue_depth=1)
                    finally:logging.getLogger().removeHandler(late)
            sys.modules['photobooth.kiosk_v2.app']=SimpleNamespace(PortraitKioskV2App=App)
            with tempfile.TemporaryDirectory() as folder:
                # run_path functions retain this dictionary as their globals.
                launcher['run_app'].__globals__['PROJECT_ROOT']=Path(folder)
                launcher['run_app']()
                paths=list((Path(folder)/'data/diagnostics').glob('portrait-v2-*.log'))
                assert len(paths)==1
                data=paths[0].read_text()
                assert data.count('"stage": "queued"')==1
                assert 'fixture native path' in data
                assert 'ordinary console path' in data
                assert 'Session end' in data
            print('CONSOLE_LOGGING_PASS')
        ''')
        with tempfile.TemporaryDirectory() as folder:
            env=dict(os.environ,KIVY_HOME=folder,KIVY_NO_ARGS='1',KIVY_NO_FILELOG='1')
            env.pop('KIVY_NO_CONSOLELOG',None);env.pop('KIVY_LOG_MODE',None)
            result=subprocess.run([sys.executable,'-c',code],cwd=root,env=env,
                                  capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr[-5000:])
        self.assertIn('CONSOLE_LOGGING_PASS',result.stdout)
        self.assertIn('fixture native path',result.stderr)
        self.assertNotIn('RecursionError',result.stderr)


if __name__ == '__main__':
    unittest.main()
