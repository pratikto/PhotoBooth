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
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from PIL import Image
from photobooth.catalog import create_template_preview

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


class PhotoBoothUI:
    """Render customer screens and forward actions, without owning session rules."""

    def __init__(self, root, templates, **callbacks):
        # Callback names match app.py exactly. Default-argument captures in loops
        # below are intentional: otherwise every button would use the LAST item.
        self.templates = tuple(templates)
        self.callbacks = callbacks
        self.current_screen = 'welcome'
        self._camera_ready = False
        self._storage_ready = False
        self.shell = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(18))
        # Paint the root itself, not only Window.clearcolor. This keeps the
        # light background visible in screenshots, embedded hosts, and exports.
        with self.shell.canvas.before:
            Color(0.95, 0.96, 0.98, 1)
            background = Rectangle(pos=self.shell.pos, size=self.shell.size)
        self.shell.bind(pos=lambda w, v: setattr(background, 'pos', v),
                        size=lambda w, v: setattr(background, 'size', v))
        root.view = self.shell
        self.header = self._label('Meongs Photobooth', 26, 54)
        self.shell.add_widget(self.header)
        self.content = BoxLayout(orientation='vertical', spacing=dp(10))
        self.shell.add_widget(self.content)
        self.status = self._label('', 14, 64)
        self.shell.add_widget(self.status)
        self.preview = None
        self.qr_view = None
        self._qr_bytes = None

    def _label(self, text, font=18, height=None):
        """Create wrapping text; height=None lets the parent allocate free space."""
        label = Label(text=text, color=NAVY, font_size=dp(font), halign='center')
        label.bind(size=lambda widget, size: setattr(widget, 'text_size', size))
        if height is not None:
            label.size_hint_y = None
            label.height = dp(height)
        return label

    def _button(self, text, callback, enabled=True):
        """Use release events for touch-friendly actions and explicit readiness gates."""
        button = Button(text=text, size_hint_y=None, height=dp(54),
                        background_normal='', background_color=NAVY,
                        disabled=not enabled, font_size=dp(16))
        button.bind(on_release=lambda _widget: callback())
        return button

    def _reset(self, screen, title, subtitle=''):
        """Replace screen widgets while leaving the shell and status line intact."""
        self.current_screen = screen
        self.content.clear_widgets()
        self.preview = None
        self.qr_view = None
        self._qr_bytes = None
        self.set_status('')
        self.content.add_widget(self._label(title, 25, 58))
        if subtitle:
            self.content.add_widget(self._label(subtitle, 16, 56))
        return self.content

    def _display(self, image, widget=None, crisp=False):
        """Upload Pillow pixels into a GPU texture without changing the source.

        Pillow stores rows top-to-bottom; Kivy texture coordinates use the opposite
        orientation, hence flip_vertical(). Preview textures are reused at the
        same resolution to avoid allocating a GPU object on every camera frame.
        QR textures use nearest filtering to preserve hard black/white edges.
        """
        widget = widget or KivyImage(fit_mode='contain')
        rgb = image.convert('RGB')
        texture = widget.texture
        if texture is None or texture.size != rgb.size:
            texture = Texture.create(size=rgb.size, colorfmt='rgb')
            texture.flip_vertical()
        if crisp:
            texture.mag_filter = 'nearest'
            texture.min_filter = 'nearest'
        texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        widget.texture = texture
        return widget

    def set_status(self, message):
        """Update feedback without rebuilding widgets or interrupting a countdown."""
        self.status.text = message

    def set_camera_status(self, ready):
        """Keep camera readiness separate from storage and order selection."""
        self._camera_ready = ready
        self.header.text = 'Meongs Photobooth  |  ' + ('KAMERA SIAP' if ready else 'KAMERA BELUM SIAP')

    def show_welcome(self, camera_ready, status_message):
        """Show the entry screen; storage is checked again when an order starts."""
        self.set_camera_status(camera_ready)
        page = self._reset('welcome', 'Bikin foto seru bareng teman',
                           'Pilih template, ambil foto, lalu simpan hasil digitalnya.')
        page.add_widget(self._label('3 foto baru + maksimal 1 retake per sesi', 22))
        page.add_widget(self._button('Mulai foto', self.callbacks['on_home_start'], camera_ready))
        self.set_status(status_message)

    def show_template_selection(self, camera_ready, status_message, storage_ready=True):
        """Build scrollable template cards, independent quantities, and an order gate."""
        self.set_camera_status(camera_ready)
        self._storage_ready = storage_ready
        page = self._reset('templates', 'Pilih template foto kamu', 'Setiap qty = 1 sesi baru')
        self.quantities = {t.template_id: 0 for t in self.templates}
        self.quantity_labels = {}
        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)
        page.add_widget(scroll)
        for template in self.templates:
            key = template.template_id
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(230), spacing=dp(6))
            card.add_widget(self._display(create_template_preview(template, (360, 150))))
            card.add_widget(self._label(template.name, 17, 32))
            controls = BoxLayout(size_hint_y=None, height=dp(54))
            controls.add_widget(self._button('-', lambda k=key: self._change_quantity(k, -1)))
            quantity = self._label('0', 20)
            self.quantity_labels[key] = quantity
            controls.add_widget(quantity)
            controls.add_widget(self._button('+', lambda k=key: self._change_quantity(k, 1)))
            card.add_widget(controls)
            grid.add_widget(card)
        self.summary = self._label('', 16, 60)
        page.add_widget(self.summary)
        self.start_button = self._button('MULAI SESI FOTO', self._start_selected, False)
        page.add_widget(self.start_button)
        self._refresh_order()
        self.set_status(status_message)

    def _change_quantity(self, key, delta):
        """Clamp quantities at zero and refresh the total without losing selections."""
        self.quantities[key] = max(0, self.quantities[key] + delta)
        self._refresh_order()

    def _refresh_order(self):
        """Require a nonempty order, a working camera, and a reserved storage slot."""
        for key, quantity in self.quantities.items():
            self.quantity_labels[key].text = str(quantity)
        total = sum(self.quantities.values())
        self.summary.text = 'Keranjang: ' + ' | '.join(
            f'{t.name} x {self.quantities[t.template_id]}' for t in self.templates
            if self.quantities[t.template_id]) + f'  —  {total} sesi'
        self.start_button.disabled = not (total and self._camera_ready and self._storage_ready)

    def _start_selected(self):
        """Pass a fresh mapping so UI state cannot mutate the controller's order."""
        self.callbacks['on_start']({k: v for k, v in self.quantities.items() if v > 0})

    def set_storage_status(self, ready, message):
        """Allow the background pool refill to unlock an already selected order."""
        self._storage_ready = ready
        if self.current_screen == 'templates':
            self._refresh_order()
        self.set_status(message)

    def show_payment(self, order_summary, session_count, total_amount, on_confirm, on_back):
        """Display a clearly labelled simulation, with no real QRIS payload.

        QRIS is a payment standard; an arbitrary generated QR must never be
        presented as a payable code. This QR contains demo text only. The
        transaction-folder QR is generated separately after photography.
        """
        from photobooth.qr_code import create_qr_image
        page = self._reset('payment', 'Pembayaran - SIMULASI',
                           'DUMMY: bukan QRIS valid. Jangan transfer uang.')
        scroll = ScrollView()
        body = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        body.bind(minimum_height=body.setter('height'))
        scroll.add_widget(body)
        page.add_widget(scroll)
        amount = 'Rp ' + f'{total_amount:,}'.replace(',', '.')
        body.add_widget(self._label(f'{order_summary}\n{session_count} sesi | Total contoh: {amount}', 18, 100))
        qr = self._display(create_qr_image(f'PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR {total_amount}'), crisp=True)
        qr.size_hint_y = None
        qr.height = dp(220)
        body.add_widget(qr)
        body.add_widget(self._label('Menunggu simulasi pembayaran\nHarga contoh dapat diatur dengan PHOTOBOOTH_DEMO_PRICE.', 15, 65))
        def confirm_once():
            # Disable before dispatch so a double tap cannot allocate two orders.
            if not confirm.disabled:
                confirm.disabled = True
                on_confirm()
        confirm = self._button('SIMULASIKAN PEMBAYARAN BERHASIL', confirm_once)
        page.add_widget(confirm)
        page.add_widget(self._button('KEMBALI PILIH TEMPLATE', on_back))

    def show_capture(self, session_label, capture_count, preview_image,
                     action_label='AMBIL FOTO', countdown_text='', can_capture=True,
                     is_retake=False):
        """Render capture progress; the controller retains the retake/countdown rules."""
        page = self._reset('capture', session_label,
                           'Retake foto terpilih' if is_retake else f'{capture_count}/3 foto tersimpan')
        self.preview = KivyImage(fit_mode='contain')
        page.add_widget(self.preview)
        if preview_image is not None:
            self.update_live_preview(preview_image)
        self.countdown = self._label(countdown_text, 40, 60)
        page.add_widget(self.countdown)
        self.capture_button = self._button(action_label, self.callbacks['on_capture'], can_capture)
        page.add_widget(self.capture_button)

    def update_live_preview(self, image):
        """Fit preview pixels only; saved photos retain their original resolution."""
        if self.current_screen == 'capture' and self.preview is not None:
            display = image.copy()
            display.thumbnail((960, 600))
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
        """Display a scheduled tick without a blocking sleep call."""
        if self.current_screen == 'capture':
            self.countdown.text = str(seconds)
            self.set_capture_enabled(False)

    def set_capture_enabled(self, enabled):
        """Prevent capture before a usable frame or during the active countdown."""
        if self.current_screen == 'capture':
            self.capture_button.disabled = not enabled

    def show_review(self, photo_paths, session_label, selected_index,
                    retake_available, status_message=''):
        """Show three captures and the selected retake target, preserving quota gates."""
        page = self._reset('review', 'Pilih foto yang ingin diganti',
                           f'{session_label} | Sisa retake: {int(retake_available)}')
        row = BoxLayout(spacing=dp(12))
        page.add_widget(row)
        for index, path in enumerate(photo_paths):
            card = BoxLayout(orientation='vertical', spacing=dp(8))
            with Image.open(path) as source:
                display = source.convert('RGB')
                display.thumbnail((500, 400))
            card.add_widget(self._display(display))
            selected = index == selected_index
            button = self._button(f'Foto {index + 1}' + (' - DIPILIH' if selected else ''),
                                  lambda i=index: self.callbacks['on_select_photo'](i), retake_available)
            if selected:
                button.background_color = YELLOW
            card.add_widget(button)
            row.add_widget(card)
        page.add_widget(self._button('RETAKE FOTO TERPILIH', self.callbacks['on_retake'],
                                     selected_index is not None and retake_available))
        page.add_widget(self._button('GUNAKAN FOTO INI', self.callbacks['on_accept_session']))
        self.set_status(status_message)

    def show_result(self, image_path, session_label, transaction_id, has_next_session,
                    seconds_remaining=None, qr_image=None, qr_pending=False, upload_message=''):
        """Show the composition alongside its stable transaction-folder QR.

        A folder link does not imply upload completion. Keep its status text
        visible next to the QR so an offline customer understands missing files.
        """
        page = self._reset('result', 'Sesi selesai', f'{session_label} | {transaction_id}')
        # Fixed-height details used to consume all of a short row, leaving
        # the QR Image with zero height. Give the QR an explicit height and
        # put the whole result panel in a scroll viewport for small windows.
        scroll = ScrollView(do_scroll_x=False)
        row = BoxLayout(spacing=dp(18), size_hint_y=None, height=dp(340))
        scroll.add_widget(row)
        page.add_widget(scroll)
        with Image.open(image_path) as source:
            display = source.convert('RGB')
            display.thumbnail((700, 650))
        row.add_widget(self._display(display))
        details = BoxLayout(orientation='vertical', spacing=dp(10))
        row.add_widget(details)
        self.qr_view = KivyImage(fit_mode='contain', size_hint_y=None, height=dp(180))
        # Kivy images are transparent outside their texture. A solid white backing
        # preserves the QR quiet zone and avoids dark-theme scan failures.
        with self.qr_view.canvas.before:
            Color(1, 1, 1, 1)
            backing = Rectangle(pos=self.qr_view.pos, size=self.qr_view.size)
        self.qr_view.bind(pos=lambda w, v: setattr(backing, 'pos', v),
                          size=lambda w, v: setattr(backing, 'size', v))
        details.add_widget(self.qr_view)
        self.qr_title = self._label('', 17, 54)
        details.add_widget(self.qr_title)
        self.upload_status = self._label(upload_message, 15, 80)
        details.add_widget(self.upload_status)
        self.set_result_qr(qr_image, qr_pending)
        self.completion = self._label('', 18, 40)
        page.add_widget(self.completion)
        if seconds_remaining is not None:
            self.set_completion_countdown(seconds_remaining)
        page.add_widget(self._button('SESI BERIKUTNYA' if has_next_session else 'SELESAI',
                                     self.callbacks['on_next_session' if has_next_session else 'on_finish']))

    def set_result_qr(self, qr_image, pending=False):
        """Replace QR only when pixels change; repeated status polls reuse it."""
        if self.current_screen != 'result' or self.qr_view is None:
            return
        pixels = qr_image.tobytes() if qr_image is not None else None
        if qr_image is not None:
            if pixels != self._qr_bytes:
                self._display(qr_image, self.qr_view, crisp=True)
            self.qr_title.text = 'Scan QR untuk membuka folder transaksi'
        else:
            self.qr_view.texture = None
            self.qr_title.text = 'Menyiapkan QR folder...' if pending else 'QR Drive tidak tersedia (hasil lokal)'
        self._qr_bytes = pixels

    def set_result_upload_status(self, message):
        """Refresh upload feedback independently of the destination QR."""
        if self.current_screen == 'result':
            self.upload_status.text = message

    def set_completion_countdown(self, seconds_remaining):
        """Format the controller-owned final-screen timeout as minutes:seconds."""
        if self.current_screen == 'result':
            minutes, seconds = divmod(max(0, seconds_remaining), 60)
            self.completion.text = f'Kembali ke awal dalam {minutes:02d}:{seconds:02d}'

    def show_error(self, title, message):
        """Use a scrollable modal so long diagnostics remain readable on small screens."""
        body = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(12))
        scroll = ScrollView()
        label = self._label(message, 16)
        label.size_hint_y = None
        label.bind(width=lambda w, width: setattr(w, 'text_size', (width, None)),
                   texture_size=lambda w, size: setattr(w, 'height', size[1] + dp(20)))
        scroll.add_widget(label)
        body.add_widget(scroll)
        popup = Popup(title=title, content=body, size_hint=(0.85, 0.8), auto_dismiss=False)
        body.add_widget(self._button('TUTUP', popup.dismiss))
        popup.open()
