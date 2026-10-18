"""Kivy presentation layer for the existing PhotoBooth controller.

This module deliberately keeps the controller-facing method names used by the
historical Tkinter UI. Workflow rules and Drive operations remain outside the
widgets. All texture creation and widget changes run on Kivy's main thread.
The desktop Camera implementation is retained; this migration alone is NOT an
Android camera/USB driver implementation or an Android packaging configuration.
"""

from pathlib import Path

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from photobooth.printer import PrinterConfig, DITHER_MODES
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from PIL import Image
from photobooth.audio import AudioManager
from photobooth.ui_kiosk import KioskExperienceMixin
from photobooth.ui_motion import CountdownDial, FlashEffect, GuideGlyph, MotionScope
from photobooth.catalog import PRICE_PER_SESSION, create_template_preview, render_photo_frame
from photobooth.ui_brand import (
    BLUSH, BLUE, CYAN, DISABLED_INK, EDGE, GREY, INK, PAPER, ROSE, SOFT, WHITE,
    BrandLockup, CarouselDots, FlowSteps, Panel, PixelRule, ReceiptSlide,
    TemplateCarousel, brand_parts, picture,
)

# Historical names remain public for hosts that imported the old tokens. Their
# values now belong to MEONG's lens-blue visual system, not the old sage theme.
SAGE = BLUE
CORAL = ROSE

class KivyHost(App):
    """Own the native window and translate controller timers to Kivy Clock.

    ``after`` uses milliseconds to preserve the controller's existing timing
    contract, while Clock uses seconds. It returns a ClockEvent (not a Tk ID).
    Keeping that event lets shutdown cancel precisely the scheduled callback.
    """

    def __init__(self, on_close):
        super().__init__()
        self.title = 'Meong Photobooth'
        self._on_close = on_close
        self.view = None
        # Desktop starts with a useful kiosk-sized canvas. Responsive layouts
        # below still support resizing; Android owns its window dimensions.
        from kivy.utils import platform
        if platform in {'win', 'linux', 'macosx'}:
            Window.size = (1200, 800)

    def build(self):
        """Return the widget tree prepared by PhotoBoothUI before App.run()."""
        Window.clearcolor = PAPER
        # Preparation can begin while Kivy attaches its root. on_start repeats
        # this idempotently, so both normal and explicitly built hosts start
        # audio; playback itself still waits for the main-thread Clock poll.
        if getattr(self, "ui", None) is not None:
            self.ui.audio.start()
        return self.view

    def on_start(self):
        """Start the persistent song after Kivy has entered its native loop."""
        if getattr(self, "ui", None) is not None:
            self.ui.audio.start()

    def on_pause(self):
        """Stop speakers when the host is backgrounded; allow native resume."""
        if getattr(self, "ui", None) is not None:
            self.ui.pause_media()
        return True

    def on_resume(self):
        if getattr(self, "ui", None) is not None:
            self.ui.resume_media()

    def after(self, milliseconds, callback):
        """Schedule without sleeping, so preview and touch input keep working."""
        return Clock.schedule_once(lambda _dt: callback(), milliseconds / 1000)

    def after_cancel(self, event):
        """Cancel a ClockEvent; cancellation is safe even after it has fired."""
        event.cancel()

    def mainloop(self):
        """Start Kivy through the controller's existing entry-point contract."""
        self.run()

    def destroy(self):
        """Stop the event loop; on_stop will invoke idempotent controller cleanup."""
        self.stop()

    def on_stop(self):
        """Release camera/worker resources for both window-X and programmatic exit."""
        if getattr(self, 'ui', None) is not None:
            self.ui.dispose()
        self._on_close()


