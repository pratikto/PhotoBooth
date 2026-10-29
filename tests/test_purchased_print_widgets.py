"""Existing native result widgets on an explicitly injected paid mock fixture."""
from contextlib import contextmanager,closing
import json
import os
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
from kivy.uix.image import Image

from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.flow import RESULT,ADVERT
from photobooth.kiosk_v2.photos import PhotoJobs
from tests.paid_print_scenario import PaidPrintScenario


class PaidPrintWidgetTests(unittest.TestCase):
    @contextmanager
    def booth(self,printer):
        with (TemporaryDirectory() as temp,closing(PaidPrintScenario(temp)) as scenario,
              patch.dict(os.environ,{'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0','PHOTOBOOTH_V2_CHECKOUT_MOCK':'0',
                'PHOTOBOOTH_V2_PRINT':'0','PHOTOBOOTH_V2_DRIVE':'0','PHOTOBOOTH_V2_STORAGE':'1',
                'PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_AD_VIDEO':'0','PHOTOBOOTH_CAMERA':'0',
                'PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0'})):
            camera=Mock();camera.read.return_value=np.zeros((80,120,3),dtype=np.uint8)
            app=PortraitKioskV2App(camera_device=camera);Window.add_widget(app.build())
            live={'active':True}
            app.navigation.page=RESULT
            adapter=scenario.adapter(printer,active=lambda:live['active'] and not app._closed and not app._suspended and app.navigation.page==RESULT)
            app._photo_jobs=PhotoJobs(adapter);app._photo_prepared=True
            app.quantities={t.template_id:scenario.quantities.get(t.template_id,0) for t in app.templates}
            app._photo_view=adapter.snapshot();app._show()
            try:yield app,scenario,adapter,live
            finally:
                app.on_stop();app._photo_jobs.wait_closed();Window.remove_widget(app.stage);EventLoop.idle()

    def settle(self,app):
        end=time.monotonic()+5
        while app._photo_jobs.busy and time.monotonic()<end:app._poll_photos();EventLoop.idle()
        app._poll_photos();self.assertFalse(app._photo_jobs.busy)

    def test_clock_single_flight_and_truthful_submission_at_both_portrait_sizes(self):
        original=Window.size
        try:
            for size in ((800,1280),(452,900)):
                with self.subTest(size=size):
                    Window.size=size;entered,release=threading.Event(),threading.Event()
                    printer=Mock()
                    def send(path,*,copies):
                        self.assertEqual(copies,2);entered.set()
                        if not release.wait(8):raise TimeoutError('fixture barrier')
                        return SimpleNamespace(success=True)
                    printer.print_image.side_effect=send
                    try:
                        with self.booth(printer) as (app,s,adapter,_):
                            app._photo_submit('print_result');self.assertTrue(entered.wait(2))
                            ticks=[];event=Clock.schedule_interval(lambda dt:ticks.append(dt),0)
                            try:
                                end=time.monotonic()+2
                                while len(ticks)<3 and time.monotonic()<end:EventLoop.idle()
                                self.assertGreaterEqual(len(ticks),3)
                                app._photo_submit('print_result')
                                self.assertIn('mengirim',app._delivery_label.text.lower())
                                self.assertEqual(next(iter(json.loads(s.manifest.read_text())['test_print_jobs'].values()))['state'],'SENDING')
                            finally:event.cancel();release.set()
                            self.settle(app)
                            self.assertEqual(app.navigation.page,RESULT)
                            self.assertEqual(app._photo_view['print_state'],'SUBMITTED')
                            self.assertIn('periksa lembar fisik',app._delivery_label.text.lower())
                            self.assertEqual(printer.print_image.call_count,1)
                            self.assertEqual(s.store.fulfillment(s.binding['order_id'],'PB001')['obligation_state'],'OWED')
                            self.assertIsNone(s.photo.printer)
                    finally:release.set()
        finally:Window.size=original

    def test_closed_result_callback_cannot_restore_private_strip_at_both_sizes(self):
        original=Window.size
        try:
            for size in ((800,1280),(452,900)):
                with self.subTest(size=size):
                    Window.size=size;entered,release=threading.Event(),threading.Event();printer=Mock()
                    def send(*args,**kwargs):
                        entered.set()
                        if not release.wait(8):raise TimeoutError('fixture barrier')
                        return SimpleNamespace(success=True)
                    printer.print_image.side_effect=send
                    try:
                        with self.booth(printer) as (app,s,adapter,live):
                            private_textures=[w.texture for w in app.stage.walk() if isinstance(w,Image) and w.texture and tuple(w.texture.size)==tuple(app._photo_view['strip'].size)]
                            self.assertTrue(private_textures)
                            app._photo_submit('print_result');self.assertTrue(entered.wait(2))
                            live['active']=False;adapter.photo.hide_private();app.on_stop()
                            Window.remove_widget(app.stage)
                            release.set();app._photo_jobs.wait_closed();app._poll_photos()
                            self.assertTrue(app._closed);self.assertNotIn(app.stage,Window.children)
                            self.assertEqual(adapter.snapshot(),{'phase':'claim_required'})
                            self.assertTrue(app._photo_jobs._results.empty())
                            self.assertFalse(any(isinstance(w,Image) and any(w.texture is t for t in private_textures)
                                                 for child in Window.children for w in child.walk()))
                            self.assertEqual(printer.print_image.call_count,1)
                            self.assertEqual(s.store.fulfillment(s.binding['order_id'],'PB001')['obligation_state'],'OWED')
                    finally:release.set()
        finally:Window.size=original
