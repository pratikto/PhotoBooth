"""Paid receipt QR pixels and original printer transport, no real device."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch
import copy

import cv2
import numpy as np

from photobooth.kiosk_v2.recovery_receipt import render_recovery_receipt, INSTRUCTIONS
from photobooth.printer import ThermalPrinter, PrinterConfig, NetworkSendError


class RecoveryReceiptTests(TestCase):
    ticket='MEONG-RECOVERY-V1:PB001:'+('a'*32)+':'+('b'*43)
    order={'mode':'sandbox','state':'PAID','booth_id':'PB001','checkout_key':'a'*32,'amount':10000}

    def test_native_receipt_qr_decodes_original_capability_at_both_paper_widths(self):
        for width in (384,576):
            with self.subTest(width=width):
                image=render_recovery_receipt(self.ticket,self.order,width)
                self.assertEqual(image.width,width);self.assertEqual(image.mode,'1')
                decoded,*_=cv2.QRCodeDetector().detectAndDecode(np.asarray(image.convert('RGB')))
                self.assertEqual(decoded,self.ticket)
                self.assertIn('Tidak perlu membayar ulang.',INSTRUCTIONS)
                self.assertIn('Pilih SCAN QR TIKET DI KAMERA.',INSTRUCTIONS)

    def test_unpaid_foreign_context_and_invalid_payload_cannot_render_recovery_receipt(self):
        for values in ({'state':'PENDING'},{'state':'EXPIRED'},{'mode':'production'},
                       {'booth_id':'PB002'},{'checkout_key':'c'*32},{'amount':True}):
            order=copy.deepcopy(self.order);order.update(values)
            with self.subTest(values=values),self.assertRaises(ValueError):
                render_recovery_receipt(self.ticket,order)
        with self.assertRaises(ValueError):render_recovery_receipt('not a ticket',self.order)

    def test_memory_bitmap_uses_original_route_without_saving_secret_preview(self):
        with TemporaryDirectory() as directory:
            printer=ThermalPrinter(PrinterConfig(lan_host='192.0.2.1'),network_sender=Mock(),usb_sender=Mock())
            image=render_recovery_receipt(self.ticket,self.order)
            with patch.object(printer,'raster_payload',return_value=b'SYNTHETIC ESC/POS') as encode:
                result=printer.print_bitmap(image)
            self.assertTrue(result.success);encode.assert_called_once_with(image)
            printer._network_sender.assert_called_once_with('192.0.2.1',9100,b'SYNTHETIC ESC/POS')
            printer._usb_sender.assert_not_called();self.assertEqual(list(Path(directory).iterdir()),[])

    def test_partial_memory_bitmap_send_cannot_fallback_or_retry(self):
        network=Mock(side_effect=NetworkSendError('synthetic partial write'));usb=Mock()
        printer=ThermalPrinter(PrinterConfig(lan_host='192.0.2.1'),network_sender=network,usb_sender=usb)
        with patch.object(printer,'raster_payload',return_value=b'SYNTHETIC ESC/POS'):
            result=printer.print_bitmap(render_recovery_receipt(self.ticket,self.order))
        self.assertFalse(result.success);self.assertEqual(network.call_count,1);usb.assert_not_called()

    def test_bitmap_validates_size_and_copy_count_before_transport(self):
        from PIL import Image
        send=Mock();printer=ThermalPrinter(PrinterConfig(print_width_dots=384),usb_sender=send)
        for image in (Image.new('RGB',(384,10)),Image.new('1',(576,10))):
            with self.assertRaises(ValueError):printer.print_bitmap(image)
        with patch.object(printer,'raster_payload',return_value=b'SYNTHETIC ESC/POS'):
            self.assertFalse(printer.print_bitmap(Image.new('1',(384,10)),copies=True).success)
        send.assert_not_called()


class RecoveryReceiptSessionTests(TestCase):
    def setUp(self):
        from tests.qris_v2_fixture import Fixture
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.f=Fixture(Path(self.tmp.name));self.addCleanup(lambda:self.f.close())
        self.f.flow.qr_renewal_enabled=True;self.f.service.begin({'template_a':1})
        self.printer=Mock(config=PrinterConfig(print_width_dots=384))
        self.printer.print_bitmap.return_value=Mock(success=True)
        self.f.service.receipt_printer=self.printer

    def paid(self):
        self.f.paid();self.f.service.check()
        return self.f.flow.customer_ticket()

    def test_paid_receipt_is_submitted_once_and_contains_no_ticket_in_journal(self):
        ticket=self.paid();view=self.f.service.print_recovery_receipt()
        self.assertEqual(view['recovery_receipt']['state'],'SUBMITTED')
        self.assertFalse(view['ticket_required']);self.assertIsNone(view['ticket_qr_rgb'])
        self.assertNotIn(ticket.split(':')[-1],self.f.flow.path.read_text())
        for _ in range(3):self.f.service.print_recovery_receipt()
        self.assertEqual(self.printer.print_bitmap.call_count,1)
        self.assertEqual(self.f.provider.charges,1)

    def test_unpaid_and_privacy_locked_paid_receipts_cannot_print(self):
        with self.assertRaises(RuntimeError):self.f.service.print_recovery_receipt()
        self.paid();self.f.flow.lock_customer()
        with self.assertRaises(RuntimeError):self.f.service.print_recovery_receipt()
        self.printer.print_bitmap.assert_not_called()

    def test_intent_save_failure_never_sends_and_can_retry_before_any_submission(self):
        self.paid()
        with patch.object(self.f.flow,'_save',side_effect=OSError('synthetic journal failure')):
            with self.assertRaises(OSError):self.f.service.print_recovery_receipt()
        self.printer.print_bitmap.assert_not_called()
        self.assertNotIn('recovery_receipt',self.f.flow.snapshot())
        self.f.service.print_recovery_receipt();self.assertEqual(self.printer.print_bitmap.call_count,1)

    def test_partial_or_unknown_send_is_uncertain_without_auto_reprint(self):
        self.paid();self.printer.print_bitmap.side_effect=OSError('synthetic partial send')
        self.assertEqual(self.f.service.print_recovery_receipt()['recovery_receipt']['state'],'UNCERTAIN')
        self.f.service.print_recovery_receipt();self.assertEqual(self.printer.print_bitmap.call_count,1)

    def test_lost_final_journal_ack_keeps_sending_and_never_resubmits(self):
        self.paid();save=self.f.flow._save
        def fail_after_send():
            if (self.f.flow.data.get('recovery_receipt') or {}).get('state')=='SUBMITTED':
                raise OSError('synthetic final save failure')
            save()
        with patch.object(self.f.flow,'_save',side_effect=fail_after_send):
            with self.assertRaises(OSError):self.f.service.print_recovery_receipt()
        self.assertEqual(self.f.flow.snapshot()['recovery_receipt']['state'],'SENDING')
        self.f.service.print_recovery_receipt();self.assertEqual(self.printer.print_bitmap.call_count,1)

    def test_restart_converts_sending_to_uncertain_and_keeps_private_owner_hold(self):
        from tests.qris_v2_fixture import Fixture
        self.paid();self.f.flow.data['recovery_receipt']={'state':'SENDING'};self.f.flow._save()
        self.f.close();self.f=Fixture(Path(self.tmp.name));self.f.flow.qr_renewal_enabled=True
        self.assertEqual(self.f.flow.snapshot()['recovery_receipt']['state'],'UNCERTAIN')
        self.assertTrue(self.f.flow.customer_claim_required);self.assertIsNone(self.f.flow.customer_ticket())
        with self.assertRaises(RuntimeError):self.f.flow.print_recovery_receipt(self.printer)
        self.printer.print_bitmap.assert_not_called()

    def test_transient_prephoto_pause_retains_live_proof_but_allocated_session_cannot_bypass_lock(self):
        self.assertTrue(self.f.flow.live_prephoto)
        self.assertTrue(self.f.flow.pause_live_prephoto())
        self.assertFalse(self.f.flow.customer_claim_required)
        ticket=self.paid();self.assertTrue(ticket)
        self.f.service.print_recovery_receipt()
        self.f.service.prepare()
        # A live allocation is still preparing until its local worker is ready.
        self.assertTrue(self.f.flow.live_prephoto);self.assertTrue(self.f.flow.pause_live_prephoto())
        self.f.flow.bind_transaction(self.f.flow.snapshot()['transaction_id'])
        self.assertFalse(self.f.flow.live_prephoto);self.assertFalse(self.f.flow.pause_live_prephoto())
        self.f.flow.lock_customer();self.assertTrue(self.f.flow.customer_claim_required)
