"""Opt-in GUI regression checks using real Kivy widgets and OpenGL textures.

Run on a desktop with PHOTOBOOTH_TEST_GUI=1, or use SDL_VIDEODRIVER=offscreen
on a machine with Mesa offscreen support. Normal storage tests do not require
an available display. These tests never contact Drive or open a real camera.
"""
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class KivyFlowTests(unittest.TestCase):
    def test_overview_composites_alpha_without_altering_source_renders(self):
        """Contact sheets must not expose RGB hidden under transparent corners.

        Widget exports have an alpha channel outside the rounded shell. Pasting
        RGBA directly into an RGB sheet discards that alpha and paints its hidden
        black channels instead. Include partial alpha and ordinary RGB input so
        the evidence stays faithful without rewriting any full-size screenshot.
        """
        from PIL import Image, ImageDraw
        from tools.render_gui import overview

        paper = (243, 245, 250)
        ink = (26, 48, 46)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for width, height in ((1200, 800), (800, 600)):
                with self.subTest(size=(width, height)):
                    source = Image.new('RGBA', (width, height), ink + (255,))
                    draw = ImageDraw.Draw(source)
                    draw.rectangle((0, 0, width // 4, height // 4), fill=(0, 0, 0, 0))
                    draw.rectangle((0, height // 2, width // 4, height), fill=ink + (128,))
                    alpha_path = root / f'alpha-{width}x{height}.png'
                    rgb_path = root / f'rgb-{width}x{height}.png'
                    source.save(alpha_path)
                    Image.new('RGB', (width, height), ink).save(rgb_path)
                    original_bytes = (alpha_path.read_bytes(), rgb_path.read_bytes())

                    overview(root, (width, height), screens=('alpha', 'rgb'))

                    with Image.open(root / f'overview-{width}x{height}.png') as sheet:
                        self.assertEqual(sheet.mode, 'RGB')
                        self.assertEqual(sheet.size, (width, height // 2 + 30))
                        self.assertEqual(sheet.getpixel((10, 40)), paper)
                        # Sample well away from resampled edges. Partial alpha
                        # must blend with paper, not become opaque dark ink.
                        expected = Image.alpha_composite(
                            Image.new('RGBA', (1, 1), paper + (255,)),
                            Image.new('RGBA', (1, 1), ink + (128,))).convert('RGB').getpixel((0, 0))
                        self.assertEqual(sheet.getpixel((10, 30 + height * 3 // 8)), expected)
                        self.assertEqual(sheet.getpixel((width // 4, 40)), ink)
                        self.assertEqual(sheet.getpixel((width // 2 + 10, 40)), ink)
                    self.assertEqual((alpha_path.read_bytes(), rgb_path.read_bytes()), original_bytes)

    def test_status_details_follow_resize_without_rebuilding_the_cart(self):
        """A message between desktop widths must not flicker or reserve a gap."""
        from kivy.base import EventLoop
        from kivy.core.text import Label as CoreLabel
        from kivy.core.window import Window
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI

        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(), on_start=lambda *_: None)
        Window.add_widget(ui.shell)
        original_size = Window.size

        def settle():
            for _ in range(8):
                EventLoop.idle()

        try:
            ui.show_template_selection(True, 'Ready', quantities={'template_a': 2})
            widths = []
            for size in ((800, 600), (1200, 800)):
                Window.size = size
                settle()
                widths.append(ui._footer_row.width - ui.camera_badge.width - ui._footer_row.spacing)
            font = CoreLabel(font_name=ui.status.font_name, font_size=ui.status.font_size)
            target = sum(widths) / 2
            message = 'Drive siap: ' + 'n' * round((target - font.get_extents('Drive siap: ')[0])
                                                   / font.get_extents('n')[0])
            start = ui.start_button
            ui.set_status(message)
            for size, needed in (((1200, 800), False), ((800, 600), True), ((1200, 800), False)):
                Window.size = size
                settle()
                self.assertEqual(ui.status_details.parent is ui._footer_row, needed)
                self.assertEqual(ui.status.is_shortened, needed)
                settle()
                self.assertEqual(ui.status_details.parent is ui._footer_row, needed)
                self.assertIs(ui.start_button, start)
                self.assertEqual(ui.quantities['template_a'], 2)
                self.assertEqual(ui.cart_total.text, 'Rp15.000')
        finally:
            Window.remove_widget(ui.shell)
            Window.size = original_size

    def test_long_footer_status_opens_complete_scrollable_details_without_losing_cart(self):
        """Long diagnostics must not be silently clipped or erase an unpaid order.

        Keep the full public status text for controller recovery, but elide its
        visual summary. Open the real popup through the persistent footer action,
        scroll its complete message, close it, and recover storage on the same
        cart. An unusually long string also guards against measuring a massive
        single-line GPU texture just to decide whether details are needed.
        """
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.uix.button import Button
        from kivy.uix.popup import Popup
        from kivy.uix.scrollview import ScrollView
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI

        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(), on_start=lambda *_: None)
        Window.add_widget(ui.shell)
        original_size = Window.size
        message = ('Slot Drive perlu diperiksa: Fixture verification failed. '
                   'Local photos are retained; no real service was contacted. ') * 40

        def settle():
            for _ in range(8):
                EventLoop.idle()

        popup = None
        try:
            for size in ((1200, 800), (800, 600)):
                with self.subTest(size=size):
                    Window.size = size
                    ui.show_template_selection(True, message, storage_ready=False,
                                               quantities={'template_a': 2})
                    start = ui.start_button
                    settle()
                    self.assertEqual(ui.status.text, message)
                    self.assertTrue(ui.status.is_shortened, 'Long status is cropped instead of elided')
                    self.assertIs(ui.status_details.parent, ui._footer_row)
                    self.assertFalse(ui.status_details.disabled)
                    self.assertTrue(start.disabled)
                    self.assertEqual(ui.cart_total.text, 'Rp15.000')
                    ui.status_details.dispatch('on_release')
                    settle()
                    popup = next(w for w in Window.children if isinstance(w, Popup))
                    self.addCleanup(popup.dismiss, animation=False)
                    scroll = next(w for w in popup.content.walk() if isinstance(w, ScrollView))
                    paragraph = scroll.children[0]
                    self.assertEqual(paragraph.text, message)
                    self.assertGreater(paragraph.height, scroll.height)
                    scroll.scroll_y = 0
                    settle()
                    # ScrollView translates its viewport instead of changing
                    # the paragraph's local y. Compare window coordinates.
                    self.assertAlmostEqual(paragraph.to_window(*paragraph.pos)[1],
                                           scroll.to_window(*scroll.pos)[1], delta=1)
                    close = next(w for w in popup.content.walk() if isinstance(w, Button))
                    close.dispatch('on_release')
                    # Dismissal is animated. Wait for its actual completion
                    # rather than assuming eight frames always exceed 100ms.
                    for _ in range(40):
                        EventLoop.idle()
                        if popup.parent is None:
                            break
                    self.assertIsNone(popup.parent)
                    popup = None
                    ui.set_storage_status(True, 'Drive siap')
                    settle()
                    self.assertIsNone(ui.status_details.parent)
                    self.assertTrue(ui.status_details.disabled)
                    self.assertFalse(ui.status.is_shortened)
                    self.assertIs(ui.start_button, start)
                    self.assertFalse(start.disabled)
                    self.assertEqual(ui.quantities['template_a'], 2)
        finally:
            if popup is not None:
                popup.dismiss(animation=False)
            Window.remove_widget(ui.shell)
            Window.size = original_size

    def test_disabled_labels_are_readable_and_recovery_restores_enabled_palette(self):
        """Read the painted label colors, including Kivy's disabled background.

        Retake-used captions still convey which photo was replaced even though
        their buttons cannot be pressed. Waiting-camera actions also need a
        readable label. Check both desktop sizes, then restore readiness and a
        nonzero quantity to verify both enabled button variants regain their
        original style without changing any callback or quantity gate.
        """
        from PIL import Image
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.uix.button import Button
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI, SAGE, SOFT, WHITE
        from tools.render_gui import button_contrast

        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(),
                          on_capture=lambda: None, on_select_photo=lambda *_: None,
                          on_retake=lambda: None, on_accept_session=lambda: None,
                          on_start=lambda *_: None)
        Window.add_widget(ui.shell)
        original_size = Window.size

        def settle():
            for _ in range(6):
                EventLoop.idle()

        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                raw = root / 'synthetic.png'
                Image.new('RGB', (640, 480), '#a7b8aa').save(raw)
                screenshot = root / 'screen.png'
                for size in ((1200, 800), (800, 600)):
                    Window.size = size
                    for screen in ('capture-waiting', 'review-used', 'templates-empty'):
                        with self.subTest(size=size, screen=screen):
                            ui.set_camera_status(True)
                            if screen == 'capture-waiting':
                                ui.show_capture('Sesi 1 dari 2', 1, None)
                                ui.set_camera_status(False)
                                controls = [ui.capture_button]
                            elif screen == 'review-used':
                                ui.show_review([raw] * 3, 'Sesi 1 dari 2', 1, False)
                                controls = [w for w in ui.content.walk()
                                            if isinstance(w, Button) and w.disabled]
                            else:
                                ui.show_template_selection(True, 'Ready')
                                controls = [ui.start_button, ui.quantity_buttons[ui.templates[0].template_id][0]]
                            settle()
                            ui.shell.export_to_png(str(screenshot))
                            for button in controls:
                                measured = button_contrast(screenshot, button)
                                self.assertGreaterEqual(measured['ratio'], 4.5, measured)
                            if screen == 'capture-waiting':
                                capture = ui.capture_button
                                ui.set_camera_status(True)
                                ui.set_capture_enabled(True)
                                self.assertIs(ui.capture_button, capture)
                                self.assertFalse(capture.disabled)
                                self.assertEqual(tuple(capture.background_color), SAGE)

                    ui.set_camera_status(True)
                    key = ui.templates[0].template_id
                    minus, plus = ui.quantity_buttons[key]
                    plus.dispatch('on_release')
                    self.assertFalse(minus.disabled)
                    self.assertEqual(tuple(minus.background_color), SOFT)
                    self.assertFalse(ui.start_button.disabled)
                    self.assertEqual(tuple(ui.start_button.background_color), WHITE)
                    minus.dispatch('on_release')
                    self.assertTrue(minus.disabled)
                    self.assertTrue(ui.start_button.disabled)
                    self.assertEqual(ui.quantities[key], 0)
        finally:
            Window.remove_widget(ui.shell)
            Window.size = original_size

    def test_review_pixels_match_the_saved_frame_before_and_after_retake(self):
        """Retake decisions must use the same crop as the accepted composition.

        Landscape, portrait, and square sources have deliberately different
        edge colors. Merely keeping a thumbnail inside its card would still
        pass if it showed edges that the saved result removes. Compare actual
        GPU pixels against each saved output frame at both desktop sizes, then
        repeat with a replacement photo and check that raw files stay intact.
        """
        from PIL import Image, ImageDraw
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.uix.image import Image as KivyImage
        from photobooth.catalog import compose_result, get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI

        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(),
                          on_select_photo=lambda *_: None, on_retake=lambda: None,
                          on_accept_session=lambda: None)
        Window.add_widget(ui.shell)
        original_size = Window.size
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                paths = []
                for index, size in enumerate(((640, 480), (480, 640), (480, 480), (800, 450))):
                    source = Image.new('RGB', size, '#74a186')
                    draw = ImageDraw.Draw(source)
                    width, height = size
                    draw.rectangle((0, 0, width // 8, height), fill='#d94444')
                    draw.rectangle((width * 7 // 8, 0, width, height), fill='#3c69c4')
                    draw.rectangle((0, 0, width, height // 8), fill='#ecc94b')
                    draw.rectangle((0, height * 7 // 8, width, height), fill='#9d5bc1')
                    draw.line((0, 0, width - 1, height - 1), fill='white', width=7)
                    path = root / f'raw-{index}.png'
                    source.save(path)
                    paths.append(path)
                raw_bytes = [path.read_bytes() for path in paths]
                for size in ((1200, 800), (800, 600)):
                    Window.size = size
                    for used in (False, True):
                        with self.subTest(size=size, retake_used=used):
                            final_paths = [paths[0], paths[3] if used else paths[1], paths[2]]
                            output = compose_result(final_paths, ui.templates[0], root / 'result.png',
                                                    'PB001_00000001', 'session_001')
                            saved_output = output.read_bytes()
                            ui.show_review(final_paths, 'Sesi 1 dari 1', 1, not used,
                                           template=ui.templates[0])
                            for _ in range(6):
                                EventLoop.idle()
                            thumbnails = sorted((widget for widget in ui.content.walk()
                                                 if isinstance(widget, KivyImage)), key=lambda w: w.x)
                            self.assertEqual(len(thumbnails), 3)
                            with Image.open(output) as result:
                                for index, widget in enumerate(thumbnails):
                                    frame = ui.templates[0].apertures[index]
                                    self.assertEqual(widget.texture.size, frame.size)
                                    shown = Image.frombytes('RGBA', widget.texture.size,
                                                            widget.texture.pixels).convert('RGB')
                                    saved = result.crop(frame.box)
                                    self.assertEqual(shown.tobytes(), saved.tobytes())
                            self.assertEqual(output.read_bytes(), saved_output)
                self.assertEqual([path.read_bytes() for path in paths], raw_bytes)
        finally:
            Window.remove_widget(ui.shell)
            Window.size = original_size

    def test_settings_audio_samples_have_no_extra_button_click(self):
        """Music and shutter auditions should not add the generic UI SFX."""
        from unittest.mock import call, patch
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI

        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(),
                         on_start=lambda *_: None)
        popup = None
        try:
            with (patch.object(ui.audio, "play") as play,
                  patch.object(ui.audio, "preview_music", return_value=True) as preview):
                popup = ui.show_audio_settings()
                ui.audio_test_buttons["music"].dispatch("on_release")
                self.assertIn("musik diulang", ui._audio_last_test)
                ui.audio_test_buttons["buttons"].dispatch("on_release")
                ui.audio_test_buttons["effects"].dispatch("on_release")
                preview.assert_called_once_with()
                self.assertEqual(play.call_args_list,
                                 [call("button"), call("shutter")])
        finally:
            if popup is not None:
                popup.dismiss(animation=False)
            ui.dispose()

    def test_button_callbacks_ignore_disabled_and_retired_screen_controls(self):
        """A queued release is checked again even after normal hit testing."""
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(), on_home_start=lambda: None)
        calls = []
        button = ui._button('Test action', lambda: calls.append('called'), enabled=False)
        button.dispatch('on_release')
        self.assertEqual(calls, [])
        button.disabled = False
        button.dispatch('on_release')
        self.assertEqual(calls, ['called'])
        ui.show_welcome(True, 'Ready')
        button.dispatch('on_release')
        self.assertEqual(calls, ['called'])

    def test_selected_template_cards_and_decrement_controls_follow_quantity(self):
        """Only nonzero quantities receive a selected outline and active minus."""
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(), on_start=lambda *_: None)
        ui.show_template_selection(True, 'Ready')
        key = ui.templates[0].template_id
        card = ui._template_cards[key]
        minus, plus = ui.quantity_buttons[key]
        self.assertFalse(card.selected)
        self.assertTrue(minus.disabled)
        plus.dispatch('on_release')
        plus.dispatch('on_release')
        self.assertTrue(card.selected)
        self.assertFalse(minus.disabled)
        self.assertEqual(ui.cart_total.text, 'Rp15.000')
        minus.dispatch('on_release')
        minus.dispatch('on_release')
        self.assertFalse(card.selected)
        self.assertTrue(minus.disabled)
        self.assertEqual(ui.cart_total.text, 'Rp0')
        minus.dispatch('on_release')
        self.assertEqual(ui.quantities[key], 0)

    def test_error_dialog_can_close_after_underlying_page_changes(self):
        """Modal dismissal must survive a controller's error-to-cart navigation."""
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.uix.button import Button
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(), on_home_start=lambda: None)
        Window.add_widget(ui.shell)
        popup = None
        try:
            ui.show_welcome(True, 'Ready')
            popup = ui.show_error('Test error', 'A simulated storage error; no Drive request was made.')
            for _ in range(8):
                EventLoop.idle()
            ui.show_template_selection(True, 'Order kept')
            close = next(widget for widget in popup.content.walk() if isinstance(widget, Button))
            close.dispatch('on_release')
            for _ in range(12):
                EventLoop.idle()
            self.assertIsNone(popup.parent)
        finally:
            if popup is not None:
                popup.dismiss(animation=False)
            Window.remove_widget(ui.shell)

    def test_pointer_taps_respect_camera_and_payment_submission_gates(self):
        """Send actual pointer events through Window, not on_release dispatch.

        This exercises hit testing, disabled-widget behavior, touch grabs, and
        callback delivery. The ordinary release-dispatch tests separately check
        stale queued callbacks that can outlive their original payment screen.
        """
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.input.motionevent import MotionEvent
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI

        class Pointer(MotionEvent):
            def depack(self, args):
                self.sx, self.sy = args
                self.profile = ['pos']
                super().depack(args)

        def settle():
            for _ in range(4):
                EventLoop.idle()

        taps = []
        callbacks = {key: lambda *args: None for key in (
            'on_start', 'on_select_photo', 'on_accept_session',
            'on_next_session', 'on_finish', 'on_close')}
        callbacks['on_home_start'] = lambda: taps.append('home')
        callbacks['on_capture'] = lambda: taps.append('capture')
        callbacks['on_retake'] = lambda: taps.append('retake')
        host = KivyHost(lambda: None)
        ui = PhotoBoothUI(host, get_templates(), **callbacks)
        original_size = Window.size
        Window.add_widget(ui.shell)

        def tap(widget):
            x, y = widget.to_window(*widget.center)
            event = Pointer('gui-test', str(len(taps)),
                            (x / Window.width, y / Window.height), is_touch=True)
            EventLoop.post_dispatch_input('begin', event)
            EventLoop.post_dispatch_input('end', event)
            settle()

        try:
            for size in ((1200, 800), (800, 600)):
                with self.subTest(size=size):
                    Window.size = size
                    taps.clear()
                    ui.show_welcome(False, 'Menunggu kamera')
                    settle()
                    tap(ui.home_start_button)
                    self.assertEqual(taps, [])
                    ui.set_camera_status(True)
                    tap(ui.home_start_button)
                    self.assertEqual(taps, ['home'])
                    ui.show_payment('Template 1 × 2', 2, 10000,
                                    lambda: taps.append('payment'), lambda: None)
                    settle()
                    ui.set_camera_status(False)
                    tap(ui.payment_confirm)
                    self.assertEqual(taps, ['home'])
                    ui.set_camera_status(True)
                    tap(ui.payment_confirm)
                    tap(ui.payment_confirm)
                    self.assertEqual(taps, ['home', 'payment'])
                    # Readiness changes cannot release a successful one-shot
                    # submission, even if its test callback keeps the page open.
                    ui.set_camera_status(False)
                    ui.set_camera_status(True)
                    tap(ui.payment_confirm)
                    self.assertEqual(taps, ['home', 'payment'])
                    ui.show_capture('Sesi 1 dari 2', 0, None)
                    settle()
                    ui.set_camera_status(False)
                    tap(ui.capture_button)
                    self.assertEqual(taps, ['home', 'payment'])
                    ui.set_camera_status(True)
                    ui.set_capture_enabled(True)
                    tap(ui.capture_button)
                    self.assertEqual(taps, ['home', 'payment', 'capture'])
        finally:
            Window.remove_widget(ui.shell)
            Window.size = original_size

    def test_desktop_layouts_keep_actions_photos_and_painted_qr_visible(self):
        """Check actual layout and rendered pixels at both supported desktop sizes.

        Texture-only assertions cannot detect a QR hidden by a ScrollView. Attach
        the UI to the real offscreen window, settle scheduled layouts, and decode
        the QR cropped from the exported screen. Camera/Drive are never opened.
        """
        from PIL import Image
        import cv2
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.uix.button import Button
        from kivy.uix.scrollview import ScrollView
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        from photobooth.catalog import get_templates, compose_result
        from photobooth.qr_code import create_qr_image

        callbacks = {key: lambda *args: None for key in (
            'on_home_start', 'on_start', 'on_capture', 'on_select_photo', 'on_retake',
            'on_accept_session', 'on_next_session', 'on_finish', 'on_close')}
        host = KivyHost(lambda: None)
        ui = PhotoBoothUI(host, get_templates(), **callbacks)
        Window.add_widget(ui.shell)
        original_size = Window.size

        def settle():
            # Kivy defers layout and text measurement; no blocking sleep or
            # artificial geometry replaces its layout and canvas callbacks.
            for _ in range(6):
                EventLoop.idle()

        def bounds(widget):
            x, y = widget.to_window(*widget.pos)
            return x, y, x + widget.width, y + widget.height

        def visible(widget):
            box = bounds(widget)
            self.assertGreater(widget.width, 0)
            self.assertGreater(widget.height, 0)
            parent = widget.parent
            while parent is not None and parent is not Window:
                # Only a ScrollView clips its descendants. Ordinary BoxLayout
                # ancestors may share absolute coordinates with their children.
                if isinstance(parent, ScrollView):
                    clip = bounds(parent)
                    self.assertGreaterEqual(box[0], clip[0] - 1)
                    self.assertGreaterEqual(box[1], clip[1] - 1)
                    self.assertLessEqual(box[2], clip[2] + 1)
                    self.assertLessEqual(box[3], clip[3] + 1)
                parent = parent.parent
            self.assertGreaterEqual(box[0], -1)
            self.assertGreaterEqual(box[1], -1)
            self.assertLessEqual(box[2], Window.width + 1)
            self.assertLessEqual(box[3], Window.height + 1)

        def painted_qr(widget, expected, output):
            visible(widget)
            ui.shell.export_to_png(str(output))
            pixels = cv2.imread(str(output))
            left, bottom, right, top = bounds(widget)
            crop = pixels[round(Window.height - top):round(Window.height - bottom),
                          round(left):round(right)]
            decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(crop)
            self.assertEqual(decoded, expected)

        url = 'https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz123456'
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / 'synthetic.png'
                frame = Image.new('RGB', (640, 480), '#d8dfd6')
                frame.save(path)
                result = compose_result([path] * 3, ui.templates[0], root / 'result.png',
                                        'PB001_00000001', 'session_001', url)
                for size in ((1200, 800), (800, 600)):
                    with self.subTest(size=size):
                        Window.size = size
                        ui.show_welcome(True, 'Drive siap')
                        settle()
                        for screen in ('welcome', 'templates', 'payment', 'capture', 'review', 'result'):
                            if screen == 'templates':
                                ui.show_template_selection(True, 'Drive siap')
                                for template in ui.templates:
                                    ui._change_quantity(template.template_id, 2)
                            elif screen == 'payment':
                                ui.show_payment('\n'.join(f'{t.name} × 2' for t in ui.templates),
                                                8, 40000, lambda: None, lambda: None)
                            elif screen == 'capture':
                                ui.show_capture('Sesi 1 dari 8 · Template 1', 1, frame)
                                ui.set_countdown(5)
                            elif screen == 'review':
                                ui.show_review([path] * 3, 'Sesi 1 dari 8', 1, True)
                            elif screen == 'result':
                                ui.show_result(result, 'Sesi 8 dari 8', 'PB001_00000001', False,
                                               60, create_qr_image(url), False,
                                               'Internet terputus. QR membuka folder tujuan; foto akan '
                                               'muncul setelah upload dilanjutkan.')
                            settle()
                            # Desktop panels must fit without a second outer
                            # scroll; gallery/item lists retain their own scroll.
                            stage = next(w for w in ui.content.children if isinstance(w, ScrollView))
                            self.assertLessEqual(stage.children[0].height, stage.height + 1, screen)
                            if screen == 'templates':
                                visible(ui.cart_total)
                                self.assertEqual(ui.cart_total.text,
                                                 'Rp' + f'{len(ui.templates) * 15000:,}'.replace(',', '.'))
                                # Each order title is now a real 52dp button
                                # within the independently scrollable cart.
                                self.assertEqual(len(ui.order_rows), len(ui.templates))
                                self.assertGreaterEqual(ui.order_items.height, 4 * 44)
                                self.assertTrue(all(row.height >= 44 for row in ui.order_rows.values()))
                                ui.template_carousel.index = len(ui.templates) - 1
                                settle()
                                # The focused quantity controls are outside
                                # the carousel. Widget.walk() without restrict
                                # also visits unrelated later siblings, such as
                                # deliberately scrolled-out cart item buttons.
                                for widget in ui.quantity_buttons[ui.templates[-1].template_id]:
                                    visible(widget)
                            elif screen == 'payment':
                                visible(ui.payment_confirm)
                                visible(ui.payment_back)
                                self.assertIsNone(ui.payment_order.text_size[1])
                                self.assertGreaterEqual(ui.payment_order.height, 4 * ui.payment_order.font_size)
                                painted_qr(ui.payment_qr, ui.payment.current.payload,
                                           root / 'payment.png')
                            elif screen == 'capture':
                                visible(ui.preview)
                                visible(ui.countdown)
                                visible(ui.capture_button)
                                self.assertGreaterEqual(ui.preview.height, 200)
                                # FloatLayout children need explicit anchors.
                                # A valid widget can otherwise extend over the
                                # camera footer while still fitting the window.
                                box = bounds(ui.preview)
                                slot = bounds(ui.preview.parent)
                                self.assertGreaterEqual(box[0], slot[0] - 1)
                                self.assertGreaterEqual(box[1], slot[1] - 1)
                                self.assertLessEqual(box[2], slot[2] + 1)
                                self.assertLessEqual(box[3], slot[3] + 1)
                            elif screen == 'review':
                                # Includes all three selection controls and both
                                # order actions, not only the main accept button.
                                for widget in ui.content.walk():
                                    if isinstance(widget, Button):
                                        visible(widget)
                            elif screen == 'result':
                                visible(ui.upload_status)
                                visible(ui.completion)
                                visible(ui.result_action)
                                painted_qr(ui.qr_view, url, root / 'folder.png')

                # Resize an existing selection without rebuilding it: breakpoint
                # handling must preserve both the chosen quantities and widgets.
                ui.show_template_selection(True, 'Ready', quantities={'template_a': 2})
                start = ui.start_button
                for size in ((1200, 800), (800, 600), (1200, 800)):
                    Window.size = size
                    settle()
                    self.assertIs(ui.start_button, start)
                    self.assertEqual(ui.quantities['template_a'], 2)
                    self.assertEqual(ui.cart_total.text, 'Rp15.000')
        finally:
            Window.remove_widget(ui.shell)
            Window.size = original_size

    def test_customer_screens_and_folder_qr(self):
        """Exercise order gates, selection callbacks, retake rules, and QR pixels."""
        from PIL import Image
        import cv2
        import numpy as np
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        from photobooth.catalog import get_templates
        from photobooth.qr_code import create_qr_image
        from photobooth.app import PhotoBoothApp

        selected = []
        orders = []
        callbacks = {key: lambda: None for key in (
            'on_home_start', 'on_capture', 'on_retake', 'on_accept_session',
            'on_next_session', 'on_finish', 'on_close')}
        callbacks['on_select_photo'] = selected.append
        callbacks['on_start'] = orders.append
        host = KivyHost(lambda: None)
        ui = PhotoBoothUI(host, get_templates(), **callbacks)
        # Both the native window title and compact on-screen wordmark must
        # agree with the approved MEONG spelling, without the old final S.
        self.assertEqual(host.title, 'Meong Photobooth')
        self.assertEqual(ui.brand.text, 'MEONG PHOTOBOOTH')
        ui.show_welcome(True, 'Ready')
        ui.show_template_selection(True, 'Preparing storage', storage_ready=False)
        key = ui.templates[0].template_id
        ui._change_quantity(key, 2)
        self.assertTrue(ui.start_button.disabled)
        ui.set_storage_status(True, 'Drive ready')
        self.assertFalse(ui.start_button.disabled)
        ui._start_selected()
        self.assertEqual(orders, [{key: 2}])
        # Two sheets of one frame have only one capture/session fee.
        self.assertEqual(ui.cart_sessions.text, '1 frame · 2 lembar')
        self.assertEqual(ui.cart_total.text, 'Rp15.000')
        self.assertEqual(ui.quantity_labels[key].text, '2 cetak')

        # Payment is an explicit simulation and confirms only once per screen.
        confirmations = []
        ui.show_payment('Template 1 · 2 lembar', 1, 15000,
                        lambda: confirmations.append(True), lambda: None)
        self.assertEqual(ui.current_screen, 'payment')
        confirm = ui.payment_confirm
        confirm.dispatch('on_release')
        confirm.dispatch('on_release')
        self.assertEqual(confirmations, [True])

        frame = Image.new('RGB', (640, 480), 'salmon')
        ui.show_capture('Session 1', 0, frame)
        ui.set_countdown(3)
        self.assertTrue(ui.capture_button.disabled)
        self.assertEqual(ui.countdown.text, '3')
        # Reusing a texture is important: camera frames must not accumulate GPU
        # allocations during an unattended, long-running booth session.
        texture = ui.preview.texture
        ui.update_live_preview(frame)
        self.assertIs(ui.preview.texture, texture)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'photo.png'
            frame.save(path)
            ui.show_review([path] * 3, 'Session 1', None, True)
            self.assertTrue(ui.retake_button.disabled)
            ui.show_review([path] * 3, 'Session 1', 1, True)
            self.assertFalse(ui.retake_button.disabled)
            ui.show_review([path] * 3, 'Session 1', 1, False)
            self.assertTrue(ui.retake_button.disabled)
            url = 'https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz123456'
            qr = create_qr_image(url)
            ui.show_result(path, 'Session 1', 'PB001_00000001', False,
                           seconds_remaining=60, qr_image=qr, upload_message='Upload pending')
            # Decode the actual GPU texture, rather than only the source Pillow
            # image, to detect broken color conversion or missing QR pixels.
            pixels = np.frombuffer(ui.qr_view.texture.pixels, dtype=np.uint8)
            width, height = ui.qr_view.texture.size
            channels = pixels.size // (width * height)
            decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(
                pixels.reshape(height, width, channels)[:, :, :3])
            self.assertEqual(decoded, url)
            # A short window must never collapse the QR to zero height.
            self.assertIsNone(ui.qr_view.size_hint_y)
            self.assertGreaterEqual(ui.qr_view.height, 180)
            self.assertIn('01:00', ui.completion.text)
            ui.set_result_upload_status('Offline; files queued')
            self.assertIsNotNone(ui.qr_view.texture)

        # The QR must remain available BEFORE verification, including upload
        # retries. A local-only transaction must never receive a fabricated URL.
        controller = PhotoBoothApp.__new__(PhotoBoothApp)
        for state in ('PENDING', 'UPLOADING', 'UPLOAD_RETRY', 'UPLOAD_COMPLETE'):
            controller.transaction = SimpleNamespace(manifest={
                'drive_folder_url': url, 'upload_status': state})
            self.assertTrue(controller._should_show_result_qr())
        controller.transaction = SimpleNamespace(manifest={})
        self.assertFalse(controller._should_show_result_qr())
        controller.transaction = None
        self.assertFalse(controller._should_show_result_qr())

    def test_timer_cancellation(self):
        """A cancelled callback must not fire after moving away from its screen."""
        from kivy.clock import Clock
        from photobooth.ui_kivy import KivyHost
        host = KivyHost(lambda: None)
        fired = []
        event = host.after(0, lambda: fired.append(True))
        host.after_cancel(event)
        Clock.tick()
        self.assertEqual(fired, [])
