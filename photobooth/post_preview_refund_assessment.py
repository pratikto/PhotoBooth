"""No-I/O owner-approved PP-06R REFUND CANDIDATE classifier.

This is a **pure policy proposal**. It has no provider client, API endpoint,
refund request key, journal mutation, or merchant authorization. Never call a
real refund from a candidate. Financial authority must separately verify the
source transaction, persist a durable idempotent refund intent and confirm
merchant-specific feature activation before any future outbound provider I/O.
"""
from dataclasses import dataclass
import re


REFUND_REASONS=frozenset({
    'PROOF_LOST_ONLY','TEMPORARY_SERVICE_OUTAGE',
    'IRRECOVERABLE_MERCHANT_SERVICE','EXCESS_SETTLED_ATTEMPTS',
    'UNKNOWN_OR_DISPUTED'
})
OUTPUT_STATES=frozenset({'NONE','PREPARED','SUBMITTED','UNCERTAIN','PHYSICAL_VERIFIED'})
UPLOAD_STATES=frozenset({'NONE','LOCAL_ONLY','IN_PROGRESS','UNKNOWN','VERIFIED'})
FULFILLMENT_STATES=frozenset({'OWED','COMPLETED','REVIEW'})


@dataclass(frozen=True)
class VerifiedPaidAttempt:
    attempt_id: str
    provider_ref: str
    merchant_id: str
    amount_idr: int
    independently_paid: bool

    def __post_init__(self):
        if (not isinstance(self.attempt_id,str)
                or not re.fullmatch(r'[a-f0-9]{32}',self.attempt_id)
                or not isinstance(self.provider_ref,str)
                or not 1 <= len(self.provider_ref) <= 160
                or not isinstance(self.merchant_id,str)
                or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',self.merchant_id)
                or type(self.amount_idr) is not int or self.amount_idr <= 0
                or type(self.independently_paid) is not bool):
            raise ValueError('Exact original provider attempt evidence required')


@dataclass(frozen=True)
class OriginalRefundEvidence:
    purchase_group_id: str
    merchant_id: str
    amount_idr: int
    original: VerifiedPaidAttempt | None
    excess: tuple[VerifiedPaidAttempt, ...] = ()
    reason: str = 'UNKNOWN_OR_DISPUTED'
    fulfillment: str = 'OWED'
    print_outcome: str = 'NONE'
    drive_outcome: str = 'NONE'
    all_external_workers_fenced: bool = False
    service_irrecoverable: bool = False
    financial_integrity_verified: bool = False
    merchant_refund_feature_verified: bool = False
    approved_commercial_policy: bool = False
    approved_abuse_limit: bool = False

    def __post_init__(self):
        if (not isinstance(self.purchase_group_id,str)
                or not re.fullmatch(r'[a-f0-9]{32}',self.purchase_group_id)
                or not isinstance(self.merchant_id,str)
                or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',self.merchant_id)
                or type(self.amount_idr) is not int or self.amount_idr <= 0
                or (self.original is not None and type(self.original) is not VerifiedPaidAttempt)
                or type(self.excess) is not tuple
                or len(self.excess)>3 or any(type(x) is not VerifiedPaidAttempt for x in self.excess)
                or self.reason not in REFUND_REASONS
                or self.fulfillment not in FULFILLMENT_STATES
                or self.print_outcome not in OUTPUT_STATES
                or self.drive_outcome not in UPLOAD_STATES
                or any(type(v) is not bool for v in (
                    self.all_external_workers_fenced,self.service_irrecoverable,
                    self.financial_integrity_verified,self.merchant_refund_feature_verified,
                    self.approved_commercial_policy,self.approved_abuse_limit))):
            raise ValueError('Complete immutable refund evaluation facts required')


@dataclass(frozen=True)
class RefundAssessment:
    disposition: str
    candidates: tuple[str, ...]
    can_issue_refund: bool = False


def assess_refund(evidence):
    """Return nonbinding, never-executable candidate IDs and a hold/review label.

    Even a candidate does NOT permit an API request: source-side identity,
    refund-key durability, exact provider status/eligibility, customer policy
    and bank settlement must be established independently by later code.
    """
    if type(evidence) is not OriginalRefundEvidence:
        raise TypeError('Only exact original refund evidence may be assessed')
    e=evidence
    source=e.original
    if (not e.financial_integrity_verified or source is None
            or not source.independently_paid
            or source.merchant_id!=e.merchant_id
            or source.amount_idr!=e.amount_idr):
        return RefundAssessment('REVIEW_REQUIRED',())
    known={source.attempt_id}
    references={source.provider_ref}
    for extra in e.excess:
        if (not extra.independently_paid or extra.merchant_id!=e.merchant_id
                or extra.amount_idr!=e.amount_idr or extra.attempt_id in known
                or extra.provider_ref in references):
            return RefundAssessment('REVIEW_REQUIRED',())
        known.add(extra.attempt_id)
        references.add(extra.provider_ref)
    if e.fulfillment=='REVIEW':
        return RefundAssessment('REVIEW_REQUIRED',())
    if e.reason=='PROOF_LOST_ONLY':
        return RefundAssessment('NO_AUTO_REFUND_PROOF_LOST',())
    if e.reason=='TEMPORARY_SERVICE_OUTAGE':
        return RefundAssessment('WAIT_RECOVERY',())
    if e.reason=='UNKNOWN_OR_DISPUTED':
        return RefundAssessment('REVIEW_REQUIRED',())
    if not all((e.merchant_refund_feature_verified,e.approved_commercial_policy,
                e.approved_abuse_limit)):
        return RefundAssessment('REVIEW_REQUIRED',())
    if e.reason=='EXCESS_SETTLED_ATTEMPTS':
        if not e.excess:
            return RefundAssessment('REVIEW_REQUIRED',())
        # Preserve original service obligation and the original single order;
        # never refund the rightful original settled payment here.
        return RefundAssessment('CANDIDATE_EXCESS_SETTLEMENT',
                                tuple(x.attempt_id for x in e.excess))
    if e.reason=='IRRECOVERABLE_MERCHANT_SERVICE':
        if (not e.service_irrecoverable or not e.all_external_workers_fenced
                or e.fulfillment!='OWED' or e.excess
                or e.print_outcome not in {'NONE','PREPARED'}
                or e.drive_outcome not in {'NONE','LOCAL_ONLY'}):
            return RefundAssessment('REVIEW_REQUIRED',())
        return RefundAssessment('CANDIDATE_FULL_SERVICE_FAILURE',(source.attempt_id,))
    return RefundAssessment('REVIEW_REQUIRED',())
