"""Backend original paid-ticket display permits; no printer/media admission.

Reuses original protected ticket service and common scoped display operations.
Receipt dispatch remains separately fenced; this seam enables no customer profile.
"""
import threading

from photobooth.post_preview_presentation import OriginalCCPPresentation
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_store import DraftHeld


class OriginalRecoveryPresentation(OriginalCCPPresentation):
    def __init__(self, credentials):
        # Different explicit authority from the CCP constructor, never a mode flag.
        if type(credentials) is not OriginalRecoveryTicketService:
            raise ValueError('Exact original paid ticket custody required')
        self.credentials = credentials
        self.ledger = credentials.ledger
        self._lock = threading.RLock()
        self._pending = None

    def offer(self, group, lease):
        with self._lock, self.ledger.lock:
            self._scope(group, lease)
            self.credentials.prepare(lease)  # Original paid/freshness/escrow checks.
            row = self.ledger.db.execute('''SELECT screen_state FROM pp_ticket_presentations
                WHERE purchase_group_id=?''', (group,)).fetchone()
            if not row or row['screen_state'] != 'NOT_OFFERED':
                raise DraftHeld('Original ticket opportunity cannot be replayed')
            if self._pending is not None:
                owner, original = self._pending
                entry = self.credentials._offers.get(original.presentation_id)
                if (owner == lease and entry and entry[0] is original
                        and 0 <= self.credentials.monotonic()-entry[1]
                        <= self.credentials.policy.offer_permit_seconds):
                    return original
            original = self.credentials.private_offer(lease)
            self._pending = (lease, original)
            return original

    def dismiss(self, group, lease, presentation_id):
        with self._lock, self.ledger.lock:
            self._scope(group, lease)
            row = self.ledger.db.execute('''SELECT screen_state,render_permit_id
                FROM pp_ticket_presentations WHERE purchase_group_id=?''', (group,)).fetchone()
            if row and row['screen_state'] == 'DISMISSED' and row['render_permit_id'] == presentation_id:
                return  # Lost ACK retry needs only durable identity, never plaintext.
            original = self._original(group, lease, presentation_id)
            self.credentials.dismiss(lease, original)
            self._pending = None
