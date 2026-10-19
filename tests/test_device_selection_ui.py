"""FEAT-008 B.2.1: selection Settings / controller mocks, no physical devices."""
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from photobooth.device_selection import DeviceSelection, DeviceSelectionError, load_device_selection
from photobooth.device_health import HealthCheck, HealthSnapshot, READY
from photobooth.hardware_adapters import DeviceDescriptor
from photobooth.printer import PrinterConfig


@unittest.skipUnless(os.environ.get("PHOTOBOOTH_TEST_GUI") == "1", "Kivy GUI tests opt-in")
class SelectionKivyTests(unittest.TestCase):
    def make_ui(self):
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        pending = []
        staged = []
        ui = PhotoBoothUI(
            KivyHost(lambda: None), get_templates(),
            on_health_refresh=pending.append,
            get_device_selection=lambda: DeviceSelection(),
            on_device_stage=lambda **kwargs: staged.append(kwargs) or "Tersimpan untuk restart.",
        )
        self.addCleanup(ui.dispose)
        return ui, pending, staged

    @staticmethod
    def snapshot(platform):
        devices = (
            DeviceDescriptor(
                "camera", "camera:active", "Configured camera index 0",
                "active-capture", platform, "ephemeral", "active-handle", (), "mock"
            ),
            DeviceDescriptor(
                "printer", "win-queue:POS80 test", "Print queue: POS80 test",
                "windows-spooler", platform, "queue-name",
                "queue-detected", (), "mock",
            ),
        )
        return HealthSnapshot(
            checked_at="2026-10-19T05:30:00+00:00",
            checks=tuple(HealthCheck(kind, READY, "mock") for kind in (
                "camera", "printer", "disk", "network", "media", "heartbeat"
            )),
            platform=platform, devices=devices,
        )

    def test_windows_queued_selection_does_not_call_runtime_devices(self):
        from kivy.uix.spinner import Spinner
        ui, pending, staged = self.make_ui()
        health = ui.show_health_settings()
        self.assertTrue(ui._health_select_button.disabled)
        pending.pop()(self.snapshot("windows"))
        self.assertFalse(ui._health_select_button.disabled)
        picker = ui.show_device_selection_settings()
        try:
            widgets = [item for item in picker.content.walk() if isinstance(item, Spinner)]
            self.assertEqual(len(widgets), 2)
            camera = next(x for x in widgets if any("Kamera OpenCV" in v for v in x.values))
            printer = next(x for x in widgets if any("POS80 test" in v for v in x.values))
            camera.text = "Kamera OpenCV indeks 2 (manual)"
            printer.text = "Windows queue: POS80 test"
            # The only effect of Save is the persistence callback.
            from kivy.uix.button import Button
            save = next(x for x in picker.content.walk()
                        if isinstance(x, Button) and x.text == "SIMPAN UNTUK RESTART")
            save.dispatch("on_release")
            self.assertEqual(staged, [{
                "camera": ("opencv-index", "2"),
                "printer": ("windows-spooler", "POS80 test"),
            }])
            self.assertEqual(ui.current_screen, "welcome")
        finally:
            picker.dismiss(animation=False)
            health.dismiss(animation=False)

    def test_android_offers_no_unimplemented_hardware(self):
        from kivy.uix.spinner import Spinner
        ui, pending, staged = self.make_ui()
        health = ui.show_health_settings()
        pending.pop()(self.snapshot("android"))
        picker = ui.show_device_selection_settings()
        try:
            options = [s.values for s in picker.content.walk() if isinstance(s, Spinner)]
            self.assertEqual(len(options), 2)
            self.assertTrue(all(set(x) == {"TIDAK DIUBAH", "KEMBALI KE DEFAULT"}
                                for x in options))
        finally:
            picker.dismiss(animation=False)
            health.dismiss(animation=False)

    def test_closing_health_closes_selection_popup(self):
        ui, pending, staged = self.make_ui()
        health = ui.show_health_settings()
        pending.pop()(self.snapshot("windows"))
        picker = ui.show_device_selection_settings()
        self.assertIs(ui._device_pick_popup, picker)
        health.dismiss(animation=False)
        self.assertIsNone(ui._health_popup)
        self.assertIsNone(ui._device_pick_popup)


