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
GAME_RECEIPT = 'game_receipt'
GAME_PLAY = 'game_play'
GAME_RESULT = 'game_result'
MOCK_CHECKOUT = 'mock_checkout'
GAME_PAGES = frozenset({GAME_RECEIPT, GAME_PLAY, GAME_RESULT})
PHOTO_CONFIRM = 'photo_confirm'
CAPTURE = 'capture'
REVIEW = 'review'
RESULT = 'result'
PHOTO_PAGES = frozenset({PHOTO_CONFIRM, CAPTURE, REVIEW, RESULT})
BROWSING_PAGES = frozenset({TUTORIAL, TEMPLATES, GAME_PREVIEW, GAME_RECEIPT, GAME_RESULT})


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
        self.page = GAME_PREVIEW
        return self.page

    def open_game_receipt(self):
        if self.page != GAME_PREVIEW:
            raise NavigationError('DEMO receipt entry requires the game intro.')
        self.page = GAME_RECEIPT

    def start_game(self):
        if self.page != GAME_RECEIPT:
            raise NavigationError('Gameplay requires a claimed DEMO attempt.')
        self.page = GAME_PLAY

    def finish_game(self):
        if self.page != GAME_PLAY:
            raise NavigationError('Only the active game may finish.')
        self.page = GAME_RESULT

    def continue_game_photo(self):
        if self.page != GAME_RESULT:
            raise NavigationError('Photo handoff requires a finished game.')
        self.entry_source = 'game_demo'
        self.page = TEMPLATES if self.tutorial_seen else TUTORIAL
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
        if self.page in {CAPTURE, REVIEW, RESULT, GAME_PLAY, MOCK_CHECKOUT}:
            raise NavigationError('An active photo test must finish safely first.')
        self.page = ADVERT
        self.tutorial_seen = False
        self.entry_source = None
        return self.page

    def confirm_photo_test(self):
        if self.page != TEMPLATES or not self.tutorial_seen:
            raise NavigationError('Complete the tutorial and choose templates first.')
        self.page = PHOTO_CONFIRM

    def open_mock_checkout(self):
        if self.page != TEMPLATES or not self.tutorial_seen:
            raise NavigationError('MOCK checkout requires the completed tutorial/gallery.')
        self.page = MOCK_CHECKOUT

    def leave_mock_checkout(self):
        # The caller must obtain terminal cancellation/expiry or one-use MOCK
        # admission from the isolated service before leaving this protected page.
        if self.page != MOCK_CHECKOUT:
            raise NavigationError('No active MOCK checkout.')
        self.page = TEMPLATES

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