class PhotoBoothUI(KioskExperienceMixin):
    """Kiosk screens; controller callbacks remain the source of workflow rules.

    The layout uses a stable header, a flexible stage, and fixed action controls.
    Galleries and long details scroll inside the stage, keeping primary actions
    reachable. Breakpoints depend on available width, not the operating system.
    """

    def __init__(self, root, templates, *, audio_manager=None, kiosk_data_dir=None, **callbacks):
        root.ui = self
        self.audio = audio_manager if audio_manager is not None else AudioManager(
            Path(__file__).resolve().parent.parent / "data" / "audio")
        self._audio_popup = None
        self.audio_sliders = {}
        self.audio_test_buttons = {}
        self._motion = MotionScope()
        self._last_countdown_value = None
        self.countdown_dial = None
        self._disposed = False
        self.templates = tuple(templates)
        self.callbacks = callbacks
        self._screen_revision = 0
        self.current_screen = 'welcome'
        self._camera_ready = False
        self._storage_ready = False
        self.preview = None
        self.live_caption = None
        self.camera_wait_hint = None
        self.capture_hint = None
        self._capture_running = False
        self._palm_state = 'disabled'
        self._palm_progress = 0.0
        self._palm_needs_release = False
        self.home_start_button = None
        self._review_can_retake = False
        self._review_has_retake = False
        self._payment_submitted = False
        self.qr_view = None
        self._qr_bytes = None
        self._result_detail_popup = None
        self.print_status = None
        self.print_button = None
        self.template_carousel = None
        self._last_template_index = 0
        self.shell = Panel(fill=PAPER, radius=0, border=False, orientation='vertical',
                           padding=dp(24), spacing=dp(12))
        root.view = self.shell
        self._flash = FlashEffect(self.shell)
        header = Panel(fill=WHITE, radius=14, border=False, size_hint_y=None,
                       height=dp(82), padding=(dp(18), dp(10)), spacing=dp(12))
        self._header_row = header
        # The approved pixel mascot and original wordmark replace the typed
        # generic header. Their display crops never change the QR's logo file.
        self.brand = BrandLockup(size_hint_x=None, width=dp(280))
        header.add_widget(self.brand)
        header.add_widget(Widget())
        self.steps = FlowSteps(size_hint=(None, None), width=dp(380),
                               height=dp(38), pos_hint={'center_y': .5})
        header.add_widget(self.steps)
        # This header belongs to the application, so the settings control is
        # present on every page and does not inherit a retired page revision.
        self.settings_button = self._button("", self.show_settings_menu,
                                            secondary=True, screen_bound=False)
        self.settings_button.size_hint = (None, None)
        self.settings_button.size = (dp(48), dp(44))
        self.settings_button.pos_hint = {"center_y": .5}
        self._attach_icon(self.settings_button, "gear", icon_only=True)
        header.add_widget(self.settings_button)
        self.shell.add_widget(header)
        self.content = BoxLayout(orientation='vertical', spacing=dp(10), pos_hint={'x': 0, 'y': 0})
        # An internal overlay layer keeps invitations inside this same native
        # window. Payment offers use a narrower host in the advertising column.
        self._page_stack = FloatLayout()
        self._page_stack.add_widget(self.content)
        self.shell.add_widget(self._page_stack)
        footer = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(12))
        self._footer_row = footer
        self.status = self._label('', 12, color=GREY)
        # The footer is intentionally one line. Keep its full text available to
        # controller recovery while replacing visual overflow with an ellipsis.
        # A separate, persistent action opens the unabridged diagnostic below.
        self.status.shorten = True
        self.status.shorten_from = 'right'
        self.status.max_lines = 1
        footer.add_widget(self.status)
        self.status_details = self._button('DETAIL', self._show_status_details, enabled=False,
                                           secondary=True, screen_bound=False)
        self.status_details.size_hint_x = None
        self.status_details.width = dp(72)
        self.status_details.size_hint_y = 1
        self.status_details.font_size = dp(12)
        self._status_measure_key = None
        self._status_natural_width = 0
        self.camera_badge = self._label('Kamera diperiksa', 12, color=GREY, align='right')
        self.camera_badge.size_hint_x = None
        self.camera_badge.width = dp(170)
        footer.add_widget(self.camera_badge)
        # Insert the details action only when needed. An invisible zero-width
        # child would still add BoxLayout spacing and squeeze normal statuses.
        footer.bind(size=self._fit_status)
        self.camera_badge.bind(width=self._fit_status)
        self.shell.add_widget(footer)
        self.header = self.brand  # Historical public handle retained for callers.
        self._page_title = self._page_subtitle = None
        self.shell.bind(size=self._fit_chrome, parent=self._on_shell_parent)
        self._fit_chrome()
        self._init_kiosk(kiosk_data_dir)

    def _on_shell_parent(self, *_args):
        """Only a mounted kiosk page owns a recurring illustration timer."""
        if self.shell.get_root_window() is not None:
            self._motion.activate()
        else:
            self._motion.suspend()

    def _fit_chrome(self, *_args):
        """Fit the brand shell without letting a wide monitor stretch the UI.

        The screenshot's 1920-pixel desktop previously produced huge empty
        cards. Cap the content width at 1440 dp and center it with outer gutters.
        Short-screen spacing retains the camera/QR minimum sizes at 800×600.
        """
        compact = self.shell.height < dp(700)
        is_advert = self.current_screen == 'advert'
        # The opening advertising placement is our largest visual surface.
        # Regular photo/checkout pages retain the narrower 1440dp layout, but
        # idle media uses nearly the whole window, including wide desktops.
        # We keep the persistent logo/settings header and the manual Start
        # controls, rather than using a fullscreen overlay that would block
        # either the face invitation or operator settings.
        max_width = 1920 if is_advert else 1440
        gutter = max(dp(8 if is_advert else (16 if compact else 28)),
                     (self.shell.width - dp(max_width)) / 2)
        vertical_top = 8 if is_advert else (12 if compact else 24)
        vertical_bottom = 6 if is_advert else (8 if compact else 20)
        self.shell.padding = (gutter, dp(vertical_top), gutter, dp(vertical_bottom))
        self.shell.spacing = dp(6 if is_advert else (10 if compact else 16))
        self._header_row.height = dp((54 if compact else 64) if is_advert else
                                     (64 if compact else 82))
        self._header_row.padding = (dp(14), dp(8 if compact else 10))
        self.brand.width = dp(216 if compact else 260)
        self.brand.mascot.width = dp(82 if compact else 100)
        self.steps.width = dp(306 if compact else 350)
        self.steps.height = dp(34 if compact else 38)
        self._footer_row.height = dp(22 if compact else 28)
        self.camera_badge.width = dp(132 if compact else 170)
        if self._page_title is not None:
            self._page_title.height = dp(36 if compact else 46)
            self._page_title.font_size = dp(24 if compact else 32)
            self._title_row.height = self._page_title.height
        if self._page_subtitle is not None:
            self._page_subtitle.height = dp(26 if compact else 34)

    def _label(self, text, font=18, height=None, bold=False, color=INK, align='left',
               auto_height=False):
        """Wrap text within its box instead of letting it overlap adjacent controls."""
        widget = Label(text=text, color=color, font_size=dp(font), bold=bold,
                       halign=align, valign='middle')
        if auto_height:
            # A scrolling paragraph must measure its natural height from width
            # alone. Binding text_size to (width, height) creates a feedback loop
            # that clips the final order line even when the viewport has room.
            widget.size_hint_y = None
            widget.bind(width=lambda w, width: setattr(w, 'text_size', (width, None)),
                        texture_size=lambda w, size: setattr(w, 'height', size[1]))
        else:
            widget.bind(size=lambda w, size: setattr(w, 'text_size', size))
        if height is not None and not auto_height:
            widget.size_hint_y = None
            widget.height = dp(height)
        return widget

    def _button(self, text, callback, enabled=True, secondary=False, screen_bound=True,
                inverse=False, play_click=True):
        """Create a touch action owned by this exact revision of the screen.

        Touch grabs and queued releases can outlive a widget's visible parent.
        Checking only the page name is insufficient when another customer or an
        edited order reaches a page with the same name. Invalidate retired page
        actions and recheck disabled state at callback delivery. Only modal close
        controls opt out: their popup can legitimately outlive a page change.
        """
        widget = Button(text=text, size_hint_y=None, height=dp(52),
                        background_normal='', background_down='',
                        background_disabled_normal='', background_disabled_down='',
                        background_color=SOFT if secondary else SAGE,
                        color=BLUE if inverse else (INK if secondary else WHITE),
                        disabled_color=DISABLED_INK,
                        font_size=dp(14), bold=True, disabled=not enabled)
        # Disabled captions still convey information such as "DIGANTI" and
        # "RETAKE SUDAH DIGUNAKAN". The default translucent atlas plus faint ink
        # reduced painted contrast below 2:1. Use our flat edge/ink tokens for a
        # quiet but readable state, and restore the exact primary/secondary fill
        # when camera readiness or quantity changes re-enable this same widget.
        def update_fill(button, disabled):
            # Camera/storage readiness can change while a pointer is held.
            # Restore readable disabled ink even if no release is delivered.
            if disabled:
                Animation.cancel_all(button, "opacity")
                button.opacity = 1
            button.background_color = EDGE if disabled else (
                WHITE if inverse else (SOFT if secondary else BLUE))
        widget.bind(disabled=update_fill)
        update_fill(widget, widget.disabled)
        revision = self._screen_revision
        def release(button):
            if button.disabled or (screen_bound and revision != self._screen_revision):
                return
            self._kiosk_activity()
            # Audio-test controls must emit only their own requested sample.
            # Ordinary UI controls retain the existing tactile click effect.
            if play_click:
                self.audio.play("button")
            Animation.cancel_all(button, "opacity")
            Animation(opacity=1, duration=.10).start(button)
            return callback()
        def press(button):
            if not button.disabled and (not screen_bound or revision == self._screen_revision):
                Animation.cancel_all(button, "opacity")
                Animation(opacity=.76, duration=.06).start(button)
        widget.bind(on_press=press, on_release=release)
        # Long translated labels wrap rather than overflowing a narrow button.
        widget.bind(size=lambda w, size: setattr(w, 'text_size', (size[0] - dp(16), size[1])))
        widget.halign = 'center'
        widget.valign = 'middle'
        return widget

    def _attach_icon(self, button, kind, *, icon_only=False):
        """Use a drawn symbol instead of platform-dependent emoji glyphs."""
        icon = GuideGlyph(kind=kind, size_hint=(None, None), size=(dp(28), dp(28)))
        def arrange(*_args):
            icon.center = (button.x + button.width / 2 if icon_only else button.x + dp(30),
                           button.y + button.height / 2)
        button.bind(pos=arrange, size=arrange)
        button.add_widget(icon)
        arrange()
        button.icon_widget = icon
        return button

    @property
    def audio_settings_open(self):
        """A modal blocks the optional palm shutter as well as pointer input."""
        return self._audio_popup is not None

    def show_settings_menu(self):
        """Keep printer and audio configuration accessible from every page."""
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(14))
        popup = Popup(title="Pengaturan Meong", content=content,
                      size_hint=(None, None), size=(dp(430), dp(280)))
        audio = self._button("PENGATURAN AUDIO", lambda: (popup.dismiss(), self.show_audio_settings()),
                             screen_bound=False)
        printer = self._button("PENGATURAN PRINTER", lambda: (popup.dismiss(), self.show_printer_settings()),
                               screen_bound=False)
        close = self._button("TUTUP", popup.dismiss, secondary=True, screen_bound=False)
        for widget in (audio, printer, close):
            content.add_widget(widget)
        popup.open()

    def show_printer_settings(self):
        """Edit the current printer route, width and dithering in one modal.

        The modal saves only after validation; an invalid form retains the
        previous working printer and displays an inline error.
        """
        callback = self.callbacks.get("on_printer_save")
        getter = self.callbacks.get("get_printer_config")
        if callback is None or getter is None:
            return
        current = getter()
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        scroll = ScrollView(do_scroll_x=False)
        fields = BoxLayout(orientation="vertical", size_hint_y=None,
                           spacing=dp(8))
        fields.bind(minimum_height=fields.setter("height"))
        scroll.add_widget(fields)
        content.add_widget(scroll)
        def field(label, value):
            fields.add_widget(self._label(label, 14, 24, color=INK))
            widget = TextInput(text=str(value), multiline=False,
                               size_hint_y=None, height=dp(42))
            fields.add_widget(widget)
            return widget
        route = Spinner(text=("USB Windows" if current.windows_printer_name else
                              "LAN" if current.lan_host else
                              "Wi-Fi" if current.wifi_host else "USB Windows"),
                        values=("USB Windows", "LAN", "Wi-Fi"),
                        size_hint_y=None, height=dp(48))
        fields.add_widget(self._label("Koneksi utama", 15, 26, bold=True))
        fields.add_widget(route)
        name = field("Nama antrean Windows (USB)", current.windows_printer_name or "POS80 Printer")
        lan = field("IP LAN", current.lan_host)
        wifi = field("IP Wi-Fi", current.wifi_host)
        port = field("Port TCP (LAN / Wi-Fi)", current.lan_port)
        width = Spinner(text=str(current.print_width_dots), values=("576", "384"),
                        size_hint_y=None, height=dp(45))
        fields.add_widget(self._label("Lebar cetak (dots)", 14, 24))
        fields.add_widget(width)
        dither = Spinner(text=current.dither_mode, values=DITHER_MODES,
                         size_hint_y=None, height=dp(45))
        fields.add_widget(self._label("Dithering foto", 14, 24))
        fields.add_widget(dither)
        status = self._label("", 12, 38, color=ROSE)
        content.add_widget(status)
        actions = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        popup = Popup(title="Printer Thermal", content=content,
                      size_hint=(.85, .9))
        def save():
            try:
                port_number = int(port.text.strip())
                if not 1 <= port_number <= 65535:
                    raise ValueError("Port harus antara 1 dan 65535.")
                selected = route.text
                host = (lan.text if selected == "LAN" else
                        wifi.text if selected == "Wi-Fi" else "")
                if selected != "USB Windows" and not host.strip():
                    raise ValueError("IP printer wajib diisi.")
                if selected == "USB Windows" and not name.text.strip():
                    raise ValueError("Nama printer Windows wajib diisi.")
                from dataclasses import replace
                config = replace(current,
                                 windows_printer_name=name.text.strip() if selected == "USB Windows" else "",
                                 lan_host=lan.text.strip() if selected == "LAN" else "",
                                 wifi_host=wifi.text.strip() if selected == "Wi-Fi" else "",
                                 lan_port=port_number, wifi_port=port_number,
                                 print_width_dots=int(width.text),
                                 dither_mode=dither.text)
                callback(config)
            except (ValueError, OSError) as error:
                status.text = str(error)
                return
            popup.dismiss()
        # A test always uses the last saved configuration, not unsaved fields.
        def test_print():
            runner = self.callbacks.get("on_printer_test")
            if runner is None:
                status.text = "Test print belum tersedia."
                return
            status.text = "Mengirim test print..."
            runner(lambda message: setattr(status, "text", message))
        actions.add_widget(self._button("TEST PRINT", test_print, secondary=True,
                                        screen_bound=False))
        actions.add_widget(self._button("BATAL", popup.dismiss, secondary=True,
                                        screen_bound=False))
        actions.add_widget(self._button("SIMPAN", save, screen_bound=False))
        content.add_widget(actions)
        popup.open()

    def _test_audio_channel(self, sound):
        """Report a real test-button tap before trying native audio playback.

        The report also distinguishes input/touch problems from mixer failures.
        Keep the button on the existing main-thread Kivy callback path.
        """
        import logging
        logging.getLogger(__name__).info("Meong audio test tapped: %s", sound)
        self._audio_last_test = f"Uji {sound}: tombol diterima"
        if sound == "music":
            # A status of 'play' does not mean the Windows speaker is audible.
            # Explicitly restart the music handle for a meaningful audition,
            # rather than just returning from AudioManager._ensure_music().
            started = self.audio.preview_music()
            self._audio_last_test += (
                " · musik diulang, dengarkan speaker" if started
                else " · musik tidak dapat diputar, periksa status")
        else:
            self.audio.play(sound)
        if getattr(self, "audio_status_label", None) is not None:
            self.audio_status_label.text = (
                f"Uji {sound} dipencet | {self.audio.summary}")
        if getattr(self, "audio_diagnostic_label", None) is not None:
            self.audio_diagnostic_label.text = self.audio.diagnostic

    def show_audio_settings(self):
        """Adjust application buses and ad volume without leaving the page."""
        if self._audio_popup is not None:
            return self._audio_popup
        self._audio_last_test = "Belum ada tombol Uji yang dipencet"
        body = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4),
                            scroll_timeout=80, scroll_distance=dp(18))
        controls_body = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        controls_body.bind(minimum_height=controls_body.setter('height'))
        scroll.add_widget(controls_body)
        body.add_widget(scroll)
        controls_body.add_widget(self._label("Atur suasanamu", 23, 30, bold=True))
        self.audio_sliders = {}
        self.audio_test_buttons = {}
        for channel, title, icon_name, sample in (
                ("music", "Musik", "music", "music"),
                ("buttons", "Tombol", "tap", "button"),
                ("effects", "Efek kamera", "camera", "shutter"),
                ("ads", "Iklan awal", "music", None)):
            row = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(8))
            row.add_widget(GuideGlyph(kind=icon_name, size_hint_x=None, width=dp(32)))
            row.add_widget(self._label(title, 16, bold=True))
            percent = self._label("", 14, align="right", color=BLUE)
            percent.size_hint_x = None
            percent.width = dp(56)
            row.add_widget(percent)
            controls_body.add_widget(row)
            controls = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
            slider = Slider(min=0, max=1, step=.01, value=getattr(self.audio.levels, channel),
                            cursor_size=(dp(26), dp(26)), value_track=True,
                            value_track_color=BLUE)
            def update(_slider, value, key=channel, caption=percent):
                self.audio.set_volume(key, value)
                self._update_ad_volume()
                caption.text = f"{round(value * 100)}%"
            slider.bind(value=update)
            # Set the first caption directly; opening a menu does not rewrite
            # preferences or restart a currently playing song.
            percent.text = f"{round(slider.value * 100)}%"
            self.audio_sliders[channel] = slider
            controls.add_widget(slider)
            if sample is not None:
                test = self._button(
                    "Uji", lambda sound=sample: self._test_audio_channel(sound),
                    secondary=True, screen_bound=False, play_click=False)
                test.size_hint_x = None
                test.width = dp(64)
                test.height = dp(44)
                controls.add_widget(test)
                self.audio_test_buttons[channel] = test
            controls_body.add_widget(controls)
        controls_body.add_widget(self._label("0% = hening", 12, 18, color=GREY))
        # Poll only while this modal is open. Read the manager's live summary
        # so loading failures and an intentionally muted mix are visible.
        self.audio_status_label = self._label(self.audio.summary, 12, 36, color=GREY)
        controls_body.add_widget(self.audio_status_label)
        # Debug readout is intentionally visible in Settings: it distinguishes
        # a stopped/zero-gain mixer from an OS output-routing problem.
        self.audio_diagnostic_label = self._label(
            self.audio.diagnostic, 11, 48, color=GREY)
        controls_body.add_widget(self.audio_diagnostic_label)
        retry = self._button("COBA AUDIO LAGI", self.audio.retry,
                             secondary=True, screen_bound=False)
        retry.height = dp(36)
        controls_body.add_widget(retry)
        self.audio_retry_button = retry
        def refresh_audio_status(_dt):
            self.audio_status_label.text = self._audio_last_test + "\n" + self.audio.summary
            self.audio_diagnostic_label.text = self.audio.diagnostic
            return self._audio_popup is not None
        status_event = Clock.schedule_interval(refresh_audio_status, .2)
        popup = Popup(title="Suara", content=body, size_hint=(None, None),
                      auto_dismiss=False, background="", background_color=PAPER,
                      title_color=INK, separator_color=EDGE)
        def fit_popup(*_args):
            popup.size = (min(dp(520), Window.width - dp(24)),
                          min(dp(590), Window.height - dp(24)))
        fit_popup()
        Window.bind(size=fit_popup)
        save = self._button("SIMPAN", popup.dismiss, screen_bound=False)
        save.height = dp(44)
        body.add_widget(save)
        def dismissed(_popup):
            status_event.cancel()
            Window.unbind(size=fit_popup)
            self.audio.save_settings()
            if self._audio_popup is popup:
                self._audio_popup = None
                self.audio_sliders = {}
                self.audio_test_buttons = {}
        popup.bind(on_dismiss=dismissed)
        self._audio_popup = popup
        popup.open()
        return popup

    def notify_photo_captured(self):
        """A successful camera save owns one shutter sound and one short flash."""
        self.audio.play("shutter")
        self.audio.set_capture_active(False)
        self._flash.pulse()

    def dispose(self):
        """Release page motion and speakers when the native window is closed."""
        if self._disposed:
            return
        self._disposed = True
        self._dispose_kiosk()
        if self._audio_popup is not None:
            self._audio_popup.dismiss(animation=False)
        self._motion.retire()
        if self.template_carousel is not None:
            self.template_carousel.deactivate()
        self._flash.close()
        self.audio.close()

    def _reset(self, screen, title, subtitle=''):
        """Discard only screen widgets, keeping shell/footer and controller state."""
        # A page owns every decoder and visual clock. Retire them before
        # replacing widgets; otherwise hidden video could keep playing audio.
        self._retire_kiosk_page()
        if self.current_screen == 'payment' and screen != 'payment':
            attempt = self.payment.current
            if attempt is not None:
                self.qris_printer.cancel(attempt.attempt_id)
                if self.payment.check() == 'paid':
                    self.payment.current = None
                else:
                    self.payment.release()
        self.audio.set_advertising(screen == 'advert')
        self._motion.retire()
        if self.countdown_dial is not None:
            Animation.cancel_all(self.countdown_dial.label)
        self._motion = MotionScope(active=self.shell.get_root_window() is not None)
        self.countdown_dial = None
        self._last_countdown_value = None
        self.audio.set_capture_active(False)
        if self._audio_popup is not None:
            self._audio_popup.dismiss(animation=False)
        # Completion can return to advertising while a customer inspects the strip.
        # Retire that modal with the result page so the next session cannot be
        # blocked by, or accidentally display, the previous customer's photos.
        if self._result_detail_popup is not None:
            self._result_detail_popup.dismiss(animation=False)
            self._result_detail_popup = None
        self.print_status = None
        self.print_button = None
        if self.template_carousel is not None:
            self.template_carousel.deactivate()
            self.template_carousel = None
        self._screen_revision += 1
        self.current_screen = screen
        if screen == 'welcome':
            self._last_template_index = 0
        self.content.clear_widgets()
        self.preview = None
        self.live_caption = None
        self.camera_wait_hint = None
        self.capture_hint = None
        self._capture_running = False
        self.home_start_button = None
        self._review_can_retake = False
        self._review_has_retake = False
        self.qr_view = None
        self._qr_bytes = None
        self._page_title = self._page_subtitle = None
        self.set_status('')
        active = {'welcome': 1, 'templates': 1, 'payment': 2,
                  'capture': 3, 'review': 3, 'result': 4}.get(screen, 1)
        self.steps.set_active(active)
        self.steps.opacity = 0 if screen == 'advert' else 1
        if title:
            self._page_title = self._label(title, 28, 46, bold=True)
            title_row = BoxLayout(size_hint_y=None, height=self._page_title.height,
                                  spacing=dp(10))
            # A small animated pictogram makes the current action recognizable
            # before reading its title. It never covers the QR or live image.
            glyph = self._motion.add(GuideGlyph(
                kind={"templates": "frames", "payment": "pay", "capture": "camera",
                      "review": "review", "result": "result"}.get(screen, "camera"),
                size_hint_x=None, width=dp(46)))
            title_row.add_widget(glyph)
            title_row.add_widget(self._page_title)
            self._title_row = title_row
            self.content.add_widget(title_row)
        if subtitle:
            self._page_subtitle = self._label(subtitle, 14, 38, color=GREY)
            self.content.add_widget(self._page_subtitle)
        self._fit_chrome()
        self._motion.enter(self.content)
        return self.content

    def _responsive_row(self, left, right, right_width=330, min_height=300):
        """Make side-by-side cards scroll safely on narrow or short windows.

        The inner layout has an explicit minimum height. This prevents fixed
        captions or buttons from squeezing a QR or camera preview to zero height.
        On phone-width windows, panels stack and can be scrolled vertically.
        """
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(5), scroll_type=['bars', 'content'],
                            always_overscroll=False)
        row = BoxLayout(spacing=dp(16), size_hint_y=None)
        row.add_widget(left)
        row.add_widget(right)
        scroll.add_widget(row)
        def arrange(*_args):
            compact = scroll.width < dp(720)
            row.orientation = 'vertical' if compact else 'horizontal'
            row.height = max(scroll.height, dp(min_height * 2 + 16 if compact else min_height))
            # A desktop row that already fits must pass touch-down directly to
            # the nested horizontal carousel. An unnecessary outer scroll grab
            # otherwise consumes a quick swipe before the carousel sees it.
            scroll.do_scroll_y = row.height > scroll.height + 1
            right.size_hint_x = 1 if compact else None
            right.width = scroll.width if compact else dp(right_width)
            left.size_hint_y = right.size_hint_y = 1
        scroll.bind(size=arrange)
        arrange()
        return scroll

    def _actions(self, *buttons):
        """Keep related actions in one reachable row instead of two tall bars.

        Secondary actions come first and the main action stays on the right.
        Both retain a 52dp touch target; no action is hidden inside a scroller.
        """
        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        for button in buttons:
            row.add_widget(button)
        return row

    def _display(self, image, widget=None, crisp=False):
        """Convert Pillow pixels to a reusable Kivy texture on the GUI thread.

        Vertical texture coordinates differ from Pillow's row order. Flip UVs
        once when a texture is created. QR uses nearest filtering and keeps the
        source image's white quiet zone; regular photos use normal filtering.
        """
        widget = widget if widget is not None else KivyImage(fit_mode='contain')
        rgb = image.convert('RGB')
        texture = widget.texture
        if texture is None or texture.size != rgb.size:
            texture = Texture.create(size=rgb.size, colorfmt='rgb')
            texture.flip_vertical()
        if crisp:
            texture.mag_filter = texture.min_filter = 'nearest'
        texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        widget.texture = texture
        widget.canvas.ask_update()
        return widget

    def set_status(self, message):
        """Keep complete feedback while fitting its summary into the footer.

        Measure with the text provider's CPU extents, not a natural-width GPU
        texture: a long backend diagnostic can exceed the graphics size limit.
        Cache the latest measurement because preview/retry polls repeat messages.
        """
        self.status.text = message
        key = (message, self.status.font_name, self.status.font_size)
        if key != self._status_measure_key:
            measure = CoreLabel(font_name=self.status.font_name, font_size=self.status.font_size)
            self._status_natural_width = measure.get_extents(message.replace('\n', ' '))[0]
            self._status_measure_key = key
        self._fit_status()

    def _fit_status(self, *_args):
        """Show details for overflow without a width-dependent toggle loop.

        Decide against the space available WITHOUT the details action. Testing
        the already shortened label width would make the action oscillate near
        the breakpoint after it consumes its own width and extra spacing.
        """
        footer = self._footer_row
        available = max(0, footer.width - self.camera_badge.width - footer.spacing)
        message = self.status.text
        needed = bool(message.strip()) and ('\n' in message or self._status_natural_width > available)
        self.status_details.disabled = not needed
        if needed and self.status_details.parent is None:
            footer.add_widget(self.status_details, index=1)
        elif not needed and self.status_details.parent is footer:
            footer.remove_widget(self.status_details)

    def _show_status_details(self):
        """Open a read-only snapshot; background status updates do not erase it."""
        if not self.status_details.disabled:
            return self.show_error('Status perangkat', self.status.text)

    def set_camera_status(self, ready):
        """Apply frame readiness to the current screen without rebuilding it.

        A device can stay open while its latest-frame mailbox is empty or stale.
        Keep the order and selection intact, but close every action that needs a
        fresh frame. A recovered camera must not unlock a submitted payment or
        a capture countdown that is already running; the controller owns timers.
        """
        self._camera_ready = ready
        self.camera_badge.text = 'Kamera siap' if ready else 'Kamera belum siap'
        self.camera_badge.color = SAGE if ready else CORAL
        if self.current_screen == 'welcome' and self.home_start_button is not None:
            self.home_start_button.disabled = not ready
        elif self.current_screen == 'templates':
            self._refresh_order()
        elif self.current_screen == 'payment':
            self.payment_confirm.disabled = (not ready or self._payment_submitted
                                             or self.payment.check() not in {'pending', 'paid'})
        elif self.current_screen == 'capture':
            if self.live_caption is not None:
                self.live_caption.text = 'LIVE CAMERA' if ready else 'MENUNGGU KAMERA'
            if not ready:
                self.capture_button.disabled = True
                if self.preview is not None:
                    # A frozen last picture must not look like a live preview.
                    self.preview.texture = None
                    self._set_preview_live(False)
        elif self.current_screen == 'review':
            self.retake_button.disabled = not (ready and self._review_can_retake)
            self.review_hint.text = self._review_message()

    def _review_message(self):
        """Explain which prerequisite closes the retake gate, not just its color."""
        if not self._review_has_retake:
            return 'Retake sudah digunakan. Ketiga foto ini siap dipakai pada hasil akhir.'
        if not self._camera_ready:
            return 'Kamera belum siap. Foto tetap aman; tunggu kamera untuk retake.'
        return 'Pilih satu foto untuk retake. Pratinjau sesuai potongan hasil akhir.'

    def _set_preview_live(self, live):
        """Show an intentional empty state instead of Kivy's white null texture."""
        if self.preview is not None:
            self.preview.opacity = 1 if live else 0
        if self.camera_wait_hint is not None:
            self.camera_wait_hint.opacity = 0 if live else 1

    def show_welcome(self, camera_ready, status_message):
        """Show the complete procedure with large illustrations and short labels."""
        self.set_camera_status(camera_ready)
        page = self._reset("welcome", "")
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        tutorial = Panel(orientation="vertical", padding=dp(16), spacing=dp(12),
                         size_hint_y=None)
        intro = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        intro.add_widget(self._label("Bikin kenangan.", 27, bold=True))
        price = self._label("Rp5.000 / sesi", 18, bold=True, color=BLUE, align="right")
        price.size_hint_x = .55
        intro.add_widget(price)
        tutorial.add_widget(intro)
        grid = GridLayout(cols=4, spacing=dp(12))
        self.welcome_steps = []
        for number, kind, title, note, fill in (
                (1, "frames", "Pilih frame", "12 desain", SOFT),
                (2, "pay", "Bayar", "Demo", CYAN),
                (3, "camera", "Senyum!", "3 foto · 1 retake", BLUSH),
                (4, "result", "Cetak + scan", "Simpan fotomu", (1, .96, .80, 1))):
            card = Panel(fill=fill, border=False, orientation="vertical",
                         padding=dp(10), spacing=dp(4))
            card.add_widget(self._label(f"{number:02d}", 12, 18, color=BLUE, bold=True))
            illustration = self._motion.add(GuideGlyph(kind=kind))
            card.add_widget(illustration)
            card.add_widget(self._label(title, 17, 27, bold=True, align="center"))
            card.add_widget(self._label(note, 12, 23, color=GREY, align="center"))
            grid.add_widget(card)
            self.welcome_steps.append(illustration)
        tutorial.add_widget(grid)
        def fit_tutorial(*_args):
            grid.cols = 2 if scroll.width < dp(650) else 4
            minimum = dp(510 if grid.cols == 2 else 300)
            tutorial.height = max(scroll.height, minimum)
            scroll.do_scroll_y = tutorial.height > scroll.height + 1
        scroll.add_widget(tutorial)
        scroll.bind(size=fit_tutorial)
        fit_tutorial()
        page.add_widget(scroll)
        self.home_start_button = self._button("MULAI FOTO", self.callbacks["on_home_start"], camera_ready)
        self._attach_icon(self.home_start_button, "camera")
        page.add_widget(self.home_start_button)
        self.set_status(status_message)

    def show_template_selection(self, camera_ready, status_message, storage_ready=True,
                                quantities=None):
        """Browse real frames horizontally in an endlessly looping carousel.

        The arrows, drag/swipe, and mouse wheel share the same native carousel.
        Quantity controls stay OUTSIDE the gesture surface, while the complete
        cart and checkout remain visible beside it on the supported desktops.
        Browsing never changes the order; only the explicit +/− controls do.
        """
        self.set_camera_status(camera_ready)
        self._storage_ready = storage_ready
        page = self._reset('templates', 'Pilih frame favoritmu.')
        self.quantities = {t.template_id: (quantities or {}).get(t.template_id, 0)
                           for t in self.templates}
        self.quantity_labels, self.quantity_buttons = {}, {}
        self._quantity_rows, self._template_cards = {}, {}
        deck = Panel(orientation='vertical', padding=dp(14), spacing=dp(7))
        top = BoxLayout(size_hint_y=None, height=dp(20))
        top.add_widget(self._label('THE FRAME COLLECTION', 11, bold=True, color=BLUE))
        self.template_counter = self._label('', 12, bold=True, align='right', color=GREY)
        self.template_counter.size_hint_x = .3
        top.add_widget(self.template_counter)
        deck.add_widget(top)
        carousel = TemplateCarousel()
        self.template_carousel = carousel
        revision = self._screen_revision
        previews = [create_template_preview(t, (240, 720)) for t in self.templates]
        for index, template in enumerate(self.templates):
            slide = ReceiptSlide(previews[index], previews[(index - 1) % len(previews)],
                                 previews[(index + 1) % len(previews)])
            self._template_cards[template.template_id] = slide.center_card
            carousel.add_widget(slide)
            # Store independent quantity widgets for every design. Only the
            # focused row is attached, so offscreen controls cannot steal taps.
            key = template.template_id
            controls = BoxLayout(spacing=dp(4), size_hint_x=None, width=dp(166))
            minus = self._button('−', lambda k=key: self._change_quantity(k, -1), secondary=True)
            plus = self._button('+', lambda k=key: self._change_quantity(k, 1), secondary=True)
            for button in (minus, plus):
                button.size_hint_x = None
                button.width, button.height = dp(44), dp(44)
                button.font_size = dp(21)
            quantity = self._label('0 sesi', 14, bold=True, align='center')
            self.quantity_labels[key] = quantity
            self.quantity_buttons[key] = (minus, plus)
            controls.add_widget(minus)
            controls.add_widget(quantity)
            controls.add_widget(plus)
            self._quantity_rows[key] = controls
        preview_row = BoxLayout(spacing=dp(6))
        self.carousel_previous = self._button("‹", lambda: carousel.navigate(-1), secondary=True)
        self.carousel_next = self._button("›", lambda: carousel.navigate(1), secondary=True)
        for button in (self.carousel_previous, self.carousel_next):
            button.size_hint = (None, None)
            button.size = (dp(44), dp(52))
            button.pos_hint = {"center_y": .5}
            button.font_size = dp(30)
        preview_row.add_widget(self.carousel_previous)
        preview_row.add_widget(carousel)
        preview_row.add_widget(self.carousel_next)
        deck.add_widget(preview_row)
        self.template_dots = CarouselDots(len(self.templates), size_hint_y=None, height=dp(8))
        deck.add_widget(self.template_dots)
        self.template_name = self._label('', 21, 30, bold=True, align='center')
        deck.add_widget(self.template_name)
        navigation = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        navigation.add_widget(Widget())
        self._focused_quantity_slot = BoxLayout(size_hint_x=None, width=dp(166))
        navigation.add_widget(self._focused_quantity_slot)
        navigation.add_widget(Widget())
        deck.add_widget(navigation)
        deck.add_widget(self._label('‹  GESER FRAME  ›', 10, 18,
                                    color=GREY, align='center'))
        cart = Panel(fill=BLUE, border=False, orientation='vertical', padding=dp(18), spacing=dp(7))
        cart.add_widget(self._label('Pesanan kamu', 22, 32, bold=True, color=WHITE))
        items = ScrollView(do_scroll_x=False, bar_width=dp(3))
        self.order_items = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.order_items.bind(minimum_height=self.order_items.setter("height"))
        self.order_rows = {}
        self._order_signature = None
        self._order_revision = 0
        items.add_widget(self.order_items)
        cart.add_widget(items)
        cart.add_widget(PixelRule(size_hint_y=None, height=dp(12)))
        self.cart_sessions = self._label('', 12, 22, color=WHITE)
        self.cart_total = self._label('', 34, 48, bold=True, color=WHITE)
        cart.add_widget(self.cart_sessions)
        cart.add_widget(self.cart_total)
        cart.add_widget(self._label('3 foto + 1 retake per sesi.', 12, 28, color=WHITE))
        self.start_button = self._button('LANJUT BAYAR', self._start_selected, False, inverse=True)
        cart.add_widget(self.start_button)
        cart.add_widget(self._label('Pembayaran demo · Tanpa tagihan.', 10, 22,
                                    color=WHITE, align='center'))
        page.add_widget(self._responsive_row(deck, cart, 300, 340))
        def focus(_carousel, index):
            # A delayed animation from a retired screen cannot change the next
            # customer's counter, quantity row, or selection.
            if self.current_screen != 'templates' or revision != self._screen_revision:
                return
            self._last_template_index = index
            template = self.templates[index]
            self.template_name.text = template.name
            self.template_counter.text = f'{index + 1:02d} / {len(self.templates):02d}'
            self.template_dots.index = index
            self._focused_quantity_slot.clear_widgets()
            self._focused_quantity_slot.add_widget(self._quantity_rows[template.template_id])
            for key, row in self.order_rows.items():
                row.background_color = (.38, .52, .98, 1) if key == template.template_id else (.20, .38, .93, 1)
        carousel.bind(index=focus)
        carousel.index = self._last_template_index % len(self.templates)
        focus(carousel, carousel.index)
        self._refresh_order()
        self.set_status(status_message)

    def _change_quantity(self, key, delta):
        """Preserve independent quantities and never permit negative orders."""
        self.quantities[key] = max(0, self.quantities[key] + delta)
        self._refresh_order()

    def _refresh_order(self):
        """Apply camera/storage/order gates; no UI click can bypass these checks."""
        for key, quantity in self.quantities.items():
            self.quantity_labels[key].text = f'{quantity} sesi'
            self.quantity_buttons[key][0].disabled = quantity == 0
            self._template_cards[key].selected = quantity > 0
        total = sum(self.quantities.values())
        signature = tuple((t.template_id, self.quantities[t.template_id]) for t in self.templates
                          if self.quantities[t.template_id])
        if signature != self._order_signature:
            self._order_signature = signature
            self._order_revision += 1
            order_revision = self._order_revision
            self.order_items.clear_widgets()
            self.order_rows = {}
            for index, template in enumerate(self.templates):
                key = template.template_id
                quantity = self.quantities[key]
                if not quantity:
                    continue
                def inspect_template(i=index, revision=order_revision):
                    # Storage readiness polls must not rebuild these buttons,
                    # and a removed row's late release cannot alter focus.
                    if revision == self._order_revision:
                        self.template_carousel.request_index(i)
                row = self._button(f"{template.name}   × {quantity}    ›",
                                   inspect_template, secondary=True)
                row.height = dp(52)
                row.font_size = dp(14)
                row.halign = "left"
                row.color = WHITE
                row.background_color = (.20, .38, .93, 1)
                self.order_rows[key] = row
                self.order_items.add_widget(row)
            if not signature:
                self.order_items.add_widget(self._label("Pilih frame, lalu tekan +", 14, 58,
                                                        color=WHITE))

        amount = 'Rp' + f'{total * PRICE_PER_SESSION:,}'.replace(',', '.')
        self.cart_sessions.text = f'{total} sesi × Rp5.000'
        self.cart_total.text = amount
        self.start_button.disabled = not (total and self._camera_ready and self._storage_ready)

    def _start_selected(self):
        """Copy the order before forwarding it to the controller payment step."""
        self.callbacks['on_start']({k: v for k, v in self.quantities.items() if v > 0})

    def set_storage_status(self, ready, message):
        """Unlock an existing selection when a valid Drive folder becomes available."""
        self._storage_ready = ready
        if self.current_screen == 'templates':
            self._refresh_order()
        self.set_status(message)

    def show_payment(self, order_summary, session_count, total_amount, on_confirm, on_back):
        """Show muted advertising beside a stable QR and an in-window print offer."""
        return self._show_ad_payment(order_summary, session_count, total_amount, on_confirm, on_back)

    def show_capture(self, session_label, capture_count, preview_image,
                     action_label='AMBIL FOTO', countdown_text='', can_capture=True, is_retake=False):
        """Make the camera the visual focus; keep progress and actions beside it."""
        page = self._reset('capture', 'Senyum, ini momenmu.', session_label)
        camera = Panel(fill=INK, orientation='vertical', padding=dp(14), spacing=dp(8))
        self.live_caption = self._label('LIVE CAMERA' if self._camera_ready else 'MENUNGGU KAMERA',
                                        11, 26, color=SOFT, bold=True)
        camera.add_widget(self.live_caption)
        # An overlay has the same bounds as the image. It becomes visible only
        # when no fresh frame exists, without changing preview dimensions or
        # pushing the camera footer around during a transient outage.
        preview_stage = FloatLayout()
        self.preview = KivyImage(fit_mode='contain', opacity=0, pos_hint={'x': 0, 'y': 0})
        preview_stage.add_widget(self.preview)
        self.camera_wait_hint = self._label('Menunggu gambar kamera.\nSesi ini tetap tersimpan.',
                                            15, color=SOFT, align='center')
        self.camera_wait_hint.pos_hint = {'x': 0, 'y': 0}
        preview_stage.add_widget(self.camera_wait_hint)
        camera.add_widget(preview_stage)
        if preview_image is not None and self._camera_ready:
            self.update_live_preview(preview_image)
        camera.add_widget(self._label('Lihat ke kamera. Cek potongan foto saat review.',
                                       13, 28, color=SOFT, align='center'))
        guide = Panel(fill=SOFT, orientation='vertical', padding=dp(18), spacing=dp(10))
        guide.add_widget(self._label('FOTO PENGGANTI' if is_retake else f'FOTO {min(capture_count + 1, 3)} / 3',
                                     13, 28, color=GREY, bold=True))
        self.countdown = self._label(countdown_text or 'Siap?', 44, bold=True, align='center')
        self.countdown_dial = self._motion.add(CountdownDial(self.countdown))
        guide.add_widget(self.countdown_dial)
        hint_row = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(8))
        self.capture_gesture = self._motion.add(GuideGlyph(kind="hand", size_hint_x=None, width=dp(42)))
        hint_row.add_widget(self.capture_gesture)
        self.capture_hint = self._label("", 13, color=GREY)
        hint_row.add_widget(self.capture_hint)
        guide.add_widget(hint_row)
        self._palm_progress = 0.0
        self._refresh_capture_hint()
        progress = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        for index in range(3):
            progress.add_widget(self._label(f'{index + 1:02d}\n' + ('Siap' if index < capture_count else '—'),
                                           12, color=SAGE if index < capture_count else GREY,
                                           align='center'))
        guide.add_widget(progress)
        self.capture_button = self._button(action_label, self.callbacks['on_capture'],
                                           can_capture and self._camera_ready)
        page.add_widget(self._responsive_row(camera, guide, 240, 300))
        self._attach_icon(self.capture_button, 'camera')
        page.add_widget(self.capture_button)

    def update_live_preview(self, image):
        """Fit only a preview copy, preserving full-resolution source photos."""
        if self.current_screen == 'capture' and self.preview is not None:
            display = image.copy()
            display.thumbnail((640, 480))
            self._display(display, self.preview)
            self._set_preview_live(True)

    def update_live_frame(self, frame):
        """Display an OpenCV BGR frame directly, without a Pillow round trip.

        Resize only the preview copy before uploading pixels to the GPU. The
        controller retains the full-resolution frame for saving and composition.
        OpenGL work stays on Kivy's main thread; the camera thread never touches
        widgets or textures. Reuse the existing texture between camera frames.
        """
        if self.current_screen != 'capture' or self.preview is None:
            return
        import cv2
        height, width = frame.shape[:2]
        scale = min(1.0, 640 / width, 480 / height)
        if scale < 1:
            frame = cv2.resize(frame, (max(1, int(width * scale)),
                                      max(1, int(height * scale))),
                               interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        size = (rgb.shape[1], rgb.shape[0])
        texture = self.preview.texture
        if texture is None or texture.size != size:
            texture = Texture.create(size=size, colorfmt='rgb')
            texture.flip_vertical()
        texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        self.preview.texture = texture
        self._set_preview_live(True)
        self.preview.canvas.ask_update()

    def set_countdown(self, seconds, is_retake=False):
        """Render controller timer ticks without sleeping on the GUI thread."""
        if self.current_screen == 'capture':
            self._capture_running = True
            self.countdown.text = str(seconds)
            if self.countdown_dial is not None:
                self.countdown_dial.set_seconds(seconds)
            if seconds > 0 and seconds != self._last_countdown_value:
                self.audio.set_capture_active(True)
                self.audio.play("count")
            self._last_countdown_value = seconds
            self._refresh_capture_hint()
            self.set_capture_enabled(False)

    @property
    def screen_revision(self):
        """Tag asynchronous gesture work with this exact page's lifetime."""
        return self._screen_revision

    def set_palm_status(self, state, progress=0.0, needs_release=False):
        """Update one existing guidance slot; the photo button stays in place."""
        self._palm_state = state
        self._palm_progress = progress
        self._palm_needs_release = needs_release
        self._refresh_capture_hint()

    def _refresh_capture_hint(self):
        """Keep gesture feedback compact without exposing SDK/download details."""
        if self.current_screen != 'capture' or self.capture_hint is None:
            return
        if self._capture_running:
            text = 'Turunkan tangan.\nLihat ke kamera.'
        elif self._palm_state in {'idle', 'loading'}:
            text = 'Tekan tombol kamera.\nGestur disiapkan...'
        elif self._palm_state == 'ready':
            if self._palm_needs_release:
                text = 'Turunkan tangan sebentar.\nAtau tekan kamera.'
            elif self._palm_progress > 0:
                text = f'Tahan telapak · {self._palm_progress:.0%}'
            else:
                text = 'Tekan kamera /\ntelapak 1 detik.'
        elif self._palm_state == 'unavailable':
            text = 'Gestur belum tersedia.\nTekan kamera.'
        else:
            text = 'Siap? Tekan kamera.\nTimer 5 detik.'
        self.capture_hint.text = text
        if getattr(self, 'capture_gesture', None) is not None:
            self.capture_gesture.kind = 'camera' if self._capture_running or self._palm_state != 'ready' else 'hand'

    def set_capture_enabled(self, enabled):
        if self.current_screen == 'capture':
            self.capture_button.disabled = not (enabled and self._camera_ready)

    def show_review(self, photo_paths, session_label, selected_index, retake_available,
                    status_message='', template=None):
        """Review the final frame crops and mark the exact retake target.

        Showing the full camera aspect ratio here used to expose side content
        absent from the final strip. Render the composer's exact RGB crop, then
        contain that frame in the card without stretching or cropping it again.
        The raw source is opened read-only and never resized in place.
        """
        page = self._reset('review', 'Sudah pas? Atau satu kali lagi?',
                           f'{session_label}  ·  Sisa retake: {int(retake_available)}')
        self._review_can_retake = selected_index is not None and retake_available
        self._review_has_retake = retake_available
        template = template or self.templates[0]
        scroll = ScrollView(do_scroll_x=False)
        gallery = GridLayout(cols=3, spacing=dp(16), size_hint_y=None)
        gallery.bind(minimum_height=gallery.setter('height'))
        def fit_review(*_args):
            # Three landscape thumbnails and their selection buttons must be
            # visible together. A fixed 290px card hid every button at 800x600.
            gallery.cols = 1 if scroll.width < dp(620) else 3
            for card in gallery.children:
                card.height = dp(290) if gallery.cols == 1 else max(dp(220), scroll.height)
        scroll.bind(size=fit_review)
        scroll.add_widget(gallery)
        page.add_widget(scroll)
        for index, path in enumerate(photo_paths):
            selected = index == selected_index
            card = Panel(fill=SOFT if selected else WHITE, orientation='vertical',
                         padding=dp(14), spacing=dp(12), size_hint_y=None, height=dp(290))
            with Image.open(path) as source:
                display = render_photo_frame(source, template, index)
            card.add_widget(self._display(display))
            caption = (' · DIPILIH' if selected else ' · Pilih untuk retake') if retake_available else (
                ' · DIGANTI' if selected else ' · Tersimpan')
            card.add_widget(self._button(f'Foto {index + 1}' + caption,
                                         lambda i=index: self.callbacks['on_select_photo'](i), retake_available,
                                         secondary=not selected))
            gallery.add_widget(card)
        fit_review()
        self.review_hint = self._label(self._review_message(), 13, 36, color=GREY)
        page.add_widget(self.review_hint)
        self.retake_button = self._button('RETAKE FOTO TERPILIH' if retake_available else 'RETAKE SUDAH DIGUNAKAN',
                                         self.callbacks['on_retake'],
                                         self._review_can_retake and self._camera_ready, secondary=True)
        self.accept_button = self._button('GUNAKAN FOTO INI', self.callbacks['on_accept_session'])
        self._attach_icon(self.accept_button, 'check')
        page.add_widget(self._actions(self.retake_button, self.accept_button))
        self.set_status(status_message)

    def show_result(self, image_path, session_label, transaction_id, has_next_session,
                    seconds_remaining=None, qr_image=None, qr_pending=False, upload_message='',
                    print_message='Belum dikirim ke printer.', print_busy=False):
        """Separate the printable composition from the customer folder QR.

        The QR has a real height even at small sizes. Long details scroll as a
        unit; the next/finish action and countdown stay outside that viewport.
        No success message here pretends that a physical print has occurred.
        """
        page = self._reset('result', 'Momennya sudah tersimpan.', f'{session_label}  ·  {transaction_id}')
        photo = Panel(orientation='vertical', padding=dp(20), spacing=dp(12))
        photo.add_widget(self._label('HASIL DIGITAL', 11, 24, bold=True, color=GREY))
        with Image.open(image_path) as source:
            display = source.convert('RGB')
            display.thumbnail((1000, 850))
        photo.add_widget(self._display(display))
        self.result_zoom_button = self._button('PERBESAR HASIL',
                                               lambda: self._show_result_detail(image_path),
                                               secondary=True)
        self.result_zoom_button.height = dp(36)
        photo.add_widget(self.result_zoom_button)
        self.print_status = self._label(print_message, 12, 34, color=GREY, align='center')
        photo.add_widget(self.print_status)
        self.print_button = self._button(
            'CETAK ULANG', self.callbacks.get('on_print', lambda: None),
            enabled=not print_busy, secondary=True,
        )
        self.print_button.height = dp(36)
        photo.add_widget(self.print_button)
        share = Panel(orientation='vertical', padding=dp(10), spacing=dp(5))
        share.add_widget(self._label('BAWA PULANG FOTOMU', 12, 20, bold=True, color=GREY))
        self.qr_view = KivyImage(fit_mode='contain', size_hint_y=None, height=dp(180))
        share.add_widget(self.qr_view)
        self.qr_title = self._label('', 15, 36, bold=True, align='center')
        share.add_widget(self.qr_title)
        self.upload_status = self._label(upload_message, 13, 48, color=GREY, align='center')
        share.add_widget(self.upload_status)
        # The flexible trailing spacer anchors fixed QR content to the top.
        # Otherwise BoxLayout leaves surplus height above it on short screens.
        share.add_widget(Widget())
        page.add_widget(self._responsive_row(photo, share, 300, 324))
        self.set_result_qr(qr_image, qr_pending)
        self.completion = self._label('', 13, color=GREY)
        if seconds_remaining is not None:
            self.set_completion_countdown(seconds_remaining)
        self.result_action = self._button('SESI BERIKUTNYA' if has_next_session else 'SELESAI',
                                         self.callbacks['on_next_session' if has_next_session else 'on_finish'])
        page.add_widget(self._actions(self.completion, self.result_action))
        # Upload progress refreshes the QR in place, so the reward is emitted
        # once when this saved result is presented, never on status polling.
        self.audio.play("success")

    def _show_result_detail(self, image_path):
        """Inspect the full receipt at a larger size without rewriting output.

        A complete 80 × 240 mm strip is narrow when contained in a desktop
        result card. This read-only viewer uses the available width and allows
        vertical scrolling, so photos and footer details can be inspected.
        Closing it returns to the same result/session; it never triggers print.
        """
        try:
            with Image.open(image_path) as source:
                image = source.convert('RGB')
        except OSError as error:
            return self.show_error('Hasil tidak dapat dibuka', str(error))
        body = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(12))
        scroll = ScrollView(do_scroll_x=False)
        display = self._display(image)
        display.size_hint = (None, None)
        display.pos_hint = {'center_x': .5}
        stage = BoxLayout(orientation='vertical', size_hint_y=None)
        stage.add_widget(display)
        def fit_detail(_widget, width):
            # Cap the enlargement at native pixel width on desktop, keeping
            # the first photograph readable without making the header enormous.
            display.width = min(width, dp(640))
            display.height = display.width * image.height / image.width
            stage.height = display.height
        stage.bind(width=fit_detail)
        scroll.add_widget(stage)
        body.add_widget(scroll)
        popup = Popup(title='Detail hasil foto', content=body, size_hint=(.85, .9),
                      auto_dismiss=False, background='', background_color=PAPER,
                      title_color=INK, separator_color=EDGE)
        body.add_widget(self._button('TUTUP', popup.dismiss, screen_bound=False))
        self._result_detail_popup = popup
        def release_detail(_popup):
            if self._result_detail_popup is popup:
                self._result_detail_popup = None
        popup.bind(on_dismiss=release_detail)
        popup.open()
        return popup

    def set_result_qr(self, qr_image, pending=False):
        """Keep the destination visible independently from synchronization state."""
        if self.current_screen != 'result' or self.qr_view is None:
            return
        pixels = qr_image.tobytes() if qr_image is not None else None
        if qr_image is not None:
            if pixels != self._qr_bytes:
                self._display(qr_image, self.qr_view, crisp=True)
            self.qr_title.text = 'Scan folder foto\nTersimpan 30 hari di Drive'
        else:
            self.qr_view.texture = None
            self.qr_title.text = 'Menyiapkan QR folder...' if pending else 'Mode lokal · QR Drive tidak tersedia'
        self._qr_bytes = pixels

    def set_print_status(self, message, busy=False):
        """Update print progress without navigating away from result view."""
        if self.current_screen == 'result' and self.print_status is not None:
            self.print_status.text = message
            if self.print_button is not None:
                self.print_button.disabled = busy

    def set_result_upload_status(self, message):
        if self.current_screen == 'result':
            self.upload_status.text = message

    def set_completion_countdown(self, seconds_remaining):
        if self.current_screen == 'result':
            minutes, seconds = divmod(max(0, seconds_remaining), 60)
            self.completion.text = f'Kembali ke awal dalam {minutes:02d}:{seconds:02d}'

    def show_error(self, title, message):
        """Keep long diagnostics readable and provide an explicit dismiss action."""
        body = Panel(orientation='vertical', spacing=dp(16), padding=dp(20))
        scroll = ScrollView()
        label = self._label(message, 16, auto_height=True)
        scroll.add_widget(label)
        body.add_widget(scroll)
        popup = Popup(title=title, content=body, size_hint=(.85, .8), auto_dismiss=False,
                      background='', background_color=PAPER, title_color=INK, separator_color=EDGE)
        body.add_widget(self._button('TUTUP', popup.dismiss, screen_bound=False))
        popup.open()
        return popup
