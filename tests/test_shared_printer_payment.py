"""Payment QR receipts use the same saved printer as photo strips."""
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from photobooth.printer import PrinterConfig
from photobooth.qris_print import QrisPrinterWorker


class SavedPaymentPrinterTests(unittest.TestCase):
    def test_saved_windows_queue_routes_qr_bytes_to_raw_spooler(self):
        from photobooth.payment import DemoPaymentGateway, PaymentCoordinator
        with tempfile.TemporaryDirectory() as tmp:
            payment = PaymentCoordinator(DemoPaymentGateway(900))
            attempt = payment.start(5000)
            config = PrinterConfig(windows_printer_name="POS80 Printer", print_width_dots=576)
            worker = QrisPrinterWorker(Path(tmp), printer_config_provider=lambda: config)
            with patch("photobooth.printer.ThermalPrinter._send_windows_raw") as raw:
                self.assertTrue(worker.submit(attempt))
                result = None
                for _ in range(150):
                    result = worker.poll()
                    if result is not None:
                        break
                    time.sleep(.02)
                self.assertIsNotNone(result)
                self.assertEqual(result.status, "sent")
                raw.assert_called_once()
                self.assertEqual(raw.call_args.args[0], "POS80 Printer")
                self.assertIn(b"\x1d\x76\x30", raw.call_args.args[1])
            worker.close()


if __name__ == "__main__":
    unittest.main()
