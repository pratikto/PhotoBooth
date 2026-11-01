"""One native receipt send, no raw credential persistence or after-send replay."""
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from PIL import Image
from photobooth.credential_vault import VaultUnavailable
from photobooth.post_preview_ticket_receipt import render_post_preview_receipt
from tests.test_post_preview_ticket import OriginalPaidTicketTests


class TicketReceiptTests(OriginalPaidTicketTests):
    # Do not inherit all historical test methods; use a separate short fixture.
    __test__ = False

    def offered(self):
        self.paid()
        self.ticket.prepare(self.lease)
        offer=self.ticket.private_offer(self.lease)
        self.ticket.mark_visible(self.lease, offer)
        return offer

    def printer(self, *, success=True):
        saved=[]
        def send(bitmap,*,copies):
            saved.append(bitmap)
            self.assertEqual(1,copies)
            self.assertEqual('1',bitmap.mode)
            self.assertEqual(576,bitmap.width)
            return SimpleNamespace(success=success)
        return SimpleNamespace(config=SimpleNamespace(print_width_dots=576),
                               print_bitmap=send),saved

    def test_no_receipt_before_genuinely_visible_and_no_unlocked_send(self):
        self.paid();self.ticket.prepare(self.lease)
        offer=self.ticket.private_offer(self.lease)
        printer,images=self.printer()
        with self.assertRaises(VaultUnavailable):
            self.ticket.send_receipt_once(self.lease,offer,printer,send_lock=threading.Lock())
        self.assertEqual([],images)
        self.assertEqual('PREPARED',self.row()['receipt_state'])

    def test_exact_original_ticket_in_memory_receipt_and_no_second_send(self):
        offer=self.offered()
        printer,images=self.printer()
        result=self.ticket.send_receipt_once(self.lease,offer,printer,send_lock=threading.Lock())
        self.assertEqual('SUBMITTED',result['receipt_state'])
        self.assertEqual('SUBMITTED',self.row()['receipt_state'])
        self.assertEqual(1,len(images))
        self.assertEqual((576, images[0].height),images[0].size)
        with self.assertRaises(VaultUnavailable):
            self.ticket.send_receipt_once(self.lease,offer,printer,send_lock=threading.Lock())
        self.assertEqual(1,len(images))
        for filename in ('drafts.db','drafts.db-wal'):
            path=self.fixture.fixture.root/filename
            if path.exists(): self.assertNotIn(offer.qr_payload.encode(),path.read_bytes())
        self.assertEqual('OWED',self.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()['status'])

    def test_missing_printer_records_not_sent_and_never_retries(self):
        offer=self.offered()
        response=self.ticket.send_receipt_once(self.lease,offer,None)
        self.assertEqual('NOT_SENT',response['receipt_state'])
        printer,images=self.printer()
        with self.assertRaises(VaultUnavailable):
            self.ticket.send_receipt_once(self.lease,offer,printer,send_lock=threading.Lock())
        self.assertEqual([],images)

    def test_no_shared_lane_prevents_send(self):
        offer=self.offered()
        printer,images=self.printer()
        response=self.ticket.send_receipt_once(self.lease,offer,printer)
        self.assertEqual('NOT_SENT',response['receipt_state'])
        self.assertEqual([],images)

    def test_transport_failure_is_uncertain_and_replay_denied(self):
        offer=self.offered()
        printer,images=self.printer(success=False)
        self.assertEqual('UNCERTAIN',self.ticket.send_receipt_once(
            self.lease,offer,printer,send_lock=threading.Lock())['receipt_state'])
        with self.assertRaises(VaultUnavailable):
            self.ticket.send_receipt_once(self.lease,offer,printer,send_lock=threading.Lock())
        self.assertEqual(1,len(images))

    def test_crash_boundary_sending_never_resends_after_restart(self):
        offer=self.offered()
        self.ledger.db.execute("UPDATE pp_ticket_presentations SET receipt_state='SENDING'")
        fresh=self.make_ticket()
        with self.assertRaises(VaultUnavailable):
            fresh.send_receipt_once(self.lease,offer,self.printer()[0],send_lock=threading.Lock())
        self.assertEqual('SENDING',self.row()['receipt_state'])
        self.assertEqual('OWED',self.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()['status'])

    def test_full_original_receipt_does_not_accept_wrong_ticket_role(self):
        offer=self.offered()
        image=render_post_preview_receipt(offer.qr_payload,booth_id='PB001',amount=15000,width=384)
        self.assertIsInstance(image,Image.Image)
        self.assertEqual('1',image.mode)
        with self.assertRaises(ValueError):
            render_post_preview_receipt('MEONG:CCP:1:PB001:x',booth_id='PB001',amount=15000)

# Avoid inheriting the base class's 10 methods as duplicate test cases.
for _name in list(vars(OriginalPaidTicketTests)):
    if _name.startswith('test_'):
        setattr(TicketReceiptTests,_name,None)


if __name__ == '__main__':
    unittest.main()
