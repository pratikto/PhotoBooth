"""Pure UI routing for the portrait kiosk.

Navigation never grants discounts, payments or receipt claims. P3 photo pages
are admitted separately by the nonfinancial test service; active photo work is
protected from generic idle returns.
"""

from dataclasses import dataclass

ADVERT = "advert"
TUTORIAL = "tutorial"
TEMPLATES = "templates"
GAME_PREVIEW = "game_preview"
PHOTO_CONFIRM = 'photo_confirm'
CAPTURE = 'capture'
REVIEW = 'review'
RESULT = 'result'
PHOTO_PAGES = frozenset({PHOTO_CONFIRM, CAPTURE, REVIEW, RESULT})
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

        An active photo test must finish through its service before this reset.
        Future production admission must still enforce independent paid-order guards.
        """
        if self.page in {CAPTURE, REVIEW, RESULT}:
            raise NavigationError('An active photo test must finish safely first.')
        self.page = ADVERT
        self.tutorial_seen = False
        self.entry_source = None
        return self.page

    def confirm_photo_test(self):
        if self.page != TEMPLATES or not self.tutorial_seen:
            raise NavigationError('Complete the tutorial and choose templates first.')
        self.page = PHOTO_CONFIRM

    def photo_step(self, phase):
        if self.page not in PHOTO_PAGES or phase not in {CAPTURE, REVIEW, RESULT, 'done'}:
            raise NavigationError('Invalid photo-test navigation.')
        self.page = phase if phase != 'done' else PHOTO_CONFIRM

    def browse_timeout(self) -> bool:
        """Only browsing screens can expire; never a hypothetical paid page."""
        if self.page not in BROWSING_PAGES:
            return False
        self.to_advertising()
        return True
