"""Exact approved JPEG import into one paid original folder without upload/print."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photobooth.booth_storage import BoothWorkspace
from photobooth.post_preview_paid_media import OriginalPaidMediaImporter
from tests.test_post_preview_paid_drive import OriginalPaidDriveReservationTests


class OriginalPaidMediaImportTests(unittest.TestCase):
    paid_fixture=OriginalPaidDriveReservationTests.paid_fixture
    binder=OriginalPaidDriveReservationTests.binder

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.workspace=BoothWorkspace(self.root,'PB001V2S2')
        self.workspace.prepare()

    def fixture_with_verified_folder(self):
        fixture=self.paid_fixture()
        def remote(manifest):
            return dict(transaction_id=manifest['transaction_id'],
                folder_id='syntheticVerifiedPaid987',
                folder_url='https://drive.google.com/drive/folders/syntheticVerifiedPaid987',
                link_verified=True,photo_number_layout=1)
        with patch.object(fixture.drive,'bind_transaction',side_effect=remote):
            binder=self.binder(fixture)
            first=binder.bind(fixture.service.lease,fixture.service.group,fixture.service.templates)
        return fixture,binder,first

    def test_paid_raw_media_import_keeps_original_bytes_and_offline_upload(self):
        fixture,binder,folder=self.fixture_with_verified_folder()
        importer=OriginalPaidMediaImporter(binder,allow_incomplete_fixture=True)
        result=importer.prepare(fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertEqual(folder['transaction_id'],result['transaction_id'])
        self.assertEqual('STAGED_PRIVATE',result['status'])
        self.assertFalse(result['print_authorized'])
        self.assertFalse(result['upload_authorized'])
        self.assertEqual(3,result['raw_count'])
        file=Path(self.workspace.root/folder['transaction_id']/'manifest.json')
        saved=json.loads(file.read_text(encoding='utf-8'))
        self.assertEqual('POST_PREVIEW_PAID',saved['purpose'])
        self.assertFalse(saved['drive_intent'])
        self.assertTrue(saved['paid_media_import_ready'])
        self.assertEqual(3,len(saved['sessions'][0]['raw_photos']))
        for record in saved['sessions'][0]['raw_photos']:
            path=file.parent/record['path']
            self.assertTrue(path.is_file())
            self.assertIn(record['path'],saved['upload_files'])
            self.assertEqual('LOCAL_ONLY',saved['upload_files'][record['path']]['status'])
        self.assertEqual('OWED',fixture.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertFalse(list(file.parent.rglob('strip.png')))

    def test_reimport_same_files_and_original_transaction_after_restart(self):
        fixture,binder,_=self.fixture_with_verified_folder()
        importer=OriginalPaidMediaImporter(binder,allow_incomplete_fixture=True)
        first=importer.prepare(fixture.service.lease,fixture.service.group,fixture.service.templates)
        file=self.workspace.root/first['transaction_id']/'manifest.json'
        original=json.loads(file.read_text(encoding='utf-8'))
        returned=OriginalPaidMediaImporter(self.binder(fixture),
            allow_incomplete_fixture=True).prepare(
                fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertEqual(first,returned)
        self.assertEqual(original,json.loads(file.read_text(encoding='utf-8')))
        self.assertEqual(25,len(self.workspace.ready_slots()))

    def test_frozen_private_jpeg_tamper_does_not_import_and_never_fabricates(self):
        fixture,binder,folder=self.fixture_with_verified_folder()
        from photobooth.post_preview_paid_media import OriginalPaidMediaImporter
        source=next((fixture.service.root/'media').rglob('photo_01.jpg'))
        source.write_bytes(b'CORRUPT')
        with self.assertRaises(Exception):
            OriginalPaidMediaImporter(binder,allow_incomplete_fixture=True).prepare(
                fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertFalse((self.workspace.root/folder['transaction_id']/'manifest.json').exists())
        self.assertEqual('OWED',fixture.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_foreign_paid_manifest_is_not_reused_or_overwritten(self):
        fixture,binder,folder=self.fixture_with_verified_folder()
        manifest=self.workspace.root/folder['transaction_id']/'manifest.json'
        manifest.write_text(json.dumps({'purpose':'FOREIGN','transaction_id':folder['transaction_id']}))
        with self.assertRaises(Exception):
            OriginalPaidMediaImporter(binder,allow_incomplete_fixture=True).prepare(
                fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertEqual('FOREIGN',json.loads(manifest.read_text())['purpose'])


if __name__=='__main__': unittest.main()
