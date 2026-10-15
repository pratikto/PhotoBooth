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
                                self.assertEqual(ui.cart_total.text, 'Rp40.000')
                                self.assertIsNone(ui.summary.text_size[1])
                                self.assertGreaterEqual(ui.summary.height, 4 * ui.summary.font_size)
                                last_card = ui._template_cards[ui.templates[-1].template_id]
                                last_card.parent.parent.scroll_y = 0
                                settle()
                                for widget in last_card.walk():
                                    if isinstance(widget, Button):
                                        visible(widget)
                            elif screen == 'payment':
                                visible(ui.payment_confirm)
                                visible(ui.payment_back)
                                self.assertIsNone(ui.payment_order.text_size[1])
                                self.assertGreaterEqual(ui.payment_order.height, 4 * ui.payment_order.font_size)
                                painted_qr(ui.payment_qr, 'PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR 40000',
                                           root / 'payment.png')
                            elif screen == 'capture':
                                visible(ui.preview)
                                visible(ui.countdown)
                                visible(ui.capture_button)
                                self.assertGreaterEqual(ui.preview.height, 200)
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
                    self.assertEqual(ui.cart_total.text, 'Rp10.000')
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
        ui.show_welcome(True, 'Ready')
        ui.show_template_selection(True, 'Preparing storage', storage_ready=False)
        key = ui.templates[0].template_id
        ui._change_quantity(key, 2)
        self.assertTrue(ui.start_button.disabled)
        ui.set_storage_status(True, 'Drive ready')
        self.assertFalse(ui.start_button.disabled)
        ui._start_selected()
        self.assertEqual(orders, [{key: 2}])

        # Payment is an explicit simulation and confirms only once per screen.
        confirmations = []
        ui.show_payment('Template 1 x 2', 2, 10000,
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
