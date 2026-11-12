"""Original Sandbox proof-gated support CASES, never executable refunds.

Reuse original status/credential/refund policy. Only provider GET observations
may refresh original finance. No refund key/POST, amount override, worker-fence
assertion, media/print authority or merchant activation is implemented here.
"""
import hashlib
import json
import re
import uuid

from photobooth.post_preview_readiness import finite_number
from photobooth.post_preview_refund_assessment import (
    REFUND_REASONS,OriginalRefundEvidence,VerifiedPaidAttempt,assess_refund,assess_proof_loss_from_journal)
from photobooth.post_preview_store import DraftHeld,ORDER_VERSION
from photobooth.post_preview_remedy_contract import STATUSES
from photobooth.post_preview_worker_fence import canonical

_HELD='Original remedy review is held'
MAX_REQUESTS_PER_GROUP=128
MAX_OBSERVATIONS_PER_CASE=1024


def _require(value):
    if not value:raise DraftHeld(_HELD)


def _id(value):
    _require(type(value) is str and re.fullmatch(r'[a-f0-9]{32}',value) is not None)
    return value


class OriginalSandboxRemedy:
    def __init__(self,claim):
        from photobooth.post_preview_sandbox_handoff import OriginalSandboxClaim,_payments
        _require(type(claim) is OriginalSandboxClaim)
        _payments(claim.payments)
        self.claim,self.payments,self.ledger=claim,claim.payments,claim.ledger
        self._install()

    def __repr__(self):return '<OriginalSandboxRemedy: case review, not refund execution>'

    def _install(self):
        reasons=','.join("'"+reason+"'" for reason in sorted(REFUND_REASONS))
        tables={
            'pp_remedy_cases':f'''CREATE TABLE pp_remedy_cases (
                case_id TEXT PRIMARY KEY CHECK(length(case_id)=32),
                purchase_group_id TEXT NOT NULL REFERENCES pp_checkout_intents(purchase_group_id),
                booth_id TEXT NOT NULL,reported_reason TEXT NOT NULL CHECK(reported_reason IN ({reasons})),
                created_at REAL NOT NULL,UNIQUE(purchase_group_id,booth_id,reported_reason)) WITHOUT ROWID''',
            'pp_remedy_requests':'''CREATE TABLE pp_remedy_requests (
                request_id TEXT PRIMARY KEY CHECK(length(request_id)=32),
                case_id TEXT NOT NULL REFERENCES pp_remedy_cases(case_id),
                proof_role TEXT NOT NULL CHECK(proof_role IN ('CCP','RECOVERY')),
                proof_sha256 TEXT NOT NULL CHECK(length(proof_sha256)=64),created_at REAL NOT NULL) WITHOUT ROWID''',
            'pp_remedy_observations':'''CREATE TABLE pp_remedy_observations (
                observation_id TEXT PRIMARY KEY CHECK(length(observation_id)=32),
                request_id TEXT NOT NULL REFERENCES pp_remedy_requests(request_id),
                source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
                payload_json TEXT NOT NULL CHECK(length(payload_json) BETWEEN 1 AND 4096),
                created_at REAL NOT NULL,UNIQUE(request_id,source_sha256)) WITHOUT ROWID'''}
        conflicts={
            'pp_remedy_cases':'case_id=NEW.case_id OR (purchase_group_id=NEW.purchase_group_id AND booth_id=NEW.booth_id AND reported_reason=NEW.reported_reason)',
            'pp_remedy_requests':'request_id=NEW.request_id',
            'pp_remedy_observations':'observation_id=NEW.observation_id OR (request_id=NEW.request_id AND source_sha256=NEW.source_sha256)'}
        definitions=list(tables.items())
        for table in tables:
            for action in ('UPDATE','DELETE'):
                name=table+'_no_'+action.lower()
                definitions.append((name,f'''CREATE TRIGGER {name} BEFORE {action} ON {table}
                    BEGIN SELECT RAISE(ABORT,'Original remedy audit is immutable'); END'''))
            name=table+'_no_replace'
            definitions.append((name,f'''CREATE TRIGGER {name} BEFORE INSERT ON {table}
                WHEN EXISTS(SELECT 1 FROM {table} WHERE {conflicts[table]})
                BEGIN SELECT RAISE(ABORT,'Original remedy audit is immutable'); END'''))
        def sql(value):return ' '.join(value.split()).casefold().rstrip(';')
        try:
            with self.ledger.write():
                present=[bool(self.ledger.db.execute('SELECT 1 FROM sqlite_master WHERE name=?',(name,)).fetchone())
                         for name,_ in definitions]
                _require(not any(present) or all(present))  # Atomic install: partial old audit is loss, not first setup.
                for name,definition in definitions:
                    saved=self.ledger.db.execute('SELECT sql FROM sqlite_master WHERE name=?',(name,)).fetchone()
                    _require(saved is None or type(saved['sql']) is str and sql(saved['sql'])==sql(definition))
                for name,definition in definitions:
                    if not self.ledger.db.execute('SELECT 1 FROM sqlite_master WHERE name=?',(name,)).fetchone():
                        self.ledger.db.execute(definition)
        except Exception:raise DraftHeld(_HELD) from None

    def _request(self,request,group,booth,proof,reason):
        digest=hashlib.sha256(proof.encode()).hexdigest()
        role='CCP' if proof.startswith('MEONG:CCP:1:') else 'RECOVERY'
        with self.ledger.write():
            self.payments._group(group,booth)
            existing=self.ledger.db.execute('''SELECT r.*,c.purchase_group_id,c.booth_id,c.reported_reason
                FROM pp_remedy_requests r JOIN pp_remedy_cases c USING(case_id) WHERE request_id=?''',(request,)).fetchone()
            if existing:
                if ((existing['purchase_group_id'],existing['booth_id'],existing['reported_reason'],
                     existing['proof_role'],existing['proof_sha256'])!=(group,booth,reason,role,digest)):
                    raise PermissionError('Original remedy request scope changed')
                return existing['case_id']
            count=self.ledger.db.execute('''SELECT COUNT(*) FROM pp_remedy_requests r
                JOIN pp_remedy_cases c USING(case_id) WHERE c.purchase_group_id=? AND c.booth_id=?''',(group,booth)).fetchone()[0]
            _require(count<MAX_REQUESTS_PER_GROUP)
            now=self.ledger.now();_require(finite_number(now))
            case=self.ledger.db.execute('SELECT case_id FROM pp_remedy_cases WHERE purchase_group_id=? '
                'AND booth_id=? AND reported_reason=?',(group,booth,reason)).fetchone()
            case_id=case[0] if case else uuid.uuid4().hex
            if not case:self.ledger.db.execute('INSERT INTO pp_remedy_cases VALUES(?,?,?,?,?)',
                                               (case_id,group,booth,reason,now))
            self.ledger.db.execute('INSERT INTO pp_remedy_requests VALUES(?,?,?,?,?)',
                                  (request,case_id,role,digest,now))
            return case_id

    def _evidence(self,group,booth,reason):
        # Collect the existing original per-attempt GET verdicts, not a GUI or
        # wall-clock freshness assertion. No CREATE/cancel/refund is invoked.
        with self.ledger.write():
            self.payments._group(group,booth)
            ids=[row[0] for row in self.ledger.db.execute('SELECT attempt_id FROM pp_payment_attempts '
                'WHERE purchase_group_id=? ORDER BY ordinal',(group,))]
            _require(len(ids)<=3)
        observations={}
        for attempt in ids:
            try:observations[attempt]=self.payments.reconcile(group,booth,attempt_id=attempt,force=True)
            except Exception:observations[attempt]={}
        with self.ledger.write():
            intent,finance=self.payments._group(group,booth)
            contract=json.loads(intent['contract_json'])
            amount=finance['amount'] if finance else contract['amount']
            attempts=[dict(row) for row in self.ledger.db.execute('SELECT attempt_id,provider_ref,payment_state,'
                'verified_at,last_provider_state FROM pp_payment_attempts WHERE purchase_group_id=? ORDER BY ordinal',(group,))]
            service=self.ledger.db.execute('SELECT status,drive_state FROM pp_paid_services WHERE purchase_group_id=?',(group,)).fetchone()
            receipt=self.ledger.db.execute('SELECT receipt_state FROM pp_ticket_presentations WHERE purchase_group_id=?',(group,)).fetchone()
            strips=[row[0] for row in self.ledger.db.execute('SELECT state FROM pp_paid_strip_jobs WHERE purchase_group_id=?',(group,))]
            def fresh(row):
                observed=observations.get(row['attempt_id'],{})
                return (observed.get('fresh_checked') is True and observed.get('checked_attempt_id')==row['attempt_id']
                        and (row['payment_state']!='PAID' or observed.get('paid_verified') is True
                             and observed.get('provider_state')=='settlement'))
            original_id=finance['legitimate_paid_attempt'] if finance else None
            paid=[row for row in attempts if row['payment_state']=='PAID']
            def verified(row):
                return VerifiedPaidAttempt(row['attempt_id'],row['provider_ref'],self.payments.merchant_id,amount,fresh(row))
            source=next((verified(row) for row in paid if row['attempt_id']==original_id),None)
            extras=tuple(verified(row) for row in paid if row['attempt_id']!=original_id)
            integrity=bool(finance and not finance['review_required'] and finance['merchant_id']==self.payments.merchant_id
                           and finance['provider_mode']=='sandbox' and source is not None and source.independently_paid
                           and all(fresh(row) and row['payment_state'] in
                               {'PAID','CANCELLED_UNPAID','EXPIRED_UNPAID','TERMINAL_UNPAID'} for row in attempts))
            uncertain=bool(receipt and receipt['receipt_state'] in {'SENDING','UNCERTAIN'}
                           or any(state in {'SENDING','UNCERTAIN'} for state in strips))
            paper='UNCERTAIN' if any(s in {'SENDING','UNCERTAIN'} for s in strips) else (
                'SUBMITTED' if 'SUBMITTED' in strips else 'PREPARED' if 'PREPARED' in strips else 'NONE')
            fulfillment=service['status'] if service and service['status'] in {'OWED','COMPLETED','REVIEW'} else 'OWED'
            evidence=OriginalRefundEvidence(group,self.payments.merchant_id,amount,source,extras,
                reason=reason,fulfillment=fulfillment,print_outcome=paper,
                drive_outcome='UNKNOWN' if service else 'NONE',financial_integrity_verified=integrity)
            facts=dict(amount=amount,attempts=attempts,legitimate=original_id,
                financial_review=bool(finance and finance['review_required']),integrity=integrity,
                receipt=receipt[0] if receipt else None,strips=strips,
                service=dict(service) if service else None)
        decision=assess_proof_loss_from_journal(self.ledger,evidence) if reason=='PROOF_LOST_ONLY' else assess_refund(evidence)
        if uncertain:status='PRINT_INSPECTION_REQUIRED'
        elif facts['financial_review']:status='REFUND_REVIEW_REQUIRED'
        elif not integrity:status='WAITING_PROVIDER'
        elif fulfillment in {'COMPLETED','REVIEW'}:status='SERVICE_REVIEW_REQUIRED'
        elif reason=='PROOF_LOST_ONLY':status='PAID_OWED_REMEDY'  # No separate delivery certification: never blame loss alone.
        elif decision.disposition=='WAIT_RECOVERY':status='PAID_OWED_DELIVERY'
        else:status='REFUND_REVIEW_REQUIRED'
        return status,integrity,facts

    def request_case(self,request,group,booth,proof,reported_reason):
        _id(request);_id(group)
        _require(type(reported_reason) is str and reported_reason in REFUND_REASONS)
        verifier=self.claim._verifier(proof)
        verified=verifier.verify(group,booth,proof)
        case=self._request(request,group,booth,proof,reported_reason)
        status,fresh,facts=self._evidence(group,booth,reported_reason)
        snapshot=dict(kind='ORIGINAL_REMEDY_CASE',case_id=case,request_id=request,purchase_group_id=group,
            booth_id=booth,reported_reason=reported_reason,mode='sandbox',order_version=ORDER_VERSION,
            status=status,refund_state='NOT_REQUESTED',refund_capability='NOT_VERIFIED',
            financial_evidence_fresh=fresh,can_issue_refund=False,fulfillment_authorized=False)
        payload=canonical(snapshot);source=hashlib.sha256(canonical(dict(facts=facts,snapshot=snapshot)).encode()).hexdigest()
        with self.ledger.write():
            if verifier._verify_locked(group,booth,proof)!=verified:
                raise PermissionError('Original customer proof changed')
            previous=self.ledger.db.execute('SELECT payload_json FROM pp_remedy_observations '
                'WHERE request_id=? AND source_sha256=?',(request,source)).fetchone()
            if previous:_require(previous[0]==payload)
            else:
                count=self.ledger.db.execute('''SELECT COUNT(*) FROM pp_remedy_observations o
                    JOIN pp_remedy_requests r USING(request_id) WHERE r.case_id=?''',(case,)).fetchone()[0]
                _require(count<MAX_OBSERVATIONS_PER_CASE and len(payload)<=4096)
                now=self.ledger.now();_require(finite_number(now))
                self.ledger.db.execute('INSERT INTO pp_remedy_observations VALUES(?,?,?,?,?)',
                    (uuid.uuid4().hex,request,source,payload,now))
        return snapshot
