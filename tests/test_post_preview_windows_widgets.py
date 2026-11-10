"""New Windows entry factory mounts the original native checkout at both sizes."""
import time
import sqlite3
from contextlib import closing
import unittest
from unittest.mock import Mock,patch
import io

from kivy.core.window import Window

from photobooth.post_preview_visit_control import create_visit_control
from photobooth.post_preview_native_exit import drain_native_app
from tests import test_post_preview_sandbox_visits as fixtures
from tests import test_post_preview_freeze_widgets as native
from tools.run_post_preview_sandbox import native_app


class ProtectedWindowsWidgetTests(unittest.TestCase):
    def test_owned_F8_copies_only_current_original_pending_qr_without_money_or_log(self):
        from kivy.core.clipboard import Clipboard
        from photobooth.kiosk_v2.owned_sandbox_simulator import OwnedSandboxSimulatorClipboard
        with patch.dict('os.environ',{'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0',
                'PHOTOBOOTH_V2_CHECKOUT_MOCK':'0','PHOTOBOOTH_V2_PRINT':'0',
                'PHOTOBOOTH_V2_DRIVE':'0','PHOTOBOOTH_AUDIO':'0',
                'PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0'}):
            f=fixtures.OriginalSandboxVisitTests(methodName='runTest');f.setUp()
            marker=f.config.private_root/'fixture-keep-pending';marker.write_text('public pending fixture')
            control,worker=create_visit_control(f.visits,finish_on_stop=True)
            helper=native.ProtectedFreezeWidgetTests(methodName='runTest');helper.setUp()
            app=bridge=None;buffer=[''];writes=[]
            def copy(value):buffer[0]=value;writes.append(bool(value))
            try:
                self.assertTrue(control.start());deadline=time.monotonic()+12;outcome=None
                while outcome is None and time.monotonic()<deadline:outcome=control.poll();time.sleep(.01)
                self.assertEqual('READY',outcome.state)
                camera=Mock();camera.read.return_value=f.frame;camera.preview.return_value=None
                Window.size=(452,900)
                app=native_app(control,camera,f.config.private_root,'452x900')
                app.build();app.root=app.stage;Window.add_widget(app.stage)
                with patch.object(Clipboard,'copy',side_effect=copy),patch.object(Clipboard,'paste',side_effect=lambda:buffer[0]):
                    bridge=OwnedSandboxSimulatorClipboard(app);bridge.install()
                    self.assertFalse(bridge.copy_current())
                    helper.final(app,f);helper.ui.click(app,'LANJUT PEMBAYARAN QRIS')
                    helper.ui.idle(app,lambda:app._photo_view.get('phase')=='checkout_ready')
                    self.assertFalse(bridge.copy_current())
                    helper.ui.click(app,'SUDAH SIMPAN BUKTI • LANJUT QRIS')
                    helper.ui.idle(app,lambda:app._photo_view.get('phase')=='payment_pending')
                    expected=app._photo_view['payment']['qr_url']
                    with patch('sys.stdout',new_callable=io.StringIO) as output:
                        Window.dispatch('on_key_down',289,0,'',[])
                    self.assertIn('SANDBOX_SIMULATOR_QR_COPIED',output.getvalue())
                    self.assertFalse(expected in output.getvalue())
                    self.assertTrue(buffer[0]==expected)
                    self.assertEqual([True],writes)
                    self.assertEqual(1,f.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
                    self.assertEqual(0,f.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_purchase_finance WHERE entitlement_id IS NOT NULL').fetchone()[0])
                    self.assertFalse((f.config.private_root/'fixture-output-send-count').exists())
                    app._suspended=True;self.assertFalse(bridge.copy_current());app._suspended=False
                    def late_copy(value):
                        copy(value)
                        if value:app._suspended=True
                    with patch.object(Clipboard,'copy',side_effect=late_copy):
                        self.assertFalse(bridge.copy_current())
                    self.assertEqual('',buffer[0]);app._suspended=False
                    app._photo_view['payment']['qr_url']='https://other.invalid/qr-code'
                    self.assertFalse(bridge.copy_current())
                    app._photo_view['payment']['qr_url']=expected
                    marker.unlink();helper.ui.click(app,'PERIKSA STATUS')
                    helper.ui.idle(app,lambda:app._photo_view.get('phase')=='ticket_visible')
                    self.assertFalse(bridge.copy_current())
                    buffer[0]='owner-new-private-clipboard'
                    bridge.close();self.assertEqual('owner-new-private-clipboard',buffer[0]);bridge=None
                    helper.ui.click(app,'LANJUT • SIMPAN TIKET')
                    helper.ui.idle(app,lambda:bool((app._photo_view.get('delivery') or {}).get('print_all_submitted')))
                    self.assertEqual(3,f.output_count())
            finally:
                if marker.exists():marker.unlink()
                if bridge is not None:bridge.close()
                if app is not None:
                    app.on_stop()
                    if app.stage.parent:Window.remove_widget(app.stage)
                    self.assertTrue(drain_native_app(app,timeout=3))
                self.assertTrue(worker.stop(timeout=12));f.doCleanups()

    def test_entry_factory_drives_original_native_checkout_and_automatic_output_at_both_sizes(self):
        for size in ((452,900),(800,1280)):
            with self.subTest(size=size),patch.dict('os.environ',{'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0',
                    'PHOTOBOOTH_V2_CHECKOUT_MOCK':'0','PHOTOBOOTH_V2_PRINT':'0','PHOTOBOOTH_V2_DRIVE':'0',
                    'PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0'}):
                f=fixtures.OriginalSandboxVisitTests(methodName='runTest');f.setUp()
                control,worker=create_visit_control(f.visits,finish_on_stop=True);app=None
                helper=native.ProtectedFreezeWidgetTests(methodName='runTest');helper.setUp()
                try:
                    self.assertTrue(control.start());deadline=time.monotonic()+12;outcome=None
                    while outcome is None and time.monotonic()<deadline:
                        outcome=control.poll();time.sleep(.01)
                    self.assertIsNotNone(outcome);self.assertEqual('READY',outcome.state)
                    camera=Mock();camera.read.return_value=f.frame;camera.preview.return_value=None
                    Window.size=size
                    app=native_app(control,camera,f.config.private_root,'%sx%s'%size)
                    app.build();app.root=app.stage;Window.add_widget(app.stage)
                    self.assertIs(camera,app.camera_device);self.assertIs(control.binding.jobs,app._photo_jobs)
                    helper.final(app,f)
                    helper.ui.click(app,'LANJUT PEMBAYARAN QRIS')
                    helper.ui.idle(app,lambda:app._photo_view.get('phase')=='checkout_ready')
                    helper.no_money(app._photo_jobs.service)
                    helper.ui.click(app,'SUDAH SIMPAN BUKTI • LANJUT QRIS')
                    helper.ui.idle(app,lambda:app._photo_view.get('phase')=='ticket_visible')
                    helper.ui.click(app,'LANJUT • SIMPAN TIKET')
                    helper.ui.idle(app,lambda:bool((app._photo_view.get('delivery') or {}).get('print_all_submitted')))
                    self.assertEqual(3,f.output_count())
                    self.assertEqual('OWED',app._photo_view['delivery']['service_status'])
                finally:
                    if app is not None:
                        app.on_stop()
                        if app.stage.parent:Window.remove_widget(app.stage)
                        self.assertTrue(drain_native_app(app,timeout=3))
                    self.assertTrue(worker.stop(timeout=12))
                    with closing(sqlite3.connect((f.config.private_root/'drafts.sqlite3').as_uri()+'?mode=ro',uri=True)) as db:
                        self.assertEqual([(1,'ISOLATED')],db.execute('SELECT closed,lifecycle FROM pp_drafts').fetchall())
                        self.assertEqual([('ACKED',)],db.execute('SELECT state FROM pp_isolation_ops').fetchall())
                        self.assertEqual([('OWED',)],db.execute('SELECT status FROM pp_paid_services').fetchall())
                    f.doCleanups()


if __name__=='__main__':unittest.main()
