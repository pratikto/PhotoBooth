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
            with patch('photobooth.booth_sync.time.monotonic',return_value=10**12):
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

    def test_binding_protocol_errors_have_specific_safe_codes(self):
        from photobooth.booth_sync import DriveBindingError
        session=Mock();existing=AppsScriptDriveClient('https://script.google.com/macros/s/fixture/exec','fixture',session=session)
        client=BoothDriveClient(existing,'PB001V2S2');session.post.return_value.status_code=200
        manifest={'transaction_id':'PB001V2S2_00000001','drive_claim_token':'a'*32,
                  'created_at':'2026-10-26T00:00:00Z','sessions':[{}]}
        valid={'ok':True,'storage_layout':2,'photo_number_layout':1,'link_verified':True,
               'transaction_id':manifest['transaction_id'],'folder_id':'fixture',
               'folder_url':'https://drive.google.com/drive/folders/fixture'}
        for override,code in (({'storage_layout':1},'BIND_LAYOUT_UNSUPPORTED'),
                              ({'transaction_id':'different'},'BIND_RESPONSE_ID_MISMATCH'),
                              ({'link_verified':False},'BIND_LINK_UNVERIFIED'),
                              ({'folder_url':'https://drive.google.com/drive/folders/different'},'BIND_RESPONSE_INVALID')):
            session.post.return_value.json.return_value={**valid,**override}
            with self.assertRaises(DriveBindingError) as error:client.bind_transaction(manifest)
            self.assertEqual(error.exception.code,code)
            self.assertEqual(error.exception.status_code,409)
            self.assertNotIn('fixture',str(error.exception))

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
                worker=BoothDriveWorker(workspace,client)
                for index in range(5):
                    worker.run_once()
                    if index < 4:
                        self.assertIsNotNone(service.snapshot()['download_qr'])
                        self.assertNotEqual(service.snapshot()['upload_status'],'UPLOAD_COMPLETE')
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

    def reserve_client(self):
        client=Mock()
        client.reserve_transactions.side_effect=lambda slots:[{
            **s,'folder_id':s['transaction_id'],'folder_url':'https://drive.google.com/drive/folders/'+s['transaction_id'],
            'status':'READY','photo_number_layout':1,'link_verified':True} for s in slots]
        return client

    def queued_transaction(self,w,client,files=2):
        slot=w.claim();store=TransactionStore(w.root,w.counter_path,w.booth_id,layout_version=2)
        plan=build_session_plans(get_templates(),{'template_a':1})[0]
        tx=store.start_transaction([plan],transaction_id=slot['transaction_id'],folder_path=slot['staging_path'])
        tx.manifest.update(drive_intent=True,drive_claim_token=slot['claim_token'])
        store._write_manifest(tx)
        for i in range(files):
            store.save_raw_photo(tx,plan,Image.new('RGB',(8,8),'red'),f'photo_{i}.jpg','capture')
        store.complete_transaction(tx)
        client.bind_transaction.side_effect=lambda m:{'folder_id':m['transaction_id'],
            'folder_url':'https://drive.google.com/drive/folders/'+m['transaction_id']}
        client.register_retention.side_effect=lambda folder,txid,started:retention_metadata(txid,started)
        client.upload_file.side_effect=lambda folder,txid,relative,path,**kw:{'id':relative,
            'size':path.stat().st_size,'md5Checksum':hashlib.md5(path.read_bytes()).hexdigest()}
        return tx

    def test_one_consumed_reserve_sends_one_slot_and_full_reconcile_runs_after_deadline_and_restart(self):
        with TemporaryDirectory() as folder,patch('photobooth.booth_sync.time.monotonic') as clock:
            clock.return_value=100
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client();worker=BoothDriveWorker(w,client)
            worker.run_once()
            self.assertEqual([len(c.args[0]) for c in client.reserve_transactions.call_args_list],[5]*5)
            client.reserve_transactions.reset_mock();w.claim();worker.run_once()
            self.assertEqual([len(c.args[0]) for c in client.reserve_transactions.call_args_list],[1])
            client.reserve_transactions.reset_mock();worker.run_once();client.reserve_transactions.assert_not_called()
            clock.return_value=100+worker.RECONCILE_SECONDS
            worker.run_once();self.assertEqual(sum(len(c.args[0]) for c in client.reserve_transactions.call_args_list),25)
            client.reserve_transactions.reset_mock();BoothDriveWorker(w,client).run_once()
            self.assertEqual(sum(len(c.args[0]) for c in client.reserve_transactions.call_args_list),25)

    def test_reserve_yields_at_batch_boundary_and_customer_sessions_are_fifo(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client();worker=BoothDriveWorker(w,client)
            reserve=client.reserve_transactions.side_effect
            txs=[]
            def arrival(slots):
                result=reserve(slots)
                if not txs:
                    txs.append(self.queued_transaction(w,client))
                    worker.notify_transaction(txs[0].transaction_id)
                return result
            client.reserve_transactions.side_effect=arrival
            worker.run_once();self.assertEqual(client.reserve_transactions.call_count,1)
            txs.append(self.queued_transaction(w,client))
            worker._wake.clear()
            self.assertTrue(worker.run_once())
            self.assertEqual([c.args[1] for c in client.upload_file.call_args_list],[txs[0].transaction_id])
            self.assertEqual(client.reserve_transactions.call_count,1) # Uploads still pending; no maintenance.
            for _ in range(3):worker.run_once()
            self.assertEqual([c.args[1] for c in client.upload_file.call_args_list],
                             [txs[0].transaction_id]*2+[txs[1].transaction_id]*2)
            for tx in txs:self.assertEqual(json.loads(tx.manifest_path.read_text())['upload_status'],'UPLOAD_COMPLETE')

    def test_customer_arrival_inside_content_chunk_uploads_before_remaining_content_and_resumes(self):
        from photobooth.content_cache import ContentCache
        from tests.test_content_cache import fixture
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client();content=ContentCache(w)
            content.load();worker=BoothDriveWorker(w,client,content)
            assets=fixture({'Global_Advertisement/large.mp4':b'x'*(512*1024+13)})
            client.asset_manifest=assets.asset_manifest
            order=[];transactions=[]
            def chunk(entry,offset,length):
                order.append('chunk')
                if not transactions:
                    transactions.append(self.queued_transaction(w,client,files=1))
                    upload=client.upload_file.side_effect
                    client.upload_file.side_effect=lambda *a,**kw:(order.append('upload'),upload(*a,**kw))[1]
                    worker.notify_transaction(transactions[0].transaction_id)
                return b'x'*length
            client.asset_chunk.side_effect=chunk
            worker.run_once()
            self.assertTrue(content.pending);self.assertFalse(content.pointer.exists())
            self.assertEqual(order,['chunk'])
            worker._wake.clear();worker.run_once()
            self.assertEqual(order,['chunk','upload','chunk'])
            self.assertFalse(content.pending);self.assertTrue(content.pointer.exists())

    def test_timeout_yields_retry_interval_restart_resumes_same_transaction_without_duplicate_success(self):
        with TemporaryDirectory() as folder,patch('photobooth.booth_sync.time.monotonic') as clock:
            clock.return_value=100
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client()
            tx=self.queued_transaction(w,client,files=1);upload=client.upload_file.side_effect
            client.upload_file.side_effect=DriveApiError('fixture timeout',503)
            worker=BoothDriveWorker(w,client);self.assertFalse(worker.run_once())
            worker.run_once();self.assertEqual(client.upload_file.call_count,1)
            data=json.loads(tx.manifest_path.read_text());self.assertEqual(data['upload_status'],'UPLOAD_RETRY')
            self.assertEqual(next(iter(data['upload_files'].values()))['attempts'],1)
            client.upload_file.side_effect=upload
            restarted=BoothDriveWorker(w,client);restarted.run_once()
            self.assertEqual(client.upload_file.call_count,1)  # Restart preserves the deadline.
            clock.return_value=131;restarted.run_once()
            data=json.loads(tx.manifest_path.read_text());self.assertEqual(data['upload_status'],'UPLOAD_COMPLETE')
            self.assertEqual(next(iter(data['upload_files'].values()))['attempts'],2)
            restarted.run_once();self.assertEqual(client.upload_file.call_count,2)

    def test_timing_separates_queue_and_request_and_omits_private_error_payload(self):
        from photobooth.delivery_timing import span
        with self.assertLogs('photobooth.delivery',level='INFO') as logs:
            with patch('photobooth.delivery_timing.time.monotonic',side_effect=[10,12,12]):
                with self.assertRaises(DriveApiError):
                    with span('upload_file','PB001V2S2_00000001',bytes=7,attempt=2):
                        raise DriveApiError('private-token-photo-payload',503)
        message='\n'.join(logs.output)
        self.assertIn('2000',message);self.assertIn('503',message)
        self.assertIn('PB001V2S2_00000001',message)
        self.assertNotIn('private-token-photo-payload',message)

    def test_old_retries_reserves_and_content_wait_for_all_customer_files(self):
        with TemporaryDirectory() as folder,patch('time.monotonic') as clock:
            now=[100.0];clock.side_effect=lambda:now[0]
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client()
            failed=[self.queued_transaction(w,client,files=1) for _ in range(3)]
            good=self.queued_transaction(w,client,files=5)
            for tx in failed:
                m=json.loads(tx.manifest_path.read_text());m['drive_binding_error']='DRIVE_RETRY'
                tx.manifest_path.write_text(json.dumps(m))
            order=[];bind=client.bind_transaction.side_effect;upload=client.upload_file.side_effect
            def binding(m):
                order.append(('bind',m['transaction_id']))
                if m['transaction_id']!=good.transaction_id:
                    now[0]+=5;raise DriveApiError('fixture secret',503)
                return bind(m)
            def uploading(*a,**kw):
                order.append(('upload',a[1]));now[0]+=8;return upload(*a,**kw)
            client.bind_transaction.side_effect=binding;client.upload_file.side_effect=uploading
            content=Mock();content.pending=True
            worker=BoothDriveWorker(w,client,content)
            for _ in range(5):
                worker.run_once()
                if len([a for a,t in order if a=='upload']) < 5:
                    self.assertTrue(all(t==good.transaction_id for _,t in order))
                    client.reserve_transactions.assert_not_called();content.sync.assert_not_called()
            self.assertEqual(order[:2],[('bind',good.transaction_id),('upload',good.transaction_id)])
            self.assertEqual(sum(action=='bind' and tx!=good.transaction_id for action,tx in order),1)
            self.assertEqual(json.loads(good.manifest_path.read_text())['upload_status'],'UPLOAD_COMPLETE')
            # Oldest due recovery is not starved by successful customer progress.
            now[0]=200;worker.run_once()
            self.assertEqual(order[-1],('bind',failed[1].transaction_id))

    def test_binding_conflict_keeps_folder_bytes_and_clock_and_survives_stale_controller_save(self):
        with TemporaryDirectory() as folder,patch('time.monotonic',return_value=100):
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client();tx=self.queued_transaction(w,client,1)
            m=json.loads(tx.manifest_path.read_text());m.update(drive_folder_id='known-original',
                drive_folder_url='https://drive.google.com/drive/folders/known-original')
            tx.manifest_path.write_text(json.dumps(m));started=m['created_at']
            raw={p:p.read_bytes() for p in tx.folder_path.glob('Photo/01/raw/*')}
            worker=BoothDriveWorker(w,client)
            with self.assertLogs('photobooth.delivery',level='INFO') as logs:worker.run_once()
            self.assertIn('BIND_FOLDER_CONFLICT','\n'.join(logs.output))
            self.assertNotIn('known-original','\n'.join(logs.output))
            client.upload_file.assert_not_called()
            tx.manifest['status']='COMPLETED';TransactionStore(w.root,w.counter_path,w.booth_id,layout_version=2)._write_manifest(tx)
            final=json.loads(tx.manifest_path.read_text())
            self.assertEqual(final['drive_folder_id'],'known-original');self.assertEqual(final['created_at'],started)
            self.assertEqual(final['drive_delivery_retry']['error_code'],'BIND_FOLDER_CONFLICT')
            self.assertEqual({p:p.read_bytes() for p in raw},raw)
            worker.notify_transaction(tx.transaction_id);worker.run_once()
            self.assertEqual(client.bind_transaction.call_count,1) # Capture kick never bypasses backoff.

    def test_binding_identity_changed_during_request_is_not_overwritten(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client();tx=self.queued_transaction(w,client,1)
            binding=client.bind_transaction.side_effect
            def changed(m):
                latest=json.loads(tx.manifest_path.read_text());latest['transaction_id']='other-identity'
                tx.manifest_path.write_text(json.dumps(latest));return binding(m)
            client.bind_transaction.side_effect=changed
            worker=BoothDriveWorker(w,client)
            with self.assertLogs('photobooth.delivery',level='INFO') as logs:worker.run_once()
            latest=json.loads(tx.manifest_path.read_text())
            self.assertEqual(latest['transaction_id'],'other-identity')
            self.assertNotIn('drive_delivery_retry',latest)
            self.assertIn('BIND_TRANSACTION_CHANGED','\n'.join(logs.output))
            client.upload_file.assert_not_called()

    def test_successful_recovery_clears_failure_and_future_failure_starts_at_base_delay(self):
        with TemporaryDirectory() as folder,patch('time.monotonic') as clock:
            clock.return_value=100
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client();tx=self.queued_transaction(w,client,2)
            upload=client.upload_file.side_effect;client.upload_file.side_effect=DriveApiError('offline',503)
            worker=BoothDriveWorker(w,client);worker.run_once()
            clock.return_value=130;client.upload_file.side_effect=upload;worker.run_once()
            self.assertIsNone(json.loads(tx.manifest_path.read_text())['drive_delivery_retry'])
            client.upload_file.side_effect=DriveApiError('offline',503);worker.run_once()
            state=json.loads(tx.manifest_path.read_text())['drive_delivery_retry']
            self.assertEqual((state['failures'],state['delay_seconds']),(1,5))

    def test_customer_short_retries_survive_restart_and_release_fifo_after_third_failure(self):
        with TemporaryDirectory() as folder,patch('time.monotonic') as clock,patch('time.time') as wall:
            now=[100.0];clock.side_effect=lambda:now[0];wall.side_effect=lambda:1000+now[0]
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client()
            old=self.queued_transaction(w,client,1)
            m=json.loads(old.manifest_path.read_text());m['drive_binding_error']='DRIVE_RETRY'
            old.manifest_path.write_text(json.dumps(m))
            head=self.queued_transaction(w,client,1);next_tx=self.queued_transaction(w,client,1)
            upload=client.upload_file.side_effect;order=[]
            def send(*a,**kw):
                order.append(a[1])
                if a[1]==head.transaction_id:raise DriveApiError('fixture offline',503)
                return upload(*a,**kw)
            client.upload_file.side_effect=send;worker=BoothDriveWorker(w,client)
            worker.run_once();worker.run_once()
            self.assertEqual(order,[head.transaction_id])
            self.assertEqual(json.loads(head.manifest_path.read_text())['drive_delivery_retry']['delay_seconds'],5)
            client.reserve_transactions.assert_not_called()
            worker=BoothDriveWorker(w,client)  # Durable priority and deadline survive a process restart.
            worker.notify_transaction(head.transaction_id);worker._wake.clear();worker.run_once()
            self.assertEqual(order,[head.transaction_id])
            now[0]=105;worker.run_once()
            self.assertEqual(json.loads(head.manifest_path.read_text())['drive_delivery_retry']['delay_seconds'],15)
            now[0]=120;self.assertTrue(worker.run_once())
            retry=json.loads(head.manifest_path.read_text())['drive_delivery_retry']
            self.assertFalse(retry['customer_priority']);self.assertEqual(retry['delay_seconds'],120)
            self.assertEqual(order,[head.transaction_id]*3)
            worker.run_once()
            self.assertEqual(order,[head.transaction_id]*3+[next_tx.transaction_id,old.transaction_id])
            self.assertEqual(json.loads(next_tx.manifest_path.read_text())['upload_status'],'UPLOAD_COMPLETE')
            self.assertEqual(json.loads(head.manifest_path.read_text())['upload_status'],'UPLOAD_RETRY')

    def test_customer_arriving_inside_old_bind_holds_next_old_network_request(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client()
            old=self.queued_transaction(w,client,1)
            m=json.loads(old.manifest_path.read_text());m['drive_binding_error']='DRIVE_RETRY'
            old.manifest_path.write_text(json.dumps(m))
            worker=BoothDriveWorker(w,client);arrivals=[];bind=client.bind_transaction.side_effect
            def binding(m):
                arrivals.append(self.queued_transaction(w,client,1))
                worker.notify_transaction(arrivals[0].transaction_id)
                return bind(m)
            client.bind_transaction.side_effect=binding
            worker.run_once()
            client.register_retention.assert_not_called();client.upload_file.assert_not_called()
            self.assertTrue(json.loads(old.manifest_path.read_text())['drive_binding_verified'])
            worker._wake.clear();worker.run_once()
            self.assertEqual(client.upload_file.call_args.args[1],arrivals[0].transaction_id)

    def test_two_transactions_keep_exact_local_folder_mapping_across_restart(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client()
            transactions=[self.queued_transaction(w,client,2) for _ in range(2)]
            original={tx.transaction_id:json.loads(tx.manifest_path.read_text()) for tx in transactions}
            worker=BoothDriveWorker(w,client);worker.run_once()
            w=BoothWorkspace(folder);w.prepare();worker=BoothDriveWorker(w,client)
            for _ in range(3):worker.run_once()
            expected={tx.transaction_id:tx for tx in transactions}
            for call in client.upload_file.call_args_list:
                folder_id,txid,relative,local_path=call.args
                self.assertEqual(folder_id,txid)
                self.assertEqual(local_path,expected[txid].folder_path/relative)
                record=json.loads(expected[txid].manifest_path.read_text())['upload_files'][relative]
                self.assertEqual(record['md5_checksum'],hashlib.md5(local_path.read_bytes()).hexdigest())
            state=json.loads(w.state_path.read_text())
            for tx in transactions:
                m=json.loads(tx.manifest_path.read_text())
                self.assertEqual(m['drive_folder_id'],tx.transaction_id)
                self.assertEqual(m['upload_status'],'UPLOAD_COMPLETE')
                self.assertEqual(m['drive_claim_token'],original[tx.transaction_id]['drive_claim_token'])
                self.assertEqual(m['created_at'],original[tx.transaction_id]['created_at'])
                self.assertEqual(state['claimed'][tx.transaction_id]['folder_id'],m['drive_folder_id'])
                self.assertNotIn(tx.transaction_id,{s['transaction_id'] for s in w.ready_slots()})

    def test_binding_cannot_reuse_another_transactions_customer_folder(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client()
            a=self.queued_transaction(w,client,1);b=self.queued_transaction(w,client,1)
            client.bind_transaction.side_effect=lambda m:{'folder_id':'same-folder',
                'folder_url':'https://drive.google.com/drive/folders/same-folder'}
            worker=BoothDriveWorker(w,client);worker.run_once()
            before=a.manifest_path.read_bytes();worker.run_once()
            self.assertEqual(a.manifest_path.read_bytes(),before)
            self.assertIsNone(json.loads(b.manifest_path.read_text())['drive_folder_id'])
            self.assertEqual(json.loads(b.manifest_path.read_text())['drive_delivery_retry']['error_code'],'BIND_FOLDER_CONFLICT')
            self.assertEqual(client.upload_file.call_count,1)

    def test_successful_old_retry_stays_background_after_restart_and_new_customer_arrival(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client()
            old=self.queued_transaction(w,client,3)
            m=json.loads(old.manifest_path.read_text());m['drive_binding_error']='DRIVE_RETRY'
            old.manifest_path.write_text(json.dumps(m))
            worker=BoothDriveWorker(w,client);worker.run_once()
            self.assertTrue(json.loads(old.manifest_path.read_text())['drive_delivery_retry']['background_only'])
            customer=self.queued_transaction(w,client,2)
            worker=BoothDriveWorker(BoothWorkspace(folder),client)
            for _ in range(3):worker.run_once()
            self.assertEqual([c.args[1] for c in client.upload_file.call_args_list],
                [old.transaction_id]+[customer.transaction_id]*2+[old.transaction_id]*2)
            self.assertEqual(json.loads(old.manifest_path.read_text())['upload_status'],'UPLOAD_COMPLETE')
            self.assertEqual(json.loads(customer.manifest_path.read_text())['upload_status'],'UPLOAD_COMPLETE')

    def test_invalid_old_metadata_cannot_interrupt_a_new_customer_or_get_overwritten(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client()
            old=self.queued_transaction(w,client,1);old.manifest_path.write_text('[]')
            customer=self.queued_transaction(w,client,1)
            worker=BoothDriveWorker(w,client);worker.run_once()
            self.assertEqual(old.manifest_path.read_text(),'[]')
            self.assertEqual(json.loads(customer.manifest_path.read_text())['upload_status'],'UPLOAD_COMPLETE')
            self.assertEqual(client.upload_file.call_count,1)


class DeliveryRetryPolicyTests(unittest.TestCase):
    def test_backoff_caps_and_oldest_due_recovery_retains_a_turn(self):
        from photobooth.delivery_retry import DeliveryRetries
        with patch('time.monotonic',return_value=100),patch('time.time',return_value=1000):
            policy=DeliveryRetries()
            delays=[policy.failed('tx','DRIVE_NETWORK_RETRY','bind')['delay_seconds'] for _ in range(8)]
            self.assertEqual(delays,[30,60,120,240,300,300,300,300])
            policy.state('older',{'drive_binding_error':'DRIVE_RETRY'})
            self.assertEqual(policy.choose([('older','path'),('tx','path2')]),('older','path'))
            policy.finish_turn();self.assertIsNone(policy.choose([('older','path')]))

    def test_restart_uses_wall_deadline_once_then_monotonic_and_bounds_corrupt_future_clock(self):
        from photobooth.delivery_retry import DeliveryRetries
        with patch('time.monotonic',return_value=500),patch('time.time',return_value=1000):
            policy=DeliveryRetries()
            saved={'drive_delivery_retry':{'failures':3,'not_before_unix':1090}}
            self.assertEqual(policy.state('tx',saved),{'failures':3,'due':590})
            self.assertEqual(policy.state('future',{'drive_delivery_retry':{'not_before_unix':1e15}})['due'],800)
            self.assertEqual(policy.state('bad',{'drive_delivery_retry':{'not_before_unix':float('nan')}})['due'],500)
        with patch('time.monotonic',return_value=589),patch('time.time',return_value=1e15):
            self.assertIsNone(policy.choose([('tx','path')]))
        with patch('time.monotonic',return_value=590):
            self.assertEqual(policy.choose([('tx','path')]),('tx','path'))


class DeliveryLoggingWorkerTests(unittest.TestCase):
    # Reuse the transaction/client fixture, without rediscovering the parent suite.
    reserve_client = BoothSyncTests.reserve_client
    queued_transaction = BoothSyncTests.queued_transaction
    def test_broken_timing_sink_does_not_kill_worker_or_requeue_verified_files(self):
        import logging
        import threading
        from photobooth.delivery_timing import LOG
        class Broken(logging.Handler):
            def emit(self,record):raise RecursionError('synthetic recursive sink')
        class ObservedWorker(BoothDriveWorker):
            def run_once(self):
                result=super().run_once();finished.set();return result
        finished=threading.Event();handler=Broken()
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();client=self.reserve_client();tx=self.queued_transaction(w,client,1)
            worker=ObservedWorker(w,client);LOG.addHandler(handler)
            try:
                worker.start();self.assertTrue(finished.wait(3),'worker died before completing its pass')
                self.assertTrue(worker._thread.is_alive())
                manifest=json.loads(tx.manifest_path.read_text())
                self.assertEqual(manifest['upload_status'],'UPLOAD_COMPLETE')
                self.assertIsNone(manifest.get('drive_delivery_retry'))
                self.assertEqual(client.upload_file.call_count,1)
            finally:
                worker.stop();worker._thread.join(timeout=3);LOG.removeHandler(handler)
