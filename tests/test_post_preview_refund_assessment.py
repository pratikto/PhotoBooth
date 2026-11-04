"""Pure PP-06R policy never initiates refund and rejects ambiguous outcomes."""
from dataclasses import replace
import unittest

from photobooth.post_preview_refund_assessment import (
    VerifiedPaidAttempt,OriginalRefundEvidence,assess_refund,assess_proof_loss_from_journal
)


class RefundAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.legit=VerifiedPaidAttempt('a'*32,'sandbox-provider-1','MTEST',15000,True)
        self.e=OriginalRefundEvidence(
            purchase_group_id='f'*32,merchant_id='MTEST',amount_idr=15000,
            original=self.legit,reason='IRRECOVERABLE_MERCHANT_SERVICE',
            service_irrecoverable=True,fulfillment='OWED',
            print_outcome='NONE',drive_outcome='LOCAL_ONLY',
            all_external_workers_fenced=True,financial_integrity_verified=True,
            merchant_refund_feature_verified=True,approved_commercial_policy=True,
            approved_abuse_limit=True)

    def test_eligible_full_is_only_nonbinding_candidate_not_payment(self):
        decision=assess_refund(self.e)
        self.assertEqual('CANDIDATE_FULL_SERVICE_FAILURE',decision.disposition)
        self.assertEqual(('a'*32,),decision.candidates)
        self.assertFalse(decision.can_issue_refund)

    def test_lost_genuinely_offered_proof_never_auto_refunds_alone(self):
        candidate=replace(self.e,reason='PROOF_LOST_ONLY',service_irrecoverable=False)
        decision=assess_refund(candidate)
        self.assertEqual('NO_AUTO_REFUND_PROOF_LOST',decision.disposition)
        self.assertEqual((),decision.candidates)

    def test_temporary_cloud_outage_is_not_irrecoverable(self):
        self.assertEqual('WAIT_RECOVERY',assess_refund(replace(
            self.e,reason='TEMPORARY_SERVICE_OUTAGE',
            service_irrecoverable=False)).disposition)

    def test_lost_proof_cannot_mask_independent_irrecoverable_service_failure(self):
        decision=assess_refund(replace(self.e,reason='PROOF_LOST_ONLY'))
        self.assertEqual('REVIEW_REQUIRED',decision.disposition)
        self.assertEqual((),decision.candidates)
        self.assertFalse(decision.can_issue_refund)

    def test_lost_proof_cannot_mask_distinct_verified_excess_settlement(self):
        extra=VerifiedPaidAttempt('b'*32,'sandbox-provider-2','MTEST',15000,True)
        decision=assess_refund(replace(self.e,reason='PROOF_LOST_ONLY',
            service_irrecoverable=False,excess=(extra,)))
        self.assertEqual('REVIEW_REQUIRED',decision.disposition)
        self.assertEqual((),decision.candidates)
        self.assertFalse(decision.can_issue_refund)

    def test_printer_submission_or_uncertain_physical_paper_blocks_full_refund(self):
        for name in ('SUBMITTED','UNCERTAIN','PHYSICAL_VERIFIED'):
            with self.subTest(name=name):
                decision=assess_refund(replace(self.e,print_outcome=name))
                self.assertEqual('REVIEW_REQUIRED',decision.disposition)

    def test_unfenced_upload_or_verified_files_block_premature_refund(self):
        for state in ('IN_PROGRESS','UNKNOWN','VERIFIED'):
            with self.subTest(state=state):
                self.assertEqual('REVIEW_REQUIRED',assess_refund(
                    replace(self.e,drive_outcome=state)).disposition)
        self.assertEqual('REVIEW_REQUIRED',assess_refund(replace(
            self.e,all_external_workers_fenced=False)).disposition)

    def test_duplicate_verified_charge_only_selects_excess_not_original(self):
        extra=VerifiedPaidAttempt('b'*32,'sandbox-provider-2','MTEST',15000,True)
        decision=assess_refund(replace(
            self.e,reason='EXCESS_SETTLED_ATTEMPTS',excess=(extra,),
            service_irrecoverable=False,fulfillment='COMPLETED'))
        self.assertEqual('CANDIDATE_EXCESS_SETTLEMENT',decision.disposition)
        self.assertEqual(('b'*32,),decision.candidates)
        self.assertNotIn(self.legit.attempt_id,decision.candidates)
        self.assertFalse(decision.can_issue_refund)

    def test_unverified_duplicate_wrong_amount_or_merchant_fails_closed(self):
        for extra in (
            VerifiedPaidAttempt('b'*32,'sandbox-provider-2','OTHER',15000,True),
            VerifiedPaidAttempt('b'*32,'sandbox-provider-2','MTEST',10000,True),
            VerifiedPaidAttempt('b'*32,'sandbox-provider-2','MTEST',15000,False),
            VerifiedPaidAttempt('a'*32,'sandbox-provider-2','MTEST',15000,True),
        ):
            with self.subTest(extra=extra):
                self.assertEqual('REVIEW_REQUIRED',assess_refund(replace(
                    self.e,reason='EXCESS_SETTLED_ATTEMPTS',excess=(extra,))).disposition)

    def test_unverified_original_or_wrong_merchant_does_not_refund(self):
        for x in (
            replace(self.e,original=None),
            replace(self.e,original=replace(self.legit,independently_paid=False)),
            replace(self.e,original=replace(self.legit,merchant_id='WRONG')),
            replace(self.e,financial_integrity_verified=False),
        ):
            with self.subTest(x=x):
                self.assertEqual('REVIEW_REQUIRED',assess_refund(x).disposition)

    def test_merchant_feature_policy_or_abuse_gate_missing_holds(self):
        for field in ('merchant_refund_feature_verified','approved_commercial_policy',
                      'approved_abuse_limit'):
            with self.subTest(field=field):
                self.assertEqual('REVIEW_REQUIRED',assess_refund(
                    replace(self.e,**{field:False})).disposition)

    def test_no_mutable_objects_or_provider_side_effects_exist(self):
        self.assertEqual((),assess_refund(replace(
            self.e,reason='UNKNOWN_OR_DISPUTED')).candidates)
        with self.assertRaises((TypeError,ValueError)):
            assess_refund({'mode':'refund'})
        with self.assertRaises(ValueError):
            VerifiedPaidAttempt('not-an-id','p','MTEST',15000,True)


