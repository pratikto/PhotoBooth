"""FEAT-008 Stage B: real Kivy widget and controller worker regressions.

Only GUI test mode runs these checks; no camera, printer, Drive or remote
endpoint is accessed. The controller thread is replaced with a test double.
"""

import os
from pathlib import Path
from types import SimpleNamespace
import threading
import unittest
from unittest.mock import Mock, patch

from photobooth.device_health import HealthCheck, HealthSnapshot, READY, WARNING, UNKNOWN


@unittest.skipUnless(os.environ.get("PHOTOBOOTH_TEST_GUI") == "1", "Kivy GUI tests opt-in")
class DeviceHealthGuiTests(unittest.TestCase):
    def make_ui(self, callback=None):
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        kwargs = {} if callback is None else {"on_health_refresh": callback}
        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(), **kwargs)
        self.addCleanup(ui.dispose)
        return ui

    def snapshot(self):
        names = ("camera", "printer", "disk", "network", "media", "heartbeat")
        statuses = (READY, READY, WARNING, READY, UNKNOWN, READY)
        return HealthSnapshot(
            checked_at="2026-10-19T03:00:00+00:00",
            checks=tuple(
                HealthCheck(name, status, f"Diagnostic for {name} (not certified)")
                for name, status in zip(names, statuses)
            ),
        )

    def test_settings_has_operator_health_button_and_existing_routes(self):
        ui = self.make_ui()
        popup = ui.show_settings_menu()
        self.addCleanup(lambda: popup.dismiss(animation=False))
        captions = [widget.text for widget in popup.content.children]
        self.assertEqual(len(captions), 4)
        self.assertIn("PENGATURAN AUDIO", captions)
        self.assertIn("PENGATURAN PRINTER", captions)
        self.assertIn("DEVICE HEALTH", captions)
        self.assertIn("TUTUP", captions)

    def test_open_is_async_refresh_and_populates_all_six_rows(self):
        from kivy.core.window import Window
        pending = []
        ui = self.make_ui(lambda callback: pending.append(callback))
        previous_screen = ui.current_screen
        previous_size = Window.size
        popup = ui.show_health_settings()
        self.addCleanup(lambda: popup.dismiss(animation=False))
        self.assertEqual(ui.current_screen, previous_screen)
        self.assertEqual(len(pending), 1)
        self.assertTrue(ui._health_refresh_button.disabled)
        self.assertEqual(len(ui._health_labels), 6)

        pending.pop()(self.snapshot())
        self.assertFalse(ui._health_refresh_button.disabled)
        self.assertIn("READY", ui._health_labels["printer"][0].text)
        self.assertIn("PERHATIAN", ui._health_labels["disk"][0].text)
        self.assertIn("BELUM DIKETAHUI", ui._health_labels["media"][0].text)
        self.assertIn("Diagnostic for media", ui._health_labels["media"][1].text)
        self.assertEqual(Window.size, previous_size)
        self.assertLessEqual(popup.width, Window.width)
        self.assertLessEqual(popup.height, Window.height)

    def test_refresh_does_not_start_parallel_requests(self):
        pending = []
        ui = self.make_ui(lambda cb: pending.append(cb))
        popup = ui.show_health_settings()
        self.addCleanup(lambda: popup.dismiss(animation=False))
        self.assertEqual(len(pending), 1)
        ui._health_refresh_button.dispatch("on_release")
        self.assertEqual(len(pending), 1)
        pending.pop()(self.snapshot())
        ui._health_refresh_button.dispatch("on_release")
        self.assertEqual(len(pending), 1)
        self.assertTrue(ui._health_refresh_button.disabled)

    def test_late_worker_result_cannot_touch_closed_or_reopened_panel(self):
        pending = []
        ui = self.make_ui(lambda cb: pending.append(cb))
        old_popup = ui.show_health_settings()
        old_callback = pending.pop()
        old_popup.dismiss(animation=False)
        self.assertIsNone(ui._health_popup)
        second_popup = ui.show_health_settings()
        self.addCleanup(lambda: second_popup.dismiss(animation=False))
        latest_callback = pending.pop()
        old_callback(self.snapshot())
        self.assertTrue(ui._health_refresh_button.disabled)
        self.assertIn("MEMERIKSA", ui._health_labels["printer"][0].text)
        latest_callback(self.snapshot())
        self.assertFalse(ui._health_refresh_button.disabled)
        self.assertIn("READY", ui._health_labels["printer"][0].text)

    def test_missing_controller_callback_and_worker_failure_are_recoverable(self):
        ui = self.make_ui()
        popup = ui.show_health_settings()
        self.addCleanup(lambda: popup.dismiss(animation=False))
        self.assertFalse(ui._health_refresh_button.disabled)
        self.assertIn("BELUM DIKETAHUI", ui._health_labels["camera"][0].text)
        self.assertIn("Tidak ada hasil", ui._health_labels["camera"][1].text)

    def test_existing_kiosk_tick_provides_heartbeat_without_new_timer(self):
        ui = self.make_ui()
        self.assertIsNone(ui._health_last_tick)
        with patch("photobooth.ui_kiosk.time.monotonic", return_value=123.456):
            ui._kiosk_tick()
        self.assertEqual(ui._health_last_tick, 123.456)


