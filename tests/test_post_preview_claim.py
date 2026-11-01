"""Original CCP claim does not preempt another visitor or permit double print."""
import threading
from pathlib import Path
import tempfile
import unittest
import numpy as np

from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_ccp import OriginalCCPService
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_claim import OriginalMockClaim
from photobooth.post_preview_isolation import OriginalMockIsolation
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests.test_post_preview_checkout_worker import PrivateCheckoutWorkerTests


class OriginalMockClaimTests(unittest.TestCase):
    final=PrivateCheckoutWorkerTests.final
    freeze=PrivateCheckoutWorkerTests.freeze
    ready=PrivateCheckoutWorkerTests.ready

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture=CheckoutFixture(Path(self.tmp.name))
        self.addCleanup(self.fixture.close)
        self.fixture.enable_paid_ticket()
        self.service=self.fixture.service
        self.frame=np.zeros((32,48,3),dtype=np.uint8)
        self.iso=OriginalMockIsolation(
            self.service.ledger,self.fixture.backend,self.fixture.jobs,self.fixture.launch_lease,
            printer_lane=self.service._receipt_lane,allow_incomplete_fixture=True)
        self.claim=OriginalMockClaim(
            self.fixture.backend,
            OriginalCCPService(self.service.ledger,self.fixture.protector,'MTEST',allow_synthetic=True),
            OriginalRecoveryTicketService(self.fixture.backend,self.fixture.protector,allow_synthetic=True),
            allow_incomplete_fixture=True)

    def paid(self):
        frozen=self.freeze()
        proof=frozen['ccp_offer'].qr_payload
        self.service.ccp_visible(frozen['ccp_offer'])
        v=self.service.begin_payment()
        self.fixture.provider.state(v['attempts'][0]['provider_order_id'],'settlement')
        self.service.check_payment('connectivity')
        self.fixture.ticket.prepare(self.service.lease)
        group=self.service.group
        self.service.retire('APP_SUSPENDED')
        operation=self.iso.prepare('PB001')
        self.iso.acknowledge('PB001',operation)
        return group,proof

    def test_returning_proof_reacquires_original_paid_entitlement_once(self):
        group,proof=self.paid()
        receipt=self.claim.claim(group,'PB001',proof)
        self.assertEqual('REACQUIRED',receipt['state'])
        self.assertTrue(receipt['service_still_owed'])
        self.assertEqual(self.service.lease.draft_id,receipt['lease'].draft_id)
        self.assertGreater(receipt['lease'].generation,self.service.lease.generation)
        self.assertEqual(1,self.fixture.provider.charges)
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        again=self.claim.claim(group,'PB001',proof)
        self.assertEqual('WAIT',again['state'])

    def test_busy_booth_keeps_original_proof_private_and_never_preempts_B(self):
        group,proof=self.paid()
        other=self.service.ledger.create('PB001','visitorB',{'template_a':1})
        waiting=self.claim.claim(group,'PB001',proof)
        self.assertEqual('WAIT',waiting['state'])
        row=self.service.ledger.db.execute('SELECT draft_id FROM pp_drafts WHERE closed=0').fetchone()
        self.assertEqual(other.draft_id,row['draft_id'])
        self.assertEqual(1,self.fixture.provider.charges)

    def test_cross_role_qr_and_wrong_booth_denied_without_releasing_anyone(self):
        group,proof=self.paid()
        for text in ('MEONG:DEMO:1:PB001:abc','MEONG:PAYMENT:1:PB001:abc','bad'):
            with self.assertRaises(PermissionError):self.claim.claim(group,'PB001',text)
        with self.assertRaises(PermissionError):self.claim.claim(group,'PB002',proof)
        self.assertEqual(1,self.service.ledger.db.execute(
            'SELECT closed FROM pp_drafts').fetchone()[0])

    def test_unknown_reconciled_provider_cannot_claim_original_media(self):
        group,proof=self.paid()
        self.fixture.session.lose_response=True
        with self.assertRaises(Exception):
            self.claim.claim(group,'PB001',proof)
        self.assertEqual(1,self.service.ledger.db.execute(
            'SELECT closed FROM pp_drafts').fetchone()[0])


if __name__=='__main__':unittest.main()
