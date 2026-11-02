"""Explicit private-preview development UI over the existing portrait app.

No payment/print/Drive adapter is mounted. This is not the complete physical-UAT
candidate. Default/legacy launchers never instantiate this subclass.
"""
import os
import time

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView

from .app import PortraitKioskV2App
from .flow import ADVERT, BROWSING_PAGES, CAPTURE, RESULT, TEMPLATES
from .photo_views import image_texture
from .photos import PhotoJobs
from .post_preview_photos import PrivatePhotoService
from .post_preview_idle import PrivateInactivityPolicy
from .theme import ArcadeButton, CYAN, GOLD, MUTED, PixelCard, text_label


class PrivatePreviewApp(PortraitKioskV2App):
    def __init__(self, private_root, *, private_service=None, idle_policy=None, **kwargs):
        # Refuse mixed profiles rather than changing ambient merchant settings.
        if any(os.environ.get(key) == '1' for key in (
                'PHOTOBOOTH_V2_CHECKOUT_SANDBOX', 'PHOTOBOOTH_V2_CHECKOUT_MOCK',
                'PHOTOBOOTH_V2_PRINT', 'PHOTOBOOTH_V2_DRIVE')):
            raise ValueError('Private preview requires isolated delivery-off profile')
        self._private_root = private_root
        self._private_service = private_service
        self._private_pending_event = None
        self._private_idle_policy = idle_policy or PrivateInactivityPolicy()
        if not isinstance(self._private_idle_policy, PrivateInactivityPolicy):
            raise TypeError('Validated phase-aware inactivity policy required')
        self._private_warning_at = None
        super().__init__(**kwargs)

    def _init_photos(self):
        super()._init_photos()
        self._photo_jobs = PhotoJobs(service=self._private_service,
            factory=lambda: PrivatePhotoService(self._private_root))

    def _warm_photo_delivery(self):
        pass  # No paid/legacy background queue or Drive pool in this profile.

    def _build_templates(self, canvas):
        super()._build_templates(canvas)
        self._test_photo_button.text = 'MULAI FOTO'

    def _photo_capture_allowed(self):
        service = self._photo_jobs.service
        return (not self._closed and not self._suspended and service is not None
                and not service._hidden.is_set() and self._photo_view.get('phase') == 'capture'
                and self.navigation.page == CAPTURE)

    def _photo_submit(self, action, *args):
        if action == 'capture':
            if not self._photo_capture_allowed():
                return
            view = self._photo_view
            args = (*args, view['capture_slot'], view['revision'], view['retake'], view['generation'])
        if action == 'abort':
            return self._queue_private_retirement('USER_CANCEL')
        return super()._photo_submit(action, *args)

    def _queue_private_retirement(self, event):
        self._private_pending_event = event
        self._private_hold()
        service = self._photo_jobs.service
        if service is not None and service.lease is not None and not self._photo_jobs.busy:
            if self._photo_jobs.submit('retire', event):
                self._private_pending_event = None

    def _private_hold(self, *, show_ads=False):
        service = self._photo_jobs.service
        if service is not None:
            service.hide_private()
        self._cancel_countdown()
        self._photo_view = {'phase': 'hold'}
        self._photo_error = ''
        self._camera_texture = None
        self._last_live_frame = self._last_preview = None
        if self._live_image is not None:
            self._live_image.texture = None
        self.navigation.page = ADVERT if show_ads else RESULT
        if show_ads:
            self._reset_visit()
        self._show()

    def _sandbox_lock_customer(self):
        service = self._photo_jobs.service
        if self._photo_jobs.busy or service is not None and service.lease is not None:
            self._queue_private_retirement('APP_SUSPENDED')

    def _sandbox_photo_outcome(self, outcome):
        service = self._photo_jobs.service
        if self._private_pending_event is not None:
            self._queue_private_retirement(self._private_pending_event)
            return True
        if service is not None and service._hidden.is_set():
            self._private_hold()
            return True
        phase = (outcome.value or {}).get('phase')
        if phase in {'final_preview', 'hold'}:
            self.navigation.page = RESULT
            self._show()
            return True
        if outcome.action == 'edit' and not outcome.error:
            self.navigation.page = TEMPLATES
            self._show()
            return True
        return False

    def _return_ad(self):
        service = self._photo_jobs.service
        if service is not None and service.lease is not None:
            self._queue_private_retirement('USER_CANCEL')
            return
        return super()._return_ad()

    def _tick(self, dt):
        service = self._photo_jobs.service
        if service is not None and service.lease is not None:
            if self._closed or self._suspended or service._hidden.is_set():
                return
            phase = self.navigation.page if self.navigation.page in BROWSING_PAGES else self._photo_view.get('phase')
            active_worker = bool(self._photo_jobs.busy and self._photo_jobs.current_action not in {'snapshot', 'warn', 'check_payment', 'ccp_visible'})
            now = time.monotonic()
            decision = self._private_idle_policy.decision(phase, now-self._last_activity,
                worker_busy=active_worker, countdown_active=self._countdown_event is not None)
            if decision == 'ACTIVE_WORK':
                self._last_activity = now
                self._private_warning_at = None
                if self._photo_error.startswith('Sesi tidak aktif.'):
                    self._photo_error = ''
                    if getattr(self, '_photo_message', None) is not None:
                        self._photo_message.text = ''
            elif decision in {'WARNING', 'EXPIRED'}:
                if self._private_warning_at is None:
                    self._private_warning_at = now
                    if not self._photo_jobs.busy:
                        self._photo_jobs.submit('warn')
                if (decision == 'EXPIRED' and
                        now-self._private_warning_at >= self._private_idle_policy.warning_seconds):
                    self._queue_private_retirement('INACTIVITY_EXPIRED')
                else:
                    self._photo_error = 'Sesi tidak aktif. Sentuh layar untuk melanjutkan.'
                    if getattr(self, '_photo_message', None) is not None:
                        self._photo_message.text = self._photo_error
            else:
                self._private_warning_at = None
                if self._photo_error.startswith('Sesi tidak aktif.'):
                    self._photo_error = ''
                    if getattr(self, '_photo_message', None) is not None:
                        self._photo_message.text = ''
            return
        return super()._tick(dt)

    def _build_photo_confirm(self, shell):
        card = PixelCard(orientation='vertical', padding=16, spacing=8)
        card.add_widget(text_label('FOTO DULU, PREVIEW SEMUA DESAIN', size=20, height=70, color=GOLD))
        card.add_widget(text_label('3 foto dan maksimal 1 retake per desain.\n'
            'Foto tetap privat di perangkat.\nBelum ada pembayaran, cetak, atau download.',
            size=17, height=160, color=MUTED))
        shell.add_widget(card)
        shell.add_widget(self._photo_action('SETUJU & MULAI FOTO', self._admit_photo_test,
                                            disabled=not self._photo_prepared))
        shell.add_widget(self._photo_action('KEMBALI PILIH DESAIN', self._leave_photo_confirm,
                                            variant='tertiary'))

    def _build_capture(self, shell):
        super()._build_capture(shell)
        self._abort_photo_button.text = 'BATAL • LINDUNGI SESI'

    def _build_review(self, shell):
        super()._build_review(shell)
        for widget in shell.walk():
            if isinstance(widget, ArcadeButton) and widget.text.startswith('AKHIRI UJI'):
                widget.text = 'BATAL • LINDUNGI SESI'

    def _build_photo_page(self, canvas):
        if self._photo_view.get('phase') == 'hold':
            shell = self._frame(canvas, brand_height=65)
            self._brand(shell, 'SESI DILINDUNGI', 'Tidak ada pembayaran baru')
            shell.add_widget(text_label('Foto privat disembunyikan.\nSesi sebelumnya tetap terlindungi.',
                                       size=20, height=150, color=MUTED))
            return
        return super()._build_photo_page(canvas)

    def _build_result(self, shell):
        view = self._photo_view
        if view['phase'] == 'final_preview':
            shell.add_widget(text_label('PREVIEW SEMUA DESAIN • BELUM DIBAYAR',
                                       size=18, height=60, color=GOLD))
            scroll = ScrollView(do_scroll_x=False)
            designs = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
            designs.bind(minimum_height=designs.setter('height'))
            for design in view['designs']:
                card = PixelCard(orientation='horizontal', padding=8, spacing=8,
                                 size_hint_y=None, height=dp(285))
                card.add_widget(Image(texture=image_texture(design['strip']), fit_mode='contain'))
                side = BoxLayout(orientation='vertical', spacing=dp(8))
                side.add_widget(text_label(design['name']+f"\n{design['copies']} lembar", size=16, height=70))
                side.add_widget(self._photo_action('TINJAU DESAIN',
                    lambda key=design['template_id']: self._photo_submit('review', key),
                    variant='secondary', height=52))
                card.add_widget(side)
                designs.add_widget(card)
            scroll.add_widget(designs)
            shell.add_widget(scroll)
            amount_text = 'Rp'+f"{view['amount']:,}".replace(',', '.')
            shell.add_widget(text_label('TOTAL '+amount_text, size=22, height=42, color=GOLD))
            shell.add_widget(self._photo_action('UBAH DESAIN / JUMLAH',
                lambda: self._photo_submit('edit'), variant='secondary'))
            shell.add_widget(self._photo_action('PEMBAYARAN BELUM TERHUBUNG', lambda: None, disabled=True))
        else:
            shell.add_widget(text_label('PREVIEW DESAIN • BELUM DIBAYAR', size=18, height=55, color=GOLD))
            shell.add_widget(Image(texture=image_texture(view['strip']), fit_mode='contain'))
            shell.add_widget(self._photo_action('TINJAU FOTO',
                lambda: self._photo_submit('review', view['template_id']), variant='secondary'))
            shell.add_widget(self._photo_action('LANJUT', lambda: self._photo_submit('next')))
        self._delivery_label = text_label('Foto privat • belum dicetak atau diunggah',
                                          size=13, height=40, color=CYAN)
        shell.add_widget(self._delivery_label)

    def _update_delivery_label(self):
        pass  # This private profile has no delivery status to poll.