class ConnectedProofRemedyTests(unittest.TestCase):
    def setUp(self):
        from tests.test_post_preview_ticket import OriginalPaidTicketTests
        self.f = OriginalPaidTicketTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.ledger = self.f.ledger

    def evidence(self):
        row = self.ledger.db.execute('''SELECT f.*,a.provider_ref FROM pp_purchase_finance f
            JOIN pp_payment_attempts a ON a.attempt_id=f.legitimate_paid_attempt''').fetchone()
        return OriginalRefundEvidence(self.f.group, row['merchant_id'], row['amount'],
            VerifiedPaidAttempt(row['legitimate_paid_attempt'], row['provider_ref'],
                row['merchant_id'], row['amount'], True),
            reason='PROOF_LOST_ONLY', financial_integrity_verified=True)

    def assess(self, evidence=None):
        before = self.ledger.db.total_changes
        decision = assess_proof_loss_from_journal(self.ledger, evidence or self.evidence())
        self.assertEqual(before, self.ledger.db.total_changes)
        self.assertFalse(decision.can_issue_refund)
        self.assertEqual((), decision.candidates)
        self.assertEqual('OWED', self.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        return decision.disposition

    def offered_ticket(self, *, dismiss=True):
        self.f.paid()
        self.f.ticket.prepare(self.f.lease)
        offer = self.f.ticket.private_offer(self.f.lease)
        self.f.ticket.mark_visible(self.f.lease, offer)
        if dismiss:
            self.f.ticket.dismiss(self.f.lease, offer)
        return offer

    def test_preexisting_late_paid_without_ever_offered_ccp_preserves_remedy(self):
        pf = self.f.fixture
        pf.fixture.issue()  # Issuance is deliberately never marked visible.
        # Fault/import fixture: an existing external attempt escaped today's
        # pre-create CCP gate. Never erase a real prior offer to simulate this.
        attempt, order = 'a'*32, 'PPSYNTHETICEXISTING'
        with self.ledger.write():
            self.ledger.db.execute('''INSERT INTO pp_purchase_finance
                (purchase_group_id,merchant_id,provider_mode,amount) VALUES(?,'MTEST','mock',10000)''',
                (self.f.group,))
            self.ledger.db.execute('''INSERT INTO pp_payment_attempts
                (attempt_id,purchase_group_id,ordinal,provider_order_id,create_phase)
                VALUES(?,?,1,?,'UNKNOWN')''', (attempt, self.f.group, order))
        pf.provider.create_qris(order, 10000)
        pf.provider.state(order, 'settlement')
        paid = pf.service.reconcile_all(self.f.group, 'PB001', force=True)
        self.assertTrue(paid['paid_verified'])
        self.f.ticket.prepare(self.f.lease)
        self.assertIsNone(pf.fixture.row()['offered_at'])
        self.assertEqual(0, self.ledger.db.execute(
            "SELECT count(*) FROM pp_events WHERE event='CCP_OFFERED'").fetchone()[0])
        self.assertEqual('PAID_OWED_REMEDY', self.assess())
        self.assertEqual(1, pf.provider.charges)
        self.assertEqual(1, len(paid['attempts']))

    def test_submitted_receipt_without_screen_is_remedy_not_customer_loss(self):
        self.f.paid()
        self.f.ticket.prepare(self.f.lease)
        with self.ledger.write():
            for state in ('SENDING', 'SUBMITTED'):
                self.ledger.db.execute('UPDATE pp_ticket_presentations SET receipt_state=?', (state,))
        self.assertEqual('PAID_OWED_REMEDY', self.assess())
        self.assertEqual(('NOT_OFFERED', 'SUBMITTED'), tuple(self.f.row()[k]
            for k in ('screen_state', 'receipt_state')))

    def test_genuine_original_offers_allow_only_narrow_loss_policy(self):
        offer = self.offered_ticket(dismiss=False)
        self.assertEqual('PAID_OWED_REMEDY', self.assess())
        self.f.ticket.dismiss(self.f.lease, offer)
        self.assertEqual('NO_AUTO_REFUND_PROOF_LOST', self.assess())

    def test_offer_timestamp_without_original_event_is_not_genuine_evidence(self):
        self.offered_ticket()
        with self.ledger.write():
            self.ledger.db.execute("DELETE FROM pp_events WHERE event='TICKET_QR_VISIBLE'")
        self.assertEqual('PAID_OWED_REMEDY', self.assess())

    def test_foreign_payment_facts_cannot_use_original_offer_journal(self):
        self.offered_ticket()
        e = self.evidence()
        for wrong in (replace(e, purchase_group_id='0'*32),
                      replace(e, merchant_id='FOREIGN'),
                      replace(e, original=replace(e.original, provider_ref='foreign'))):
            with self.subTest(field=wrong.merchant_id):
                self.assertEqual('REVIEW_REQUIRED', self.assess(wrong))

    def test_independent_service_failure_never_hidden_by_genuine_proof_loss(self):
        self.offered_ticket()
        self.assertEqual('REVIEW_REQUIRED', self.assess(replace(
            self.evidence(), service_irrecoverable=True)))


if __name__ == '__main__':unittest.main()
