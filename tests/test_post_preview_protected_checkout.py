"""Original protected native facade against actual API/fixed provider core."""
import hashlib
import threading
import unittest
from unittest.mock import patch

from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_client import PostPreviewClient
from photobooth.kiosk_v2.post_preview_protected_checkout import ProtectedCheckoutService
from tests.post_preview_protected_fixture import ProtectedNativeHarness


class ProtectedCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.f = ProtectedNativeHarness(self)
        self.service = self.f.service

    def test_same_frozen_photos_paid_ticket_original_folder_and_batches_over_http(self):
        before = hashlib.sha256(self.f.intent['contract_json'].encode()).hexdigest()
        self.f.ticket()
        view = self.service.prepare_paid_delivery()
        self.assertEqual({'template_a':'PREPARED','template_b':'PREPARED'},view['delivery']['print_states'])
        self.assertFalse(view['delivery']['drive_verified'])
        self.assertEqual('OWED',view['delivery']['service_status'])
        for _ in range(3):view = self.service.paid_print_next()
        self.assertTrue(view['delivery']['print_all_submitted'])
        self.assertFalse(view['delivery']['physical_paper_verified'])
        self.assertEqual(3,len(self.f.sends))
        self.assertEqual(1,self.f.remote.charges)
        self.assertEqual(1,len(self.f.binds))
        self.assertEqual(before,hashlib.sha256(self.f.ledger.db.execute(
            'SELECT contract_json FROM pp_checkout_intents').fetchone()[0].encode()).hexdigest())
        self.assertEqual([2,1],[r[0] for r in self.f.ledger.db.execute(
            'SELECT copies FROM pp_paid_strip_jobs ORDER BY template_id')])
        self.assertFalse(view['fulfillment_authorized'])
        self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_unpaid_and_undismissed_ticket_cannot_allocate_folder(self):
        self.f.proof()
        with self.assertRaises(DraftHeld):self.service.prepare_paid_delivery()
        self.assertEqual([],self.f.binds)
        self.assertEqual([],self.f.sends)
        with self.assertRaises(DraftHeld):self.service.prepare_ticket()

    def test_original_receipt_uncertainty_holds_delivery_without_replay(self):
        self.f.paid();view=self.service.prepare_ticket()
        self.service.ticket_visible(view['ticket_offer'])
        self.f.uncertain=True
        self.assertEqual('UNCERTAIN',self.service.ticket_send_receipt()['ticket_receipt']['receipt_state'])
        self.service.ticket_dismiss()
        with self.assertRaises(DraftHeld):self.service.prepare_paid_delivery()
        self.assertEqual(1,len(self.f.sends));self.assertEqual([],self.f.binds)

    def test_partial_photo_holds_all_following_batches_and_never_replays(self):
        self.f.ticket();self.service.prepare_paid_delivery();self.f.uncertain=True
        view=self.service.paid_print_next()
        self.assertTrue(view['delivery']['needs_operator_review'])
        for _ in range(2):
            with self.assertRaises(DraftHeld):self.service.paid_print_next()
        self.assertEqual(2,len(self.f.sends))
        self.assertEqual('PREPARED',view['delivery']['print_states']['template_b'])

    def test_lost_bind_reply_retries_same_original_purchase(self):
        self.f.ticket();self.f.lost_bind=True
        with self.assertRaises(DraftHeld):self.service.prepare_paid_delivery()
        self.assertEqual('paid_hold',self.service.phase)
        view=self.service.prepare_paid_delivery()
        self.assertEqual([view['delivery']['transaction_id']]*2,self.f.binds)
        self.assertEqual(1,self.f.remote.charges)

    def test_late_delivery_reply_cannot_restore_private_snapshot_after_hide(self):
        self.f.ticket();self.service.prepare_paid_delivery()
        original=self.service._delivery.inspect
        def late(*args):
            result=original(*args);self.service.hide_private();return result
        with patch.object(self.service._delivery,'inspect',side_effect=late):
            with self.assertRaises(DraftHeld):self.service.paid_delivery_status()
        self.assertEqual({'phase':'hold'},self.service.snapshot())
        self.assertIsNone(self.service._delivery_state)
        self.assertIsNone(self.service._ticket_offer)
        self.assertIsNone(self.service._payment)

    def test_wrong_mode_and_reopened_root_do_not_authorize_original_takeover(self):
        mock=PostPreviewClient('https://fixture.invalid','PB001','x'*48,expected_mode='mock')
        self.addCleanup(mock.close)
        with self.assertRaises(DraftHeld):
            ProtectedCheckoutService(self.f.root,payment_client=mock,qr_loader=lambda _:None)
        reopened=ProtectedCheckoutService(self.f.root,payment_client=self.f.client,qr_loader=lambda _:None)
        self.addCleanup(reopened.ledger.close)
        with self.assertRaises(DraftHeld):reopened.accept_frozen_checkout(self.f.group)
        self.assertEqual('hold',reopened.prepare()['phase'])
        self.assertEqual(0,self.f.remote.charges)

    def test_no_new_visitor_after_result_timeout_and_original_rights_survive(self):
        self.f.ticket();self.service.prepare_paid_delivery()
        before=self.f.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0]
        self.service.retire('RESULT_TIMEOUT')
        with self.assertRaises(DraftHeld):self.service.start(self.f.templates,{'template_a':1})
        self.assertEqual(0,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual(before,self.f.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0])
        self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual(0,self.f.remote.cancels)

    def test_hide_does_not_wait_for_original_receipt_http_and_no_late_private_result(self):
        self.f.paid();view=self.service.prepare_ticket()
        self.service.ticket_visible(view['ticket_offer'])
        self.f.receipt_entered=threading.Event();self.f.receipt_release=threading.Event()
        errors=[]
        def send():
            try:self.service.ticket_send_receipt()
            except DraftHeld:errors.append('held')
        thread=threading.Thread(target=send);thread.start()
        try:
            self.assertTrue(self.f.receipt_entered.wait(3))
            self.service.hide_private()
            self.assertEqual({'phase':'hold'},self.service.snapshot())
            self.assertTrue(thread.is_alive())
        finally:self.f.receipt_release.set();thread.join(5)
        self.assertFalse(thread.is_alive());self.assertEqual(['held'],errors)
        self.assertIsNone(self.service._ticket_receipt)


if __name__=='__main__':unittest.main()
