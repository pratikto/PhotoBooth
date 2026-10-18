"""Mocked Windows spooler tests; no physical printer required."""
import sys
import types
import unittest
from unittest.mock import Mock, patch

from photobooth.printer import PrinterConfig, ThermalPrinter


class WindowsRawTests(unittest.TestCase):
    def test_queue_name_is_explicit_and_parsed(self):
        cfg = PrinterConfig.from_environment({
            "PHOTOBOOTH_PRINTER_WINDOWS_NAME": " POS80 Printer(2) "
        })
        self.assertEqual(cfg.windows_printer_name, "POS80 Printer(2)")

    def test_raw_payload_and_job_cleanup(self):
        fake = types.ModuleType("win32print")
        fake.OpenPrinter = Mock(return_value=123)
        fake.StartDocPrinter = Mock(return_value=45)
        fake.StartPagePrinter = Mock()
        fake.WritePrinter = Mock(side_effect=lambda handle, data: len(data))
        fake.EndPagePrinter = Mock()
        fake.EndDocPrinter = Mock()
        fake.ClosePrinter = Mock()
        with patch.dict(sys.modules, {"win32print": fake}):
            ThermalPrinter._send_windows_raw("POS80 Printer", b"\x1b@HELLO")
        fake.OpenPrinter.assert_called_once_with("POS80 Printer")
        fake.StartDocPrinter.assert_called_once_with(
            123, 1, ("Meong Photobooth ESC/POS", None, "RAW")
        )
        fake.WritePrinter.assert_called_once_with(123, b"\x1b@HELLO")
        fake.EndDocPrinter.assert_called_once_with(123)
        fake.ClosePrinter.assert_called_once_with(123)

    def test_three_copies_are_one_windows_raw_document(self):
        """Three physical cuts share a single StartDocPrinter/WritePrinter.

        The spooler returns a byte count, not a sensor reading for real paper.
        """
        from pathlib import Path
        from tempfile import TemporaryDirectory
        fake = types.ModuleType("win32print")
        fake.OpenPrinter = Mock(return_value=42)
        fake.StartDocPrinter = Mock(return_value=73)
        fake.StartPagePrinter = Mock()
        fake.WritePrinter = Mock(side_effect=lambda handle, data: len(data))
        fake.EndPagePrinter = Mock()
        fake.EndDocPrinter = Mock()
        fake.ClosePrinter = Mock()
        base = b"IMG" + b"\x1dV\x00"
        with TemporaryDirectory() as temp:
            image = Path(temp) / "result.png"
            image.write_bytes(b"mocked input")
            printer = ThermalPrinter(
                PrinterConfig(windows_printer_name="POS80 Printer"),
                payload_builder=Mock(return_value=base),
            )
            with patch.dict(sys.modules, {"win32print": fake}), \\
                 patch("photobooth.printer.os.name", "nt"):
                result = printer.print_image(image, copies=3)

        self.assertTrue(result.success)
        fake.StartDocPrinter.assert_called_once()
        fake.WritePrinter.assert_called_once_with(42, base * 3)
        fake.EndDocPrinter.assert_called_once()
        fake.ClosePrinter.assert_called_once()

    def test_partial_spooler_write_is_not_retried(self):
        fake = types.ModuleType("win32print")
        fake.OpenPrinter = Mock(return_value=1)
        fake.StartDocPrinter = Mock()
        fake.StartPagePrinter = Mock()
        fake.WritePrinter = Mock(return_value=1)
        fake.EndPagePrinter = Mock()
        fake.EndDocPrinter = Mock()
        fake.ClosePrinter = Mock()
        with patch.dict(sys.modules, {"win32print": fake}):
            with self.assertRaises(OSError):
                ThermalPrinter._send_windows_raw("POS80 Printer", b"\x1b@HELLO")
        fake.EndDocPrinter.assert_called_once()
        fake.ClosePrinter.assert_called_once()

    def test_windows_config_routes_usb_to_spooler(self):
        printer = ThermalPrinter(PrinterConfig(windows_printer_name="POS80 Printer"))
        with patch("photobooth.printer.os.name", "nt"):
            with patch.object(printer, "_send_windows_raw") as sender:
                printer._send_usb(b"raw")
                sender.assert_called_once_with("POS80 Printer", b"raw")


if __name__ == "__main__":
    unittest.main()
