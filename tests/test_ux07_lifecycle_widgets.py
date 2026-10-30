"""UX-07.l2a: original transport-off host/controller privacy, no commercial mounting."""
import hashlib
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
import numpy as np
from kivy.core.window import Window
from kivy.uix.image import Image
from photobooth.kiosk_v2.flow import CAPTURE,SANDBOX_CHECKOUT
from tests import test_kiosk_v2_sandbox_widgets as sandbox


class LifecyclePrivacyTests(unittest.TestCase):
    def helpers(self):
        return sandbox.SandboxWidgetTests()

    def private_start(self,h,app,f):
        ticket=h.start_private_capture(app,f)
        app._photo_submit('capture',np.zeros((120,160,3),dtype=np.uint8));h.settle(app)
        photo=app._photo_jobs.service
        self.assertIsNone(photo.printer);self.assertIsNone(photo.drive_client)
        files={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in photo.transaction.folder_path.rglob('*') if p.is_file()}
        return ticket,photo,files

    def assert_private(self,app,f):
        self.assertEqual(app.navigation.page,SANDBOX_CHECKOUT)
        self.assertEqual(app._photo_view,{})
        self.assertTrue(f.flow.customer_claim_required)
        self.assertFalse(app._sandbox_can_capture())
        self.assertIsNone(app._countdown_event)
        self.assertFalse(any(isinstance(w,Image) and w.texture is not None for w in app.stage.walk()
                             if getattr(w,'source','')==''))

    def test_pause_resume_requires_original_proof_and_deliberate_continuation_at_both_sizes(self):
        previous=Window.size
        try:
            for size in ((800,1280),(452,900)):
                with self.subTest(size=size):
                    Window.size=size;h=self.helpers()
                    with h.booth() as (app,f):
                        ticket,photo,files=self.private_start(h,app,f)
                        original=f.flow.snapshot();epoch=app._sandbox_privacy_epoch
                        with patch.object(photo,'capture',wraps=photo.capture) as capture, patch.object(photo,'print_result',wraps=photo.print_result) as printing:
                            app.on_pause();self.assertGreater(app._sandbox_privacy_epoch,epoch)
                            app.on_resume();h.settle(app);self.assert_private(app,f)
                            # Foreign-booth and incorrect original secret never reveal media.
                            for invalid in (ticket.replace(':PB001:',':PB002:'),ticket.rsplit(':',1)[0]+':'+'B'*43):
                                app._sandbox_claim_input.text=invalid;app._sandbox_claim();h.settle(app)
                                self.assert_private(app,f)
                            self.assertEqual({p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},files)
                            self.assertEqual(f.flow.snapshot()['transaction_id'],original['transaction_id'])
                            self.assertEqual(f.flow.snapshot()['quantities'],original['quantities'])
                            self.assertEqual(f.store.fulfillment(original['order']['order_id'],'PB001')['obligation_state'],'OWED')
                            app._sandbox_claim_input.text=ticket;app._sandbox_claim();h.settle(app)
                            self.assertTrue(app._sandbox_view['resume_ready']);self.assertEqual(app._photo_view,{})
                            app._sandbox_resume();h.settle(app)
                            self.assertEqual(app.navigation.page,CAPTURE)
                            self.assertEqual(app._photo_view['captured'],1)
                            self.assertEqual(app._photo_view['transaction_id'],original['transaction_id'])
                            self.assertIsNone(app._countdown_event)
                            capture.assert_not_called();printing.assert_not_called()
                        self.assertEqual(f.provider.charges,1)
        finally:Window.size=previous

    def test_claim_reply_retired_by_pause_cannot_restore_media_at_both_sizes(self):
        previous=Window.size
        try:
            for size in ((800,1280),(452,900)):
                with self.subTest(size=size):
                    Window.size=size;h=self.helpers()
                    with h.booth() as (app,f):
                        ticket,photo,files=self.private_start(h,app,f)
                        app._sandbox_lock_customer()
                        entered,release=threading.Event(),threading.Event()
                        original=f.flow.client.customer_claim
                        def delayed(*args):
                            result=original(*args);entered.set()
                            if not release.wait(5):raise RuntimeError('Fixture callback did not drain')
                            return result
                        with patch.object(f.flow.client,'customer_claim',side_effect=delayed):
                            app._sandbox_claim_input.text=ticket;app._sandbox_claim()
                            try:
                                self.assertTrue(entered.wait(2));app.on_pause();app.on_resume()
                            finally:release.set()
                            h.settle(app)
                        self.assert_private(app,f)
                        self.assertEqual(f.provider.charges,1)
                        self.assertEqual({p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},files)
                        self.assertIsNone(photo.printer);self.assertIsNone(photo.drive_client)
        finally:Window.size=previous
