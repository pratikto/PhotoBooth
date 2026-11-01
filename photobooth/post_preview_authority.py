"""Backend-owned charge request and original-worker readiness observations.

No customer request may submit these objects. Occupancy observation is read-only;
it never releases a booth, rotates a fence, cancels an order or grants media.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from photobooth.post_preview_readiness import CheckObservation, ReadinessScope
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
            if (self.launch_lease.stream.closed or self.jobs._closed or self.jobs.service is not self.service
                    or self.service._hidden.is_set() or self.service._closed.is_set()
                    or self.service.lease is None or self.service.phase not in
                    {'claim_proof','checkout_ready','payment_pending','payment_hold','paid_hold'}
                    or self.jobs.busy and self.jobs.current_action not in
                    {'freeze_checkout','ccp_visible','begin_payment','continue_payment','check_payment','snapshot'}):
                return denied
            with ledger.write():
                lease = self.service.lease
                ledger._owned(lease)
                row = ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?', (lease.draft_id,)).fetchone()
                if (not row or ReadinessScope(row['purchase_group_id'], lease.booth_id,
                        row['contract_sha256'], lease.generation) != scope):
                    return denied
                # Prior PP financial/service rights cannot be silently treated
                # as free. Later paid release must provide its own exact proof.
                if ledger.db.execute('''SELECT 1 FROM pp_purchase_finance f
                    JOIN pp_checkout_intents i ON i.purchase_group_id=f.purchase_group_id
                    JOIN pp_drafts d ON d.draft_id=i.draft_id
                    WHERE d.booth_id=? AND i.purchase_group_id!=? LIMIT 1''',
                    (scope.booth_id, scope.purchase_group_id)).fetchone():
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
