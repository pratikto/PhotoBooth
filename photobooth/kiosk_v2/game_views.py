"""Mount the latest original Meong Fly UI; retain v2 navigation/storage guards."""

from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from photobooth.advertising import PROJECT_ROOT
from .demo_game import DemoGameStore, GameJobs
from .flow import GAME_PREVIEW, GAME_RECEIPT, GAME_PLAY, GAME_RESULT
from .game_scene import KioskGameStage, KioskGameFlow
from .theme import text_label, GOLD

GAME_HOST_PAGES = {GAME_PREVIEW, GAME_RECEIPT, GAME_PLAY, GAME_RESULT}


class GameViews:
    def _init_game(self):
        self._game_jobs = self._provided_game_jobs or GameJobs(
            lambda: DemoGameStore(PROJECT_ROOT/'data'/'kiosk-v2-p4'))
        self._game_attempt = self._game_result = self._game_engine = None
        self._game_field = self._reference_stage = self._reference_flow = None
        self._game_paused = False
        self._game_error = ''
        self._game_footer = None

    def _open_game_demo(self):
        if self._reference_flow.open_scan():
            self.navigation.open_game_receipt()
            self._game_error = ''
            self._activity()
            self._show()

    def _claim_game_demo(self):
        if self.navigation.page != GAME_RECEIPT or self._game_jobs.busy:
            return
        if self._game_jobs.submit('claim', self._view_revision, self._demo_code.text):
            self._demo_code.disabled = True
            self._demo_code.focus = False
            if self._game_footer is not None:self._game_footer.disabled = True
            self._game_message.text = 'Memeriksa kode DEMO…'
            self._game_field._refresh()

    def _poll_game(self):
        if self._closed or self._suspended:
            return
        outcome = self._game_jobs.poll()
        if outcome is None or outcome.revision != self._view_revision:
            return
        if outcome.action == 'claim' and self.navigation.page == GAME_RECEIPT:
            if outcome.error:
                self._game_error = {'invalid':'Gunakan kode DEMO- diikuti huruf/angka.',
                                    'used':'Kode DEMO sudah dipakai. Tidak ada kesempatan ulang.'}.get(
                                        outcome.error, 'Penyimpanan belum siap. Game belum dimulai.')
                if self._game_footer is not None:self._game_footer.disabled = False
                self._game_field._refresh()
                return
            self._game_attempt, self._game_result = outcome.value, None
            self._game_error = ''
            # Run original claim/start only after v2 has persisted the claim.
            # The bridge ledger checks that exact acknowledged token in memory.
            if not self._reference_flow.claim_and_start(outcome.value['token']):
                raise RuntimeError('Acknowledged DEMO claim could not start the original game.')
            self._game_engine = self._reference_flow.game
            self._game_paused = False
            self.navigation.start_game()
            self._show()
        elif outcome.action == 'finish' and self.navigation.page == GAME_PLAY:
            self._game_result = outcome.value if not outcome.error else None
            self._game_error = '' if not outcome.error else 'Hasil belum tersimpan; lanjut foto tanpa potensi promo.'
            self._reference_flow.screen = ('won' if self._game_result and self._game_result['result']=='won' else 'lost')
            self.navigation.finish_game()
            self._show()

    def _flap_game(self):
        if self.navigation.page == GAME_PLAY and self._reference_flow is not None:
            self._reference_flow.flap()

    def _game_tick(self, dt):
        # Only the original Stage update / Flow tick drives the round. There is
        # no second v2 game clock or independently implemented draw/physics loop.
        if self._game_field is not None:
            self._game_field.update(dt)

    def _finish_game_demo(self, result='abandoned'):
        if self.navigation.page != GAME_PLAY or self._game_jobs.busy:
            return
        if self._game_jobs.submit('finish', self._view_revision, self._game_attempt['attempt_id'],
                                  result, self._game_engine.score):
            if self._game_footer is not None:self._game_footer.disabled = True
            self._game_busy_label.text = 'Menyimpan hasil DEMO…'
            self._game_field.receipt.disabled = True

    def _toggle_game_pause(self):
        if self._game_jobs.busy or self.navigation.page != GAME_PLAY:
            return
        if self._reference_flow.toggle_pause():
            self._game_paused = self._reference_flow.paused
            self._game_field._refresh()

    def _pause_game(self):
        if self.navigation.page == GAME_PLAY and not self._game_paused:
            self._toggle_game_pause()

    def _continue_game_photo(self):
        if self._game_jobs.busy:
            return
        self._reference_flow.tutorial_seen = self.navigation.tutorial_seen
        self._reference_flow.continue_from_result()
        self.navigation.continue_game_photo()
        self._activity()
        self._show()

    def _retire_game_field(self):
        field, self._game_field = self._game_field, None
        if field is None:
            return
        if not self._closed and self.navigation.page in GAME_HOST_PAGES:
            field.detach()  # Preserve original paper/effect state across game pages.
        else:
            field.dispose()
            self._reference_stage = self._reference_flow = None

    def _build_game_page(self, canvas):
        shell = BoxLayout(orientation='vertical', spacing=0, padding=0)
        canvas.add_widget(shell)
        if self._reference_stage is None:
            self._reference_flow = KioskGameFlow(self)
            self._reference_stage = KioskGameStage(self, self._reference_flow)
        field = self._game_field = self._reference_stage
        shell.add_widget(field)
        self._demo_code = field.receipt
        self._game_message = field.notice
        self._game_busy_label = text_label(self._game_error, size=13, height=0, color=GOLD)
        self._game_busy_label.bind(text=lambda label,text:setattr(label,'height',dp(32) if text else 0))
        if self._game_error:self._game_busy_label.height=dp(32)
        shell.add_widget(self._game_busy_label)
        playing = self.navigation.page == GAME_PLAY
        self._game_footer = None
        if playing:
            self._game_footer = self._action('AKHIRI GAME • TANPA MAIN ULANG',
                self._finish_game_demo, variant='tertiary', height=48, disabled=self._game_jobs.busy)
            shell.add_widget(self._game_footer)
        field.mount()

    def _back_game_intro(self):
        if self._game_jobs.busy:
            return
        if self.navigation.page == GAME_RECEIPT and self._reference_flow.back():
            self.navigation.page = GAME_PREVIEW
            self._game_error = ''
            self._show()
