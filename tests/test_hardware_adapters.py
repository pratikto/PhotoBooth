"""Safe platform capability descriptors; never enumerate physical cameras here."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from photobooth.hardware_adapters import (
    DeviceDescriptor, platform_family, adapter_for, configured_inventory,
)
from photobooth.device_health import collect_health_snapshot, READY, UNKNOWN
from photobooth.printer import PrinterConfig


class HardwareAdapterTests(unittest.TestCase):
    def test_windows_platform(self):
        self.assertEqual(platform_family("win32", {}), "windows")
        self.assertEqual(adapter_for("win32", {}).family, "windows")

    def test_linux_platform(self):
        self.assertEqual(platform_family("linux", {}), "linux")
        self.assertEqual(adapter_for("linux", {}).family, "linux")

    def test_android_native_platform(self):
        self.assertEqual(platform_family("android", {}), "android")

    def test_android_python_linux_detection(self):
        self.assertEqual(platform_family("linux", {"ANDROID_ARGUMENT": "/a"}), "android")

    def test_normal_linux_with_unrelated_env_not_android(self):
        self.assertEqual(platform_family("linux", {"SHELL": "/bin/sh"}), "linux")

    def test_unsupported_platform_is_explicit(self):
        self.assertEqual(adapter_for("darwin", {}).family, "other")

    def test_active_camera_index_is_ephemeral_not_hardware_id(self):
        obj = SimpleNamespace(camera_index=2, capture=object())
        result = adapter_for("linux", {}).describe_camera(obj)
        self.assertEqual(result.name, "Configured camera index 2")
        self.assertEqual(result.presence, "active-handle")
        self.assertEqual(result.identity_quality, "ephemeral")
        self.assertIn("cached-frame", result.capabilities)

    def test_configured_camera_not_claimed_as_detected(self):
        result = adapter_for("win32", {}).describe_camera(
            SimpleNamespace(camera_index=0, capture=None)
        )
        self.assertEqual(result.presence, "not-open")
        self.assertNotEqual(result.identity_quality, "stable")

    def test_windows_printer_identifies_routes_without_claiming_paper(self):
        cfg = PrinterConfig(
            lan_host="192.0.2.10", wifi_host="192.0.2.11",
            windows_printer_name="POS80 Queue",
        )
        devices = configured_inventory(None, cfg, platform="win32", environ={})
        printers = [item for item in devices if item.kind == "printer"]
        self.assertEqual(
            [item.device_id for item in printers],
            ["printer:lan", "printer:wifi", "printer:windows-queue"],
        )
        self.assertTrue(all(item.presence == "configured" for item in printers))
        self.assertTrue(all("paper" not in item.capabilities for item in printers))

    def test_linux_uses_node_only_as_configured(self):
        cfg = PrinterConfig(usb_device_path="/dev/usb/lp0")
        devices = configured_inventory(None, cfg, platform="linux", environ={})
        route = next(x for x in devices if x.device_id == "printer:usb-path")
        self.assertEqual(route.identity_quality, "ephemeral")
        self.assertEqual(route.presence, "configured")

    def test_usb_vidpid_is_model_only(self):
        cfg = PrinterConfig(usb_vendor_id=0x1234, usb_product_id=0x5678)
        desc = configured_inventory(None, cfg, platform="linux", environ={})
        route = next(x for x in desc if x.device_id == "printer:usb-vidpid")
        self.assertEqual(route.identity_quality, "model-only")

    def test_android_reports_unimplemented_native_bridges(self):
        cfg = PrinterConfig(lan_host="192.0.2.4", windows_printer_name="queue")
        inventory = configured_inventory(SimpleNamespace(camera_index=0), cfg,
                                         platform="android", environ={})
        self.assertEqual(len(inventory), 2)
        self.assertTrue(all(d.presence == "unsupported" for d in inventory))
        self.assertTrue(all(not d.capabilities for d in inventory))

    def test_android_snapshot_does_not_run_desktop_printer_or_camera_probes(self):
        cfg = PrinterConfig(lan_host="192.0.2.4")
        with (
            patch("photobooth.device_health.check_camera") as cam,
            patch("photobooth.device_health.check_printer") as printer,
            patch("photobooth.device_health.check_disk") as disk,
            patch("photobooth.device_health.check_network") as network,
            patch("photobooth.device_health.check_media") as media,
            patch("photobooth.device_health.check_heartbeat") as heartbeat,
        ):
            from photobooth.device_health import HealthCheck
            for mocked, kind in ((disk, "disk"), (network, "network"),
                                 (media, "media"), (heartbeat, "heartbeat")):
                mocked.return_value = HealthCheck(kind, READY, "mock")
            report = collect_health_snapshot(
                camera=SimpleNamespace(camera_index=0),
                printer_config=cfg,
                platform="android",
            )
        cam.assert_not_called()
        printer.assert_not_called()
        self.assertEqual(report.platform, "android")
        self.assertEqual(report.by_name("camera").status, UNKNOWN)
        self.assertEqual(report.by_name("printer").status, UNKNOWN)
        self.assertTrue(all(d.presence == "unsupported" for d in report.devices))

    def test_snapshot_is_backwards_compatible_with_existing_constructor(self):
        from photobooth.device_health import HealthSnapshot
        report = HealthSnapshot("2026-10-19T00:00:00+00:00", ())
        self.assertEqual(report.devices, ())
        self.assertEqual(report.platform, "unknown")


if __name__ == "__main__":
    unittest.main()
