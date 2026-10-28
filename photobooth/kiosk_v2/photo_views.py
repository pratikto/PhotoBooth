"""Native portrait P3 photo pages; I/O stays in the isolated photo worker."""

import math
import time
import logging
import os

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from photobooth.advertising import PROJECT_ROOT
from .flow import PHOTO_CONFIRM, CAPTURE, REVIEW, RESULT, PHOTO_PAGES, TEMPLATES, SANDBOX_CHECKOUT
from .theme import PixelCard, text_label, GOLD, MUTED, CYAN
from .branding import CAMERA_ART
from .theme import ArcadeButton
from photobooth.delivery_timing import event


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
        self._last_preview = None
        self._photo_refresh_at = 0
        self._photo_pending_action = None
        self._download_qr_texture_key = None

    def _ensure_photo_jobs(self):
        if self._photo_jobs is None:
            from .photos import PhotoJobs, configured_test
            photo_root = (self._sandbox_jobs.store.flow.path.parent / 'photo-tests' if self._sandbox_enabled
                          else PROJECT_ROOT / 'data' / 'kiosk-v2-p3')
            self._photo_jobs = PhotoJobs(factory=lambda: configured_test(photo_root, configuration_root=PROJECT_ROOT, storage_layout=1) if self._sandbox_enabled else configured_test(photo_root))

    def _warm_photo_delivery(self):
        # Resume the existing isolated queue on launch, without requiring a new
        # photo/transaction. Native clients/pool I/O initialize on PhotoJobs.
        if (not self._sandbox_enabled and (os.environ.get('PHOTOBOOTH_V2_DRIVE') == '1' or os.environ.get('PHOTOBOOTH_V2_STORAGE') == '2')
                and self._photo_jobs is None):
            self._ensure_photo_jobs()
            self._photo_jobs.submit('prepare')

    def _enter_photo_test(self):
        if (not any(self.quantities.values()) or
                (self._sandbox_enabled and (not self._sandbox_consent or
                 (self._sandbox_view or {}).get('phase') != 'RESERVED'))):
            return
        self.navigation.confirm_photo_test()
        self._ensure_photo_jobs()
        self._photo_view = {}
        self._photo_error = ''
        if not self._photo_jobs.busy:
            self._photo_jobs.submit('reset' if self._photo_prepared else 'prepare')
        self._show()

    def _leave_photo_confirm(self):
        if self._photo_jobs.busy:
            return
        self.navigation.page = SANDBOX_CHECKOUT if self._sandbox_consent else TEMPLATES
        self._show()

    def _photo_submit(self, action, *args):
        if self._suspended or self._closed or self._photo_jobs is None or self._photo_jobs.busy:
            return
        self._photo_error = ''
        if self._photo_jobs.submit(action, *args):
            self._photo_pending_action = action
            if action != 'snapshot':
                # Preserve the current camera/strip and layout while I/O runs.
                # Completion rebuilds once, retiring these callbacks by revision.
                for control in self.stage.walk():
                    if isinstance(control, ArcadeButton):
                        control.disabled = True
                self._photo_message.text = 'Sedang memproses… tunggu sebentar.'
                if action == 'print_result':
                    self._update_delivery_label()

    def _admit_photo_test(self):
        if not self._photo_view.get('drive_ready', True):
            return
        if self.camera_device.read() is None:
            if self._sandbox_enabled and self._sandbox_report_issue('DEVICE_UNAVAILABLE'):
                return
            self._photo_error = 'Kamera belum siap. Sambungkan kamera lalu coba lagi.'
            self._show()
            return
        if self._sandbox_enabled:
            self._sandbox_prepare_photo()
        else:
            self._photo_submit('start', self.templates, dict(self.quantities))

    def _poll_photos(self):
        jobs = self._photo_jobs
        if jobs is None or self._closed or self._suspended:
            return
        outcome = jobs.poll()
        if outcome is not None:
            previous_setup = tuple(self._photo_view.get(k) for k in ('drive_ready','drive_error'))
            self._photo_pending_action = None
            if outcome.value:
                self._photo_view = outcome.value
            if outcome.error:
                self._photo_error = {
                    'drive_configuration': 'Drive belum dikonfigurasi. Hubungi operator; belum ada foto diunggah.',
                    'booth_profile': 'Profil penyimpanan belum sesuai. Hubungi operator sebelum mulai foto.',
                }.get(getattr(outcome,'setup_error',None),
                    'Proses belum berhasil. Periksa kamera, penyimpanan atau koneksi; '
                    'foto yang tersimpan tetap aman. Detail ada di log.')
            elif outcome.action == 'prepare':
                self._photo_prepared = True
            if outcome.action != 'snapshot':
                self._photo_refresh_at = time.monotonic() + 1
            if self._sandbox_photo_outcome(outcome):
                return
            # A boot-time preparation/late snapshot must not rebuild the ad
            # player or move a visitor onto an old photo screen.
            if self.navigation.page not in PHOTO_PAGES:
                return
            phase = self._photo_view.get('phase')
            if phase in {CAPTURE, REVIEW, RESULT, 'done'}:
                self.navigation.photo_step(phase)
            if phase == 'done':
                self._return_ad()
                return
            if not self._suspended:
                if outcome.action == 'snapshot':
                    self._photo_message.text = self._photo_error
                    if self.navigation.page == PHOTO_CONFIRM:
                        if previous_setup != tuple(self._photo_view.get(k) for k in ('drive_ready','drive_error')):
                            self._show()
                    else:
                        self._update_delivery_label()
                else:
                    self._show()
                if outcome.action == 'capture' and not outcome.error:
                    self.audio_v2.cue('shutter')
                if outcome.action == 'compose' and not outcome.error:
                    self.audio_v2.cue('success')
                    if (self._photo_view.get('auto_print') and self._photo_view.get('print_available')
                            and self._photo_view.get('print_state') == 'NOT_SENT'):
                        self._photo_submit('print_result')
        waiting_drive = (self._photo_view.get('drive_enabled') and
            ((self.navigation.page == PHOTO_CONFIRM and not self._photo_view.get('drive_ready')) or
             (self.navigation.page == RESULT and self._photo_view.get('upload_status') != 'UPLOAD_COMPLETE')))
        if (not self._suspended and waiting_drive and not jobs.busy and
                self._photo_prepared and
                time.monotonic() >= self._photo_refresh_at):
            self._photo_refresh_at = time.monotonic() + 3
            jobs.submit('snapshot')

    def _photo_pause(self):
        self._cancel_countdown()

    def _cancel_countdown(self):
        if self._countdown_event is not None:
            self._countdown_event.cancel()
            self._countdown_event = None

    def _photo_capture_allowed(self):
        # PhotoViews also supports the standalone, nonfinancial P3 preview.
        # The complete Sandbox app always supplies its durable admission guard.
        guard = getattr(self, '_sandbox_can_capture', None)
        return guard() if guard is not None else True

    def _start_countdown(self, source='button'):
        if not self._photo_capture_allowed() or self._photo_jobs.busy or self._countdown_event is not None:
            return
        if self.camera_device.read() is None:
            if self._sandbox_enabled and self._sandbox_report_issue('DEVICE_UNAVAILABLE'):
                return
            self._photo_error = 'Kamera belum siap. Hitung mundur belum dimulai.'
            self._show()
            return
        self._photo_error = ''
        self.palm_shutter.latch()
        self._countdown_deadline = time.monotonic() + 5
        self._last_count = None
        self._countdown_event = Clock.schedule_interval(self._countdown_tick, .05)
        logging.getLogger(__name__).info('Countdown started source=%s revision=%s', source, self._view_revision)
        self._countdown_tick(0)

    def _countdown_tick(self, _dt):
        if self._suspended or self._closed or self.navigation.page != CAPTURE:
            self._cancel_countdown()
            return False
        frame = self.camera_device.read()
        if frame is None:
            self._cancel_countdown()
            if self._sandbox_enabled and self._sandbox_report_issue('DEVICE_UNAVAILABLE'):
                return False
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

    def _update_live_photo(self, frame, preview=None):
        if self.navigation.page != CAPTURE or self._live_image is None:
            return
        if frame is None:
            self._live_image.texture = None
            self._live_image.opacity = 0
            self._camera_hint.text = 'KAMERA BELUM SIAP • sambungkan kamera'
            self._count_label.font_size = dp(28)
            self._count_label.text = 'KAMERA\nBELUM SIAP'
        elif preview is not None and preview is not self._last_preview:
            started = time.perf_counter()
            self._live_image.opacity = 1
            self._last_preview = preview
            size = preview.size
            if self._camera_texture is None or self._camera_texture.size != size:
                self._camera_texture = Texture.create(size=size, colorfmt='rgb')
                self._camera_texture.flip_vertical()
                self._camera_texture.flip_horizontal()
            self._camera_texture.blit_buffer(preview.pixels, colorfmt='rgb', bufferfmt='ubyte')
            self._live_image.texture = self._camera_texture
            # Like v1, invalidate the canvas after updating a reused texture.
            # Its identity is unchanged, so Image.texture emits no redraw.
            self._live_image.canvas.ask_update()
            self._camera_hint.text = 'PREVIEW & STRIP CERMIN • foto asli tetap normal'
            if self._countdown_event is None:
                self._count_label.text = ''
            self.performance.upload(time.perf_counter() - started)
        if frame is not None:
            self._count_label.font_size = dp(100)
        if self._countdown_event is None:
            self._capture_button.disabled = not self._photo_capture_allowed() or frame is None or self._photo_jobs.busy

    def _build_photo_page(self, canvas):
        self._live_image = None
        self._last_live_frame = None
        self._last_preview = None
        shell = self._frame(canvas, brand_height=65)
        page = self.navigation.page
        title = {PHOTO_CONFIRM: 'UJI FOTO', CAPTURE: 'SENYUM DULU, MEONG!',
                 REVIEW: 'PILIH MOMEN TERBAIK', RESULT: 'STRIP KAMU SUDAH SIAP'}[page]
        self._brand(shell, title, 'MODE UJI • QRIS SANDBOX' if self._sandbox_consent else 'MODE UJI • TANPA PEMBAYARAN')
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
        status = ('Sedang memproses… tunggu sebentar.' if self._photo_jobs.foreground_busy else self._photo_error)
        self._photo_message = text_label(status, size=13, height=62, color=GOLD)
        shell.add_widget(self._photo_message)

    def _photo_action(self, title, callback, *, disabled=False, variant='primary', height=56):
        return self._action(title, callback, variant=variant, height=height,
                            disabled=disabled or self._photo_jobs.foreground_busy)

    def _build_photo_confirm(self, shell):
        card = PixelCard(orientation='vertical', padding=16, spacing=8)
        self._photo_confirm_card = card
        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(orientation='vertical',size_hint_y=None,spacing=dp(8))
        body.bind(minimum_height=body.setter('height'))
        scroll.add_widget(body);card.add_widget(scroll)
        body.add_widget(Image(source=str(CAMERA_ART), fit_mode='contain',
                              size_hint_y=None, height=dp(70)))
        body.add_widget(text_label('3 FOTO + 1 RETAKE PER DESAIN', size=20, height=52,
                                   color=GOLD, bold=True))
        total = sum(self.quantities.values())
        designs = sum(value > 0 for value in self.quantities.values())
        body.add_widget(text_label(f'{designs} desain • {total} lembar pilihan', size=19, height=36))
        setup = self._photo_view
        if setup.get('drive_enabled'):
            message = ('DRIVE DI BACKGROUND • foto & cetak tetap bisa offline' if setup.get('storage_layout') == 2 else
                       'DRIVE SIAP • folder foto sudah tersedia' if setup.get('drive_ready') else
                       'MENYIAPKAN DRIVE • tunggu folder tersedia' if not setup.get('drive_error') else
                       'DRIVE BELUM SIAP • periksa koneksi / hubungi operator')
            body.add_widget(text_label(message,size=13,height=52,color=CYAN))
        body.add_widget(text_label(
            'Foto uji disimpan di perangkat ini.\n'
            'Preview dan strip memakai cermin; foto asli tetap normal.\n\n'
            'Jumlah lembar tidak menambah sesi foto.\n' +
            ('Setelah disetujui, strip dicetak otomatis.\n' if self._photo_view.get('auto_print') else
             'Cetak dikirim setelah tombol CETAK ditekan.\n') +
            'Drive hanya tersedia jika dikonfigurasi operator.',
            size=16, height=190, color=MUTED))
        shell.add_widget(card)
        shell.add_widget(self._photo_action('SETUJU & MULAI UJI FOTO', self._admit_photo_test,
                                            disabled=not self._photo_prepared or not setup.get('drive_ready',True)))
        if not self._photo_prepared and not self._photo_jobs.busy:
            shell.add_widget(self._photo_action('COBA PERSIAPAN LAGI',
                                                lambda: self._photo_submit('prepare'), variant='secondary'))
        shell.add_widget(self._photo_action('KEMBALI KE PESANAN UJI' if self._sandbox_consent else 'KEMBALI PILIH TEMPLATE', self._leave_photo_confirm,
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
        self._palm_hint = text_label('Tekan SIAP untuk mulai foto.', size=13, height=38, color=CYAN)
        shell.add_widget(self._palm_hint)
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
            delivery = 'DRIVE TERVERIFIKASI • pindai QR di layar untuk download'
        elif view.get('binding_error'):
            delivery = 'DRIVE GAGAL TERSAMBUNG • operator perlu memeriksa setup/deployment Drive'
        elif upload == 'PENDING_DRIVE_BINDING':
            delivery = 'MENYIAPKAN FOLDER • foto lokal aman; upload & QR menyusul saat online'
        elif view.get('retention_error'):
            delivery = 'UPLOAD DITAHAN • operator perlu memeriksa kebijakan retensi Drive'
        elif upload in {'ACTION_REQUIRED','LOCAL_EXPIRED'}:
            delivery = 'DRIVE PERLU DIPERIKSA • hubungi operator; download belum terverifikasi'
        elif upload == 'UPLOAD_RETRY':
            delivery = 'UPLOAD TERTUNDA • foto lokal aman; dicoba lagi otomatis'
        else:
            total = view.get('upload_total', 0)
            verified = view.get('upload_verified', 0)
            delivery = (f'MENGUNGGAH FOTO {min(verified+1,total)} DARI {total} • foto lokal aman'
                        if total and verified < total else
                        'MEMVERIFIKASI FOTO • proses lanjut di background')
        printing = {'NOT_SENT': 'Cetak belum dikirim.', 'SUBMITTED': 'Terkirim ke printer • periksa lembar fisik.',
                    'SENDING': 'Mengirim ke printer…', 'UNCERTAIN': 'Hasil cetak belum pasti • periksa printer.'}
        progress = ('Menyiapkan / mengirim cetak…' if self._photo_jobs.busy and
                    self._photo_pending_action == 'print_result' else printing[view['print_state']])
        return delivery + '\n' + progress

    def _update_delivery_label(self):
        if self.navigation.page == RESULT and hasattr(self, '_delivery_label'):
            self._delivery_label.text = self._delivery_text()
            self._update_download_qr()

    def _update_download_qr(self):
        if not getattr(self,'_download_image',None):
            return
        view=self._photo_view
        photo=view.get('download_qr')
        key=(view.get('transaction_id'),view.get('folder_url')) if photo is not None else None
        if key != self._download_qr_texture_key:
            self._download_image.texture = image_texture(photo) if photo is not None else None
            if self._download_image.texture:
                self._download_image.texture.mag_filter = self._download_image.texture.min_filter = 'nearest'
            self._download_qr_texture_key = key
            if key is not None:
                event('gui_qr_visible', view.get('transaction_id'), result='ok',
                      upload_complete=view.get('upload_status') == 'UPLOAD_COMPLETE')
        self._download_image.opacity = 1 if photo is not None else 0
        if photo is not None:
            if view.get('upload_status') == 'UPLOAD_COMPLETE':
                hint = 'SCAN UNTUK DOWNLOAD'
            elif view.get('retention_error') or view.get('upload_status') == 'UPLOAD_RETRY':
                hint = 'SCAN & SIMPAN LINK\nUpload tertunda.\nHubungi operator.'
            else:
                hint = 'SCAN & SIMPAN LINK\nFoto sedang diunggah.\nCek lagi dalam 30 menit.'
        elif view.get('binding_error') or view.get('upload_status') in {'UPLOAD_COMPLETE', 'LOCAL_EXPIRED', 'ACTION_REQUIRED'}:
            hint = 'Link foto belum siap; hubungi operator.'
        else:
            hint = 'Menyiapkan link foto.\nQR muncul saat folder siap.'
        self._download_hint.text = hint

    def _build_result(self, shell):
        view = self._photo_view
        self._download_image = None
        self._download_qr_texture_key = None
        card = PixelCard(orientation='horizontal', padding=10,spacing=8)
        card.add_widget(Image(texture=image_texture(view['strip']), fit_mode='contain'))
        if view.get('drive_enabled') or view.get('folder_url'):
            download = BoxLayout(orientation='vertical',spacing=dp(8),size_hint_x=.75)
            download.add_widget(text_label('FOTO DIGITAL',size=16,height=35,color=GOLD,bold=True))
            self._download_image=Image(fit_mode='contain',opacity=0)
            download.add_widget(self._download_image)
            self._download_hint=text_label('',size=13,height=70,color=CYAN)
            download.add_widget(self._download_hint)
            card.add_widget(download)
            self._update_download_qr()
        shell.add_widget(card)
        self._delivery_label = text_label(self._delivery_text(), size=14, height=72, color=CYAN)
        shell.add_widget(self._delivery_label)
        uncertain = view['print_state'] == 'UNCERTAIN' and not view['print_checked']
        print_title = (f"CETAK OTOMATIS • {view['copies']} LEMBAR" if view.get('auto_print') else
                       f"CETAK UJI • {view['copies']} LEMBAR") if view['print_available'] else 'CETAK UJI • BELUM DIAKTIFKAN OPERATOR'
        shell.add_widget(self._photo_action(
            print_title,
            lambda: self._photo_submit('print_result'), variant='secondary',
            disabled=not view['print_available'] or view.get('auto_print',False) or view['print_state'] != 'NOT_SENT'))
        if uncertain:
            shell.add_widget(self._photo_action('SAYA SUDAH CEK PRINTER',
                                                lambda: self._photo_submit('acknowledge_print'), variant='tertiary'))
        label = 'SESI BERIKUTNYA' if view['session_number'] < view['session_count'] else 'SELESAI • KEMBALI IKLAN'
        shell.add_widget(self._photo_action(label, lambda: self._photo_submit('next'), disabled=uncertain))

