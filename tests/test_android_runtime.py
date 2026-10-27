"""Native adapters with synthetic devices; never certify Android hardware/paper."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

from photobooth.kiosk_v2.android_settings import DEFAULTS, validated, save_settings, load_settings, configure_mobile
from photobooth.kiosk_v2.android_usb import UsbOtgSender


class MobileConfigurationTests(unittest.TestCase):
    def test_private_settings_never_accept_merchant_keys_and_reject_insecure_backends(self):
        for values in ({'MIDTRANS_SERVER_KEY':'do-not-store'}, {'sandbox_enabled':True},
                       {'api_url':'http://192.168.1.20:8000'}, {'usb_vendor':True},
                       {'api_url':'https://name:password@example.test'},
                       {'api_url':'https://example.test/?token=secret'}):
            with self.subTest(keys=list(values)), self.assertRaises(ValueError):
                validated(values)
        self.assertEqual(validated({})['camera_facing'],0)

    def test_persist_settings_and_preserve_pending_identity(self):
        with tempfile.TemporaryDirectory() as root:
            cfg={**DEFAULTS,'sandbox_enabled':True,'api_url':'https://fixture.invalid','booth_token':'a'*48}
            save_settings(root,cfg)
            self.assertEqual(load_settings(root),cfg)
            self.assertEqual((Path(root)/'mobile-settings.json').stat().st_mode&0o777,0o600)
            journal=Path(root)/'data/kiosk-v2-sandbox/android/visit.json'
            journal.parent.mkdir(parents=True);journal.write_text('{"phase":"WAITING"}')
            with self.assertRaises(ValueError):save_settings(root,{**cfg,'sandbox_enabled':False})
            self.assertEqual(journal.read_text(),'{"phase":"WAITING"}')
            save_settings(root,{**cfg,'booth_token':'b'*48}) # credential rotation keeps journal identity
            with self.assertRaises(ValueError):configure_mobile(root,DEFAULTS,environ={})

    def test_environment_uses_private_root_and_only_booth_credentials(self):
        with tempfile.TemporaryDirectory() as root:
            env={'MIDTRANS_SERVER_KEY':'inherited','PHOTOBOOTH_V2_STORAGE_ROOT':'/elsewhere',
                 'PHOTOBOOTH_WEB_APP_URL':'inherited','MEONG_QRIS_LOCAL_PREVIEW':'1'}
            cfg={**DEFAULTS,'sandbox_enabled':True,'api_url':'https://fixture.invalid','booth_token':'a'*48}
            configure_mobile(root,cfg,environ=env)
            self.assertEqual(env['PHOTOBOOTH_CAMERA'],'1')
            self.assertEqual(env['PHOTOBOOTH_V2_CHECKOUT_SANDBOX'],'1')
            self.assertEqual(env['MEONG_QRIS_JOURNAL'],str(Path(root)/'data/kiosk-v2-sandbox/android/visit.json'))
            for key in ('MIDTRANS_SERVER_KEY','MEONG_QRIS_LOCAL_PREVIEW','PHOTOBOOTH_V2_STORAGE_ROOT','PHOTOBOOTH_WEB_APP_URL'):
                self.assertNotIn(key,env)

    def test_backend_restart_reuses_booth_token_and_keeps_merchant_key_out_of_export(self):
        from tools.run_android_sandbox_backend import backend_profile
        with tempfile.TemporaryDirectory() as root:
            args=({},'MTEST','Mid-server-TEST-ONLY-NOT-A-CREDENTIAL','PB001',8765,'https://fixture.invalid')
            backend,path=backend_profile(*args,root=Path(root))
            first=json.loads(path.read_text())
            again,_=backend_profile(*args,root=Path(root))
            self.assertEqual(backend['MEONG_QRIS_BOOTH_TOKEN'],again['MEONG_QRIS_BOOTH_TOKEN'])
            self.assertEqual(first['booth_token'],again['MEONG_QRIS_BOOTH_TOKEN'])
            self.assertNotIn(args[2],path.read_text())
            self.assertEqual(backend['PHOTOBOOTH_V2_PRINT'],'0')
            with self.assertRaises(ValueError):backend_profile(*args[:-1],'https://other.invalid',root=Path(root))


class UsbAdapterTests(unittest.TestCase):
    def make_sender(self, counts=None, allowed=True):
        endpoint=Mock();endpoint.getType.return_value=2;endpoint.getDirection.return_value=0
        interface=Mock();interface.getEndpointCount.return_value=1;interface.getEndpoint.return_value=endpoint
        device=Mock();device.getVendorId.return_value=0x4838;device.getProductId.return_value=0x3830
        device.getInterfaceCount.return_value=1;device.getInterface.return_value=interface
        manager=Mock();manager.hasPermission.return_value=allowed
        iterator=manager.getDeviceList.return_value.values.return_value.iterator.return_value
        iterator.hasNext.side_effect=[True,False];iterator.next.return_value=device
        connection=manager.openDevice.return_value;connection.claimInterface.return_value=True
        connection.bulkTransfer.side_effect=counts or (lambda endpoint,block,size,timeout:size)
        return UsbOtgSender(0x4838,0x3830,context_factory=lambda:(None,manager)),manager,connection

    def test_chunks_once_and_releases_after_short_writes(self):
        sender,manager,connection=self.make_sender([3,2])
        sender(b'abcde')
        self.assertEqual([c.args[1] for c in connection.bulkTransfer.call_args_list],[b'abcde',b'de'])
        connection.releaseInterface.assert_called_once();connection.close.assert_called_once()
        manager.openDevice.assert_called_once()

    def test_partial_failure_never_reopens_or_retries_payload(self):
        sender,manager,connection=self.make_sender([3,-1])
        with self.assertRaises(RuntimeError):sender(b'abcde')
        self.assertEqual(connection.bulkTransfer.call_count,2)
        manager.openDevice.assert_called_once();connection.close.assert_called_once()

    def test_denied_permission_sends_zero_bytes(self):
        sender,manager,connection=self.make_sender(allowed=False)
        with self.assertRaises(RuntimeError):sender(b'do-not-send')
        manager.openDevice.assert_not_called();connection.bulkTransfer.assert_not_called()


class MobileCameraTests(unittest.TestCase):
    def test_nv21_channels_rotation_and_bounded_preview(self):
        import numpy as np
        from photobooth.kiosk_v2.android_camera import nv21_bgr, preview_pixels, java_bytes
        self.assertEqual(java_bytes([-128,-1,0,127]),bytes([128,255,0,127]))
        raw=bytes([16,235,81,145,128,128])
        normal=nv21_bgr(raw,2,2)
        self.assertEqual(tuple(normal[0,0]),(0,0,0))
        self.assertEqual(tuple(normal[0,1]),(255,255,255))
        self.assertTrue(np.array_equal(nv21_bgr(raw,2,2,90),np.rot90(normal,-1)))
        with self.assertRaises(ValueError):nv21_bgr(b'bad',2,2)
        size,pixels=preview_pixels(np.zeros((1600,1200,3),dtype=np.uint8))
        self.assertLessEqual(size[0],640);self.assertLessEqual(size[1],480)
        self.assertEqual(len(pixels),size[0]*size[1]*3)

    def test_pause_during_native_still_cannot_publish_old_capture(self):
        import numpy as np
        from photobooth.kiosk_v2.android_camera import MobileCamera
        entered,release=threading.Event(),threading.Event()
        class Service:
            def __init__(self,index):pass
            def open(self):return True
            def read(self):return np.zeros((8,8,3),dtype=np.uint8)
            def capture(self):entered.set();release.wait(3);return self.read()
            def close(self):pass
        camera=MobileCamera(service_factory=Service);camera.start()
        deadline=time.monotonic()+3
        while camera.read() is None and time.monotonic()<deadline:time.sleep(.01)
        errors=[]
        def capture():
            try:camera.capture()
            except RuntimeError as error:errors.append(error)
        thread=threading.Thread(target=capture);thread.start()
        self.assertTrue(entered.wait(3));camera.set_active(False);release.set();thread.join(3)
        self.assertEqual(len(errors),1);self.assertIsNone(camera.read())
        camera.close();camera.wait_closed()


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_ANDROID')=='1','Android native GUI opt-in')
class MobileRuntimeWidgetTests(unittest.TestCase):
    def settle(self,app):
        from kivy.base import EventLoop
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            app._poll_photos();app._poll_sandbox();EventLoop.idle()
            if not (app._photo_jobs and app._photo_jobs.busy) and not (app._sandbox_jobs and app._sandbox_jobs.busy):return
            time.sleep(.005)
        self.fail('Mobile worker did not settle')

    @contextmanager
    def booth(self,sandbox=False,send_error=False):
        import numpy as np
        from kivy.core.window import Window
        from photobooth.kiosk_v2.android_runtime import create_mobile
        from tests.qris_v2_fixture import Fixture
        from photobooth.kiosk_v2.android_preview import DATA_MODULES
        from contextlib import ExitStack
        import importlib
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ,{}), ExitStack() as stack:
            import photobooth.advertising as advertising
            stack.enter_context(patch.object(advertising,'DEFAULT_VIDEO_DIR',advertising.DEFAULT_VIDEO_DIR))
            for name in DATA_MODULES:
                module=importlib.import_module('photobooth.kiosk_v2.'+name)
                stack.enter_context(patch.object(module,'PROJECT_ROOT',module.PROJECT_ROOT))
            fixture=Fixture(Path(root)) if sandbox else None
            camera=Mock();camera.read.return_value=np.zeros((24,32,3),dtype=np.uint8)
            camera.capture.return_value=np.zeros((1200,1600,3),dtype=np.uint8)
            camera.state='ready'
            sends=[]
            def send(payload):
                sends.append(payload)
                if send_error:raise OSError('synthetic partial send')
            settings={**DEFAULTS,'audio_enabled':False,'video_enabled':False,'face_enabled':False,
                      'palm_enabled':False,'print_enabled':True,'sandbox_enabled':sandbox,
                      'api_url':'https://fixture.invalid','booth_token':'a'*48}
            app=create_mobile(root,settings=settings,camera=camera,usb_sender=send,
                              sandbox_jobs=fixture.jobs if fixture else None)
            width=int(os.environ.get('ANDROID_PREVIEW_WIDTH','452'));size=Window.size
            Window.size=(width,1280 if width==800 else 900)
            Window.add_widget(app.build())
            try:
                self.settle(app)
                yield app,fixture,camera,sends,Path(root)
            finally:
                app.on_stop()
                for name in ('_game_jobs','_mock_jobs','_sandbox_jobs','_photo_jobs','_health_reports'):
                    worker=getattr(app,name,None)
                    if worker:worker.wait_closed()
                if fixture:fixture.close()
                Window.remove_widget(app.stage);Window.size=size

    def capture_three(self,app):
        for _ in range(3):
            app._start_countdown();app._countdown_deadline=time.monotonic()-.1;app._countdown_tick(0);self.settle(app)

    def screenshot(self,app,name):
        output=os.environ.get('MEONG_ANDROID_RENDER_DIR')
        if output:
            path=Path(output);path.mkdir(parents=True,exist_ok=True)
            width,height=map(int,app.stage.size)
            app.stage.export_to_png(str(path/f'mobile-{name}-{width}x{height}.png'))

    def test_local_native_capture_full_resolution_retake_auto_usb_print_and_pause(self):
        from PIL import Image
        with self.booth() as (app,f,camera,sends,root):
            app._choose_photo();app._complete_tutorial();app._change_copies(2)
            self.assertFalse(app._test_photo_button.disabled)
            app._enter_photo_test();self.settle(app);app._admit_photo_test();self.settle(app)
            self.assertEqual(app.navigation.page,'capture');self.screenshot(app,'camera')
            app._start_countdown();app._operator_key(None,27)
            self.assertIsNone(app._countdown_event);camera.capture.assert_not_called()
            self.capture_three(app);self.screenshot(app,'review')
            app._photo_submit('retake',0);self.settle(app)
            app._start_countdown();app._countdown_deadline=0;app._countdown_tick(0);self.settle(app)
            self.assertTrue(app._photo_view['retake_used'])
            app._photo_submit('compose');self.settle(app);self.screenshot(app,'result')
            self.assertEqual(len(sends),1);self.assertEqual(sends[0][:len(sends[0])//2],sends[0][len(sends[0])//2:])
            self.assertEqual(app._photo_view['print_state'],'SUBMITTED')
            self.assertEqual(camera.capture.call_count,4)
            raw=next(root.glob('data/Photobooth/**/raw/photo_01.jpg'))
            with Image.open(raw) as image:self.assertEqual(image.size,(1600,1200))
            app._show();app.on_pause();app.on_resume();self.assertEqual(len(sends),1)

    def test_sandbox_ack_guard_then_same_photo_print_path_uncertain_not_replayed(self):
        with self.booth(sandbox=True,send_error=True) as (app,f,camera,sends,root):
            app._choose_photo();app._complete_tutorial();app._change_copies(1);app._open_sandbox()
            self.assertEqual(f.provider.charges,0)
            app._sandbox_begin();self.settle(app);self.screenshot(app,'sandbox-waiting')
            with patch('kivy.core.clipboard.Clipboard.copy') as copy:
                app._copy_simulator_url();copy.assert_called_once_with(f.flow.snapshot()['order']['qr_url'])
            self.assertEqual(f.provider.charges,1)
            app._sandbox_photo_consent();self.assertIsNone(app._photo_jobs)
            f.paid();app._sandbox_retry();self.settle(app)
            app._sandbox_photo_consent();self.settle(app)
            with patch.object(f.backend,'service_transition',side_effect=TimeoutError('fixture lost ACK')):
                app._admit_photo_test();self.settle(app)
            app._start_countdown();self.assertIsNone(app._countdown_event);camera.capture.assert_not_called()
            tx=app._photo_view['transaction_id'];app._sandbox_retry();self.settle(app)
            self.assertEqual(app._photo_view['transaction_id'],tx)
            self.capture_three(app);app._photo_submit('compose');self.settle(app)
            self.assertEqual(len(sends),1);self.assertEqual(app._photo_view['print_state'],'UNCERTAIN')
            app._photo_submit('print_result');self.settle(app);self.assertEqual(len(sends),1)
            app._photo_submit('next');self.settle(app);self.assertEqual(f.flow.snapshot()['phase'],'STARTED')
            app._photo_submit('acknowledge_print');self.settle(app)
            app._photo_submit('next');self.settle(app)
            self.assertEqual(f.flow.snapshot()['phase'],'COMPLETED');self.assertEqual(f.provider.charges,1)

    def test_mobile_settings_same_safe_entry_with_masked_tokens(self):
        with self.booth() as (app,f,camera,sends,root):
            app._open_operator();self.assertIsNotNone(app._operator_panel)
            self.screenshot(app,'settings')
            from kivy.uix.textinput import TextInput
            secrets=[w for w in app._operator_panel.popup.walk() if isinstance(w,TextInput) and w.password]
            self.assertEqual(len(secrets),2)
            app._operator_key(None,27);self.assertIsNone(app._operator_panel)
            app._open_mobile_health()
            from kivy.base import EventLoop
            deadline=time.monotonic()+4
            while app._operator_panel.snapshot is None and time.monotonic()<deadline:
                EventLoop.idle();time.sleep(.005)
            snapshot=app._operator_panel.snapshot
            self.assertIsNotNone(snapshot);self.assertEqual(len(snapshot.checks),6)
            self.assertEqual(snapshot.platform,'android');self.assertEqual(sends,[])
            self.screenshot(app,'health');app._close_operator()
