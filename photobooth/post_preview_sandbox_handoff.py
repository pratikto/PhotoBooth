"""Protected backend isolation/claim authority; no customer launcher enabled.

Original mock constructors remain guarded. The financial/occupancy algorithms
are reused only after exact original Sandbox/custody/worker authority checks.
No HTTP caller may create a worker receipt, select a key or assert quiescence.
"""
import json
import threading
import uuid

from photobooth.credential_vault import WindowsDPAPIProtector
from photobooth.linux_credential_vault import LinuxSecretServiceProtector
from photobooth.midtrans_sandbox import MidtransSandboxClient
from photobooth.post_preview_ccp import OriginalCCPService
from photobooth.post_preview_claim import OriginalMockClaim
from photobooth.post_preview_isolation import OriginalMockIsolation
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_readiness import finite_number
from photobooth.post_preview_sandbox_delivery import OriginalSandboxPaidDelivery
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_worker_fence import (
    WorkerReceiptVerifier, install_worker_receipts, canonical, _frame, _hex,
)


def _payments(payments):
    if (type(payments) is not PostPreviewPayments or payments.mode!='sandbox'
            or type(payments.provider) is not MidtransSandboxClient):
        raise DraftHeld('Exact original Sandbox financial authority required')


def require_acked_worker_receipt(ledger, operation):
    """Durable backend-validated evidence survives a backend capability restart.

    Called in the original claim/ACK transaction. The immutable receipt was
    authenticated with the private current capability BEFORE original ACK.
    No customer-provided content or current-key reissuance is accepted here.
    """
    rows=ledger.db.execute('SELECT * FROM pp_worker_retirements WHERE operation_id=? '
        'AND backend_verified_at IS NOT NULL',(operation['operation_id'],)).fetchall()
    if (operation['state']!='ACKED' or len(rows)!=1
            or rows[0]['backend_verified_at']!=operation['acknowledged_at']):
        raise DraftHeld('Original backend-ACKed native worker receipt required')
    receipt=rows[0]
    try:
        frame=json.loads(receipt['frame_json'])
        from photobooth.post_preview_worker_fence import _original
        original=_original(ledger,operation['operation_id'])
        stamp=frame['observed_at']
        if (type(frame) is not dict or type(frame.get('version')) is not int
                or type(frame.get('generation')) is not int
                or not _hex(receipt['key_id'],32) or not _hex(receipt['mac'],64)
                or not finite_number(stamp) or not finite_number(receipt['backend_verified_at'])
                or not original['prepared_at']<=stamp<=receipt['backend_verified_at']
                or canonical(frame)!=receipt['frame_json']
                or frame!=_frame(original,receipt['key_id'],stamp)):
            raise ValueError('Original worker receipt changed')
    except (ValueError,TypeError,KeyError,RecursionError):
        raise DraftHeld('Original ACK worker evidence cannot be verified') from None


