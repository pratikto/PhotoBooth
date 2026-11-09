"""Proof-gated return of original PAID/OWED into a genuinely FREE mock booth.

Only the original CCP or PAID Recovery Ticket type may identify a returning
customer. Proof verification alone NEVER authorizes photos or releases
another visitor's occupancy. Provider settlement must be freshly rechecked.
The optional exact Windows DPAPI mock profile changes credential protection
only. No real Midtrans/Sandbox or camera restart is activated here.
"""
from photobooth.post_preview_ccp import OriginalCCPService
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_store import DraftHeld,DraftLease,PostPreviewStore
from photobooth.credential_vault import mock_protector_allowed


class OriginalMockClaim:
    def __init__(self, payments, ccp, ticket, *, allow_incomplete_fixture=False,
                 allow_windows_protected_mock=False):
        if (allow_incomplete_fixture is not True
                or not isinstance(payments,PostPreviewPayments) or payments.mode!='mock'
                or not isinstance(ccp,OriginalCCPService)
                or not isinstance(ticket,OriginalRecoveryTicketService)
                or ccp.ledger is not payments.ledger or ticket.ledger is not payments.ledger
                or ccp.merchant_id!=payments.merchant_id
                or ticket.merchant_id!=payments.merchant_id
                or not mock_protector_allowed(ccp.protector,
                    windows_protected=allow_windows_protected_mock)
                or not mock_protector_allowed(ticket.protector,
                    windows_protected=allow_windows_protected_mock)):
            raise DraftHeld('Exact original mock claim verifiers required')
        self.payments,self.ccp,self.ticket=payments,ccp,ticket
        self.ledger=payments.ledger

    def _busy_after_proof(self, purchase_group_id, booth_id, payload, proof, verifier):
        return False  # Preserve the original mock reconciliation order.

    def _require_worker_receipt(self, receipt):
        pass  # Mock release already checked its original in-process workers.

    def _fresh_confirmation(self, purchase_group_id, booth_id):
        observed=self.payments.reconcile_all(purchase_group_id,booth_id,force=True)
        if (observed['obligation_state']!='OWED'
                or observed['entitlement_id'] is None
                or observed['state']=='REVIEW_REQUIRED'):
            raise DraftHeld('Original independently PAID unfulfilled entitlement required')
        with self.ledger.write():
            intent,finance=self.payments._group(purchase_group_id,booth_id)
            original_attempt=finance['legitimate_paid_attempt']
        if not original_attempt:
            raise DraftHeld('Original settled attempt unavailable')
        confirmed=self.payments.reconcile(
            purchase_group_id,booth_id,attempt_id=original_attempt,force=True)
        return observed,confirmed

    def claim(self,purchase_group_id,booth_id,payload):
        """Return the original trusted DraftLease or WAIT, never media bytes.

        Acquiring an original claimant while another visitor is active returns
        WAIT without preempting, even with otherwise perfectly valid proof.
        """
        if not isinstance(payload,str):
            raise PermissionError('Exact original private CCP or Recovery Ticket is required')
        if payload.startswith('MEONG:CCP:1:'):
            verifier=self.ccp
        elif payload.startswith('MEONG:RECOVERY:1:'):
            verifier=self.ticket
        else:
            raise PermissionError('Customer claim QR has the wrong identity role')
        proof=verifier.verify(purchase_group_id,booth_id,payload)
        # A verified QR alone is not settlement. A fresh independently signed
        # provider GET is mandatory after the original private proof.
        if self._busy_after_proof(purchase_group_id,booth_id,payload,proof,verifier):
            return {'state':'WAIT','reason':'BOOTH_BUSY','lease':None}
        observed,confirmed=self._fresh_confirmation(purchase_group_id,booth_id)
        if (not confirmed['fresh_checked'] or not confirmed['paid_verified']
                or confirmed['entitlement_id']!=observed['entitlement_id']):
            raise DraftHeld('Fresh exact original settlement cannot be verified')
        with self.ledger.write():
            # No provider I/O or transaction gap between current proof validity
            # and the original booth's occupancy compare-and-swap below.
            from photobooth.post_preview_refund_fence import deny_full_mock_refund_fulfillment
            deny_full_mock_refund_fulfillment(self.ledger,purchase_group_id)
            current_proof=verifier._verify_locked(purchase_group_id,booth_id,payload)
            if current_proof is None or current_proof!=proof:
                raise PermissionError('Original Checkout Claim Proof required')
            intent,finance=self.payments._group(purchase_group_id,booth_id)
            if (proof.draft_id!=intent['draft_id'] or finance['review_required']
                    or finance['entitlement_id']!=confirmed['entitlement_id']):
                raise DraftHeld('Original proof/payment scope changed')
            old=self.ledger.db.execute(
                'SELECT * FROM pp_drafts WHERE draft_id=?',(proof.draft_id,)).fetchone()
            if not old or old['booth_id']!=booth_id:
                raise DraftHeld('Original photo owner is not available')
            owner=self.ledger.db.execute(
                'SELECT * FROM pp_drafts WHERE booth_id=? AND closed=0',(booth_id,)).fetchone()
            if owner:
                return {'state':'WAIT','reason':'BOOTH_BUSY','lease':None}
            receipt=self.ledger.db.execute('''SELECT * FROM pp_isolation_ops
                WHERE draft_id=? AND state='ACKED' ORDER BY original_generation DESC LIMIT 1''',
                (proof.draft_id,)).fetchone()
            paid=self.ledger.db.execute(
                'SELECT status FROM pp_paid_services WHERE purchase_group_id=?',
                (purchase_group_id,)).fetchone()
            if (not receipt or old['closed']!=1 or old['lifecycle']!='ISOLATED'
                    or old['generation']!=receipt['original_generation']+1
                    or receipt['financial_class']!='PAID_OWED'
                    or (paid and paid['status']!='OWED')):
                raise DraftHeld('Original paid visit was not safely isolated')
            self._require_worker_receipt(receipt)
            self.ledger.db.execute('''UPDATE pp_drafts SET closed=0,lifecycle='ACTIVE',
                generation=generation+1,updated_at=? WHERE draft_id=? AND closed=1
                AND generation=?''',
                (self.ledger.now(),proof.draft_id,old['generation']))
            self.ledger._event(proof.draft_id,'ORIGINAL_PAID_CLAIM_REACQUIRED')
            lease=DraftLease(proof.draft_id,booth_id,old['visit_id'],old['generation']+1)
            self.ledger._owned(lease)
            return {'state':'REACQUIRED','lease':lease,'purchase_group_id':purchase_group_id,
                    'entitlement_id':finance['entitlement_id'],'service_still_owed':True}
