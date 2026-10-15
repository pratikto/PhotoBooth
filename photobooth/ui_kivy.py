"""Kivy presentation layer for the existing PhotoBooth controller.

This module deliberately keeps the controller-facing method names used by the
historical Tkinter UI. Workflow rules and Drive operations remain outside the
widgets. All texture creation and widget changes run on Kivy's main thread.
The desktop Camera implementation is retained; this migration alone is NOT an
Android camera/USB driver implementation or an Android packaging configuration.
"""

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from PIL import Image
from photobooth.catalog import PRICE_PER_SESSION, create_template_preview

NAVY = (0.106, 0.227, 0.376, 1)
MUTED = (0.39, 0.44, 0.52, 1)
YELLOW = (1, 0.74, 0, 1)


class KivyHost(App):
    """Own the native window and translate controller timers to Kivy Clock.

    ``after`` uses milliseconds to preserve the controller's existing timing
    contract, while Clock uses seconds. It returns a ClockEvent (not a Tk ID).
    Keeping that event lets shutdown cancel precisely the scheduled callback.
    """

    def __init__(self, on_close):
        super().__init__()
        self.title = 'Meongs Photobooth'
        self._on_close = on_close
        self.view = None
        # Desktop starts with a useful kiosk-sized canvas. Responsive layouts
        # below still support resizing; Android owns its window dimensions.
        from kivy.utils import platform
        if platform in {'win', 'linux', 'macosx'}:
            Window.size = (1200, 800)

    def build(self):
        """Return the widget tree prepared by PhotoBoothUI before App.run()."""
        Window.clearcolor = (0.95, 0.96, 0.98, 1)
        return self.view

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
        self._on_close()


# Visual tokens are centralized so every screen shares the same hierarchy.
# Muted sage, warm paper, and dark ink keep a long-running kiosk calm and legible.
PAPER = (0.965, 0.961, 0.941, 1)
WHITE = (1, 1, 1, 1)
INK = (0.10, 0.19, 0.18, 1)
SAGE = (0.16, 0.37, 0.30, 1)
SOFT = (0.91, 0.94, 0.91, 1)
GREY = (0.43, 0.48, 0.45, 1)
EDGE = (0.84, 0.87, 0.83, 1)
CORAL = (0.80, 0.36, 0.25, 1)


class Panel(BoxLayout):
    """A rounded card whose canvas follows its position and dimensions.

    Canvas instructions must be bound to geometry because BoxLayout positions
    children after construction. Without these bindings, backgrounds stay at the
    origin or stop matching their widgets when the window is resized.
    """
    def __init__(self, fill=WHITE, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*fill)
            self._background = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        self.bind(pos=self._paint, size=self._paint)

    def _paint(self, *_args):
        self._background.pos = self.pos
        self._background.size = self.size


