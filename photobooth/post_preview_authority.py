"""Backend-owned charge request and original-worker readiness observations.

No customer request may submit these objects. Occupancy observation is read-only;
it never releases a booth, rotates a fence, cancels an order or grants media.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from photobooth.post_preview_readiness import CheckObservation, ReadinessScope, FreezeScope, finite_number
from photobooth.post_preview_store import DraftHeld

_authenticated_charge = ContextVar('postpay_authenticated_charge', default=None)


@contextmanager
def authenticated_charge_request(scope, observed_at):
    """Used only after backend BoothAuthenticator + original lease validation."""
    token = _authenticated_charge.set((scope, observed_at))
    try:
        yield
    finally:
        _authenticated_charge.reset(token)


def authenticated_payment_readiness(scope):
    original = _authenticated_charge.get()
    if original is None:
        return CheckObservation('UNKNOWN', None)
    expected, stamp = original
    return CheckObservation('READY' if type(expected) is ReadinessScope and expected == scope
                            else 'NOT_READY', stamp)


class OriginalWorkerReadiness:
    def __init__(self, service, jobs, launch_lease, legacy, *, environ=None):
        self.service, self.jobs, self.launch_lease, self.legacy = service, jobs, launch_lease, legacy
        self.environ = dict(environ or {})

    def __call__(self, scope):
        from photobooth.checkout_store import CheckoutStore
        from photobooth.kiosk_v2.photos import PhotoJobs
        from photobooth.kiosk_v2.post_preview_photos import PrivatePhotoService
        from photobooth.kiosk_v2.recovery import LaunchLease, review_recovery
        unknown = CheckObservation('UNKNOWN', None)
        if (not isinstance(self.service, PrivatePhotoService) or not isinstance(self.jobs, PhotoJobs)
                or not isinstance(self.launch_lease, LaunchLease) or not isinstance(self.legacy, CheckoutStore)):
            return unknown
        ledger = self.service.ledger
        stamp = ledger.now()
        denied = CheckObservation('NOT_READY', stamp)
        try:
            freezing=type(scope) is FreezeScope
            if type(scope) not in {ReadinessScope,FreezeScope}:return denied
            if (self.launch_lease.stream.closed or self.jobs._closed or self.jobs.service is not self.service
                    or self.service._hidden.is_set() or self.service._closed.is_set()
                    or self.service.lease is None or self.service.phase not in
                    ({'final_preview'} if freezing else
                     {'claim_proof','checkout_ready','payment_pending','payment_hold','paid_hold'})
                    or freezing and (not self.jobs.busy or self.jobs.current_action!='freeze_checkout')
                    or self.jobs.busy and self.jobs.current_action not in
                    {'freeze_checkout','ccp_visible','begin_payment','continue_payment','check_payment','snapshot'}):
                return denied
            if freezing:
                actual=self.service.checkout.freeze_scope(self.service.lease,self.service.templates,
                    revision=scope.revision,expected_amount=scope.amount)
                if actual!=scope:return denied
            with ledger.write():
                lease = self.service.lease
                ledger._owned(lease)
                row = ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?', (lease.draft_id,)).fetchone()
                if (not freezing and (not row or ReadinessScope(row['purchase_group_id'], lease.booth_id,
                        row['contract_sha256'], lease.generation) != scope)):
                    return denied
                # Historical money/OWED must survive a safe handoff, but its
                # existence alone does not mean the old visit still owns the
                # booth. Require the exact generation's completed PP-06 ACK;
                # closed/public Ads or an ACK from a prior claim are not proof.
                prior=ledger.db.execute('''SELECT d.*,i.purchase_group_id,f.review_required
                    FROM pp_drafts d JOIN pp_checkout_intents i ON i.draft_id=d.draft_id
                    LEFT JOIN pp_purchase_finance f ON f.purchase_group_id=i.purchase_group_id
                    WHERE d.booth_id=? AND d.draft_id!=?''',
                    (scope.booth_id,lease.draft_id)).fetchall()
                for old in prior:
                    if (not old['closed'] or old['lifecycle']!='ISOLATED'
                            or old['review_required']):
                        return denied
                    receipt=ledger.db.execute('''SELECT * FROM pp_isolation_ops
                        WHERE draft_id=? AND booth_id=? AND original_generation=?
                        AND state='ACKED' ''',
                        (old['draft_id'],scope.booth_id,old['generation']-1)).fetchone()
                    if (not receipt or not finite_number(receipt['prepared_at'])
                            or not finite_number(receipt['acknowledged_at'])
                            or not receipt['prepared_at']<=receipt['acknowledged_at']<=stamp):
                        return denied
                    group=old['purchase_group_id']
                    if ledger.db.execute('''SELECT 1 FROM pp_payment_attempts
                        WHERE purchase_group_id=? AND payment_state NOT IN
                        ('CANCELLED_UNPAID','EXPIRED_UNPAID','TERMINAL_UNPAID','NOT_CREATED','PAID')
                        LIMIT 1''',(group,)).fetchone():
                        return denied
                    if ledger.db.execute('''SELECT 1 FROM pp_ticket_presentations
                        WHERE purchase_group_id=? AND receipt_state IN ('SENDING','UNCERTAIN')
                        UNION ALL SELECT 1 FROM pp_paid_strip_jobs
                        WHERE purchase_group_id=? AND state IN ('SENDING','UNCERTAIN')
                        LIMIT 1''',(group,group)).fetchone():
                        return denied
            with self.legacy.lock:
                rows = self.legacy.db.execute('SELECT * FROM checkouts WHERE booth_id=?', (scope.booth_id,)).fetchall()
                for old in rows:
                    if not old['closed'] or old['state'] not in {'PAID','EXPIRED','CANCELLED','FAILED'}:
                        return denied
                    if old['state'] == 'PAID':
                        rights = self.legacy.fulfillment(old['id'], scope.booth_id)
                        if rights['obligation_state'] == 'FULFILLED':
                            continue
                        from photobooth.checkout_release import latest
                        release = latest(self.legacy, old['id'], scope.booth_id)
                        fence = self.legacy.service_fence(old['id'], scope.booth_id)
                        if (not release or release['state'] != 'ACKED' or not release['isolation_id']
                                or not fence or not fence['suspended'] or fence['generation'] != release['generation']):
                            return denied
            root = Path(self.launch_lease.stream.name).parent.parent
            if review_recovery(root, environ=self.environ)['status'] != 'CLEAR_FOR_MANUAL_START':
                return denied
            return CheckObservation('READY', stamp)
        except DraftHeld:
            return denied
        except Exception:
            return unknown
