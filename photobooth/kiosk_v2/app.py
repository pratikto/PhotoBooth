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

from photobooth.advertising import AdCatalog, AdEventLog, PROJECT_ROOT
from photobooth.branding import LOGO_PATH
from photobooth.catalog import create_template_preview, get_templates
from photobooth.ui_ads import AdvertisementPlayer
from photobooth.workflow import quote_order

from .audio import make_kivy_audio
from .flow import ADVERT, BROWSING_PAGES, GAME_PREVIEW, TEMPLATES, TUTORIAL, VisitFlow
from .theme import ArcadeButton, CYAN, GOLD, MUTED, PixelCard, PINK, Starfield, text_label


LOG = logging.getLogger(__name__)


def _portrait_strip_texture(template):
    """Convert only this approved master preview to a GPU texture, preserving 1:3."""
    preview = create_template_preview(template, (180, 540)).convert("RGB")
    texture = Texture.create(size=preview.size, colorfmt="rgb")
    texture.blit_buffer(preview.tobytes(), colorfmt="rgb", bufferfmt="ubyte")
    texture.flip_vertical()
    texture.mag_filter = texture.min_filter = "nearest"
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


class PortraitKioskV2App(App):
    """Separate greenfield window; the original python main.py remains untouched."""

    title = "MEONG PHOTOBOOTH - PORTRAIT GUI V2 (PROTOTIPE)"

    def build(self):
        # Preview hardware dimensions only; actual kiosk fullscreen is deferred
        # until rotation, OS touch calibration and face camera have been tested.
        Window.size = (800, 1280)
        self.navigation = VisitFlow()
        self.templates = get_templates()
        self.catalog = AdCatalog()
        self.events = AdEventLog(PROJECT_ROOT / "data" / "advertising" / "events-v2.jsonl")
        self.audio_v2 = make_kivy_audio()
        self.quantities = {t.template_id: 0 for t in self.templates}
        self.template_index = 0
        self._textures = {}
        self._ad_player = None
        self._invitation = None
        self._invitation_timer = None
        self._warning_label = None
        self._last_activity = time.monotonic()
        self.stage = ScreenManager(transition=NoTransition())
        self._show()
        self._heartbeat = Clock.schedule_interval(self._tick, 1)
        return self.stage

    def on_pause(self):
        self.audio_v2.suspend()
        if self._ad_player is not None:
            self._ad_player.pause()
        return True

    def on_resume(self):
        self.audio_v2.resume()
        if self._ad_player is not None:
            self._ad_player.resume()

    def on_stop(self):
        if getattr(self, "_heartbeat", None):
            self._heartbeat.cancel()
        self._close_invitation()
        self._stop_ad()
        if getattr(self, "audio_v2", None):
            self.audio_v2.close()

    def _activity(self):
        self._last_activity = time.monotonic()
        if self._warning_label is not None:
            self._warning_label.text = ""

    def _tick(self, _dt):
        if self.navigation.page not in BROWSING_PAGES:
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

    def _show(self):
        """Retire old media before rebuilding only the opt-in v2 page tree."""
        self._close_invitation()
        self._stop_ad()
        self._warning_label = None
        self.stage.clear_widgets()
        page = Screen(name=self.navigation.page)
        canvas = TouchStage(self._activity)
        page.add_widget(canvas)
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

    def _frame(self, canvas):
        shell = BoxLayout(
            orientation="vertical", padding=[dp(20), dp(18), dp(20), dp(18)],
            spacing=dp(13),
        )
        canvas.add_widget(shell)
        return shell

    @staticmethod
    def _brand(shell, title, subtitle):
        logo = Image(source=str(LOGO_PATH), fit_mode="contain",
                     size_hint_y=None, height=dp(117))
        shell.add_widget(logo)
        shell.add_widget(text_label(title, size=23, height=37, bold=True, color=GOLD))
        shell.add_widget(text_label(subtitle, size=13, height=40, color=MUTED))

    def _action(self, title, callback, *, variant="primary", height=62, disabled=False):
        button = ArcadeButton(title, variant=variant, height=height)
        button.disabled = disabled
        button.bind(on_release=lambda *_: callback())
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
        shell = self._frame(canvas)
        self._brand(shell, "YOUR NEXT MEMORY STARTS HERE", "Pixel-space photobooth • 3 foto + QR")
        shell.add_widget(text_label("IKLAN / MODE SIAGA", size=14, height=30, color=CYAN))
        creative = PixelCard(orientation="vertical", padding=6, spacing=0)
        media_host = FloatLayout()
        self._ad_player = AdvertisementPlayer(
            self.catalog, "idle", self.events, volume=.55,
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0},
        )
        media_host.add_widget(self._ad_player)
        creative.add_widget(media_host)
        shell.add_widget(creative)
        self._advert_host = media_host
        shell.add_widget(self._action("MULAI FOTO", lambda: self._choose_photo("manual")))
        shell.add_widget(self._action("MAIN MEONG FLY", lambda: self._choose_game("manual"),
                                      variant="secondary"))
        shell.add_widget(self._action("LIHAT UNDANGAN (DEMO)", self._show_invitation,
                                      variant="tertiary", height=48))
        shell.add_widget(text_label(
            "Iklan berjalan saat tidak digunakan. Mini game belum terintegrasi.",
            size=11, height=37, color=MUTED,
        ))

    def _show_invitation(self):
        """Visual preview: actual 5-second camera detector is NOT yet connected."""
        if self.navigation.page != ADVERT:
            return
        self._close_invitation()
        panel = PixelCard(
            orientation="vertical", size_hint=(.95, None), height=dp(228),
            pos_hint={"center_x": .5, "center_y": .48},
            padding=11, spacing=6,
        )
        panel.add_widget(text_label("HAI! MAU FOTO ATAU MAIN?", size=16,
                                    height=37, color=GOLD, bold=True))
        panel.add_widget(text_label("Undangan Meong saat kamu mendekat!",
                                    size=12, height=28))
        panel.add_widget(self._action("AYO FOTO", lambda: self._choose_photo("face_preview"),
                                      height=48))
        panel.add_widget(self._action("MAIN MEONG FLY",
                                      lambda: self._choose_game("face_preview"),
                                      variant="secondary", height=48))
        panel.add_widget(self._action("NANTI SAJA", self._close_invitation,
                                      variant="tertiary", height=33))
        self._advert_host.add_widget(panel)
        self._invitation = panel
        self._ad_player.set_volume(.15)
        self._invitation_timer = Clock.schedule_once(
            self._close_invitation, self.catalog.timing.offer_timeout,
        )

    def _build_tutorial(self, canvas):
        shell = self._frame(canvas)
        self._brand(shell, "CARA PAKAI MEONG", "Wajib sekali per kunjungan sebelum memilih template")
        guide = ScrollView(size_hint_y=1, bar_width=dp(3), do_scroll_x=False)
        stack = BoxLayout(orientation="vertical", size_hint_y=None,
                          spacing=dp(13), padding=[dp(4), dp(7), dp(4), dp(11)])
        stack.bind(minimum_height=stack.setter("height"))
        steps = (
            ("01  PILIH TEMPLATE", "Pilih dari 12 strip thermal 3 foto + QR."),
            ("02  LAKUKAN PEMBAYARAN", "Bayar melalui mode pembayaran yang tersedia."),
            ("03  AMBIL 3 FOTO", "Berpose tiga kali. Ada 1 kesempatan retake."),
            ("04  CETAK DAN SCAN", "Ambil strip 80 x 240 mm dan scan QR foto."),
        )
        for title, detail in steps:
            panel = PixelCard(
                orientation="vertical", size_hint_y=None,
                height=dp(106), padding=11, spacing=4,
            )
            panel.add_widget(text_label(title, size=18, height=41, color=CYAN, bold=True))
            panel.add_widget(text_label(detail, size=13, height=45, color=MUTED))
            stack.add_widget(panel)
        guide.add_widget(stack)
        shell.add_widget(guide)
        self._warning_label = text_label("", size=12, height=31, color=GOLD)
        shell.add_widget(self._warning_label)
        shell.add_widget(self._action("LANJUT PILIH TEMPLATE", self._complete_tutorial))
        shell.add_widget(self._action("BATAL / KEMBALI IKLAN", self._return_ad,
                                      variant="tertiary", height=48))

    def _complete_tutorial(self):
        self.navigation.complete_tutorial()
        self._activity()
        self._show()

    def _build_game_notice(self, canvas):
        shell = self._frame(canvas)
        self._brand(shell, "MEONG FLY!", "Mini game dan diskon Rp2.500 — belum terhubung")
        shell.add_widget(text_label("PENGEMBANGAN TERPISAH", size=17,
                                    height=42, color=CYAN, bold=True))
        info = PixelCard(orientation="vertical", padding=18, spacing=8)
        info.add_widget(text_label(
            "MEONG FLY MASIH DEMO",
            size=22, height=57, color=GOLD, bold=True,
        ))
        info.add_widget(text_label(
            "Game berada di branch feature/meong-flappy-challenge.",
            size=15, height=80, color=MUTED,
        ))
        info.add_widget(text_label(
            "Belum ada scan struk kafe asli, permainan di dalam GUI ini,"
            " atau diskon yang berlaku di QRIS.",
            size=14, height=120,
        ))
        shell.add_widget(info)
        shell.add_widget(self._action("LANJUT FOTO TANPA GAME",
                                      lambda: self._choose_photo("skip_game")))
        shell.add_widget(self._action("KEMBALI KE IKLAN", self._return_ad,
                                      variant="tertiary"))

    def _build_templates(self, canvas):
        shell = self._frame(canvas)
        shell.add_widget(text_label("PILIH TEMPLATE STRIP", size=23, height=53,
                                    color=GOLD, bold=True))
        shell.add_widget(text_label("12 desain asli • 3 foto + 1 QR download",
                                    size=13, height=34, color=MUTED))
        deck = PixelCard(orientation="vertical", padding=10, spacing=5)
        self._preview = Image(fit_mode="contain")
        deck.add_widget(self._preview)
        self._template_name = text_label("", size=17, height=36, color=CYAN, bold=True)
        deck.add_widget(self._template_name)
        nav = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        nav.add_widget(self._action("◀ SEBELUMNYA", lambda: self._shift_template(-1),
                                    variant="tertiary", height=52))
        nav.add_widget(self._action("BERIKUTNYA ▶", lambda: self._shift_template(1),
                                    variant="secondary", height=52))
        deck.add_widget(nav)
        shell.add_widget(deck)
        count_card = PixelCard(orientation="vertical", size_hint_y=None,
                               height=dp(146), spacing=5)
        count_card.add_widget(text_label("JUMLAH CETAK TEMPLATE INI",
                                         size=13, height=31, color=MUTED))
        row = BoxLayout(size_hint_y=None, height=dp(53), spacing=dp(12))
        row.add_widget(self._action("−", lambda: self._change_copies(-1),
                                     variant="tertiary", height=53))
        self._copy_value = text_label("0", size=24, height=53, color=GOLD, bold=True)
        row.add_widget(self._copy_value)
        row.add_widget(self._action("+", lambda: self._change_copies(1),
                                     variant="secondary", height=53))
        count_card.add_widget(row)
        self._order_summary = text_label("", size=13, height=28)
        count_card.add_widget(self._order_summary)
        shell.add_widget(count_card)
        self._warning_label = text_label("", size=12, height=25, color=GOLD)
        shell.add_widget(self._warning_label)
        shell.add_widget(self._action("PEMBAYARAN (BELUM TERHUBUNG)",
                                      lambda: None, disabled=True, height=56))
        shell.add_widget(self._action("SELESAI / KEMBALI IKLAN", self._return_ad,
                                      variant="tertiary", height=48))
        self._update_template()

    def _shift_template(self, step):
        self.template_index = (self.template_index + step) % len(self.templates)
        self.audio_v2.cue()
        self._activity()
        self._update_template()

    def _change_copies(self, delta):
        template = self.templates[self.template_index]
        old = self.quantities[template.template_id]
        self.quantities[template.template_id] = max(0, min(9, old + delta))
        self.audio_v2.cue()
        self._activity()
        self._update_template()

    def _update_template(self):
        template = self.templates[self.template_index]
        self._template_name.text = (
            f"{self.template_index + 1:02d} / {len(self.templates):02d} • {template.name}"
        )
        if template.template_id not in self._textures:
            self._textures[template.template_id] = _portrait_strip_texture(template)
        self._preview.texture = self._textures[template.template_id]
        self._copy_value.text = str(self.quantities[template.template_id])
        quote = quote_order(self.templates, self.quantities)
        self._order_summary.text = (
            f"{quote.session_count} sesi • {quote.print_copy_count} lembar • "
            f"DEMO Rp{quote.total_amount:,}".replace(",", ".")
        )
