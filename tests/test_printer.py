"""Test LAN, Wi-Fi, and USB transport order without printer hardware."""

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch

from photobooth.printer import (
    NetworkConnectionError,
    NetworkSendError,
    PrinterConfig,
    ThermalPrinter,
)


class PrinterConfigTests(unittest.TestCase):
    def test_environment_parses_network_order_usb_ids_and_width(self):
        config = PrinterConfig.from_environment(
            {
                "PHOTOBOOTH_PRINTER_LAN_HOST": " 10.0.0.20 ",
                "PHOTOBOOTH_PRINTER_LAN_PORT": "9101",
                "PHOTOBOOTH_PRINTER_WIFI_HOST": " 192.168.1.25 ",
                "PHOTOBOOTH_PRINTER_WIFI_PORT": "9200",
                "PHOTOBOOTH_PRINTER_NETWORK_TIMEOUT": "1.5",
                "PHOTOBOOTH_PRINTER_USB_VENDOR_ID": "04b8",
                "PHOTOBOOTH_PRINTER_USB_PRODUCT_ID": "0x0202",
                "PHOTOBOOTH_PRINTER_USB_DEVICE": "/dev/usb/lp1",
                "PHOTOBOOTH_PRINTER_WIDTH_DOTS": "640",
            }
        )

        self.assertEqual(config.lan_host, "10.0.0.20")
        self.assertEqual(config.lan_port, 9101)
        self.assertEqual(config.wifi_host, "192.168.1.25")
        self.assertEqual(config.wifi_port, 9200)
        self.assertEqual(config.network_timeout, 1.5)
        self.assertEqual(config.usb_vendor_id, 0x04B8)
        self.assertEqual(config.usb_product_id, 0x0202)
        self.assertEqual(config.usb_device_path, "/dev/usb/lp1")
        self.assertEqual(config.print_width_dots, 640)

    def test_legacy_wifi_timeout_remains_a_fallback_alias(self):
        config = PrinterConfig.from_environment(
            {"PHOTOBOOTH_PRINTER_WIFI_TIMEOUT": "1.25"}
        )

        self.assertEqual(config.network_timeout, 1.25)

    def test_invalid_environment_uses_safe_defaults(self):
        config = PrinterConfig.from_environment(
            {
                "PHOTOBOOTH_PRINTER_LAN_PORT": "not-a-port",
                "PHOTOBOOTH_PRINTER_WIFI_PORT": "99999",
                "PHOTOBOOTH_PRINTER_NETWORK_TIMEOUT": "0",
                "PHOTOBOOTH_PRINTER_WIDTH_DOTS": "99999",
                "PHOTOBOOTH_PRINTER_USB_VENDOR_ID": "not-hex",
            }
        )

        self.assertEqual(config.lan_port, 9100)
        self.assertEqual(config.wifi_port, 9100)
        self.assertEqual(config.network_timeout, 2.0)
        self.assertEqual(config.print_width_dots, 576)
        self.assertIsNone(config.usb_vendor_id)


class ThermalPrinterTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.image_path = Path(self.temp_dir.name) / "result.png"
        self.image_path.write_bytes(b"test image")
        self.payload_builder = Mock(return_value=b"escpos job")

    def test_lan_is_primary_and_usb_is_not_used_on_success(self):
        network = Mock()
        usb = Mock()
        printer = ThermalPrinter(
            PrinterConfig(
                lan_host="10.0.0.20",
                wifi_host="192.168.1.20",
            ),
            payload_builder=self.payload_builder,
            network_sender=network,
            usb_sender=usb,
        )

        result = printer.print_image(self.image_path)

        self.payload_builder.assert_called_once_with(self.image_path)
        network.assert_called_once_with("10.0.0.20", 9100, b"escpos job")
        usb.assert_not_called()
        self.assertTrue(result.success)
        self.assertEqual(result.transport, "LAN")
        self.assertFalse(result.fell_back)

    def test_lan_connection_failure_tries_wifi_before_usb(self):
        network = Mock(
            side_effect=[
                NetworkConnectionError("LAN connection refused"),
                None,
            ]
        )
        usb = Mock()
        printer = ThermalPrinter(
            PrinterConfig(
                lan_host="10.0.0.20",
                wifi_host="192.168.1.20",
            ),
            payload_builder=self.payload_builder,
            network_sender=network,
            usb_sender=usb,
        )

        result = printer.print_image(self.image_path)

        self.assertEqual(
            network.call_args_list,
            [
                call("10.0.0.20", 9100, b"escpos job"),
                call("192.168.1.20", 9100, b"escpos job"),
            ],
        )
        usb.assert_not_called()
        self.assertTrue(result.success)
        self.assertEqual(result.transport, "Wi-Fi")
        self.assertTrue(result.fell_back)
        self.assertIn("LAN gagal", result.user_message)

    def test_all_network_connection_failures_fall_back_to_usb(self):
        network = Mock(
            side_effect=[
                NetworkConnectionError("LAN connection refused"),
                NetworkConnectionError("Wi-Fi host unreachable"),
            ]
        )
        usb = Mock()
        printer = ThermalPrinter(
            PrinterConfig(
                lan_host="10.0.0.20",
                lan_port=9101,
                wifi_host="192.168.1.20",
                wifi_port=9102,
            ),
            payload_builder=self.payload_builder,
            network_sender=network,
            usb_sender=usb,
        )

        result = printer.print_image(self.image_path)

        self.assertEqual(
            network.call_args_list,
            [
                call("10.0.0.20", 9101, b"escpos job"),
                call("192.168.1.20", 9102, b"escpos job"),
            ],
        )
        usb.assert_called_once_with(b"escpos job")
        self.assertTrue(result.success)
        self.assertEqual(result.transport, "USB")
        self.assertTrue(result.fell_back)
        self.assertIn("LAN, Wi-Fi tidak tersambung", result.user_message)

    def test_wifi_is_used_when_lan_host_is_not_configured(self):
        network = Mock()
        usb = Mock()
        printer = ThermalPrinter(
            PrinterConfig(wifi_host="192.168.1.20"),
            payload_builder=self.payload_builder,
            network_sender=network,
            usb_sender=usb,
        )

        result = printer.print_image(self.image_path)

        network.assert_called_once_with("192.168.1.20", 9100, b"escpos job")
        usb.assert_not_called()
        self.assertTrue(result.success)
        self.assertEqual(result.transport, "Wi-Fi")
        self.assertFalse(result.fell_back)

    def test_network_write_failure_does_not_retry_wifi_or_usb(self):
        network = Mock(side_effect=NetworkSendError("broken pipe"))
        usb = Mock()
        printer = ThermalPrinter(
            PrinterConfig(
                lan_host="10.0.0.20",
                wifi_host="192.168.1.20",
            ),
            payload_builder=self.payload_builder,
            network_sender=network,
            usb_sender=usb,
        )

        result = printer.print_image(self.image_path)

        network.assert_called_once_with("10.0.0.20", 9100, b"escpos job")
        usb.assert_not_called()
        self.assertFalse(result.success)
        self.assertIn("status cetak tidak pasti", result.message)

    def test_tcp_connection_error_is_classified_before_any_write(self):
        printer = ThermalPrinter(PrinterConfig())
        with patch(
            "photobooth.printer.socket.create_connection",
            side_effect=OSError("refused"),
        ):
            with self.assertRaises(NetworkConnectionError):
                printer._send_network("10.0.0.20", 9100, b"escpos job")

    def test_tcp_write_error_is_classified_as_uncertain(self):
        connection = Mock()
        connection.sendall.side_effect = OSError("broken pipe")
        printer = ThermalPrinter(PrinterConfig())
        with patch(
            "photobooth.printer.socket.create_connection",
            return_value=connection,
        ):
            with self.assertRaises(NetworkSendError):
                printer._send_network("10.0.0.20", 9100, b"escpos job")
        connection.close.assert_called_once()

    def test_blank_network_hosts_use_usb_immediately(self):
        network = Mock()
        usb = Mock()
        printer = ThermalPrinter(
            PrinterConfig(),
            payload_builder=self.payload_builder,
            network_sender=network,
            usb_sender=usb,
        )

        result = printer.print_image(self.image_path)

        network.assert_not_called()
        usb.assert_called_once_with(b"escpos job")
        self.assertTrue(result.success)
        self.assertEqual(result.transport, "USB")
        self.assertFalse(result.fell_back)

    def test_payload_scales_to_80mm_head_width_and_adds_cut(self):
        from PIL import Image

        class Dummy:
            output = b"escpos job"
            image_size = None
            cut_called = False

            def image(self, bitmap, **kwargs):
                self.image_size = bitmap.size
                self.image_options = kwargs

            def cut(self):
                self.cut_called = True

        dummy = Dummy()
        escpos_module = types.ModuleType("escpos")
        printer_module = types.ModuleType("escpos.printer")
        printer_module.Dummy = lambda: dummy
        escpos_module.printer = printer_module
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "result.png"
            Image.new("RGB", (640, 1920), "white").save(image_path)
            printer = ThermalPrinter(PrinterConfig(print_width_dots=576))
            with patch.dict(
                sys.modules,
                {
                    "escpos": escpos_module,
                    "escpos.printer": printer_module,
                },
            ):
                payload = printer._build_payload(image_path)

        self.assertEqual(dummy.image_size, (576, 1728))
        self.assertEqual(dummy.image_options["impl"], "bitImageRaster")
        self.assertTrue(dummy.cut_called)
        self.assertEqual(payload, b"escpos job")

    def test_missing_image_is_rejected_before_opening_a_transport(self):
        network = Mock()
        usb = Mock()
        printer = ThermalPrinter(
            PrinterConfig(lan_host="10.0.0.20", wifi_host="192.168.1.20"),
            payload_builder=self.payload_builder,
            network_sender=network,
            usb_sender=usb,
        )

        result = printer.print_image(Path(self.temp_dir.name) / "missing.png")

        network.assert_not_called()
        usb.assert_not_called()
        self.payload_builder.assert_not_called()
        self.assertFalse(result.success)
        self.assertIn("tidak ditemukan", result.message)


if __name__ == "__main__":
    unittest.main()
