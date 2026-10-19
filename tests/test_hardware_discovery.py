"""FEAT-008 B.2: read-only OS discovery, with no physical device opened."""
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from photobooth.hardware_discovery import (
    _enumerate_windows_queues, _linux_cups_queues, _linux_video_devices,
    discover_local_devices,
)
from photobooth.device_health import collect_health_snapshot, HealthCheck, READY


class DiscoveryTests(unittest.TestCase):
    def test_windows_enumeration_uses_queue_list_only(self):
        spooler = SimpleNamespace(
            PRINTER_ENUM_LOCAL=2, PRINTER_ENUM_CONNECTIONS=4,
            EnumPrinters=Mock(return_value=[
                {"pPrinterName": "POS80"}, {"pPrinterName": "POS80"},
                {"pPrinterName": "Office Laser"}, {"pPrinterName": ""},
            ]),
            OpenPrinter=Mock(), StartDocPrinter=Mock(),
        )
        found = discover_local_devices(platform="win32", environ={}, spooler=spooler)
        self.assertEqual([d.device_id for d in found],
                         ["win-queue:Office Laser", "win-queue:POS80"])
        self.assertTrue(all(d.presence == "queue-detected" for d in found))
        self.assertTrue(all(d.identity_quality == "queue-name" for d in found))
        spooler.EnumPrinters.assert_called_once_with(6, None, 2)
        spooler.OpenPrinter.assert_not_called()
        spooler.StartDocPrinter.assert_not_called()

    def test_windows_spooler_missing_means_no_claim_of_detection(self):
        bad = SimpleNamespace(PRINTER_ENUM_LOCAL=2, PRINTER_ENUM_CONNECTIONS=4,
                              EnumPrinters=Mock(side_effect=OSError("offline")))
        self.assertEqual(discover_local_devices(platform="win32", environ={}, spooler=bad), ())

    def test_linux_cups_queue_enumeration_is_read_only_and_bounded(self):
        runner = Mock(return_value=SimpleNamespace(
            returncode=0, stdout="POS80\nOffice\nPOS80\n"
        ))
        names = _linux_cups_queues(runner=runner)
        self.assertEqual(names, ("Office", "POS80"))
        runner.assert_called_once_with(
            ["lpstat", "-e"], capture_output=True, text=True,
            timeout=1.5, check=False,
        )

    def test_linux_cups_failure_returns_empty_not_false_ready(self):
        runner = Mock(return_value=SimpleNamespace(returncode=1, stdout=""))
        self.assertEqual(_linux_cups_queues(runner=runner), ())

    def test_linux_v4l_by_id_alias_is_stable_candidate_not_verified_camera(self):
        with tempfile.TemporaryDirectory() as root_path:
            root = Path(root_path)
            v4l = root / "v4l" / "by-id"
            v4l.mkdir(parents=True)
            fake = root / "video0"
            fake.write_bytes(b"fake camera device file")
            alias = v4l / "usb-ExampleCam-video-index0"
            alias.symlink_to(fake)
            found = _linux_video_devices(root=root)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].identity_quality, "udev-by-id")
        self.assertEqual(found[0].presence, "node-detected")
        self.assertNotIn("cached-frame", found[0].capabilities)

    def test_linux_not_connected_device_nodes_not_invented(self):
        with tempfile.TemporaryDirectory() as root_path:
            found = discover_local_devices(
                platform="linux", environ={}, root=Path(root_path),
                cups_runner=Mock(return_value=SimpleNamespace(returncode=1, stdout="")),
            )
            self.assertEqual(found, ())

    def test_android_never_invokes_desktop_enumeration(self):
        spooler = SimpleNamespace(EnumPrinters=Mock())
        runner = Mock()
        found = discover_local_devices(
            platform="android", environ={}, spooler=spooler,
            cups_runner=runner,
        )
        self.assertEqual(found, ())
        spooler.EnumPrinters.assert_not_called()
        runner.assert_not_called()

    def test_no_discovery_by_default_preserves_original_mock_purity(self):
        with patch("photobooth.device_health.discover_local_devices") as discover, (
            patch("photobooth.device_health.check_camera",
                  return_value=HealthCheck("camera", READY, "ok"))
        ), (
            patch("photobooth.device_health.check_printer",
                  return_value=HealthCheck("printer", READY, "ok"))
        ), (
            patch("photobooth.device_health.check_disk",
                  return_value=HealthCheck("disk", READY, "ok"))
        ), (
            patch("photobooth.device_health.check_network",
                  return_value=HealthCheck("network", READY, "ok"))
        ), (
            patch("photobooth.device_health.check_media",
                  return_value=HealthCheck("media", READY, "ok"))
        ), (
            patch("photobooth.device_health.check_heartbeat",
                  return_value=HealthCheck("heartbeat", READY, "ok"))
        ):
            report = collect_health_snapshot(platform="linux")
        discover.assert_not_called()
        self.assertEqual(len(report.checks), 6)

    def test_explicit_discovery_augments_inventory_without_overwriting_current_selection(self):
        from photobooth.hardware_adapters import DeviceDescriptor
        candidate = DeviceDescriptor(
            "printer", "win-queue:POS80", "POS80",
            "windows-spooler", "windows", "queue-name",
            "queue-detected", ("spooler-presence",), "No paper check",
        )
        with patch("photobooth.device_health.discover_local_devices", return_value=(candidate,)) as scan:
            with (
                patch("photobooth.device_health.check_camera", return_value=HealthCheck("camera", READY, "ok")),
                patch("photobooth.device_health.check_printer", return_value=HealthCheck("printer", READY, "ok")),
                patch("photobooth.device_health.check_disk", return_value=HealthCheck("disk", READY, "ok")),
                patch("photobooth.device_health.check_network", return_value=HealthCheck("network", READY, "ok")),
                patch("photobooth.device_health.check_media", return_value=HealthCheck("media", READY, "ok")),
                patch("photobooth.device_health.check_heartbeat", return_value=HealthCheck("heartbeat", READY, "ok")),
            ):
                report = collect_health_snapshot(
                    platform="win32", include_discovery=True,
                )
        scan.assert_called_once_with(platform="win32")
        self.assertEqual(report.devices[-1], candidate)
        self.assertEqual(report.devices[0].kind, "camera")


if __name__ == "__main__":
    unittest.main()
