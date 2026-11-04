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

    def paid(self, proof_kind='CCP'):
        frozen=self.freeze()
        proof=frozen['ccp_offer'].qr_payload
        self.service.ccp_visible(frozen['ccp_offer'])
        v=self.service.begin_payment()
        self.fixture.provider.state(v['payment']['attempts'][0]['provider_order_id'],'settlement')
        self.service.check_payment('connectivity')
        self.fixture.ticket.prepare(self.service.lease)
        if proof_kind=='RECOVERY':
            proof=self.fixture.ticket.private_offer(self.service.lease).qr_payload
        group=self.service.group
        self.service.retire('APP_SUSPENDED')
        operation=self.iso.prepare('PB001')
        self.iso.acknowledge('PB001',operation)
        return group,proof

    def assert_proof_change_during_provider_check_is_denied(self, kind, change):
        group,proof=self.paid(kind)
        ledger=self.service.ledger
        table={'CCP':'pp_ccp_credentials','RECOVERY':'pp_ticket_credentials'}[kind]
        original=dict(ledger.db.execute('SELECT * FROM pp_drafts').fetchone())
        entitlement=ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0]
        expiry=ledger.db.execute(f'SELECT expires_at FROM {table}').fetchone()[0]
        clock=[expiry-1]
        ledger.now=lambda:clock[0]
        get_status=self.fixture.provider.get_status
        reads=[]

        def changing_status(order_id):
            response=get_status(order_id)
            reads.append(order_id)
            # The last independent settlement GET races the proof's lifetime.
            # Both responses remain fresh; no lease timeout can mask this bug.
            if len(reads)==2:
                if change=='expiry':
                    clock[0]=expiry
                else:
                    with ledger.write():
                        ledger.db.execute(f'UPDATE {table} SET revoked=1 WHERE purchase_group_id=?',(group,))
            return response

        self.fixture.provider.get_status=changing_status
        with self.assertRaises(PermissionError):
            self.claim.claim(group,'PB001',proof)
        self.assertEqual(2,len(reads))
        current=ledger.db.execute('SELECT * FROM pp_drafts').fetchone()
        self.assertEqual((1,'ISOLATED',original['generation']),
                         (current['closed'],current['lifecycle'],current['generation']))
        self.assertEqual(entitlement,ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0])
        self.assertEqual('OWED',ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual(1,self.fixture.provider.charges)
        self.assertEqual([],self.fixture.receipt_sizes)
        self.assertEqual(0,ledger.db.execute("SELECT count(*) FROM pp_events WHERE event='ORIGINAL_PAID_CLAIM_REACQUIRED'").fetchone()[0])

    def test_ccp_expiring_during_final_settlement_check_cannot_reacquire(self):
        self.assert_proof_change_during_provider_check_is_denied('CCP','expiry')

    def test_ccp_revoked_during_final_settlement_check_cannot_reacquire(self):
        self.assert_proof_change_during_provider_check_is_denied('CCP','revocation')

    def test_ticket_expiring_during_final_settlement_check_cannot_reacquire(self):
        self.assert_proof_change_during_provider_check_is_denied('RECOVERY','expiry')

    def test_ticket_revoked_during_final_settlement_check_cannot_reacquire(self):
        self.assert_proof_change_during_provider_check_is_denied('RECOVERY','revocation')

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
        # One transient HTTP loss is recoverable by the following fresh GET.
        # A continuous provider outage must never be interpreted as fresh PAID.
        self.fixture.provider.outage=True
        with self.assertRaises(Exception):
            self.claim.claim(group,'PB001',proof)
        self.assertEqual(1,self.service.ledger.db.execute(
            'SELECT closed FROM pp_drafts').fetchone()[0])


    def test_claimed_paid_media_rehydrates_original_worker_without_recapture(self):
        from photobooth.kiosk_v2.post_preview_checkout import PrivateCheckoutService
        from photobooth.post_preview_ticket import OriginalRecoveryTicketService
        group,proof=self.paid()
        valid=self.claim.claim(group,'PB001',proof)
        self.assertEqual('REACQUIRED',valid['state'])
        root=self.service.root
        fresh=PrivateCheckoutService(
            root,payment_client=self.fixture.client,protector=self.fixture.protector,
            merchant_id='MTEST',readiness=lambda:self.fixture.ready,
            qr_loader=lambda _:None,allow_incomplete_fixture=True,
            trusted_ledger=self.service.ledger)
        self.addCleanup(fresh.close)
        fresh.attach_paid_ticket(
            OriginalRecoveryTicketService(self.fixture.backend,self.fixture.protector,
                                          allow_synthetic=True),
            printer=None,shared_lane=threading.Lock())
        restored=fresh.recover_original_owed(valid['lease'],group)
        self.assertEqual('paid_hold',restored['phase'])
        self.assertEqual('OWED',restored['payment']['obligation_state'])
        self.assertFalse(restored['ticket_dismissed'])
        self.assertEqual(1,self.fixture.provider.charges)
        first=fresh.prepare_ticket()
        self.assertEqual('ticket_offer',first['phase'])
        with self.assertRaises(DraftHeld):
            fresh.recover_original_owed(valid['lease'],group)

    def test_wrong_directory_cannot_inject_foreign_trusted_ledger(self):
        from photobooth.kiosk_v2.post_preview_checkout import PrivateCheckoutService
        with self.assertRaises(DraftHeld):
            PrivateCheckoutService(
                Path(self.tmp.name)/'other',
                payment_client=self.fixture.client,protector=self.fixture.protector,
                merchant_id='MTEST',readiness=lambda:self.fixture.ready,
                qr_loader=lambda _:None,allow_incomplete_fixture=True,
                trusted_ledger=self.service.ledger)


if __name__=='__main__':unittest.main()
