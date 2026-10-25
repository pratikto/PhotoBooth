"""Native v2 print/Drive handoff; cameras, transports and cloud are fixtures."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch

import numpy as np
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window

from photobooth.catalog import get_templates
from photobooth.manifest_io import write_json_atomic
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.flow import ADVERT,PHOTO_CONFIRM,RESULT
from photobooth.kiosk_v2.photos import PhotoTest,PhotoSetupError
from photobooth.kiosk_v2.theme import ArcadeButton


class DeliveryWidgetTests(unittest.TestCase):
    @contextmanager
    def booth(self,service_factory=None,*,drive=False):
        with TemporaryDirectory() as temp,patch.dict(os.environ,{
                'PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_AD_VIDEO':'0','PHOTOBOOTH_CAMERA':'0',
                'PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0',
                'PHOTOBOOTH_V2_CHECKOUT_MOCK':'0','PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0',
                'PHOTOBOOTH_V2_DRIVE':'1' if drive else '0'}):
            root=Path(temp);printer=Mock();printer.print_image.return_value=SimpleNamespace(success=True)
            service=PhotoTest(root,printer=printer,auto_print=True)
            camera=Mock();camera.read.return_value=np.zeros((80,120,3),dtype=np.uint8)
            with patch('photobooth.kiosk_v2.photos.configured_test',side_effect=service_factory or (lambda *_a,**_k:service)) as factory:
                app=PortraitKioskV2App(camera_device=camera);Window.add_widget(app.build())
                try:yield app,service,printer,factory,root
                finally:
                    app.on_stop()
                    if app._photo_jobs:app._photo_jobs.wait_closed()
                    service.close();Window.remove_widget(app.stage);EventLoop.idle()
    def settle(self,app):
        end=time.monotonic()+5
        while app._photo_jobs and app._photo_jobs.busy and time.monotonic()<end:
            app._poll_photos();EventLoop.idle();time.sleep(.003)
        app._poll_photos()
        self.assertFalse(app._photo_jobs.busy)
    def enter(self,app,*,two=False):
        app._choose_photo();app._complete_tutorial();app._change_copies(2)
        if two:app.quantities[get_templates()[1].template_id]=1
        app._enter_photo_test();self.settle(app);app._admit_photo_test();self.settle(app)
    def review(self,app):
        for _ in range(3):app._photo_submit('capture',app.camera_device.read());self.settle(app)
    def test_approved_strip_auto_prints_once_with_responsive_heartbeat_resize_and_minimize(self):
        entered=threading.Event();release=threading.Event()
        with self.booth() as (app,service,printer,_,root):
            self.enter(app);self.review(app);printer.print_image.assert_not_called()
            def send(*_a,**_kw):entered.set();release.wait(3);return SimpleNamespace(success=True)
            printer.print_image.side_effect=send;ticks=[]
            timer=Clock.schedule_interval(lambda dt:ticks.append(dt),.01);original=Window.size
            try:
                app._photo_submit('compose')
                until=time.monotonic()+3
                while not entered.is_set() and time.monotonic()<until:app._poll_photos();EventLoop.idle()
                self.assertTrue(entered.is_set());self.assertEqual(app.navigation.page,RESULT)
                self.assertTrue(app._photo_jobs.busy)
                for _ in range(8):EventLoop.idle()
                self.assertGreater(len(ticks),3)
                for size in ((800,1280),(452,900),(360,640)):
                    Window.size=size;EventLoop.idle();app._show()
                app.on_pause();app.on_resume()
                self.assertEqual(printer.print_image.call_count,1)
                release.set();self.settle(app)
                self.assertEqual(printer.print_image.call_args.kwargs['copies'],2)
                self.assertEqual(app._photo_view['print_state'],'SUBMITTED')
                auto=next(w for w in app.stage.walk() if isinstance(w,ArcadeButton) and 'CETAK OTOMATIS' in w.text)
                self.assertTrue(auto.disabled);auto.dispatch('on_release');self.assertEqual(printer.print_image.call_count,1)
            finally:release.set();timer.cancel();Window.size=original
    def test_two_designs_print_exact_copy_counts_and_no_new_capture_for_copies(self):
        with self.booth() as (app,service,printer,_,root):
            self.enter(app,two=True)
            for n in range(2):
                self.review(app);app._photo_submit('compose');self.settle(app)
                self.assertEqual(app._photo_view['print_state'],'SUBMITTED')
                app._photo_submit('next');self.settle(app)
            self.assertEqual(app.navigation.page,ADVERT)
            self.assertEqual([c.kwargs['copies'] for c in printer.print_image.call_args_list],[2,1])
            self.assertEqual(len(list(root.rglob('photo_*.jpg'))),6)
    def test_uncertain_auto_send_does_not_retry_and_requires_operator_ack(self):
        with self.booth() as (app,service,printer,_,root):
            printer.print_image.side_effect=OSError('fixture uncertain send')
            self.enter(app);self.review(app);app._photo_submit('compose');self.settle(app)
            self.assertEqual(app._photo_view['print_state'],'UNCERTAIN')
            finish=next(w for w in app.stage.walk() if isinstance(w,ArcadeButton) and 'SELESAI' in w.text)
            self.assertTrue(finish.disabled)
            app.on_pause();app.on_resume();app._show();self.assertEqual(printer.print_image.call_count,1)
            app._photo_submit('acknowledge_print');self.settle(app)
            app._photo_submit('next');self.settle(app)
            self.assertEqual(app.navigation.page,ADVERT);self.assertEqual(printer.print_image.call_count,1)
    def test_boot_preparation_is_background_no_ad_reset_no_second_service_and_live_ready_gate(self):
        entered=threading.Event();release=threading.Event();threads=[];ui=threading.get_ident()
        with self.booth(drive=True) as (app,service,_,factory,root):
            service.drive_client=Mock();pool=service.pool=Mock()
            pool.has_ready_slot.return_value=False;pool.last_error=None
            def prepare():
                threads.append(threading.get_ident());entered.set();release.wait(3);return service.snapshot()
            with patch.object(service,'prepare',side_effect=prepare):
                player=app._ad_player;app._warm_photo_delivery()
                self.assertTrue(entered.wait(1));self.assertEqual(app.navigation.page,ADVERT)
                release.set();self.settle(app)
                self.assertIs(app._ad_player,player);self.assertEqual(factory.call_count,1)
                self.assertNotEqual(threads[0],ui);self.assertFalse(list(root.rglob('manifest.json')))
                app._choose_photo();app._complete_tutorial();app._change_copies(1)
                app._enter_photo_test();self.settle(app)
                consent=next(w for w in app.stage.walk() if isinstance(w,ArcadeButton) and w.text=='SETUJU & MULAI UJI FOTO')
                self.assertTrue(consent.disabled);app._admit_photo_test();self.assertIsNone(service.transaction)
                pool.has_ready_slot.return_value=True;app._photo_refresh_at=0
                app._poll_photos();self.settle(app)
                consent=next(w for w in app.stage.walk() if isinstance(w,ArcadeButton) and w.text=='SETUJU & MULAI UJI FOTO')
                self.assertFalse(consent.disabled);self.assertEqual(factory.call_count,1)
    def test_missing_drive_config_stays_on_consent_without_fake_qr_or_capture(self):
        def unavailable(*_a,**_k):raise PhotoSetupError('drive_configuration')
        with self.booth(service_factory=unavailable) as (app,service,_,factory,root):
            app._choose_photo();app._complete_tutorial();app._change_copies(1)
            app._enter_photo_test();self.settle(app)
            self.assertEqual(app.navigation.page,PHOTO_CONFIRM)
            self.assertIn('Drive belum dikonfigurasi',app._photo_error)
            self.assertFalse(app._photo_prepared);self.assertIsNone(service.transaction)
            self.assertFalse(list(root.rglob('manifest.json')))
    def test_verified_qr_arrives_without_rebuilding_result_or_reprinting(self):
        with self.booth() as (app,service,printer,_,root):
            self.enter(app);self.review(app)
            manifest=service.transaction.manifest;url='https://example.test/photos/v2'
            manifest.update(drive_folder_url=url,upload_status='PENDING_UPLOAD')
            write_json_atomic(service.transaction.manifest_path,manifest)
            app._photo_submit('compose');self.settle(app)
            self.assertIsNotNone(app._download_image);self.assertEqual(app._download_image.opacity,0)
            image=app._download_image;stage=app.stage.current_screen
            manifest=json.loads(service.transaction.manifest_path.read_text());manifest['upload_status']='UPLOAD_COMPLETE'
            write_json_atomic(service.transaction.manifest_path,manifest)
            app._photo_submit('snapshot');self.settle(app)
            self.assertIs(app._download_image,image);self.assertIs(app.stage.current_screen,stage)
            self.assertEqual(image.opacity,1);self.assertEqual(printer.print_image.call_count,1)
            import cv2
            photo=app._photo_view['download_qr'];decoded,_,_=cv2.QRCodeDetector().detectAndDecode(np.asarray(photo))
            self.assertEqual(decoded,url)
