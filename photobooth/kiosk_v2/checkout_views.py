"""Opt-in, explicitly nonpayable local MOCK checkout widgets."""

import os
import time
import uuid

from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from photobooth.advertising import PROJECT_ROOT
from .demo_game import GameJobs
from .flow import MOCK_CHECKOUT, TEMPLATES
from .mock_checkout import configured_mock_checkout
from .theme import PixelCard, text_label, GOLD, CYAN, MUTED


class CheckoutViews:
    def _init_checkout(self):
        self._mock_enabled = os.environ.get('PHOTOBOOTH_V2_CHECKOUT_MOCK', '0') == '1'
        self._mock_jobs = self._provided_checkout_jobs or GameJobs(
            lambda: configured_mock_checkout(PROJECT_ROOT/'data'/'kiosk-v2-p4', configuration_root=PROJECT_ROOT),
            actions={'open_checkout', 'status', 'transition', 'admit'})
        self._mock_view = None
        self._mock_error = ''
        self._mock_key = None
        self._mock_skip_promo = False
        self._mock_refresh_at = 0

    def _open_mock_checkout(self):
        if (not self._mock_enabled or self.navigation.page != TEMPLATES or
                not any(self.quantities.values()) or self._mock_jobs.busy):
            return
        self.navigation.open_mock_checkout()
        self._mock_view = None
        self._mock_error = ''
        self._mock_key = uuid.uuid4().hex
        self._mock_skip_promo = False
        self._show()
        self._retry_mock_open()

    def _retry_mock_open(self):
        attempt = self._game_result.get('attempt_id') if self._game_result and not self._mock_skip_promo else None
        self._mock_submit('open_checkout', dict(self.quantities), self._mock_key, attempt)

    def _mock_without_promo(self):
        if self._mock_view or self._mock_jobs.busy:
            return
        self._mock_skip_promo = True
        self._mock_key = uuid.uuid4().hex
        self._retry_mock_open()

    def _mock_submit(self, action, *args):
        if self._closed or self._suspended or self.navigation.page != MOCK_CHECKOUT:
            return
        if self._mock_jobs.submit(action, self._view_revision, *args):
            self._mock_error = ''
            self._mock_message.text = 'Memeriksa catatan MOCK…'
            for button in self._mock_controls:
                button.disabled = True

    def _mock_status(self):
        if self._mock_view:
            self._mock_submit('status', self._mock_view['order_id'])
        else:
            self._retry_mock_open()

    def _mock_transition(self, action):
        if self._mock_view:
            self._mock_submit('transition', self._mock_view['order_id'], action)

    def _mock_admit(self):
        if self._mock_view and self._mock_view['state'] == 'CONFIRMED':
            self._mock_submit('admit', self._mock_view['order_id'])

    def _mock_leave(self):
        if self._mock_jobs.busy or not self._mock_view or self._mock_view['state'] not in {'CANCELLED', 'EXPIRED', 'ADMITTED'}:
            return
        self.navigation.leave_mock_checkout()
        self._show()

    def _poll_checkout(self):
        if self._closed or self._suspended:
            return
        outcome = self._mock_jobs.poll()
        if outcome is not None:
            if outcome.revision != self._view_revision or self.navigation.page != MOCK_CHECKOUT:
                return
            if outcome.error:
                if outcome.error == 'promo-used':
                    self._game_discount_used = True
                self._mock_error = {
                    'promo-used': 'Potensi promo DEMO sudah dipakai pada pesanan sebelumnya.',
                    'unresolved': 'Status belum pasti. Selesaikan simulasi atau periksa status dahulu.',
                    'not-admissible': 'Izin MOCK belum tersedia atau sudah pernah digunakan.',
                    'printer-not-ready': 'Koneksi printer belum terkonfirmasi. Periksa printer lalu coba lagi.',
                }.get(outcome.error, 'Belum berhasil. Periksa status MOCK; belum ada izin foto baru.')
            else:
                self._mock_view = outcome.value
                if (self._mock_view['state'] == 'ADMITTED' and self._mock_view['discount'] and
                        self._game_result and self._mock_view['attempt_id'] == self._game_result.get('attempt_id')):
                    self._game_discount_used = True
                self._mock_error = ('Pesanan MOCK aktif dipulihkan; pilihan tersimpan digunakan.'
                                    if self._mock_view['request_key'] != self._mock_key else '')
                if outcome.action == 'admit' and self._mock_view['state'] == 'ADMITTED':
                    # Freeze the backend cart, not any later client selection.
                    cart = self._mock_view['quantities']
                    self.quantities = {t.template_id:cart.get(t.template_id, 0) for t in self.templates}
                    self.navigation.leave_mock_checkout()
                    self._enter_photo_test()  # Existing explicit nonfinancial consent, no auto capture.
                    return
            self._mock_refresh_at = time.monotonic()+2
            self._show()
        if (self.navigation.page == MOCK_CHECKOUT and self._mock_view and
                self._mock_view['state'] == 'PENDING' and not self._mock_jobs.busy):
            remaining = max(0, int(self._mock_view['expires']-time.time()))
            self._mock_timer.text = f'Simulasi kedaluwarsa dalam {remaining} detik'
            if remaining == 0 and time.monotonic() >= self._mock_refresh_at:
                self._mock_status()

    def _build_mock_checkout(self, canvas):
        shell = self._frame(canvas, brand_height=48)
        shell.spacing = dp(8)
        self._brand(shell, 'CHECKOUT MOCK', 'SIMULASI LOKAL • JANGAN DIBAYAR')
        card = self._mock_card = PixelCard(orientation='vertical', padding=10, spacing=6)
        view = self._mock_view
        state = view['state'] if view else 'LOADING'
        if state != 'PENDING':
            card.add_widget(Widget())
        if view:
            money = lambda value: 'Rp'+f'{value:,}'.replace(',', '.')
            card.add_widget(text_label(money(view['total']), size=30, height=46, color=GOLD, bold=True))
            card.add_widget(text_label(
                f"Subtotal {money(view['subtotal'])} • MOCK −{money(view['discount'])}\n"
                f"{len(view['quantities'])} desain • {sum(view['quantities'].values())} lembar",
                size=16, height=60, color=CYAN))
            if state == 'PENDING' and view.get('qr_rgb'):
                size, pixels = view['qr_rgb']
                texture = Texture.create(size=size, colorfmt='rgb')
                texture.blit_buffer(pixels, colorfmt='rgb', bufferfmt='ubyte')
                texture.flip_vertical()
                texture.mag_filter = texture.min_filter = 'nearest'
                self._mock_qr = Image(texture=texture, fit_mode='contain')
                card.add_widget(self._mock_qr)
            titles = {'PENDING':'QR MOCK • BUKAN QRIS', 'UNKNOWN':'STATUS BELUM PASTI',
                      'CONFIRMED':'SIMULASI DIKONFIRMASI', 'CANCELLED':'MOCK DIBATALKAN',
                      'EXPIRED':'MOCK KEDALUWARSA', 'ADMITTED':'IZIN MOCK SUDAH DIPAKAI'}
            card.add_widget(text_label(titles[state], size=18, height=36, color=GOLD, bold=True))
            card.add_widget(text_label('Pesanan '+view['order_id'][:8]+' • '+view['mode'],
                                      size=13, height=24, color=MUTED))
        self._mock_timer = text_label('', size=13, height=26, color=CYAN)
        card.add_widget(self._mock_timer)
        card.add_widget(text_label(
            'QR ini bukan pembayaran bank.\n'
            'Tidak ada tagihan atau diskon nyata.', size=14, height=54, color=MUTED))
        if state != 'PENDING':
            card.add_widget(Widget())
        shell.add_widget(card)
        self._mock_message = text_label(self._mock_error, size=13, height=40, color=GOLD)
        shell.add_widget(self._mock_message)
        self._mock_controls = []
        def action(title, callback, variant='secondary', disabled=False, host=None):
            button = self._action(title, callback, variant=variant, height=48,
                                  disabled=disabled or self._mock_jobs.busy)
            self._mock_controls.append(button)
            (shell if host is None else host).add_widget(button)
        if state in {'PENDING', 'UNKNOWN'}:
            action('SIMULASI KONFIRMASI • MOCK', lambda:self._mock_transition('confirm'))
            if state == 'PENDING':
                tools = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
                shell.add_widget(tools)
                action('SIMULASI BELUM PASTI', lambda:self._mock_transition('unknown'), 'tertiary', host=tools)
                action('CEK STATUS MOCK', self._mock_status, 'tertiary', host=tools)
                for button in self._mock_controls[-2:]:
                    button.font_size = dp(12)
                action('BATALKAN MOCK', lambda:self._mock_transition('cancel'), 'tertiary')
                return
            else:
                action('SIMULASI DITOLAK • SELESAIKAN', lambda:self._mock_transition('reject'), 'tertiary')
        elif state == 'CONFIRMED':
            action('LANJUT KE PERSETUJUAN UJI FOTO', self._mock_admit, 'primary')
        elif state in {'CANCELLED', 'EXPIRED', 'ADMITTED'}:
            action('KEMBALI PILIH TEMPLATE', self._mock_leave, 'primary')
        elif state == 'LOADING' and self._mock_error:
            action('COBA MOCK TANPA POTENSI PROMO', self._mock_without_promo, 'secondary')
        action('CEK STATUS MOCK' if view else 'COBA PEMERIKSAAN LAGI', self._mock_status, 'tertiary')
