"""Pure PP-06R policy never initiates refund and rejects ambiguous outcomes."""
from dataclasses import replace
import unittest

from photobooth.post_preview_refund_assessment import (
    VerifiedPaidAttempt,OriginalRefundEvidence,assess_refund
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


if __name__ == '__main__':unittest.main()
