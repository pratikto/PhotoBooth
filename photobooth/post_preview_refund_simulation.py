"""Durable refund lifecycle SIMULATOR, unmounted and incapable of money I/O.

The exact SQLite provider type is mandatory. No HTTP client, Midtrans endpoint,
merchant activation or customer payout is implemented. Keys/statuses describe
this simulator only; they do not establish real provider idempotency semantics.
"""
from contextlib import contextmanager, ExitStack
import json
from pathlib import Path
import sqlite3
import threading
import uuid

from photobooth.booth_storage import checked_path
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_refund_assessment import OriginalRefundEvidence, assess_refund
from photobooth.post_preview_isolation import OriginalMockIsolation
from photobooth.post_preview_store import DraftHeld
from photobooth.manifest_io import manifest_lock


class SimulatedRefundProvider:
    """Independent durable fake provider; every operation is local SQLite."""
    def __init__(self, path, *, simulation=False, eligible=True):
        if simulation is not True:
            raise DraftHeld('Explicit refund simulator required')
        path=checked_path(path);path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(path,isolation_level=None,check_same_thread=False)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS simulated_refunds (
            refund_key TEXT PRIMARY KEY, merchant TEXT NOT NULL, charge_ref TEXT NOT NULL,
            amount INTEGER NOT NULL, state TEXT NOT NULL, requests INTEGER NOT NULL,
            UNIQUE(merchant,charge_ref))''')
        self.eligible=eligible;self.lose_reply=False;self.response_override=None
        self._lock=threading.RLock()

    def simulate_request(self,key,merchant,charge_ref,amount):
        with self._lock:
            row=self.db.execute('SELECT * FROM simulated_refunds WHERE refund_key=?',(key,)).fetchone()
            if row:
                if (row['merchant'],row['charge_ref'],row['amount'])!=(merchant,charge_ref,amount):
                    raise DraftHeld('Simulator original charge/key conflict')
                self.db.execute('UPDATE simulated_refunds SET requests=requests+1 WHERE refund_key=?',(key,))
            else:
                self.db.execute('INSERT INTO simulated_refunds VALUES(?,?,?,?,?,1)',
                                (key,merchant,charge_ref,amount,'REQUESTED'))
            if self.lose_reply:
                self.lose_reply=False
                raise OSError('Simulated accepted request response loss')
            return self.lookup(key)

    def lookup(self,key):
        with self._lock:
            row=self.db.execute('SELECT * FROM simulated_refunds WHERE refund_key=?',(key,)).fetchone()
            return dict(self.response_override or row) if self.response_override or row else None

    def advance(self,key,state):
        if state not in {'REQUESTED','PROCESSING','CONFIRMED'}:
            raise ValueError('Supported simulated state required')
        with self._lock:
            self.db.execute('UPDATE simulated_refunds SET state=? WHERE refund_key=?',(state,key))

    def close(self): self.db.close()


class MockRefundCoordinator:
    """Original-charge journal and fences for mock-only lifecycle experiments."""
    def __init__(self,payments,provider,*,isolation=None,simulation=False):
        if (simulation is not True or type(payments) is not PostPreviewPayments
                or payments.mode!='mock' or type(provider) is not SimulatedRefundProvider
                or isolation is not None and (type(isolation) is not OriginalMockIsolation
                    or isolation.payments is not payments)):
            raise DraftHeld('Only exact original mock refund simulation components allowed')
        self.payments,self.ledger,self.provider,self.isolation=payments,payments.ledger,provider,isolation
        self._lock=threading.RLock()
        with self.ledger.write():
            self.ledger.db.execute('''CREATE TABLE IF NOT EXISTS pp_mock_refund_intents (
                intent_id TEXT PRIMARY KEY, purchase_group_id TEXT NOT NULL REFERENCES pp_checkout_intents(purchase_group_id),
                attempt_id TEXT NOT NULL UNIQUE REFERENCES pp_payment_attempts(attempt_id),
                merchant TEXT NOT NULL, charge_ref TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>0),
                kind TEXT NOT NULL CHECK(kind IN ('FULL','EXCESS')), refund_key TEXT NOT NULL UNIQUE,
                state TEXT NOT NULL CHECK(state IN ('PREPARED','SENT_UNKNOWN','REQUESTED','PROCESSING','CONFIRMED','REVIEW_REQUIRED')),
                created_at REAL NOT NULL, updated_at REAL NOT NULL)''')
            self.ledger.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_mock_refund_identity_immutable
                BEFORE UPDATE OF intent_id,purchase_group_id,attempt_id,merchant,charge_ref,amount,kind,refund_key,created_at
                ON pp_mock_refund_intents BEGIN SELECT RAISE(ABORT,'Original mock refund identity immutable'); END''')

    def _intent(self,intent_id,group,booth):
        self.payments._group(group,booth)
        row=self.ledger.db.execute('SELECT * FROM pp_mock_refund_intents WHERE intent_id=? AND purchase_group_id=?',
                                  (intent_id,group)).fetchone()
        if row is None: raise DraftHeld('Exact original simulated refund required')
        return row

    def _paid(self,group,booth,attempt):
        fresh=self.payments.reconcile(group,booth,attempt_id=attempt,force=True)
        if not fresh['fresh_checked'] or not fresh['paid_verified']:
            raise DraftHeld('Fresh original settlement required; no refund for unknown/unpaid')

    @contextmanager
    def _full_fence(self,group,booth):
        iso=self.isolation
        if (iso is None or iso.launcher.stream.closed or iso.jobs._closed
                or Path(iso.launcher.stream.name).resolve() != (iso.jobs.service.root/'data'/'kiosk-v2-launch.lock').resolve()):
            raise DraftHeld('Original worker isolation context and process lock required')
        with iso._lock,ExitStack() as guards:
            if iso.delivery is not None:
                if iso.delivery.worker is not None:
                    raise DraftHeld('Live cloud worker is outside the refund simulator fence')
                if not iso.delivery.binder._lock.acquire(blocking=False):
                    raise DraftHeld('Original cloud/photo worker is still active')
                guards.callback(iso.delivery.binder._lock.release)
            with self.ledger.write():
                intent,finance=self.payments._group(group,booth)
                old=self.ledger.db.execute('SELECT * FROM pp_drafts WHERE draft_id=?',(intent['draft_id'],)).fetchone()
                if not old or finance['review_required']:
                    raise DraftHeld('Original owner/finance requires review')
                if old['closed']==0:
                    iso._quiescent(old)
                else:
                    ack=self.ledger.db.execute('''SELECT * FROM pp_isolation_ops WHERE draft_id=? AND state='ACKED'
                        AND original_generation=?''',(old['draft_id'],old['generation']-1)).fetchone()
                    if not ack or old['lifecycle']!='ISOLATED':
                        raise DraftHeld('Original archived worker fence unavailable')
                receipt=self.ledger.db.execute('SELECT receipt_state FROM pp_ticket_presentations WHERE purchase_group_id=?',(group,)).fetchone()
                if receipt and receipt['receipt_state'] in {'SENDING','UNCERTAIN'}:
                    raise DraftHeld('Original receipt physical outcome requires review')
                if self.ledger.db.execute("SELECT 1 FROM pp_paid_strip_jobs WHERE purchase_group_id=? AND state IN ('SENDING','UNCERTAIN','SUBMITTED')",(group,)).fetchone():
                    raise DraftHeld('Original photo paper outcome requires review')
                service=self.ledger.db.execute('SELECT * FROM pp_paid_services WHERE purchase_group_id=?',(group,)).fetchone()
                if service and service['transaction_id']:
                    if iso.delivery is None or service['drive_state']=='UPLOADED':
                        raise DraftHeld('Original cloud publication requires independent review')
                    file=checked_path(iso.delivery.binder.workspace.root/service['transaction_id']/'manifest.json')
                    guards.enter_context(manifest_lock(file))
                    if not file.is_file() or file.stat().st_size>2*1024*1024:
                        raise DraftHeld('Bounded original manifest required')
                    data=json.loads(file.read_text(encoding='utf-8'))
                    if (data.get('payment_binding',{}).get('service_id')!=service['service_id']
                            or data.get('upload_status') not in {'PENDING_UPLOAD','LOCAL_ONLY','PENDING_DRIVE_BINDING'}
                            or any(not isinstance(v,dict) or v.get('status') not in {'PENDING','LOCAL_ONLY'}
                                   or v.get('drive_file_id') for v in data.get('upload_files',{}).values())):
                        raise DraftHeld('Original uploaded or uncertain bytes require review')
            if not iso.lane.acquire(blocking=False): raise DraftHeld('Original thermal lane active')
            guards.callback(iso.lane.release)
            yield

    def prepare(self,evidence,booth,*,attempt_id=None):
        if type(evidence) is not OriginalRefundEvidence:
            raise TypeError('Exact immutable assessment facts required')
        decision=assess_refund(evidence)
        target=attempt_id or (decision.candidates[0] if len(decision.candidates)==1 else None)
        if target not in decision.candidates or self.provider.eligible is not True:
            raise DraftHeld('Simulated refund eligibility not established')
        group=evidence.purchase_group_id
        self.payments.reconcile_all(group,booth,force=True)
        self._paid(group,booth,target)
        kind='FULL' if decision.disposition=='CANDIDATE_FULL_SERVICE_FAILURE' else 'EXCESS'
        with self._lock,ExitStack() as guards:
            if kind=='FULL':guards.enter_context(self._full_fence(group,booth))
            with self.ledger.write():
                intent,finance=self.payments._group(group,booth)
                source=evidence.original
                if kind=='FULL' and self.ledger.db.execute(
                    "SELECT 1 FROM pp_payment_attempts WHERE purchase_group_id=? AND payment_state NOT IN ('PAID','EXPIRED_UNPAID','CANCELLED_UNPAID','TERMINAL_UNPAID','NOT_CREATED')",(group,)).fetchone():
                    raise DraftHeld('Other original payment attempts remain unresolved')
                paid={x['attempt_id']:x for x in self.ledger.db.execute(
                    "SELECT * FROM pp_payment_attempts WHERE purchase_group_id=? AND payment_state='PAID'",(group,))}
                expected={x.attempt_id:x for x in (source,*evidence.excess)}
                if (finance['review_required'] or finance['legitimate_paid_attempt']!=source.attempt_id
                        or finance['merchant_id']!=evidence.merchant_id or finance['amount']!=evidence.amount_idr
                        or set(paid)!=set(expected) or any(x['provider_ref']!=expected[k].provider_ref
                            or expected[k].merchant_id!=finance['merchant_id'] or expected[k].amount_idr!=finance['amount']
                            for k,x in paid.items())):
                    raise DraftHeld('Original settled charge facts conflict')
                old=self.ledger.db.execute('SELECT * FROM pp_mock_refund_intents WHERE attempt_id=?',(target,)).fetchone()
                if old:
                    if old['purchase_group_id']!=group or old['kind']!=kind:raise DraftHeld('Original refund intent conflict')
                    return old['intent_id']
                key=uuid.uuid4().hex;now=self.ledger.now()
                self.ledger.db.execute('INSERT INTO pp_mock_refund_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                    (key,group,target,finance['merchant_id'],paid[target]['provider_ref'],finance['amount'],kind,
                     'MOCK-REFUND-'+key,'PREPARED',now,now))
                self.ledger._event(intent['draft_id'],'MOCK_REFUND_INTENT_PREPARED')
                return key

    def submit(self,intent_id,group,booth,*,checkpoint=None):
        with self.ledger.write():row=dict(self._intent(intent_id,group,booth))
        if row['state']!='PREPARED':return self.reconcile(intent_id,group,booth)
        if self.provider.eligible is not True:
            raise DraftHeld('Simulated provider eligibility changed before request')
        self._paid(group,booth,row['attempt_id'])
        with self._lock,ExitStack() as guards:
            if row['kind']=='FULL':guards.enter_context(self._full_fence(group,booth))
            with self.ledger.write():
                current=self._intent(intent_id,group,booth)
                send=current['state']=='PREPARED'
                if send:self.ledger.db.execute("UPDATE pp_mock_refund_intents SET state='SENT_UNKNOWN',updated_at=? WHERE intent_id=?",(self.ledger.now(),intent_id))
            if send:
                if checkpoint is not None:checkpoint('SENT_BEFORE_SIMULATOR')
                try:self.provider.simulate_request(row['refund_key'],row['merchant'],row['charge_ref'],row['amount'])
                except OSError:pass
                if checkpoint is not None:checkpoint('SIMULATOR_REPLY_BOUNDARY')
        return self.reconcile(intent_id,group,booth)

    def reconcile(self,intent_id,group,booth):
        with self.ledger.write():row=dict(self._intent(intent_id,group,booth))
        response=self.provider.lookup(row['refund_key'])
        with self.ledger.write():
            current=self._intent(intent_id,group,booth)
            if response:
                if ((response.get('refund_key'),response.get('merchant'),response.get('charge_ref'),response.get('amount'))
                        !=(row['refund_key'],row['merchant'],row['charge_ref'],row['amount'])
                        or response.get('state') not in {'REQUESTED','PROCESSING','CONFIRMED'}):
                    state='REVIEW_REQUIRED'
                else:
                    rank={'PREPARED':0,'SENT_UNKNOWN':0,'REQUESTED':1,'PROCESSING':2,'CONFIRMED':3,'REVIEW_REQUIRED':99}
                    state=current['state'] if rank[current['state']]>=rank[response['state']] else response['state']
                self.ledger.db.execute('UPDATE pp_mock_refund_intents SET state=?,updated_at=? WHERE intent_id=?',
                                      (state,self.ledger.now(),intent_id))
        return self.status(intent_id,group,booth)

    def status(self,intent_id,group,booth):
        with self.ledger.write():row=self._intent(intent_id,group,booth)
        return {'state':row['state'],'reference':'MOCK-'+row['intent_id'],
                'simulation_only':True,'money_returned':False,'media_authorized':False}
