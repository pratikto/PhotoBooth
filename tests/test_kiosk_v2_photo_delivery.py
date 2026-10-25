"""Worker-only setup/QR contracts over existing v1 photo/delivery services."""
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
from unittest.mock import Mock,patch

import numpy as np
from PIL import Image

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoJobs,PhotoSetupError,PhotoTest,configured_test


class PhotoDeliveryTests(unittest.TestCase):
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
    def test_download_qr_only_after_verified_upload_is_encoded_off_ui_and_cached(self):
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
                self.assertIsNone(service.snapshot()['download_qr'])
                manifest['upload_status']='UPLOAD_COMPLETE';path.write_text(json.dumps(manifest))
                jobs.submit('snapshot');jobs.wait_closed();view=jobs.poll().value
                self.assertEqual(view['download_qr'].size,(180,180))
                service.snapshot();self.assertEqual(len(calls),1)
                self.assertEqual(calls[0][0],url);self.assertNotEqual(calls[0][1],ui)
            jobs.close()
