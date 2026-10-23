"""P4 DEMO pages, independent of the reference standalone App or real scanner."""

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from photobooth.advertising import PROJECT_ROOT
from .demo_game import DemoGameStore, GameJobs
from .flow import GAME_PREVIEW, GAME_RECEIPT, GAME_PLAY, GAME_RESULT
from .game_engine import MeongFly, TARGET_SCORE
from .game_scene import GameField
from .branding import CAMERA_ART
from .theme import CYAN, GOLD, MUTED, PixelCard, text_label


class GameViews:
    def _init_game(self):
        self._game_jobs = self._provided_game_jobs or GameJobs(
            lambda: DemoGameStore(PROJECT_ROOT/'data'/'kiosk-v2-p4'))
        self._game_attempt = self._game_result = self._game_engine = None
        self._game_field = self._game_event = None
        self._game_paused = False
        self._game_error = ''

    def _open_game_demo(self):
        self.navigation.open_game_receipt()
        self._game_error = ''
        self._show()

    def _claim_game_demo(self):
        if self.navigation.page != GAME_RECEIPT or self._game_jobs.busy:
            return
        if self._game_jobs.submit('claim', self._view_revision, self._demo_code.text):
            self._demo_start.disabled = True
            self._demo_back.disabled = True
            self._demo_code.disabled = True
            self._demo_code.focus = False
            self._game_message.text = 'Memeriksa kode DEMO…'

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
                self._demo_start.disabled = self._demo_code.disabled = False
                self._demo_back.disabled = False
                self._game_message.text = self._game_error
                return
            self._game_attempt, self._game_result = outcome.value, None
            self._game_engine = MeongFly()
            self._game_paused = False
            self.navigation.start_game()
            self._show()
        elif outcome.action == 'finish' and self.navigation.page == GAME_PLAY:
            self._game_result = outcome.value if not outcome.error else None
            self._game_error = '' if not outcome.error else 'Hasil belum tersimpan; lanjut foto tanpa potensi promo.'
            self.navigation.finish_game()
            self._show()

    def _flap_game(self):
        if (self.navigation.page != GAME_PLAY or self._suspended or self._closed or
                self._game_paused or self._game_jobs.busy):
            return
        if self._game_engine.status == 'ready':
            self._game_engine.start()
        elif self._game_engine.status == 'playing':
            self._game_engine.flap()
        else:
            return
        self.audio_v2.cue('button')

    def _game_tick(self, dt):
        if self._closed or self.navigation.page != GAME_PLAY:
            return False
        if self._suspended or self._game_paused or self._game_jobs.busy:
            return
        self._game_engine.step(dt)
        self._game_field.draw()
        self._game_score.text = f'{self._game_engine.score:02d} / {TARGET_SCORE:02d} POIN'
        self._game_message.text = ('TAP AREA GAME UNTUK MULAI' if self._game_engine.status == 'ready'
                                   else 'TAP UNTUK TERBANG • HINDARI ASTEROID')
        if self._game_engine.status in {'won', 'lost'}:
            self._finish_game_demo(self._game_engine.status)

    def _finish_game_demo(self, result='abandoned'):
        if self.navigation.page != GAME_PLAY or self._game_jobs.busy:
            return
        if self._game_jobs.submit('finish', self._view_revision, self._game_attempt['attempt_id'],
                                  result, self._game_engine.score):
            self._game_message.text = 'Menyimpan hasil DEMO…'
            self._game_pause_button.disabled = self._game_exit_button.disabled = True

    def _toggle_game_pause(self):
        if self._game_jobs.busy:
            return
        self._game_paused = not self._game_paused
        self._game_pause_button.text = 'LANJUT MAIN' if self._game_paused else 'JEDA'
        self._game_message.text = 'GAME DIJEDA' if self._game_paused else 'TAP UNTUK TERBANG'

    def _pause_game(self):
        if self.navigation.page == GAME_PLAY and not self._game_paused:
            self._toggle_game_pause()

    def _continue_game_photo(self):
        self.navigation.continue_game_photo()
        self._activity()
        self._show()

    def _retire_game_field(self):
        if self._game_field is not None:
            self._game_field.dispose()
            self._game_field = None
        if self._game_event is not None:
            self._game_event.cancel()
            self._game_event = None

    def _build_game_page(self, canvas):
        shell = self._frame(canvas, brand_height=65)
        page = self.navigation.page
        self._brand(shell, {GAME_RECEIPT:'KODE STRUK DEMO', GAME_PLAY:'MEONG FLY!',
                            GAME_RESULT:'HASIL MEONG FLY'}[page], 'MODE DEMO • TANPA DISKON NYATA')
        if page == GAME_RECEIPT:
            card = PixelCard(orientation='vertical', padding=16, spacing=12)
            card.add_widget(Widget())
            card.add_widget(text_label('SATU KODE • SATU KESEMPATAN', size=20, height=60, color=GOLD, bold=True))
            card.add_widget(text_label('Ketik kode uji dengan awalan DEMO-.\nContoh: DEMO-COBA-001\n\n'
                                      'Ini bukan validasi struk kafe.\nKamera scanner produksi tetap nonaktif.',
                                      size=16, height=160, color=MUTED))
            self._demo_code = TextInput(multiline=False, hint_text='DEMO-COBA-001',
                                        size_hint_y=None, height=dp(60), font_size=dp(20), write_tab=False)
            card.add_widget(self._demo_code)
            card.add_widget(Widget())
            shell.add_widget(card)
            self._game_message = text_label(self._game_error, size=14, height=65, color=GOLD)
            shell.add_widget(self._game_message)
            self._demo_start = self._action('VALIDASI KODE & MAIN DEMO', self._claim_game_demo,
                                            disabled=self._game_jobs.busy)
            shell.add_widget(self._demo_start)
            self._demo_back = self._action('KEMBALI KE PENGANTAR', self._back_game_intro,
                                           variant='tertiary', height=48)
            shell.add_widget(self._demo_back)
        elif page == GAME_PLAY:
            self._game_score = text_label('00 / 10 POIN', size=24, height=45, color=GOLD, bold=True)
            shell.add_widget(self._game_score)
            card = PixelCard(orientation='vertical', padding=8)
            self._game_field = GameField(self._game_engine, self._page_callback(self._flap_game))
            card.add_widget(self._game_field)
            shell.add_widget(card)
            self._game_message = text_label('TAP AREA GAME UNTUK MULAI', size=14, height=60, color=CYAN)
            shell.add_widget(self._game_message)
            self._game_pause_button = self._action('LANJUT MAIN' if self._game_paused else 'JEDA',
                                                    self._toggle_game_pause, variant='secondary', height=52)
            shell.add_widget(self._game_pause_button)
            self._game_exit_button = self._action('AKHIRI GAME • TANPA MAIN ULANG', self._finish_game_demo,
                                                   variant='tertiary', height=48)
            shell.add_widget(self._game_exit_button)
            self._game_event = Clock.schedule_interval(self._game_tick, 1/60)
        else:
            won = bool(self._game_result and self._game_result['result'] == 'won')
            card = PixelCard(orientation='vertical', padding=14, spacing=10)
            card.add_widget(Widget())
            card.add_widget(Image(source=str(CAMERA_ART), fit_mode='contain', size_hint_y=None, height=dp(110)))
            card.add_widget(text_label('MEONG MENANG!' if won else 'TERIMA KASIH SUDAH MAIN!',
                                      size=26, height=65, color=GOLD, bold=True))
            card.add_widget(text_label(f'SKOR {self._game_engine.score} / {TARGET_SCORE}',
                                      size=23, height=50, color=CYAN))
            card.add_widget(text_label('Potensi promo simulasi Rp2.500' if won else 'Tanpa potongan harga',
                                      size=19, height=50, color=GOLD))
            card.add_widget(text_label(self._game_error or 'Kode sudah dipakai, tidak ada MAIN LAGI.\n'
                                      'Lanjut ke tutorial dan galeri foto.\nPromo nyata belum aktif.',
                                      size=15, height=110, color=MUTED))
            card.add_widget(Widget())
            shell.add_widget(card)
            shell.add_widget(self._action('LANJUT PILIH TEMPLATE', self._continue_game_photo))
            shell.add_widget(self._action('SELESAI / KEMBALI IKLAN', self._return_ad,
                                          variant='tertiary', height=48))

    def _back_game_intro(self):
        if self._game_jobs.busy:
            return
        if self.navigation.page == GAME_RECEIPT:
            self.navigation.page = GAME_PREVIEW
            self._show()
