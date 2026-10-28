"""AR-04 actual file/process crash windows and immutable saved capture identity."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from photobooth.catalog import get_templates
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import build_session_plans


class CaptureJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.store=TransactionStore(self.root/'photos',self.root/'counter.json',capture_protocol=1)
        self.plan=build_session_plans(get_templates(),{'template_a':1})[0]
        self.tx=self.store.start_transaction([self.plan])
        self.image=Image.new('RGB',(32,24),(17,83,201))

    def test_committed_photo_has_verified_intent_hash_and_no_overwrite_retry(self):
        path=self.store.save_raw_photo(self.tx,self.plan,self.image,'photo_01.jpg','capture')
        before=path.read_bytes();m=json.loads(self.tx.manifest_path.read_text())
        intent=next(iter(m['capture_intents'].values()))
        self.assertEqual(intent['state'],'COMMITTED')
        self.assertEqual(intent['sha256'],hashlib.sha256(before).hexdigest())
        self.assertEqual(intent['size_bytes'],len(before))
        with self.assertRaises(RuntimeError):
            self.store.save_raw_photo(self.tx,self.plan,Image.new('RGB',(32,24),'red'),'photo_01.jpg','capture')
        self.assertEqual(path.read_bytes(),before)

    def test_existing_unacknowledged_photo_is_never_replaced_or_adopted_by_save(self):
        path=self.tx.folder_path/'raw'/self.plan.session_id/'photo_01.jpg'
        path.parent.mkdir(parents=True);self.image.save(path)
        before=path.read_bytes()
        with self.assertRaises(RuntimeError):self.store.save_raw_photo(self.tx,self.plan,self.image,'photo_01.jpg','capture')
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(json.loads(self.tx.manifest_path.read_text())['sessions'][0]['raw_photos'],[])

    def test_abrupt_process_exit_at_every_write_boundary_preserves_evidence(self):
        for stage in ('intent','temporary','staged','published','committed'):
            with self.subTest(stage=stage):
                root=self.root/stage
                result=subprocess.run([sys.executable,'-m','tests.capture_crash_fixture',str(root),stage],
                    cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,timeout=20)
                self.assertEqual(result.returncode,71,result.stderr)
                manifest=next((root/'photos').glob('*/manifest.json'))
                data=json.loads(manifest.read_text());intent=next(iter(data['capture_intents'].values()))
                path=manifest.parent/intent['path']
                self.assertEqual(len(data['sessions'][0]['raw_photos']),1 if stage=='committed' else 0)
                self.assertEqual(path.exists(),stage in {'published','committed'})
                if path.exists():
                    with Image.open(path) as image:image.verify()
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),intent['sha256'])

    def test_failure_before_publication_never_acknowledges_a_capture(self):
        with patch('os.link',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.store.save_raw_photo(self.tx,self.plan,self.image,'photo_01.jpg','capture')
        m=json.loads(self.tx.manifest_path.read_text())
        self.assertEqual(m['sessions'][0]['raw_photos'],[])
        self.assertEqual(next(iter(m['capture_intents'].values()))['state'],'STAGED')

    def test_symlink_target_is_rejected_without_touching_external_bytes(self):
        target=self.root/'external.jpg';self.image.save(target);before=target.read_bytes()
        path=self.tx.folder_path/'raw'/self.plan.session_id/'photo_01.jpg';path.parent.mkdir(parents=True)
        try:path.symlink_to(target)
        except (OSError,NotImplementedError):self.skipTest('Symlink creation not supported')
        with self.assertRaises((RuntimeError,ValueError)):
            self.store.save_raw_photo(self.tx,self.plan,self.image,'photo_01.jpg','capture')
        self.assertEqual(target.read_bytes(),before)

    def test_archive_path_is_rejected_before_creating_or_descending_it(self):
        with self.assertRaises(ValueError):
            TransactionStore(self.root/'old'/'photos',self.root/'counter2.json',capture_protocol=1)
        self.assertFalse((self.root/'old').exists())

    def test_retake_selection_and_consumed_quota_commit_with_same_saved_bytes(self):
        from photobooth.kiosk_v2.photos import PhotoTest
        import numpy as np
        photo=PhotoTest(self.root/'v2');self.addCleanup(photo.close)
        photo.start(get_templates(),{'template_a':2})
        frame=np.zeros((24,32,3),dtype=np.uint8)
        for _ in range(3):photo.capture(frame)
        photo.retake(1)
        before=json.loads(photo.transaction.manifest_path.read_text())
        self.assertEqual(before['sessions'][0]['pending_retake_index'],1)
        self.assertFalse(before['sessions'][0]['retake_used'])
        with patch('photobooth.capture_journal.boundary',side_effect=lambda stage: (_ for _ in ()).throw(RuntimeError('lost local reply')) if stage=='committed' else None):
            with self.assertRaises(RuntimeError):photo.capture(frame)
        after=json.loads(photo.transaction.manifest_path.read_text())
        record=after['sessions'][0]
        self.assertTrue(record['retake_used'])
        self.assertEqual(record['selected_photo'],record['raw_photos'][1]['path'])
        self.assertNotIn('pending_retake_index',record)
        originals=[(photo.transaction.folder_path/p['path']).read_bytes() for p in record['raw_photos']]
        with self.assertRaises(RuntimeError):photo.capture(frame)
        self.assertEqual([(photo.transaction.folder_path/p['path']).read_bytes() for p in record['raw_photos']],originals)
