"""Native checkout integration fixture, explicitly unavailable to Sandbox money.

Reuses original portrait shell/controls and private proof card. No launcher or
production configuration mounts this incomplete paid-delivery flow.
"""
import time

from kivy.uix.image import Image

from .ccp_view import PrivateCCPCard
from .flow import RESULT
from .photo_views import image_texture
from .post_preview_app import PrivatePreviewApp
from .post_preview_checkout import CHECKOUT_PHASES, PrivateCheckoutService
from .theme import GOLD, MUTED, text_label


class PrivateCheckoutFixtureApp(PrivatePreviewApp):
    def __init__(self, private_root, *, private_service, **kwargs):
        if not isinstance(private_service, PrivateCheckoutService):
            raise TypeError('Explicit incomplete mock checkout service required')
        self._claim_card = self._claim_pending = None
        self._payment_check_at = 0
        super().__init__(private_root, private_service=private_service, **kwargs)

    def _show(self):
        if self._claim_card is not None:
            self._claim_card.retire()
            self._claim_card = None
        return super()._show()

    def _private_hold(self):
        self._claim_pending = None
        return super()._private_hold()

    def _photo_action(self, title, callback, **kwargs):
        if title == 'PEMBAYARAN BELUM TERHUBUNG':
            title, callback = 'LANJUT CHECKOUT SIMULASI', self._freeze_checkout
            kwargs['disabled'] = False
        return super()._photo_action(title, callback, **kwargs)

    def _freeze_checkout(self):
        view = self._photo_view
        self._photo_submit('freeze_checkout', view.get('revision'), view.get('amount'))

    def _sandbox_photo_outcome(self, outcome):
        if super()._sandbox_photo_outcome(outcome):
            return True
        if (outcome.value or {}).get('phase') in CHECKOUT_PHASES:
            self.navigation.page = RESULT
            self._payment_check_at = time.monotonic()+10
            self._show()
            return True
        return False

    def _claim_current(self, offer):
        service = self._photo_jobs.service
        return (not self._closed and not self._suspended and not service._hidden.is_set()
                and self.navigation.page == RESULT
                and self._photo_view.get('phase') in {'claim_proof', 'checkout_ready'}
                and self._photo_view.get('ccp_offer') is offer)

    def _claim_rendered(self, offer):
        if self._claim_current(offer) and self._photo_view.get('phase') == 'claim_proof':
            self._claim_pending = offer

    def _poll_photos(self):
        super()._poll_photos()
        if self._closed or self._suspended or self._photo_jobs.busy:
            return
        if self._claim_pending is not None:
            offer, self._claim_pending = self._claim_pending, None
            if self._claim_current(offer):
                self._photo_submit('ccp_visible', offer)
        elif (self._photo_view.get('phase') in {'payment_pending', 'payment_hold'}
                and time.monotonic() >= self._payment_check_at):
            self._payment_check_at = time.monotonic()+10
            self._photo_submit('check_payment')

    def _build_photo_page(self, canvas):
        if self._photo_view.get('phase') not in CHECKOUT_PHASES:
            return super()._build_photo_page(canvas)
        self._live_image = None
        self._camera_texture = None
        self._last_live_frame = self._last_preview = None
        shell = self._frame(canvas, brand_height=65)
        self._brand(shell, 'CHECKOUT PRIVAT', 'SIMULASI • BUKAN PEMBAYARAN QRIS')
        view = self._photo_view
        phase = view['phase']
        if phase in {'claim_proof', 'checkout_ready'}:
            offer = view.get('ccp_offer')
            if offer is not None and view.get('ccp_qr') is not None:
                self._claim_card = PrivateCCPCard(offer, view['ccp_qr'], self._claim_rendered,
                                                is_current=lambda: self._claim_current(offer))
                shell.add_widget(self._claim_card)
            else:
                shell.add_widget(text_label('Bukti privat belum siap. Belum ada pembayaran.',
                                           size=18, height=120, color=MUTED))
                shell.add_widget(self._photo_action('COBA TAMPILKAN BUKTI',
                                                   lambda: self._photo_submit('offer_claim')))
            shell.add_widget(self._photo_action('SUDAH SIMPAN BUKTI • LANJUT SIMULASI',
                lambda: self._photo_submit('begin_payment'), disabled=phase != 'checkout_ready'))
        elif phase == 'paid_hold':
            shell.add_widget(text_label('PEMBAYARAN SIMULASI TERVERIFIKASI', size=20, height=100, color=GOLD))
            shell.add_widget(text_label('Layanan tetap tercatat sebagai kewajiban.\n'
                'Integrasi tiket, cetak, dan Drive belum selesai.', size=17, height=160, color=MUTED))
        else:
            payment = view.get('payment') or {}
            shell.add_widget(text_label('MENUNGGU PEMBAYARAN SIMULASI', size=19, height=65, color=GOLD))
            if view.get('payment_qr') is not None:
                shell.add_widget(Image(texture=image_texture(view['payment_qr']), fit_mode='contain'))
            else:
                shell.add_widget(text_label('Status belum pasti. Pesanan asli tetap dilindungi.',
                                           size=18, height=120, color=MUTED))
            shell.add_widget(self._photo_action('PERIKSA STATUS',
                lambda: self._photo_submit('check_payment', 'connectivity'), variant='secondary'))
            if payment.get('state') == 'EXPIRED_UNPAID':
                shell.add_widget(self._photo_action('LANJUTKAN PESANAN ASLI',
                    lambda: self._photo_submit('continue_payment', True)))
        shell.add_widget(self._photo_action('BATAL • LINDUNGI SESI',
                                            lambda: self._photo_submit('abort'), variant='tertiary'))
        self._photo_message = text_label(self._photo_error, size=13, height=62, color=GOLD)
        shell.add_widget(self._photo_message)
