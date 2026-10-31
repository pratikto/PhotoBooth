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
