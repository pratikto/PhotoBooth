"""Synthetic paid ticket worker sequence; payment/Drive/real printer still OFF."""
from pathlib import Path
import tempfile
import threading
import unittest

import numpy as np
from photobooth.credential_vault import VaultUnavailable
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests.test_post_preview_checkout_worker import PrivateCheckoutWorkerTests


class PrivateTicketCheckoutTests(unittest.TestCase):
    final = PrivateCheckoutWorkerTests.final
    freeze = PrivateCheckoutWorkerTests.freeze
    ready = PrivateCheckoutWorkerTests.ready

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture=CheckoutFixture(Path(self.temp.name))
        self.addCleanup(self.fixture.close)
        self.fixture.enable_paid_ticket()
        self.service=self.fixture.service
        self.frame=np.zeros((32,48,3),dtype=np.uint8)

    def paid(self):
        view=self.ready()
        original=view['payment']['attempts'][0]['provider_order_id']
        self.fixture.provider.state(original,'settlement')
        view=self.service.check_payment('connectivity')
        self.assertEqual('paid_hold',view['phase'])
        return view

    def test_full_paid_ticket_service_one_original_receipt_and_dismissal(self):
        self.paid()
        first=self.service.prepare_ticket()
        self.assertEqual('ticket_offer',first['phase'])
        self.assertIsNotNone(first['ticket_qr'])
        with self.assertRaises(DraftHeld):self.service.ticket_send_receipt()
        self.assertEqual('PREPARED',self.fixture.ticket.ledger.db.execute(
            'SELECT receipt_state FROM pp_ticket_presentations').fetchone()[0])
        self.service.ticket_visible(first['ticket_offer'])
        shown=self.service.ticket_send_receipt()
        self.assertEqual('ticket_visible',shown['phase'])
        self.assertEqual('SUBMITTED',shown['ticket_receipt']['receipt_state'])
        self.assertEqual(1,len(self.fixture.receipt_sizes))
        last=self.service.ticket_dismiss()
        self.assertEqual('paid_hold',last['phase'])
        self.assertTrue(last['ticket_dismissed'])
        self.assertFalse(last['fulfillment_authorized'])
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        with self.assertRaises((DraftHeld,VaultUnavailable)):
            self.service.prepare_ticket()
        with self.assertRaises((DraftHeld,VaultUnavailable)):
            self.service.ticket_send_receipt()
        self.assertEqual(1,len(self.fixture.receipt_sizes))

    def test_paid_ticket_is_different_from_checkout_claim_proof(self):
        self.paid()
        ticket=self.service.prepare_ticket()
        self.assertTrue(ticket['ticket_offer'].qr_payload.startswith('MEONG:RECOVERY:1:'))
        with self.assertRaises((DraftHeld,VaultUnavailable)):
            self.service.ticket_visible(self.service._offer)
        self.assertEqual('NOT_OFFERED',self.service.ledger.db.execute(
            'SELECT screen_state FROM pp_ticket_presentations').fetchone()[0])

    def test_retired_private_owner_cannot_offer_receipt_or_restore_pixels(self):
        self.paid()
        self.service.prepare_ticket()
        self.service.hide_private()
        self.assertEqual({'phase':'hold'},self.service.snapshot())
        with self.assertRaises((DraftHeld,VaultUnavailable)):
            self.service.ticket_send_receipt()
        self.assertEqual(0,len(self.fixture.receipt_sizes))
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_printer_send_does_not_modify_payment_or_draft(self):
        self.paid()
        first=self.service.prepare_ticket()
        self.service.ticket_visible(first['ticket_offer'])
        before=self.fixture.provider.charges
        self.service.ticket_send_receipt()
        self.assertEqual(before,self.fixture.provider.charges)
        self.assertEqual(1,len(self.fixture.receipt_sizes))
        self.assertEqual('ACTIVE',self.service.ledger.db.execute(
            'SELECT lifecycle FROM pp_drafts').fetchone()[0])


if __name__=='__main__': unittest.main()
