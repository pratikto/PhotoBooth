"""AR-05 composition publication never overwrites an unacknowledged output."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoTest


class OutputJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.photo=PhotoTest(Path(self.tmp.name));self.addCleanup(self.photo.close)
        self.photo.start(get_templates(),{'template_a':2})
        for _ in range(3):self.photo.capture(np.zeros((24,32,3),dtype=np.uint8))

    def test_committed_output_has_frozen_inputs_and_exact_hash(self):
        self.photo.compose()
        m=json.loads(self.photo.transaction.manifest_path.read_text())
        intent=m['output_intents']['session_001']
        path=self.photo.transaction.folder_path/intent['path']
        self.assertEqual(intent['state'],'COMMITTED')
        self.assertEqual(intent['sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(intent['final_photos'],m['sessions'][0]['final_photos'])

    def test_lost_reply_after_output_publication_cannot_recompose_or_overwrite(self):
        def stop(stage):
            if stage=='output_published':raise RuntimeError('synthetic crash')
        with patch('photobooth.capture_journal.boundary',side_effect=stop):
            with self.assertRaises(RuntimeError):self.photo.compose()
        output=self.photo.store.output_path(self.photo.transaction,self.photo.session.plan)
        before=output.read_bytes()
        with self.assertRaises(RuntimeError):self.photo.compose()
        self.assertEqual(output.read_bytes(),before)
        self.assertIsNone(json.loads(self.photo.transaction.manifest_path.read_text())['sessions'][0]['output_path'])

    def test_tampered_capture_cannot_be_composed_as_original_paid_photo(self):
        path=self.photo.session.initial_photo_paths[0]
        path.write_bytes(self.photo.session.initial_photo_paths[1].read_bytes()+b'tampered')
        with self.assertRaises(RuntimeError):self.photo.compose()
