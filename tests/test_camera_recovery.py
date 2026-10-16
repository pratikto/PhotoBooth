"""Controller and real-widget checks for a temporary loss of camera frames.

The synthetic camera has an already-open handle whose mailbox can return None.
This tests recovery when fresh frames resume, not USB hotplug or driver reopening.
Controller timers are held for deterministic manual ticks; no real camera,
network, credentials, or user transaction directories are used.
"""

from contextlib import ExitStack
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class CameraRecoveryTests(unittest.TestCase):
    def setUp(self):
        from photobooth.app import PhotoBoothApp
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        directory = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.frame = np.full((240, 320, 3), (60, 130, 180), dtype=np.uint8)
        self.latest = self.frame
        camera = SimpleNamespace(open=lambda: True, read=lambda: self.latest, close=lambda: None)
        self.stack.enter_context(patch('photobooth.app.PROJECT_ROOT', Path(directory)))
        self.stack.enter_context(patch('photobooth.app.Camera', return_value=camera))
        self.stack.enter_context(patch('photobooth.app.AppsScriptDriveClient.from_configuration', return_value=None))
        self.stack.enter_context(patch('photobooth.app.GoogleDriveClient.from_environment', return_value=None))
        self.stack.enter_context(patch.dict(os.environ, {
            'PHOTOBOOTH_LOCAL_ONLY': '1', 'PHOTOBOOTH_PALM_TRIGGER': '0'}))
        self.stack.enter_context(patch('photobooth.app.KivyHost.after',
                                       return_value=SimpleNamespace(cancel=lambda: None)))
        self.app = PhotoBoothApp()
        self.addCleanup(self.app.close)
        self.errors = self.stack.enter_context(patch.object(self.app.ui, 'show_error'))
        self.app._connect_camera()

    def order(self):
        self.app._open_template_selection()
        self.key = self.app.templates[0].template_id
        self.app.ui._change_quantity(self.key, 2)
        self.app.ui.start_button.dispatch('on_release')

    def install_palm_observations(self):
        """Inject model observations while keeping the real controller and UI."""
        class Worker:
            state = 'ready'
            result = None
            def submit(self, _frame, _context):
                pass
            def poll(self):
                result, self.result = self.result, None
                return result
            def pause(self):
                self.result = None
            def close(self):
                self.state = 'closed'
        self.app.palm_worker.close()
        self.app.palm_worker = Worker()
        self.palm_now = 100.0
        self.stack.enter_context(patch('photobooth.app.time',
                                       SimpleNamespace(monotonic=lambda: self.palm_now)))

    def palm_sample(self, score, timestamp, context=None, age=0):
        from photobooth.palm_gesture import PalmObservation
        self.palm_now = timestamp
        self.app.palm_worker.result = PalmObservation(
            self.app.ui.screen_revision if context is None else context,
            timestamp - age, score)
        self.app._update_palm_trigger(self.app.current_frame)

    def test_palm_and_button_share_capture_rules_including_selected_photo_retake(self):
        self.install_palm_observations()
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        for t in (100, 100.2, 100.4, 100.6, 100.8):
            self.palm_sample(.95, t)
            self.assertIsNone(self.app._countdown_after_id)
        self.palm_sample(.95, 101.01)
        self.assertIsNotNone(self.app._countdown_after_id)
        self.assertTrue(self.app.ui.capture_button.disabled)
        self.assertIn('Turunkan tangan', self.app.ui.capture_hint.text)
        timer = self.app._countdown_after_id
        for t in (101.2, 101.4, 101.6):
            self.palm_sample(.95, t)
        self.assertIs(self.app._countdown_after_id, timer)
        for _ in range(5):
            self.app._countdown_tick()
        self.assertEqual(len(self.app.current_session.initial_photo_paths), 1)
        for t in (102, 102.2, 102.4, 102.6, 102.8, 103.01):
            self.palm_sample(.95, t)
        self.assertIsNone(self.app._countdown_after_id)  # Same held palm cannot take photo two.
        self.assertFalse(self.app.ui.capture_button.disabled)
        self.app.ui.capture_button.dispatch('on_release')  # Button works even while palm is latched.
        for _ in range(5):
            self.app._countdown_tick()
        self.assertEqual(len(self.app.current_session.initial_photo_paths), 2)
        for t in (104, 104.2, 104.41):
            self.palm_sample(0, t)
        for t in (104.6, 104.8, 105, 105.2, 105.4, 105.61):
            self.palm_sample(.95, t)
        self.assertIsNotNone(self.app._countdown_after_id)
        for _ in range(5):
            self.app._countdown_tick()
        self.assertEqual(self.app.ui.current_screen, 'review')
        for t in (106, 106.2, 106.4, 106.6, 106.8, 107.01):
            self.palm_sample(.95, t)
        self.assertEqual(self.app.ui.current_screen, 'review')  # Gestures never choose retake.
        self.assertIsNone(self.app._countdown_after_id)
        self.app._select_photo(2)
        originals = list(self.app.current_session.final_photo_paths)
        self.app.ui.retake_button.dispatch('on_release')
        self.assertIsNone(self.app._countdown_after_id)
        for t in (108, 108.2, 108.41):
            self.palm_sample(0, t)
        for t in (108.6, 108.8, 109, 109.2, 109.4, 109.61):
            self.palm_sample(.95, t)
        self.assertIsNotNone(self.app._countdown_after_id)
        self.assertFalse(self.app.current_session.retake_used)
        for _ in range(5):
            self.app._countdown_tick()
        session = self.app.current_session
        self.assertTrue(session.retake_used)
        self.assertEqual(session.final_photo_paths, originals[:2] + [session.retake_path])
        self.assertTrue(self.app.ui.retake_button.disabled)

    def test_stale_wrong_page_missing_camera_and_low_confidence_cannot_fire_palm_shutter(self):
        self.install_palm_observations()
        self.order()
        # Neither payment nor another screen accepts a gesture confirmation.
        for t in (100, 100.2, 100.4, 100.6, 100.8, 101.01):
            self.palm_sample(.95, t)
        self.assertIsNone(self.app.transaction)
        self.app.ui.payment_confirm.dispatch('on_release')
        old_page = self.app.ui.screen_revision - 1
        for start, kwargs in ((102, {'context': old_page}), (104, {'age': 1}), (106, {}),
                              (108, {'age': -1})):
            for offset in (0, .2, .4, .6, .8, 1.01):
                self.palm_sample(.95 if kwargs else .4, start + offset, **kwargs)
            self.assertIsNone(self.app._countdown_after_id)
        self.app.camera_ready = False
        for t in (110, 110.2, 110.4, 110.6, 110.8, 111.01):
            self.palm_sample(.95, t)
        self.assertIsNone(self.app._countdown_after_id)
        self.app.camera_ready = True
        self.app.ui.capture_button.dispatch('on_release')
        self.assertIsNotNone(self.app._countdown_after_id)  # Gesture rejection cannot break button use.

    def test_unavailable_detector_keeps_the_existing_button_and_does_not_consume_retake(self):
        self.install_palm_observations()
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        self.app.palm_worker.state = 'unavailable'
        for t in (100, 100.2, 100.4, 100.6, 100.8, 101.01):
            self.palm_sample(.95, t)
        self.assertIsNone(self.app._countdown_after_id)
        self.assertIn('Gestur belum tersedia', self.app.ui.capture_hint.text)
        self.assertFalse(self.app.ui.capture_button.disabled)
        self.assertFalse(self.app.current_session.retake_used)
        self.app.ui.capture_button.dispatch('on_release')
        self.assertIsNotNone(self.app._countdown_after_id)

    def test_button_press_during_a_partial_palm_hold_does_not_restart_countdown(self):
        self.install_palm_observations()
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        for t in (100, 100.2, 100.4, 100.6, 100.8):
            self.palm_sample(.95, t)
        self.app.ui.capture_button.dispatch('on_release')
        self.app._countdown_tick()
        self.assertEqual(self.app._countdown_remaining, 4)
        for t in (101, 101.2, 101.4, 101.6, 101.8, 102.01):
            self.palm_sample(.95, t)
        self.assertEqual(self.app._countdown_remaining, 4)
        self.assertEqual(len(self.app.current_session.initial_photo_paths), 0)

    def test_fresh_delayed_inferences_use_frame_times_for_a_continuous_hold(self):
        """A constant 300ms inference delay must not reset every valid sample."""
        self.install_palm_observations()
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        for t in (100, 100.2, 100.4, 100.6, 100.8):
            self.palm_sample(.95, t, age=.3)
            self.assertIsNone(self.app._countdown_after_id)
        self.palm_sample(.95, 101.01, age=.3)
        self.assertIsNotNone(self.app._countdown_after_id)

    @unittest.skipUnless(os.environ.get('PHOTOBOOTH_PALM_TEST_ASSETS'), 'Native model assets are opt-in')
    def test_real_model_worker_drives_the_actual_controller_and_keeps_button_capture(self):
        """Use real inference and mailboxes; only camera acquisition is synthetic."""
        import cv2
        from photobooth.palm_gesture import PalmGestureWorker

        assets = Path(os.environ['PHOTOBOOTH_PALM_TEST_ASSETS'])
        self.app.palm_worker.close()
        self.app.palm_worker = PalmGestureWorker(assets / 'gesture_recognizer.task')
        self.app.palm_worker.start()
        deadline = time.monotonic() + 5
        while self.app.palm_worker.state == 'loading' and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertEqual(self.app.palm_worker.state, 'ready')
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        original_button = self.app.ui.capture_button
        self.assertFalse(original_button.disabled)
        source = cv2.imread(str(assets / 'left_hands.jpg'))
        self.assertIsNotNone(source)
        deadline = time.monotonic() + 5
        while self.app._countdown_after_id is None and time.monotonic() < deadline:
            self.latest = source.copy()  # Each read represents a distinct camera exposure.
            self.app._update_preview()
            time.sleep(.12)
        self.assertIsNotNone(self.app._countdown_after_id)
        self.assertEqual(self.app._countdown_remaining, 5)
        self.assertIsNotNone(original_button)
        self.assertIn('AMBIL FOTO', original_button.text)
        self.assertEqual(len(self.app.current_session.initial_photo_paths), 0)
        for _ in range(5):
            self.app._countdown_tick()
        self.assertEqual(len(self.app.current_session.initial_photo_paths), 1)
        self.assertFalse(self.app.ui.capture_button.disabled)

    def test_retake_waits_for_capture_press_before_replacing_the_selected_photo(self):
        """Opening retake previews the camera; only a second press starts capture.

        Drive the real buttons and deterministic timer ticks. Waiting must not
        schedule a countdown, write a file, or spend the session's allowance.
        A completed retake replaces only the selected result position while
        retaining all three original files.
        """
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        for _ in range(3):
            self.app._save_current_frame(False)
        self.app._select_photo(1)
        session = self.app.current_session
        originals = list(session.initial_photo_paths)
        original_bytes = [path.read_bytes() for path in originals]
        manifest_bytes = self.app.transaction.manifest_path.read_bytes()
        with patch.object(self.app.root, 'after', wraps=self.app.root.after) as schedule:
            self.app.ui.retake_button.dispatch('on_release')
            self.assertEqual(self.app.ui.current_screen, 'capture')
            self.assertIsNone(self.app._countdown_after_id)
            schedule.assert_not_called()
            self.assertEqual(self.app.ui.countdown.text, 'Siap?')
            self.assertEqual(self.app.ui.capture_button.text, 'AMBIL FOTO PENGGANTI')
            self.assertFalse(self.app.ui.capture_button.disabled)
            self.assertEqual(session.selected_index, 1)
            self.assertFalse(session.retake_used)
            self.assertEqual(session.final_photo_paths, originals)
            self.assertEqual(self.app.transaction.manifest_path.read_bytes(), manifest_bytes)

            # An old review release must not skip the ready screen, either.
            self.app.ui.retake_button.dispatch('on_release')
            schedule.assert_not_called()
            self.app.current_frame = np.full_like(self.frame, (180, 90, 30))
            self.app.ui.capture_button.dispatch('on_release')
            self.assertIsNotNone(self.app._countdown_after_id)
            schedule.assert_called_once()
            self.assertEqual(self.app.ui.countdown.text, '5')
            self.assertTrue(self.app.ui.capture_button.disabled)
            self.app.ui.capture_button.dispatch('on_release')
            schedule.assert_called_once()
            for _ in range(4):
                self.app._countdown_tick()
                self.assertFalse(session.retake_used)
            self.app._countdown_tick()

        self.assertEqual(self.app.ui.current_screen, 'review')
        self.assertTrue(session.retake_used)
        self.assertEqual(session.retake_target_index, 1)
        self.assertEqual(session.final_photo_paths,
                         [originals[0], session.retake_path, originals[2]])
        self.assertEqual([path.read_bytes() for path in originals], original_bytes)
        self.assertNotEqual(session.retake_path.read_bytes(), original_bytes[1])
        self.assertTrue(self.app.ui.retake_button.disabled)

    def test_camera_recovery_on_retake_ready_screen_still_waits_for_a_press(self):
        """Frame recovery enables the retake shutter without starting its timer."""
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        for _ in range(3):
            self.app._save_current_frame(False)
        self.app._select_photo(2)
        self.app.ui.retake_button.dispatch('on_release')
        ready_button = self.app.ui.capture_button
        self.latest = None
        self.app._update_preview()
        self.assertTrue(ready_button.disabled)
        ready_button.dispatch('on_release')
        self.assertIsNone(self.app._countdown_after_id)
        self.latest = self.frame
        self.app._update_preview()
        self.assertIs(self.app.ui.capture_button, ready_button)
        self.assertFalse(ready_button.disabled)
        self.assertEqual(self.app.ui.countdown.text, 'Siap?')
        self.assertIsNone(self.app._countdown_after_id)
        self.assertFalse(self.app.current_session.retake_used)
        self.assertEqual(self.app.current_session.selected_index, 2)
        ready_button.dispatch('on_release')
        timer = self.app._countdown_after_id
        self.assertIsNotNone(timer)
        # Further camera updates cannot unlock a countdown already in progress.
        self.latest = None
        self.app._update_preview()
        self.latest = self.frame
        self.app._update_preview()
        self.assertIs(self.app._countdown_after_id, timer)
        self.assertTrue(self.app.ui.capture_button.disabled)

    def test_retry_after_retake_metadata_failure_uploads_the_replacement_bytes(self):
        """Exercise the actual GUI/controller path into a same-filename retry.

        The JPEG and its queue entry succeed, but recording the selected target
        fails once. A worker uploads those first bytes before the customer tries
        again. The retry must replace the selected photo locally AND queue its
        new bytes, not inherit the first upload's VERIFIED flag.
        """
        import hashlib
        import json
        from photobooth.drive_sync import sync_manifest

        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        transaction = self.app.transaction
        transaction.manifest.update({
            'drive_folder_id': 'fixture-folder',
            'drive_folder_url': 'https://drive.google.com/drive/folders/fixture-folder',
        })
        self.app.store._write_manifest(transaction)
        for _ in range(3):
            self.app._save_current_frame(False)
        self.app._select_photo(1)
        with patch.object(self.app.store, 'record_retake', side_effect=OSError('Fixture disk failure')):
            self.app._save_current_frame(True)
        self.assertEqual(self.app.ui.current_screen, 'review')
        self.assertFalse(self.app.current_session.retake_used)
        self.errors.assert_called_once()
        uploads = []

        class Drive:
            def upload_file(self, _folder, _transaction, relative_path, local_path, **_kwargs):
                data = local_path.read_bytes()
                uploads.append((relative_path, data))
                return {'id': 'fixture-file', 'size': str(len(data)),
                        'md5Checksum': hashlib.md5(data).hexdigest()}

        backend = Drive()
        sync_manifest(transaction.manifest_path, backend)
        key = 'raw/session_001/retake_01.jpg'
        first_bytes = (transaction.folder_path / key).read_bytes()
        self.app.current_frame = np.full_like(self.frame, (180, 90, 30))
        self.app._save_current_frame(True)
        self.assertTrue(self.app.current_session.retake_used)
        self.assertTrue(self.app.ui.retake_button.disabled)
        new_bytes = self.app.current_session.retake_path.read_bytes()
        self.assertNotEqual(new_bytes, first_bytes)
        saved = json.loads(transaction.manifest_path.read_text(encoding='utf-8'))
        self.assertEqual(saved['upload_files'][key]['status'], 'PENDING_UPLOAD')
        sync_manifest(transaction.manifest_path, backend)
        uploaded_retakes = [data for path, data in uploads if path == key]
        self.assertEqual(uploaded_retakes, [first_bytes, new_bytes])
        self.assertEqual(self.app.current_session.final_photo_paths[1],
                         self.app.current_session.retake_path)

    def test_camera_readiness_tracks_home_cart_and_payment_without_losing_order(self):
        ui = self.app.ui
        self.latest = None
        self.app._update_preview()
        self.assertFalse(self.app.camera_ready)
        self.assertTrue(ui.home_start_button.disabled)
        self.latest = self.frame
        self.app._update_preview()
        self.assertTrue(self.app.camera_ready)
        self.assertFalse(ui.home_start_button.disabled)
        self.assertNotIn('Menunggu gambar', ui.status.text)
        self.app._open_template_selection()
        key = self.app.templates[0].template_id
        ui._change_quantity(key, 2)
        self.latest = None
        self.app._update_preview()
        self.assertTrue(ui.start_button.disabled)
        self.latest = self.frame
        self.app._update_preview()
        self.assertFalse(ui.start_button.disabled)
        self.assertEqual(ui.quantities[key], 2)
        ui.start_button.dispatch('on_release')
        confirm = ui.payment_confirm
        self.latest = None
        self.app._update_preview()
        self.assertTrue(confirm.disabled)
        confirm.dispatch('on_release')  # Even a queued stale release is ignored.
        self.assertIsNone(self.app.transaction)
        self.latest = self.frame
        self.app._update_preview()
        self.assertIs(ui.payment_confirm, confirm)
        self.assertFalse(confirm.disabled)
        self.assertEqual(ui.payment_total, 10000)
        confirm.dispatch('on_release')
        self.assertEqual(len(self.app.sessions), 2)

    def test_missing_frames_clear_preview_and_cannot_start_a_countdown(self):
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        transaction = self.app.transaction
        session = self.app.current_session
        self.assertIsNotNone(self.app.ui.preview.texture)
        self.latest = None
        self.app._update_preview()
        self.assertFalse(self.app.camera_ready)
        self.assertTrue(self.app.ui.capture_button.disabled)
        self.assertIsNone(self.app.ui.preview.texture)
        self.assertEqual(self.app.ui.preview.opacity, 0)
        self.assertEqual(self.app.ui.camera_wait_hint.opacity, 1)
        self.assertIn('MENUNGGU', self.app.ui.live_caption.text)
        self.app._start_capture_countdown()
        self.assertIsNone(self.app._countdown_after_id)
        self.latest = self.frame
        self.app._update_preview()
        self.assertTrue(self.app.camera_ready)
        self.assertFalse(self.app.ui.capture_button.disabled)
        self.assertIsNotNone(self.app.ui.preview.texture)
        self.assertEqual(self.app.ui.preview.opacity, 1)
        self.assertEqual(self.app.ui.camera_wait_hint.opacity, 0)
        self.assertEqual(self.app.ui.live_caption.text, 'LIVE CAMERA')
        self.assertIs(self.app.transaction, transaction)
        self.assertIs(self.app.current_session, session)
        self.app._start_capture_countdown()
        self.assertIsNotNone(self.app._countdown_after_id)

    def test_rejected_confirmation_unlocks_after_camera_recovers(self):
        self.order()
        confirm = self.app.ui.payment_confirm
        # The controller performs a second check even if an old UI release was
        # already queued before the camera state changed.
        self.app.camera_ready = False
        confirm.dispatch('on_release')
        self.assertIsNone(self.app.transaction)
        self.errors.assert_called_once()
        self.app._update_preview()
        self.assertFalse(confirm.disabled)
        confirm.dispatch('on_release')
        transaction = self.app.transaction
        self.assertIsNotNone(transaction)
        confirm.dispatch('on_release')
        self.assertIs(self.app.transaction, transaction)
        self.assertEqual(len(self.app.sessions), 2)

    def test_late_release_from_replaced_payment_cannot_submit_old_quantities(self):
        self.order()
        old_confirm = self.app.ui.payment_confirm
        self.app.ui.payment_back.dispatch('on_release')
        self.app.ui._change_quantity(self.key, -1)
        self.app.ui.start_button.dispatch('on_release')
        self.assertEqual(self.app.ui.payment_total, 5000)
        old_confirm.dispatch('on_release')
        self.assertIsNone(self.app.transaction)
        self.assertFalse(self.app.ui.payment_confirm.disabled)
        self.app.ui.payment_confirm.dispatch('on_release')
        self.assertEqual(len(self.app.sessions), 1)

    def test_stale_back_cannot_restore_an_older_cart(self):
        """An old navigation release must not overwrite the customer's edit."""
        self.order()
        old_back = self.app.ui.payment_back
        old_back.dispatch('on_release')
        self.app.ui._change_quantity(self.key, 1)
        self.app.ui.start_button.dispatch('on_release')
        self.assertEqual(self.app.ui.payment_total, 15000)
        old_back.dispatch('on_release')
        self.assertEqual(self.app.ui.current_screen, 'payment')
        self.assertEqual(self.app.ui.payment_total, 15000)
        self.assertIsNone(self.app.transaction)
        self.app.ui.payment_back.dispatch('on_release')
        self.assertEqual(self.app.ui.quantities[self.key], 3)

    def test_stale_finish_cannot_complete_another_customer_transaction(self):
        """Retained result controls belong to one screen, not the next customer."""
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        for number in range(2):
            for _ in range(3):
                self.app._save_current_frame(False)
            self.app._accept_current_session()
            if number == 0:
                self.app.ui.result_action.dispatch('on_release')
        old_finish = self.app.ui.result_action
        old_finish.dispatch('on_release')
        self.assertEqual(self.app.ui.current_screen, 'welcome')
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        transaction = self.app.transaction
        initial_status = transaction.manifest['status']
        old_finish.dispatch('on_release')
        self.assertIs(self.app.transaction, transaction)
        self.assertEqual(transaction.manifest['status'], initial_status)
        self.assertEqual(self.app.ui.current_screen, 'capture')

    def test_completion_request_cannot_skip_unfinished_sessions(self):
        """Controller completion is valid only after accepting the final output."""
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        transaction = self.app.transaction
        initial_status = transaction.manifest['status']
        self.app._finish_transaction()  # Simulates a late timer/controller request.
        self.assertIs(self.app.transaction, transaction)
        self.assertEqual(transaction.manifest['status'], initial_status)
        self.assertEqual(self.app.ui.current_screen, 'capture')
        for _ in range(3):
            self.app._save_current_frame(False)
        self.app._accept_current_session()
        self.app._finish_transaction()  # A first-session result is not the end.
        self.assertIs(self.app.transaction, transaction)
        self.assertEqual(self.app.ui.current_screen, 'result')
        self.app._start_next_session()
        for _ in range(3):
            self.app._save_current_frame(False)
        self.app._accept_current_session()
        self.assertEqual(self.app._completion_remaining, 60)
        for _ in range(60):
            self.app._completion_countdown_tick()
        self.assertIsNone(self.app.transaction)
        self.assertEqual(transaction.manifest['status'], 'COMPLETED')
        self.assertEqual(self.app.ui.current_screen, 'welcome')

    def test_failed_retake_keeps_allowance_and_exhausted_state_is_explicit(self):
        self.order()
        self.app.ui.payment_confirm.dispatch('on_release')
        for _ in range(3):
            self.app._save_current_frame(False)
        self.app._select_photo(1)
        self.app.ui.retake_button.dispatch('on_release')
        self.app.ui.capture_button.dispatch('on_release')
        self.latest = None
        self.app._update_preview()
        for _ in range(5):
            self.app._countdown_tick()
        session = self.app.current_session
        self.assertEqual(self.app.ui.current_screen, 'review')
        self.assertFalse(session.retake_used)
        self.assertTrue(self.app.ui.retake_button.disabled)
        self.assertEqual(session.selected_index, 1)
        self.assertIn('Kamera belum siap', self.app.ui.review_hint.text)
        self.latest = self.frame
        self.app._update_preview()
        self.assertFalse(self.app.ui.retake_button.disabled)
        self.assertNotIn('Kamera belum siap', self.app.ui.review_hint.text)
        self.app.ui.retake_button.dispatch('on_release')
        self.app.ui.capture_button.dispatch('on_release')
        for _ in range(5):
            self.app._countdown_tick()
        self.assertTrue(session.retake_used)
        self.assertTrue(self.app.ui.retake_button.disabled)
        self.assertEqual(self.app.ui.retake_button.text, 'RETAKE SUDAH DIGUNAKAN')
        labels = [getattr(widget, 'text', '') for widget in self.app.ui.content.walk()]
        self.assertIn('Foto 2 · DIGANTI', labels)
        self.assertFalse(any('Pilih untuk retake' in label for label in labels))
        self.assertIn('Retake sudah digunakan', self.app.ui.review_hint.text)
