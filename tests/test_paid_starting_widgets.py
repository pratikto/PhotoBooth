"""Original native paid admission with unavailable printer and lost allocation ACK."""
from unittest import TestCase
from unittest.mock import Mock,patch
from pathlib import Path
from tempfile import TemporaryDirectory
import os
from kivy.core.window import Window
from photobooth.kiosk_v2.flow import CAPTURE,SANDBOX_CHECKOUT
from photobooth.printer import ThermalPrinter,PrinterConfig
import tests.test_kiosk_v2_sandbox_widgets as fixture

class PaidStartingTests(TestCase):
    def test_missing_physical_printer_still_enters_original_camera_with_configured_photo_worker(self):
        from photobooth.kiosk_v2.photos import configured_test
        original=Window.size
        try:
            for size in [(800,1280),(452,900)]:
                with self.subTest(size=size),TemporaryDirectory() as temporary:
                    Window.size=size;root=Path(temporary)
                    sender=Mock(side_effect=OSError('Synthetic unavailable printer'))
                    printer=ThermalPrinter(PrinterConfig(print_width_dots=384),usb_sender=sender)
                    h=fixture.SandboxWidgetTests()
                    with h.booth(printer=printer) as (app,f),patch.dict(os.environ,{
                            'PHOTOBOOTH_V2_SANDBOX_PRINT':'1','PHOTOBOOTH_V2_PRINT':'1',
                            'PHOTOBOOTH_V2_DRIVE':'0','PHOTOBOOTH_V2_STORAGE':'1'}):
                        def configured(photo_root,**kwargs):
                            with patch('photobooth.printer.ThermalPrinter',return_value=printer):
                                return configured_test(photo_root,configuration_root=root,storage_layout=1)
                        with patch('photobooth.kiosk_v2.photos.configured_test',side_effect=configured):
                            f.flow.qr_renewal_enabled=True;h.pending(app);f.paid();app._sandbox_retry();h.settle(app)
                        self.assertEqual(app.navigation.page,CAPTURE)
                        self.assertEqual(f.flow.snapshot()['recovery_receipt']['state'],'UNCERTAIN')
                        self.assertEqual(sender.call_count,1);self.assertEqual(f.provider.charges,1)
                        self.assertEqual(app._photo_view['captured'],0)
        finally:Window.size=original

    def test_live_allocation_reply_failure_then_check_enters_same_camera_without_recharge_or_reprint(self):
        original_size=Window.size
        try:
            for size in [(800,1280),(452,900)]:
                Window.size=size
                for stage in ['before','after']:
                    with self.subTest(stage=stage):
                        sender=Mock(side_effect=OSError('Synthetic unavailable printer'))
                        printer=ThermalPrinter(PrinterConfig(print_width_dots=384),usb_sender=sender)
                        h=fixture.SandboxWidgetTests()
                        with h.booth(printer=printer) as (app,f):
                            f.flow.qr_renewal_enabled=True;h.pending(app);f.paid()
                            allocate=f.flow.client.allocate;operations=[]
                            def interrupted(oid,grant,operation):
                                operations.append((oid,grant,operation))
                                if len(operations)==1:
                                    if stage=='after':allocate(oid,grant,operation)
                                    raise RuntimeError('Synthetic lost allocation reply')
                                return allocate(oid,grant,operation)
                            with patch.object(f.flow.client,'allocate',side_effect=interrupted):
                                app._sandbox_retry();h.settle(app)
                                self.assertEqual(f.flow.snapshot()['phase'],'STARTING')
                                original=f.flow.snapshot();app._sandbox_retry();h.settle(app)
                                self.assertEqual(app.navigation.page,CAPTURE)
                            self.assertEqual(len(operations),2);self.assertEqual(operations[0],operations[1])
                            self.assertEqual(f.provider.charges,1);self.assertEqual(sender.call_count,1)
                            self.assertEqual(f.flow.snapshot()['order']['order_id'],original['order']['order_id'])
                            self.assertEqual(app._photo_view['captured'],0)
                            self.assertEqual(f.store.db.execute('SELECT count(*) FROM checkout_fulfillments').fetchone()[0],1)
                            self.assertEqual(f.store.fulfillment(original['order']['order_id'],'PB001')['obligation_state'],'OWED')
        finally:Window.size=original_size

    def test_slow_original_admission_survives_idle_and_pause_without_customer_ticket_at_both_sizes(self):
        import threading,time
        from kivy.base import EventLoop
        previous=Window.size
        try:
            for size in [(800,1280),(452,900)]:
                with self.subTest(size=size):
                    Window.size=size;entered,release=threading.Event(),threading.Event()
                    sender=Mock(side_effect=OSError('Synthetic unavailable printer'))
                    printer=ThermalPrinter(PrinterConfig(print_width_dots=384),usb_sender=sender)
                    h=fixture.SandboxWidgetTests()
                    with h.booth(printer=printer) as (app,f):
                        f.flow.qr_renewal_enabled=True;h.pending(app);f.paid()
                        original=f.flow.client.allocate
                        def delayed(*args):
                            entered.set()
                            if not release.wait(8):raise RuntimeError('Synthetic allocation wait expired')
                            return original(*args)
                        with patch.object(f.flow.client,'allocate',side_effect=delayed):
                            try:
                                app._sandbox_retry();deadline=time.monotonic()+5
                                while not entered.is_set() and time.monotonic()<deadline:
                                    app._poll_photos();app._poll_sandbox();EventLoop.idle()
                                self.assertTrue(entered.is_set())
                                self.assertEqual(f.flow.snapshot()['phase'],'STARTING')
                                app._last_activity=time.monotonic()-120;app._tick(0)
                                self.assertFalse(f.flow.customer_claim_required)
                                app.on_pause();app.on_resume()
                                self.assertFalse(f.flow.customer_claim_required)
                            finally:release.set()
                            h.settle(app);app._sandbox_retry();h.settle(app)
                        self.assertEqual(app.navigation.page,CAPTURE)
                        self.assertEqual(app._photo_view['captured'],0)
                        self.assertEqual(f.provider.charges,1);self.assertEqual(sender.call_count,1)
        finally:Window.size=previous
