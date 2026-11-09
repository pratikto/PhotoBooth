"""Native original backend ticket card/timer seam, not a merchant launcher.

prepare/acknowledge_visible/dismiss run on the serialized worker. Card creation,
poll/NEXT and immediate hide run on the UI thread. Paper dispatch has its own
original journal/lane; this component never interprets paid status as printing
or machine-release authority.
"""
import threading

from photobooth.post_preview_ccp import render_private_ccp
from photobooth.post_preview_proof_client import PostPreviewRecoveryClient
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_ticket_window import VisibleTicketWindow


class RemoteRecoveryTicketSession:
    def __init__(self, client, group, lease, *, monotonic=None):
        if type(client) is not PostPreviewRecoveryClient:
            raise TypeError('Original authenticated paid ticket client required')
        self.client, self.group, self.lease = client, group, lease
        self.window = VisibleTicketWindow() if monotonic is None else VisibleTicketWindow(monotonic=monotonic)
        self._hidden = threading.Event()
        self._offer = self._qr = self.card = self._rendered_offer = None
        self._dismiss_pending = False
        self._prepared = False

    def _active(self):
        if self._hidden.is_set():
            raise DraftHeld('Original ticket display retired')

    def prepare(self):
        self._active()
        if self._prepared:
            raise DraftHeld('Original ticket session cannot restart')
        self._prepared = True  # Never automatically reoffer after a lost response.
        offer = self.client.private_offer(self.group, self.lease)
        qr = render_private_ccp(offer)
        self._offer, self._qr = offer, qr
        if self._hidden.is_set():
            self._offer = self._qr = None
            self._active()

    def _current(self, offer):
        return not self._hidden.is_set() and self._offer is offer

    def create_card(self):
        self._active()
        if self._offer is None or self.card is not None or self._dismiss_pending:
            raise DraftHeld('Exact original ticket card required')
        from .ccp_view import PrivateRecoveryTicketCard
        offer = self._offer
        def rendered(actual):
            if actual is offer and self._current(offer):
                self._rendered_offer = offer
                # Genuine UI rendering starts the privacy deadline immediately.
                # Network acknowledgement must never extend this opportunity.
                self.window.start(genuine_visible=True)
        self.card = PrivateRecoveryTicketCard(offer, self._qr, rendered,
                                             is_current=lambda:self._current(offer))
        self._qr = None
        if self._hidden.is_set():
            self.card.retire()
            self._active()
        return self.card

    def acknowledge_visible(self):
        self._active()
        offer = self._rendered_offer
        if offer is None or not self._current(offer):
            raise DraftHeld('Genuine original card rendering required')
        self.client.mark_visible(self.lease, offer)
        self._active()

    def finish(self, *, next_pressed=False):
        self._active()
        if not self.window.dismiss(next_pressed=next_pressed):
            return False
        self._dismiss_pending = True
        if self.card is not None:
            self.card.retire()  # Immediate wipe, never waits for backend/printer.
        return True

    def poll(self):
        self._active()
        if self.window.active and self.window.remaining() == 0:
            self.finish()
        return self.window.remaining()

    def dismiss(self):
        self._active()
        if not self._dismiss_pending or self._offer is None:
            raise DraftHeld('Original visible NEXT/timeout required')
        self.client.dismiss(self.lease, self._offer)
        self.hide_private()

    def hide_private(self):
        self._hidden.set()
        self.window.retire()
        if self.card is not None:
            self.card.retire()
        self.client.hide_private()
        self._offer = self._qr = self._rendered_offer = None