class PhotoBoothUI:
    """Kiosk screens; controller callbacks remain the source of workflow rules.

    The layout uses a stable header, a flexible stage, and fixed action controls.
    Galleries and long details scroll inside the stage, keeping primary actions
    reachable. Breakpoints depend on available width, not the operating system.
    """

    def __init__(self, root, templates, **callbacks):
        self.templates = tuple(templates)
        self.callbacks = callbacks
        self.current_screen = 'welcome'
        self._camera_ready = False
        self._storage_ready = False
        self.preview = None
        self.qr_view = None
        self._qr_bytes = None
        self.shell = Panel(fill=PAPER, orientation='vertical', padding=dp(24), spacing=dp(12))
        root.view = self.shell
        header = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(12))
        self._header_row = header
        self.brand = self._label('meongs.', 29, bold=True)
        self.brand.size_hint_x = .4
        header.add_widget(self.brand)
        self.steps = self._label('01  Template    /    02  Bayar    /    03  Foto    /    04  Hasil', 12,
                                 color=GREY, align='right')
        header.add_widget(self.steps)
        self.shell.add_widget(header)
        self.content = BoxLayout(orientation='vertical', spacing=dp(10))
        self.shell.add_widget(self.content)
        footer = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(12))
        self._footer_row = footer
        self.status = self._label('', 12, color=GREY)
        footer.add_widget(self.status)
        self.camera_badge = self._label('Kamera diperiksa', 12, color=GREY, align='right')
        self.camera_badge.size_hint_x = None
        self.camera_badge.width = dp(170)
        footer.add_widget(self.camera_badge)
        self.shell.add_widget(footer)
        self.header = self.brand  # Historical public handle retained for callers.
        self._page_title = self._page_subtitle = None
        self.shell.bind(size=self._fit_chrome)
        self._fit_chrome()

    def _fit_chrome(self, *_args):
        """Reserve more room for content on short desktop windows.

        Keeping the same 58px header, 34px footer, and large page headings at
        800x600 used to leave only 200px for a 420px payment card. The resulting
        outer scroll clipped the QR and camera. Resize existing widgets in place
        so a window resize never rebuilds the screen or loses the current cart.
        """
        compact = self.shell.height < dp(700)
        self.shell.padding = dp(20 if compact else 24)
        self.shell.spacing = dp(10 if compact else 12)
        self._header_row.height = dp(44 if compact else 58)
        self._footer_row.height = dp(26 if compact else 34)
        self.camera_badge.width = dp(132 if compact else 170)
        if self._page_title is not None:
            self._page_title.height = dp(36 if compact else 46)
            self._page_title.font_size = dp(26 if compact else 28)
        if self._page_subtitle is not None:
            self._page_subtitle.height = dp(28 if compact else 38)

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

    def _button(self, text, callback, enabled=True, secondary=False):
        """Consistent 52dp touch targets; secondary actions use a quieter treatment."""
        widget = Button(text=text, size_hint_y=None, height=dp(52),
                        background_normal='', background_down='',
                        background_color=SOFT if secondary else SAGE,
                        color=INK if secondary else WHITE,
                        disabled_color=(0.55, 0.60, 0.56, 1),
                        font_size=dp(14), bold=True, disabled=not enabled)
        widget.bind(on_release=lambda _widget: callback())
        # Long translated labels wrap rather than overflowing a narrow button.
        widget.bind(size=lambda w, size: setattr(w, 'text_size', (size[0] - dp(16), size[1])))
        widget.halign = 'center'
        widget.valign = 'middle'
        return widget

    def _reset(self, screen, title, subtitle=''):
        """Discard only screen widgets, keeping shell/footer and controller state."""
        self.current_screen = screen
        self.content.clear_widgets()
        self.preview = None
        self.qr_view = None
        self._qr_bytes = None
        self._page_title = self._page_subtitle = None
        self.set_status('')
        active = {'welcome': 1, 'templates': 1, 'payment': 2,
                  'capture': 3, 'review': 3, 'result': 4}.get(screen, 1)
        self.steps.text = '   /   '.join(
            ('[ ' + label + ' ]') if index == active else label
            for index, label in enumerate(('01 Template', '02 Bayar', '03 Foto', '04 Hasil'), 1))
        if title:
            self._page_title = self._label(title, 28, 46, bold=True)
            self.content.add_widget(self._page_title)
        if subtitle:
            self._page_subtitle = self._label(subtitle, 14, 38, color=GREY)
            self.content.add_widget(self._page_subtitle)
        self._fit_chrome()
        return self.content

    def _responsive_row(self, left, right, right_width=330, min_height=300):
        """Make side-by-side cards scroll safely on narrow or short windows.

        The inner layout has an explicit minimum height. This prevents fixed
        captions or buttons from squeezing a QR or camera preview to zero height.
        On phone-width windows, panels stack and can be scrolled vertically.
        """
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(5), scroll_type=['bars', 'content'])
        row = BoxLayout(spacing=dp(16), size_hint_y=None)
        row.add_widget(left)
        row.add_widget(right)
        scroll.add_widget(row)
        def arrange(*_args):
            compact = scroll.width < dp(720)
            row.orientation = 'vertical' if compact else 'horizontal'
            row.height = max(scroll.height, dp(min_height * 2 + 16 if compact else min_height))
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
        """Display controller feedback independently from page navigation."""
        self.status.text = message

    def set_camera_status(self, ready):
        """Keep the camera indicator separate from Drive readiness."""
        self._camera_ready = ready
        self.camera_badge.text = 'Kamera siap' if ready else 'Kamera belum siap'
        self.camera_badge.color = SAGE if ready else CORAL

    def show_welcome(self, camera_ready, status_message):
        """Introduce the session with one prominent action and honest storage state."""
        self.set_camera_status(camera_ready)
        page = self._reset('welcome', '')
        hero = Panel(fill=SAGE, orientation='vertical', padding=dp(30), spacing=dp(16))
        hero.add_widget(self._label('A LITTLE MOMENT. A GOOD MEMORY.', 12, 32, color=SOFT))
        hero.add_widget(self._label('Satu momen,\nbanyak cerita.', 42, bold=True, color=WHITE))
        hero.add_widget(self._label('Bikin foto seru bareng teman.\nPilih gaya, ambil foto, dan bawa pulang kenangannya.',
                                    17, 92, color=SOFT))

        aside = Panel(orientation='vertical', padding=dp(20), spacing=dp(8))
        aside.add_widget(self._label('Cara mainnya', 22, 46, bold=True))
        for title, note in [('01   Pilih gaya', 'Pilih template dan jumlah sesi.'),
                            ('02   Siapkan senyum', 'Tiga foto baru di setiap sesi.'),
                            ('03   Simpan momennya', 'Satu retake per sesi. Scan QR folder foto.')]:
            aside.add_widget(self._label(title, 18, 32, bold=True))
            aside.add_widget(self._label(note, 14, 40, color=GREY))
        aside.add_widget(self._label('Pembayaran saat ini masih simulasi.', 12, 40, color=CORAL))
        # A trailing spacer top-aligns the instructions on large windows without
        # increasing the minimum height or pushing their heading down the card.
        aside.add_widget(Widget())
        page.add_widget(self._responsive_row(hero, aside, 330, 400))
        page.add_widget(self._button('MULAI FOTO', self.callbacks['on_home_start'], camera_ready))
        self.set_status(status_message)

    def show_template_selection(self, camera_ready, status_message, storage_ready=True,
                                quantities=None):
        """A compact template gallery plus a continuously updated order summary."""
        self.set_camera_status(camera_ready)
        self._storage_ready = storage_ready
        page = self._reset('templates', 'Pilih gaya fotomu.', 'Setiap qty berarti satu sesi baru berisi tiga foto.')
        self.quantities = {t.template_id: (quantities or {}).get(t.template_id, 0)
                           for t in self.templates}
        self.quantity_labels = {}
        self._template_cards = {}
        gallery = ScrollView(do_scroll_x=False, bar_width=dp(5))
        grid = GridLayout(cols=2, spacing=dp(14), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        gallery.bind(width=lambda w, width: setattr(grid, 'cols', 1 if width < dp(370) else 2))
        gallery.add_widget(grid)
        for number, template in enumerate(self.templates, 1):
            key = template.template_id
            card = Panel(orientation='vertical', size_hint_y=None, height=dp(228),
                         padding=dp(14), spacing=dp(7))
            card.add_widget(self._display(create_template_preview(template, (520, 220))))
            card.add_widget(self._label(template.name, 17, 27, bold=True))
            card.add_widget(self._label('Rp5.000 / sesi', 13, 24, color=GREY))
            controls = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
            minus = self._button('−', lambda k=key: self._change_quantity(k, -1), secondary=True)
            plus = self._button('+', lambda k=key: self._change_quantity(k, 1), secondary=True)
            for button in (minus, plus):
                button.size_hint_x = None
                button.width = dp(46)
                button.height = dp(42)
            quantity = self._label('0 sesi', 14, bold=True, align='center')
            self.quantity_labels[key] = quantity
            controls.add_widget(minus)
            controls.add_widget(quantity)
            controls.add_widget(plus)
            card.add_widget(controls)
            self._template_cards[key] = card
            grid.add_widget(card)
        cart = Panel(orientation='vertical', padding=dp(18), spacing=dp(10))
        cart.add_widget(self._label('PESANAN KAMU', 12, 26, color=GREY, bold=True))
        cart.add_widget(self._label('Momen pilihanmu', 22, 36, bold=True))
        # Only the item list scrolls. The session count and payable total remain
        # visible even when all four templates have quantities in the order.
        items = ScrollView(do_scroll_x=False, bar_width=dp(4))
        self.summary = self._label('', 15, auto_height=True)
        items.add_widget(self.summary)
        cart.add_widget(items)
        self.cart_sessions = self._label('', 13, 26, color=GREY)
        self.cart_total = self._label('', 27, 44, bold=True)
        cart.add_widget(self.cart_sessions)
        cart.add_widget(self.cart_total)
        cart.add_widget(self._label('3 foto + 1 retake per sesi.', 13, 30, color=GREY))
        self.start_button = self._button('LANJUT KE PEMBAYARAN', self._start_selected, False)
        page.add_widget(self._responsive_row(gallery, cart, 280, 300))
        # Keep the primary order action outside scrolling panels so it remains
        # reachable at 800x600 without scrolling a cart or guessing its position.
        page.add_widget(self.start_button)
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
        total = sum(self.quantities.values())
        lines = [f'{t.name}     × {self.quantities[t.template_id]}' for t in self.templates
                 if self.quantities[t.template_id]]
        amount = 'Rp' + f'{total * PRICE_PER_SESSION:,}'.replace(',', '.')
        self.summary.text = ('\n'.join(lines) if lines else
                             'Belum ada pilihan.\nTambahkan sesi dengan tombol +.')
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
        """Render a non-payable demo QR and explicit, one-shot simulation action."""
        from photobooth.qr_code import create_qr_image
        page = self._reset('payment', 'Satu langkah sebelum berfoto.', 'SIMULASI PEMBAYARAN · Bukan QRIS valid. Jangan transfer uang.')
        self.payment_total = total_amount
        pay = Panel(orientation='vertical', padding=dp(14), spacing=dp(6))
        pay.add_widget(self._label('QR DEMO / TIDAK UNTUK TRANSFER', 12, 24, bold=True, color=CORAL, align='center'))
        qr = self._display(create_qr_image(f'PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR {total_amount}'), crisp=True)
        qr.size_hint_y = None
        # 180px plus its quiet zone is legible at 800x600. The old 228px QR
        # and 420px minimum card were clipped by the two full-width actions.
        qr.height = dp(180)
        self.payment_qr = qr
        pay.add_widget(qr)
        pay.add_widget(self._label('Menunggu simulasi pembayaran', 15, 28, bold=True, align='center'))
        pay.add_widget(self._label('Tekan tombol simulasi untuk melanjutkan.\nTidak ada uang yang ditagihkan.', 13, 40, color=GREY, align='center'))
        pay.add_widget(Widget())
        detail = Panel(orientation='vertical', padding=dp(18), spacing=dp(10))
        detail.add_widget(self._label('RINGKASAN PESANAN', 12, 28, bold=True, color=GREY))
        order_list = ScrollView(do_scroll_x=False, bar_width=dp(4))
        order_text = self._label(order_summary, 16, auto_height=True)
        self.payment_order = order_text
        order_list.add_widget(order_text)
        detail.add_widget(order_list)
        detail.add_widget(self._label(f'{session_count} sesi × Rp5.000', 13, 30, color=GREY))
        detail.add_widget(self._label('Rp ' + f'{total_amount:,}'.replace(',', '.'), 30, 60, bold=True))
        def confirm_once():
            # A second tap cannot create another transaction or reserve another
            # Drive folder. Controller guards also reject off-screen callbacks.
            if not self.payment_confirm.disabled:
                self.payment_confirm.disabled = True
                on_confirm()
        self.payment_confirm = self._button('SIMULASIKAN PEMBAYARAN BERHASIL', confirm_once)
        page.add_widget(self._responsive_row(pay, detail, 330, 324))
        self.payment_back = self._button('UBAH PESANAN', on_back, secondary=True)
        self.payment_back.size_hint_x = .45
        page.add_widget(self._actions(self.payment_back, self.payment_confirm))

    def show_capture(self, session_label, capture_count, preview_image,
                     action_label='AMBIL FOTO', countdown_text='', can_capture=True, is_retake=False):
        """Make the camera the visual focus; keep progress and actions beside it."""
        page = self._reset('capture', 'Senyum, ini momenmu.', session_label)
        camera = Panel(fill=INK, orientation='vertical', padding=dp(14), spacing=dp(8))
        camera.add_widget(self._label('LIVE CAMERA', 11, 26, color=SOFT, bold=True))
        self.preview = KivyImage(fit_mode='contain')
        camera.add_widget(self.preview)
        if preview_image is not None:
            self.update_live_preview(preview_image)
        camera.add_widget(self._label('Lihat ke kamera, bukan ke layar.', 13, 28, color=SOFT, align='center'))
        guide = Panel(orientation='vertical', padding=dp(18), spacing=dp(10))
        guide.add_widget(self._label('FOTO PENGGANTI' if is_retake else f'FOTO {min(capture_count + 1, 3)} / 3',
                                     13, 28, color=GREY, bold=True))
        self.countdown = self._label(countdown_text or 'Siap?', 44, bold=True, align='center')
        guide.add_widget(self.countdown)
        guide.add_widget(self._label('Atur posisi, lalu tekan tombol.\nCountdown 5 detik.', 14, 66, color=GREY))
        progress = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        for index in range(3):
            progress.add_widget(self._label(f'{index + 1:02d}\n' + ('Siap' if index < capture_count else '—'),
                                           12, color=SAGE if index < capture_count else GREY,
                                           align='center'))
        guide.add_widget(progress)
        self.capture_button = self._button(action_label, self.callbacks['on_capture'], can_capture)
        page.add_widget(self._responsive_row(camera, guide, 240, 300))
        page.add_widget(self.capture_button)

    def update_live_preview(self, image):
        """Fit only a preview copy, preserving full-resolution source photos."""
        if self.current_screen == 'capture' and self.preview is not None:
            display = image.copy()
            display.thumbnail((640, 480))
            self._display(display, self.preview)

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
        self.preview.canvas.ask_update()

    def set_countdown(self, seconds, is_retake=False):
        """Render controller timer ticks without sleeping on the GUI thread."""
        if self.current_screen == 'capture':
            self.countdown.text = str(seconds)
            self.set_capture_enabled(False)

    def set_capture_enabled(self, enabled):
        if self.current_screen == 'capture':
            self.capture_button.disabled = not enabled

    def show_review(self, photo_paths, session_label, selected_index, retake_available, status_message=''):
        """Review all three photos; mark the exact selected retake target."""
        page = self._reset('review', 'Sudah pas? Atau satu kali lagi?',
                           f'{session_label}  ·  Sisa retake: {int(retake_available)}')
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
                display = source.convert('RGB')
                display.thumbnail((600, 450))
            card.add_widget(self._display(display))
            card.add_widget(self._button(f'Foto {index + 1}' + (' · DIPILIH' if selected else ' · Pilih untuk retake'),
                                         lambda i=index: self.callbacks['on_select_photo'](i), retake_available,
                                         secondary=not selected))
            gallery.add_widget(card)
        fit_review()
        page.add_widget(self._label('Pilih satu foto untuk retake. Ketiga foto dipakai pada hasil akhir.', 13, 36, color=GREY))
        self.retake_button = self._button('RETAKE FOTO TERPILIH', self.callbacks['on_retake'],
                                         selected_index is not None and retake_available, secondary=True)
        self.accept_button = self._button('GUNAKAN FOTO INI', self.callbacks['on_accept_session'])
        page.add_widget(self._actions(self.retake_button, self.accept_button))
        self.set_status(status_message)

    def show_result(self, image_path, session_label, transaction_id, has_next_session,
                    seconds_remaining=None, qr_image=None, qr_pending=False, upload_message=''):
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
        photo.add_widget(self._label('Cetak fisik belum terhubung.', 12, 28, color=GREY, align='center'))
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

    def set_result_qr(self, qr_image, pending=False):
        """Keep the destination visible independently from synchronization state."""
        if self.current_screen != 'result' or self.qr_view is None:
            return
        pixels = qr_image.tobytes() if qr_image is not None else None
        if qr_image is not None:
            if pixels != self._qr_bytes:
                self._display(qr_image, self.qr_view, crisp=True)
            self.qr_title.text = 'Scan untuk membuka folder foto'
        else:
            self.qr_view.texture = None
            self.qr_title.text = 'Menyiapkan QR folder...' if pending else 'Mode lokal · QR Drive tidak tersedia'
        self._qr_bytes = pixels

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
        popup = Popup(title=title, content=body, size_hint=(.85, .8), auto_dismiss=False)
        body.add_widget(self._button('TUTUP', popup.dismiss))
        popup.open()
