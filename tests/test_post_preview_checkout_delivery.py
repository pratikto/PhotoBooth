"""Synthetic checkout worker integration to verified Drive/print obligations."""
from pathlib import Path
import tempfile
import unittest

import numpy as np
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests.test_post_preview_checkout_worker import PrivateCheckoutWorkerTests


class PrivateCheckoutPaidDeliveryTests(unittest.TestCase):
    final=PrivateCheckoutWorkerTests.final
    freeze=PrivateCheckoutWorkerTests.freeze
    ready=PrivateCheckoutWorkerTests.ready

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture=CheckoutFixture(Path(self.temp.name))
        self.addCleanup(self.fixture.close)
        self.fixture.enable_paid_ticket()
        self.fixture.enable_paid_delivery()
        self.service=self.fixture.service
        self.frame=np.zeros((32,48,3),dtype=np.uint8)

    def payable(self):
        view=self.ready()
        self.fixture.provider.state(view['payment']['attempts'][0]['provider_order_id'],'settlement')
        view=self.service.check_payment('connectivity')
        self.assertEqual('paid_hold',view['phase'])
        return view

    def ticket(self):
        self.payable()
        offered=self.service.prepare_ticket()
        self.service.ticket_visible(offered['ticket_offer'])
        self.service.ticket_send_receipt()
        self.service.ticket_dismiss()

    def test_original_checkout_proceeds_to_saved_photos_qr_and_once_only_print(self):
        self.ticket()
        before=self.fixture.provider.charges
        state=self.service.prepare_paid_delivery()
        self.assertEqual('paid_delivery',state['phase'])
        self.assertEqual('PENDING_UPLOAD',state['delivery']['upload_status'])
        self.assertEqual('OWED',state['delivery']['service_status'])
        self.assertIn('template_a',state['delivery']['print_states'])
        self.assertFalse(state['delivery']['drive_verified'])
        self.assertFalse(state['fulfillment_authorized'])
        printed=self.service.paid_print_next()
        self.assertEqual('SUBMITTED',printed['delivery']['print_states']['template_a'])
        self.assertEqual(1,len(self.fixture.paid_print_sends))
        self.assertEqual(before,self.fixture.provider.charges)
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual('SUBMITTED',self.service.paid_print_next()['delivery']['print_states']['template_a'])
        self.assertEqual(1,len(self.fixture.paid_print_sends))
        self.assertEqual('NOT_CONFIGURED',
            self.fixture.paid_monitor.enqueue(self.service.lease,self.service.group,self.service.templates)['worker'])

    def test_no_paid_ticket_must_not_prepare_or_print(self):
        self.payable()
        with self.assertRaises(DraftHeld):
            self.service.prepare_paid_delivery()
        with self.assertRaises(DraftHeld):
            self.service.paid_print_next()
        self.assertEqual([],self.fixture.paid_print_sends)
        self.assertEqual(0,self.service.ledger.db.execute(
            'SELECT count(*) FROM pp_paid_strip_jobs').fetchone()[0])

    def test_nonexistent_drive_binding_does_not_claim_success_or_output(self):
        self.ticket()
        def dead(_manifest):
            raise OSError('fixture drive down')
        self.fixture.drive.bind_transaction=dead
        with self.assertRaises(DraftHeld):
            self.service.prepare_paid_delivery()
        self.assertEqual('paid_hold',self.service.phase)
        self.assertEqual([],self.fixture.paid_print_sends)
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_untrusted_or_mismatched_printer_lane_cannot_attach(self):
        with self.assertRaises(DraftHeld):
            self.service.attach_paid_delivery(
                self.fixture.paid_monitor,self.fixture.paid_dispatcher,
                printer=None,shared_lane=object())


if __name__=='__main__':
    unittest.main()
