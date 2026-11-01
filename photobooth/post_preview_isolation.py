"""Durable original mock-only booth isolation; never a refund or ticket release.

Runs after privacy retirement, out of the photo-job dispatcher. New visitor
admission requires a completed local quiescence fence and exactly acknowledged
original financial class. Backend/multi-booth real-money release is NOT enabled
until separately authenticated production support exists.
"""
import threading
import uuid

from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_store import DraftHeld,PostPreviewStore


class OriginalMockIsolation:
    def __init__(self, ledger, payments, jobs, launcher, *, printer_lane,
                 delivery=None, allow_incomplete_fixture=False):
        if (allow_incomplete_fixture is not True or
                not isinstance(ledger,PostPreviewStore) or
                not isinstance(payments,PostPreviewPayments) or payments.mode!='mock'
                or payments.ledger is not ledger or
                not isinstance(jobs,PhotoJobs) or jobs.service is None
                or jobs.service.ledger is not ledger or
                not isinstance(launcher,LaunchLease)
                or not isinstance(printer_lane, type(threading.Lock()))):
            raise DraftHeld('Exact original synthetic booth/worker/finance fence required')
        self.ledger,self.payments,self.jobs,self.launcher=ledger,payments,jobs,launcher
        self.lane=printer_lane
        self.delivery=delivery
        self._lock=threading.RLock()

    def _quiescent(self, draft):
        service=self.jobs.service
        if (self.jobs.busy or service.lease is None or
                service.lease.draft_id!=draft['draft_id'] or
                not service._hidden.is_set()):
            raise DraftHeld('Private worker must retire before original booth release')
        if (self.delivery is not None and self.delivery.worker is not None
                and self.delivery.worker._thread.is_alive()):
            raise DraftHeld('Original Drive worker is still active')
        if not self.lane.acquire(blocking=False):
            raise DraftHeld('Original thermal paper transport is still sending')
        self.lane.release()

    def _financial(self, draft):
        intent=self.ledger.db.execute(
            'SELECT * FROM pp_checkout_intents WHERE draft_id=?',
            (draft['draft_id'],)).fetchone()
        if intent is None:
            return 'NO_PAYMENT'
        group=intent['purchase_group_id']
        finance=self.ledger.db.execute(
            'SELECT * FROM pp_purchase_finance WHERE purchase_group_id=?',
            (group,)).fetchone()
        if finance is None:
            return 'NO_PAYMENT'
        if finance['review_required']:
            raise DraftHeld('Unresolved financial discrepancy requires review')
        attempts=list(self.ledger.db.execute(
            'SELECT * FROM pp_payment_attempts WHERE purchase_group_id=?',(group,)))
        terminals={'CANCELLED_UNPAID','EXPIRED_UNPAID','TERMINAL_UNPAID','NOT_CREATED'}
        if finance['entitlement_id'] is None:
            if any(a['payment_state'] not in terminals for a in attempts):
                raise DraftHeld('PENDING/UNKNOWN payment cannot release booth')
            return 'TERMINAL_UNPAID'
        if (not attempts or any(a['payment_state'] not in terminals|{'PAID'} for a in attempts)
                or not finance['legitimate_paid_attempt']):
            raise DraftHeld('Original PAID attempt/other attempts need reconciliation')
        original=next((a for a in attempts if a['attempt_id']==finance['legitimate_paid_attempt']),None)
        if (not original or original['payment_state']!='PAID'
                or not original['provider_ref'] or original['verified_at'] is None):
            raise DraftHeld('Original independently verified paid attempt required')
        ccp=self.ledger.db.execute('SELECT offered_at FROM pp_ccp_credentials WHERE purchase_group_id=?',
                                  (group,)).fetchone()
        if ccp is None or ccp['offered_at'] is None:
            raise DraftHeld('Customer original claim was never genuinely offered')
        ticket=self.ledger.db.execute(
            'SELECT receipt_state FROM pp_ticket_presentations WHERE purchase_group_id=?',(group,)).fetchone()
        if ticket and ticket['receipt_state'] in {'SENDING','UNCERTAIN'}:
            raise DraftHeld('Original ticket physical output requires classification')
        states=[row['state'] for row in self.ledger.db.execute(
            'SELECT state FROM pp_paid_strip_jobs WHERE purchase_group_id=?',(group,))]
        if any(state in {'SENDING','UNCERTAIN'} for state in states):
            raise DraftHeld('Original purchased photo physical output is uncertain')
        return 'PAID_OWED'

    def _owner(self,booth_id):
        rows=self.ledger.db.execute(
            'SELECT * FROM pp_drafts WHERE booth_id=? AND closed=0',
            (booth_id,)).fetchall()
        if len(rows)!=1:
            raise DraftHeld('Exact one original unresolved booth owner required')
        draft=rows[0]
        if draft['lifecycle']=='ACTIVE':
            raise DraftHeld('Current customer must privacy-retire first')
        return draft

    def prepare(self,booth_id):
        """Durable PREPARED only; NEVER allows new visitor before ACK."""
        with self._lock,self.ledger.write():
            draft=self._owner(booth_id)
            self._quiescent(draft)
            financial=self._financial(draft)
            existing=self.ledger.db.execute(
                'SELECT * FROM pp_isolation_ops WHERE draft_id=? AND original_generation=?',
                (draft['draft_id'],draft['generation'])).fetchone()
            if existing:
                if (existing['original_generation']!=draft['generation']
                        or existing['financial_class']!=financial
                        or existing['state']!='PREPARED'):
                    raise DraftHeld('Original isolation receipt changed')
                return existing['operation_id']
            key=uuid.uuid4().hex
            self.ledger.db.execute('''INSERT INTO pp_isolation_ops
                (draft_id,operation_id,booth_id,original_generation,financial_class,prepared_at)
                VALUES(?,?,?,?,?,?)''',
                (draft['draft_id'],key,booth_id,draft['generation'],financial,self.ledger.now()))
            self.ledger._event(draft['draft_id'],'ISOLATION_PREPARED')
            return key

    def acknowledge(self,booth_id,operation_id):
        """Recheck all source statuses and fence before freeing the booth."""
        with self._lock,self.ledger.write():
            stored=self.ledger.db.execute(
                'SELECT * FROM pp_isolation_ops WHERE operation_id=? AND booth_id=?',
                (operation_id,booth_id)).fetchone()
            if stored is None:
                raise DraftHeld('Exact original isolation PREPARED operation required')
            if stored['state']=='ACKED':
                return False
            draft=self._owner(booth_id)
            if draft['draft_id']!=stored['draft_id']:
                raise DraftHeld('Different original visitor owns the booth')
            self._quiescent(draft)
            if (draft['generation']!=stored['original_generation']
                    or self._financial(draft)!=stored['financial_class']):
                raise DraftHeld('Original isolation evidence changed after PREPARE')
            self.ledger.db.execute('''UPDATE pp_drafts SET closed=1,
                lifecycle='ISOLATED',generation=generation+1,updated_at=?
                WHERE draft_id=? AND closed=0 AND generation=?''',
                (self.ledger.now(),draft['draft_id'],draft['generation']))
            self.ledger.db.execute('''UPDATE pp_isolation_ops
                SET state='ACKED',acknowledged_at=? WHERE operation_id=? AND state='PREPARED' ''',
                (self.ledger.now(),operation_id))
            self.ledger._event(draft['draft_id'],'ISOLATION_ACKED')
            return True
