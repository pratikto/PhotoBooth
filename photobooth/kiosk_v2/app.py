"""Opt-in Kivy portrait kiosk UI v2; does not launch the production booth.

Stage P0-P2: real advertising widget and camera-cat artwork, tutorial, 12 exact
thermal template previews, and a safe quantity/DEMO quote. Real game, QRIS,
camera, retakes, Drive and printing are deliberately NOT wired up yet.
"""

from pathlib import Path
import logging
import time

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
from .flow import ADVERT, BROWSING_PAGES, GAME_PREVIEW, TEMPLATES, TUTORIAL, VisitFlow
from .theme import ArcadeButton, CYAN, GOLD, MUTED, PixelCard, PINK, Starfield, WHITE, text_label
from .viewport import PortraitViewport
from .previews import PreviewPreloader


LOG = logging.getLogger(__name__)


def _portrait_strip_texture(template, preview=None):
    """Convert only this approved master preview to a GPU texture, preserving 1:3."""
    if preview is None:
        preview = create_template_preview(template, (180, 540)).convert("RGB")
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
        if self.collide_point(*touch.pos):
            self._activity()
        return super().on_touch_down(touch)


class SwipeGallery(BoxLayout):
    """Real horizontal touch gesture for the approved strip carousel.

    Grab each pointer stream until release so Windows touch/pen providers keep
    delivering its move/up events. Only gestures ending inside turn a template.
    Predominantly vertical and short motions are ignored.
    """

    def __init__(self, on_swipe, **kwargs):
        self._on_swipe = on_swipe
        self._touch_origins = {}
        super().__init__(**kwargs)

    @staticmethod
    def swipe_step(dx, dy, *, threshold=None):
        if abs(dx) < (dp(54) if threshold is None else threshold) or abs(dx) <= abs(dy) * 1.35:
            return 0
        return -1 if dx > 0 else 1

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if not self.collide_point(*touch.pos) or touch.is_mouse_scrolling:
            return False
        # Normalized window coordinates survive Kivy's parent/local transforms.
        self._touch_origins[touch.uid] = (touch, touch.sx, touch.sy, tuple(Window.size))
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self or touch.uid in self._touch_origins:
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        # Kivy sends both normal and grabbed dispatch; consume only the latter.
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        origin = self._touch_origins.pop(touch.uid, None)
        touch.ungrab(self)
        if origin is None or not self.collide_point(*touch.pos):
            return True
        _, sx, sy, viewport = origin
        if tuple(Window.size) != viewport:
            return True  # A resize in the middle of a drag is not a swipe.
        x0, _ = self.to_window(0, 0)
        x1, _ = self.to_window(dp(54), 0)
        step = self.swipe_step((touch.sx - sx) * Window.width,
                               (touch.sy - sy) * Window.height,
                               threshold=abs(x1 - x0))
        if step:
            self._on_swipe(step)
        return True

    def dispose(self):
        """A retired page must not retain a native pointer grab."""
        for touch, _sx, _sy, _viewport in self._touch_origins.values():
            touch.ungrab(self)
        self._touch_origins.clear()


