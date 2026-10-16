"""Exercise the actual controller, Kivy screens, and storage in one customer order.

A synthetic camera replaces hardware and a stub worker prevents network access.
No credentials, customer folder IDs, or payment-provider calls are required.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class ControllerFlowTests(unittest.TestCase):
    def test_an_abandoned_review_cannot_compose_new_photo_bytes_after_fifteen_days(self):
        """An old on-screen session must not undo the background retention job."""
        from datetime import datetime, timedelta, timezone
        import json
        from photobooth.app import PhotoBoothApp
        with tempfile.TemporaryDirectory() as directory, \
             patch('photobooth.app.PROJECT_ROOT', Path(directory)), \
             patch('photobooth.app.Camera'), \
             patch('photobooth.app.AppsScriptDriveClient.from_configuration', return_value=None), \
             patch('photobooth.app.GoogleDriveClient.from_environment', return_value=None), \
             patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY': '1', 'PHOTOBOOTH_PALM_TRIGGER': '0'}):
            app = PhotoBoothApp()
            try:
                app.camera_ready = True
                app.current_frame = np.zeros((240, 320, 3), dtype=np.uint8)
                app._open_template_selection()
                app._open_dummy_payment({app.templates[0].template_id: 1})
                app.ui.payment_confirm.dispatch('on_release')
                for _ in range(3):
                    app._save_current_frame(False)
                transaction = app.transaction
                manifest = json.loads(transaction.manifest_path.read_text())
                manifest['created_at'] = (datetime.now(timezone.utc) - timedelta(days=16)).isoformat()
                app.store._atomic_write_json(transaction.manifest_path, manifest)
                with patch.object(app.ui, 'show_error') as error:
                    app.ui.accept_button.dispatch('on_release')
                error.assert_called_once()
                self.assertIn('retention deadline', error.call_args.args[1])
                self.assertFalse((transaction.folder_path / 'output').exists())
                self.assertIsNone(app.current_session.output_path)
                self.assertTrue(json.loads(transaction.manifest_path.read_text())['local_photos_expired_at'])
            finally:
                app.close()

    def test_editing_payment_preserves_cart_and_recalculates_the_total(self):
        """Returning from payment must edit the same order without allocating a slot.

        The test drives real button callbacks, rather than calling the payment
        method with a second hand-written amount. It catches lost quantities and
        a stale confirmation total after the customer removes a session.
        """
        from photobooth.app import PhotoBoothApp
        with tempfile.TemporaryDirectory() as directory, \
             patch('photobooth.app.PROJECT_ROOT', Path(directory)), \
             patch('photobooth.app.Camera'), \
             patch('photobooth.app.AppsScriptDriveClient.from_configuration', return_value=None), \
             patch('photobooth.app.GoogleDriveClient.from_environment', return_value=None), \
             patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY': '1', 'PHOTOBOOTH_PALM_TRIGGER': '0'}):
            app = PhotoBoothApp()
            try:
                app.camera_ready = True
                app.current_frame = np.zeros((240, 320, 3), dtype=np.uint8)
                app._open_template_selection()
                first, second = (template.template_id for template in app.templates[:2])
                app.ui._change_quantity(first, 2)
                app.ui._change_quantity(second, 1)
                app.ui.start_button.dispatch('on_release')
                self.assertEqual(app.ui.payment_total, 15000)
                app.ui.payment_back.dispatch('on_release')
                self.assertEqual(app.ui.current_screen, 'templates')
                self.assertEqual(app.ui.quantities[first], 2)
                self.assertEqual(app.ui.quantities[second], 1)
                self.assertIsNone(app.transaction)
                app.ui._change_quantity(first, -1)
                app.ui._change_quantity(second, -1)
                self.assertEqual(app.ui.cart_total.text, 'Rp5.000')
                app.ui.start_button.dispatch('on_release')
                self.assertEqual(app.ui.payment_total, 5000)
                app.ui.payment_confirm.dispatch('on_release')
                self.assertEqual(len(app.sessions), 1)
                self.assertIsNotNone(app.transaction)
            finally:
                app.close()

    def test_two_sessions_payment_capture_retake_output_and_completion(self):
        from photobooth.app import PhotoBoothApp
        class FakeCamera:
            def __init__(self, **kwargs):
                self.closed = False
            def open(self):
                return True
            def read(self):
                return np.full((240, 320, 3), (45, 120, 180), dtype=np.uint8)
            def close(self):
                self.closed = True
        with tempfile.TemporaryDirectory() as directory, \
             patch('photobooth.app.PROJECT_ROOT', Path(directory)), \
             patch('photobooth.app.Camera', FakeCamera), \
             patch('photobooth.app.AppsScriptDriveClient.from_configuration', return_value=None), \
             patch('photobooth.app.GoogleDriveClient.from_environment', return_value=None), \
             patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY': '1', 'PHOTOBOOTH_PALM_TRIGGER': '0'}):
            app = PhotoBoothApp()
            try:
                app._connect_camera()
                app._open_template_selection()
                self.assertEqual(app.ui.current_screen, 'templates')
                order = {app.templates[0].template_id: 2}
                app._open_dummy_payment(order)
                self.assertIsNone(app.transaction)  # No transaction before payment.
                self.assertEqual(app.ui.payment_total, 10000)  # Two sessions at IDR 5,000.
                app.ui.payment_confirm.dispatch('on_release')
                self.assertEqual(app.ui.current_screen, 'capture')
                transaction = app.transaction
                app._start_transaction(order)  # A stale payment click is ignored.
                self.assertIs(app.transaction, transaction)
                app._start_capture_countdown()
                self.assertTrue(app.ui.capture_button.disabled)
                for _ in range(5):
                    # Drive timer ticks directly, cancelling real scheduled ticks
                    # to keep the deterministic test under a second.
                    app._cancel_after(app._countdown_after_id)
                    app._countdown_tick()
                self.assertEqual(len(app.current_session.initial_photo_paths), 1)
                app._save_current_frame(False)
                app._save_current_frame(False)
                self.assertEqual(app.ui.current_screen, 'review')
                app.ui.retake_button.dispatch('on_release')  # No selected target: no timer.
                self.assertIsNone(app._countdown_after_id)
                app._select_photo(1)
                app.ui.retake_button.dispatch('on_release')
                self.assertIsNone(app._countdown_after_id)  # Ready first; no automatic timer.
                app.ui.capture_button.dispatch('on_release')
                for _ in range(5):
                    app._cancel_after(app._countdown_after_id)
                    app._countdown_tick()
                self.assertTrue(app.current_session.retake_used)
                self.assertFalse(app.current_session.can_retake)
                app._accept_current_session()
                self.assertEqual(app.ui.current_screen, 'result')
                self.assertTrue(app.current_session.output_path.is_file())
                app._start_next_session()
                self.assertFalse(app.current_session.retake_used)  # Independent quota.
                for _ in range(3):
                    app._save_current_frame(False)
                app._accept_current_session()
                self.assertEqual(app.ui.current_screen, 'result')
                self.assertEqual(app._completion_remaining, 60)
                app._finish_transaction()
                self.assertEqual(app.ui.current_screen, 'welcome')
                import json
                manifest = json.loads(transaction.manifest_path.read_text())
                self.assertEqual(manifest['status'], 'COMPLETED')
                self.assertEqual(len(manifest['sessions']), 2)
                for record in manifest['sessions']:
                    self.assertTrue((transaction.folder_path / record['output_path']).is_file())
            finally:
                app.close()
                self.assertTrue(app.camera.closed)

    def test_reserved_folder_qr_survives_offline_and_upload_retries(self):
        """Keep one destination through capture, outage, completion, and retry."""
        import hashlib
        from photobooth.app import PhotoBoothApp
        from photobooth.drive_storage import RemoteDriveSlot, DriveApiError
        from photobooth.drive_sync import sync_manifest
        class FakeCamera:
            def __init__(self, **kwargs):
                pass
            def open(self):
                return True
            def read(self):
                return np.full((180, 240, 3), 128, dtype=np.uint8)
            def close(self):
                pass
        url = 'https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz123456'
        class Backend:
            offline = True
            calls = 0
            def ensure_folder_pool(self, *args):
                return [RemoteDriveSlot(folder_id='test-folder', folder_url=url,
                                        slot_key='PB001_00000001', status='READY',
                                        folder_name='PB001_00000001', transaction_id='PB001_00000001',
                                        verified=True)]
            def upload_file(self, folder_id, transaction_id, relative_path, local_path, **kwargs):
                if self.offline:
                    raise DriveApiError('Simulated outage', 503)
                self.calls += 1
                return {'id': f'file-{self.calls}', 'size': str(local_path.stat().st_size),
                        'md5Checksum': hashlib.md5(local_path.read_bytes()).hexdigest()}
        with tempfile.TemporaryDirectory() as directory, \
             patch('photobooth.app.PROJECT_ROOT', Path(directory)), \
             patch('photobooth.app.Camera', FakeCamera), \
             patch('photobooth.app.AppsScriptDriveClient.from_configuration', return_value=None), \
             patch('photobooth.app.GoogleDriveClient.from_environment', return_value=None), \
             patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY': '0', 'PHOTOBOOTH_PALM_TRIGGER': '0'}):
            app = PhotoBoothApp()
            backend = Backend()
            try:
                app.drive_pool.refresh(backend)
                app._connect_camera()
                app._open_template_selection()
                app._open_dummy_payment({app.templates[0].template_id: 1})
                app.ui.payment_confirm.dispatch('on_release')
                transaction = app.transaction
                for _ in range(3):
                    app._save_current_frame(False)
                app._accept_current_session()
                self.assertIsNotNone(app.ui.qr_view.texture)
                # Verify the saved/uploaded PNG itself, not only the UI QR.
                import cv2
                decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(
                    cv2.imread(str(app.current_session.output_path)))
                self.assertEqual(decoded, url)
                qr_pixels = app.ui._qr_bytes
                manifest = sync_manifest(transaction.manifest_path, backend)
                self.assertEqual(manifest['upload_status'], 'UPLOAD_RETRY')
                self.assertEqual(manifest['drive_folder_url'], url)
                app._schedule_drive_status_update()
                self.assertEqual(app.ui._qr_bytes, qr_pixels)
                app._finish_transaction()
                backend.offline = False
                manifest = sync_manifest(transaction.manifest_path, backend)
                self.assertEqual(manifest['upload_status'], 'UPLOAD_COMPLETE')
                self.assertEqual(manifest['drive_folder_url'], url)
                self.assertEqual(backend.calls, 4)  # Three raw images + final composition.
                sync_manifest(transaction.manifest_path, backend)
                self.assertEqual(backend.calls, 4)  # Verified files are never re-uploaded.
            finally:
                app.close()

    def test_selected_heart_and_arcade_templates_follow_their_own_sessions(self):
        """Real callbacks must pass the chosen design through review and save.

        Using a non-default heart first catches accidental fallback to the
        first catalog entry. A second arcade session catches stale design state
        when advancing, while a third-photo retake checks replacement order.
        """
        from PIL import Image
        from kivy.uix.image import Image as KivyImage
        from photobooth.app import PhotoBoothApp
        with tempfile.TemporaryDirectory() as directory, \
             patch('photobooth.app.PROJECT_ROOT', Path(directory)), \
             patch('photobooth.app.Camera'), \
             patch('photobooth.app.AppsScriptDriveClient.from_configuration', return_value=None), \
             patch('photobooth.app.GoogleDriveClient.from_environment', return_value=None), \
             patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY': '1', 'PHOTOBOOTH_PALM_TRIGGER': '0'}):
            app = PhotoBoothApp()
            try:
                app.camera_ready = True
                app.current_frame = np.full((600, 800, 3), (60, 70, 170), dtype=np.uint8)
                heart, arcade = app.templates[1], app.templates[8]
                app._open_template_selection()
                app.ui._change_quantity(heart.template_id, 1)
                app.ui._change_quantity(arcade.template_id, 1)
                app.ui.start_button.dispatch('on_release')
                app.ui.payment_confirm.dispatch('on_release')
                for template in (heart, arcade):
                    self.assertEqual(app.current_session.plan.template, template)
                    for _ in range(3):
                        app._save_current_frame(False)
                    thumbnails = sorted((widget for widget in app.ui.content.walk()
                                         if isinstance(widget, KivyImage)), key=lambda w: w.x)
                    self.assertEqual(sorted(widget.texture.size for widget in thumbnails),
                                     sorted(frame.size for frame in template.apertures))
                    if template == heart:
                        app._select_photo(2)
                        app.ui.retake_button.dispatch('on_release')
                        self.assertEqual(app.ui.countdown.text, 'Siap?')
                        self.assertIsNone(app._countdown_after_id)
                        app.current_frame = np.full((600, 800, 3), (190, 70, 30), dtype=np.uint8)
                        app._save_current_frame(True)
                    app.ui.accept_button.dispatch('on_release')
                    self.assertEqual(app.ui.current_screen, 'result')
                    output = app.current_session.output_path
                    self.assertEqual(output.name, template.template_id + '.png')
                    with Image.open(output) as saved, Image.open(template.artwork_path) as master:
                        # Header ink comes from the actual selected design.
                        self.assertEqual(saved.crop((0, 0, 640, 120)).tobytes(),
                                         master.crop((0, 0, 640, 120)).tobytes())
                        self.assertEqual(saved.size, (640, 1920))
                        if template == heart:
                            colors = []
                            for frame in template.apertures:
                                x0, y0, x1, y1 = frame.box
                                colors.append(saved.getpixel(((x0 + x1) // 2, (y0 + y1) // 2)))
                            self.assertEqual(colors[0], colors[1])
                            self.assertNotEqual(colors[1], colors[2])
                    if template == heart:
                        before = output.read_bytes()
                        app.ui.result_zoom_button.dispatch('on_release')
                        detail = app.ui._result_detail_popup
                        self.assertIsNotNone(detail)
                        self.assertEqual(output.read_bytes(), before)
                        app.ui.result_action.dispatch('on_release')
                        self.assertIsNone(app.ui._result_detail_popup)
                        self.assertIsNone(detail.parent)
                app.ui.result_action.dispatch('on_release')
                self.assertEqual(app.ui.current_screen, 'welcome')
            finally:
                app.close()
