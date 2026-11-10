"""Protected backend isolation/claim authority; no customer launcher enabled.

Original mock constructors remain guarded. The financial/occupancy algorithms
are reused only after exact original Sandbox/custody/worker authority checks.
No HTTP caller may create a worker receipt, select a key or assert quiescence.
"""
from contextvars import ContextVar
import hashlib
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
from photobooth.post_preview_store import DraftHeld,DraftLease
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_worker_fence import (
    WorkerReceiptVerifier, install_worker_receipts, canonical, _frame, _hex,
)

_claim_request=ContextVar('original_protected_claim_request',default=None)


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
            # Match original reconcile_all ordering: recover ONLY the durable
            # original cancel intent before GET, without requiring a scheduler.
            self.payments._send_cancel(group,booth,attempt[0])
            observed=self.payments.reconcile(group,booth,attempt_id=attempt[0],force=True)
            if not observed['fresh_checked']:
                raise DraftHeld('Fresh original release reconciliation required')

    def prepare(self, booth, *, expected_owner=None):
        _payments(self.payments)
        with self._lock:
            with self.ledger.write():
                draft=dict(self._owner(booth))
                if expected_owner is not None and (type(expected_owner) is not DraftLease
                        or expected_owner!=DraftLease(draft['draft_id'],booth,
                            draft['visit_id'],draft['generation'])):
                    raise DraftHeld('Exact original retired owner required')
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
        _payments(self.payments)
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
        self._request_lock=threading.RLock()
        install_worker_receipts(self.ledger)
        self._install_requests()

    claim=OriginalMockClaim.claim

    def _install_requests(self):
        with self.ledger.write():
            self.ledger.db.execute('''CREATE TABLE IF NOT EXISTS pp_protected_claim_ops (
                request_id TEXT PRIMARY KEY,booth_id TEXT NOT NULL,
                purchase_group_id TEXT NOT NULL REFERENCES pp_checkout_intents(purchase_group_id),
                proof_sha256 TEXT NOT NULL CHECK(length(proof_sha256)=64),
                state TEXT NOT NULL DEFAULT 'PREPARED' CHECK(state IN ('PREPARED','REACQUIRED')),
                draft_id TEXT,visit_id TEXT,generation INTEGER,entitlement_id TEXT,
                release_operation TEXT REFERENCES pp_isolation_ops(operation_id),
                created_at REAL NOT NULL,
                CHECK((state='PREPARED' AND draft_id IS NULL AND visit_id IS NULL
                    AND generation IS NULL AND entitlement_id IS NULL AND release_operation IS NULL)
                  OR (state='REACQUIRED' AND draft_id IS NOT NULL AND visit_id IS NOT NULL
                    AND generation>0 AND entitlement_id IS NOT NULL AND release_operation IS NOT NULL)))''')
            columns=[(r['name'],r['type'],r['notnull'],r['pk'])
                     for r in self.ledger.db.execute('PRAGMA table_info(pp_protected_claim_ops)')]
            expected=[('request_id','TEXT',0,1),('booth_id','TEXT',1,0),
                ('purchase_group_id','TEXT',1,0),('proof_sha256','TEXT',1,0),('state','TEXT',1,0),
                ('draft_id','TEXT',0,0),('visit_id','TEXT',0,0),('generation','INTEGER',0,0),
                ('entitlement_id','TEXT',0,0),('release_operation','TEXT',0,0),('created_at','REAL',1,0)]
            links=sorted((r['table'],r['from'],r['to'])
                for r in self.ledger.db.execute('PRAGMA foreign_key_list(pp_protected_claim_ops)'))
            if (columns!=expected or links!=[
                    ('pp_checkout_intents','purchase_group_id','purchase_group_id'),
                    ('pp_isolation_ops','release_operation','operation_id')]):
                raise DraftHeld('Original claim-request schema requires review')
            self.ledger.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_protected_claim_identity
                BEFORE UPDATE OF request_id,booth_id,purchase_group_id,proof_sha256,created_at ON pp_protected_claim_ops
                BEGIN SELECT RAISE(ABORT,'Original claim request is immutable'); END''')
            self.ledger.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_protected_claim_no_replay
                BEFORE UPDATE ON pp_protected_claim_ops
                WHEN OLD.state='REACQUIRED' OR NEW.state!='REACQUIRED'
                BEGIN SELECT RAISE(ABORT,'Original claim cannot be replaced'); END''')
            self.ledger.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_protected_claim_no_delete
                BEFORE DELETE ON pp_protected_claim_ops
                BEGIN SELECT RAISE(ABORT,'Original claim request must be retained'); END''')

    def _verifier(self, payload):
        if type(payload) is str and len(payload)<=256:
            if payload.startswith('MEONG:CCP:1:'):return self.ccp
            if payload.startswith('MEONG:RECOVERY:1:'):return self.ticket
        raise PermissionError('Original private customer proof required')

    def _record_reacquired(self, result):
        context=_claim_request.get()
        if context is None:
            return  # Trusted core-only call, never an exposed transport route.
        actor,request_id,proof_hash=context
        if actor is not self:
            raise DraftHeld('Original claim request context changed')
        lease=result['lease']
        release=self.ledger.db.execute("SELECT * FROM pp_isolation_ops WHERE draft_id=? "
            "AND original_generation=? AND state='ACKED'",(lease.draft_id,lease.generation-2)).fetchone()
        if not release:
            raise DraftHeld('Original claim release operation unavailable')
        changed=self.ledger.db.execute('''UPDATE pp_protected_claim_ops SET state='REACQUIRED',
            draft_id=?,visit_id=?,generation=?,entitlement_id=?,release_operation=?
            WHERE request_id=? AND state='PREPARED' AND booth_id=? AND purchase_group_id=? AND proof_sha256=?''',
            (lease.draft_id,lease.visit_id,lease.generation,result['entitlement_id'],release['operation_id'],
             request_id,lease.booth_id,result['purchase_group_id'],proof_hash)).rowcount
        if changed!=1:
            raise DraftHeld('Original claim request cannot be committed')

    def claim_once(self, request_id, group, booth, payload):
        """Original request persisted before GET; grant/CAS recorded atomically.

        Every retry still requires original proof and fresh legitimate settlement.
        A superseded owner/generation yields WAIT, never restoration of old pixels.
        """
        _payments(self.payments)
        if not _hex(request_id,32):
            raise ValueError('Original claim request identity required')
        verifier=self._verifier(payload)
        proof=verifier.verify(group,booth,payload)
        proof_hash=hashlib.sha256(payload.encode()).hexdigest()
        with self._request_lock:
            with self.ledger.write():
                current=verifier._verify_locked(group,booth,payload)
                if current!=proof:
                    raise PermissionError('Original private customer proof required')
                request=self.ledger.db.execute('SELECT * FROM pp_protected_claim_ops WHERE request_id=?',
                                              (request_id,)).fetchone()
                if request:
                    if (request['booth_id']!=booth or request['purchase_group_id']!=group
                            or request['proof_sha256']!=proof_hash):
                        raise PermissionError('Original claim request scope changed')
                    replay=request['state']=='REACQUIRED'
                    if replay:
                        owner=self.ledger.db.execute('SELECT * FROM pp_drafts WHERE booth_id=? AND closed=0',
                                                     (booth,)).fetchone()
                        if (not owner or owner['draft_id']!=request['draft_id']
                                or owner['visit_id']!=request['visit_id']
                                or owner['generation']!=request['generation'] or owner['lifecycle']!='ACTIVE'):
                            return {'state':'WAIT','reason':'BOOTH_BUSY','lease':None}
                else:
                    self.ledger.db.execute('''INSERT INTO pp_protected_claim_ops
                        (request_id,booth_id,purchase_group_id,proof_sha256,created_at)
                        VALUES(?,?,?,?,?)''',(request_id,booth,group,proof_hash,self.ledger.now()))
                    replay=False
            if not replay:
                token=_claim_request.set((self,request_id,proof_hash))
                try:return self.claim(group,booth,payload)
                finally:_claim_request.reset(token)
            observed,confirmed=self._fresh_confirmation(group,booth)
            if not confirmed['fresh_checked'] or not confirmed['paid_verified']:
                raise DraftHeld('Fresh original claim settlement required')
            with self.ledger.write():
                if verifier._verify_locked(group,booth,payload)!=proof:
                    raise PermissionError('Original customer proof changed')
                from photobooth.post_preview_refund_fence import deny_full_mock_refund_fulfillment
                deny_full_mock_refund_fulfillment(self.ledger,group)
                request=self.ledger.db.execute('SELECT * FROM pp_protected_claim_ops WHERE request_id=?',
                                              (request_id,)).fetchone()
                _,finance=self.payments._group(group,booth)
                if (finance['review_required'] or finance['entitlement_id']!=request['entitlement_id']
                        or observed['entitlement_id']!=request['entitlement_id']
                        or confirmed['entitlement_id']!=request['entitlement_id']):
                    raise DraftHeld('Original claim entitlement changed')
                paid=self.ledger.db.execute('SELECT status FROM pp_paid_services WHERE purchase_group_id=?',
                                            (group,)).fetchone()
                if paid and paid['status']!='OWED':
                    raise DraftHeld('Original claim service is no longer owed')
                owner=self.ledger.db.execute('SELECT * FROM pp_drafts WHERE booth_id=? AND closed=0',
                                             (booth,)).fetchone()
                if (not owner or owner['draft_id']!=request['draft_id'] or owner['visit_id']!=request['visit_id']
                        or owner['generation']!=request['generation'] or owner['lifecycle']!='ACTIVE'):
                    return {'state':'WAIT','reason':'BOOTH_BUSY','lease':None}
                release=self.ledger.db.execute('SELECT * FROM pp_isolation_ops WHERE operation_id=?',
                                               (request['release_operation'],)).fetchone()
                require_acked_worker_receipt(self.ledger,release)
                lease=DraftLease(owner['draft_id'],booth,owner['visit_id'],owner['generation'])
                self.ledger._owned(lease)
                return dict(state='REACQUIRED',lease=lease,purchase_group_id=group,
                            entitlement_id=request['entitlement_id'],service_still_owed=True)

    def _require_worker_receipt(self, receipt):
        require_acked_worker_receipt(self.ledger,receipt)

    def _release_class_allows_claim(self, receipt):
        # A later independent settlement must not strand an original claimant
        # whose previously terminal-unpaid visit was genuinely worker-fenced.
        # Fresh PAID/proof and the authenticated receipt are still mandatory;
        # NO_PAYMENT or an unvalidated/uncertain release never qualifies.
        return receipt['financial_class'] in {'PAID_OWED','TERMINAL_UNPAID'}

    def _busy_after_proof(self, group, booth, payload, proof, verifier):
        with self.ledger.write():
            if verifier._verify_locked(group,booth,payload)!=proof:
                raise PermissionError('Original customer proof required')
            return bool(self.ledger.db.execute('SELECT 1 FROM pp_drafts WHERE booth_id=? AND closed=0',
                                                (booth,)).fetchone())

    def _fresh_confirmation(self, group, booth):
        _payments(self.payments)
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