class PortraitKioskV2App(App):
    """Separate greenfield window; the original python main.py remains untouched."""

    title = "MEONG PHOTOBOOTH - PORTRAIT GUI V2 (PROTOTIPE)"

    def build(self):
        # Window defaults belong to the dedicated launcher, not the shared App.
        # This keeps importing/building the prototype free of global size changes.
        self._suspended = False
        self._closed = False
        self._view_revision = 0
        self.navigation = VisitFlow()
        self.templates = get_templates()
        self.catalog = AdCatalog()
        self.events = AdEventLog(PROJECT_ROOT / "data" / "advertising" / "events-v2.jsonl")
        self.audio_v2 = make_kivy_audio()
        self.quantities = {t.template_id: 0 for t in self.templates}
        self.template_index = 0
        self._textures = {}
        self._preview_preloader = PreviewPreloader(self.templates)
        self._ad_player = None
        self._invitation = None
        self._invitation_timer = None
        self._warning_label = None
        self._last_activity = time.monotonic()
        self.stage = ScreenManager(transition=NoTransition())
        self._show()
        self._warmup = Clock.schedule_once(self._prepare_idle_assets, 0)
        self._heartbeat = Clock.schedule_interval(self._tick, 1)
        Window.bind(on_minimize=self._window_minimized, on_restore=self._window_restored)
        return self.stage

    def _prepare_idle_assets(self, _dt):
        if self._closed:
            return
        self._preview_preloader.start()
        if not self._suspended:
            self.audio_v2.prepare()

    def _window_minimized(self, *_args):
        self.on_pause()

    def _window_restored(self, *_args):
        self.on_resume()

    def on_pause(self):
        self._suspended = True
        self.audio_v2.suspend()
        if self._ad_player is not None:
            self._ad_player.pause()
        return True

    def on_resume(self):
        if self._closed or not self._suspended:
            return
        self._suspended = False
        # Background time is not customer browsing time.
        self._activity()
        self.audio_v2.resume()
        if self._ad_player is not None:
            self._ad_player.resume()

    def on_stop(self):
        self._closed = True
        Window.unbind(on_minimize=self._window_minimized, on_restore=self._window_restored)
        self._retire_gestures()
        if getattr(self, "_heartbeat", None):
            self._heartbeat.cancel()
        if getattr(self, '_warmup', None):
            self._warmup.cancel()
        if getattr(self, '_preview_preloader', None):
            self._preview_preloader.close()
        self._close_invitation()
        self._stop_ad()
        if getattr(self, "audio_v2", None):
            self.audio_v2.close()

    def _activity(self):
        self._last_activity = time.monotonic()
        if self._warning_label is not None:
            self._warning_label.text = ""

    def _tick(self, _dt):
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
            self._invitation.parent.remove_widget(self._invitation)
        self._invitation = None
        if self._ad_player is not None:
            self._ad_player.set_volume(.55)

    def _retire_gestures(self):
        for widget in self.stage.walk():
            if isinstance(widget, SwipeGallery):
                widget.dispose()

    def _show(self):
        """Retire old media before rebuilding only the opt-in v2 page tree."""
        self._view_revision += 1
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
        if page.name == ADVERT:
            self._build_advert(canvas)
        elif page.name == TUTORIAL:
            self._build_tutorial(canvas)
        elif page.name == TEMPLATES:
            self._build_templates(canvas)
        elif page.name == GAME_PREVIEW:
            self._build_game_notice(canvas)
        else:
            raise RuntimeError("Unknown prototype page")

    def _frame(self, canvas, *, brand_height=100):
        shell = BoxLayout(
            orientation="vertical", padding=[dp(20), dp(18), dp(20), dp(18)],
            spacing=dp(13),
        )
        canvas.add_widget(shell)
        if brand_height:
            shell.add_widget(MeongLogo(size_hint_y=None, height=dp(brand_height)))
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
        def activate():
            # Give feedback before routing/decoder retirement. The short shared
            # click now survives page handoffs; suspend/close still stop it.
            self.audio_v2.cue("button")
            callback()

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

    def _return_ad(self):
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
        headline.add_widget(text_label("PETUALANGAN DIMULAI DI SINI",
                                      size=12, height=34, color=GOLD))
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

        # Cara Pakai enters the already mandatory tutorial and keeps the
        # single-visit gate. Invitation remains a PREVIEW-only operator action.
        tools = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        tools.add_widget(self._action(
            "CARA PAKAI", lambda: self._choose_photo("help"),
            variant="tertiary", height=48))
        tools.add_widget(self._action(
            "UNDANGAN (DEMO)", self._show_invitation,
            variant="tertiary", height=48))
        shell.add_widget(tools)
        shell.add_widget(text_label(
            "Mode iklan aktif saat idle • Game dan QRIS masih prototype",
            size=12, height=31, color=MUTED,
        ))

    def _show_invitation(self):
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
            "AYO FOTO", lambda: self._choose_photo("face_preview"),
            height=50))
        panel.add_widget(self._action(
            "MAIN MEONG FLY", lambda: self._choose_game("face_preview"),
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
        """Dedicated Meong Fly entry screen, *not* a working receipt/game path."""
        # One large shared transparent brand in the hero; no duplicated header.
        shell = self._frame(canvas, brand_height=0)
        shell.add_widget(text_label(
            "MEONG FLY!", size=28, height=58,
            color=GOLD, bold=True))
        shell.add_widget(text_label(
            "TERBANG • HINDARI ASTEROID • KUMPULKAN POIN",
            size=13, height=32, color=CYAN))

        hero = PixelCard(orientation="vertical", padding=10, spacing=6)
        hero.add_widget(MeongLogo(hero=True))
        hero.add_widget(text_label(
            "MAIN SEKALI, MENANG DAPAT DISKON!",
            size=17, height=46, color=CYAN, bold=True))
        shell.add_widget(hero)

        rules = PixelCard(orientation="vertical", size_hint_y=None,
                          height=dp(224), padding=12, spacing=4)
        rules.add_widget(text_label(
            "ATURAN MEONG FLY", size=18, height=38,
            color=GOLD, bold=True))
        rules.add_widget(text_label(
            "01  Satu struk kafe = satu kesempatan main",
            size=14, height=42, color=WHITE, align="left"))
        rules.add_widget(text_label(
            "02  Menang: potensi diskon Rp2.500",
            size=14, height=42, color=WHITE, align="left"))
        rules.add_widget(text_label(
            "03  Setelah game, pilih template foto",
            size=14, height=42, color=WHITE, align="left"))
        rules.add_widget(text_label(
            "SCAN STRUK / DISKON ASLI BELUM TERHUBUNG",
            size=12, height=31, color=MUTED))
        shell.add_widget(rules)

        self._warning_label = text_label(
            "", size=12, height=26, color=GOLD)
        shell.add_widget(self._warning_label)
        shell.add_widget(self._action(
            "LANJUT SCAN STRUK (BELUM AKTIF)",
            lambda: None, disabled=True, height=56))
        shell.add_widget(self._action(
            "LANJUT FOTO TANPA GAME",
            lambda: self._choose_photo("skip_game")))
        shell.add_widget(self._action(
            "KEMBALI KE IKLAN", self._return_ad,
            variant="tertiary", height=48))

    def _build_templates(self, canvas):
        shell = self._frame(canvas, brand_height=64)
        shell.add_widget(text_label(
            "PILIH TEMPLATE STRIP", size=24, height=53,
            color=GOLD, bold=True))
        shell.add_widget(text_label(
            "12 desain asli • 3 foto vertikal + 1 QR untuk download",
            size=13, height=34, color=MUTED))

        deck = PixelCard(orientation="vertical", padding=10, spacing=6)
        deck.add_widget(text_label(
            "GESER PILIHANMU DI GALAKSI MEONG!",
            size=14, height=30, color=CYAN, bold=True))

        gallery = SwipeGallery(on_swipe=self._page_callback(self._swipe_template),
                               orientation="horizontal", spacing=dp(7))
        left = BoxLayout(orientation="vertical", size_hint_x=.22,
                         spacing=dp(2))
        left.add_widget(Widget(size_hint_y=.18))
        self._previous_preview = Image(fit_mode="contain", size_hint_y=.70)
        left.add_widget(self._previous_preview)
        left.add_widget(text_label(
            "SEBELUM", size=12, height=25, color=MUTED))
        left.add_widget(Widget(size_hint_y=.12))
        gallery.add_widget(left)

        middle = BoxLayout(orientation="vertical", size_hint_x=.56)
        self._preview = Image(fit_mode="contain")
        middle.add_widget(self._preview)
        gallery.add_widget(middle)

        right = BoxLayout(orientation="vertical", size_hint_x=.22,
                          spacing=dp(2))
        right.add_widget(Widget(size_hint_y=.18))
        self._next_preview = Image(fit_mode="contain", size_hint_y=.70)
        right.add_widget(self._next_preview)
        right.add_widget(text_label(
            "BERIKUT", size=12, height=25, color=MUTED))
        right.add_widget(Widget(size_hint_y=.12))
        gallery.add_widget(right)
        deck.add_widget(gallery)

        self._template_name = text_label(
            "", size=18, height=39, color=GOLD, bold=True)
        deck.add_widget(self._template_name)
        nav = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(12))
        nav.add_widget(self._action(
            "SEBELUMNYA", lambda: self._shift_template(-1),
            variant="tertiary", height=54))
        nav.add_widget(self._action(
            "BERIKUTNYA", lambda: self._shift_template(1),
            variant="secondary", height=54))
        deck.add_widget(nav)
        shell.add_widget(deck)

        count_card = PixelCard(orientation="vertical", size_hint_y=None,
                               height=dp(166), spacing=5, padding=9)
        count_card.add_widget(text_label(
            "JUMLAH CETAK UNTUK DESAIN INI",
            size=14, height=31, color=CYAN, bold=True))
        row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(12))
        row.add_widget(self._action(
            "-", lambda: self._change_copies(-1),
            variant="tertiary", height=55))
        self._copy_value = text_label(
            "0", size=26, height=55, color=GOLD, bold=True)
        row.add_widget(self._copy_value)
        row.add_widget(self._action(
            "+", lambda: self._change_copies(1),
            variant="secondary", height=55))
        count_card.add_widget(row)
        self._order_summary = text_label(
            "", size=14, height=52, color=WHITE)
        count_card.add_widget(self._order_summary)
        shell.add_widget(count_card)

        self._warning_label = text_label(
            "", size=12, height=25, color=GOLD)
        shell.add_widget(self._warning_label)
        shell.add_widget(self._action(
            "PEMBAYARAN (BELUM TERHUBUNG)",
            lambda: None, disabled=True, height=56))
        shell.add_widget(self._action(
            "SELESAI / KEMBALI IKLAN", self._return_ad,
            variant="tertiary", height=48))
        self._update_template()

    def _swipe_template(self, step):
        self._shift_template(step)
        self.audio_v2.cue("button")

    def _shift_template(self, step):
        self.template_index = (self.template_index + step) % len(self.templates)
        self._activity()
        self._update_template()

    def _change_copies(self, delta):
        template = self.templates[self.template_index]
        old = self.quantities[template.template_id]
        self.quantities[template.template_id] = max(0, min(9, old + delta))
        self._activity()
        self._update_order()

    def _update_template(self):
        template = self.templates[self.template_index]
        previous = self.templates[(self.template_index - 1) % len(self.templates)]
        following = self.templates[(self.template_index + 1) % len(self.templates)]
        self._template_name.text = (
            f"{self.template_index + 1:02d} / {len(self.templates):02d}  •  {template.name}"
        )
        for item in (previous, template, following):
            if item.template_id not in self._textures:
                self._textures[item.template_id] = _portrait_strip_texture(
                    item, self._preview_preloader.get(item))
        self._previous_preview.texture = self._textures[previous.template_id]
        self._preview.texture = self._textures[template.template_id]
        self._next_preview.texture = self._textures[following.template_id]
        self._update_order()

    def _update_order(self):
        template = self.templates[self.template_index]
        self._copy_value.text = str(self.quantities[template.template_id])
        quote = quote_order(self.templates, self.quantities)
        total = f"{quote.total_amount:,}".replace(",", ".")
        self._order_summary.text = (
            f"{quote.session_count} sesi foto  •  {quote.print_copy_count} lembar"
            f"\nSIMULASI DEMO: Rp{total}  •  Bukan tagihan QRIS"
        )
