"""Synthetic paid ticket worker sequence; payment/Drive/real printer still OFF."""
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

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
        if view['phase'] == 'payment_hold' and view['payment'] is None:
            # This positive privacy fixture may encounter the real two-second
            # readiness fence on a loaded host. Retry only a proven UNSENT
            # setup, through the original service's fresh checks, once.
            self.assertEqual(0, self.fixture.provider.charges)
            before = self.service.ledger.db.execute(
                'SELECT attempt_id,create_phase FROM pp_payment_attempts').fetchall()
            self.assertTrue(all(row['create_phase'] == 'PREPARED' for row in before))
            view = self.service.begin_payment()
            if before:
                self.assertEqual([row['attempt_id'] for row in before], [row[0] for row in
                    self.service.ledger.db.execute('SELECT attempt_id FROM pp_payment_attempts')])
        self.assertEqual('payment_pending', view['phase'])
        self.assertIsNotNone(view['payment'])
        self.assertEqual(1, self.fixture.provider.charges)
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

    def test_paid_setup_reobserves_expired_readiness_without_replacing_unsent_attempt(self):
        clock = [1000.0]
        self.service.ledger.now = lambda: clock[0]
        prepare = self.fixture.backend._prepare
        attempts = []
        def delayed_once(*args, **kwargs):
            result = prepare(*args, **kwargs)
            attempts.append(result[1]['attempt_id'])
            if len(attempts) == 1:
                clock[0] += 3  # Existing two-second guard must HOLD before POST.
            else:
                self.assertEqual(0, self.fixture.provider.charges)
                self.assertEqual('PREPARED', self.service.ledger.db.execute(
                    'SELECT create_phase FROM pp_payment_attempts').fetchone()[0])
            return result
        with patch.object(self.fixture.backend, '_prepare', side_effect=delayed_once):
            self.paid()
        self.assertEqual(2, len(attempts))
        self.assertEqual(attempts[0], attempts[1])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(1, self.service.ledger.db.execute(
            'SELECT count(*) FROM pp_payment_attempts').fetchone()[0])


if __name__=='__main__': unittest.main()
