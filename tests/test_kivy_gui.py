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
            retake = next(w for w in ui.content.children
                          if getattr(w, 'text', '') == 'RETAKE FOTO TERPILIH')
            self.assertTrue(retake.disabled)
            ui.show_review([path] * 3, 'Session 1', 1, True)
            retake = next(w for w in ui.content.children
                          if getattr(w, 'text', '') == 'RETAKE FOTO TERPILIH')
            self.assertFalse(retake.disabled)
            ui.show_review([path] * 3, 'Session 1', 1, False)
            retake = next(w for w in ui.content.children
                          if getattr(w, 'text', '') == 'RETAKE FOTO TERPILIH')
            self.assertTrue(retake.disabled)
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
