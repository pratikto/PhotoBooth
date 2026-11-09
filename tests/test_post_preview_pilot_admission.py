"""MOCK-only user B admission and original A paid proof self-service."""
import threading
from pathlib import Path
import tempfile
import unittest
import numpy as np

from photobooth.catalog import get_templates
from photobooth.post_preview_pilot_admission import OriginalPilotAdmission
from photobooth.post_preview_claim import OriginalMockClaim
from photobooth.post_preview_ccp import OriginalCCPService
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_isolation import OriginalMockIsolation
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests.test_post_preview_checkout_worker import PrivateCheckoutWorkerTests


class PilotAdmissionTests(unittest.TestCase):
    final=PrivateCheckoutWorkerTests.final
    freeze=PrivateCheckoutWorkerTests.freeze
    ready=PrivateCheckoutWorkerTests.ready

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture=CheckoutFixture(Path(self.temp.name))
        self.addCleanup(self.fixture.close)
        self.fixture.enable_paid_ticket()
        self.service=self.fixture.service
        self.frame=np.zeros((32,48,3),dtype=np.uint8)
        self.iso=OriginalMockIsolation(
            self.service.ledger,self.fixture.backend,self.fixture.jobs,
            self.fixture.launch_lease,printer_lane=self.service._receipt_lane,
            allow_incomplete_fixture=True)
        self.claim=OriginalMockClaim(
            self.fixture.backend,
            OriginalCCPService(self.service.ledger,self.fixture.protector,'MTEST',
                               allow_synthetic=True),
            OriginalRecoveryTicketService(self.fixture.backend,self.fixture.protector,
                                          allow_synthetic=True),
            allow_incomplete_fixture=True)
        self.admission=OriginalPilotAdmission(
            self.iso,self.claim,allow_synthetic_pilot=True)

    def paid_private_A(self):
        frozen=self.freeze()
        proof=frozen['ccp_offer'].qr_payload
        self.service.ccp_visible(frozen['ccp_offer'])
        payment=self.service.begin_payment()
        self.fixture.provider.state(payment['payment']['attempts'][0]['provider_order_id'],
                                    'settlement')
        self.service.check_payment('connectivity')
        self.fixture.ticket.prepare(self.service.lease)
        original=self.service.lease
        self.service.retire('APP_SUSPENDED')
        return original,proof,self.service.group

    def test_acked_hand_off_to_B_preserves_original_A_and_rejects_stale_generation(self):
        old,proof,group=self.paid_private_A()
        self.assertTrue(self.admission.ensure_new_visitor_ready())
        new=self.service.start(get_templates(),{'template_a':1})
        self.assertNotEqual(old.draft_id,self.service.lease.draft_id)
        self.assertEqual(1,self.fixture.provider.charges)
        with self.assertRaises(DraftHeld):self.service.ledger.inspect(old)
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services WHERE purchase_group_id=?',(group,)
        ).fetchone()[0])
        self.assertEqual(1,self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_isolation_ops WHERE state='ACKED'").fetchone()[0])

    def test_acked_reply_recovery_cannot_skip_original_collector_fence(self):
        from tests.test_post_preview_isolation import OriginalMockIsolationTests
        old,proof,group=self.paid_private_A()
        operation=self.iso.prepare('PB001')
        self.iso.acknowledge('PB001',operation)
        server,release,_,_=OriginalMockIsolationTests.stalled_collector(self)
        self.iso.readiness=server
        with self.assertRaises(DraftHeld):self.admission.ensure_new_visitor_ready()
        self.assertEqual(old,self.service.lease)
        self.assertTrue(self.service._hidden.is_set())
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services WHERE purchase_group_id=?',(group,)).fetchone()[0])
        release.set();self.assertTrue(server.stop())
        self.assertTrue(self.admission.ensure_new_visitor_ready())
        new=self.service.start(get_templates(),{'template_a':1})
        self.assertNotEqual(old.draft_id,self.service.lease.draft_id)
        self.assertGreater(new['generation'],old.generation)

    def test_original_A_proof_waits_while_B_live(self):
        old,proof,group=self.paid_private_A()
        self.admission.ensure_new_visitor_ready()
        self.service.start(get_templates(),{'template_a':1})
        other=self.service.lease
        result=self.admission.recover_paid(proof)
        self.assertEqual('WAIT',result['state'])
        self.assertEqual(other,self.service.lease)
        self.assertFalse(self.service._hidden.is_set())
        self.assertEqual(1,self.fixture.provider.charges)

    def test_old_original_A_reacquires_safely_from_protected_idle(self):
        old,proof,group=self.paid_private_A()
        claimed=self.admission.recover_paid(proof)
        self.assertEqual('RESTORED',claimed['state'])
        self.assertEqual(old.draft_id,self.service.lease.draft_id)
        self.assertGreater(self.service.lease.generation,old.generation)
        self.assertEqual('OWED',claimed['snapshot']['payment']['obligation_state'])
        self.assertEqual(1,self.fixture.provider.charges)
        self.assertEqual(1,self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_isolation_ops WHERE state='ACKED'").fetchone()[0])
        self.assertEqual(0,self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_payment_attempts WHERE payment_state='UNKNOWN'").fetchone()[0])

    def test_prepared_ack_reply_loss_uses_same_operation_id(self):
        self.service.prepare()
        self.service.start(get_templates(),{'template_a':1})
        old_lease=self.service.lease
        self.service.retire('APP_SUSPENDED')
        original=self.iso.prepare('PB001')
        self.assertTrue(self.admission.ensure_new_visitor_ready())
        recorded=self.service.ledger.db.execute(
            'SELECT operation_id FROM pp_isolation_ops').fetchone()[0]
        self.assertEqual(original,recorded)
        self.assertIsNone(self.service.lease)
        self.assertEqual(old_lease.generation+1,
                         self.service.ledger.db.execute(
                             'SELECT original_generation FROM pp_isolation_ops'
                         ).fetchone()[0])
        self.assertEqual(1,self.service.ledger.db.execute(
            'SELECT count(*) FROM pp_isolation_ops').fetchone()[0])

    def test_pending_provider_and_live_customer_never_released(self):
        view=self.ready()
        self.service.retire('APP_SUSPENDED')
        with self.assertRaises(DraftHeld):self.admission.ensure_new_visitor_ready()
        self.assertEqual(0,self.service.ledger.db.execute(
            'SELECT closed FROM pp_drafts').fetchone()[0])

    def test_foreign_ticket_role_cannot_create_entitlement_or_release(self):
        old,proof,group=self.paid_private_A()
        for token in ('MEONG:PAYMENT:1:PB001:abc', 'bad'):
            with self.assertRaises(PermissionError):
                self.admission.recover_paid(token)
        self.assertEqual(0,self.service.ledger.db.execute(
            'SELECT closed FROM pp_drafts').fetchone()[0])


if __name__=='__main__':unittest.main()
