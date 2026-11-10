"""Actual native Ads/control/original child visits; external effects fake.

Freeze uses the existing explicit fixture primitive, not a customer launcher.
"""
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import threading
import time
import unittest
from unittest.mock import Mock,patch

from kivy.base import EventLoop
from kivy.core.window import Window
from kivy.uix.image import Image

from photobooth.kiosk_v2.flow import ADVERT,RESULT
from photobooth.kiosk_v2.post_preview_visits_app import ProtectedVisitsApp
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.kiosk_v2.operator_health import OperatorMeongLogo
from photobooth.post_preview_visit_control import create_visit_control
from tests import test_post_preview_sandbox_visits as fixtures


class ProtectedVisitWidgetTests(unittest.TestCase):
    @contextmanager
    def booth(self,size=(452,900)):
        with patch.dict(os.environ,{'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0',
                'PHOTOBOOTH_V2_CHECKOUT_MOCK':'0','PHOTOBOOTH_V2_PRINT':'0',
                'PHOTOBOOTH_V2_DRIVE':'0','PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_AD_VIDEO':'0',
                'PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0'}):
            f=fixtures.OriginalSandboxVisitTests();f.setUp()
            control,worker=create_visit_control(f.visits)
            app=None
            try:
                self.assertTrue(control.start())
                deadline=time.monotonic()+12;result=None
                while result is None and time.monotonic()<deadline:
                    result=control.poll();time.sleep(.02)
                self.assertIsNotNone(result);self.assertEqual('READY',result.state)
                Window.size=size
                camera=Mock();camera.read.return_value=f.frame;camera.preview.return_value=None
                app=ProtectedVisitsApp(f.config.private_root,visit_control=control,camera_device=camera)
                app.build();app.root=app.stage;Window.add_widget(app.stage)
                self.assertIs(app._photo_jobs,f.visits._jobs)
                yield app,f,control,worker
            finally:
                if app is not None:
                    app.on_stop()
                    if app.stage.parent:Window.remove_widget(app.stage)
                self.assertTrue(worker.stop(timeout=12),'Actual original trusted shutdown held')
                f.doCleanups()

    def idle(self,app,predicate=None,timeout=18):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            EventLoop.idle();app._poll_photos()
            if predicate is not None and predicate():return
            if predicate is None and not app._visit_control.busy and not app._photo_jobs.busy:return
            time.sleep(.01)
        self.fail('Original native visits did not reach expected state: '+
                  app._visit_control.state+' '+str(app._photo_view.get('phase')))

    def click(self,app,title):
        buttons=[w for w in app.stage.walk() if getattr(w,'text',None)==title]
        self.assertEqual(1,len(buttons),title);self.assertFalse(buttons[0].disabled,title)
        buttons[0].dispatch('on_release')

    def paid_result(self,app,f,quantities=None,*,recovery=False):
        service=app._photo_jobs.service;original=service.prepare_ticket;ticket=[]
        def capture_ticket():
            view=original();ticket.append(view['ticket_offer'].qr_payload);return view
        with patch.object(service,'prepare_ticket',side_effect=capture_ticket):
            group,proof=f.paid(app._visit_control.binding,quantities)
        app._photo_view=app._photo_jobs.service.snapshot()
        app.navigation.page=RESULT;app._show();self.idle(app)
        self.assertEqual('paid_delivery',app._photo_view['phase'])
        return group,ticket[0] if recovery else proof

    def expire(self,app):
        old=app._photo_jobs
        app._paid_result_deadline=time.monotonic()-1;app._poll_photos()
        self.assertEqual(ADVERT,app.navigation.page)
        self.assertEqual({'phase':'hold'},app._photo_view)
        self.idle(app,lambda:app._visit_ready and app._photo_jobs is not old)
        self.assertIs(app._photo_jobs,app._visit_control.binding.jobs)

    def claim(self,app,proof):
        self.click(app,'PUNYA TIKET PEMULIHAN')
        popup,field=app._pilot_popup,app._pilot_input
        self.assertEqual('PEMULIHAN PRIVAT • SANDBOX',popup.title)
        field.text=proof
        buttons=[w for w in popup.content.walk() if getattr(w,'text',None)=='VALIDASI TIKET']
        self.assertEqual(1,len(buttons));buttons[0].dispatch('on_release')
        self.assertEqual('',field.text);self.assertIsNone(app._pilot_input)

    def test_actual_native_A_B_A_original_popup_and_jobs_at_both_portrait_sizes(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size),self.booth(size) as (app,f,control,worker):
                group,proof=self.paid_result(app,f,{'template_a':2,'template_b':1},recovery=size==(452,900))
                draft=app._photo_jobs.service.lease.draft_id
                original_entitlement=f.visits.ledger.db.execute(
                    'SELECT entitlement_id FROM pp_purchase_finance WHERE purchase_group_id=?',(group,)).fetchone()[0]
                hashes={str(p.relative_to(f.config.private_root)):hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (f.config.private_root/'media'/draft).rglob('*') if p.is_file()}
                self.assertTrue(hashes)
                self.expire(app)
                self.assertTrue(all(q==0 for q in app.quantities.values()))
                app._choose_photo();self.assertNotEqual(ADVERT,app.navigation.page)
                app._return_ad()
                self.idle(app,lambda:app._visit_ready and not control.busy)
                self.paid_result(app,f)
                self.expire(app)
                sends=f.output_count()
                self.claim(app,proof)
                app._choose_photo();app._choose_game()
                self.assertEqual(ADVERT,app.navigation.page)
                self.idle(app,lambda:app._photo_view.get('phase')=='paid_delivery')
                self.assertEqual(group,app._photo_view['purchase_group_id'])
                self.assertEqual(sends,f.output_count())
                self.assertEqual(2,f.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
                self.assertEqual(original_entitlement,f.visits.ledger.db.execute(
                    'SELECT entitlement_id FROM pp_purchase_finance WHERE purchase_group_id=?',(group,)).fetchone()[0])
                self.assertEqual(hashes,{str(p.relative_to(f.config.private_root)):hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (f.config.private_root/'media'/draft).rglob('*') if p.is_file()})
                self.assertIs(app._photo_jobs,f.visits._jobs)
                self.assertFalse(any(value is f.visits or value is worker for value in vars(app).values()))
                target=os.environ.get('MEONG_PROTECTED_VISITS_SCREENSHOTS')
                if target:
                    folder=Path(target);folder.mkdir(parents=True,exist_ok=True)
                    for _ in range(4):EventLoop.idle()
                    Window.screenshot(name=str(folder/('restored-%sx%s.png'%size)))

    def test_native_minimize_during_late_claim_hides_input_and_never_paints_late_private_result(self):
        with self.booth() as (app,f,control,worker):
            group,proof=self.paid_result(app,f);self.expire(app)
            service=app._photo_jobs.service
            entered,release=threading.Event(),threading.Event();original=service._handoff.claim
            def held(*args):
                grant=original(*args);entered.set();release.wait(8);return grant
            try:
                with patch.object(service._handoff,'claim',side_effect=held):
                    self.claim(app,proof)
                    self.idle(app,entered.is_set)
                    started=time.monotonic();app.on_pause()
                    self.assertLess(time.monotonic()-started,1)
                    self.assertEqual({'phase':'hold'},app._photo_view)
                    self.assertIsNone(app._pilot_input);self.assertIsNone(app._ticket_card)
                    app.on_resume();release.set()
                    self.idle(app,lambda:app._visit_ready and not control.busy)
                self.assertEqual(ADVERT,app.navigation.page)
                self.assertEqual('confirm',app._photo_view['phase'])
                self.assertNotIn(proof,repr(vars(control)))
                self.assertEqual('OWED',f.visits.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
            finally:release.set()

    def test_original_unserved_paid_claim_renders_ticket_then_automatic_delivery(self):
        with self.booth() as (app,f,control,worker):
            group,proof=f.frozen(control.binding,{'template_a':2,'template_b':1})
            service=app._photo_jobs.service;service.begin_payment()
            def settled():
                view=service.check_payment('connectivity')
                if view['phase']!='paid_hold':raise fixtures.DraftHeld('Original settlement pacing')
                return view
            f.retry(settled)
            app._queue_private_retirement('APP_SUSPENDED')
            self.idle(app,lambda:app._visit_ready and not control.busy)
            self.claim(app,proof)
            self.idle(app,lambda:app._photo_view.get('phase')=='ticket_visible')
            self.assertTrue(app._ticket_window.active)
            self.assertIsNotNone(app._ticket_card.qr_image.texture)
            self.click(app,'LANJUT • SIMPAN TIKET')
            self.idle(app,lambda:bool((app._photo_view.get('delivery') or {}).get('print_all_submitted')))
            self.assertEqual(group,app._photo_view['purchase_group_id'])
            self.assertEqual(1,f.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
            self.assertEqual('OWED',f.visits.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_native_stop_does_not_close_original_ledger_under_blocked_photo_io(self):
        with self.booth() as (app,f,control,worker):
            jobs=app._photo_jobs;service=jobs.service
            entered,release=threading.Event(),threading.Event();original=service.snapshot
            def held():entered.set();release.wait(8);return original()
            try:
                with patch.object(service,'snapshot',side_effect=held):
                    self.assertTrue(jobs.submit('snapshot'));self.assertTrue(entered.wait(2))
                    started=time.monotonic();app.on_stop()
                    self.assertLess(time.monotonic()-started,1)
                    self.assertFalse(worker.stop(timeout=.1));self.assertFalse(control.stopped)
                    self.assertEqual(1,service.ledger.db.execute('SELECT 1').fetchone()[0])
                    with self.assertRaises(OSError):LaunchLease(f.config.private_root)
                    release.set()
                self.assertTrue(worker.stop(timeout=12));self.assertTrue(control.stopped)
                self.assertTrue(service._closed.is_set())
            finally:release.set()

    def test_paid_result_logo_qr_and_status_button_fit_live_resize_without_new_payment(self):
        with self.booth((800,1280)) as (app,f,control,worker):
            self.paid_result(app,f,{'template_a':2,'template_b':1})
            deadline=app._paid_result_deadline
            for size in ((800,1280),(452,900),(800,1280)):
                Window.size=size
                for _ in range(5):EventLoop.idle()
                self.assertEqual(size,tuple(Window.size))
                widgets=[w for w in app.stage.walk() if isinstance(w,(OperatorMeongLogo,Image))
                         or getattr(w,'text',None)=='CEK STATUS UPLOAD']
                self.assertGreaterEqual(len(widgets),3)
                for widget in widgets:
                    x,y=widget.to_window(0,0,relative=True)
                    right,top=widget.to_window(widget.width,widget.height,relative=True)
                    self.assertGreaterEqual(x,-1);self.assertGreaterEqual(y,-1)
                    self.assertLessEqual(right,Window.width+1)
                    self.assertLessEqual(top,Window.height+1)
                self.assertEqual(deadline,app._paid_result_deadline)
                self.assertEqual(1,f.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
