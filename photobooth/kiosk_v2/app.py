"""Opt-in Kivy portrait kiosk UI v2; does not launch the production booth.

P3 adds a nonfinancial photo-test path; P4 adds manual-token DEMO gameplay.
Production payment, merchant scanning and redeemable discounts stay off.
"""

from pathlib import Path
import logging
import os
import time
import math

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from photobooth.advertising import AdCatalog, AdEventLog, PROJECT_ROOT
from photobooth.catalog import create_template_preview, get_templates
from photobooth.ui_ads import AdvertisementPlayer
from photobooth.workflow import quote_order

from .audio import make_kivy_audio
from .branding import MeongLogo
from .illustrations import TutorialIcon
from .flow import ADVERT, BROWSING_PAGES, GAME_PREVIEW, GAME_PAGES, TEMPLATES, TUTORIAL, PHOTO_PAGES, MOCK_CHECKOUT, SANDBOX_CHECKOUT, VisitFlow
from .theme import ArcadeButton, CYAN, GOLD, MUTED, PixelCard, PINK, Starfield, WHITE, text_label
from .viewport import PortraitViewport
from .previews import PREVIEW_SIZE, PreviewPreloader
from .gallery import SwipeGallery, StripCarousel
from .devices import AsyncCamera, FaceInviter
from .photo_views import PhotoViews
from .live_preview import LivePreview
from .performance import PerformanceLog
from .sensors import PalmShutter
from .game_views import GameViews
from .checkout_views import CheckoutViews
from .sandbox_views import SandboxViews
from .operator_health import OperatorViews, OperatorMeongLogo
from .game_offer import demo_amount, is_demo_winner


LOG = logging.getLogger(__name__)


def _portrait_strip_texture(template, preview=None):
    """Convert only this approved master preview to a GPU texture, preserving 1:3."""
    if preview is None:
        preview = create_template_preview(template, PREVIEW_SIZE).convert("RGB")
    texture = Texture.create(size=preview.size, colorfmt="rgb")
    texture.blit_buffer(preview.tobytes(), colorfmt="rgb", bufferfmt="ubyte")
    texture.flip_vertical()
    texture.mag_filter = "nearest"
    # Thin thermal frame lines need area interpolation when the whole window
    # shrinks; nearest minification can drop a line completely. Brand pixel art
    # keeps its separate nearest filter.
    texture.min_filter = "linear"
    return texture


class TouchStage(Starfield):
    """Touch monitoring on the actual page, including swipes over a ScrollView."""

    def __init__(self, on_activity, **kwargs):
        self._activity = on_activity
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        if getattr(touch, 'button', 'left') in {'right', 'middle'}:
            return False
        if self.collide_point(*touch.pos):
            self._activity()
        return super().on_touch_down(touch)