@unittest.skipUnless(os.environ.get("PHOTOBOOTH_TEST_GUI") == "1", "Kivy GUI tests opt-in")
class HealthWorkerControllerTests(unittest.TestCase):
    def make_controller(self):
        from photobooth.app import PhotoBoothApp
        from photobooth.printer import PrinterConfig
        obj = PhotoBoothApp.__new__(PhotoBoothApp)
        obj.is_closing = False
        obj._health_probe_lock = threading.Lock()
        obj._print_lock = threading.Lock()
        obj._print_jobs_in_flight = set()
        obj.camera = SimpleNamespace(capture=None)
        obj.printer = SimpleNamespace(config=PrinterConfig())
        obj.photos_root = Path("synthetic-photos")
        obj.ui = SimpleNamespace(
            ad_catalog=SimpleNamespace(path=Path("offline-playlist.json"), items=[]),
            _health_last_tick=123.45,
        )
        queued = []
        obj.root = SimpleNamespace(after=lambda delay, callback: queued.append((delay, callback)))
        return obj, queued

    def test_worker_does_not_block_ui_or_run_checks_inline(self):
        from photobooth.app import PhotoBoothApp
        obj, queued = self.make_controller()
        callbacks = []
        made = []

        class SyntheticThread:
            def __init__(self, *, target, name, daemon):
                self.target = target
                self.name = name
                self.daemon = daemon
                made.append(self)

            def start(self):
                self.started = True

        snapshot = SimpleNamespace(checks=(), checked_at="2026-10-19T03:00:00+00:00")
        with (
            patch("photobooth.app.threading.Thread", SyntheticThread),
            patch("photobooth.app.collect_health_snapshot", return_value=snapshot) as collect,
        ):
            PhotoBoothApp._refresh_device_health(obj, callbacks.append)
            self.assertTrue(made[0].started)
            self.assertTrue(made[0].daemon)
            self.assertEqual(made[0].name, "meong-device-health")
            collect.assert_not_called()
            self.assertEqual(queued, [])
            # A second request while the first worker lives cannot start
            # another expensive probe.
            PhotoBoothApp._refresh_device_health(obj, callbacks.append)
            self.assertEqual(len(made), 1)
            self.assertEqual(len(queued), 1)
            queued.pop()[1]()
            self.assertEqual(callbacks, [None])

            made[0].target()
            collect.assert_called_once_with(
                camera=obj.camera,
                printer_config=obj.printer.config,
                photo_directory=obj.photos_root,
                ad_catalog=obj.ui.ad_catalog,
                last_heartbeat=123.45,
                printer_busy=False,
            )
            self.assertEqual(len(queued), 1)
            self.assertEqual(callbacks, [None])
            queued.pop()[1]()
            self.assertEqual(callbacks, [None, snapshot])
            self.assertFalse(obj._health_probe_lock.locked())

    def test_inflight_print_is_captured_on_main_thread(self):
        from photobooth.app import PhotoBoothApp
        obj, queued = self.make_controller()
        obj._print_jobs_in_flight.add("active-job")
        workers = []

        class SyntheticThread:
            def __init__(self, *, target, **_kwargs):
                workers.append(target)
            def start(self):
                pass

        with (
            patch("photobooth.app.threading.Thread", SyntheticThread),
            patch("photobooth.app.collect_health_snapshot") as collect,
        ):
            PhotoBoothApp._refresh_device_health(obj, lambda _: None)
            workers.pop()()
            self.assertTrue(collect.call_args.kwargs["printer_busy"])
            self.assertEqual(len(queued), 1)
            queued.pop()[1]()

    def test_closing_during_worker_discards_late_result(self):
        from photobooth.app import PhotoBoothApp
        obj, queued = self.make_controller()
        made = []

        class SyntheticThread:
            def __init__(self, *, target, **_kwargs):
                made.append(target)
            def start(self):
                pass

        with (
            patch("photobooth.app.threading.Thread", SyntheticThread),
            patch("photobooth.app.collect_health_snapshot", return_value=None),
        ):
            PhotoBoothApp._refresh_device_health(obj, lambda _: None)
            obj.is_closing = True
            made.pop()()
            self.assertEqual(queued, [])
            self.assertFalse(obj._health_probe_lock.locked())


if __name__ == "__main__":
    unittest.main()
