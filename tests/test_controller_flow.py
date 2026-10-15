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
             patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY': '1'}):
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
                app._start_retake_countdown()  # No selected target: no timer.
                self.assertIsNone(app._countdown_after_id)
                app._select_photo(1)
                app._start_retake_countdown()
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
             patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY': '0'}):
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
