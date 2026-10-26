"""Reconnect uses the same local claim, immutable deadlines and original queue."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from PIL import Image
from photobooth.booth_storage import BoothWorkspace
from photobooth.booth_sync import BoothDriveClient, BoothDriveWorker
from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError
from photobooth.retention import retention_metadata
from photobooth.transaction_store import TransactionStore
from photobooth.catalog import get_templates
from photobooth.workflow import build_session_plans


class BoothSyncTests(unittest.TestCase):
    def test_offline_claim_reconnect_keeps_bytes_id_deadline_and_binding_on_stale_save(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder,'PB001V2S2');w.prepare();slot=w.claim()
            store=TransactionStore(w.root,w.counter_path,w.booth_id,layout_version=2)
            plan=build_session_plans(get_templates(),{'template_a':1})[0]
            tx=store.start_transaction([plan],transaction_id=slot['transaction_id'],folder_path=slot['staging_path'])
            tx.manifest.update(drive_intent=True,drive_claim_token=slot['claim_token'],upload_status='PENDING_DRIVE_BINDING')
            store._write_manifest(tx)
            raw=store.save_raw_photo(tx,plan,Image.new('RGB',(80,50),'red'),'photo_01.jpg','capture')
            before=raw.read_bytes();started=tx.manifest['created_at']
            client=Mock();client.reserve_transactions.return_value=[];client.bind_transaction.side_effect=DriveApiError('offline',503)
            worker=BoothDriveWorker(w,client);worker.run_once()
            self.assertIsNone(json.loads(tx.manifest_path.read_text())['drive_folder_id'])
            self.assertEqual(raw.read_bytes(),before)
            client.bind_transaction.side_effect=None
            client.bind_transaction.return_value={'folder_id':'bound','folder_url':'https://drive.google.com/drive/folders/bound'}
            client.register_retention.return_value=retention_metadata(tx.transaction_id,started)
            client.upload_file.return_value={'id':'image','size':str(len(before)),'md5Checksum':hashlib.md5(before).hexdigest()}
            worker.run_once()
            remote=json.loads(tx.manifest_path.read_text());self.assertEqual(remote['drive_folder_id'],'bound')
            self.assertTrue(remote['drive_retention_registered_at']);self.assertEqual(remote['upload_files']['Photo/01/raw/photo_01.jpg']['status'],'VERIFIED')
            store.complete_transaction(tx)  # Stale controller must not erase binding/progress.
            final=json.loads(tx.manifest_path.read_text());self.assertEqual(final['upload_status'],'UPLOAD_COMPLETE')
            self.assertEqual(final['drive_folder_id'],'bound');self.assertEqual(final['created_at'],started)
            self.assertEqual(raw.read_bytes(),before);self.assertEqual(w.root.name,'PB001')
            worker.run_once();self.assertEqual(client.upload_file.call_count,1)

    def test_missing_retention_clock_does_not_upload_or_block_new_local_claims(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();slot=w.claim();store=TransactionStore(w.root,w.counter_path,w.booth_id,layout_version=2)
            plans=build_session_plans(get_templates(),{'template_a':1})
            tx=store.start_transaction(plans,transaction_id=slot['transaction_id'],folder_path=slot['staging_path'])
            tx.manifest.update(drive_intent=True,drive_claim_token=slot['claim_token']);store._write_manifest(tx)
            client=Mock();client.reserve_transactions.return_value=[];client.bind_transaction.return_value={'folder_id':'bound','folder_url':'https://drive.google.com/drive/folders/bound'}
            client.register_retention.side_effect=DriveApiError('clock missing',409)
            BoothDriveWorker(w,client).run_once();client.upload_file.assert_not_called()
            self.assertNotEqual(w.claim()['transaction_id'],slot['transaction_id'])

    def test_client_reuses_existing_transport_and_rejects_mismatched_bind_chunk(self):
        session=Mock();existing=AppsScriptDriveClient('https://script.google.com/macros/s/fixture/exec','fixture',session=session)
        client=BoothDriveClient(existing,'PB001V2S2')
        session.post.return_value.status_code=200
        session.post.return_value.json.return_value={'ok':True,'storage_layout':2,'slots':[]}
        client.reserve_transactions([])
        body=session.post.call_args.kwargs['json'];self.assertEqual(body['token'],'fixture');self.assertEqual(body['storage_layout'],2)
        self.assertEqual(body['booth_id'],'PB001V2S2')
        session.post.return_value.json.return_value={'ok':True,'storage_layout':2,'transaction_id':'different','folder_id':'x'}
        with self.assertRaises(DriveApiError):client.bind_transaction({'transaction_id':'PB001V2S2_00000001','drive_claim_token':'a'*32,'created_at':'2026-10-26T00:00:00Z','sessions':[{}]})
        session.post.return_value.json.return_value={'ok':True,'data':'eA==','offset':1,'size':2,'md5':'a'*32}
        with self.assertRaises(DriveApiError):client.asset_chunk({'id':'x','path':'Global_Advertisement/x.png','size':2,'md5':'a'*32},0,1)

    def test_configured_layout2_without_credentials_is_offline_ready_and_never_falls_back_to_legacy_oauth(self):
        from photobooth.kiosk_v2.photos import configured_test
        with TemporaryDirectory() as folder, patch.dict('os.environ', {
                'PHOTOBOOTH_V2_STORAGE':'2','PHOTOBOOTH_V2_PRINT':'0','PHOTOBOOTH_V2_DRIVE':'1',
                'PHOTOBOOTH_V2_BOOTH_ID':'PB001V2','PHOTOBOOTH_V2_STORAGE_ROOT':str(Path(folder)/'Photobooth')}), patch(
                'photobooth.drive_storage.AppsScriptDriveClient.from_configuration',return_value=None), patch(
                'photobooth.drive_storage.GoogleDriveClient.from_environment',side_effect=AssertionError('legacy OAuth')):
            service=configured_test(Path(folder)/'data'/'kiosk-v2-p3',configuration_root=folder)
            try:
                view=service.prepare()
                self.assertEqual(view['storage_layout'],2);self.assertTrue(view['drive_enabled'])
                self.assertTrue(view['drive_ready']);self.assertTrue(view['drive_error'])
                self.assertEqual(service.workspace.root.name,'PB001');self.assertEqual(len(service.workspace.ready_slots()),25)
                self.assertIsNone(service.drive_worker)
                self.assertFalse((Path(folder)/'data'/'kiosk-v2-p3'/'photos').exists())
            finally:service.close()


    def test_flat_upload_mapping_keeps_sessions_distinct_and_verifies_real_bytes(self):
        session=Mock();existing=AppsScriptDriveClient('https://script.google.com/macros/s/fixture/exec','fixture',session=session)
        client=BoothDriveClient(existing,'PB001V2S2')
        session.post.return_value.status_code=200
        with TemporaryDirectory() as folder:
            path=Path(folder)/'strip.png';path.write_bytes(b'fixture pixels')
            session.post.return_value.json.return_value={'ok':True,'file':{'id':'file',
                'size_bytes':path.stat().st_size,'md5_checksum':hashlib.md5(path.read_bytes()).hexdigest()}}
            for number in ('01','02'):
                client.upload_file('folder','PB001V2S2_00000001',f'Photo/{number}/color/strip.png',path)
                payload=session.post.call_args.kwargs['json']
                self.assertEqual(payload['relative_path'],f'color/session_{int(number):03d}_strip.png')
                self.assertEqual(payload['filename'],f'session_{int(number):03d}_strip.png')

    def test_private_reserve_response_is_rejected_before_its_url_can_reach_print(self):
        session=Mock();existing=AppsScriptDriveClient('https://script.google.com/macros/s/fixture/exec','fixture',session=session)
        client=BoothDriveClient(existing,'PB001V2S2');session.post.return_value.status_code=200
        slot={'transaction_id':'PB001V2S2_00000001','folder_id':'folder',
              'folder_url':'https://drive.google.com/drive/folders/folder','status':'READY'}
        session.post.return_value.json.return_value={'ok':True,'storage_layout':2,'slots':[slot]}
        with self.assertRaises(DriveApiError):client.reserve_transactions([{'transaction_id':slot['transaction_id']}])
        slot.update(photo_number_layout=1,link_verified=True)
        self.assertEqual(client.reserve_transactions([{'transaction_id':slot['transaction_id']}])[0]['folder_id'],'folder')

    def test_layout2_background_delivery_completes_and_exposes_qr_without_print_replay(self):
        import numpy as np
        from photobooth.kiosk_v2.photos import PhotoTest
        with TemporaryDirectory() as folder:
            workspace=BoothWorkspace(folder,'PB001V2S2')
            service=PhotoTest(folder,workspace=workspace,drive_requested=True)
            try:
                service.prepare();service.start(get_templates(),{'template_a':1})
                for _ in range(3):service.capture(np.zeros((60,80,3),dtype=np.uint8))
                service.compose()
                client=Mock();client.reserve_transactions.return_value=[]
                client.bind_transaction.return_value={'folder_id':'bound','folder_url':'https://drive.google.com/drive/folders/bound',
                    'photo_number_layout':1,'link_verified':True}
                client.register_retention.side_effect=lambda _folder,tx,stamp:retention_metadata(tx,stamp)
                def uploaded(_folder,_tx,_relative,path,**_kwargs):
                    data=Path(path).read_bytes()
                    return {'id':str(path),'size':str(len(data)),'md5Checksum':hashlib.md5(data).hexdigest()}
                client.upload_file.side_effect=uploaded
                worker=BoothDriveWorker(workspace,client);worker.run_once()
                view=service.snapshot()
                self.assertEqual(view['upload_status'],'UPLOAD_COMPLETE')
                self.assertIsNotNone(view['download_qr'])
                self.assertEqual(client.upload_file.call_count,5)
                worker.run_once();self.assertEqual(client.upload_file.call_count,5)
                self.assertEqual(view['print_state'],'NOT_SENT')
            finally:service.close()

    def test_pre_fix_private_cached_url_is_withheld_from_a_new_visit(self):
        from photobooth.kiosk_v2.photos import PhotoTest
        with TemporaryDirectory() as folder:
            workspace=BoothWorkspace(folder,'PB001V2S2');workspace.prepare()
            slot=workspace.ready_slots()[0]
            workspace.remember_remote([{**slot,'folder_id':'private','folder_url':'https://drive.google.com/drive/folders/private'}])
            service=PhotoTest(folder,workspace=workspace,drive_requested=True)
            try:
                service.prepare();view=service.start(get_templates(),{'template_a':1})
                self.assertIsNone(view['folder_url'])
                self.assertEqual(view['upload_status'],'PENDING_DRIVE_BINDING')
            finally:service.close()
