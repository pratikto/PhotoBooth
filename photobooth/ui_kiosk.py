"""Advertising, inactivity and payment presentation for the Kivy kiosk.

All offers are ordinary widgets inside the existing window. Payment offers
belong exclusively to the advertising column; the payment QR and its controls
remain visible and usable. Fifteen seconds applies to unanswered offers only,
never to an accepted print job or to the payment's validity period.
"""

import os
from pathlib import Path
import time

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from PIL import Image

from photobooth.advertising import AdCatalog, AdEventLog
from photobooth.payment import DemoPaymentGateway, PaymentCoordinator
from photobooth.qris_print import QrisPrinterWorker
from photobooth.qr_code import create_qr_image
from photobooth.ui_ads import AdvertisementPlayer
from photobooth.ui_brand import BLUE, GREY, INK, SOFT, WHITE, Panel


class KioskExperienceMixin:
    """Keep media and payment lifetimes explicit while retaining existing UI API."""

    def _init_kiosk(self, data_dir=None):
        directory = Path(data_dir or Path(__file__).resolve().parent.parent / 'data')
        self.ad_catalog = AdCatalog()
        self.kiosk_timing = self.ad_catalog.timing
        self.ad_events = AdEventLog(directory / 'advertising' / 'events.jsonl')
        self.payment = PaymentCoordinator(DemoPaymentGateway(self.kiosk_timing.payment_validity))
        # Payment QR receipts and photo strips share the operator's saved
        # LAN/Wi-Fi/Windows USB printer configuration. The callable is evaluated
        # for each job so changes in Settings apply without restarting.
        self.qris_printer = QrisPrinterWorker(
            directory / 'qris-spool',
            printer_config_provider=self.callbacks.get('get_printer_config'),
        )
        self._ad_player = self._ad_stage = None
        self._inline_offer = self._offer_host = self._offer_fit = None
        self._offer_deadline = self._offer_kind = None
        self._enlarged = None
        self._last_activity = time.monotonic()
        self._media_paused = False
        self._payment_offered = set()
        self._last_payment_state = None
        self._kiosk_event = Clock.schedule_interval(self._kiosk_tick, .25)
        Window.bind(on_touch_down=self._kiosk_activity, on_touch_move=self._kiosk_activity,
                    on_key_down=self._kiosk_activity)

    def _kiosk_activity(self, *_args):
        """Only real interaction resets landing inactivity; camera presence does not."""
        self._last_activity = time.monotonic()
        if self._offer_kind == 'idle-warning':
            self._close_inline_offer()
        return False

    def _dispose_kiosk(self):
        self._kiosk_event.cancel()
        Window.unbind(on_touch_down=self._kiosk_activity, on_touch_move=self._kiosk_activity,
                      on_key_down=self._kiosk_activity)
        self._retire_kiosk_page()
        self.qris_printer.close()

    def _retire_kiosk_page(self):
        """Unload video and remove every overlay before advancing the page revision."""
        self._close_inline_offer()
        self._close_enlargement(resume=False)
        if self._ad_player is not None:
            self._ad_player.close()
            self._ad_player = None
        self._ad_stage = None
        self._last_activity = time.monotonic()

    def pause_media(self):
        """Native backgrounding silences both independent audio owners."""
        self._media_paused = True
        self.audio.pause()
        if self._ad_player is not None:
            self._ad_player.pause()

    def resume_media(self):
        self._media_paused = False
        self.audio.resume()
        if self._ad_player is not None and self._enlarged is None:
            self._ad_player.resume()

    def _advert_volume(self):
        if os.environ.get('PHOTOBOOTH_AUDIO', '1').lower() in {'0', 'false', 'no'}:
            return 0
        return self.audio.levels.ads * (.35 if self._offer_kind == 'face' else 1)

    def _update_ad_volume(self):
        if self._ad_player is not None:
            self._ad_player.set_volume(self._advert_volume())

    def _add_advertisement(self, stage, placement):
        self._ad_stage = stage
        self._ad_player = AdvertisementPlayer(self.ad_catalog, placement, self.ad_events,
                                               self._advert_volume(), pos_hint={'x': 0, 'y': 0})
        stage.add_widget(self._ad_player)

    def show_advertisement(self, camera_ready=None, status_message=''):
        """Start with media; face detection invites, while manual entry stays available."""
        if self.current_screen == 'payment' and not self.payment.release():
            self.set_status('Periksa status pembayaran sebelum meninggalkan halaman ini.')
            return False
        if camera_ready is not None:
            self.set_camera_status(camera_ready)
        page = self._reset('advert', '')
        # Operators can edit a JSON playlist between customers without a code
        # change. A new idle placement picks up those changes, including timers.
        self.ad_catalog = AdCatalog(self.ad_catalog.path)
        self.kiosk_timing = self.ad_catalog.timing
        stage = FloatLayout()
        self._add_advertisement(stage, 'idle')
        page.add_widget(stage)
        self.advert_start_button = self._button('MULAI FOTO', lambda: self._enter_from_ad('manual'))
        self._attach_icon(self.advert_start_button, 'camera')
        guide = self._button('CARA PAKAI', lambda: self.show_welcome(
            self._camera_ready, 'Pilih frame, bayar, lalu abadikan senyummu.'), secondary=True)
        guide.size_hint_x = .4
        page.add_widget(self._actions(guide, self.advert_start_button))
        self.set_status(status_message)
        return True

    def _enter_from_ad(self, source):
        """Attribute a successful entry, never treat a face detection as a view/person."""
        if self.current_screen != 'advert':
            return
        ad_id = self._ad_player.ad_id if self._ad_player else 'meong-fallback'
        # Both the manual action and the face invitation first open the visual
        # guide. The guide's own Start button advances to the layout picker.
        # Calling the controller here previously skipped the tutorial entirely.
        self.show_welcome(self._camera_ready, 'Ikuti langkah mudah ini sebelum memilih layout.')
        if self.current_screen == 'welcome':
            self.ad_events.write('photo_entry', ad_id=ad_id, placement='idle', source=source)

    def show_face_invitation(self):
        if (self.current_screen != 'advert' or self._inline_offer is not None
                or self.audio_settings_open):
            return False
        self._show_inline_offer(self._ad_stage, 'face', 'Mau berfoto?',
                                'Pilih frame favoritmu dan buat kenangan baru.',
                                'AYO FOTO', lambda: self._enter_from_ad('face_prompt'))
        self._update_ad_volume()
        return True

    def _show_inline_offer(self, host, kind, title, message, action_text, action,
                           *, timeout=True, secondary='NANTI SAJA'):
        """A nonmodal card stays inside its host; payment host excludes the QR column."""
        self._close_inline_offer()
        card = Panel(fill=WHITE, orientation='vertical', padding=dp(14), spacing=dp(5),
                     size_hint=(None, None), height=dp(174), pos_hint={'x': .02, 'y': .03})
        card.add_widget(self._label(title, 21, 30, bold=True))
        self.offer_message = self._label(message, 13, 45, color=GREY)
        card.add_widget(self.offer_message)
        def still_open(callback):
            # A queued touch release from a timed-out/replaced card cannot
            # start a session or submit a later customer's print job.
            if self._inline_offer is card and card.parent is host:
                callback()
        self.offer_action = self._button(action_text, lambda: still_open(action))
        self.offer_dismiss = self._button(secondary, lambda: still_open(self._close_inline_offer), secondary=True)
        for button in (self.offer_action, self.offer_dismiss):
            button.height = dp(40)
            button.font_size = dp(12)
        actions = self._actions(self.offer_dismiss, self.offer_action)
        actions.height = dp(40)
        card.add_widget(actions)
        self.offer_countdown = self._label('', 10, 14, color=GREY, align='right')
        card.add_widget(self.offer_countdown)
        def fit(*_args):
            card.width = max(1, min(dp(460), host.width - dp(16)))
        host.bind(size=fit)
        fit()
        host.add_widget(card)
        self._inline_offer, self._offer_host, self._offer_fit = card, host, fit
        self._offer_kind = kind
        self._offer_deadline = time.monotonic() + self.kiosk_timing.offer_timeout if timeout else None
        return card

    def _close_inline_offer(self):
        if self._offer_host is not None:
            self._offer_host.unbind(size=self._offer_fit)
            if self._inline_offer.parent is self._offer_host:
                self._offer_host.remove_widget(self._inline_offer)
        self._inline_offer = self._offer_host = self._offer_fit = None
        self._offer_deadline = self._offer_kind = None
        self._update_ad_volume()

    def _kiosk_tick(self, _dt=0):
        if self._disposed:
            return False
        if self._media_paused:
            return
        now = time.monotonic()
        if self._offer_deadline is not None:
            remaining = self._offer_deadline - now
            if remaining <= 0:
                self._close_inline_offer()
            else:
                self.offer_countdown.text = f'Tutup otomatis dalam {int(remaining) + 1} dtk'
        if self.current_screen in {'welcome', 'templates'}:
            inactive = now - self._last_activity
            limit = self.kiosk_timing.landing_idle
            if inactive >= limit:
                callback = self.callbacks.get('on_idle')
                if callback is not None:
                    callback()
                else:
                    self.show_advertisement()
            elif inactive >= max(0, limit - self.kiosk_timing.idle_warning) and self._inline_offer is None:
                self._show_inline_offer(self._page_stack, 'idle-warning', 'Masih memilih?',
                                        'Layar akan kembali ke iklan jika tidak digunakan.',
                                        'LANJUT PILIH', self._kiosk_activity,
                                        timeout=False, secondary='TUTUP')
                # Any touch on the landing page already resets the inactivity
                # timer. Opening the automatic warning must not count as input.
            if self._offer_kind == 'idle-warning':
                remaining = max(0, int(limit - inactive) + 1)
                self.offer_countdown.text = f'Kembali ke iklan dalam {remaining} dtk'
        elif self.current_screen == 'payment':
            self._refresh_payment()
        result = self.qris_printer.poll()
        if (result is not None and self.current_screen == 'payment' and self.payment.current
                and result.attempt_id == self.payment.current.attempt_id
                and self.payment.check() == 'pending'):
            self._show_print_result(result)

    def _show_ad_payment(self, order_summary, session_count, total_amount, on_confirm, on_back):
        """Payment remains visibly simulated until a real verified gateway is supplied."""
        previous = self.payment.current
        if previous is not None and not self.payment.release():
            self.set_status('Pembayaran sebelumnya perlu diselesaikan atau diperiksa dahulu.')
            return False
        if previous is not None:
            self.qris_printer.cancel(previous.attempt_id)
        page = self._reset('payment', 'Bayar, lalu berfoto.')
        self.payment.gateway.validity = self.kiosk_timing.payment_validity
        attempt = self.payment.begin(total_amount)
        self.payment_total = total_amount
        self._payment_submitted = False
        self._payment_delivery_attempted = False
        self._payment_on_confirm = on_confirm
        self._last_payment_state = None
        self._payment_offered.clear()
        stage = FloatLayout()
        self._add_advertisement(stage, 'payment')
        ad_card = Panel(fill=WHITE, orientation='vertical', padding=dp(10), spacing=dp(6))
        ad_card.add_widget(self._label('MEONG PARTNERS', 10, 16, bold=True, color=BLUE))
        ad_card.add_widget(stage)
        ad_card.add_widget(self._label('Selesaikan pembayaran untuk mulai berfoto.', 12, 20,
                                       color=GREY, align='center'))
        self.payment_ad_card = ad_card
        detail = Panel(fill=WHITE, orientation='vertical', padding=dp(10), spacing=dp(4))
        total = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(8))
        total.add_widget(self._label('Rp ' + f'{total_amount:,}'.replace(',', '.'), 28, bold=True))
        count = self._label(f'{session_count} sesi', 12, color=GREY, align='right')
        count.size_hint_x = .4
        total.add_widget(count)
        detail.add_widget(total)
        detail.add_widget(self._label('QR DEMO · BUKAN UNTUK TRANSFER', 10, 16,
                                     bold=True, color=BLUE, align='center'))
        self._payment_qr_image = create_qr_image(attempt.payload, with_logo=False)
        self.payment_qr = self._display(self._payment_qr_image, crisp=True)
        detail.add_widget(self.payment_qr)
        self.payment_status = self._label('', 11, 23, bold=True, align='center', color=GREY)
        detail.add_widget(self.payment_status)
        tools = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        self.payment_enlarge = self._button('PERBESAR QR', self.show_payment_enlargement, secondary=True)
        self.payment_print = self._button('CETAK QR', self._request_payment_print)
        for button in (self.payment_enlarge, self.payment_print):
            button.height = dp(36)
            button.font_size = dp(11)
            tools.add_widget(button)
        detail.add_widget(tools)
        order_list = ScrollView(do_scroll_x=False, bar_width=dp(3), size_hint_y=None, height=dp(42))
        self.payment_order = self._label(order_summary, 12, auto_height=True, color=GREY)
        order_list.add_widget(self.payment_order)
        detail.add_widget(order_list)
        self.payment_details = detail
        row = self._responsive_row(ad_card, detail, 340, 350)
        def proportion(*_args):
            if row.width >= dp(720):
                detail.width = max(dp(300), row.width * .35)
        row.bind(size=proportion)
        proportion()
        page.add_widget(row)
        def confirm_once():
            if (self.current_screen != 'payment' or self.payment_confirm is not confirm_button
                    or confirm_button.disabled):
                return
            # This is an explicit DEMO action. Printed paper, a UI timeout and
            # the customer's banking screen never imply a successful payment.
            current = self.payment.current
            if current is None:
                return
            if not self.payment.gateway.simulate_success(current):
                self._refresh_payment()
                return
            self._deliver_paid_payment()
        self.payment_confirm = self._button('SIMULASIKAN PEMBAYARAN BERHASIL', confirm_once,
                                           enabled=self._camera_ready)
        confirm_button = self.payment_confirm
        self.payment_back = self._button('UBAH PESANAN', lambda: self._leave_payment(on_back), secondary=True)
        self.payment_back.size_hint_x = .45
        page.add_widget(self._actions(self.payment_back, self.payment_confirm))
        self._refresh_payment()
        return True

    def _deliver_paid_payment(self):
        """Advance a confirmed demo success once, retaining manual recovery.

        A late successful status check follows the same path as the explicit
        demo button. If the controller rejects capture (for example, no camera
        frames), keep this paid attempt and expose a retry without marking a
        second payment or opening repeated error dialogs on every status tick.
        """
        if self.current_screen != 'payment' or self._payment_submitted:
            return
        if self.payment.check() != 'paid':
            return
        current, button = self.payment.current, self.payment_confirm
        self._payment_delivery_attempted = True
        self._payment_submitted = True
        self._close_inline_offer()
        self._close_enlargement()
        self.qris_printer.cancel(current.attempt_id)
        button.disabled = True
        accepted = self._payment_on_confirm()
        if (accepted is False and self.current_screen == 'payment'
                and self.payment.current is current and self.payment_confirm is button):
            self._payment_submitted = False
            button.disabled = not self._camera_ready
            button.text = 'LANJUT FOTO'

    def _leave_payment(self, callback):
        attempt = self.payment.current
        if not self.payment.release():
            self.set_status('Status pembayaran perlu diperiksa. Pesanan tetap disimpan di halaman ini.')
            self._refresh_payment()
            return
        if attempt is not None:
            self.qris_printer.cancel(attempt.attempt_id)
        callback()

    def _refresh_payment(self):
        attempt = self.payment.current
        if attempt is None:
            return
        state = self.payment.check()
        if state == 'paid' and not self._payment_delivery_attempted:
            self._deliver_paid_payment()
            if self.current_screen != 'payment' or self.payment.current is not attempt:
                return
        remaining = int(attempt.remaining())
        if state == 'pending':
            self.payment_status.text = f'Menunggu demo · {remaining // 60:02d}:{remaining % 60:02d}'
        elif state == 'paid':
            self.payment_status.text = 'Pembayaran demo berhasil'
        elif state == 'unknown':
            self.payment_status.text = 'Memeriksa status pembayaran...'
        else:
            self.payment_status.text = 'QR kedaluwarsa · perbarui untuk melanjutkan'
        self.payment_print.disabled = self.qris_printer.busy or state in {'paid', 'unknown'}
        self.payment_enlarge.disabled = state != 'pending'
        self.payment_confirm.disabled = (not self._camera_ready or self._payment_submitted
                                          or state not in {'pending', 'paid'})
        self.payment_qr.opacity = 1 if state in {'pending', 'unknown'} else .15
        if state in {'paid', 'expired', 'cancelled', 'failed'} and state != self._last_payment_state:
            self.qris_printer.cancel(attempt.attempt_id)
            self._close_inline_offer()
            self._close_enlargement()
        self._last_payment_state = state
        if self._inline_offer is not None or self._enlarged is not None or self.audio_settings_open:
            return
        key = (attempt.attempt_id, state)
        elapsed = (attempt.expires_at - attempt.created_at).total_seconds() - attempt.remaining()
        if key not in self._payment_offered:
            if state in {'expired', 'cancelled', 'failed'}:
                self._payment_offered.add(key)
                self._offer_payment_print(renew=True)
            elif state == 'pending' and elapsed >= self.kiosk_timing.payment_offer_after:
                self._payment_offered.add(key)
                self._offer_payment_print()

    def _offer_payment_print(self, renew=False):
        if self.current_screen != 'payment' or self._enlarged is not None:
            return
        self._show_inline_offer(self._ad_stage, 'print-offer',
                                'QR perlu diperbarui?' if renew else 'Sulit memindai layar?',
                                'Buat QR baru, lalu cetak untuk dipindai.' if renew else
                                'Cetak kode di kertas, lalu pindai dengan ponselmu.',
                                'PERBARUI + CETAK' if renew else 'CETAK QR',
                                self._renew_and_print if renew else self._request_payment_print)

    def _request_payment_print(self):
        if self.current_screen != 'payment' or self.qris_printer.busy:
            return
        state = self.payment.check()
        if state in {'expired', 'cancelled', 'failed'}:
            self._close_enlargement()
            self._offer_payment_print(renew=True)
            return
        if state != 'pending':
            self.set_status('Periksa status pembayaran sebelum mencetak QR.')
            return
        self._close_enlargement()
        if self.qris_printer.submit(self.payment.current):
            self._show_inline_offer(self._ad_stage, 'printing', 'Menyiapkan cetakan...',
                                    'Pembayaran tetap menunggu. QR di kanan tetap bisa dipindai.',
                                    'MENCETAK...', lambda: None, timeout=False, secondary='TUTUP')
            self.offer_action.disabled = True
            self.payment_print.disabled = True

    def _renew_and_print(self):
        """Recheck final status before replacing an expired/failed/cancelled QR."""
        old = self.payment.current
        if old is None or self.qris_printer.busy:
            return
        try:
            current = self.payment.renew()
        except RuntimeError:
            self.set_status('QR belum diperbarui. Periksa status pembayaran lama dahulu.')
            return
        self.qris_printer.cancel(old.attempt_id)
        self._payment_qr_image = create_qr_image(current.payload, with_logo=False)
        self._display(self._payment_qr_image, self.payment_qr, crisp=True)
        self._last_payment_state = None
        self._close_inline_offer()
        self._refresh_payment()
        self._request_payment_print()

    def _show_print_result(self, result):
        title = {'sent': 'Ambil kertas QR', 'preview': 'Pratinjau cetakan siap',
                 'error': 'QR belum dicetak', 'unknown': 'Periksa printer'}.get(result.status, 'Status cetak')
        self._show_inline_offer(self._ad_stage, 'print-result', title, result.message,
                                'LIHAT PRATINJAU' if result.preview else 'TUTUP',
                                (lambda: self.show_payment_enlargement(result.preview)) if result.preview
                                else self._close_inline_offer, timeout=False, secondary='TUTUP')

    def show_payment_enlargement(self, receipt_path=None):
        """Use the ad column for a larger code/receipt; no extra native window."""
        if self.current_screen != 'payment' or self.payment.check() != 'pending':
            return
        self._close_inline_offer()
        self._close_enlargement()
        self._ad_player.pause()
        body = Panel(fill=WHITE, orientation='vertical', padding=dp(12), spacing=dp(8),
                     pos_hint={'x': 0, 'y': 0})
        body.add_widget(self._label('PRATINJAU CETAKAN' if receipt_path else 'PINDAI QR DEMO',
                                    14, 24, bold=True, color=BLUE, align='center'))
        if receipt_path:
            with Image.open(receipt_path) as source:
                image = source.copy()
        else:
            image = self._payment_qr_image
        self.enlarged_qr = self._display(image, crisp=True)
        body.add_widget(self.enlarged_qr)
        close = self._button('KEMBALI KE IKLAN', self._close_enlargement, secondary=True)
        close.height = dp(40)
        body.add_widget(close)
        self._ad_stage.add_widget(body)
        self._enlarged = body

    def _close_enlargement(self, resume=True):
        if self._enlarged is not None:
            if self._enlarged.parent is not None:
                self._enlarged.parent.remove_widget(self._enlarged)
            self._enlarged = None
            if resume and self._ad_player is not None:
                self._ad_player.resume()