@unittest.skipUnless(os.environ.get("PHOTOBOOTH_TEST_GUI") == "1", "Kivy GUI tests opt-in")
class SelectionControllerTests(unittest.TestCase):
    def make_controller(self, directory):
        from photobooth.app import PhotoBoothApp
        obj = PhotoBoothApp.__new__(PhotoBoothApp)
        obj.is_closing = False
        obj._device_selection_file = Path(directory) / "device_selection.json"
        obj._device_selection = DeviceSelection()
        obj._latest_health_snapshot = SimpleNamespace(devices=(
            DeviceDescriptor(
                "printer", "win-queue:POS80", "Print queue: POS80",
                "windows-spooler", "windows", "queue-name", "queue-detected", (), "mock",
            ),
            DeviceDescriptor(
                "camera", "v4l:by-id:usb-Cam-video-index0", "usb-Cam-video-index0",
                "v4l2", "linux", "udev-by-id", "node-detected", (), "mock",
            ),
        ))
        obj.printer = SimpleNamespace(config=PrinterConfig(lan_host="192.0.2.5"))
        obj._printer_settings_file = Path(directory) / "printer_settings.json"
        from photobooth.printer_settings import save_printer_config
        obj._save_printer_config = save_printer_config
        return obj

    def test_stage_windows_is_persisted_but_active_printer_is_unchanged(self):
        from photobooth.app import PhotoBoothApp
        with tempfile.TemporaryDirectory() as temp, (
            patch("photobooth.app.platform_family", return_value="windows")
        ):
            controller = self.make_controller(temp)
            message = PhotoBoothApp._stage_device_selection(
                controller, camera=("opencv-index", "2"),
                printer=("windows-spooler", "POS80"),
            )
            self.assertIn("restart", message.lower())
            self.assertEqual(controller.printer.config.lan_host, "192.0.2.5")
            selection = load_device_selection(controller._device_selection_file)
            self.assertEqual(selection.camera_value, "2")
            self.assertEqual(selection.printer_value, "POS80")

    def test_printer_cannot_stage_unseen_or_other_platform_queue(self):
        from photobooth.app import PhotoBoothApp
        with tempfile.TemporaryDirectory() as temp:
            controller = self.make_controller(temp)
            with patch("photobooth.app.platform_family", return_value="windows"):
                with self.assertRaises(DeviceSelectionError):
                    PhotoBoothApp._stage_device_selection(
                        controller, printer=("windows-spooler", "OTHER"))
            with patch("photobooth.app.platform_family", return_value="linux"):
                with self.assertRaises(DeviceSelectionError):
                    PhotoBoothApp._stage_device_selection(
                        controller, printer=("windows-spooler", "POS80"))
            self.assertFalse(controller._device_selection_file.exists())

    def test_legacy_printer_save_clears_pending_queue_without_affecting_camera(self):
        from photobooth.app import PhotoBoothApp
        from photobooth.device_selection import stage_selection, save_device_selection
        with tempfile.TemporaryDirectory() as temp:
            controller = self.make_controller(temp)
            selection = stage_selection(
                DeviceSelection(), camera=("opencv-index", "3"),
                printer=("windows-spooler", "POS80"),
            )
            save_device_selection(controller._device_selection_file, selection)
            controller._device_selection = selection
            cfg = PrinterConfig(windows_printer_name="New manual queue")
            PhotoBoothApp._configure_printer(controller, cfg)
            result = load_device_selection(controller._device_selection_file)
            self.assertEqual(result.printer_kind, "")
            self.assertEqual(result.camera_value, "3")
            self.assertEqual(controller.printer.config.windows_printer_name,
                             "New manual queue")


if __name__ == "__main__":
    unittest.main()
