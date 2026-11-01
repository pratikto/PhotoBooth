"""Purchased frozen strips: real verified Drive URL but no print or cloud I/O."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from photobooth.booth_storage import BoothWorkspace
from photobooth.post_preview_paid_media import OriginalPaidMediaImporter
from photobooth.post_preview_paid_strips import OriginalPaidStripPreparer
from tests.test_post_preview_paid_drive import OriginalPaidDriveReservationTests


class OriginalPaidStripTests(unittest.TestCase):
    paid_fixture=OriginalPaidDriveReservationTests.paid_fixture
    binder=OriginalPaidDriveReservationTests.binder

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.workspace=BoothWorkspace(self.root,'PB001V2S2')
        self.workspace.prepare()

    def prepared(self):
        fixture=self.paid_fixture()
        binder=self.binder(fixture)
        def remote(manifest):
            return dict(transaction_id=manifest['transaction_id'],
                folder_id='syntheticVerifiedPaid987',link_verified=True,photo_number_layout=1,
                folder_url='https://drive.google.com/drive/folders/syntheticVerifiedPaid987')
        with patch.object(fixture.drive,'bind_transaction',side_effect=remote):
            binder.bind(fixture.service.lease,fixture.service.group,fixture.service.templates)
        importer=OriginalPaidMediaImporter(binder,allow_incomplete_fixture=True)
        return fixture,OriginalPaidStripPreparer(importer,allow_incomplete_fixture=True)

    def test_verified_paid_original_three_photos_and_one_qr_strip(self):
        fixture,preparer=self.prepared()
        result=preparer.prepare(fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertEqual('OWED_PREPARED',result['status'])
        self.assertFalse(result['printing_started'])
        self.assertFalse(result['public_upload_started'])
        self.assertEqual(1,len(result['jobs']))
        job=result['jobs'][0]
        with Image.open(job['output_path']) as image:
            self.assertEqual((640,1920),image.size)
            self.assertEqual('PNG',image.format)
        self.assertEqual(job['output_sha256'],
                         hashlib.sha256(Path(job['output_path']).read_bytes()).hexdigest())
        manifest=json.loads((self.workspace.root/result['transaction_id']/'manifest.json').read_text())
        self.assertTrue(manifest['drive_intent'])
        self.assertEqual('PENDING_UPLOAD',manifest['upload_status'])
        self.assertEqual('READY_FOR_PAID_DELIVERY',manifest['status'])
        self.assertEqual('https://drive.google.com/drive/folders/syntheticVerifiedPaid987',
                         manifest['drive_folder_url'])
        self.assertEqual(3,len(manifest['sessions'][0]['raw_photos']))
        self.assertEqual(3,len(manifest['sessions'][0]['final_photos']))
        self.assertEqual('OWED',fixture.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual('PREPARED',fixture.service.ledger.db.execute(
            'SELECT state FROM pp_paid_strip_jobs').fetchone()[0])

    def test_idempotent_strip_staging_reuses_exact_original_job_and_png(self):
        fixture,preparer=self.prepared()
        first=preparer.prepare(fixture.service.lease,fixture.service.group,fixture.service.templates)
        second=OriginalPaidStripPreparer(
            OriginalPaidMediaImporter(self.binder(fixture),allow_incomplete_fixture=True),
            allow_incomplete_fixture=True).prepare(fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertEqual(first,second)
        self.assertEqual(1,fixture.service.ledger.db.execute(
            'SELECT count(*) FROM pp_paid_strip_jobs').fetchone()[0])
        self.assertEqual(25,len(self.workspace.ready_slots()))

    def test_corrupt_existing_strip_blocks_replacement_and_does_not_reprint(self):
        fixture,preparer=self.prepared()
        first=preparer.prepare(fixture.service.lease,fixture.service.group,fixture.service.templates)
        output=Path(first['jobs'][0]['output_path'])
        output.write_bytes(b'CORRUPT')
        with self.assertRaises(Exception):
            preparer.prepare(fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertEqual(b'CORRUPT',output.read_bytes())
        self.assertEqual('PREPARED',fixture.service.ledger.db.execute(
            'SELECT state FROM pp_paid_strip_jobs').fetchone()[0])


if __name__=='__main__':unittest.main()
