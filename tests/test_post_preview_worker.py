"""Original PhotoJobs + private service fixtures, no device/payment authority."""
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import numpy as np

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.post_preview_photos import PrivatePhotoService
from photobooth.post_preview_store import DraftHeld


class PrivateWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.service = PrivatePhotoService(self.root)
        self.addCleanup(self.shutdown)
        self.templates = get_templates()
        self.frame = np.zeros((32, 48, 3), dtype=np.uint8)
        self.frame[:, :24] = (0, 0, 255)
        self.frame[:, 24:] = (255, 0, 0)

    def shutdown(self):
        self.service.close()
        self.service.wait_closed()

    def start(self):
        self.service.prepare()
        return self.service.start(self.templates, {'template_a': 2, 'template_b': 1})

    def capture_args(self, view=None):
        view = view or self.service.snapshot()
        return (self.frame, view['capture_slot'], view['revision'], view['retake'], view['generation'])

    def trio(self):
        for _ in range(3): self.service.capture(*self.capture_args())

    def finish(self):
        self.start()
        self.trio()
        self.service.compose()
        self.service.next()
        self.trio()
        self.service.compose()
        return self.service.next()

    def test_multidesign_worker_reaches_all_designs_without_any_delivery_transport(self):
        result = self.finish()
        self.assertEqual('final_preview', result['phase'])
        self.assertEqual(25000, result['amount'])
        self.assertEqual([2, 1], [d['copies'] for d in result['designs']])
        self.assertEqual([(160, 480)]*2, [d['strip'].size for d in result['designs']])
        self.assertFalse(result['print_available'])
        self.assertFalse(result['auto_print'])
        self.assertIsNone(result['download_qr'])
        self.assertFalse(result['drive_enabled'])
        self.assertEqual(0, self.service.ledger.db.execute('SELECT count(*) FROM pp_checkout_intents').fetchone()[0])

    def test_final_cart_edit_keeps_original_template_quota_and_photos(self):
        self.start()
        self.trio()
        self.service.retake(1)
        self.service.capture(*self.capture_args())
        self.service.compose()
        self.service.next()
        self.trio()
        self.service.compose()
        self.service.next()
        before = {p: p.read_bytes() for p in (self.root/'media').rglob('*.jpg')}
        self.service.edit()
        view = self.service.start(self.templates, {'template_a': 9})
        self.assertEqual('review', view['phase'])
        self.assertTrue(view['retake_used'])
        self.assertEqual(3, len(view['thumbnails']))
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        with self.assertRaises(DraftHeld): self.service.retake(0)

    def test_stale_capture_revision_and_role_do_not_take_next_photo(self):
        original = self.start()
        args = self.capture_args(original)
        self.service.capture(*args)
        with self.assertRaises(DraftHeld): self.service.capture(*args)
        self.assertEqual(1, self.service.snapshot()['captured'])

    def test_hide_is_immediate_and_late_snapshot_cannot_expose_old_media(self):
        self.start()
        self.trio()
        entered = threading.Event()
        release = threading.Event()
        original = self.service.photos.inspect
        def blocked(*args):
            entered.set()
            release.wait(3)
            return original(*args)
        outcomes = []
        with patch.object(self.service.photos, 'inspect', side_effect=blocked):
            worker = threading.Thread(target=lambda: outcomes.append(self.service.snapshot()))
            worker.start()
            self.assertTrue(entered.wait(3))
            started = time.monotonic()
            self.service.hide_private()
            self.assertLess(time.monotonic()-started, .1)
            self.assertEqual({'phase': 'hold'}, self.service.snapshot())
            release.set()
            worker.join(5)
        self.assertEqual([{'phase': 'hold'}], outcomes)

    def test_restart_has_no_automatic_photo_restoration_or_new_visitor(self):
        self.start()
        self.trio()
        other = PrivatePhotoService(self.root)
        try:
            view = other.prepare()
            self.assertEqual('hold', view['phase'])
            self.assertNotIn('thumbnails', view)
            with self.assertRaises(DraftHeld): other.start(self.templates, {'template_b': 1})
        finally:
            other.close()
            other.wait_closed()

    def test_retire_records_distinct_event_and_never_proves_booth_free(self):
        self.start()
        self.service.retire('APP_SUSPENDED')
        self.assertEqual({'phase': 'hold'}, self.service.snapshot())
        row = self.service.ledger.db.execute('SELECT * FROM pp_drafts').fetchone()
        self.assertEqual(0, row['closed'])
        self.assertEqual('APP_SUSPENDED', row['lifecycle'])

    def test_original_photojobs_dispatches_one_capture_and_rejects_repeated_taps(self):
        self.start()
        jobs = PhotoJobs(service=self.service)
        entered, release = threading.Event(), threading.Event()
        original = self.service.capture
        def blocked(*args):
            entered.set()
            release.wait(3)
            return original(*args)
        with patch.object(self.service, 'capture', side_effect=blocked):
            self.assertTrue(jobs.submit('capture', *self.capture_args()))
            self.assertTrue(entered.wait(3))
            self.assertFalse(jobs.submit('capture', *self.capture_args()))
            release.set()
            deadline = time.monotonic()+5
            outcome = None
            while outcome is None and time.monotonic()<deadline:
                outcome = jobs.poll()
                if outcome is None: time.sleep(.01)
        self.assertIsNotNone(outcome)
        self.assertIsNone(outcome.error)
        self.assertEqual(1, outcome.value['captured'])

    def test_wrong_generation_frame_type_and_template_cannot_authorize_shutter(self):
        view = self.start()
        args = list(self.capture_args(view))
        args[-1] += 1
        with self.assertRaises(DraftHeld): self.service.capture(*args)
        args = list(self.capture_args(view))
        args[0] = self.frame.astype('float32')
        with self.assertRaises(ValueError): self.service.capture(*args)
        with self.assertRaises(DraftHeld): self.service.review('template_l')
        self.assertFalse(list((self.root/'media').rglob('*.jpg')))


if __name__ == '__main__': unittest.main()
