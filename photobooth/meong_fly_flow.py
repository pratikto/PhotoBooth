"""Kivy-independent state machine for the isolated FEAT-021 demo.

The only receipt accepted is a DEMO-* token. Never treat a demo outcome as a
redeemable discount or a payment transaction.
"""

from .meong_fly import MeongFly


class MeongFlyFlow:
    """Five-screen navigation with a single irreversible receipt claim."""

    def __init__(self, ledger, game=None, tutorial_seen=False):
        self.ledger = ledger
        self.game = game if game is not None else MeongFly()
        self.screen = "start"
        self.active_receipt = None
        self.result_recorded = False
        self.paused = False
        self.message = ""
        self.tutorial_seen = bool(tutorial_seen)
        self.photo_outcome = None  # in-memory handoff only, never a real discount

    @property
    def can_play(self):
        return self.active_receipt is None

    def open_scan(self):
        if self.screen != "start" or not self.can_play:
            return False
        self.screen = "scan"
        self.message = ""
        return True

    def back(self):
        """Only an unclaimed receipt-entry screen may navigate back."""
        if self.screen != "scan" or not self.can_play:
            return False
        self.screen = "start"
        self.message = ""
        return True

    def claim_and_start(self, entered_code):
        """Consume the demo code BEFORE starting gameplay (fail closed)."""
        if self.screen != "scan" or not self.can_play:
            return False
        code = entered_code.strip()
        if not code.startswith("DEMO-") or not code[5:] or len(code) > 100:
            self.message = "Gunakan kode demo: DEMO-123"
            return False
        if not self.ledger.claim(code):
            self.message = "Kode tidak valid / sudah digunakan."
            return False
        self.active_receipt = code
        self.result_recorded = False
        self.paused = False
        self.game.start()
        self.screen = "game"
        self.message = ""
        return True

    def flap(self):
        if self.screen != "game" or self.paused:
            return False
        self.game.flap()
        return True

    def toggle_pause(self):
        if self.screen != "game":
            return False
        self.paused = not self.paused
        return True

    def tick(self, dt):
        """Advance only the running game; persist exactly one terminal result."""
        if self.screen != "game" or self.paused:
            return
        self.game.step(dt)
        if self.game.status not in ("won", "lost"):
            return
        if not self.result_recorded:
            self.ledger.finish(self.active_receipt, self.game.status == "won")
            self.result_recorded = True
        self.screen = self.game.status

    def _route_to_photo(self):
        """Route to required one-time tutorial, then standalone layout preview.

        The production tutorial/template selector is deliberately not imported
        into this isolated demo. Its integration requires separate approval.
        """
        self.screen = "layouts" if self.tutorial_seen else "tutorial"
        return True

    def finish_tutorial(self):
        if self.screen != "tutorial":
            return False
        self.tutorial_seen = True
        self.screen = "layouts"
        return True

    def select_layout(self, layout_id):
        """Record the desired demo layout, without launching a photo session."""
        if self.screen != "layouts":
            return False
        if not isinstance(layout_id, int) or not 1 <= layout_id <= 12:
            return False
        self.selected_layout = layout_id
        self.screen = "exit"
        return True

    def continue_from_result(self):
        """Win/loss -> tutorial (if unseen) -> layout selector, never payment."""
        if self.screen not in ("won", "lost"):
            return False
        self.photo_outcome = {
            "won": self.screen == "won",
            "demo_discount_idr": 2500 if self.screen == "won" else 0,
            "receipt_demo": self.active_receipt,
        }
        return self._route_to_photo()

    def direct_photo(self):
        """Skip mini-game; tutorial gate still applies before layout selection."""
        if self.screen != "start" or not self.can_play:
            return False
        self.photo_outcome = {
            "won": False,
            "demo_discount_idr": 0,
            "receipt_demo": None,
        }
        return self._route_to_photo()
