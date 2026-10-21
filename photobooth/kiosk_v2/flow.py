"""Pure UI routing for the portrait kiosk.

This module owns only navigation for the unconnected prototype. It deliberately
cannot grant discounts, accept payments, claim receipts or start a photo session.
All future paid/capture states must be introduced behind validated backends.
"""

from dataclasses import dataclass

ADVERT = "advert"
TUTORIAL = "tutorial"
TEMPLATES = "templates"
GAME_PREVIEW = "game_preview"
BROWSING_PAGES = frozenset({TUTORIAL, TEMPLATES, GAME_PREVIEW})


class NavigationError(ValueError):
    """Invalid or stale touch event must not mutate the current visitor."""


@dataclass
class VisitFlow:
    """A tutorial is completed at most once during one active visitor's visit.

    Returning to advertising ends the current visit, even on timeout. The
    one-receipt-one-attempt ledger will be independent of this transient UI
    state when a real mini-game integration is separately approved.
    """

    page: str = ADVERT
    tutorial_seen: bool = False
    entry_source: str | None = None

    def begin_photo(self, source: str = "manual") -> str:
        if self.page not in (ADVERT, GAME_PREVIEW):
            raise NavigationError("Photo entry is only available from advertising or game demo.")
        self.entry_source = source
        self.page = TEMPLATES if self.tutorial_seen else TUTORIAL
        return self.page

    def begin_game_preview(self, source: str = "manual") -> str:
        if self.page != ADVERT:
            raise NavigationError("Meong Fly entry belongs to the idle advertising screen.")
        self.entry_source = source
        # There is no real game, receipt scanner or discount bridge on this branch.
        self.page = GAME_PREVIEW
        return self.page

    def complete_tutorial(self) -> str:
        if self.page != TUTORIAL:
            raise NavigationError("A tutorial is marked seen only upon completion.")
        self.tutorial_seen = True
        self.page = TEMPLATES
        return self.page

    def to_advertising(self) -> str:
        """Discard uncommitted visitor UI state for the next visitor.

        This prototype cannot enter payment/capture/printing. Production
        integration will have to enforce the existing paid-order guards.
        """
        self.page = ADVERT
        self.tutorial_seen = False
        self.entry_source = None
        return self.page

    def browse_timeout(self) -> bool:
        """Only browsing screens can expire; never a hypothetical paid page."""
        if self.page not in BROWSING_PAGES:
            return False
        self.to_advertising()
        return True