class OriginalSandboxIsolation:
    def __init__(self, payments, delivery, receipts):
        _payments(payments)
        if (type(delivery) is not OriginalSandboxPaidDelivery
                or delivery.binder.payments is not payments
                or type(receipts) is not WorkerReceiptVerifier
                or receipts.ledger is not payments.ledger):
            raise DraftHeld('Original backend delivery and native receipt authority required')
        delivery.binder._backend_context()
        self.payments,self.delivery,self.receipts=payments,delivery,receipts
        self.ledger=payments.ledger
        self._lock=threading.RLock()
        install_worker_receipts(self.ledger)

    # These original methods only classify stored finance/occupancy. No mock
    # constructor, fixture flag, provider or local-worker stand-in is created.
    _financial=OriginalMockIsolation._financial
    _owner=OriginalMockIsolation._owner

    def _refresh(self, draft_id, booth):
        with self.ledger.write():
            row=self.ledger.db.execute('SELECT purchase_group_id FROM pp_checkout_intents '
                                      'WHERE draft_id=?',(draft_id,)).fetchone()
            group=row[0] if row else None
            attempts=list(self.ledger.db.execute('SELECT attempt_id FROM pp_payment_attempts '
                'WHERE purchase_group_id=? ORDER BY ordinal',(group,))) if group else []
        # Fresh original observations only; pacing/404/outage never fabricates
        # an unpaid terminal. Retrying is the SAME PREPARED operation.
        for attempt in attempts:
            observed=self.payments.reconcile(group,booth,attempt_id=attempt[0],force=True)
            if not observed['fresh_checked']:
                raise DraftHeld('Fresh original release reconciliation required')

    def prepare(self, booth):
        with self._lock:
            with self.ledger.write():
                draft=dict(self._owner(booth))
            self._refresh(draft['draft_id'],booth)
            with self.ledger.write():
                current=self._owner(booth)
                if (current['draft_id']!=draft['draft_id'] or current['generation']!=draft['generation']):
                    raise DraftHeld('Original release owner changed')
                financial=self._financial(current)
                existing=self.ledger.db.execute('SELECT * FROM pp_isolation_ops '
                    'WHERE draft_id=? AND original_generation=?',
                    (current['draft_id'],current['generation'])).fetchone()
                if existing:
                    if existing['state']!='PREPARED' or existing['financial_class']!=financial:
                        raise DraftHeld('Original release financial evidence changed')
                    return existing['operation_id']
                operation=uuid.uuid4().hex
                stamp=self.ledger.now()
                if not finite_number(stamp) or stamp<current['updated_at']:
                    raise DraftHeld('Original release preparation clock is invalid')
                self.ledger.db.execute('''INSERT INTO pp_isolation_ops
                    (draft_id,operation_id,booth_id,original_generation,financial_class,state,prepared_at)
                    VALUES(?,?,?,?,?,'PREPARED',?)''',
                    (current['draft_id'],operation,booth,current['generation'],financial,stamp))
                self.ledger._event(current['draft_id'],'PROTECTED_ISOLATION_PREPARED')
                return operation

    def acknowledge(self, booth, operation):
        with self._lock:
            with self.ledger.write():
                stored=self.ledger.db.execute('SELECT * FROM pp_isolation_ops '
                    'WHERE operation_id=? AND booth_id=?',(operation,booth)).fetchone()
                if not stored:
                    raise DraftHeld('Exact original release operation required')
                if stored['state']=='ACKED':
                    require_acked_worker_receipt(self.ledger,stored)
                    return False  # Original lost ACK replay, never release B.
                self.receipts.verify(operation)
                original=dict(stored)
            if not self.delivery.stop():
                raise DraftHeld('Original backend delivery worker is still active')
            self._refresh(original['draft_id'],booth)
            with self.ledger.write():
                stored=self.ledger.db.execute('SELECT * FROM pp_isolation_ops '
                    'WHERE operation_id=? AND booth_id=?',(operation,booth)).fetchone()
                draft=self._owner(booth)
                receipt=self.receipts.verify(operation)
                if (stored['state']!='PREPARED' or draft['draft_id']!=original['draft_id']
                        or draft['generation']!=original['original_generation']
                        or self._financial(draft)!=stored['financial_class']
                        or receipt['backend_verified_at'] is not None):
                    raise DraftHeld('Original worker/financial release evidence changed')
                stamp=self.ledger.now()
                if (not finite_number(stamp) or stamp<stored['prepared_at']
                        or stamp<json.loads(receipt['frame_json'])['observed_at']):
                    raise DraftHeld('Original release acknowledgement clock is invalid')
                changed=self.ledger.db.execute('''UPDATE pp_drafts SET closed=1,
                    lifecycle='ISOLATED',generation=generation+1,updated_at=?
                    WHERE draft_id=? AND closed=0 AND generation=?''',
                    (stamp,draft['draft_id'],stored['original_generation'])).rowcount
                if changed!=1:
                    raise DraftHeld('Original occupancy cannot be released')
                self.ledger.db.execute("UPDATE pp_isolation_ops SET state='ACKED',acknowledged_at=? "
                    'WHERE operation_id=?',(stamp,operation))
                self.ledger.db.execute('UPDATE pp_worker_retirements SET backend_verified_at=? '
                    'WHERE operation_id=? AND key_id=?',(stamp,operation,receipt['key_id']))
                self.ledger._event(draft['draft_id'],'PROTECTED_ISOLATION_ACKED')
                return True


class OriginalSandboxClaim:
    def __init__(self, payments, ccp, ticket):
        _payments(payments)
        if (type(ccp) is not OriginalCCPService or type(ticket) is not OriginalRecoveryTicketService
                or ccp.ledger is not payments.ledger or ticket.payments is not payments
                or ccp.merchant_id!=payments.merchant_id or ticket.merchant_id!=payments.merchant_id
                or ccp.protector is not ticket.protector
                or type(ccp.protector) not in {WindowsDPAPIProtector,LinuxSecretServiceProtector}):
            raise DraftHeld('Exact original protected claim custody required')
        self.payments,self.ccp,self.ticket=payments,ccp,ticket
        self.ledger=payments.ledger

    claim=OriginalMockClaim.claim

    def _require_worker_receipt(self, receipt):
        require_acked_worker_receipt(self.ledger,receipt)

    def _busy_after_proof(self, group, booth, payload, proof, verifier):
        with self.ledger.write():
            if verifier._verify_locked(group,booth,payload)!=proof:
                raise PermissionError('Original customer proof required')
            return bool(self.ledger.db.execute('SELECT 1 FROM pp_drafts WHERE booth_id=? AND closed=0',
                                                (booth,)).fetchone())

    def _fresh_confirmation(self, group, booth):
        with self.ledger.write():
            _,finance=self.payments._group(group,booth)
            original=finance['legitimate_paid_attempt'] if finance else None
        if original:
            confirmed=self.payments.reconcile(group,booth,attempt_id=original,force=True)
            observed=self.payments.reconcile_all(group,booth,force=True)
        else:
            observed=self.payments.reconcile_all(group,booth,force=True)
            with self.ledger.write():
                _,finance=self.payments._group(group,booth)
                original=finance['legitimate_paid_attempt'] if finance else None
            if original and observed['checked_attempt_id']==original and observed['paid_verified']:
                confirmed=observed
            elif original:
                confirmed=self.payments.reconcile(group,booth,attempt_id=original,force=True)
            else:
                raise DraftHeld('Original settled attempt unavailable')
        if (observed['obligation_state']!='OWED' or not observed['entitlement_id']
                or observed['state']=='REVIEW_REQUIRED' or confirmed['checked_attempt_id']!=original):
            raise DraftHeld('Original independent settled obligation required')
        return observed,confirmed
