"""Original-order maintenance only; no create, renewal, fulfillment or release.

Financial leases and pacing live in the durable payment coordinator. This
single bounded scheduler reuses them after restart, including retired visits
and terminal attempts that may still receive late settlement. No public listener
or provider configuration is created by constructing this worker.
"""
import math
import threading


class PostPreviewLifecycleWorker:
    def __init__(self, payments, inbox, *, interval=1, max_groups=16):
        if inbox.payments is not payments:
            raise ValueError('Original payment coordinator and inbox required')
        if (type(interval) not in (int, float) or not math.isfinite(interval)
                or not 0.1 <= interval <= 60):
            raise ValueError('Bounded worker interval required')
        if type(max_groups) is not int or not 1 <= max_groups <= 100:
            raise ValueError('Bounded original-order batch required')
        self.payments, self.inbox = payments, inbox
        self.interval, self.max_groups = interval, max_groups
        self._cursor = ''
        self._stop = threading.Event()
        self._thread = None
        self._lifecycle_lock = threading.Lock()
        self._cycle_lock = threading.Lock()

    def _groups(self):
        ledger = self.payments.ledger
        with ledger.write():
            rows = ledger.db.execute('''SELECT f.purchase_group_id,d.booth_id
                FROM pp_purchase_finance f
                JOIN pp_checkout_intents i ON i.purchase_group_id=f.purchase_group_id
                JOIN pp_drafts d ON d.draft_id=i.draft_id
                WHERE f.purchase_group_id>? ORDER BY f.purchase_group_id LIMIT ?''',
                (self._cursor, self.max_groups)).fetchall()
            if not rows and self._cursor:
                self._cursor = ''
                rows = ledger.db.execute('''SELECT f.purchase_group_id,d.booth_id
                    FROM pp_purchase_finance f
                    JOIN pp_checkout_intents i ON i.purchase_group_id=f.purchase_group_id
                    JOIN pp_drafts d ON d.draft_id=i.draft_id
                    ORDER BY f.purchase_group_id LIMIT ?''', (self.max_groups,)).fetchall()
            if rows:
                self._cursor = rows[-1]['purchase_group_id']
            return [(r['purchase_group_id'], r['booth_id']) for r in rows]

    def run_once(self):
        # A manual maintenance tick cannot overlap the scheduler's own tick.
        if not self._cycle_lock.acquire(blocking=False):
            return {'inbox': 0, 'groups': 0, 'errors': 0}
        report = {'inbox': 0, 'groups': 0, 'errors': 0}
        try:
            try:
                report['inbox'] = int(self.inbox.process_one())
            except Exception:
                report['errors'] += 1
            try:
                groups = self._groups()
            except Exception:
                report['errors'] += 1
                return report
            for group, booth in groups:
                if self._stop.is_set():
                    break
                try:
                    # Never force pacing, POST a create, renew or grant service.
                    # reconcile_all also recovers durable original cancel intent.
                    self.payments.reconcile_all(group, booth)
                    report['groups'] += 1
                except Exception:
                    # One corrupt/unavailable original scope must not starve all
                    # others. No exception text, credentials or media is logged.
                    report['errors'] += 1
            return report
        finally:
            self._cycle_lock.release()

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        while not self._stop.is_set():
            self.run_once()
            self._stop.wait(self.interval)

    def start(self):
        with self._lifecycle_lock:
            if self.running:
                raise RuntimeError('Original lifecycle worker is still running')
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, name='postpay-lifecycle', daemon=True)
            self._thread.start()

    def stop(self, *, timeout=35):
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 <= timeout <= 60:
            raise ValueError('Bounded shutdown wait required')
        with self._lifecycle_lock:
            self._stop.set()
            if self._thread is not None:
                self._thread.join(timeout)
            return not self.running
