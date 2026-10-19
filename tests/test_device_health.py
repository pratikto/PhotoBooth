"""FEAT-008 Stage A: deterministic, no-hardware health probe regressions."""

from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from photobooth import device_health as health
from photobooth.printer import PrinterConfig


class DeviceHealthTests(unittest.TestCase):
    def setUp(self):
        self.opened = []

    def fake_dial(self, host, port, timeout):
        """Return a closeable fake socket, capturing every attempted route."""
        self.opened.append((host, port, timeout))
        return SimpleNamespace(close=Mock())

    def test_camera_not_supplied_does_not_open_device(self):
        self.assertEqual(health.check_camera(None).status, health.UNKNOWN)

    def test_camera_closed_is_unavailable_without_reopening(self):
        fake = SimpleNamespace(capture=None, open=Mock(), read=Mock())
        self.assertEqual(health.check_camera(fake).status, health.UNAVAILABLE)
        fake.open.assert_not_called()
        fake.read.assert_not_called()

    def test_camera_live_frame_is_ready_with_mailbox_only(self):
        fake = SimpleNamespace(
            capture=SimpleNamespace(isOpened=lambda: True),
            read=Mock(return_value=object()),
            open=Mock(),
        )
        self.assertEqual(health.check_camera(fake).status, health.READY)
        fake.read.assert_called_once_with()
        fake.open.assert_not_called()

    def test_camera_stale_frame_is_warning(self):
        fake = SimpleNamespace(
            capture=SimpleNamespace(isOpened=lambda: True),
            read=lambda: None,
        )
        self.assertEqual(health.check_camera(fake).status, health.WARNING)

    def test_camera_status_exception_does_not_abort_diagnostics(self):
        fake = SimpleNamespace(
            capture=SimpleNamespace(isOpened=Mock(side_effect=OSError("driver"))),
            read=Mock(),
        )
        self.assertEqual(health.check_camera(fake).status, health.UNAVAILABLE)
        fake.read.assert_not_called()

    def test_printer_network_probe_does_not_send_print_data(self):
        connection = SimpleNamespace(close=Mock(), send=Mock(), sendall=Mock())
        dial = Mock(return_value=connection)
        config = PrinterConfig(lan_host="192.0.2.15", wifi_host="192.0.2.16")
        result = health.check_printer(config, dial=dial, platform="win32")
        self.assertEqual(result.status, health.READY)
        self.assertIn("paper status is unknown", result.message)
        dial.assert_called_once_with("192.0.2.15", 9100, 0.75)
        connection.close.assert_called_once_with()
        connection.send.assert_not_called()
        connection.sendall.assert_not_called()

    def test_printer_wifi_fallback_after_lan_failure(self):
        def dial(host, port, timeout):
            self.opened.append((host, port, timeout))
            if host == "192.0.2.1":
                raise OSError("LAN offline")
            return SimpleNamespace(close=Mock())
        config = PrinterConfig(lan_host="192.0.2.1", wifi_host="192.0.2.2")
        result = health.check_printer(config, dial=dial, platform="win32")
        self.assertEqual(result.status, health.READY)
        self.assertTrue(result.message.startswith("Wi-Fi"))
        self.assertEqual([r[0] for r in self.opened], ["192.0.2.1", "192.0.2.2"])

    def test_printer_windows_queue_only_checks_spooler_not_paper(self):
        queue_probe = Mock(return_value=True)
        config = PrinterConfig(windows_printer_name="POS80 Printer")
        result = health.check_printer(
            config, platform="win32", windows_queue_probe=queue_probe
        )
        self.assertEqual(result.status, health.READY)
        self.assertIn("paper status are unknown", result.message)
        queue_probe.assert_called_once_with("POS80 Printer")

    def test_printer_unavailable_queue_and_network_are_warning(self):
        config = PrinterConfig(lan_host="192.0.2.1", windows_printer_name="POS80")
        result = health.check_printer(
            config, platform="win32",
            dial=Mock(side_effect=OSError("offline")),
            windows_queue_probe=Mock(side_effect=OSError("spooler offline")),
        )
        self.assertEqual(result.status, health.WARNING)
        self.assertNotIn("192.0.2.1", result.message)
        self.assertNotIn("POS80", result.message)

    def test_printer_usb_device_node_is_presence_only(self):
        config = PrinterConfig(usb_device_path="/dev/usb/lp0")
        result = health.check_printer(
            config, platform="linux", device_exists=lambda _: True
        )
        self.assertEqual(result.status, health.READY)
        self.assertIn("paper status are unknown", result.message)

    def test_printer_usb_ids_only_never_claim_ready(self):
        config = PrinterConfig(
            usb_vendor_id=0x04B8, usb_product_id=0x0202, usb_device_path=None
        )
        result = health.check_printer(config, platform="linux")
        self.assertEqual(result.status, health.UNKNOWN)

    def test_printer_missing_config_is_unknown(self):
        self.assertEqual(health.check_printer(None).status, health.UNKNOWN)

    def test_disk_healthy_checks_nearest_existing_ancestor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            usage = Mock(return_value=SimpleNamespace(total=1000, free=700))
            r = health.check_disk(
                root / "not-yet-created" / "photos",
                usage=usage,
                minimum_free_bytes=50,
            )
            self.assertEqual(r.status, health.READY)
            usage.assert_called_once_with(root)

    def test_disk_warns_when_bytes_or_percentage_low(self):
        usage = Mock(return_value=SimpleNamespace(total=1000, free=80))
        r = health.check_disk(
            ".", usage=usage, minimum_free_bytes=50, minimum_free_fraction=0.1
        )
        self.assertEqual(r.status, health.WARNING)
        usage = Mock(return_value=SimpleNamespace(total=1000, free=200))
        r = health.check_disk(
            ".", usage=usage, minimum_free_bytes=250, minimum_free_fraction=0.1
        )
        self.assertEqual(r.status, health.WARNING)

    def test_disk_errors_are_unknown_and_no_files_created(self):
        self.assertEqual(health.check_disk(None).status, health.UNKNOWN)
        result = health.check_disk(".", usage=Mock(side_effect=OSError("denied")))
        self.assertEqual(result.status, health.UNKNOWN)
        self.assertEqual(
            health.check_disk(".", usage=lambda _: SimpleNamespace(total=0, free=0)).status,
            health.UNKNOWN,
        )

    def test_network_socket_is_closed_and_timeout_is_short(self):
        connection = SimpleNamespace(close=Mock(), send=Mock())
        dial = Mock(return_value=connection)
        result = health.check_network(dial=dial)
        self.assertEqual(result.status, health.READY)
        dial.assert_called_once_with("1.1.1.1", 443, 0.75)
        connection.close.assert_called_once_with()
        connection.send.assert_not_called()

    def test_network_probe_failure_not_absolute_internet_claim(self):
        result = health.check_network(dial=Mock(side_effect=TimeoutError()))
        self.assertEqual(result.status, health.WARNING)
        self.assertIn("other network routes", result.message)

    def test_media_assets_exist_but_decoder_not_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "playlist.json").write_text("{}", encoding="utf-8")
            (root / "ad.jpg").write_bytes(b"image stub")
            (root / "poster.jpg").write_bytes(b"poster stub")
            catalog = SimpleNamespace(
                path=root / "playlist.json",
                items=[SimpleNamespace(path=root / "ad.jpg", poster=root / "poster.jpg")],
            )
            result = health.check_media(catalog)
            self.assertEqual(result.status, health.READY)
            self.assertIn("decoder not tested", result.message)

    def test_media_missing_playlist_or_assets_are_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = SimpleNamespace(path=root / "not-found.mp4", poster=None)
            catalog = SimpleNamespace(path=root / "playlist.json", items=[item])
            self.assertEqual(health.check_media(catalog).status, health.WARNING)
            catalog.path.write_text("{}", encoding="utf-8")
            self.assertEqual(health.check_media(catalog).status, health.WARNING)
            (root / "not-found.mp4").write_bytes(b"")
            self.assertEqual(health.check_media(catalog).status, health.WARNING)

    def test_media_empty_and_unknown_status(self):
        self.assertEqual(health.check_media(None).status, health.UNKNOWN)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "playlist.json"
            path.write_text("{}", encoding="utf-8")
            self.assertEqual(
                health.check_media(SimpleNamespace(path=path, items=[])).status,
                health.WARNING,
            )

    def test_heartbeat_ready_stale_and_absent(self):
        self.assertEqual(health.check_heartbeat(None).status, health.UNKNOWN)
        self.assertEqual(health.check_heartbeat(100.0, now=103.0).status, health.READY)
        self.assertEqual(health.check_heartbeat(100.0, now=106.0).status, health.WARNING)
        self.assertEqual(health.check_heartbeat(103.0, now=100.0).status, health.UNKNOWN)

    def test_snapshot_has_six_ordered_checks_with_timezone_aware_timestamp(self):
        # No real physical I/O. Patch every check that could reach a device
        # or filesystem; the snapshot only aggregates typed observations.
        with (
            patch.object(health, "check_camera", return_value=health.HealthCheck("camera", health.READY, "test")),
            patch.object(health, "check_printer", return_value=health.HealthCheck("printer", health.UNKNOWN, "test")),
            patch.object(health, "check_disk", return_value=health.HealthCheck("disk", health.READY, "test")),
            patch.object(health, "check_network", return_value=health.HealthCheck("network", health.WARNING, "test")),
            patch.object(health, "check_media", return_value=health.HealthCheck("media", health.READY, "test")),
            patch.object(health, "check_heartbeat", return_value=health.HealthCheck("heartbeat", health.UNKNOWN, "test")),
        ):
            snapshot = health.collect_health_snapshot()
        self.assertEqual(
            [check.name for check in snapshot.checks],
            ["camera", "printer", "disk", "network", "media", "heartbeat"],
        )
        self.assertEqual(snapshot.by_name("network").status, health.WARNING)
        self.assertTrue(snapshot.checked_at.endswith("+00:00"))


if __name__ == "__main__":
    unittest.main()
