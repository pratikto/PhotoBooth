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

    def _retire_kiosk_page(self):
        """Unload video and remove every overlay before advancing the page revision."""
        self._close_inline_offer()
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
        self.callbacks['on_home_start']()
        if self.current_screen != 'advert':
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
