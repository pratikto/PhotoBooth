"""Actual owner pilot main/build/binding path, synthetic camera and transports."""
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import Mock, patch


class OwnerPilotRuntimeTests(unittest.TestCase):
    def test_actual_pilot_entry_reaches_original_paid_output_at_both_sizes(self):
        import numpy as np
        from kivy.base import EventLoop
        from kivy.config import Config
        from kivy.core.window import Window
        from photobooth.kiosk_v2.post_preview_checkout_app import PrivateCheckoutFixtureApp
        from tests.post_preview_checkout_fixture import CheckoutFixture
        from tests.test_post_preview_checkout_widgets import PrivateCheckoutWidgetTests
        from tools.run_post_preview_checkout_pilot import main

        helper=PrivateCheckoutWidgetTests(methodName='runTest')
        for size in ('452x900','800x1280'):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as folder:
                fixtures=[]
                camera=Mock()
                camera.read.side_effect=lambda: np.zeros((32,48,3),dtype=np.uint8)
                camera.preview.return_value=None
                camera.capture.isOpened.return_value=True
                def created(root):
                    fixture=CheckoutFixture(root)
                    fixtures.append(fixture)
                    return fixture
                def run(app):
                    app.build();app.root=app.stage
                    self.assertEqual(tuple(map(int,size.split('x'))),
                        (Config.getint('graphics','width'),Config.getint('graphics','height')))
                    Window.size=tuple(map(int,size.split('x')))
                    Window.add_widget(app.stage)
                    try:
                        fixture=fixtures[0]
                        self.assertIs(app._photo_jobs,fixture.authority.jobs)
                        self.assertIs(camera,fixture.camera)
                        self.assertIsNotNone(app._pilot_admission)
                        helper.proof(app)
                        helper.click(app,'SUDAH SIMPAN BUKTI • LANJUT SIMULASI');helper.settle(app)
                        helper.click(app,'SIMULASI PAID • TANPA TRANSFER');helper.settle(app)
                        deadline=time.monotonic()+10
                        while time.monotonic()<deadline and app._photo_view.get('phase')!='ticket_visible':
                            EventLoop.idle()
                            if app._ticket_card is not None:
                                app._ticket_card._ready_at=0
                                app._ticket_card._rendered(0)
                            app._poll_photos();time.sleep(.01)
                        self.assertEqual('ticket_visible',app._photo_view.get('phase'),app._photo_error)
                        helper.click(app,'LANJUT • SIMPAN TIKET')
                        deadline=time.monotonic()+10
                        while time.monotonic()<deadline and app._photo_view.get('phase')!='paid_delivery':
                            app._poll_photos();EventLoop.idle();time.sleep(.01)
                        self.assertEqual('paid_delivery',app._photo_view.get('phase'),app._photo_error)
                        helper.settle(app)  # Paid output advances automatically.
                        self.assertEqual(1,fixture.provider.charges)
                        self.assertEqual(1,len(fixture.receipt_sizes))
                        self.assertEqual([2,1],[copies for _,copies in fixture.paid_print_sends])
                        self.assertEqual('OWED',app._photo_view['delivery']['service_status'])
                        self.assertFalse(app._photo_view['delivery']['physical_paper_verified'])
                    finally:
                        app.on_stop();Window.remove_widget(app.stage)
                with patch.dict(os.environ,{
                    'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0','PHOTOBOOTH_V2_CHECKOUT_MOCK':'0',
                    'PHOTOBOOTH_V2_PRINT':'0','PHOTOBOOTH_V2_DRIVE':'0','PHOTOBOOTH_AUDIO':'0',
                    'PHOTOBOOTH_AD_VIDEO':'0','PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0'}), \
                    patch('tests.post_preview_checkout_fixture.CheckoutFixture',side_effect=created), \
                    patch('photobooth.kiosk_v2.app.AsyncCamera',return_value=camera), \
                    patch.object(PrivateCheckoutFixtureApp,'run',autospec=True,side_effect=run):
                    self.assertEqual(0,main(['--synthetic-payment-only','--private-root',str(Path(folder)/'fresh'),'--size',size]))
