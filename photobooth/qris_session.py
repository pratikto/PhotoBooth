"""Persistent kiosk visit state, independent of Kivy and camera hardware.

Network methods run on the controller's single worker. Journal transitions are
atomic and never contain a bearer/provider secret. A restart after capture may
have started is held for operator recovery; it cannot create another session
or resend an uncertain printer job.
"""
import copy
import hashlib
import json
from pathlib import Path
import threading
import time
import uuid
import secrets

from photobooth.manifest_io import write_json_atomic
from photobooth.payment_quote import quote_checkout


class KioskLease:
    """Prevent two local GUI processes from consuming the same visit journal."""
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.file = path.open('a+b')
        self.file.seek(0)
        if not self.file.read(1):
            self.file.write(b'0'); self.file.flush()
        self.file.seek(0)
        try:
            if __import__('os').name == 'nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, IOError) as error:
            self.file.close()
            raise RuntimeError('Another kiosk owns the payment journal') from error

    def close(self):
        if not self.file.closed:
            self.file.seek(0)
            if __import__('os').name == 'nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
            self.file.close()


class KioskCheckout:
    PHASES = {'CREATING', 'WAITING', 'RESERVED', 'STARTING', 'STARTED',
              'COMPLETING', 'COMPLETED', 'CANCELLING', 'CANCELLED', 'RECOVERY','RELEASING','SUSPENDED'}

    def __init__(self, path, client, *, mode, booth_id, endpoint):
        if mode not in {'sandbox', 'mock'}:
            raise ValueError('Only explicitly selected test environments are supported')
        self.path, self.client = Path(path), client
        self.context = {'mode': mode, 'booth_id': booth_id, 'endpoint': endpoint.rstrip('/')}
        self.lock = threading.RLock()
        self.worker_lock = threading.RLock()
        self.lease = KioskLease(str(self.path) + '.lock')
        self.data = None
        self._reconcile_at = 0
        self._customer_ticket = None
        self._opened_existing = False
        self._ownership_confirmed = False
        self._ownership_expires = 0
        self._permit_issued = False
        self._ticket_acknowledged = False
        self._last_claim_ticket = None
        self._resume_payment_confirmed = False
        self._privacy_generation = 0
        self._issue_retry_at = 0
        try:
            if self.path.exists():
                self._opened_existing = True
                if self.path.stat().st_size > 65536:
                    raise ValueError('Payment journal is too large')
                self.data = json.loads(self.path.read_text(encoding='utf-8'))
                if (self.data.get('version') != 1 or self.data.get('context') != self.context
                        or self.data.get('phase') not in self.PHASES
                        or quote_checkout(self.data['quantities']).total_amount != self.data['amount']
                        or len(self.data.get('checkout_key', '')) != 32):
                    raise ValueError('Payment journal needs operator recovery')
                if self.data['phase'] in {'STARTING', 'STARTED'}:
                    self.data['recovery'] = {'interrupted_phase': self.data['phase'],
                                             'reason': 'restart_after_capture_intent'}
                    self.data['phase'] = 'RECOVERY'
                    self._save()
        except BaseException:
            self.lease.close()
            raise

    def _save(self):
        from photobooth.capture_journal import sync_directory
        write_json_atomic(self.path, self.data)
        sync_directory(self.path.parent)

    def snapshot(self):
        with self.lock:
            return copy.deepcopy(self.data)

    @property
    def active(self):
        state = self.snapshot()
        return state is not None and state['phase'] not in {'COMPLETED', 'CANCELLED','SUSPENDED'}

    @property
    def customer_claim_required(self):
        return (bool(getattr(self.client,'customer_capability_supported',False)) and self.active
                and self._opened_existing and not self._ownership_confirmed)

    def customer_ticket(self):
        with self.lock:
            if (not self._customer_ticket or not self.data or self._opened_existing
                    or not (self.data.get('order') or {}).get('customer_capability_bound')):
                return None
            return ':'.join(('MEONG-RECOVERY-V1',self.context['booth_id'],
                             self.data['checkout_key'],self._customer_ticket))

    def acknowledge_ticket(self):
        if not self.customer_ticket():
            raise RuntimeError('Original live customer ticket required')
        self._ticket_acknowledged = True
        self._customer_ticket = None
        self._last_claim_ticket = None
        self._resume_payment_confirmed = False

    @property
    def ticket_acknowledged(self):
        return self._ticket_acknowledged

    def lock_customer(self):
        """Privacy lock after inactivity/minimize; never discard payment rights."""
        with self.lock:
            self._privacy_generation += 1
            self._opened_existing = True
            self._ownership_confirmed = False
            self._ownership_expires = 0
            self._customer_ticket = None
            self._last_claim_ticket = None
            self._resume_payment_confirmed = False
            self._ticket_acknowledged = False

    def customer_claim(self, ticket):
        if not isinstance(ticket,str) or len(ticket)>200:
            raise ValueError('Original customer ticket required')
        parts=ticket.strip().split(':')
        if (len(parts)!=4 or parts[:2]!=['MEONG-RECOVERY-V1',self.context['booth_id']]
                or not self.data or parts[2]!=self.data['checkout_key'] or not self.data.get('order')):
            raise ValueError('Original customer ticket required')
        with self.worker_lock:
            with self.lock:
                generation=self._privacy_generation
                operation=self.data.setdefault('customer_claim_operation_id',uuid.uuid4().hex)
                self._save()
            result=self.client.customer_claim(self.data['order']['order_id'],parts[3],operation)
            self._accept(result)
            with self.lock:
                if generation != self._privacy_generation:
                    raise RuntimeError('Customer proof callback belongs to a retired visit')
                allocation=result.get('fulfillment') or {}
                if result['state']=='PENDING' and not self.data.get('transaction_id'):
                    self.data['phase']='WAITING'
                elif allocation.get('transaction_id'):
                    if (self.data.get('allocation_operation_id')!=allocation.get('allocation_operation_id')
                            or self.data.get('transaction_id') not in (None,allocation['transaction_id'])):
                        raise RuntimeError('Original allocation requires operator review')
                    self.data['transaction_id']=allocation['transaction_id']
                    self.data['phase']='RECOVERY'
                elif result['service_state']=='RESERVED' and not self.data.get('transaction_id'):
                    self.data['phase']='RESERVED'
                else:
                    raise RuntimeError('Original service state requires review')
                self._ownership_confirmed=True
                self._ownership_expires=time.monotonic()+60
                self._permit_issued=False
                self._ticket_acknowledged=True
                self._last_claim_ticket=ticket
                self._resume_payment_confirmed=(result.get('customer_claim') or {}).get('payment_verified') is True
                self._save()
            return self.snapshot()

    def resume_binding(self):
        if not self._ownership_confirmed or time.monotonic()>=self._ownership_expires:
            raise RuntimeError('Fresh original customer proof required')
        order=self.data.get('order') or {};allocation=order.get('fulfillment') or {}
        if (not allocation.get('transaction_id') or allocation.get('transaction_id')!=self.data.get('transaction_id')
                or allocation.get('allocation_operation_id')!=self.data.get('allocation_operation_id')
                or not self._resume_payment_confirmed or order.get('state')!='PAID'):
            raise RuntimeError('Exact original photo binding required')
        binding={key:allocation[key] for key in ('fulfillment_id','transaction_id',
            'allocation_operation_id','contract_hash','booth_id','merchant_id')}
        binding.update(order_id=order['order_id'],grant_id=order['grant_id'])
        return binding

    def resume_permit(self):
        if (self._permit_issued or not self._last_claim_ticket or not self._ownership_confirmed
                or time.monotonic()>=self._ownership_expires):
            raise RuntimeError('Resume permission already issued')
        # Re-verify the original secret/action and current settlement at the
        # deliberate resume action, not a stale GUI flag or cached poll result.
        self.customer_claim(self._last_claim_ticket)
        from photobooth.resume_authority import trusted_resume_permit
        with self.lock:
            generation=self._privacy_generation
            permit=trusted_resume_permit(self.resume_binding(), validator=lambda:
                generation == self._privacy_generation and self._ownership_confirmed
                and time.monotonic() < self._ownership_expires)
            self._permit_issued=True
            return permit

    def confirm_resume(self, transaction_id, photo_phase):
        """Acknowledge the original validated photo session, never allocate again."""
        if photo_phase not in {'capture', 'review', 'result', 'done'}:
            raise RuntimeError('Validated original photo phase required')
        with self.worker_lock:
            with self.lock:
                if self.resume_binding()['transaction_id'] != transaction_id:
                    raise RuntimeError('Original transaction required')
                generation=self._privacy_generation
                ticket=self._last_claim_ticket
            # Delayed local reconstruction must not admit capture against stale
            # settlement, including when the server already completed service.
            self.customer_claim(ticket)
            order=self.snapshot()['order']
            if order['service_state'] == 'COMPLETED':
                if photo_phase not in {'result', 'done'}:
                    raise RuntimeError('Completed service cannot admit another capture')
            elif order['service_state'] in {'RESERVED', 'STARTED'}:
                result=self._transition(order,'STARTED',transaction_id)
                self._accept(result)
            else:
                raise RuntimeError('Original service requires operator review')
            with self.lock:
                if generation != self._privacy_generation or self.customer_claim_required:
                    raise RuntimeError('Resume acknowledgment belongs to a retired visit')
                self.data['phase']='STARTED'
                self.data['allocation_ready']=True
                self._save()
            return self.snapshot()

    def begin(self, quantities):
        quote = quote_checkout(quantities)
        with self.lock:
            if self.active:
                if self.data['quantities'] != quantities:
                    raise RuntimeError('The current visit cannot be replaced')
                return self.snapshot()
            self.data = {'version': 1, 'context': self.context, 'checkout_key': uuid.uuid4().hex,
                         'quantities': dict(quantities), 'amount': quote.total_amount,
                         'phase': 'CREATING', 'order': None, 'transaction_id': None}
            self._opened_existing=False
            self._ownership_confirmed=False
            self._permit_issued=False
            self._ticket_acknowledged=False
            self._last_claim_ticket=None
            self._resume_payment_confirmed=False
            self._customer_ticket=None
            if getattr(self.client,'customer_capability_supported',False):
                self._customer_ticket=secrets.token_urlsafe(32)
                self.data['customer_capability_hash']=hashlib.sha256(self._customer_ticket.encode()).hexdigest()
            # This must happen BEFORE the first network request.
            self._save()
            return self.snapshot()

    def _accept(self, order):
        with self.lock:
            data = self.data
            if (order.get('mode') != self.context['mode'] or order.get('checkout_key') != data['checkout_key']
                    or order.get('quantities') != data['quantities'] or order.get('amount') != data['amount']
                    or (data['order'] and order.get('order_id') != data['order']['order_id'])):
                raise ValueError('Backend returned a different visit')
            data['order'] = order
            self._save()

    def _transition(self, order, state, transaction_id):
        fence=order.get('service_fence') or {}
        options={'service_fence':fence['token']} if fence else {}
        return self.client.service_transition(order['order_id'],order['grant_id'],state,transaction_id,**options)

    def prepare_release(self, pin):
        with self.worker_lock:
            self.lock_customer()
            with self.lock:
                if not self.data or not self.data.get('order') or self.data['phase']=='SUSPENDED':
                    raise RuntimeError('Active original visit required')
                operation=self.data.setdefault('release_operation_id',uuid.uuid4().hex)
                self.data['phase']='RELEASING';self._save()
            self._accept(self.client.release(self.data['order']['order_id'],pin,operation))
            with self.lock:
                allocation=(self.data['order'].get('fulfillment') or {})
                if allocation.get('transaction_id'):
                    if (allocation.get('allocation_operation_id')!=self.data.get('allocation_operation_id')
                            or self.data.get('transaction_id') not in (None,allocation['transaction_id'])):
                        raise RuntimeError('Exact original allocation requires review')
                    self.data['transaction_id']=allocation['transaction_id'];self._save()
            return self.snapshot()

    def acknowledge_release(self, pin, receipt):
        from photobooth.release_authority import IsolationReceipt
        from photobooth.booth_storage import checked_path
        with self.worker_lock:
            data=self.snapshot();order=data['order'];release=order.get('release') or {}
            if (data['phase']!='RELEASING' or not isinstance(receipt,IsolationReceipt)
                    or release.get('operation_id')!=data.get('release_operation_id')):
                raise RuntimeError('Prepared local isolation required')
            receipt.consume(order['order_id'],data.get('transaction_id'),release['generation'])
            with self.lock:
                isolation=self.data.setdefault('isolation_id',receipt.isolation_id)
                self._save()
            self._accept(self.client.release(order['order_id'],pin,data['release_operation_id'],isolation_id=isolation))
            archive=self.snapshot();archive['phase']='SUSPENDED'
            self._archive_snapshot(archive,data['release_operation_id'])
            with self.lock:
                self.data=archive;self._save()
            self.lock_customer()
            return self.snapshot()

    def _archive_snapshot(self, snapshot, operation):
        from photobooth.booth_storage import checked_path
        from photobooth.capture_journal import sync_directory
        directory=checked_path(self.path.parent/'visits');directory.mkdir(parents=True,exist_ok=True)
        history=checked_path(directory/snapshot['checkout_key']);history.mkdir(exist_ok=True)
        write_json_atomic(checked_path(history/(operation+'.json')),snapshot)
        sync_directory(history)
        write_json_atomic(checked_path(directory/(snapshot['checkout_key']+'.json')),snapshot)
        sync_directory(directory)
        sync_directory(self.path.parent)

    def open_archived(self, ticket):
        import re
        from photobooth.booth_storage import checked_path
        parts=ticket.strip().split(':') if isinstance(ticket,str) and len(ticket)<=200 else []
        if (len(parts)!=4 or parts[:2]!=['MEONG-RECOVERY-V1',self.context['booth_id']]
                or re.fullmatch(r'[a-f0-9]{32}',parts[2]) is None):
            raise ValueError('Original customer ticket required')
        with self.worker_lock:
            if self.active:raise RuntimeError('Current customer must finish first')
            path=checked_path(self.path.parent/'visits'/(parts[2]+'.json'))
            if path.stat().st_size>65536:raise RuntimeError('Bounded original journal required')
            candidate=json.loads(path.read_text())
            if (candidate.get('context')!=self.context or candidate.get('phase') not in {'SUSPENDED','COMPLETED'}
                    or candidate.get('checkout_key')!=parts[2] or candidate.get('version')!=1
                    or quote_checkout(candidate['quantities']).total_amount!=candidate['amount']):
                raise RuntimeError('Original saved visit required')
            self.lock_customer()
            with self.lock:
                self.data=candidate;self.data['phase']='RECOVERY';self._save()
            result=self.customer_claim(ticket)
            with self.lock:
                self.data.pop('release_operation_id',None);self.data.pop('isolation_id',None);self._save()
            return self.snapshot()

    def _reconcile_payment(self, trigger):
        """Observe only; callers already own the single checkout worker."""
        self._reconcile_at = time.monotonic()+10
        result = self.client.reconcile(self.data['order']['order_id'], trigger=trigger)
        self._accept(result)
        delay = (result.get('reconciliation') or {}).get('retry_after', 10)
        if type(delay) is not int:
            delay = 10
        self._reconcile_at = time.monotonic()+max(1, min(60, delay))

    def connectivity_restored(self):
        """One same-order GET hint, never a claim, service ACK or camera action."""
        with self.worker_lock:
            data = self.snapshot() or {}
            if (not self.active or not data.get('order')
                    or not (data['phase'] in {'CREATING', 'WAITING', 'RECOVERY', 'RELEASING'}
                            or self.customer_claim_required)
                    or not callable(getattr(self.client, 'reconcile', None))):
                return False
            # The backend's persisted priority budget and in-flight lease are
            # authoritative even when this bypasses the local retry deadline.
            self._reconcile_payment('connectivity')
            return True

    def refresh(self):
        """Advance one bounded worker iteration, not a UI-thread network loop."""
        with self.worker_lock:
            if self.data is None:
                return None
            if self.data.get('pending_fulfillment_issue'):
                if time.monotonic() >= self._issue_retry_at:
                    self._send_fulfillment_issue()
                return self.snapshot()
            phase, order = self.data['phase'], self.data['order']
            if phase in {'RECOVERY','RELEASING'} or (self.customer_claim_required and order):
                # Observe payment privately after restart, never allocate or
                # display previous media. Legacy/third-party clients without
                # this narrow method retain the original conservative hold.
                reconcile = getattr(self.client, 'reconcile', None)
                if order and callable(reconcile) and time.monotonic() >= self._reconcile_at:
                    trigger = 'restart' if self._reconcile_at == 0 else 'poll'
                    self._reconcile_payment(trigger)
                return self.snapshot()
            if phase in {'COMPLETED', 'CANCELLED', 'STARTED','SUSPENDED'}:
                return self.snapshot()
            if phase == 'STARTING':
                if self.data['transaction_id'] and (not self.data.get('allocation_operation_id')
                                                    or self.data.get('allocation_ready') is True):
                    result = self._transition(order,'STARTED',self.data['transaction_id'])
                    self._accept(result)
                    self.data['phase'] = 'STARTED'; self._save()
                return self.snapshot()
            if phase == 'COMPLETING':
                result = self._transition(order,'COMPLETED',self.data['transaction_id'])
                self._accept(result)
                finished=self.snapshot();finished['phase']='COMPLETED'
                self._archive_snapshot(finished,'completed')
                self.data=finished;self._save()
                return self.snapshot()
            if phase == 'CANCELLING' and order:
                try:
                    result = self.client.cancel(order['order_id'])
                except Exception:
                    # A cancel may lose a race with settlement; the subsequent
                    # authoritative poll determines which customer keeps it.
                    result = self.client.status(order['order_id'])
            elif order is None:
                options = ({'customer_capability_hash':self.data['customer_capability_hash']}
                           if self.data.get('customer_capability_hash') else {})
                result = self.client.create_order(self.data['quantities'], self.data['checkout_key'],**options)
            else:
                result = self.client.status(order['order_id'])
            self._accept(result)  # persist identity before fetching an image
            state = result['state']
            if state in {'EXPIRED', 'CANCELLED', 'FAILED'}:
                self.data['phase'] = 'CANCELLED'
            elif state == 'REVIEW_REQUIRED':
                self.data['phase'] = 'RECOVERY'
            elif state == 'PAID':
                if result['service_state'] not in {'NONE', 'RESERVED'}:
                    self.data['phase'] = 'RECOVERY'
                else:
                    permit = self.client.claim(result['order_id'], self.data['checkout_key'])
                    self._accept(permit)
                    self.data['phase'] = 'RESERVED'
            elif phase != 'CANCELLING':
                self.data['phase'] = 'WAITING'
            self._save()
            return self.snapshot()

    def prepare_capture(self):
        with self.worker_lock:
            with self.lock:
                if self.customer_claim_required or self.data['phase'] != 'RESERVED' or not self.data['order'].get('grant_id'):
                    raise RuntimeError('A verified permit is required')
                allocate = getattr(self.client, 'allocate', None)
                if callable(allocate):
                    self.data.setdefault('allocation_operation_id',uuid.uuid4().hex)
                    self.data['allocation_ready'] = False
                self.data['phase'] = 'STARTING'; self._save()
                order = self.data['order']
                operation_id = self.data.get('allocation_operation_id')
            # Never hold the snapshot/UI lock during backend I/O.
            if callable(allocate):
                result = allocate(order['order_id'], order['grant_id'], operation_id)
                self._accept(result)
                with self.lock:
                    if self.data['phase'] != 'STARTING' or self.data.get('allocation_operation_id') != operation_id:
                        raise RuntimeError('Allocation callback belongs to a retired phase')
                    self.data['transaction_id'] = result['fulfillment']['transaction_id']
                    self._save()

    def bind_transaction(self, transaction_id):
        with self.lock:
            if self.data['phase'] != 'STARTING' or self.data['transaction_id'] not in (None, transaction_id):
                raise RuntimeError('Capture transaction is already bound')
            self.data['transaction_id'] = transaction_id; self._save()
            if self.data.get('allocation_operation_id'):
                self.data['allocation_ready'] = True; self._save()

    def require_recovery(self):
        with self.lock:
            self.data.setdefault('recovery', {'interrupted_phase': self.data['phase'],
                                               'reason': 'capture_requires_review'})
            self.data['phase'] = 'RECOVERY'; self._save()

    def report_fulfillment_issue(self, reason):
        from photobooth.checkout_store import FULFILLMENT_ISSUE_REASONS
        if reason not in FULFILLMENT_ISSUE_REASONS:
            raise ValueError('Allowlisted issue reason required')
        with self.worker_lock:
            with self.lock:
                order=(self.data or {}).get('order') or {}
                if (order.get('fulfillment') or {}).get('obligation_state')!='OWED':
                    raise RuntimeError('Original paid obligation required')
                operations=self.data.setdefault('fulfillment_issue_operations',{})
                operation=operations.setdefault(reason,uuid.uuid4().hex)
                self.data['pending_fulfillment_issue']={'operation_id':operation,'reason':reason}
                self.data['phase']='RECOVERY'
                self._save()  # Durable report identity before API I/O.
            return self._send_fulfillment_issue()

    def _send_fulfillment_issue(self):
        pending=self.snapshot()['pending_fulfillment_issue']
        self._issue_retry_at=time.monotonic()+10
        result=self.client.report_fulfillment_issue(self.data['order']['order_id'],
            pending['operation_id'],pending['reason'])
        self._accept(result)
        with self.lock:
            self.data.pop('pending_fulfillment_issue',None)
            self._save()
        return self.snapshot()

    def request_complete(self):
        with self.lock:
            if self.data['phase'] not in {'STARTED', 'COMPLETING'} or not self.data['transaction_id']:
                raise RuntimeError('No started service to complete')
            self.data['phase'] = 'COMPLETING'; self._save()

    def request_cancel(self):
        with self.lock:
            if self.data['phase'] not in {'CREATING', 'WAITING', 'CANCELLING'}:
                raise RuntimeError('This payment cannot be abandoned')
            self.data['phase'] = 'CANCELLING'; self._save()

    def close(self):
        with self.lock:
            self._customer_ticket=None
            self._last_claim_ticket=None
            self._resume_payment_confirmed=False
            self._ownership_confirmed=False
            try:
                self.client.close()
            finally:
                self.lease.close()
