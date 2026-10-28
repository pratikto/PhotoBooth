"""Persistent kiosk visit state, independent of Kivy and camera hardware.

Network methods run on the controller's single worker. Journal transitions are
atomic and never contain a bearer/provider secret. A restart after capture may
have started is held for operator recovery; it cannot create another session
or resend an uncertain printer job.
"""
import copy
import json
from pathlib import Path
import threading
import time
import uuid

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
              'COMPLETING', 'COMPLETED', 'CANCELLING', 'CANCELLED', 'RECOVERY'}

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
        try:
            if self.path.exists():
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
        write_json_atomic(self.path, self.data)

    def snapshot(self):
        with self.lock:
            return copy.deepcopy(self.data)

    @property
    def active(self):
        state = self.snapshot()
        return state is not None and state['phase'] not in {'COMPLETED', 'CANCELLED'}

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


    def refresh(self):
        """Advance one bounded worker iteration, not a UI-thread network loop."""
        with self.worker_lock:
            if self.data is None:
                return None
            phase, order = self.data['phase'], self.data['order']
            if phase == 'RECOVERY':
                # Observe payment privately after restart, never allocate or
                # display previous media. Legacy/third-party clients without
                # this narrow method retain the original conservative hold.
                reconcile = getattr(self.client, 'reconcile', None)
                if order and callable(reconcile) and time.monotonic() >= self._reconcile_at:
                    trigger = 'restart' if self._reconcile_at == 0 else 'poll'
                    self._reconcile_at = time.monotonic()+10
                    result = reconcile(order['order_id'], trigger=trigger)
                    self._accept(result)
                    delay = (result.get('reconciliation') or {}).get('retry_after', 10)
                    if type(delay) is not int:
                        delay = 10
                    self._reconcile_at = time.monotonic()+max(1, min(60, delay))
                return self.snapshot()
            if phase in {'COMPLETED', 'CANCELLED', 'STARTED'}:
                return self.snapshot()
            if phase == 'STARTING':
                if self.data['transaction_id'] and (not self.data.get('allocation_operation_id')
                                                    or self.data.get('allocation_ready') is True):
                    result = self.client.service_transition(order['order_id'], order['grant_id'],
                                                           'STARTED', self.data['transaction_id'])
                    self._accept(result)
                    self.data['phase'] = 'STARTED'; self._save()
                return self.snapshot()
            if phase == 'COMPLETING':
                result = self.client.service_transition(order['order_id'], order['grant_id'],
                                                       'COMPLETED', self.data['transaction_id'])
                self._accept(result)
                self.data['phase'] = 'COMPLETED'; self._save()
                return self.snapshot()
            if phase == 'CANCELLING' and order:
                try:
                    result = self.client.cancel(order['order_id'])
                except Exception:
                    # A cancel may lose a race with settlement; the subsequent
                    # authoritative poll determines which customer keeps it.
                    result = self.client.status(order['order_id'])
            elif order is None:
                result = self.client.create_order(self.data['quantities'], self.data['checkout_key'])
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
                if self.data['phase'] != 'RESERVED' or not self.data['order'].get('grant_id'):
                    raise RuntimeError('A verified permit is required')
                allocate = getattr(self.client, 'allocate', None)
                if callable(allocate):
                    self.data['allocation_operation_id'] = uuid.uuid4().hex
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
            self.client.close()
            self.lease.close()
