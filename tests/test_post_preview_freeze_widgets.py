"""Native checkout button uses the original protected freeze, never fixture freeze."""
import hashlib
import os
from pathlib import Path
import threading
import unittest
from unittest.mock import patch

from kivy.base import EventLoop

from photobooth.kiosk_v2.flow import ADVERT,RESULT
from tests import test_post_preview_visits_widgets as visit_widgets
from tests import test_post_preview_widgets as photo_widgets


class ProtectedFreezeWidgetTests(unittest.TestCase):
    def setUp(self):
        self.ui=visit_widgets.ProtectedVisitWidgetTests(methodName='runTest')

    def final(self,app,f,quantities=None):
        self.ui.idle(app)
        app._choose_photo();app._complete_tutorial()
        app.quantities.update(quantities or {'template_a':2,'template_b':1})
        app._enter_photo_test();self.ui.idle(app)
        app._admit_photo_test();self.ui.idle(app)
        for _ in range(len(app._photo_jobs.service.selected)):
            for _ in range(3):
                photo_widgets.PrivateWidgetTests.shot(self,app)
            app._photo_submit('compose');self.ui.idle(app)
            app._photo_submit('next');self.ui.idle(app)
        self.assertEqual('final_preview',app._photo_view['phase'])
        self.assertEqual(RESULT,app.navigation.page)

    def settle(self,app):
        self.ui.idle(app)

    def no_money(self,service):
        for table in ('pp_payment_attempts','pp_purchase_finance','pp_paid_services'):
            self.assertEqual(0,service.ledger.db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0])

    def screenshot(self,label,size):
        target=os.environ.get('MEONG_PROTECTED_FREEZE_SCREENSHOTS')
        if target:
            from kivy.core.window import Window
            folder=Path(target);folder.mkdir(parents=True,exist_ok=True)
            for _ in range(4):EventLoop.idle()
            Window.screenshot(name=str(folder/(label+'-%sx%s.png'%size)))

    def test_original_native_checkout_button_freezes_before_any_charge_at_both_sizes(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size),self.ui.booth(size) as (app,f,control,worker):
                self.final(app,f)
                service=app._photo_jobs.service
                self.assertEqual(0,service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
                self.ui.click(app,'LANJUT PEMBAYARAN QRIS')
                self.ui.idle(app,lambda:app._photo_view.get('phase')=='checkout_ready')
                self.assertIs(app._photo_jobs,f.visits._jobs)
                self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
                self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_ccp_credentials').fetchone()[0])
                self.assertEqual(0,service.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
                self.assertEqual(0,service.ledger.db.execute('SELECT COUNT(*) FROM pp_paid_services').fetchone()[0])
                self.assertFalse((f.config.private_root/'fixture-output-send-count').exists())
                self.assertIsNotNone(app._claim_card)

    def test_actual_native_capture_checkout_ticket_and_automatic_2_1_delivery_at_both_sizes(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size),self.ui.booth(size) as (app,f,control,worker):
                self.final(app,f)
                service=app._photo_jobs.service;lease=service.lease
                photos=list((f.config.private_root/'media'/lease.draft_id).rglob('*.jpg'))
                self.assertEqual(6,len(photos))
                hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in photos}
                from kivy.core.window import Window
                for title in ('LANJUT PEMBAYARAN QRIS','UBAH DESAIN / JUMLAH'):
                    button=next(w for w in app.stage.walk() if getattr(w,'text',None)==title)
                    x,y=button.to_window(0,0,relative=True)
                    right,top=button.to_window(button.width,button.height,relative=True)
                    self.assertGreaterEqual(x,-1);self.assertGreaterEqual(y,-1)
                    self.assertLessEqual(right,Window.width+1);self.assertLessEqual(top,Window.height+1)
                self.screenshot('final-preview',size)
                # The frontend never calls the fixture/local freeze primitive.
                # Actual backend is in another process and owns this commit.
                with patch.object(service.checkout,'freeze',side_effect=AssertionError('Backend freeze only')):
                    self.ui.click(app,'LANJUT PEMBAYARAN QRIS')
                    self.ui.idle(app,lambda:app._photo_view.get('phase')=='checkout_ready')
                self.no_money(service)
                self.assertIsNotNone(service.ledger.db.execute('SELECT offered_at FROM pp_ccp_credentials').fetchone()[0])
                self.assertFalse(any('SIMULASI PAID' in str(getattr(w,'text','')) for w in app.stage.walk()))
                group=service.group
                app._freeze_checkout()  # A stale checkout callback cannot freeze/charge twice.
                self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
                self.ui.click(app,'SUDAH SIMPAN BUKTI • LANJUT QRIS')
                self.ui.idle(app,lambda:app._photo_view.get('phase')=='ticket_visible')
                self.assertTrue(app._ticket_window.active)
                self.assertGreater(app._ticket_window.remaining(),0)
                self.assertLessEqual(app._ticket_window.remaining(),30)
                self.assertIsNotNone(app._ticket_card.qr_image.texture)
                self.ui.click(app,'LANJUT • SIMPAN TIKET')
                self.ui.idle(app,lambda:bool((app._photo_view.get('delivery') or {}).get('print_all_submitted')))
                self.assertEqual(group,app._photo_view['purchase_group_id'])
                self.assertEqual([(2,'SUBMITTED'),(1,'SUBMITTED')],
                    [tuple(r) for r in service.ledger.db.execute('SELECT copies,state FROM pp_paid_strip_jobs ORDER BY template_id')])
                self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
                self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_ticket_credentials').fetchone()[0])
                self.assertEqual('DISMISSED',service.ledger.db.execute('SELECT screen_state FROM pp_ticket_presentations').fetchone()[0])
                self.assertEqual(3,f.output_count())
                self.assertEqual('OWED',app._photo_view['delivery']['service_status'])
                self.assertFalse(app._photo_view['delivery']['physical_paper_verified'])
                self.assertEqual(hashes,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in photos})
                self.screenshot('paid-result',size)

    def test_lost_freeze_reply_native_button_retries_same_original_group_without_new_money(self):
        with self.ui.booth() as (app,f,control,worker):
            self.final(app,f,{'template_a':1})
            service=app._photo_jobs.service;original=service.client._transport._call;lost=[]
            def dropped(method,path,**kwargs):
                result=original(method,path,**kwargs)
                if path.endswith('/freeze') and not lost:
                    lost.append(True);raise OSError('Synthetic lost protected freeze reply')
                return result
            with patch.object(service.client._transport,'_call',side_effect=dropped):
                self.ui.click(app,'LANJUT PEMBAYARAN QRIS');self.ui.idle(app)
                self.assertTrue(lost);self.assertEqual('final_preview',app._photo_view['phase'])
                group=service.ledger.db.execute('SELECT purchase_group_id FROM pp_checkout_intents').fetchone()[0]
                self.no_money(service)
                self.ui.click(app,'LANJUT PEMBAYARAN QRIS')
                self.ui.idle(app,lambda:app._photo_view.get('phase')=='checkout_ready')
            self.assertEqual(group,service.group)
            self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
            self.no_money(service)

    def test_committed_freeze_response_after_native_privacy_never_repaints_or_offers_ccp(self):
        with self.ui.booth() as (app,f,control,worker):
            self.final(app,f,{'template_a':1})
            service=app._photo_jobs.service;old_jobs=app._photo_jobs
            original=service.client._transport._call;entered=threading.Event();release=threading.Event()
            def held(method,path,**kwargs):
                result=original(method,path,**kwargs)
                if path.endswith('/freeze'):entered.set();release.wait(8)
                return result
            try:
                with patch.object(service.client._transport,'_call',side_effect=held):
                    self.ui.click(app,'LANJUT PEMBAYARAN QRIS')
                    self.assertTrue(entered.wait(5))
                    app._queue_private_retirement('APP_SUSPENDED')
                    self.assertEqual(ADVERT,app.navigation.page)
                    self.assertEqual({'phase':'hold'},app._photo_view)
                    app._freeze_checkout();release.set()
                    self.ui.idle(app,lambda:app._visit_ready and app._photo_jobs is not old_jobs)
                self.assertEqual(ADVERT,app.navigation.page)
                self.assertIsNone(app._claim_card);self.assertIsNone(app._ticket_card)
                self.assertEqual(1,f.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
                self.assertEqual(0,f.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_ccp_credentials').fetchone()[0])
                self.no_money(app._photo_jobs.service)
            finally:release.set()

    def test_foreign_native_jobs_binding_cannot_start_freeze_and_default_profile_stays_disabled(self):
        from photobooth.kiosk_v2.photos import PhotoJobs
        from tests import test_post_preview_protected_widgets as protected_widgets
        with self.ui.booth() as (app,f,control,worker):
            self.final(app,f,{'template_a':1});original_jobs=app._photo_jobs
            try:
                app._photo_jobs=PhotoJobs(original_jobs.service)
                with patch.object(original_jobs.service.client,'freeze_checkout',side_effect=AssertionError('No foreign worker RPC')):
                    app._freeze_checkout()
            finally:app._photo_jobs=original_jobs
            self.assertEqual(0,original_jobs.service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
        helper=protected_widgets.ProtectedNativeWidgetTests(methodName='runTest')
        with helper.booth() as (app,f):
            buttons=[w for w in app.stage.walk() if getattr(w,'text',None)=='CHECKOUT SANDBOX BELUM DIAKTIFKAN']
            self.assertEqual(1,len(buttons));self.assertTrue(buttons[0].disabled)


if __name__=='__main__':unittest.main()
