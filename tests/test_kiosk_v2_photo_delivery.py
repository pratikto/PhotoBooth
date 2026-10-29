"""Worker-only setup/QR contracts over existing v1 photo/delivery services."""
from pathlib import Path
import hashlib
import json
from tempfile import TemporaryDirectory
import threading
import time
import unittest
from unittest.mock import Mock,patch

import numpy as np
from PIL import Image

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoJobs,PhotoSetupError,PhotoTest,configured_test


class PhotoDeliveryTests(unittest.TestCase):
    def test_ux11_stalled_real_upload_queue_keeps_clock_live_and_original_files_once(self):
        from kivy.base import EventLoop
        from kivy.clock import Clock
        from kivy.core.window import Window  # Ensure actual SDL event loop exists.
        from photobooth.drive_pool import DriveSlotPool
        from photobooth.drive_storage import RemoteDriveSlot
        from photobooth.retention import retention_metadata
        entered,release=threading.Event(),threading.Event()
        with TemporaryDirectory() as folder:
            root=Path(folder);client=Mock()
            client.ensure_folder_pool.return_value=[RemoteDriveSlot(
                'fixture-folder','https://example.test/photos/frozen','fixture-slot','READY',
                'PB001V2_00000001',transaction_id='PB001V2_00000001',verified=True)]
            client.register_retention.side_effect=lambda _folder,tx,started:retention_metadata(tx,started)
            ui=threading.get_ident();threads=[]
            def upload(_folder,_tx,relative,path,**_kwargs):
                threads.append(threading.get_ident());entered.set()
                if not release.wait(8):raise AssertionError('Synthetic upload barrier timeout')
                data=path.read_bytes()
                return {'id':relative,'size':len(data),'md5Checksum':hashlib.md5(data).hexdigest()}
            client.upload_file.side_effect=upload
            old=PhotoTest(root,drive_client=client)
            old.pool=DriveSlotPool(old.store.photos_root,root/'drive-pool.json','PB001V2',1)
            old.pool.refresh(client);templates=get_templates()
            old.start(templates,{templates[0].template_id:1})
            for _ in range(3):old.capture(np.zeros((24,32,3),dtype=np.uint8))
            old.compose();manifest=old.transaction.manifest_path
            files={p:p.read_bytes() for p in (*old.session.initial_photo_paths,old.session.output_path)}
            counter=(root/'counter.json').read_bytes();old.close()
            fresh=PhotoTest(root,drive_client=client);jobs=PhotoJobs(fresh)
            ticks=[];timer=Clock.schedule_interval(lambda dt:ticks.append(dt),0)
            try:
                fresh.prepare();self.assertTrue(entered.wait(2))
                self.assertTrue(jobs.submit('snapshot'))
                outcome=None;deadline=time.monotonic()+2
                while outcome is None and time.monotonic()<deadline:
                    EventLoop.idle();outcome=jobs.poll()
                self.assertIsNotNone(outcome)
                self.assertIsNone(outcome.error)
                self.assertEqual(outcome.value['phase'],'confirm')
                for _ in range(5):EventLoop.idle()
                self.assertGreaterEqual(len(ticks),3)
                self.assertIsNone(fresh.transaction)
                self.assertEqual(client.upload_file.call_count,1)
                self.assertTrue(all(t!=ui for t in threads))
                self.assertEqual(json.loads(manifest.read_text())['upload_status'],'UPLOADING')
                release.set();deadline=time.monotonic()+5
                while json.loads(manifest.read_text())['upload_status']!='UPLOAD_COMPLETE' and time.monotonic()<deadline:
                    EventLoop.idle()
                self.assertEqual(json.loads(manifest.read_text())['upload_status'],'UPLOAD_COMPLETE')
                self.assertEqual(client.upload_file.call_count,4)
                self.assertEqual((root/'counter.json').read_bytes(),counter)
                self.assertEqual({p:p.read_bytes() for p in files},files)
                self.assertEqual(len(list(fresh.store.photos_root.glob('*/manifest.json'))),1)
                client.cleanup_expired.assert_not_called()
            finally:
                release.set();timer.cancel();jobs.close();jobs.wait_closed()
                if fresh.drive_worker:fresh.drive_worker._thread.join(timeout=5)

    def test_new_service_resumes_real_existing_upload_queue_without_new_visit_or_print(self):
        from photobooth.drive_pool import DriveSlotPool
        from photobooth.drive_storage import RemoteDriveSlot
        from photobooth.retention import retention_metadata
        with TemporaryDirectory() as folder:
            root=Path(folder);client=Mock()
            client.ensure_folder_pool.return_value=[RemoteDriveSlot(
                'fixture-folder','https://example.test/photos/resume','fixture-slot','READY',
                'PB001V2_00000001',transaction_id='PB001V2_00000001',verified=True)]
            client.register_retention.side_effect=lambda _folder,tx,started:retention_metadata(tx,started)
            def upload(_folder,_tx,relative,path,**_kwargs):
                data=path.read_bytes()
                return {'id':relative,'size':len(data),'md5Checksum':hashlib.md5(data).hexdigest()}
            client.upload_file.side_effect=upload
            old=PhotoTest(root,drive_client=client)
            old.pool=DriveSlotPool(old.store.photos_root,root/'drive-pool.json','PB001V2',1)
            old.pool.refresh(client);templates=get_templates()
            old.start(templates,{templates[0].template_id:1})
            for _ in range(3):old.capture(np.zeros((80,120,3),dtype=np.uint8))
            old.compose();manifest=old.transaction.manifest_path
            counter=(root/'counter.json').read_bytes();old.close()
            # Start the actual inherited v1 sync loop with fixture transports.
            # It must deliver the old queue even though no new visit is started.
            fresh=PhotoTest(root,drive_client=client)
            try:
                fresh.prepare();deadline=time.monotonic()+5
                while json.loads(manifest.read_text())['upload_status']!='UPLOAD_COMPLETE' and time.monotonic()<deadline:
                    time.sleep(.01)
                self.assertEqual(json.loads(manifest.read_text())['upload_status'],'UPLOAD_COMPLETE')
                self.assertIsNone(fresh.transaction);self.assertEqual((root/'counter.json').read_bytes(),counter)
                self.assertEqual(client.upload_file.call_count,4)
                self.assertEqual(len(list(fresh.store.photos_root.glob('*/manifest.json'))),1)
                client.cleanup_expired.assert_not_called()
            finally:
                fresh.close()
                if fresh.drive_worker:fresh.drive_worker._thread.join(timeout=1)
    def test_setup_snapshot_reports_real_pool_readiness_and_reuses_one_worker(self):
        with TemporaryDirectory() as folder:
            service=PhotoTest(folder,printer=Mock(),drive_client=Mock(),auto_print=True)
            pool=Mock();pool.has_ready_slot.return_value=False;pool.last_error=None
            worker=Mock()
            with patch('photobooth.drive_pool.DriveSlotPool',return_value=pool),patch(
                    'photobooth.kiosk_v2.photo_drive.RetentionGuardedSync',return_value=worker),patch(
                    'photobooth.retention.PhotoRetentionWorker'):
                first=service.prepare();self.assertFalse(first['drive_ready'])
                self.assertTrue(first['drive_enabled']);self.assertTrue(first['auto_print'])
                pool.has_ready_slot.return_value=True
                self.assertTrue(service.snapshot()['drive_ready'])
                service.prepare();worker.start.assert_called_once();service.close()
    def test_configured_service_reuses_saved_printer_and_original_drive_factories(self):
        with TemporaryDirectory() as folder,patch.dict('os.environ',{
                'PHOTOBOOTH_V2_PRINT':'1','PHOTOBOOTH_V2_DRIVE':'1','PHOTOBOOTH_V2_AUTO_PRINT':'1',
                'PHOTOBOOTH_V2_BOOTH_ID':'PB001V2'}),patch(
                'photobooth.printer_settings.load_printer_config',return_value=Mock()) as read,patch(
                'photobooth.printer.ThermalPrinter') as printer,patch(
                'photobooth.drive_storage.AppsScriptDriveClient.from_configuration',return_value=Mock()) as original,patch(
                'photobooth.drive_storage.GoogleDriveClient.from_environment') as oauth:
            config=Path(folder)/'v1-config';service=configured_test(Path(folder)/'isolated-v2',configuration_root=config)
            read.assert_called_once_with(config/'data'/'printer_settings.json')
            self.assertIs(service.printer,printer.return_value)
            self.assertIs(service.drive_client,original.return_value)
            self.assertTrue(service.auto_print);oauth.assert_not_called();service.close()
    def test_missing_credentials_is_a_safe_setup_error_not_a_fake_folder(self):
        with TemporaryDirectory() as folder,patch.dict('os.environ',{
                'PHOTOBOOTH_V2_PRINT':'0','PHOTOBOOTH_V2_DRIVE':'1'}),patch(
                'photobooth.drive_storage.AppsScriptDriveClient.from_configuration',return_value=None),patch(
                'photobooth.drive_storage.GoogleDriveClient.from_environment',return_value=None):
            with self.assertRaises(PhotoSetupError) as result:configured_test(folder)
            self.assertEqual(result.exception.code,'drive_configuration')
    def test_download_qr_before_upload_is_encoded_off_ui_cached_and_preserves_progress(self):
        import json
        with TemporaryDirectory() as folder:
            service=PhotoTest(folder);templates=get_templates()
            service.start(templates,{templates[0].template_id:1})
            for _ in range(3):service.capture(np.zeros((80,120,3),dtype=np.uint8))
            service.compose();path=service.transaction.manifest_path
            manifest=json.loads(path.read_text());url='https://example.test/photos/verified'
            manifest.update(drive_folder_url=url,upload_status='PENDING_UPLOAD')
            path.write_text(json.dumps(manifest));ui=threading.get_ident();calls=[]
            def encode(value):
                calls.append((value,threading.get_ident()));return Image.new('RGB',(180,180),'white')
            jobs=PhotoJobs(service)
            with patch('photobooth.qr_code.create_qr_image',side_effect=encode):
                before=path.read_bytes()
                jobs.submit('snapshot');jobs.wait_closed();view=jobs.poll().value
                self.assertEqual(view['download_qr'].size,(180,180))
                self.assertEqual(view['upload_status'],'PENDING_UPLOAD')
                self.assertEqual(path.read_bytes(),before)
                manifest['upload_status']='UPLOAD_COMPLETE';path.write_text(json.dumps(manifest))
                service.snapshot();self.assertEqual(len(calls),1)
                self.assertEqual(calls[0][0],url);self.assertNotEqual(calls[0][1],ui)
            jobs.close()

    def test_layout2_early_qr_requires_verified_destination_and_withholds_unsafe_states(self):
        from photobooth.booth_storage import BoothWorkspace
        with TemporaryDirectory() as folder:
            workspace=BoothWorkspace(Path(folder)/'Photobooth','PB001V2S2')
            service=PhotoTest(folder,workspace=workspace,drive_requested=True)
            templates=get_templates();service.start(templates,{templates[0].template_id:1})
            path=service.transaction.manifest_path;manifest=json.loads(path.read_text())
            manifest.update(drive_folder_id='fixture-folder',
                drive_folder_url='https://drive.google.com/drive/folders/fixture-folder',
                photo_number_layout=1)
            path.write_text(json.dumps(manifest))
            # A cached reserve already verified by the transport can precede bind/upload.
            self.assertIsNotNone(service.snapshot()['download_qr'])
            for fields in ({'drive_folder_url':None},{'photo_number_layout':None},
                           {'drive_folder_id':'different-folder'},
                           {'drive_binding_error':'DRIVE_RETRY'},
                           {'upload_status':'LOCAL_ONLY'},{'upload_status':'LOCAL_EXPIRED'},
                           {'upload_status':'ACTION_REQUIRED'}):
                with self.subTest(fields=fields):
                    path.write_text(json.dumps({**manifest,**fields}))
                    self.assertIsNone(service.snapshot()['download_qr'])
            service.close()
