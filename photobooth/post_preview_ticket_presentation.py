"""Backend original paid-ticket display permits; no printer/media admission.

Reuses original protected ticket service and common scoped display operations.
Receipt dispatch remains separately fenced; this seam enables no customer profile.
"""
import threading

from photobooth.post_preview_presentation import OriginalCCPPresentation
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_store import DraftHeld
from photobooth.printer import ThermalPrinter


class OriginalRecoveryPresentation(OriginalCCPPresentation):
    def __init__(self, credentials, *, printer=None, shared_lane=None):
        # Different explicit authority from the CCP constructor, never a mode flag.
        if type(credentials) is not OriginalRecoveryTicketService:
            raise ValueError('Exact original paid ticket custody required')
        if not (printer is None and shared_lane is None) and (
                type(printer) is not ThermalPrinter or type(shared_lane) is not type(threading.Lock())):
            raise ValueError('Original thermal printer and shared owned lane required')
        self.credentials = credentials
        self.ledger = credentials.ledger
        self._lock = threading.RLock()
        self._pending = None
        self._printer, self._printer_lane = printer, shared_lane

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

    def receipt(self, group, lease, presentation_id):
        """One durable original send; a repeated request only observes the job.

        Hold this ticket's actor across I/O, never the SQLite lock. The native
        screen has its own UI clock and does not acquire this actor/printer lane.
        """
        with self._lock:
            with self.ledger.lock:
                self._scope(group, lease)
                row = self.ledger.db.execute('''SELECT * FROM pp_ticket_presentations
                    WHERE purchase_group_id=?''', (group,)).fetchone()
                if (not row or row['render_permit_id'] != presentation_id
                        or row['screen_state'] not in {'VISIBLE', 'DISMISSED'}):
                    raise DraftHeld('Original genuinely visible receipt required')
                if row['receipt_state'] in {'SENDING', 'SUBMITTED', 'NOT_SENT', 'UNCERTAIN'}:
                    return dict(receipt_job_id=row['receipt_job_id'], receipt_state=row['receipt_state'],
                                physical_paper_verified=False)
                original = self._original(group, lease, presentation_id)
            result = self.credentials.send_receipt_once(lease, original, self._printer,
                                                         send_lock=self._printer_lane)
            return dict(result, physical_paper_verified=False)
