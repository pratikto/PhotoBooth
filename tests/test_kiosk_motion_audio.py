"""Pointer-level kiosk checks for the visual tutorial, audio and order preview.

Camera frames, audio handles, payment, printer and Drive are all fixtures. These
checks use real Kivy layouts and input dispatch rather than invoking cart
callbacks directly and pretending that their touch targets were reachable.
"""

import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch


@unittest.skipUnless(os.environ.get("PHOTOBOOTH_TEST_GUI") == "1", "GUI checks are opt-in")
class KioskInteractionTests(unittest.TestCase):
    def setUp(self):
        from kivy.core.window import Window
        from photobooth.audio import AudioManager, SOUND_NAMES
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        from test_audio import FakeSound
        self.original_size = Window.size
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        with patch.dict(os.environ, {"PHOTOBOOTH_AUDIO": "1"}):
            self.audio = AudioManager(Path(self.directory.name) / "audio")
        self.audio._sounds = {name: FakeSound() for name in SOUND_NAMES}
        self.audio._apply_levels()
        self.capture_actions = []
        callbacks = {name: lambda: None for name in
                     ("on_home_start", "on_retake", "on_accept_session", "on_next_session", "on_finish")}
        callbacks["on_capture"] = lambda: self.capture_actions.append(True)
        callbacks["on_select_photo"] = lambda index: None
        callbacks["on_start"] = lambda order: None
        self.ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(),
                               audio_manager=self.audio, **callbacks)
        Window.add_widget(self.ui.shell)
        self.ui.show_welcome(True, "Ready")
        self.settle()

    def tearDown(self):
        from kivy.core.window import Window
        self.ui.dispose()
        Window.remove_widget(self.ui.shell)
        Window.size = self.original_size

    def settle(self, seconds=.35):
        from kivy.base import EventLoop
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            EventLoop.idle()
        EventLoop.idle()
        EventLoop.idle()

    def tap(self, widget):
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.input.motionevent import MotionEvent
        class Pointer(MotionEvent):
            def depack(self, args):
                self.sx, self.sy = args
                self.profile = ["pos"]
                super().depack(args)
        x, y = widget.to_window(*widget.center)
        pointer = Pointer("kiosk-ui-test", str(id(widget)),
                          (x / Window.width, y / Window.height), is_touch=True)
        EventLoop.post_dispatch_input("begin", pointer)
        EventLoop.post_dispatch_input("end", pointer)
        self.settle()

    def open_audio_settings_from_header(self):
        """Exercise the actual two-step Settings menu instead of bypassing it.

        Current production UX opens a general Settings popup from the gear
        icon; the operator must then select PENGATURAN AUDIO. Historical tests
        incorrectly expected the audio sliders immediately after the gear.
        Real pointer dispatch verifies both accessible controls.
        """
        from kivy.core.window import Window
        from kivy.uix.button import Button
        from kivy.uix.popup import Popup

        self.tap(self.ui.settings_button)
        menus = [
            widget for widget in Window.children
            if isinstance(widget, Popup) and widget.title == "Pengaturan Meong"
        ]
        self.assertEqual(len(menus), 1, "Gear must open the Settings menu")
        audio_options = [
            widget for widget in menus[0].content.walk()
            if isinstance(widget, Button) and widget.text == "PENGATURAN AUDIO"
        ]
        self.assertEqual(len(audio_options), 1)
        self.tap(audio_options[0])
        self.assertTrue(self.ui.audio_settings_open)
        self.assertEqual(self.ui._audio_popup.title, "Suara")

    def test_tutorial_uses_four_distinct_visual_steps_and_retires_its_clock(self):
        self.assertEqual([item.kind for item in self.ui.welcome_steps],
                         ["frames", "pay", "camera", "result"])
        scope = self.ui._motion
        phase = self.ui.welcome_steps[0].phase
        self.settle()
        self.assertNotEqual(self.ui.welcome_steps[0].phase, phase)
        self.ui.show_template_selection(True, "Ready")
        self.assertTrue(scope.retired)
        self.assertIsNone(scope._event)
        self.assertFalse(scope.widgets)

    def test_order_titles_animate_to_their_receipt_without_changing_quantities(self):
        from kivy.core.window import Window
        for size in ((800, 600), (1200, 800)):
            with self.subTest(size=size):
                Window.size = size
                self.ui.show_template_selection(True, "Ready")
                first, target = self.ui.templates[0], self.ui.templates[7]
                self.ui._change_quantity(first.template_id, 1)
                self.ui._change_quantity(target.template_id, 2)
                self.settle()
                before = dict(self.ui.quantities)
                row = self.ui.order_rows[target.template_id]
                # Storage polling keeps the original touch target attached.
                self.ui.set_storage_status(True, "Still ready")
                self.assertIs(self.ui.order_rows[target.template_id], row)
                self.tap(row)
                self.settle(.5)
                self.assertEqual(self.ui.template_carousel.index, 7)
                self.assertEqual(self.ui.template_name.text, target.name)
                self.assertEqual(self.ui.quantities, before)
                self.assertEqual(self.ui.cart_total.text, "Rp25.000")
                left, right = self.ui.carousel_previous, self.ui.carousel_next
                carousel = self.ui.template_carousel
                self.assertLess(left.center_x, carousel.x)
                self.assertGreater(right.center_x, carousel.right)
                self.assertAlmostEqual(left.center_y, carousel.center_y, delta=2)
                self.assertAlmostEqual(right.center_y, carousel.center_y, delta=2)

    def test_retired_order_rows_and_requested_focus_cannot_change_a_later_page(self):
        self.ui.show_template_selection(True, "Ready")
        key = self.ui.templates[7].template_id
        self.ui._change_quantity(key, 1)
        old_row = self.ui.order_rows[key]
        self.ui.template_carousel.request_index(7)
        old_carousel = self.ui.template_carousel
        self.ui.show_welcome(True, "New customer")
        old_row.dispatch("on_release")
        self.settle()
        self.assertTrue(old_carousel.disabled)
        self.assertIsNone(old_carousel._focus_event)
        self.assertEqual(self.ui.current_screen, "welcome")
        self.ui.show_template_selection(True, "Ready")
        self.assertEqual(self.ui.template_carousel.index, 0)
        self.assertEqual(self.ui.cart_total.text, "Rp0")

    def test_settings_persist_four_gains_without_modifying_a_capture_or_order(self):
        from photobooth.audio import AudioLevels
        from PIL import Image
        self.ui.show_template_selection(True, "Ready")
        self.ui._change_quantity(self.ui.templates[0].template_id, 2)
        before = dict(self.ui.quantities)
        self.open_audio_settings_from_header()
        self.assertEqual(set(self.ui.audio_sliders), {"music", "buttons", "effects", "ads"})
        self.ui.audio_sliders["music"].value = .13
        self.ui.audio_sliders["buttons"].value = 0
        self.ui.audio_sliders["effects"].value = .42
        self.ui.audio_sliders["ads"].value = .37
        self.ui._audio_popup.dismiss(animation=False)
        self.settle(.1)
        self.assertFalse(self.ui.audio_settings_open)
        self.assertEqual(self.ui.quantities, before)
        self.assertEqual(AudioLevels.load(self.audio.settings_path), self.audio.levels)
        self.ui.show_capture("Session", 0, Image.new("RGB", (640, 480), "pink"))
        self.ui.set_countdown(5)
        self.open_audio_settings_from_header()
        self.assertEqual(self.ui.countdown.text, "5")
        self.assertTrue(self.ui.capture_button.disabled)
        self.assertFalse(self.capture_actions)

    def test_count_cues_are_one_per_tick_and_a_saved_photo_has_one_shutter(self):
        from PIL import Image
        self.ui.show_capture("Session", 0, Image.new("RGB", (640, 480), "pink"))
        count = self.audio._sounds["count"]
        shutter = self.audio._sounds["shutter"]
        for seconds in (5, 5, 4, 4, 3, 2, 1):
            self.ui.set_countdown(seconds)
        self.assertEqual(count.plays, 5)
        self.assertEqual(shutter.plays, 0)
        self.ui.notify_photo_captured()
        self.assertEqual(shutter.plays, 1)
        old_dial = self.ui.countdown_dial
        self.ui.show_welcome(True, "Ready")
        self.assertEqual(self.audio._sounds["music"].volume, self.audio.levels.music)
        self.assertIsNone(self.ui.countdown_dial)
        self.settle()
        self.assertEqual(count.plays, 5)
        self.assertIsNotNone(old_dial)

    def test_explicit_music_preview_restarts_for_audition_and_reports_mute_state(self):
        """Manual UJI MUSIK must restart audio, unlike ordinary background music.

        The owner explicitly requested a useful speaker test after a mixer
        reported 'playing' without audible sound. Each operator UJI tap must
        re-issue playback; passive page transitions must not do so.
        """
        self.open_audio_settings_from_header()
        self.assertEqual(set(self.ui.audio_test_buttons), {"music", "buttons", "effects"})
        song = self.audio._sounds["music"]
        baseline = song.plays
        self.tap(self.ui.audio_test_buttons["music"])
        self.assertEqual(song.plays, baseline + 1)
        self.assertIn("Musik menyala", self.ui.audio_status_label.text)
        self.tap(self.ui.audio_test_buttons["music"])
        self.assertEqual(song.plays, baseline + 2)
        self.assertIn("musik diulang", self.ui.audio_status_label.text)
        self.ui.audio_sliders["music"].value = 0
        self.settle()
        self.assertEqual(song.state, "stop")
        self.assertIn("Musik dibisukan", self.ui.audio_status_label.text)
        self.ui._audio_popup.dismiss(animation=False)
        self.settle(.1)
        self.assertFalse(self.ui.audio_test_buttons)

    def test_static_gear_pixels_are_painted_inside_the_header_button(self):
        """Geometry alone misses a stale canvas drawn at the previous y=0."""
        from PIL import Image
        import numpy as np
        from kivy.core.window import Window
        path = Path(self.directory.name) / "header.png"
        self.ui.shell.export_to_png(str(path))
        button = self.ui.settings_button
        x, y = button.to_window(*button.pos)
        with Image.open(path) as source:
            pixels = np.asarray(source.convert("RGB"))
        patch_pixels = pixels[round(Window.height - y - button.height):round(Window.height - y),
                              round(x):round(x + button.width)]
        blue_ink = ((patch_pixels[:, :, 0] < 100) & (patch_pixels[:, :, 1] < 160)
                    & (patch_pixels[:, :, 2] > 180))
        self.assertGreater(int(np.count_nonzero(blue_ink)), 40)

    def test_last_order_title_is_reachable_by_scrolling_and_keeps_the_same_total(self):
        """All twelve rows stay usable even though they cannot all fit at once."""
        from kivy.core.window import Window
        Window.size = (800, 600)
        self.ui.show_template_selection(True, "Ready")
        for template in self.ui.templates:
            self.ui._change_quantity(template.template_id, 1)
        scroll = self.ui.order_items.parent
        scroll.scroll_y = 0
        self.settle()
        last = self.ui.templates[-1]
        row = self.ui.order_rows[last.template_id]
        x, y = row.to_window(*row.pos)
        sx, sy = scroll.to_window(*scroll.pos)
        self.assertGreaterEqual(y, sy - 1)
        self.assertLessEqual(y + row.height, sy + scroll.height + 1)
        self.tap(row)
        self.settle(.5)
        self.assertEqual(self.ui.template_carousel.index, len(self.ui.templates) - 1)
        self.assertEqual(self.ui.cart_total.text, "Rp120.000")

    def test_settings_remain_in_the_header_on_all_six_screens(self):
        from PIL import Image
        path = Path(self.directory.name) / "photo.png"
        Image.new("RGB", (640, 480), "pink").save(path)
        steps = (
            lambda: self.ui.show_welcome(True, "Ready"),
            lambda: self.ui.show_template_selection(True, "Ready"),
            lambda: self.ui.show_payment("Frame × 1", 1, 5000, lambda: None, lambda: None),
            lambda: self.ui.show_capture("Session", 0, None),
            lambda: self.ui.show_review([path] * 3, "Session", None, True),
            lambda: self.ui.show_result(path, "Session", "PB001_00000001", False),
        )
        settings = self.ui.settings_button
        for show in steps:
            show()
            self.settle(.1)
            self.assertIs(self.ui.settings_button, settings)
            self.assertIs(settings.parent, self.ui._header_row)
            self.open_audio_settings_from_header()
            self.ui._audio_popup.dismiss(animation=False)
            self.settle(.1)


if __name__ == "__main__":
    unittest.main()
