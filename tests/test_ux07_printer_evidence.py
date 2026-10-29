"""Read-only route evidence must never become paper or payment acceptance."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from photobooth.device_health import HealthCheck, READY, UNKNOWN, WARNING, check_printer
from photobooth.kiosk_v2.readiness import BRANCH, inventory
from tools import check_portrait_v2


class PrinterRouteEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env_patch = patch.dict(os.environ, {
            'PHOTOBOOTH_PRINTER_LAN_HOST': '', 'PHOTOBOOTH_PRINTER_WIFI_HOST': '',
            'PHOTOBOOTH_PRINTER_WINDOWS_NAME': '',
            'PHOTOBOOTH_PRINTER_USB_VENDOR_ID': '', 'PHOTOBOOTH_PRINTER_USB_PRODUCT_ID': ''})
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def metadata(self):
        def git(root, *args):
            return {'branch': BRANCH, 'rev-parse': 'a' * 40, 'status': ''}[args[0]]
        return patch('photobooth.kiosk_v2.readiness.git_value', side_effect=git)

    def report(self, *, requested=True, env=None):
        with self.metadata(), patch('photobooth.kiosk_v2.readiness.importlib.metadata.version', return_value='1.0'):
            return inventory(self.root, env={} if env is None else env, display={}, probe_printer=requested)

    def settings(self, **values):
        path = self.root / 'data' / 'printer_settings.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'lan_host': '', 'wifi_host': '',
                                   'windows_printer_name': 'PRIVATE QUEUE A', **values}))
        return path

    def test_default_never_reads_settings_or_probes_despite_print_opt_in(self):
        with (patch('photobooth.printer_settings.load_printer_config') as settings,
              patch('photobooth.device_health.check_printer') as probe):
            report = self.report(requested=False, env={'PHOTOBOOTH_V2_PRINT': '1'})
            settings.assert_not_called(); probe.assert_not_called()
        self.assertEqual(report['printer_route']['status'], 'not_run')
        self.assertEqual(report['preflight']['status'], 'READY_FOR_MANUAL_TEST')
        self.assertEqual(set(report['acceptance'].values()), {'NOT_RUN'})

    def test_sandbox_refuses_explicit_probe_before_configuration_access(self):
        with (patch('photobooth.printer_settings.load_printer_config') as settings,
              patch('photobooth.device_health.check_printer') as probe):
            report = self.report(env={'PHOTOBOOTH_V2_CHECKOUT_SANDBOX': '1',
                                      'MEONG_QRIS_MODE': 'sandbox'})
            settings.assert_not_called(); probe.assert_not_called()
        self.assertEqual(report['printer_route']['status'], 'denied_sandbox')
        self.assertEqual(report['preflight']['status'], 'NEEDS_ATTENTION')
        self.assertEqual(set(report['acceptance'].values()), {'NOT_RUN'})

    def test_original_windows_queue_probe_reloads_settings_without_printing_or_certifying_paper(self):
        path = self.settings()
        with (patch('photobooth.device_health.sys', SimpleNamespace(platform='win32')),
              patch('photobooth.device_health._windows_queue_probe', side_effect=[True, False]) as queue,
              patch('photobooth.device_health.check_printer', wraps=check_printer) as probe,
              patch('photobooth.printer.ThermalPrinter') as printer):
            first = self.report()
            self.settings(windows_printer_name='PRIVATE QUEUE B')
            before = path.read_bytes()
            second = self.report()
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual([call.args[0] for call in queue.call_args_list],
                             ['PRIVATE QUEUE A', 'PRIVATE QUEUE B'])
            self.assertEqual(probe.call_count, 2)
            printer.assert_not_called()
        self.assertEqual(first['printer_route']['status'], READY)
        self.assertEqual(first['preflight']['status'], 'READY_FOR_MANUAL_TEST')
        self.assertEqual(second['printer_route']['status'], WARNING)
        self.assertEqual(second['preflight']['status'], 'NEEDS_ATTENTION')
        for report in (first, second):
            self.assertNotIn('PRIVATE', json.dumps(report))
            self.assertEqual(report['acceptance']['purchased_print_payment_preflight'], 'NOT_RUN')
            self.assertEqual(report['acceptance']['physical_print_output'], 'NOT_RUN')

    def test_status_and_exception_details_are_allowlisted_and_redacted(self):
        for value in (WARNING, UNKNOWN, 'unavailable', 'PRIVATE INVALID STATUS'):
            with (self.subTest(value=value),
                  patch('photobooth.device_health.check_printer', return_value=
                        HealthCheck('printer', value, 'PRIVATE driver/host/path/token'))):
                report = self.report()
                self.assertEqual(report['printer_route']['status'], value if value != 'PRIVATE INVALID STATUS' else UNKNOWN)
                self.assertEqual(report['preflight']['status'], 'NEEDS_ATTENTION')
                self.assertNotIn('PRIVATE', json.dumps(report))
        for target in ('photobooth.printer_settings.load_printer_config',
                       'photobooth.device_health.check_printer'):
            with self.subTest(target=target), patch(target, side_effect=OSError('PRIVATE driver/host/path/token')):
                report = self.report()
                self.assertEqual(report['printer_route']['status'], UNKNOWN)
                self.assertNotIn('PRIVATE', json.dumps(report))
                self.assertEqual(set(report['acceptance'].values()), {'NOT_RUN'})

    def test_original_tcp_observation_closes_without_sending_or_mutating_records(self):
        self.settings(lan_host='192.0.2.51')
        for name in ('orders.sqlite', 'counter.json', 'photos/customer.jpg', 'visit.json'):
            p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b'synthetic unchanged financial/media marker')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        connection = SimpleNamespace(close=Mock(), send=Mock(), sendall=Mock())
        with (patch('photobooth.device_health._network_dial', return_value=connection) as dial,
              patch('photobooth.printer.ThermalPrinter') as printer):
            report = self.report()
            dial.assert_called_once_with('192.0.2.51', 9100, .75)
            connection.close.assert_called_once_with()
            connection.send.assert_not_called(); connection.sendall.assert_not_called()
            printer.assert_not_called()
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertEqual(report['printer_route']['status'], READY)
        self.assertNotIn('192.0.2.51', json.dumps(report))
        self.assertEqual(set(report['acceptance'].values()), {'NOT_RUN'})

    def test_cli_persists_sanitized_failed_probe_and_returns_attention(self):
        destination = self.root / 'diagnostics' / 'route.json'
        with (self.metadata(), patch('photobooth.kiosk_v2.readiness.importlib.metadata.version', return_value='1.0'),
              patch('tools.check_portrait_v2.ROOT', self.root),
              patch.dict(os.environ, {'PHOTOBOOTH_V2_CHECKOUT_SANDBOX': '0',
                                     'MIDTRANS_SERVER_KEY': '', 'MIDTRANS_MERCHANT_ID': ''}),
              patch('photobooth.device_health.check_printer', side_effect=OSError('PRIVATE HOST ERROR')),
              redirect_stdout(io.StringIO()) as output):
            result = check_portrait_v2.main(['--probe-printer', '--output', str(destination)])
        self.assertEqual(result, 1)
        report = json.loads(destination.read_text())
        self.assertEqual(report['printer_route']['status'], UNKNOWN)
        self.assertNotIn('PRIVATE HOST ERROR', destination.read_text() + output.getvalue())
        self.assertEqual(set(report['acceptance'].values()), {'NOT_RUN'})

    def test_default_cli_runs_without_site_packages_and_preserves_not_run(self):
        tool = Path(__file__).resolve().parents[1] / 'tools' / 'check_portrait_v2.py'
        output = self.root / 'default.json'
        result = subprocess.run([sys.executable, '-S', str(tool), '--output', str(output)],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1, result.stderr)  # Missing optional dependencies require attention.
        report = json.loads(output.read_text())
        self.assertEqual(report['printer_route']['status'], 'not_run')
        self.assertEqual(set(report['acceptance'].values()), {'NOT_RUN'})
