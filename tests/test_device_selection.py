"""No-hardware regression for next-start hardware selection (FEAT-008 B.2.1)."""
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from photobooth.device_selection import (
    DeviceSelection, DeviceSelectionError, camera_startup_source,
    load_device_selection, printer_startup_config, save_device_selection,
    stage_selection,
)
from photobooth.printer import PrinterConfig


class DeviceSelectionTests(unittest.TestCase):
    def test_missing_preferences_preserve_legacy_startup(self):
        with tempfile.TemporaryDirectory() as temp:
            prefs = load_device_selection(Path(temp) / "not-created.json")
        self.assertEqual(prefs, DeviceSelection())
        self.assertEqual(camera_startup_source(prefs, 3, platform="win32"), 3)
        cfg = PrinterConfig(lan_host="192.0.2.50")
        self.assertIs(printer_startup_config(prefs, cfg, platform="win32"), cfg)

    def test_atomic_save_round_trip_and_no_transient_files(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data" / "device_selection.json"
            chosen = stage_selection(DeviceSelection(), camera=("opencv-index", "2"))
            save_device_selection(path, chosen)
            self.assertEqual(load_device_selection(path), chosen)
            self.assertEqual(set(p.name for p in path.parent.iterdir()), {path.name})
            self.assertEqual(json.loads(path.read_text())["version"], 1)

    def test_staging_one_kind_keeps_the_other(self):
        camera = stage_selection(DeviceSelection(), camera=("opencv-index", "3"))
        both = stage_selection(camera, printer=("windows-spooler", "Thermal POS"))
        self.assertEqual(both.camera_value, "3")
        self.assertEqual(both.printer_value, "Thermal POS")
        reset = stage_selection(both, camera=("", ""))
        self.assertEqual(reset.camera_kind, "")
        self.assertEqual(reset.printer_value, "Thermal POS")

    def test_index_boundary_validation(self):
        for ok in ("0", "9", "10", "15"):
            self.assertEqual(camera_startup_source(
                stage_selection(DeviceSelection(), camera=("opencv-index", ok)),
                0, platform="win32"), int(ok))
        for bad in ("-1", "16", "001", " 2", "2.0", "999", "cv2"):
            with self.subTest(bad=bad), self.assertRaises(DeviceSelectionError):
                stage_selection(DeviceSelection(), camera=("opencv-index", bad))

    def test_v4l_rejects_traversal_paths_and_unreliable_names(self):
        for bad in ("../../passwd", "video0", "..", "usb-a/../../evil",
                    "usb-\n", "pci-foo\\other", "", "usb-" + "a" * 190):
            with self.subTest(bad=bad), self.assertRaises(DeviceSelectionError):
                stage_selection(DeviceSelection(), camera=("linux-v4l-by-id", bad))

    def test_linux_camera_symlink_remains_selected_and_is_not_opened(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            node = root / "video2"
            node.write_bytes(b"fake node; no camera opened")
            aliases = root / "by-id"
            aliases.mkdir()
            (aliases / "usb-ExampleCam-video-index0").symlink_to(node)
            chosen = stage_selection(DeviceSelection(), camera=(
                "linux-v4l-by-id", "usb-ExampleCam-video-index0",
            ))
            result = camera_startup_source(
                chosen, 0, platform="linux", aliases_root=aliases,
            )
            self.assertEqual(result, str(aliases / "usb-ExampleCam-video-index0"))

    def test_missing_selected_camera_fails_closed_never_uses_index_zero(self):
        chosen = stage_selection(DeviceSelection(), camera=(
            "linux-v4l-by-id", "usb-ExampleCam-video-index0",
        ))
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(DeviceSelectionError):
                camera_startup_source(chosen, 0, platform="linux", aliases_root=Path(temp))

    def test_camera_selection_does_not_cross_os(self):
        selected = stage_selection(DeviceSelection(), camera=(
            "linux-v4l-by-id", "usb-ExampleCam-video-index0",
        ))
        with self.assertRaises(DeviceSelectionError):
            camera_startup_source(selected, 0, platform="win32")
        selected = stage_selection(DeviceSelection(), camera=("opencv-index", "1"))
        with self.assertRaises(DeviceSelectionError):
            camera_startup_source(selected, 0, platform="android")

    def test_windows_printer_activation_does_not_modify_saved_config(self):
        cfg = PrinterConfig(
            lan_host="192.0.2.45", wifi_host="192.0.2.46",
            windows_printer_name="Old queue", dither_mode="floyd-steinberg",
        )
        selected = stage_selection(DeviceSelection(), printer=(
            "windows-spooler", "POS80 Window queue",
        ))
        applied = printer_startup_config(selected, cfg, platform="win32")
        self.assertEqual(applied.windows_printer_name, "POS80 Window queue")
        self.assertEqual(applied.lan_host, "")
        self.assertEqual(applied.wifi_host, "")
        self.assertEqual(cfg.lan_host, "192.0.2.45")
        self.assertEqual(applied.dither_mode, cfg.dither_mode)

    def test_cross_platform_printer_selection_fails_closed(self):
        selected = stage_selection(DeviceSelection(), printer=(
            "windows-spooler", "POS80",
        ))
        with self.assertRaises(DeviceSelectionError):
            printer_startup_config(selected, PrinterConfig(), platform="linux")

    def test_corrupt_file_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "selected.json"
            for raw in ('{bad json', '{"version":2}', '["other"]'):
                path.write_text(raw, encoding="utf-8")
                with self.assertRaises(DeviceSelectionError):
                    load_device_selection(path)

    def test_injection_of_extra_fields_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "prefs.json"
            obj = dict(version=1, camera_kind="", camera_value="",
                       printer_kind="", printer_value="", secret="unexpected")
            path.write_text(json.dumps(obj), encoding="utf-8")
            with self.assertRaises(DeviceSelectionError):
                load_device_selection(path)

    def test_invalid_queue_names_and_backend_are_rejected(self):
        for name in ("", "   ", "Queue\nTEST", " " + "printer",
                     "x" * 260):
            with self.subTest(name=name), self.assertRaises(DeviceSelectionError):
                stage_selection(DeviceSelection(), printer=("windows-spooler", name))
        with self.assertRaises(DeviceSelectionError):
            stage_selection(DeviceSelection(), printer=("cups-queue", "POS80"))


if __name__ == "__main__":
    unittest.main()
