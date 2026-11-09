"""Backend-owned original CCP presentation, without media/payment authority.

Only authenticated current-owner API calls reach this adapter. The native
renderer gets a bounded private offer; only the backend owns OS custody and the
exact original in-memory permit. This does not mount a merchant kiosk profile.
"""
import threading

from photobooth.post_preview_ccp import OriginalCCPService
from photobooth.post_preview_store import DraftHeld


class OriginalCCPPresentation:
    def __init__(self, credentials):
        if type(credentials) is not OriginalCCPService:
            raise ValueError('Exact original CCP custody required')
        self.credentials = credentials
        self.ledger = credentials.ledger
        self._lock = threading.RLock()
        self._pending = None

    def _scope(self, group, lease):
        _, intent = self.credentials._scope(lease)
        if intent['purchase_group_id'] != group:
            raise DraftHeld('Exact original checkout required')

    def offer(self, group, lease):
        with self._lock, self.ledger.lock:
            self._scope(group, lease)
            finance = self.ledger.db.execute('''SELECT entitlement_id,review_required
                FROM pp_purchase_finance WHERE purchase_group_id=?''', (group,)).fetchone()
            if finance and (finance['entitlement_id'] or finance['review_required']):
                raise DraftHeld('CCP checkout presentation precedes paid recovery')
            self.credentials.issue_once(lease)
            pending = self._pending
            if pending is not None:
                owner, original = pending
                entry = self.credentials._offers.get(original.presentation_id)
                if (owner == lease and entry and entry[0] is original
                        and 0 <= self.credentials.monotonic()-entry[1]
                        <= self.credentials.policy.offer_permit_seconds):
                    return original  # Lost response retries the same permit/proof.
            original = self.credentials.private_offer(lease)
            self._pending = (lease, original)
            return original

    def _original(self, group, lease, presentation_id):
        self._scope(group, lease)
        pending = self._pending
        if (pending is None or pending[0] != lease
                or pending[1].presentation_id != presentation_id):
            raise DraftHeld('Exact live original display permit required')
        return pending[1]

    def visible(self, group, lease, presentation_id):
        with self._lock, self.ledger.lock:
            original = self._original(group, lease, presentation_id)
            self.credentials.mark_visible(lease, original)

    def retire(self, group, lease, presentation_id):
        with self._lock, self.ledger.lock:
            original = self._original(group, lease, presentation_id)
            self.credentials.retire_offer(original)
            self._pending = None

    def close(self):
        with self._lock:
            self.credentials.hide_private()
            self._pending = None
