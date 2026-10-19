"""FEAT-008 B.3 read-only cross-platform reconnect regression."""
import unittest
from types import SimpleNamespace
from photobooth.device_selection import DeviceSelection, stage_selection
from photobooth.device_recovery import selected_device_observation as observe


def candidate(kind, name, presence):
    return SimpleNamespace(kind=kind, name=name, device_id=name, presence=presence)


class DeviceRecoveryTests(unittest.TestCase):
    def test_empty_selection_preserves_legacy_behavior(self):
        self.assertEqual(observe(DeviceSelection(), "camera", platform="win32").state, "unselected")

    def test_discovery_unavailable_is_not_disconnection(self):
        s = stage_selection(DeviceSelection(), printer=("windows-spooler", "POS80"))
        self.assertEqual(observe(s, "printer", platform="win32").state, "unknown")

    def test_windows_printer_disconnect_and_return_same_identity(self):
        s = stage_selection(DeviceSelection(), printer=("windows-spooler", "POS80"))
        detected = [candidate("printer", "POS80", "queue-detected")]
        first = observe(s, "printer", platform="win32", detected=detected, discovery_complete=True)
        missing = observe(s, "printer", platform="win32", detected=[], previous=first, discovery_complete=True)
        other = observe(s, "printer", platform="win32",
                        detected=[candidate("printer", "Another printer", "queue-detected")],
                        previous=missing, discovery_complete=True)
        returned = observe(s, "printer", platform="win32", detected=detected,
                           previous=missing, discovery_complete=True)
        self.assertEqual([x.state for x in (first, missing, other, returned)],
                         ["candidate", "missing", "missing", "returned"])

    def test_configured_routes_do_not_fake_presence(self):
        s = stage_selection(DeviceSelection(), printer=("windows-spooler", "POS80"))
        result = observe(s, "printer", platform="win32",
                         detected=[candidate("printer", "POS80", "configured")],
                         discovery_complete=True)
        self.assertEqual(result.state, "missing")

    def test_linux_alias_must_match_original_camera(self):
        s = stage_selection(DeviceSelection(), camera=("linux-v4l-by-id", "usb-camera-index0"))
        result = observe(s, "camera", platform="linux",
                         detected=[candidate("camera", "/dev/v4l/by-id/usb-camera-index0", "node-detected")],
                         discovery_complete=True)
        self.assertEqual(result.state, "candidate")
        self.assertEqual(observe(s, "camera", platform="linux",
                         detected=[candidate("camera", "/dev/video0", "node-detected")],
                         discovery_complete=True).state, "missing")

    def test_windows_camera_index_requires_live_frame(self):
        s = stage_selection(DeviceSelection(), camera=("opencv-index", "3"))
        self.assertEqual(observe(s, "camera", platform="win32",
                         discovery_complete=True).state, "unknown")

    def test_cross_os_is_unsupported_and_android_deferred(self):
        s = stage_selection(DeviceSelection(), printer=("windows-spooler", "POS80"))
        self.assertEqual(observe(s, "printer", platform="linux", discovery_complete=True).state,
                         "unsupported")
        self.assertEqual(observe(s, "printer", platform="android", discovery_complete=True).state,
                         "unsupported")

    def test_invalid_device_kind_rejected(self):
        with self.assertRaises(ValueError):
            observe(DeviceSelection(), "disk", platform="win32")
