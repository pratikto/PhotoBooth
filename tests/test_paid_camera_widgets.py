"""Original HTTP payment -> one paper recovery receipt -> camera -> approved strip."""
from unittest import TestCase
from unittest.mock import Mock, patch
import time
import numpy as np
from kivy.core.window import Window

import tests.test_kiosk_v2_sandbox_widgets as fixture
from photobooth.kiosk_v2.flow import CAPTURE, SANDBOX_CHECKOUT
from photobooth.printer import ThermalPrinter, PrinterConfig


class PaidCameraTests(TestCase):
    def test_dedicated_configuration_mounts_both_printers_with_drive_off(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        import os
        from photobooth.kiosk_v2.photos import configured_test
        from photobooth.kiosk_v2.sandbox_checkout import configured_sandbox
        with TemporaryDirectory() as directory:
            root=Path(directory);journal=root/'data'/'kiosk-v2-sandbox'/'MTEST'/'PB001'/'visit.json'
            env={'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'1','PHOTOBOOTH_V2_CHECKOUT_MOCK':'0',
                 'PHOTOBOOTH_V2_SANDBOX_PRINT':'1','PHOTOBOOTH_V2_PRINT':'1','PHOTOBOOTH_V2_DRIVE':'0',
                 'PHOTOBOOTH_V2_STORAGE':'1','MIDTRANS_SERVER_KEY':'','MIDTRANS_MERCHANT_ID':'',
                 'MEONG_QRIS_MODE':'sandbox','MEONG_QRIS_JOURNAL':str(journal)}
            client=Mock(booth_id='PB001',base_url='http://127.0.0.1:8765')
            with patch.dict(os.environ,env),patch('photobooth.kiosk_v2.sandbox_checkout.QrisKioskClient',return_value=client):
                checkout=configured_sandbox(root,dict(os.environ))
                photos=configured_test(journal.parent/'photos',configuration_root=root,storage_layout=1)
                try:
                    self.assertIsInstance(checkout.receipt_printer,ThermalPrinter)
                    self.assertIsInstance(photos.printer,ThermalPrinter)
                    self.assertEqual(checkout.receipt_printer.config,photos.printer.config)
                    self.assertTrue(photos.auto_print);self.assertTrue(photos.sandbox_print)
                    self.assertIsNone(photos.drive_client);self.assertIsNone(photos.workspace)
                finally:checkout.close();photos.close()

    def test_paid_prints_one_receipt_enters_camera_then_approved_photo_prints_once_at_both_sizes(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size),patch.object(ThermalPrinter,'raster_payload',return_value=b'SYNTHETIC RASTER'):
                sender=Mock();printer=ThermalPrinter(PrinterConfig(print_width_dots=384),usb_sender=sender)
                h=fixture.SandboxWidgetTests()
                with h.booth(printer=printer) as (app,f):
                    Window.size=size;f.flow.qr_renewal_enabled=True;h.pending(app)
                    self.assertEqual(sender.call_count,0)
                    f.paid();app._sandbox_retry();h.settle(app)
                    self.assertEqual(app.navigation.page,CAPTURE);self.assertEqual(sender.call_count,1)
                    self.assertEqual(f.flow.snapshot()['recovery_receipt']['state'],'SUBMITTED')
                    self.assertEqual(app._photo_view['captured'],0);self.assertIsNone(app._countdown_event)
                    labels=[getattr(w,'text','') for w in app.stage.walk()]
                    self.assertNotIn('SIMPAN TIKET PEMULIHAN',labels);self.assertNotIn('SUDAH SIMPAN • LANJUT',labels)
                    original=f.flow.snapshot()['order']['order_id']
                    for _ in range(3):
                        app._photo_submit('capture',np.zeros((120,160,3),dtype=np.uint8));h.settle(app)
                    self.assertEqual(sender.call_count,1)
                    app._photo_submit('compose');h.settle(app)
                    self.assertEqual(sender.call_count,2)
                    self.assertEqual(app._photo_view['print_state'],'SUBMITTED')
                    app._show();app._sandbox_submit('check');h.settle(app)
                    self.assertEqual(sender.call_count,2);self.assertEqual(f.provider.charges,1)
                    self.assertEqual(f.flow.snapshot()['order']['order_id'],original)

    def test_old_payment_idle_time_does_not_lock_newly_paid_camera(self):
        h=fixture.SandboxWidgetTests()
        with h.booth() as (app,f):
            f.flow.qr_renewal_enabled=True;h.pending(app)
            app._last_activity=time.monotonic()-120;app._tick(0)
            self.assertFalse(f.flow.customer_claim_required)
            f.paid();app._sandbox_retry();h.settle(app);app._tick(0)
            self.assertEqual(app.navigation.page,CAPTURE);self.assertFalse(f.flow.customer_claim_required)
            self.assertLess(time.monotonic()-app._last_activity,5)

    def test_minimized_live_checkout_can_accept_payment_without_unprinted_ticket_claim(self):
        h=fixture.SandboxWidgetTests()
        with h.booth() as (app,f):
            f.flow.qr_renewal_enabled=True;h.pending(app)
            app.on_pause();self.assertFalse(f.flow.customer_claim_required)
            f.paid();app.on_resume();app._sandbox_retry();h.settle(app)
            self.assertEqual(app.navigation.page,CAPTURE);self.assertEqual(f.provider.charges,1)

    def test_allocated_private_photos_still_lock_and_never_reprint_receipt_on_check(self):
        h=fixture.SandboxWidgetTests()
        with h.booth() as (app,f):
            f.flow.qr_renewal_enabled=True;h.pending(app)
            f.paid();app._sandbox_retry();h.settle(app)
            self.assertEqual(app.navigation.page,CAPTURE)
            app._photo_submit('capture',np.zeros((120,160,3),dtype=np.uint8));h.settle(app)
            app.on_pause();app.on_resume();app._sandbox_retry();h.settle(app)
            self.assertEqual(app.navigation.page,SANDBOX_CHECKOUT)
            self.assertTrue(f.flow.customer_claim_required);self.assertEqual(app._photo_view,{})
            self.assertEqual(f.provider.charges,1)

    def test_print_failure_keeps_paid_camera_and_never_automatically_resubmits_ticket(self):
        with patch.object(ThermalPrinter,'raster_payload',return_value=b'SYNTHETIC RASTER'):
            sender=Mock(side_effect=OSError('synthetic unknown printer outcome'))
            printer=ThermalPrinter(PrinterConfig(print_width_dots=384),usb_sender=sender)
            h=fixture.SandboxWidgetTests()
            with h.booth(printer=printer) as (app,f):
                f.flow.qr_renewal_enabled=True;h.pending(app)
                f.paid();app._sandbox_retry();h.settle(app)
                self.assertEqual(app.navigation.page,CAPTURE);self.assertEqual(sender.call_count,1)
                self.assertEqual(f.flow.snapshot()['recovery_receipt']['state'],'UNCERTAIN')
                app._sandbox_submit('check');h.settle(app)
                self.assertEqual(sender.call_count,1);self.assertEqual(f.provider.charges,1)

    def test_printed_ticket_restores_private_photo_without_reprinting_receipt(self):
        images=[]
        def encode(image):images.append(image.copy());return b'SYNTHETIC RASTER'
        with patch.object(ThermalPrinter,'raster_payload',side_effect=encode):
            sender=Mock();printer=ThermalPrinter(PrinterConfig(print_width_dots=384),usb_sender=sender)
            h=fixture.SandboxWidgetTests()
            with h.booth(printer=printer) as (app,f):
                f.flow.qr_renewal_enabled=True;h.pending(app)
                f.paid();app._sandbox_retry();h.settle(app)
                self.assertEqual(len(images),1)
                ticket_frame=np.asarray(images[0].convert('RGB'))
                app._photo_submit('capture',np.zeros((120,160,3),dtype=np.uint8));h.settle(app)
                transaction=f.flow.snapshot()['transaction_id']
                app.on_pause();app.on_resume();app._sandbox_retry();h.settle(app)
                # Use the original scanner's bounded primary/alternate route,
                # then actual backend proof, rather than a primary-only decoder.
                app._sandbox_submit('scan_claim',ticket_frame);h.settle(app)
                app._sandbox_resume();h.settle(app)
                self.assertEqual(app.navigation.page,CAPTURE);self.assertEqual(app._photo_view['captured'],1)
                self.assertEqual(f.flow.snapshot()['transaction_id'],transaction)
                self.assertEqual(sender.call_count,1);self.assertEqual(f.provider.charges,1)
