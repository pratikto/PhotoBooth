"""Durable original mock-only booth isolation; never a refund or ticket release.

Runs after privacy retirement, out of the photo-job dispatcher. New visitor
admission requires a completed local quiescence fence and exactly acknowledged
original financial class. Backend/multi-booth real-money release is NOT enabled
until separately authenticated production support exists.
"""
import threading
import uuid
from pathlib import Path
from contextlib import ExitStack, contextmanager

from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_store import DraftHeld,PostPreviewStore
from photobooth.post_preview_paid_delivery import OriginalPaidDeliveryMonitor
from photobooth.booth_sync import BoothDriveWorker
from photobooth.post_preview_readiness_bridge import WorkerReadinessServer


class OriginalMockIsolation:
    def __init__(self, ledger, payments, jobs, launcher, *, printer_lane,
                 delivery=None, readiness=None, allow_incomplete_fixture=False):
        if (allow_incomplete_fixture is not True or
                not isinstance(ledger,PostPreviewStore) or
                not isinstance(payments,PostPreviewPayments) or payments.mode!='mock'
                or payments.ledger is not ledger or
                not isinstance(jobs,PhotoJobs) or jobs.service is None
                or jobs.service.ledger is not ledger or
                not isinstance(launcher,LaunchLease)
                or not isinstance(printer_lane, type(threading.Lock()))
                or readiness is not None and type(readiness) is not WorkerReadinessServer
                or delivery is not None and
                   (not isinstance(delivery,OriginalPaidDeliveryMonitor)
                    or delivery.binder.ledger is not ledger)):
            raise DraftHeld('Exact original synthetic booth/worker/finance fence required')
        self.ledger,self.payments,self.jobs,self.launcher=ledger,payments,jobs,launcher
        self.lane=printer_lane
        self.delivery=delivery
        self.readiness=readiness
        self._lock=threading.RLock()

    def restore_prepared_after_process_exit(self, booth_id, operation_id):
        """Reconstruct only the hidden original MOCK worker before its ACK.

        Call during bootstrap, before exposing PhotoJobs/camera/UI. The exact
        private-root kernel lock proves the previous owner process has exited;
        an unrelated repository lock or merely reopened SQLite is insufficient.
        No credential is decrypted, photo loaded, print sent or lease freed.
        Customer claim and original media verification still follow a safe ACK.
        """
        from photobooth.kiosk_v2.post_preview_checkout import PrivateCheckoutService
        from photobooth.post_preview_store import DraftLease, LIFECYCLE_EVENTS
        service = self.jobs.service
        stream = self.launcher.stream
        if (not isinstance(service, PrivateCheckoutService) or stream.closed
                or Path(stream.name).resolve() != (service.root/'data'/'kiosk-v2-launch.lock').resolve()
                or self.jobs.busy or self.jobs._thread is not None or self.jobs._closed
                or service._closed.is_set() or service.lease is not None
                or not service.paid_ticket_enabled or service.booth_id != booth_id):
            raise DraftHeld('Exact fresh original worker and private-root process lock required')
        with self._lock:
            with self.ledger.write():
                operation = self.ledger.db.execute('''SELECT o.*,i.purchase_group_id
                    FROM pp_isolation_ops o JOIN pp_checkout_intents i ON i.draft_id=o.draft_id
                    WHERE o.operation_id=? AND o.booth_id=?''', (operation_id,booth_id)).fetchone()
                if not operation or operation['state'] != 'PREPARED' or operation['financial_class'] != 'PAID_OWED':
                    raise DraftHeld('Exact original prepared paid operation required')
                group = operation['purchase_group_id']
                generation = operation['original_generation']
            observed = self.payments.reconcile_all(group,booth_id,force=True)
            if (observed['obligation_state'] != 'OWED' or not observed['entitlement_id']
                    or observed['state'] == 'REVIEW_REQUIRED'):
                raise DraftHeld('Original paid obligation cannot be verified')
            with self.ledger.write():
                _, finance = self.payments._group(group,booth_id)
                attempt = finance['legitimate_paid_attempt']
            confirmed = self.payments.reconcile(group,booth_id,attempt_id=attempt,force=True)
            if (not confirmed['fresh_checked'] or not confirmed['paid_verified']
                    or confirmed['entitlement_id'] != observed['entitlement_id']):
                raise DraftHeld('Fresh exact original settlement required')
            with ExitStack() as fences, self.ledger.write():
                fences.enter_context(self._readiness_guard())
                current = self.ledger.db.execute('SELECT * FROM pp_isolation_ops WHERE operation_id=?',
                                                 (operation_id,)).fetchone()
                draft = self._owner(booth_id)
                if (not current or current['state'] != 'PREPARED'
                        or current['original_generation'] != generation
                        or draft['draft_id'] != operation['draft_id'] or draft['generation'] != generation
                        or generation < 2 or draft['lifecycle'] not in LIFECYCLE_EVENTS-{'INACTIVITY_WARNING'}
                        or self.jobs.busy or self.jobs._thread is not None or service.lease is not None
                        or self._financial(draft) != 'PAID_OWED'):
                    raise DraftHeld('Original prepared worker context changed')
                fences.enter_context(self._drive_guard())
                if not self.lane.acquire(blocking=False):
                    raise DraftHeld('Original printer lane is still active')
                fences.callback(self.lane.release)
                # Privacy retirement had already fenced the original live
                # lease by +1. Restore that exact retired lease, never the new
                # booth generation and never a customer media capability.
                service.hide_private()
                service.lease = DraftLease(draft['draft_id'],booth_id,draft['visit_id'],generation-1)
                service.group = group
                service.phase = 'hold'
                self.ledger._event(draft['draft_id'],'BOOT_PREPARED_CONTEXT_RESTORED')
            return operation_id

    @contextmanager
    def _readiness_guard(self):
        if self.readiness is None:
            yield
            return
        with ExitStack() as guard:
            try:
                guard.enter_context(self.readiness.quiescent())
            except RuntimeError:
                raise DraftHeld('Original readiness collector is still active') from None
            yield

    def fence_readiness(self):
        """Also required when recovering an already ACKed original operation."""
        with self._readiness_guard():
            pass

    @contextmanager
    def _drive_guard(self):
        worker=self.delivery.worker if self.delivery is not None else None
        if worker is None:
            yield
            return
        if (not isinstance(worker,BoothDriveWorker)
                or worker.workspace is not self.delivery.binder.workspace
                or worker.client is not self.delivery.binder.client):
            raise DraftHeld('Exact original Drive worker fence required')
        with ExitStack() as guard:
            try:
                guard.enter_context(worker.quiescent())
            except RuntimeError:
                raise DraftHeld('Original Drive request is still active') from None
            yield

    def _quiescent(self, draft):
        service=self.jobs.service
        if (self.jobs.busy or service.lease is None or
                service.lease.draft_id!=draft['draft_id'] or
                not service._hidden.is_set()):
            raise DraftHeld('Private worker must retire before original booth release')
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
        # ExitStack releases the Drive fence only AFTER ledger commit/rollback.
        with self._lock,ExitStack() as fences,self.ledger.write():
            draft=self._owner(booth_id)
            fences.enter_context(self._readiness_guard())
            fences.enter_context(self._drive_guard())
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
                (draft_id,operation_id,booth_id,original_generation,financial_class,state,prepared_at)
                VALUES(?,?,?,?,?,'PREPARED',?)''',
                (draft['draft_id'],key,booth_id,draft['generation'],financial,self.ledger.now()))
            self.ledger._event(draft['draft_id'],'ISOLATION_PREPARED')
            return key

    def acknowledge(self,booth_id,operation_id):
        """Recheck all source statuses and fence before freeing the booth."""
        with self._lock,ExitStack() as fences,self.ledger.write():
            stored=self.ledger.db.execute(
                'SELECT * FROM pp_isolation_ops WHERE operation_id=? AND booth_id=?',
                (operation_id,booth_id)).fetchone()
            if stored is None:
                raise DraftHeld('Exact original isolation PREPARED operation required')
            fences.enter_context(self._readiness_guard())
            if stored['state']=='ACKED':
                return False
            draft=self._owner(booth_id)
            if draft['draft_id']!=stored['draft_id']:
                raise DraftHeld('Different original visitor owns the booth')
            fences.enter_context(self._drive_guard())
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