class PortraitKioskV2App(PhotoViews, GameViews, CheckoutViews, SandboxViews, OperatorViews, App):
    """Separate greenfield window; the original python main.py remains untouched."""

    title = "MEONG PHOTOBOOTH - PORTRAIT GUI V2 (PROTOTIPE)"

    def __init__(self, *, camera_device=None, face_inviter=None, palm_shutter=None, game_jobs=None,
                 checkout_jobs=None, sandbox_jobs=None, **kwargs):
        self._provided_camera = camera_device
        self._provided_inviter = face_inviter
        self._provided_palm = palm_shutter
        self._provided_game_jobs = game_jobs
        self._provided_checkout_jobs = checkout_jobs
        self._provided_sandbox_jobs = sandbox_jobs
        super().__init__(**kwargs)

    def build(self):
        # Window defaults belong to the dedicated launcher, not the shared App.
        # This keeps importing/building the prototype free of global size changes.
        self._suspended = False
        self._closed = False
        self._view_revision = 0
        self._init_sandbox()
        self._init_photos()
        self._init_game()
        self._init_checkout()
        self.live_preview = LivePreview()
        self.performance = PerformanceLog()
        self._sensor_states = None
        self.navigation = VisitFlow()
        self.templates = get_templates()
        self.catalog = AdCatalog()
        self.events = AdEventLog(PROJECT_ROOT / "data" / "advertising" / "events-v2.jsonl")
        self.audio_v2 = make_kivy_audio()
        self.quantities = {t.template_id: 0 for t in self.templates}
        self.template_index = 0
        self._textures = {}
        self._preview_preloader = PreviewPreloader(self.templates)
        self._idle_audio_pending = ['count', 'shutter', 'success', 'game_music']
        self._idle_failed_previews = set()
        self._idle_asset_event = None
        self._ad_player = None
        self._invitation = None
        self._invitation_timer = None
        self._warning_label = None
        self._last_activity = time.monotonic()
        camera_enabled = os.environ.get('PHOTOBOOTH_CAMERA', '1').lower() not in {'0', 'false', 'no'}
        try:
            camera_index = int(os.environ.get('PHOTOBOOTH_CAMERA_INDEX', '0'))
        except ValueError:
            camera_index = 0
        self.camera_device = self._provided_camera or AsyncCamera(enabled=camera_enabled, index=camera_index)
        face_enabled = os.environ.get('PHOTOBOOTH_FACE_TRIGGER', '1').lower() not in {'0', 'false', 'no'}
        self.face_inviter = self._provided_inviter or FaceInviter(
            enabled=face_enabled, hold=self.catalog.timing.face_hold,
            cooldown=self.catalog.timing.face_cooldown)
        palm_enabled = os.environ.get('PHOTOBOOTH_PALM_TRIGGER', '1').lower() not in {'0', 'false', 'no'}
        self.palm_shutter = self._provided_palm or PalmShutter(enabled=palm_enabled)
        LOG.info('Input configuration camera_enabled=%s camera_index=%s face_enabled=%s palm_enabled=%s',
                 camera_enabled, camera_index, face_enabled, palm_enabled)
        self._init_operator()
        self.stage = ScreenManager(transition=NoTransition())
        if self._sandbox_enabled:
            self.navigation.page = SANDBOX_CHECKOUT
            self._sandbox_submit('boot')
        self._show()
        self._warmup = Clock.schedule_once(self._prepare_idle_assets, 0)
        self._heartbeat = Clock.schedule_interval(self._tick, 1)
        self._devices_event = Clock.schedule_interval(self._devices_tick, 1 / 30)
        Window.bind(on_minimize=self._window_minimized, on_restore=self._window_restored)
        return self.stage

    def _prepare_idle_assets(self, _dt):
        if self._closed:
            return
        self._preview_preloader.start()
        self._warm_photo_delivery()
        self.camera_device.start()
        if not self._suspended:
            self.audio_v2.prepare()
        self._idle_asset_event = Clock.schedule_interval(self._warm_idle_assets, .05)

    def _warm_idle_assets(self, _dt):
        """Upload one ready strip/load one silent cue per idle turn, never on tap."""
        if self._closed:
            return False
        if self._suspended or self.navigation.page != ADVERT or self._invitation is not None:
            return
        started = time.perf_counter()
        if self._idle_audio_pending:
            name = self._idle_audio_pending.pop(0)
            self.audio_v2.prepare(names=(name,))
            LOG.info('Idle asset ready kind=audio name=%s prepare_ms=%.1f',
                     name, (time.perf_counter() - started) * 1000)
            return
        pending = False
        for template in (self.templates[0], *self.templates[-1:], *self.templates[1:-1]):
            key = template.template_id
            if key in self._textures or key in self._idle_failed_previews:
                continue
            pending = True
            preview = self._preview_preloader.get(template)
            if preview is None:
                continue  # CPU decoder is still busy; never wait on a future here.
            try:
                self._textures[key] = _portrait_strip_texture(template, preview)
                LOG.info('Idle asset ready kind=strip name=%s prepare_ms=%.1f',
                         key, (time.perf_counter() - started) * 1000)
            except Exception:
                self._idle_failed_previews.add(key)
                LOG.warning('Idle strip upload unavailable: %s', key, exc_info=True)
            return  # Keep the next Kivy turn free for input and advertising.
        if not pending:
            return False

    def _devices_tick(self, _dt):
        if self._closed:
            return False
        self._operator_last_tick = time.monotonic()
        self._poll_operator()
        self._poll_photos()
        if self._suspended:
            return
        self._poll_game()
        self._poll_checkout()
        self._poll_sandbox()
        frame = self.camera_device.read()
        if self.navigation.page == 'capture':
            self.live_preview.submit(frame, self._view_revision)
        preview = self.live_preview.read(self._view_revision)
        self._update_live_photo(frame, preview)
        self.performance.observe(self.navigation.page, _dt, frame, preview)
        allowed = self.navigation.page == ADVERT and self._invitation is None and not self._operator_active
        if self.face_inviter.update(frame, self._view_revision, allowed=allowed):
            self._show_invitation(source='face')
        active = self.navigation.page == 'capture'
        can_trigger = (active and self._countdown_event is None and
                       not self._photo_jobs.busy and not self._capture_button.disabled)
        if self.palm_shutter.update(frame, self._view_revision, active=active, can_trigger=can_trigger):
            self._start_countdown(source='palm')
        self._update_sensor_hints(camera_ready=frame is not None)

    def _window_minimized(self, *_args):
        self.on_pause()

    def _update_sensor_hints(self, *, camera_ready=True):
        face_state, palm_state = self.face_inviter.state, self.palm_shutter.state
        states = (face_state if isinstance(face_state, str) else 'unknown',
                  palm_state if isinstance(palm_state, str) else 'unknown')
        if states != self._sensor_states:
            LOG.info('Detection face_state=%s palm_state=%s', *states)
            self._sensor_states = states
        if self.navigation.page == ADVERT:
            progress = self.face_inviter.progress
            progress = progress if isinstance(progress, (int, float)) else 0
            self._face_hint.text = (
                f"WAJAH TERLIHAT • TAHAN {max(1, math.ceil((1-progress)*self.catalog.timing.face_hold))} DTK"
                if progress > 0 else 'PETUALANGAN DIMULAI DI SINI')
        elif self.navigation.page == 'capture':
            if not camera_ready:
                hint = 'Sambungkan kamera untuk memakai SIAP/telapak'
            elif self._countdown_event is not None:
                hint = 'Senyum! Turunkan telapak setelah countdown.'
            elif palm_state in {'disabled', 'unavailable', 'closed'}:
                hint = 'Telapak belum tersedia • pakai tombol SIAP'
            elif palm_state != 'ready':
                hint = 'Menyiapkan deteksi telapak • SIAP tetap bisa'
            elif self.palm_shutter.needs_release:
                hint = 'Turunkan telapak sebelum foto berikutnya'
            elif self.palm_shutter.progress > 0:
                hint = 'Tahan telapak terbuka sebentar…'
            else:
                hint = 'Angkat telapak 1 detik atau tekan SIAP'
            self._palm_hint.text = hint

    def _window_restored(self, *_args):
        self.on_resume()

    def on_pause(self):
        self._suspended = True
        self._sandbox_lock_customer()
        self._close_operator()
        self._photo_pause()
        self._pause_game()
        self.live_preview.pause()
        self.performance.flush()
        self.camera_device.set_active(False)
        self.face_inviter.pause()
        self.palm_shutter.pause()
        self.audio_v2.suspend()
        for widget in self.stage.walk():
            if isinstance(widget, SwipeGallery):
                widget.cancel_motion()
            elif isinstance(widget, MeongLogo):
                widget.set_active(False)
        if self._ad_player is not None:
            self._ad_player.pause()
        return True

    def on_resume(self):
        if self._closed or not self._suspended:
            return
        self._suspended = False
        self.performance.flush()
        self.camera_device.set_active(True)
        # Background time is not customer browsing time.
        self._activity()
        self.audio_v2.resume()
        for widget in self.stage.walk():
            if isinstance(widget, MeongLogo):
                widget.set_active(True)
        if self._ad_player is not None:
            self._ad_player.resume()
        if self.navigation.page in PHOTO_PAGES:
            self._show()

    def on_stop(self):
        self._closed = True
        self._close_operator()
        self._health_reports.close()
        Window.unbind(on_keyboard=self._operator_key)
        self._cancel_countdown()
        self._retire_game_field()
        self._game_jobs.close()
        self._mock_jobs.close()
        if self._sandbox_jobs:
            self._sandbox_jobs.close()
        self.live_preview.close()
        self.performance.flush()
        if self._photo_jobs is not None:
            self._photo_jobs.close()
        Window.unbind(on_minimize=self._window_minimized, on_restore=self._window_restored)
        self._retire_gestures()
        if getattr(self, "_heartbeat", None):
            self._heartbeat.cancel()
        if getattr(self, '_warmup', None):
            self._warmup.cancel()
        if self._idle_asset_event is not None:
            self._idle_asset_event.cancel()
        if getattr(self, '_preview_preloader', None):
            self._preview_preloader.close()
        if getattr(self, '_devices_event', None):
            self._devices_event.cancel()
        if getattr(self, 'camera_device', None):
            self.camera_device.close()
        if getattr(self, 'face_inviter', None):
            self.face_inviter.close()
        if getattr(self, 'palm_shutter', None):
            self.palm_shutter.close()
        self._close_invitation()
        self._stop_ad()
        if getattr(self, "audio_v2", None):
            self.audio_v2.close()

    def _activity(self):
        self._last_activity = time.monotonic()
        if self._warning_label is not None:
            self._warning_label.text = ""

    def _apply_cached_content(self):
        # Worker owns all network/JSON/image decoding. Swap references only at
        # idle; active visitors keep immutable artwork paths through capture.
        if (self._closed or self._suspended or self._sandbox_enabled
                or self.navigation.page != ADVERT or self._invitation is not None or self._operator_active):
            return
        jobs = self._photo_jobs
        service = jobs.service if jobs and not jobs.busy else None
        content = getattr(service, 'content', None)
        snapshot = content.current if content else None
        if not snapshot or snapshot['version'] == getattr(self, '_content_version', None):
            return
        self._content_version = snapshot['version']
        self.catalog = snapshot['catalog']
        if not self._mock_enabled:
            self.templates = snapshot['templates']
            self.quantities = {t.template_id: 0 for t in self.templates}
            self.template_index = 0
            self._preview_preloader.close()
            self._preview_preloader = PreviewPreloader(self.templates)
            self._preview_preloader.start()
            self._textures.clear()
            self._idle_failed_previews.clear()
        self._show()

    def _tick(self, _dt):
        self._apply_cached_content()
        if (not self._closed and not self._suspended and self._sandbox_enabled
                and time.monotonic()-self._last_activity >= 60
                and self._sandbox_jobs and self._sandbox_jobs.store
                and self._sandbox_jobs.store.flow.active
                and not self._sandbox_jobs.store.flow.customer_claim_required):
            self._sandbox_lock_customer()
        if self._closed or self._suspended or self.navigation.page not in BROWSING_PAGES:
            return
        duration = time.monotonic() - self._last_activity
        deadline = self.catalog.timing.landing_idle
        if duration >= deadline:
            if self.navigation.browse_timeout():
                self._reset_visit()
                self._show()
        elif self._warning_label is not None:
            remaining = deadline - duration
            self._warning_label.text = (
                "Sesi kembali ke iklan dalam " + str(int(remaining) + 1) + " detik"
                if remaining <= self.catalog.timing.idle_warning else ""
            )

    def _stop_ad(self):
        player, self._ad_player = self._ad_player, None
        if player is not None:
            player.close()

    def _close_invitation(self, *_args):
        if self._invitation_timer is not None:
            self._invitation_timer.cancel()
            self._invitation_timer = None
        if self._invitation is not None and self._invitation.parent is not None:
            for control in self._invitation.walk(restrict=True):
                if isinstance(control, ArcadeButton):
                    control.disabled = True
            self._invitation.parent.remove_widget(self._invitation)
        self._invitation = None
        if self._ad_player is not None:
            self._ad_player.set_volume(.55)

    def _retire_gestures(self):
        for widget in self.stage.walk():
            if isinstance(widget, (SwipeGallery, MeongLogo)):
                widget.dispose()

    def _show(self):
        """Retire old media before rebuilding only the opt-in v2 page tree."""
        started = time.perf_counter()
        self.live_preview.pause()
        LOG.info('Page rebuild begin from=%s to=%s revision=%s',
                 self.stage.current, self.navigation.page, self._view_revision + 1)
        self._view_revision += 1
        self._retire_game_field()
        self.face_inviter.pause()
        self.palm_shutter.pause()
        self._close_invitation()
        self._stop_ad()
        self._warning_label = None
        self._retire_gestures()
        self.stage.clear_widgets()
        page = Screen(name=self.navigation.page)
        canvas = TouchStage(self._activity)
        page.add_widget(PortraitViewport(canvas))
        self.stage.add_widget(page)
        self.stage.current = page.name
        self.audio_v2.enter_page(self.navigation.page)
        LOG.info('Page media retired; audio owner=%s; building view', self.navigation.page)
        if page.name == ADVERT:
            self._build_advert(canvas)
        elif page.name == TUTORIAL:
            self._build_tutorial(canvas)
        elif page.name == TEMPLATES:
            self._build_templates(canvas)
        elif page.name == GAME_PREVIEW:
            self._build_game_notice(canvas)
        elif page.name in PHOTO_PAGES:
            self._build_photo_page(canvas)
        elif page.name in GAME_PAGES:
            self._build_game_page(canvas)
        elif page.name == SANDBOX_CHECKOUT:
            self._build_sandbox_checkout(canvas)
        elif page.name == MOCK_CHECKOUT:
            self._build_mock_checkout(canvas)
        else:
            raise RuntimeError("Unknown prototype page")
        LOG.info('Page ready page=%s revision=%s build_ms=%.1f',
                 page.name, self._view_revision, (time.perf_counter() - started) * 1000)

    def _frame(self, canvas, *, brand_height=100):
        shell = BoxLayout(
            orientation="vertical", padding=[dp(20), dp(18), dp(20), dp(18)],
            spacing=dp(13),
        )
        canvas.add_widget(shell)
        if brand_height:
            shell.add_widget(OperatorMeongLogo(operator_open=self._open_operator,
                                             operator_allowed=self._operator_allowed,
                                             size_hint_y=None, height=dp(brand_height)))
        return shell

    @staticmethod
    def _brand(shell, title, subtitle):
        shell.add_widget(text_label(title, size=23, height=37, bold=True, color=GOLD))
        shell.add_widget(text_label(subtitle, size=13, height=40, color=MUTED))

    def _page_callback(self, callback):
        """Late touch/swipe releases belong only to the page that created them."""
        revision = self._view_revision

        def invoke(*args):
            if self._closed or self._suspended or revision != self._view_revision:
                return
            return callback(*args)

        return invoke

    def _action(self, title, callback, *, variant="primary", height=62, disabled=False):
        button = ArcadeButton(title, variant=variant, height=height)
        button.disabled = disabled
        button._operator_press_epoch = self._operator_epoch
        button.bind(on_press=lambda w:setattr(w, '_operator_press_epoch', self._operator_epoch))
        def activate():
            if self._operator_active or button._operator_press_epoch != self._operator_epoch:
                return
            # Give feedback before routing/decoder retirement. The short shared
            # click now survives page handoffs; suspend/close still stop it.
            started = time.perf_counter()
            self.audio_v2.cue("button")
            audio_seconds = time.perf_counter() - started
            try:
                callback()
            finally:
                elapsed = time.perf_counter() - started
                if elapsed >= .05:
                    LOG.info('Slow action title=%s total_ms=%.1f audio_ms=%.1f callback_ms=%.1f',
                             title, elapsed * 1000, audio_seconds * 1000,
                             (elapsed - audio_seconds) * 1000)

        invoke = self._page_callback(activate)
        button.bind(on_release=lambda *_: None if button.disabled else invoke())
        return button

    def _choose_photo(self, source="manual"):
        if self.navigation.page == ADVERT and self._ad_player is not None:
            self.events.write(
                "photo_entry", ad_id=self._ad_player.ad_id,
                placement="idle", source=source,
            )
        self.navigation.begin_photo(source)
        self._activity()
        self._show()

    def _choose_game(self, source="manual"):
        if self.navigation.page == ADVERT and self._ad_player is not None:
            self.events.write(
                "game_entry_preview", ad_id=self._ad_player.ad_id,
                placement="idle", source=source,
            )
        self.navigation.begin_game_preview(source)
        self._activity()
        self._show()

    def _reset_visit(self):
        # UI-only reset. An actual receipt-attempt ledger will NEVER be cleared.
        self.quantities = {t.template_id: 0 for t in self.templates}
        self.template_index = 0
        self._game_attempt = self._game_result = self._game_engine = None
        self._mock_view = None
        self._mock_key = None
        self._game_error = ''
        self._game_discount_used = False

    def _return_ad(self):
        LOG.info('Return to advertising requested from=%s', self.navigation.page)
        self.navigation.to_advertising()
        self._reset_visit()
        self._activity()
        self._show()

    def _build_advert(self, canvas):
        """Attract mode stays advertising-first, with two equally visible paths."""
        shell = self._frame(canvas)
        self._brand(shell, "ABADIKAN MOMEN DI GALAKSI",
                    "STRIP 3 FOTO + QR DOWNLOAD • MEONG PHOTOBOOTH")

        headline = PixelCard(orientation="horizontal", size_hint_y=None,
                             height=dp(50), padding=7, spacing=8)
        headline.add_widget(text_label("IKLAN / MODE SIAGA", size=15, height=34,
                                      color=CYAN, bold=True))
        self._face_hint = text_label("PETUALANGAN DIMULAI DI SINI", size=12, height=34, color=GOLD)
        headline.add_widget(self._face_hint)
        shell.add_widget(headline)

        creative = PixelCard(orientation="vertical", padding=6, spacing=0)
        media_host = FloatLayout()
        self._ad_player = AdvertisementPlayer(
            self.catalog, "idle", self.events, volume=.55,
            on_media_change=self._page_callback(self.audio_v2.set_ad_media),
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0},
        )
        media_host.add_widget(self._ad_player)
        creative.add_widget(media_host)
        shell.add_widget(creative)
        self._advert_host = media_host

        shell.add_widget(self._action(
            "MULAI FOTO", lambda: self._choose_photo("manual")))
        shell.add_widget(self._action(
            "MAIN MEONG FLY", lambda: self._choose_game("manual"),
            variant="secondary"))

        # Photo entry already requires the tutorial; no separate help action.
        # Invitation remains a PREVIEW-only operator action.
        shell.add_widget(self._action(
            "UNDANGAN (DEMO)", self._show_invitation,
            variant="tertiary", height=48))
        shell.add_widget(text_label(
            "Mode iklan aktif saat idle • Game dan QRIS masih prototype",
            size=12, height=31, color=MUTED,
        ))

    def _show_invitation(self, source='face_preview'):
        """Real ad media stays visible beneath a nonmodal, manual demo invite."""
        if self._closed or self._suspended or self.navigation.page != ADVERT:
            return
        self._close_invitation()
        panel = PixelCard(
            orientation="vertical", size_hint=(.94, None), height=dp(286),
            pos_hint={"center_x": .5, "center_y": .49},
            padding=12, spacing=7,
        )
        panel.add_widget(text_label(
            "HAIII! MAU FOTO ATAU MAIN?", size=19,
            height=42, color=GOLD, bold=True))
        panel.add_widget(text_label(
            "Yuk pilih petualanganmu bareng Meong!",
            size=13, height=30, color=MUTED))
        panel.add_widget(self._action(
            "AYO FOTO", lambda: self._choose_photo(source),
            height=50))
        panel.add_widget(self._action(
            "MAIN MEONG FLY", lambda: self._choose_game(source),
            variant="secondary", height=50))
        panel.add_widget(self._action(
            "NANTI SAJA", self._close_invitation,
            variant="tertiary", height=48))
        self._advert_host.add_widget(panel)
        self._invitation = panel
        self._ad_player.set_volume(.15)
        self._invitation_timer = Clock.schedule_once(
            self._close_invitation, self.catalog.timing.offer_timeout,
        )

    def _build_tutorial(self, canvas):
        shell = self._frame(canvas)
        self._brand(shell, "CARA PAKAI MEONG", "CUMA 4 LANGKAH • GAMPANG BANGET!")

        status = PixelCard(orientation="horizontal", size_hint_y=None,
                           height=dp(50), padding=7, spacing=5)
        status.add_widget(text_label(
            "TUTORIAL WAJIB", size=14, height=33, color=CYAN, bold=True))
        status.add_widget(text_label(
            "Cukup sekali per kunjungan", size=13, height=33, color=GOLD))
        shell.add_widget(status)

        guide = ScrollView(size_hint_y=1, bar_width=dp(4), do_scroll_x=False)
        stack = BoxLayout(orientation="vertical", size_hint_y=None,
                          spacing=dp(12),
                          padding=[dp(3), dp(8), dp(3), dp(12)])
        stack.bind(minimum_height=stack.setter("height"))

        steps = (
            ("template", "01  PILIH TEMPLATE",
             "Cari desain favoritmu dari 12 strip asli."),
            ("payment", "02  BAYAR",
             "Selesaikan pembayaran sesuai instruksi layar."),
            ("camera", "03  AMBIL 3 FOTO",
             "Pose tiga kali! Kamu bisa ulang satu foto."),
            ("print", "04  CETAK & SCAN QR",
             "Ambil strip vertikal, scan QR untuk foto digital."),
        )
        for kind, title, detail in steps:
            card = PixelCard(orientation="horizontal", size_hint_y=None,
                             height=dp(146), padding=12, spacing=14)
            art = TutorialIcon(kind=kind, size_hint=(None, 1), width=dp(106))
            card.add_widget(art)

            copy = BoxLayout(orientation="vertical", spacing=dp(6))
            copy.add_widget(text_label(
                title, size=18, height=45, color=CYAN,
                bold=True, align="left"))
            copy.add_widget(text_label(
                detail, size=15, height=64, color=MUTED, align="left"))
            card.add_widget(copy)
            stack.add_widget(card)

        guide.add_widget(stack)
        shell.add_widget(guide)
        self._warning_label = text_label(
            "", size=12, height=29, color=GOLD)
        shell.add_widget(self._warning_label)
        shell.add_widget(self._action(
            "UJI MUSIK (CEK SPEAKER)", self._test_music,
            variant="secondary", height=48))
        self._audio_status = text_label(
            "Musik diputar otomatis di halaman ini. Dengarkan speaker.",
            size=12, height=38, color=MUTED,
        )
        shell.add_widget(self._audio_status)
        shell.add_widget(self._action(
            "LANJUT PILIH TEMPLATE", self._complete_tutorial))
        shell.add_widget(self._action(
            "BATAL / KEMBALI IKLAN", self._return_ad,
            variant="tertiary", height=48))

    def _test_music(self):
        requested = self.audio_v2.test_music()
        status = self.audio_v2.status()
        provider = status["provider"]
        if requested:
            self._audio_status.text = (
                f"Playback diminta ({provider}). Pastikan terdengar di speaker."
            )
        else:
            self._audio_status.text = (
                f"Audio tidak siap ({provider}): {status['last_error'] or 'cek volume'}"
            )

    def _complete_tutorial(self):
        self.navigation.complete_tutorial()
        self._activity()
        self._show()

    def _build_game_notice(self, canvas):
        self._build_game_page(canvas)

    def _build_templates(self, canvas):
        # Most vertical space belongs to the approved 1:3 strips. Utility text
        # and order controls stay compact; floating arrows do not consume a row.
        shell = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        canvas.add_widget(shell)
        shell.add_widget(MeongLogo(size_hint_y=None, height=dp(78)))
        self._game_offer_note = None

        deck = PixelCard(orientation='vertical', padding=8, spacing=4)
        host = FloatLayout()
        gallery = StripCarousel(on_swipe=self._page_callback(self._swipe_template),
                                size_hint=(1, None), pos_hint={'x': 0, 'y': 0})
        # Title floats inside the gallery, above the complete strip artwork.
        # A small inner inset reserves its lane without covering a design.
        host.bind(height=lambda widget, height:setattr(gallery, 'height', max(1, height-dp(26))))
        self._carousel = gallery
        self._previous_preview = gallery.previous_image
        self._preview = gallery.selected_image
        self._next_preview = gallery.next_image
        host.add_widget(gallery)
        title = self._gallery_title = PixelCard(size_hint=(None, None), width=dp(236),
            height=dp(26), padding=0, pos_hint={'center_x': .5, 'top': 1})
        title.add_widget(text_label('PILIH TEMPLATE STRIP', size=14, height=26,
                                    color=GOLD, bold=True))
        host.add_widget(title)
        for label, step, hint in (('SEBELUMNYA', -1, {'x': .01, 'y': .015}),
                                   ('BERIKUTNYA', 1, {'right': .99, 'y': .015})):
            arrow = self._action(label, lambda step=step: self._shift_template(step),
                                 variant='tertiary' if step == -1 else 'secondary', height=48)
            arrow.size_hint = (None, None)
            arrow.width = dp(108)
            arrow.font_size = dp(12)
            arrow.pos_hint = hint
            host.add_widget(arrow)
        deck.add_widget(host)
        self._template_name = text_label('', size=18, height=30, color=GOLD, bold=True)
        deck.add_widget(self._template_name)
        shell.add_widget(deck)

        count_card = self._count_card = PixelCard(orientation='vertical', size_hint_y=None,
                               height=dp(90), padding=8)
        row = BoxLayout(spacing=dp(16), padding=[0, dp(4), 0, dp(4)])
        quantity_column = BoxLayout(orientation='vertical', size_hint_x=.5)
        quantity = BoxLayout(spacing=dp(4), size_hint_y=None, height=dp(48))
        quantity.add_widget(self._action('-', lambda: self._change_copies(-1),
                                         variant='tertiary', height=48))
        self._copy_value = text_label('0', size=24, height=48, color=GOLD, bold=True)
        self._copy_value.size_hint_x = .65
        quantity.add_widget(self._copy_value)
        quantity.add_widget(self._action('+', lambda: self._change_copies(1),
                                         variant='secondary', height=48))
        quantity_column.add_widget(quantity)
        self._order_summary = text_label('', size=12, height=18, color=WHITE)
        quantity_column.add_widget(self._order_summary)
        row.add_widget(quantity_column)
        price = BoxLayout(orientation='vertical', size_hint_x=.5)
        price.add_widget(text_label('TOTAL SIMULASI', size=10, height=14, color=WHITE))
        self._order_total_label = text_label('', size=24, height=32, color=GOLD, bold=True)
        price.add_widget(self._order_total_label)
        self._game_offer_note = text_label('', size=12, height=20, color=GOLD)
        price.add_widget(self._game_offer_note)
        row.add_widget(price)
        count_card.add_widget(row)
        shell.add_widget(count_card)

        self._warning_label = text_label('', size=12, height=0, color=GOLD)
        self._warning_label.bind(text=lambda label, text: setattr(label, 'height', dp(22) if text else 0))
        shell.add_widget(self._warning_label)
        footer = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        payment = self._action('QRIS SANDBOX' if self._sandbox_enabled else 'PEMBAYARAN (BELUM TERHUBUNG)',
                               self._open_sandbox, disabled=not self._sandbox_enabled, height=48)
        payment.size_hint_x = .40
        payment.font_size = dp(10)
        payment.halign = 'center'
        payment.valign = 'middle'
        payment.bind(size=lambda w, size: setattr(w, 'text_size', (max(10, size[0] - dp(12)), size[1])))
        self._test_photo_button = self._action('UJI FOTO', self._enter_photo_test,
                                               variant='secondary', height=48, disabled=self._sandbox_enabled)
        self._test_photo_button.size_hint_x = .22
        self._test_photo_button.font_size = dp(12)
        finish = self._action('SELESAI / KEMBALI IKLAN', self._return_ad,
                              variant='tertiary', height=48)
        finish.size_hint_x = .38
        finish.font_size = dp(11)
        footer.add_widget(payment)
        footer.add_widget(self._test_photo_button)
        footer.add_widget(finish)
        shell.add_widget(footer)
        if self._mock_enabled:
            self._mock_checkout_button = self._action('UJI CHECKOUT MOCK • TANPA PEMBAYARAN',
                                                       self._open_mock_checkout, variant='secondary', height=44)
            shell.add_widget(self._mock_checkout_button)
        self._update_template()

    def _swipe_template(self, step):
        self._shift_template(step)
        self.audio_v2.cue("button")

    def _shift_template(self, step):
        self.template_index = (self.template_index + step) % len(self.templates)
        self._activity()
        self._update_template(step=step)

    def _change_copies(self, delta):
        template = self.templates[self.template_index]
        old = self.quantities[template.template_id]
        self.quantities[template.template_id] = max(0, min(9, old + delta))
        self._activity()
        self._carousel.cancel_motion()
        self._update_order()

    def _update_template(self, *, step=0):
        template = self.templates[self.template_index]
        neighbours = tuple(self.templates[(self.template_index + rank) % len(self.templates)]
                           for rank in (-2, -1, 0, 1, 2))
        self._template_name.text = (
            f"{self.template_index + 1:02d} / {len(self.templates):02d}  •  {template.name}"
        )
        for item in neighbours:
            if item.template_id not in self._textures:
                self._textures[item.template_id] = _portrait_strip_texture(
                    item, self._preview_preloader.get(item))
        self._carousel.show(tuple(self._textures[item.template_id] for item in neighbours), step=step)
        self._update_order()

    def _update_order(self):
        template = self.templates[self.template_index]
        self._copy_value.text = str(self.quantities[template.template_id])
        quote = quote_order(self.templates, self.quantities)
        self._test_photo_button.disabled = self._sandbox_enabled or quote.session_count == 0
        if self._mock_enabled:
            self._mock_checkout_button.disabled = quote.session_count == 0
        # The result was acknowledged by the durable game worker. This preview
        # shares amount math with MOCK; checkout still revalidates its ledger.
        eligible = is_demo_winner(self._game_result) and not self._game_discount_used
        amount = self._gallery_amount = demo_amount(quote.total_amount, eligible)
        money = lambda value:'Rp'+f'{value:,}'.replace(',', '.')
        self._order_total_label.text = money(amount.total)
        self._order_summary.text = f'{quote.print_copy_count} lembar • {quote.session_count} sesi'
        self._game_offer_note.text = (
            f'Hemat {money(amount.discount)}' if amount.discount else
            'Diskon siap' if eligible else
            'Diskon sudah dipakai' if self._game_discount_used else '')
