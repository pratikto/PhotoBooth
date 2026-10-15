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
        self.status = self._label('', 12, color=GREY)
        footer.add_widget(self.status)
        self.camera_badge = self._label('Kamera diperiksa', 12, color=GREY, align='right')
        self.camera_badge.size_hint_x = None
        self.camera_badge.width = dp(170)
        footer.add_widget(self.camera_badge)
        self.shell.add_widget(footer)
        self.header = self.brand  # Historical public handle retained for callers.

    def _label(self, text, font=18, height=None, bold=False, color=INK, align='left'):
        """Wrap text within its box instead of letting it overlap adjacent controls."""
        widget = Label(text=text, color=color, font_size=dp(font), bold=bold,
                       halign=align, valign='middle')
        widget.bind(size=lambda w, size: setattr(w, 'text_size', size))
        if height is not None:
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
        self.set_status('')
        active = {'welcome': 1, 'templates': 1, 'payment': 2,
                  'capture': 3, 'review': 3, 'result': 4}.get(screen, 1)
        self.steps.text = '   /   '.join(
            ('[ ' + label + ' ]') if index == active else label
            for index, label in enumerate(('01 Template', '02 Bayar', '03 Foto', '04 Hasil'), 1))
        if title:
            self.content.add_widget(self._label(title, 28, 46, bold=True))
        if subtitle:
            self.content.add_widget(self._label(subtitle, 14, 38, color=GREY))
        return self.content

    def _responsive_row(self, left, right, right_width=330, min_height=350):
        """Make side-by-side cards scroll safely on narrow or short windows.

        The inner layout has an explicit minimum height. This prevents fixed
        captions or buttons from squeezing a QR or camera preview to zero height.
        On phone-width windows, panels stack and can be scrolled vertically.
        """
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(5), scroll_type=['bars', 'content'])
        row = BoxLayout(spacing=dp(18), size_hint_y=None)
        row.add_widget(left)
        row.add_widget(right)
        scroll.add_widget(row)
        def arrange(*_args):
            compact = scroll.width < dp(720)
            row.orientation = 'vertical' if compact else 'horizontal'
            row.height = max(scroll.height, dp(min_height * 2 + 18 if compact else min_height))
            right.size_hint_x = 1 if compact else None
            right.width = scroll.width if compact else dp(right_width)
            left.size_hint_y = right.size_hint_y = 1
        scroll.bind(size=arrange)
        arrange()
        return scroll

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

        aside = Panel(orientation='vertical', padding=dp(24), spacing=dp(12))
        aside.add_widget(self._label('Cara mainnya', 22, 46, bold=True))
        for title, note in [('01   Pilih gaya', 'Pilih template dan jumlah sesi.'),
                            ('02   Siapkan senyum', 'Tiga foto baru di setiap sesi.'),
                            ('03   Simpan momennya', 'Satu retake per sesi. Scan QR folder foto.')]:
            aside.add_widget(self._label(title, 18, 38, bold=True))
            aside.add_widget(self._label(note, 14, 52, color=GREY))
        aside.add_widget(self._label('Pembayaran saat ini masih simulasi.', 12, 48, color=CORAL))
        page.add_widget(self._responsive_row(hero, aside, 330, 460))
        page.add_widget(self._button('MULAI FOTO', self.callbacks['on_home_start'], camera_ready))
        self.set_status(status_message)

    def show_template_selection(self, camera_ready, status_message, storage_ready=True):
        """A compact template gallery plus a continuously updated order summary."""
        self.set_camera_status(camera_ready)
        self._storage_ready = storage_ready
        page = self._reset('templates', 'Pilih gaya fotomu.', 'Setiap qty berarti satu sesi baru berisi tiga foto.')
        self.quantities = {t.template_id: 0 for t in self.templates}
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
        cart = Panel(orientation='vertical', padding=dp(22), spacing=dp(14))
        cart.add_widget(self._label('PESANAN KAMU', 12, 26, color=GREY, bold=True))
        cart.add_widget(self._label('Momen pilihanmu', 23, 52, bold=True))
        self.summary = self._label('', 16)
        cart.add_widget(self.summary)
        cart.add_widget(self._label('3 foto baru + 1 kesempatan retake\ndi setiap sesi yang kamu pilih.', 13, 66, color=GREY))
        self.start_button = self._button('LANJUT KE PEMBAYARAN', self._start_selected, False)
        page.add_widget(self._responsive_row(gallery, cart, 325, 440))
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
        self.summary.text = ('\n\n'.join(lines) + f'\n\n{total} sesi × Rp5.000\n\nTotal  {amount}'
                             if lines else 'Belum ada pilihan.\nTambahkan sesi dengan tombol +.')
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
        pay = Panel(orientation='vertical', padding=dp(22), spacing=dp(8))
        pay.add_widget(self._label('QR DEMO / TIDAK UNTUK TRANSFER', 12, 30, bold=True, color=CORAL, align='center'))
        qr = self._display(create_qr_image(f'PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR {total_amount}'), crisp=True)
        qr.size_hint_y = None
        qr.height = dp(228)
        pay.add_widget(qr)
        pay.add_widget(self._label('Menunggu simulasi pembayaran', 16, 42, bold=True, align='center'))
        pay.add_widget(self._label('Tekan tombol simulasi di sebelah untuk\nmelanjutkan. Tidak ada uang yang ditagihkan.', 14, 62, color=GREY, align='center'))
        detail = Panel(orientation='vertical', padding=dp(22), spacing=dp(12))
        detail.add_widget(self._label('RINGKASAN PESANAN', 12, 28, bold=True, color=GREY))
        detail.add_widget(self._label(order_summary, 17))
        detail.add_widget(self._label(f'{session_count} sesi × Rp5.000', 13, 30, color=GREY))
        detail.add_widget(self._label('Rp ' + f'{total_amount:,}'.replace(',', '.'), 30, 60, bold=True))
        def confirm_once():
            # A second tap cannot create another transaction or reserve another
            # Drive folder. Controller guards also reject off-screen callbacks.
            if not self.payment_confirm.disabled:
                self.payment_confirm.disabled = True
                on_confirm()
        self.payment_confirm = self._button('SIMULASIKAN PEMBAYARAN BERHASIL', confirm_once)
        page.add_widget(self._responsive_row(pay, detail, 380, 420))
        page.add_widget(self.payment_confirm)
        page.add_widget(self._button('KEMBALI PILIH TEMPLATE', on_back, secondary=True))

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
        guide = Panel(orientation='vertical', padding=dp(22), spacing=dp(10))
        guide.add_widget(self._label('FOTO PENGGANTI' if is_retake else f'FOTO {min(capture_count + 1, 3)} / 3',
                                     13, 36, color=GREY, bold=True))
        self.countdown = self._label(countdown_text or 'Siap?', 44, 100, bold=True, align='center')
        guide.add_widget(self.countdown)
        guide.add_widget(self._label('Ambil posisi yang nyaman.\nCountdown dimulai setelah tombol ditekan.', 15, 82, color=GREY))
        for index in range(3):
            guide.add_widget(self._label(f'{index + 1:02d}    ' + ('Tersimpan' if index < capture_count else 'Menunggu'),
                                        14, 28, color=SAGE if index < capture_count else GREY))
        self.capture_button = self._button(action_label, self.callbacks['on_capture'], can_capture)
        page.add_widget(self._responsive_row(camera, guide, 285, 430))
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
        scroll.bind(width=lambda w, width: setattr(gallery, 'cols', 1 if width < dp(620) else 3))
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
        page.add_widget(self._label('Pilih satu foto jika ingin menggantinya. Ketiga foto digunakan dalam hasil akhir.', 13, 44, color=GREY))
        # Keep these actions directly in content so keyboard/automation clients
        # can discover their enabled state without traversing decorative cards.
        page.add_widget(self._button('RETAKE FOTO TERPILIH', self.callbacks['on_retake'],
                                     selected_index is not None and retake_available, secondary=True))
        page.add_widget(self._button('GUNAKAN FOTO INI', self.callbacks['on_accept_session']))
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
        share = Panel(orientation='vertical', padding=dp(16), spacing=dp(8))
        share.add_widget(self._label('BAWA PULANG FOTOMU', 12, 24, bold=True, color=GREY))
        self.qr_view = KivyImage(fit_mode='contain', size_hint_y=None, height=dp(180))
        share.add_widget(self.qr_view)
        self.qr_title = self._label('', 16, 52, bold=True, align='center')
        share.add_widget(self.qr_title)
        self.upload_status = self._label(upload_message, 13, 92, color=GREY, align='center')
        share.add_widget(self.upload_status)
        # The flexible trailing spacer anchors fixed QR content to the top.
        # Otherwise BoxLayout leaves surplus height above it on short screens.
        share.add_widget(Widget())
        page.add_widget(self._responsive_row(photo, share, 350, 455))
        self.set_result_qr(qr_image, qr_pending)
        self.completion = self._label('', 13, 28, color=GREY, align='right')
        page.add_widget(self.completion)
        if seconds_remaining is not None:
            self.set_completion_countdown(seconds_remaining)
        page.add_widget(self._button('SESI BERIKUTNYA' if has_next_session else 'SELESAI',
                                     self.callbacks['on_next_session' if has_next_session else 'on_finish']))

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
        label = self._label(message, 16)
        label.size_hint_y = None
        label.bind(width=lambda w, width: setattr(w, 'text_size', (width, None)),
                   texture_size=lambda w, size: setattr(w, 'height', size[1] + dp(20)))
        scroll.add_widget(label)
        body.add_widget(scroll)
        popup = Popup(title=title, content=body, size_hint=(.85, .8), auto_dismiss=False)
        body.add_widget(self._button('TUTUP', popup.dismiss))
        popup.open()
