"""Real isolated JPEG/composition and durable print safety, without devices."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np
from PIL import Image

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoTest, PhotoJobs, PURPOSE


class PhotoWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'v2-only'
        self.templates = get_templates()
        self.service = PhotoTest(self.root)
        self.addCleanup(self.service.close)
        self.quantities = {self.templates[0].template_id: 3}
        self.frame = np.zeros((80, 120, 3), dtype=np.uint8)
        self.frame[:, :60] = [0, 0, 255]  # LEFT red: must remain left in saved original.
        self.frame[:, 60:] = [255, 0, 0]

    def start_review(self):
        self.service.start(self.templates, self.quantities)
        for _ in range(3):
            self.service.capture(self.frame)

    def test_isolated_admission_three_photos_and_unmirrored_original_pixels(self):
        with self.assertRaises(ValueError):
            self.service.start(self.templates, {})
        self.start_review()
        view = self.service.snapshot()
        self.assertEqual((view['phase'], view['copies'], len(view['thumbnails'])), ('review', 3, 3))
        self.assertFalse(self.service.transaction.manifest['financial_transaction'])
        self.assertEqual(self.service.transaction.manifest['purpose'], PURPOSE)
        with Image.open(self.service.session.initial_photo_paths[0]) as raw:
            self.assertGreater(raw.getpixel((10, 40))[0], 240)
            self.assertGreater(raw.getpixel((110, 40))[2], 240)
        with self.assertRaises(ValueError):
            self.service.capture(self.frame)
        with self.assertRaises(ValueError):
            self.service.start(self.templates, self.quantities)
        self.assertTrue(all(path.is_relative_to(self.root) for path in self.root.rglob('*')))

    def test_retake_quota_preserves_original_and_is_per_design_not_per_copy(self):
        self.quantities[self.templates[1].template_id] = 2
        self.start_review()
        originals = [path.read_bytes() for path in self.service.session.initial_photo_paths]
        self.service.retake(1)
        self.service.capture(self.frame // 2)
        session = self.service.session
        self.assertEqual(session.retake_target_index, 1)
        self.assertEqual(len(session.raw_photo_paths), 4)
        self.assertEqual([p.read_bytes() for p in session.initial_photo_paths], originals)
        with self.assertRaises(ValueError):
            self.service.retake(0)
        view = self.service.compose()
        self.assertEqual(view['strip'].size, (320, 960))
        with Image.open(session.output_path) as strip:
            self.assertEqual(strip.size, (640, 1920))
        self.assertIsNone(view['folder_url'])
        self.assertEqual(view['upload_status'], 'LOCAL_ONLY')
        self.service.next()
        self.assertFalse(self.service.session.retake_used)
        self.assertEqual(self.service.session.plan.print_copies, 2)
        for _ in range(3):
            self.service.capture(self.frame)
        self.service.compose()
        self.assertEqual(self.service.transaction.manifest['status'], 'COMPLETED')
        self.assertEqual(self.service.next()['phase'], 'done')

    def test_failed_save_does_not_advance_photo_or_consume_retake(self):
        self.start_review()
        self.service.retake(0)
        with patch.object(self.service.store, 'save_raw_photo', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.service.capture(self.frame)
        self.assertFalse(self.service.session.retake_used)
        self.assertEqual(self.service.phase, 'capture')
        self.service.capture(self.frame)
        self.assertTrue(self.service.session.retake_used)

    def test_copies_one_batch_and_durable_no_duplicate_print(self):
        self.start_review()
        self.service.compose()
        def send(path, *, copies):
            manifest = json.loads(self.service.transaction.manifest_path.read_text())
            self.assertEqual(manifest['test_print_jobs']['session_001']['state'], 'SENDING')
            self.assertEqual(copies, 3)
            return SimpleNamespace(success=True)
        self.service.printer = Mock()
        self.service.printer.print_image.side_effect = send
        self.assertEqual(self.service.print_result()['print_state'], 'SUBMITTED')
        with self.assertRaises(ValueError):
            self.service.print_result()
        self.service.printer.print_image.assert_called_once()

    def test_uncertain_send_requires_operator_check_and_restart_never_replays(self):
        self.start_review()
        self.service.compose()
        self.service.printer = Mock()
        self.service.printer.print_image.side_effect = OSError('partial send')
        self.assertEqual(self.service.print_result()['print_state'], 'UNCERTAIN')
        with self.assertRaises(ValueError):
            self.service.next()
        self.service.acknowledge_print()
        self.assertEqual(self.service.next()['phase'], 'done')
        path = self.service.transaction.manifest_path
        manifest = json.loads(path.read_text())
        manifest['test_print_jobs']['session_001']['state'] = 'SENDING'
        path.write_text(json.dumps(manifest))
        restarted = PhotoTest(self.root, printer=self.service.printer)
        restarted.prepare()
        self.assertEqual(restarted.recovered_prints, 1)
        self.assertEqual(json.loads(path.read_text())['test_print_jobs']['session_001']['state'], 'UNCERTAIN')
        self.service.printer.print_image.assert_called_once()
        restarted.close()

    def test_invalid_quantities_and_early_composition_are_rejected(self):
        for quantities in ({'unknown': 1}, {self.templates[0].template_id: 10},
                           {self.templates[0].template_id: True}):
            with self.assertRaises(ValueError):
                self.service.start(self.templates, quantities)
        self.service.start(self.templates, self.quantities)
        with self.assertRaises(ValueError):
            self.service.compose()
        with self.assertRaises(ValueError):
            self.service.capture(None)
        self.assertEqual(len(self.service.session.initial_photo_paths), 0)

    def test_early_exit_preserves_files_and_next_run_never_reuses_id(self):
        self.service.start(self.templates, self.quantities)
        self.service.capture(self.frame)
        path = self.service.session.initial_photo_paths[0]
        old_id = self.service.transaction.transaction_id
        self.assertEqual(self.service.abort()['phase'], 'done')
        self.assertTrue(path.is_file())
        self.assertTrue(self.service.transaction.manifest['test_ended_early'])
        restarted = PhotoTest(self.root)
        view = restarted.start(self.templates, self.quantities)
        self.assertNotEqual(view['transaction_id'], old_id)
        restarted.close()

    def test_worker_is_nonblocking_single_flight_and_discards_completion_after_close(self):
        entered, release = threading.Event(), threading.Event()
        service = Mock()
        def slow():
            entered.set()
            release.wait(2)
            return {'phase': 'capture'}
        service.start.side_effect = slow
        jobs = PhotoJobs(service)
        self.assertTrue(jobs.submit('start'))
        self.assertTrue(entered.wait(1))
        self.assertIsNone(jobs.poll())
        self.assertFalse(jobs.submit('start'))
        jobs.close()
        release.set()
        jobs.wait_closed()
        self.assertIsNone(jobs.poll())
        self.assertFalse(jobs.submit('start'))
        service.close.assert_called_once()

    def test_drive_retention_guard_blocks_upload_without_backend_ack(self):
        from photobooth.kiosk_v2.photo_drive import RetentionGuardedSync
        self.start_review()
        path = self.service.transaction.manifest_path
        manifest = json.loads(path.read_text())
        manifest.update(drive_folder_id='test-only-folder', upload_status='PENDING_UPLOAD')
        path.write_text(json.dumps(manifest))
        client = Mock()
        client.register_retention.return_value = {}  # Old backend cannot acknowledge.
        worker = RetentionGuardedSync(self.service.store.photos_root, client, Mock())
        with patch('photobooth.kiosk_v2.photo_drive.sync_manifest') as sync:
            worker._process_pending_uploads()
            sync.assert_not_called()
            manifest = json.loads(path.read_text())
            self.assertTrue(manifest['drive_retention_error'])
            manifest['drive_retention_registered_at'] = '2026-10-23T00:00:00+00:00'
            path.write_text(json.dumps(manifest))
            worker._process_pending_uploads()
            sync.assert_called_once_with(path, client)
        client.cleanup_expired.assert_not_called()


if __name__ == '__main__':
    unittest.main()
