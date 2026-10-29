"""Nonpayable MOCK pre-order printer observations; synthetic transports only."""
from contextlib import closing
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from photobooth.device_health import HealthCheck, READY, WARNING, UNKNOWN, UNAVAILABLE
from photobooth.kiosk_v2 import mock_checkout


class MockPrinterPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {
            'PHOTOBOOTH_V2_PRINT': '1', 'PHOTOBOOTH_V2_DRIVE': '0',
            'PHOTOBOOTH_V2_CHECKOUT_SANDBOX': '0'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def configured(self):
        return mock_checkout.configured_mock_checkout(
            self.root / 'mock', configuration_root=self.root)

    def open(self, presentation, key='mock-printer-request-0001', attempt=None, cart=None):
        return presentation.open_checkout(cart or {'template_a': 1}, key, attempt)

    def rows(self, presentation, table='mock_orders'):
        with closing(presentation.store._connect()) as db:
            return [tuple(row) for row in db.execute('SELECT * FROM '+table+' ORDER BY rowid')]

    def settings(self, **values):
        path = self.root / 'data' / 'printer_settings.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'lan_host': '', 'wifi_host': '',
            'windows_printer_name': 'SYNTHETIC QUEUE A', **values}), encoding='utf-8')
        return path

    def test_opt_out_never_loads_config_probes_or_constructs_printer(self):
        with (patch.dict(os.environ, {'PHOTOBOOTH_V2_PRINT': '0'}),
              patch('photobooth.printer_settings.load_printer_config') as config,
              patch('photobooth.device_health.check_printer') as probe,
              patch('photobooth.printer.ThermalPrinter') as printer):
            view = self.open(self.configured())
        self.assertEqual(view['mode'], 'MOCK')
        self.assertTrue(view['qr_payload'].startswith('MEONG MOCK ONLY - NOT QRIS - '))
        config.assert_not_called(); probe.assert_not_called(); printer.assert_not_called()

    def test_degraded_unknown_and_exceptions_deny_before_order_qr_or_reward_reservation(self):
        presentation = self.configured()
        attempt = presentation.store.claim('DEMO-PRINTER-PREFLIGHT')['attempt_id']
        presentation.store.finish(attempt, 'won', 10)
        before = self.rows(presentation, 'attempts')
        for status in (WARNING, UNKNOWN, UNAVAILABLE, 'invalid'):
            with (self.subTest(status=status),
                  patch('photobooth.device_health.check_printer', return_value=
                        HealthCheck('printer', status, 'PRIVATE driver/address/path')),
                  patch.object(presentation, '_present') as present):
                with self.assertRaisesRegex(mock_checkout.MockCheckoutError, '^printer-not-ready$'):
                    self.open(presentation, attempt=attempt)
                present.assert_not_called()
            self.assertEqual(self.rows(presentation), [])
            self.assertEqual(self.rows(presentation, 'attempts'), before)
        for target in ('photobooth.device_health.check_printer',
                       'photobooth.printer_settings.load_printer_config'):
            with self.subTest(target=target), patch(target, side_effect=OSError('PRIVATE driver/path')):
                with self.assertRaisesRegex(mock_checkout.MockCheckoutError, '^printer-not-ready$'):
                    self.open(presentation, attempt=attempt)
            self.assertEqual(self.rows(presentation), [])
            self.assertEqual(self.rows(presentation, 'attempts'), before)

    def test_retry_reads_current_saved_config_and_creates_exactly_one_mock_order(self):
        settings = self.settings()
        before = settings.read_bytes()
        presentation = self.configured()
        with (patch('photobooth.device_health.check_printer', side_effect=[
                HealthCheck('printer', WARNING, 'fixture'),
                HealthCheck('printer', READY, 'route only')]) as probe,
              patch('photobooth.printer.ThermalPrinter') as printer):
            with self.assertRaises(mock_checkout.MockCheckoutError): self.open(presentation)
            self.assertEqual(self.rows(presentation), [])
            self.assertEqual(settings.read_bytes(), before)
            self.settings(windows_printer_name='SYNTHETIC QUEUE B')
            view = self.open(presentation)
            self.assertEqual([call.args[0].windows_printer_name for call in probe.call_args_list],
                             ['SYNTHETIC QUEUE A', 'SYNTHETIC QUEUE B'])
            self.assertEqual(self.open(presentation)['order_id'], view['order_id'])
            self.assertEqual(probe.call_count, 2)
            printer.assert_not_called()
        self.assertEqual(len(self.rows(presentation)), 1)
        self.assertEqual(view['state'], 'PENDING')
        self.assertIsNone(view['admission_id'])
        self.assertIn('qr_rgb', view)

    def test_original_lan_wifi_fallback_closes_without_print_bytes_before_order(self):
        self.settings(lan_host='192.0.2.11', wifi_host='192.0.2.12')
        presentation = self.configured()
        connection = SimpleNamespace(close=Mock(), send=Mock(), sendall=Mock())
        calls = []
        def dial(host, port, timeout):
            self.assertEqual(self.rows(presentation), [])
            calls.append((host, port, timeout))
            if host == '192.0.2.11': raise TimeoutError('synthetic unreachable')
            return connection
        with (patch('photobooth.device_health._network_dial', side_effect=dial),
              patch('photobooth.device_health._windows_queue_probe') as queue,
              patch('photobooth.printer.ThermalPrinter') as printer):
            view = self.open(presentation)
        self.assertEqual(calls, [('192.0.2.11', 9100, .75), ('192.0.2.12', 9100, .75)])
        connection.close.assert_called_once_with()
        connection.send.assert_not_called(); connection.sendall.assert_not_called()
        queue.assert_not_called(); printer.assert_not_called()
        self.assertEqual(len(self.rows(presentation)), 1)
        self.assertEqual(view['mode'], 'MOCK')

    def test_success_is_not_cached_for_a_later_new_order(self):
        presentation = self.configured()
        with patch('photobooth.device_health.check_printer', side_effect=[
                HealthCheck('printer', READY, 'route only'),
                HealthCheck('printer', UNKNOWN, 'now unknown')]) as probe:
            first = self.open(presentation)
            presentation.transition(first['order_id'], 'cancel')
            before = self.rows(presentation)
            with self.assertRaisesRegex(mock_checkout.MockCheckoutError, '^printer-not-ready$'):
                self.open(presentation, key='mock-printer-request-0002')
            self.assertEqual(probe.call_count, 2)
            self.assertEqual(self.rows(presentation), before)

    def test_existing_pending_unknown_confirmed_recover_without_new_health_or_identity(self):
        for state in ('PENDING', 'UNKNOWN', 'CONFIRMED'):
            with self.subTest(state=state), TemporaryDirectory() as temp:
                root = Path(temp)
                presentation = mock_checkout.configured_mock_checkout(root, configuration_root=self.root)
                first = presentation.store.create({'template_a': 1}, 'existing-printer-request')
                if state != 'PENDING':
                    presentation.store.transition(first['order_id'], 'unknown' if state == 'UNKNOWN' else 'confirm')
                before = self.rows(presentation)
                with (patch('photobooth.printer_settings.load_printer_config') as config,
                      patch('photobooth.device_health.check_printer') as probe):
                    reopened = mock_checkout.configured_mock_checkout(root, configuration_root=self.root)
                    view = self.open(reopened, cart={'template_b': 9})
                    self.assertEqual(view['order_id'], first['order_id'])
                    self.assertEqual(view['quantities'], {'template_a': 1})
                    self.assertEqual(view['state'], state)
                    self.assertIsNone(view['admission_id'])
                    with self.assertRaisesRegex(mock_checkout.MockCheckoutError, 'key-conflict'):
                        self.open(reopened, key=first['request_key'], cart={'template_b': 9})
                    config.assert_not_called(); probe.assert_not_called()
                self.assertEqual(self.rows(reopened), before)

    def test_conflicting_sandbox_print_opt_in_denies_before_any_printer_probe(self):
        with (patch.dict(os.environ, {'PHOTOBOOTH_V2_CHECKOUT_SANDBOX': '1'}),
              patch('photobooth.printer_settings.load_printer_config') as config,
              patch('photobooth.device_health.check_printer') as probe):
            presentation = self.configured()
            with self.assertRaisesRegex(mock_checkout.MockCheckoutError, '^printer-not-ready$'):
                self.open(presentation)
            self.assertEqual(self.rows(presentation), [])
            config.assert_not_called(); probe.assert_not_called()
