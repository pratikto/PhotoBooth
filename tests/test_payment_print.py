"""Payment expiry/race guards and actual QR pixels sent to an ESC/POS socket."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

from photobooth.payment import DemoPaymentGateway, PaymentCoordinator
from photobooth.qris_print import QrisPrinterWorker, escpos_raster, render_payment_slip


class PaymentAndPrintTests(unittest.TestCase):
    def test_printing_does_not_renew_and_expiry_renewal_keeps_amount_but_changes_attempt(self):
        now = datetime.now(timezone.utc)
        gateway = DemoPaymentGateway(validity=90, now=lambda: now)
        flow = PaymentCoordinator(gateway)
        first = flow.begin(10000)
        before = first.snapshot()
        render_payment_slip(first)
        self.assertEqual(first, before)
        with self.assertRaises(RuntimeError):
            flow.renew()
        now += timedelta(seconds=91)
        self.assertEqual(flow.check(), 'expired')
        second = flow.renew()
        self.assertNotEqual(first.attempt_id, second.attempt_id)
        self.assertNotEqual(first.payload, second.payload)
        self.assertEqual(second.amount, 10000)
        self.assertEqual(first.state, 'expired')

    def test_a_connection_timeout_or_payment_during_cancel_cannot_create_another_qr(self):
        class Gateway(DemoPaymentGateway):
            mode = 'normal'
            def status(self, attempt):
                if self.mode == 'timeout':
                    raise TimeoutError('No provider response')
                return super().status(attempt)
            def cancel(self, attempt):
                attempt.state = 'paid'  # Payment arrived immediately before cancellation.
                return 'paid'
        gateway = Gateway()
        flow = PaymentCoordinator(gateway)
        first = flow.begin(5000)
        gateway.mode = 'timeout'
        self.assertEqual(flow.check(), 'unknown')
        self.assertFalse(flow.release())
        with self.assertRaises(RuntimeError):
            flow.begin(5000)
        self.assertIs(flow.current, first)
        gateway.mode = 'normal'
        self.assertFalse(flow.release())
        self.assertEqual(flow.check(), 'paid')
        with self.assertRaises(RuntimeError):
            flow.renew()

    def test_actual_native_dot_slip_and_raster_decode_to_the_exact_payment_payload(self):
        attempt = DemoPaymentGateway().create(15000)
        for width in (384, 576):
            with self.subTest(width=width):
                slip = render_payment_slip(attempt, width)
                decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(np.asarray(slip.convert('RGB')))
                self.assertEqual(decoded, attempt.payload)
                wire = escpos_raster(slip)
                width_bytes = int.from_bytes(wire[6:8], 'little')
                height = int.from_bytes(wire[8:10], 'little')
                data = bytes(x ^ 255 for x in wire[10:10 + width_bytes * height])
                reconstructed = Image.frombytes('1', (width_bytes * 8, height), data)
                self.assertEqual(reconstructed.tobytes(), slip.tobytes())
                self.assertEqual(set(reconstructed.getdata()), {0, 255})

    def await_result(self, worker):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            result = worker.poll()
            if result is not None:
                return result
            time.sleep(.01)
        self.fail('Printer worker did not finish')

    def test_unconfigured_printer_reports_preview_and_does_not_claim_paper_was_printed(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = QrisPrinterWorker(directory, host='')
            self.addCleanup(worker.close)
            attempt = DemoPaymentGateway().create(5000)
            self.assertTrue(worker.submit(attempt))
            result = self.await_result(worker)
            self.assertEqual(result.status, 'preview')
            self.assertTrue(result.preview.is_file())
            self.assertEqual(attempt.state, 'pending')

    def test_lan_send_is_explicit_and_cancelled_jobs_cannot_send(self):
        with tempfile.TemporaryDirectory() as directory, patch('photobooth.qris_print.socket.create_connection') as connect:
            worker = QrisPrinterWorker(directory, host='192.0.2.10')
            self.addCleanup(worker.close)
            attempt = DemoPaymentGateway().create(5000)
            self.assertTrue(worker.submit(attempt))
            result = self.await_result(worker)
            self.assertEqual(result.status, 'sent')
            printer = connect.return_value.__enter__.return_value
            wire = printer.sendall.call_args.args[0]
            self.assertEqual(wire, result.preview.with_suffix('.bin').read_bytes())
            connect.assert_called_once_with(('192.0.2.10', 9100), timeout=4)
            worker.cancel(attempt.attempt_id)
            self.assertTrue(worker.submit(attempt))
            result = self.await_result(worker)
            self.assertEqual(result.status, 'error')
            self.assertEqual(connect.call_count, 1)

    def test_partial_tcp_failure_is_uncertain_and_never_retried_automatically(self):
        with tempfile.TemporaryDirectory() as directory, patch('photobooth.qris_print.socket.create_connection') as connect:
            connect.return_value.__enter__.return_value.sendall.side_effect = TimeoutError('partial send')
            worker = QrisPrinterWorker(directory, host='192.0.2.10')
            self.addCleanup(worker.close)
            self.assertTrue(worker.submit(DemoPaymentGateway().create(5000)))
            self.assertEqual(self.await_result(worker).status, 'unknown')
            self.assertEqual(connect.call_count, 1)

    def test_invalid_printer_settings_report_an_error_without_breaking_payment(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = QrisPrinterWorker(directory, host='', port='typo')
            self.addCleanup(worker.close)
            attempt = DemoPaymentGateway().create(5000)
            self.assertTrue(worker.submit(attempt))
            result = self.await_result(worker)
            self.assertEqual(result.status, 'error')
            self.assertIsNone(result.preview)
            self.assertEqual(attempt.state, 'pending')

    def test_a_fast_completed_print_stays_locked_until_the_ui_receives_its_result(self):
        with tempfile.TemporaryDirectory() as directory:
            worker = QrisPrinterWorker(directory, host='')
            self.addCleanup(worker.close)
            attempt = DemoPaymentGateway().create(5000)
            self.assertTrue(worker.submit(attempt))
            deadline = time.monotonic() + 3
            while worker._results.empty() and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertTrue(worker.busy)
            self.assertFalse(worker.submit(attempt))
            self.assertEqual(worker.poll().status, 'preview')
            self.assertFalse(worker.busy)
