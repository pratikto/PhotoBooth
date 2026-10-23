"""Native portrait P3 photo pages; I/O stays in the isolated photo worker."""

import math
import time

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from photobooth.advertising import PROJECT_ROOT
from .flow import PHOTO_CONFIRM, CAPTURE, REVIEW, RESULT, PHOTO_PAGES, TEMPLATES
from .theme import PixelCard, text_label, GOLD, MUTED, CYAN
from .branding import CAMERA_ART


def image_texture(photo):
    texture = Texture.create(size=photo.size, colorfmt='rgb')
    texture.blit_buffer(photo.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
    texture.flip_vertical()
    return texture


class PhotoViews:
    def _init_photos(self):
        self._photo_jobs = None
        self._photo_view = {}
        self._photo_error = ''
        self._photo_prepared = False
        self._countdown_event = None
        self._live_image = None
        self._camera_texture = None
        self._last_live_frame = None
        self._photo_refresh_at = 0

    def _enter_photo_test(self):
        if not any(self.quantities.values()):
            return
        from .photos import PhotoJobs, configured_test
        self.navigation.confirm_photo_test()
        if self._photo_jobs is None:
            self._photo_jobs = PhotoJobs(factory=lambda: configured_test(PROJECT_ROOT / 'data' / 'kiosk-v2-p3'))
        self._photo_view = {}
        self._photo_error = ''
        self._photo_jobs.submit('reset' if self._photo_prepared else 'prepare')
        self._show()

    def _leave_photo_confirm(self):
        if self._photo_jobs.busy:
            return
        self.navigation.page = TEMPLATES
        self._show()

    def _photo_submit(self, action, *args):
        if self._suspended or self._closed or self._photo_jobs is None or self._photo_jobs.busy:
            return
        self._photo_error = ''
        if self._photo_jobs.submit(action, *args):
            if action != 'snapshot':
                self._show()

    def _admit_photo_test(self):
        if self.camera_device.read() is None:
            self._photo_error = 'Kamera belum siap. Sambungkan kamera lalu coba lagi.'
            self._show()
            return
        self._photo_submit('start', self.templates, dict(self.quantities))

    def _poll_photos(self):
        jobs = self._photo_jobs
        if jobs is None or self._closed or self._suspended:
            return
        outcome = jobs.poll()
        if outcome is not None:
            if outcome.value:
                self._photo_view = outcome.value
            if outcome.error:
                self._photo_error = ('Proses belum berhasil. Periksa kamera, penyimpanan atau koneksi; '
                                     'foto yang tersimpan tetap aman. Detail ada di log.')
            elif outcome.action == 'prepare':
                self._photo_prepared = True
            phase = self._photo_view.get('phase')
            if phase in {CAPTURE, REVIEW, RESULT, 'done'}:
                self.navigation.photo_step(phase)
            if phase == 'done':
                self._return_ad()
                return
            if not self._suspended:
                if outcome.action == 'snapshot':
                    self._update_delivery_label()
                else:
                    self._show()
                if outcome.action == 'capture' and not outcome.error:
                    self.audio_v2.cue('shutter')
                if outcome.action == 'compose' and not outcome.error:
                    self.audio_v2.cue('success')
        if (not self._suspended and self.navigation.page == RESULT and not jobs.busy and
                time.monotonic() >= self._photo_refresh_at):
            self._photo_refresh_at = time.monotonic() + 3
            jobs.submit('snapshot')

    def _photo_pause(self):
        self._cancel_countdown()

    def _cancel_countdown(self):
        if self._countdown_event is not None:
            self._countdown_event.cancel()
            self._countdown_event = None

    def _start_countdown(self):
        if self._photo_jobs.busy or self._countdown_event is not None:
            return
        if self.camera_device.read() is None:
            self._photo_error = 'Kamera belum siap. Hitung mundur belum dimulai.'
            self._show()
            return
        self._photo_error = ''
        self._countdown_deadline = time.monotonic() + 5
        self._last_count = None
        self._countdown_event = Clock.schedule_interval(self._countdown_tick, .05)
        self._countdown_tick(0)

    def _countdown_tick(self, _dt):
        if self._suspended or self._closed or self.navigation.page != CAPTURE:
            self._cancel_countdown()
            return False
        frame = self.camera_device.read()
        if frame is None:
            self._cancel_countdown()
            self._photo_error = 'Kamera terputus. Sambungkan kembali, lalu ulangi hitung mundur.'
            self._show()
            return False
        remaining = math.ceil(max(0, self._countdown_deadline - time.monotonic()))
        self._capture_button.disabled = True
        self._abort_photo_button.disabled = True
        if remaining == 0:
            self._cancel_countdown()
            self._photo_submit('capture', frame)
            return False
        if remaining != self._last_count:
            self._count_label.text = str(remaining)
            self.audio_v2.cue('count')
            self._last_count = remaining

    def _update_live_photo(self, frame):
        if self.navigation.page != CAPTURE or self._live_image is None:
            return
        if frame is None:
            self._live_image.texture = None
            self._live_image.opacity = 0
            self._camera_hint.text = 'KAMERA BELUM SIAP • sambungkan kamera'
            self._count_label.font_size = dp(28)
            self._count_label.text = 'KAMERA\nBELUM SIAP'
        elif frame is not self._last_live_frame:
            self._live_image.opacity = 1
            self._last_live_frame = frame
            # Bound upload bytes; this view-only texture never reaches saved photos.
            step = max(1, (frame.shape[1] + 639) // 640)
            preview = frame[::step, ::step]
            size = (preview.shape[1], preview.shape[0])
            if self._camera_texture is None or self._camera_texture.size != size:
                self._camera_texture = Texture.create(size=size, colorfmt='bgr')
                self._camera_texture.flip_vertical()
                self._camera_texture.flip_horizontal()
            self._camera_texture.blit_buffer(preview.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
            self._live_image.texture = self._camera_texture
            self._camera_hint.text = 'PREVIEW CERMIN • hasil foto tidak dicerminkan'
            if self._countdown_event is None:
                self._count_label.text = ''
        if frame is not None:
            self._count_label.font_size = dp(100)
        if self._countdown_event is None:
            self._capture_button.disabled = frame is None or self._photo_jobs.busy

    def _build_photo_page(self, canvas):
        self._live_image = None
        self._last_live_frame = None
        shell = self._frame(canvas, brand_height=65)
        page = self.navigation.page
        title = {PHOTO_CONFIRM: 'UJI FOTO', CAPTURE: 'SENYUM DULU, MEONG!',
                 REVIEW: 'PILIH MOMEN TERBAIK', RESULT: 'STRIP KAMU SUDAH SIAP'}[page]
        self._brand(shell, title, 'MODE UJI • TANPA PEMBAYARAN')
        view = self._photo_view
        if view.get('session_number'):
            shell.add_widget(text_label(
                f"SESI {view['session_number']}/{view['session_count']} • {view['template']} • {view['copies']} LEMBAR",
                size=14, height=28, color=CYAN))
        if page == PHOTO_CONFIRM:
            self._build_photo_confirm(shell)
        elif page == CAPTURE:
            self._build_capture(shell)
        elif page == REVIEW:
            self._build_review(shell)
        else:
            self._build_result(shell)
        status = ('Sedang memproses… tunggu sebentar.' if self._photo_jobs.busy else self._photo_error)
        self._photo_message = text_label(status, size=13, height=62, color=GOLD)
        shell.add_widget(self._photo_message)

    def _photo_action(self, title, callback, *, disabled=False, variant='primary', height=56):
        return self._action(title, callback, variant=variant, height=height,
                            disabled=disabled or self._photo_jobs.busy)

    def _build_photo_confirm(self, shell):
        card = PixelCard(orientation='vertical', padding=16, spacing=8)
        self._photo_confirm_card = card
        card.add_widget(Widget())
        card.add_widget(Image(source=str(CAMERA_ART), fit_mode='contain',
                              size_hint_y=None, height=dp(90)))
        card.add_widget(text_label('3 FOTO + 1 RETAKE PER DESAIN', size=20, height=52,
                                   color=GOLD, bold=True))
        total = sum(self.quantities.values())
        designs = sum(value > 0 for value in self.quantities.values())
        card.add_widget(text_label(f'{designs} desain • {total} lembar pilihan', size=19, height=36))
        card.add_widget(text_label(
            'Foto uji disimpan di perangkat ini.\n'
            'Preview kamera memakai cermin; foto asli tetap normal.\n\n'
            'Jumlah lembar tidak menambah sesi foto.\n'
            'Cetak hanya dikirim setelah tombol CETAK ditekan.\n'
            'Drive hanya tersedia jika dikonfigurasi operator.',
            size=16, height=190, color=MUTED))
        card.add_widget(Widget())
        shell.add_widget(card)
        shell.add_widget(self._photo_action('SETUJU & MULAI UJI FOTO', self._admit_photo_test,
                                            disabled=not self._photo_prepared))
        if not self._photo_prepared and not self._photo_jobs.busy:
            shell.add_widget(self._photo_action('COBA PERSIAPAN LAGI',
                                                lambda: self._photo_submit('prepare'), variant='secondary'))
        shell.add_widget(self._photo_action('KEMBALI PILIH TEMPLATE', self._leave_photo_confirm,
                                            variant='tertiary', height=48))

    def _build_capture(self, shell):
        view = self._photo_view
        number = view.get('captured', 0) + 1
        shell.add_widget(text_label('RETAKE • 1 KESEMPATAN' if view.get('retake') else f'FOTO {number} / 3',
                                    size=22, height=42, color=GOLD, bold=True))
        card = PixelCard(orientation='vertical', padding=8)
        host = FloatLayout()
        self._live_image = Image(fit_mode='contain', opacity=0, pos_hint={'x': 0, 'y': 0})
        host.add_widget(self._live_image)
        self._count_label = text_label('', size=100, height=150, color=GOLD, bold=True)
        self._count_label.size_hint = (.6, .4)
        self._count_label.pos_hint = {'center_x': .5, 'center_y': .5}
        host.add_widget(self._count_label)
        card.add_widget(host)
        shell.add_widget(card)
        self._camera_hint = text_label('MENYIAPKAN KAMERA…', size=13, height=42, color=MUTED)
        shell.add_widget(self._camera_hint)
        self._capture_button = self._photo_action('SIAP • HITUNG MUNDUR 5 DETIK', self._start_countdown)
        shell.add_widget(self._capture_button)
        self._abort_photo_button = self._photo_action('AKHIRI UJI • SIMPAN FOTO YANG ADA',
                                                     lambda: self._photo_submit('abort'),
                                                     variant='tertiary', height=48)
        shell.add_widget(self._abort_photo_button)

    def _build_review(self, shell):
        view = self._photo_view
        for index, photo in enumerate(view['thumbnails']):
            card = PixelCard(orientation='horizontal', padding=8, spacing=10)
            card.add_widget(Image(texture=image_texture(photo), fit_mode='contain', size_hint_x=.64))
            side = BoxLayout(orientation='vertical', spacing=8, size_hint_x=.36)
            side.add_widget(Widget())
            side.add_widget(text_label(f'FOTO {index + 1}', size=19, height=38, color=GOLD))
            side.add_widget(self._photo_action('RETAKE', lambda index=index: self._photo_submit('retake', index),
                                               disabled=view['retake_used'], variant='secondary', height=52))
            side.add_widget(Widget())
            card.add_widget(side)
            shell.add_widget(card)
        shell.add_widget(text_label('Retake sudah dipakai.' if view['retake_used'] else
                                    'Boleh ambil ulang satu foto. Foto asli tetap disimpan.',
                                    size=14, height=42, color=MUTED))
        shell.add_widget(self._photo_action('PAKAI FOTO INI • BUAT STRIP', lambda: self._photo_submit('compose')))
        shell.add_widget(self._photo_action('AKHIRI UJI • SIMPAN FOTO YANG ADA',
                                            lambda: self._photo_submit('abort'), variant='tertiary', height=48))

    def _delivery_text(self):
        view = self._photo_view
        upload = view['upload_status']
        if upload == 'LOCAL_ONLY':
            delivery = 'MODE LOKAL • foto tersimpan di perangkat; tanpa QR download'
        elif upload == 'UPLOAD_COMPLETE':
            delivery = 'DRIVE TERVERIFIKASI • pindai QR pada strip untuk download'
        elif view.get('retention_error'):
            delivery = 'UPLOAD DITAHAN • operator perlu memeriksa kebijakan retensi Drive'
        else:
            delivery = 'UPLOAD BELUM SELESAI • foto lokal aman; download belum terverifikasi'
        printing = {'NOT_SENT': 'Cetak belum dikirim.', 'SUBMITTED': 'Terkirim ke printer • periksa lembar fisik.',
                    'SENDING': 'Mengirim ke printer…', 'UNCERTAIN': 'Hasil cetak belum pasti • periksa printer.'}
        return delivery + '\n' + printing[view['print_state']]

    def _update_delivery_label(self):
        if self.navigation.page == RESULT and hasattr(self, '_delivery_label'):
            self._delivery_label.text = self._delivery_text()

    def _build_result(self, shell):
        view = self._photo_view
        card = PixelCard(orientation='vertical', padding=10)
        card.add_widget(Image(texture=image_texture(view['strip']), fit_mode='contain'))
        shell.add_widget(card)
        self._delivery_label = text_label(self._delivery_text(), size=14, height=72, color=CYAN)
        shell.add_widget(self._delivery_label)
        uncertain = view['print_state'] == 'UNCERTAIN' and not view['print_checked']
        shell.add_widget(self._photo_action(
            f"CETAK UJI • {view['copies']} LEMBAR" if view['print_available'] else 'CETAK UJI • BELUM DIAKTIFKAN OPERATOR',
            lambda: self._photo_submit('print_result'), variant='secondary',
            disabled=not view['print_available'] or view['print_state'] != 'NOT_SENT'))
        if uncertain:
            shell.add_widget(self._photo_action('SAYA SUDAH CEK PRINTER',
                                                lambda: self._photo_submit('acknowledge_print'), variant='tertiary'))
        label = 'SESI BERIKUTNYA' if view['session_number'] < view['session_count'] else 'SELESAI • KEMBALI IKLAN'
        shell.add_widget(self._photo_action(label, lambda: self._photo_submit('next'), disabled=uncertain))
