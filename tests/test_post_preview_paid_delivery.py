"""Post-preview original PAID Drive delivery monitor: no fake completion."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from photobooth.booth_storage import BoothWorkspace
from photobooth.post_preview_paid_delivery import OriginalPaidDeliveryMonitor
from tests.test_post_preview_paid_strips import OriginalPaidStripTests


class OriginalPaidDeliveryTests(unittest.TestCase):
    prepared=OriginalPaidStripTests.prepared
    paid_fixture=OriginalPaidStripTests.paid_fixture
    binder=OriginalPaidStripTests.binder

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.workspace=BoothWorkspace(self.root,'PB001V2S2')
        self.workspace.prepare()

    def monitor(self):
        fixture,preparer=self.prepared()
        return fixture,OriginalPaidDeliveryMonitor(preparer,allow_incomplete_fixture=True)

    def full(self,fixture,monitor):
        service=fixture.service
        monitor.enqueue(service.lease,service.group,service.templates)
        data=monitor.inspect(service.lease,service.group)
        path=self.workspace.root/data['transaction_id']/'manifest.json'
        manifest=json.loads(path.read_text(encoding='utf-8'))
        manifest['drive_retention_registered_at']='synthetic-retention-proof'
        for i,(relative,item) in enumerate(manifest['upload_files'].items(),1):
            item['status']='VERIFIED'
            item['md5_checksum']=hashlib.md5((path.parent/relative).read_bytes()).hexdigest()
            item['drive_file_id']='verifiedRemoteFile'+str(i)
        manifest['upload_status']='UPLOAD_COMPLETE'
        path.write_text(json.dumps(manifest),encoding='utf-8')
        return path

    def test_staging_does_not_publish_files_without_worker(self):
        fixture,monitor=self.monitor()
        service=fixture.service
        status=monitor.enqueue(service.lease,service.group,service.templates)
        self.assertEqual('NOT_CONFIGURED',status['worker'])
        self.assertEqual('PENDING_UPLOAD',status['upload_status'])
        self.assertFalse(status['drive_verified'])
        self.assertEqual(0,status['upload_verified'])
        self.assertEqual('OWED',status['service_status'])
        self.assertFalse(status['safe_to_release_without_original_claim'])

    def test_all_verified_files_update_only_drive_state_not_service_or_print(self):
        fixture,monitor=self.monitor()
        service=fixture.service
        self.full(fixture,monitor)
        done=monitor.inspect(service.lease,service.group)
        self.assertTrue(done['drive_verified'])
        self.assertEqual(done['upload_total'],done['upload_verified'])
        self.assertEqual('UPLOADED',service.ledger.db.execute(
            'SELECT drive_state FROM pp_paid_services').fetchone()[0])
        self.assertEqual('OWED',service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertFalse(done['print_all_submitted'])
        self.assertFalse(done['physical_paper_verified'])

    def test_fake_all_done_without_remote_md5_ack_is_rejected(self):
        fixture,monitor=self.monitor()
        service=fixture.service
        path=self.full(fixture,monitor)
        data=json.loads(path.read_text())
        first=next(iter(data['upload_files'].values()))
        first['md5_checksum']='0'*32
        path.write_text(json.dumps(data))
        with self.assertRaises(Exception):
            monitor.inspect(service.lease,service.group)
        self.assertEqual('OWED',service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_wrong_original_folder_or_corrupt_strip_blocks_delivery(self):
        fixture,monitor=self.monitor()
        service=fixture.service
        path=self.full(fixture,monitor)
        data=json.loads(path.read_text())
        data['drive_folder_url']='https://drive.google.com/drive/folders/OTHER'
        path.write_text(json.dumps(data))
        with self.assertRaises(Exception):
            monitor.inspect(service.lease,service.group)
        data['drive_folder_url']='https://drive.google.com/drive/folders/syntheticVerifiedPaid987'
        path.write_text(json.dumps(data))
        strip=next(path.parent.rglob('strip.png'))
        strip.write_bytes(b'corrupt')
        with self.assertRaises(Exception):
            monitor.inspect(service.lease,service.group)

    def test_no_second_transaction_or_print_on_repeated_poll(self):
        fixture,monitor=self.monitor()
        service=fixture.service
        self.full(fixture,monitor)
        first=monitor.inspect(service.lease,service.group)
        second=monitor.inspect(service.lease,service.group)
        self.assertEqual(first,second)
        self.assertEqual(25,len(self.workspace.ready_slots()))
        self.assertEqual(1,service.ledger.db.execute(
            'SELECT count(*) FROM pp_paid_strip_jobs').fetchone()[0])


if __name__=='__main__':
    unittest.main()
