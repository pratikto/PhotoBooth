"""Real private JPEGs with synthetic pixels, never live camera/print/Drive."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from photobooth.capture_journal import CaptureRecoveryRequired
from photobooth.catalog import get_templates
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_store import DraftHeld, DraftLease, PostPreviewStore


class PrivateCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = PostPreviewStore(self.root/'drafts.db')
        self.addCleanup(self.ledger.close)
        self.templates = get_templates()
        self.a, self.b = self.templates[:2]
        self.lease = self.ledger.create('PB001', 'visitA', {'template_a': 2, 'template_b': 1})
        self.photos = PrivateDraftPhotos(self.ledger, self.root/'private')
        # Asymmetric pixels catch accidental capture mirroring.
        self.image = Image.new('RGB', (48, 32), 'red')
        self.image.paste((0, 0, 255), (24, 0, 48, 32))

    def revision(self):
        return self.ledger.inspect(self.lease)['revision']

    def capture(self, template, slot, retake=False):
        return self.photos.capture(self.lease, template, self.image, slot=slot,
                                   revision=self.revision(), retake=retake)

    def trio(self, template):
        return [self.capture(template, n) for n in range(3)]

    def select_retake(self, template, slot):
        self.photos.request_retake(self.lease, template, slot, revision=self.revision())

    def test_three_originals_and_independent_retake_per_template(self):
        for template in (self.a, self.b):
            self.trio(template)
            self.select_retake(template, 1)
            retake = self.capture(template, 1, True)
            state = self.photos.inspect(self.lease, template)
            self.assertEqual(3, state['original_count'])
            self.assertTrue(state['retake_saved'])
            self.assertEqual(retake, state['final_paths'][1])
            with self.assertRaises(DraftHeld): self.select_retake(template, 2)
        self.assertEqual(8, len(list((self.root/'private').rglob('*.jpg'))))

    def test_all_twelve_templates_capture_once_despite_nine_copies(self):
        self.ledger.edit(self.lease, {t.template_id: 9 for t in self.templates}, revision=self.revision())
        for template in self.templates:
            self.trio(template)
            self.select_retake(template, 0)
            self.capture(template, 0, True)
        self.assertEqual(48, len(list((self.root/'private').rglob('*.jpg'))))
        self.assertFalse(list((self.root/'private').rglob('unused-counter.json')))

    def test_original_orientation_and_private_local_metadata(self):
        path = self.capture(self.a, 0)
        with Image.open(path) as saved:
            self.assertGreater(saved.getpixel((3, 3))[0], saved.getpixel((3, 3))[2])
            self.assertGreater(saved.getpixel((44, 3))[2], saved.getpixel((44, 3))[0])
        state = self.photos.inspect(self.lease, self.a)
        data = json.loads(state['manifest_path'].read_text())
        self.assertEqual('IN_PROGRESS', data['status'])
        self.assertIsNone(data['drive_folder_url'])
        self.assertFalse(data['financial_transaction'])
        self.assertFalse(data['payment_enabled'])
        self.assertTrue(all(v['status'] == 'LOCAL_ONLY' for v in data['upload_files'].values()))
        self.assertFalse(data.get('test_print_jobs'))

    def test_deselection_restart_reselection_preserves_exact_retaken_bytes(self):
        self.trio(self.a)
        self.select_retake(self.a, 2)
        path = self.capture(self.a, 2, True)
        before = path.read_bytes()
        lineage = self.photos.inspect(self.lease, self.a)['lineage_id']
        self.ledger.edit(self.lease, {'template_b': 3}, revision=self.revision())
        with self.assertRaises(DraftHeld): self.photos.inspect(self.lease, self.a)
        other = PostPreviewStore(self.root/'drafts.db')
        self.addCleanup(other.close)
        adapter = PrivateDraftPhotos(other, self.root/'private')
        other.edit(self.lease, {'template_a': 9}, revision=self.revision())
        state = adapter.inspect(self.lease, self.a)
        self.assertEqual(lineage, state['lineage_id'])
        self.assertTrue(state['retake_consumed'])
        self.assertEqual(before, state['final_paths'][2].read_bytes())
        with self.assertRaises(DraftHeld): self.select_retake(self.a, 0)

    def test_retake_selection_survives_before_any_retake_file_write(self):
        self.trio(self.a)
        self.select_retake(self.a, 1)
        restarted = PrivateDraftPhotos(self.ledger, self.root/'private')
        state = restarted.inspect(self.lease, self.a)
        self.assertTrue(state['retake_consumed'])
        self.assertFalse(state['retake_saved'])
        self.capture(self.a, 1, True)
        with self.assertRaises(DraftHeld): self.select_retake(self.a, 0)

    def test_duplicate_callback_returns_original_bytes_and_never_advances_slot(self):
        path = self.capture(self.a, 0)
        before = path.read_bytes()
        revision = self.revision()
        other = self.photos.capture(self.lease, self.a, Image.new('RGB', (48, 32), 'green'),
                                    slot=0, revision=revision)
        self.assertEqual(path, other)
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(revision, self.revision())
        self.assertEqual(1, self.photos.inspect(self.lease, self.a)['original_count'])

    def test_wrong_slot_role_revision_and_retired_worker_are_rejected(self):
        with self.assertRaises(DraftHeld): self.capture(self.a, 1)
        with self.assertRaises(DraftHeld): self.capture(self.a, 0, True)
        with self.assertRaises(ValueError): self.capture(self.a, True)
        with self.assertRaises(DraftHeld):
            self.photos.capture(self.lease, self.a, self.image, slot=0, revision=0)
        self.ledger.lifecycle_event(self.lease, 'APP_SUSPENDED')
        with self.assertRaises(DraftHeld):
            self.photos.capture(self.lease, self.a, self.image, slot=0, revision=1)
        self.assertFalse(list((self.root/'private').rglob('*.jpg')))

    def test_lost_commit_reply_recovers_original_without_repeated_shutter(self):
        def fault(stage):
            if stage == 'committed': raise RuntimeError('lost local reply')
        with patch('photobooth.capture_journal.boundary', side_effect=fault):
            with self.assertRaises(RuntimeError): self.capture(self.a, 0)
        path = self.capture(self.a, 0)
        self.assertEqual(1, self.photos.inspect(self.lease, self.a)['original_count'])
        self.assertEqual(1, len(list(path.parent.glob('photo_01.jpg'))))

    def test_recover_staged_capture_after_publication_failure(self):
        with patch('photobooth.capture_journal.os.link', side_effect=OSError('disk unavailable')):
            with self.assertRaises(OSError): self.capture(self.a, 0)
        state = self.photos.inspect(self.lease, self.a)
        self.assertEqual(1, state['original_count'])
        path = state['final_paths'][0]
        data = json.loads(state['manifest_path'].read_text())
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         data['sessions'][0]['raw_photos'][0]['sha256'])

    def test_unhashed_temporary_bytes_are_held_without_overwrite(self):
        def fault(stage):
            if stage == 'temporary': raise RuntimeError('write interrupted')
        with patch('photobooth.capture_journal.boundary', side_effect=fault):
            with self.assertRaises(RuntimeError): self.capture(self.a, 0)
        files = {p: p.read_bytes() for p in (self.root/'private').rglob('*.jpg')}
        with self.assertRaises(CaptureRecoveryRequired): self.capture(self.a, 0)
        self.assertEqual(files, {p: p.read_bytes() for p in files})

    def test_changed_artwork_and_tampered_media_are_held(self):
        path = self.capture(self.a, 0)
        artwork = self.root/'changed.png'
        shutil.copyfile(self.a.artwork_path, artwork)
        artwork.write_bytes(artwork.read_bytes()+b'changed')
        with self.assertRaises(CaptureRecoveryRequired):
            self.photos.inspect(self.lease, replace(self.a, artwork_path=artwork))
        path.write_bytes(b'not original media')
        with self.assertRaises(CaptureRecoveryRequired): self.photos.inspect(self.lease, self.a)

    def test_capture_before_frame_intent_can_continue_but_never_auto_shoots(self):
        def fault(stage):
            if stage == 'intent': raise RuntimeError('before frame')
        with patch('photobooth.capture_journal.boundary', side_effect=fault):
            with self.assertRaises(RuntimeError): self.capture(self.a, 0)
        self.assertEqual(0, self.photos.inspect(self.lease, self.a)['original_count'])
        self.capture(self.a, 0)
        self.assertEqual(1, self.photos.inspect(self.lease, self.a)['original_count'])

    def test_real_process_exits_keep_original_identity_bytes_and_retake_quota(self):
        for retake in (False, True):
            for stage in ('intent', 'temporary', 'staged', 'published', 'committed'):
                with self.subTest(retake=retake, stage=stage):
                    root = self.root / (str(retake)+'-'+stage)
                    child = subprocess.run([sys.executable, '-m', 'tests.post_preview_crash_fixture',
                        str(root), stage, str(int(retake))], capture_output=True, text=True, timeout=20)
                    self.assertEqual(73, child.returncode, child.stderr)
                    ledger = PostPreviewStore(root/'drafts.db')
                    try:
                        row = ledger.db.execute('SELECT * FROM pp_drafts').fetchone()
                        lease = DraftLease(row['draft_id'], row['booth_id'], row['visit_id'], row['generation'])
                        adapter = PrivateDraftPhotos(ledger, root/'private')
                        if stage == 'temporary':
                            with self.assertRaises(CaptureRecoveryRequired): adapter.inspect(lease, self.a)
                            continue
                        state = adapter.inspect(lease, self.a)
                        saved = stage in ('staged', 'published', 'committed')
                        self.assertEqual(3 if retake else int(saved), state['original_count'])
                        self.assertEqual(retake, state['retake_consumed'])
                        self.assertEqual(retake and saved, state['retake_saved'])
                        if retake:
                            with self.assertRaises(DraftHeld):
                                adapter.request_retake(lease, self.a, 0, revision=ledger.inspect(lease)['revision'])
                        before = {p: p.read_bytes() for p in state['final_paths']}
                        adapter.inspect(lease, self.a)
                        self.assertEqual(before, {p: p.read_bytes() for p in before})
                    finally:
                        ledger.close()


if __name__ == '__main__':
    unittest.main()
