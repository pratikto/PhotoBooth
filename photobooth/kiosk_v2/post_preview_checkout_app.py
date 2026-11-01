"""Native checkout integration fixture, explicitly unavailable to Sandbox money.

Reuses original portrait shell/controls and private proof card. No launcher or
production configuration mounts this incomplete paid-delivery flow.
"""
import time

from kivy.uix.image import Image

from .ccp_view import PrivateCCPCard, PrivateRecoveryTicketCard
from photobooth.post_preview_ticket_window import VisibleTicketWindow
from .flow import RESULT
from .photo_views import image_texture
from .post_preview_app import PrivatePreviewApp
from .post_preview_checkout import CHECKOUT_PHASES, TICKET_PHASES, PrivateCheckoutService
from .theme import GOLD, MUTED, text_label


class PrivateCheckoutFixtureApp(PrivatePreviewApp):
    def __init__(self, private_root, *, private_service, **kwargs):
        if not isinstance(private_service, PrivateCheckoutService):
            raise TypeError('Explicit incomplete mock checkout service required')
        self._claim_card = self._claim_pending = None
        self._ticket_card = self._ticket_pending = None
        self._ticket_window = self._ticket_next_button = None
        self._ticket_countdown = self._ticket_status = None
        self._ticket_receipt_pending = self._ticket_dismiss_pending = False
        self._payment_check_at = 0
        super().__init__(private_root, private_service=private_service, **kwargs)

    def _show(self):
        if self._claim_card is not None:
            self._claim_card.retire()
            self._claim_card = None
        if self._ticket_card is not None:
            self._ticket_card.retire()
            self._ticket_card = None
        return super()._show()

    def _private_hold(self):
        self._claim_pending = self._ticket_pending = None
        self._ticket_receipt_pending = self._ticket_dismiss_pending = False
        if self._ticket_window is not None:
            self._ticket_window.retire()
        if self._ticket_card is not None:
            self._ticket_card.retire()
            self._ticket_card = None
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
        view = outcome.value or {}
        phase = view.get('phase')
        if outcome.action == 'ticket_visible':
            if outcome.error or phase != 'ticket_visible':
                if self._ticket_status is not None:
                    self._ticket_status.text = 'Bukti tampilan tiket belum dapat diverifikasi.'
                return True
            if self._ticket_window is not None and self._ticket_window.start(genuine_visible=True):
                self._ticket_receipt_pending = True
            if self._ticket_next_button is not None:
                self._ticket_next_button.disabled = False
            self._update_ticket_countdown()
            return True  # Keep the exact same visible QR widget; never reset timer.
        if outcome.action == 'ticket_send_receipt':
            if self._ticket_status is not None:
                status = (view.get('ticket_receipt') or {}).get('receipt_state','UNCERTAIN')
                self._ticket_status.text = ('Status kirim tiket: '+status
                                            if not outcome.error else
                                            'Status kirim tiket perlu pemeriksaan.')
            return True  # A late printer ACK MUST NOT recreate/redisplay the code.
        if outcome.action == 'ticket_dismiss':
            if self._ticket_window is not None:
                self._ticket_window.retire()
            self.navigation.page = RESULT
            self._show()
            if not outcome.error and self._photo_jobs.service.paid_delivery_enabled:
                self._photo_submit('prepare_paid_delivery')
            return True
        if outcome.action in {'prepare_paid_delivery','paid_delivery_status','paid_print_next'}:
            # Render the original paid obligation; never mark service completed
            # because a printer transport or a Drive upload acknowledged bytes.
            self.navigation.page = RESULT
            self._show()
            return True
        if (phase == 'paid_hold' and not outcome.error
                and outcome.action in {'begin_payment','check_payment','continue_payment'}
                and self._photo_jobs.service.paid_ticket_enabled):
            self.navigation.page = RESULT
            self._show()
            self._photo_submit('prepare_ticket')
            return True
        if super()._sandbox_photo_outcome(outcome):
            return True
        if phase in CHECKOUT_PHASES:
            self.navigation.page = RESULT
            self._payment_check_at = time.monotonic()+10
            if phase == 'ticket_offer' and self._ticket_window is None:
                self._ticket_window = VisibleTicketWindow()
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

    def _ticket_current(self, offer):
        service = self._photo_jobs.service
        return (not self._closed and not self._suspended and not service._hidden.is_set()
                and self.navigation.page == RESULT
                and self._photo_view.get('phase') in TICKET_PHASES
                and not self._ticket_dismiss_pending
                and self._photo_view.get('ticket_offer') is offer)

    def _ticket_rendered(self, offer):
        if (self._ticket_current(offer)
                and self._photo_view.get('phase') == 'ticket_offer'):
            self._ticket_pending = offer

    def _update_ticket_countdown(self):
        if self._ticket_countdown is None or self._ticket_window is None:
            return
        remaining = self._ticket_window.remaining()
        if remaining is not None:
            self._ticket_countdown.text = f'Tiket tampil: {remaining} detik tersisa'

    def _ticket_next(self, *, user=True):
        if self._ticket_window is None or not self._ticket_window.dismiss(
                next_pressed=user):
            return
        self._ticket_dismiss_pending = True
        # Retire private QR/code immediately even if receipt printer is still
        # sending. The original serialized worker must still finish its job.
        if self._ticket_card is not None:
            self._ticket_card.retire()
            self._ticket_card = None
        if self._ticket_next_button is not None:
            self._ticket_next_button.disabled = True
        if self._ticket_countdown is not None:
            self._ticket_countdown.text = 'Tiket ditutup. Menyelesaikan pengiriman tiket...'

    def _poll_photos(self):
        super()._poll_photos()
        if self._closed or self._suspended or self._photo_jobs.busy:
            return
        if self._claim_pending is not None:
            offer, self._claim_pending = self._claim_pending, None
            if self._claim_current(offer):
                self._photo_submit('ccp_visible', offer)
        elif self._ticket_pending is not None:
            offer, self._ticket_pending = self._ticket_pending, None
            if self._ticket_current(offer):
                self._photo_submit('ticket_visible', offer)
        elif (self._photo_view.get('phase') in {'payment_pending', 'payment_hold'}
                and time.monotonic() >= self._payment_check_at):
            self._payment_check_at = time.monotonic()+10
            self._photo_submit('check_payment')
        if self._photo_view.get('phase') == 'ticket_visible':
            self._update_ticket_countdown()
            if (self._ticket_window is not None and self._ticket_window.active
                    and self._ticket_window.remaining() == 0):
                self._ticket_next(user=False)
            # Direct PhotoJobs submit (not _photo_submit) keeps NEXT usable
            # during the slow physical send, while maintaining single-flight.
            if self._ticket_receipt_pending and not self._photo_jobs.busy:
                if self._photo_jobs.submit('ticket_send_receipt'):
                    self._ticket_receipt_pending = False
            elif (self._ticket_dismiss_pending and
                  not self._ticket_receipt_pending and not self._photo_jobs.busy):
                if self._photo_jobs.submit('ticket_dismiss'):
                    self._ticket_dismiss_pending = False

    def _build_ticket_page(self, canvas):
        self._live_image = None
        self._camera_texture = None
        self._last_live_frame = self._last_preview = None
        shell = self._frame(canvas, brand_height=65)
        self._brand(shell, 'TIKET PEMULIHAN', 'SIMULASI • SIMPAN QR SEBELUM LANJUT')
        view = self._photo_view
        offer = view.get('ticket_offer')
        if offer is not None and view.get('ticket_qr') is not None:
            self._ticket_card = PrivateRecoveryTicketCard(
                offer, view['ticket_qr'], self._ticket_rendered,
                is_current=lambda: self._ticket_current(offer))
            shell.add_widget(self._ticket_card)
        else:
            shell.add_widget(text_label('Tiket privat belum siap. Pembayaran tetap tercatat.',
                                        size=17, height=120, color=MUTED))
        self._ticket_countdown = text_label(
            'Memastikan QR dan kode terlihat penuh...', size=14, height=40, color=GOLD)
        shell.add_widget(self._ticket_countdown)
        shell.add_widget(text_label(
            'JIKA TIDAK DISIMPAN, SESI PRIVAT TIDAK BISA DIPULIHKAN.',
            size=13, height=40, color=MUTED))
        self._ticket_next_button = self._photo_action(
            'LANJUT • SIMPAN TIKET', self._ticket_next,
            disabled=self._ticket_window is None or not self._ticket_window.active)
        shell.add_widget(self._ticket_next_button)
        self._ticket_status = text_label(
            'Mencetak tiket asli satu kali, tanpa menunggu printer.',
            size=12, height=36, color=MUTED)
        shell.add_widget(self._ticket_status)
        self._photo_message = text_label(self._photo_error, size=13, height=45, color=GOLD)
        shell.add_widget(self._photo_message)
        self._update_ticket_countdown()


    def _build_paid_delivery_page(self, canvas):
        """Native MOCK-only purchased-output page; never a completed service claim."""
        self._live_image = None
        self._camera_texture = None
        self._last_live_frame = self._last_preview = None
        shell = self._frame(canvas, brand_height=65)
        self._brand(shell, 'HASIL FOTO BERBAYAR', 'SIMULASI • STATUS DELIVERY ASLI')
        data=self._photo_view.get('delivery') or {}
        shell.add_widget(text_label(
            'FOTO SUDAH DIBAYAR • KEWAJIBAN MASIH AKTIF',
            size=17,height=55,color=GOLD))
        url=data.get('folder_url')
        if url:
            from photobooth.qr_code import create_qr_image
            try:
                qr=create_qr_image(url,monochrome=True)
            except (RuntimeError,ValueError,OSError):
                qr=None
            if qr is not None:
                shell.add_widget(Image(texture=image_texture(qr),
                                       fit_mode='contain',size_hint_y=None,height=225))
        completed=data.get('drive_verified') is True
        uploaded=data.get('upload_verified',0)
        total=data.get('upload_total',0)
        shell.add_widget(text_label(
            ('Foto tersinkron di Drive' if completed else
             'Upload Drive: '+str(uploaded)+' dari '+str(total)+' file terverifikasi'),
            size=15,height=50,color=GOLD if completed else MUTED))
        states=data.get('print_states') or {}
        for template_id,state in states.items():
            shell.add_widget(text_label(template_id+' • '+state,size=13,height=36,color=MUTED))
        if data.get('needs_operator_review'):
            shell.add_widget(text_label(
                'Status cetak tidak pasti. Jangan cetak ulang otomatis.',
                size=13,height=55,color=GOLD))
        elif data.get('print_all_submitted'):
            shell.add_widget(text_label(
                'Data cetak terkirim. Kertas fisik harus diperiksa.',
                size=13,height=45,color=MUTED))
        outstanding=any(state=='PREPARED' for state in states.values())
        shell.add_widget(self._photo_action(
            'CETAK FOTO YANG SUDAH DIBAYAR',
            lambda: self._photo_submit('paid_print_next'),
            disabled=not outstanding))
        shell.add_widget(self._photo_action(
            'CEK STATUS UPLOAD',lambda: self._photo_submit('paid_delivery_status'),
            variant='secondary'))
        shell.add_widget(text_label(
            'Status PAID/OWED dilindungi. Menutup UI tidak menghapus pesanan.',
            size=12,height=48,color=MUTED))
        self._photo_message=text_label(self._photo_error,size=13,height=55,color=GOLD)
        shell.add_widget(self._photo_message)

    def _build_photo_page(self, canvas):
        if self._photo_view.get('phase') == 'paid_delivery':
            return self._build_paid_delivery_page(canvas)
        if self._photo_view.get('phase') in TICKET_PHASES:
            return self._build_ticket_page(canvas)
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
            if view.get('ticket_dismissed') and self._photo_jobs.service.paid_delivery_enabled:
                shell.add_widget(self._photo_action('COBA SIAPKAN DELIVERY',
                    lambda: self._photo_submit('prepare_paid_delivery')))
            shell.add_widget(text_label(
                ('Tiket sudah diberikan. Layanan foto masih menunggu cetak dan Drive.'
                 if view.get('ticket_dismissed') else
                 'Layanan tetap tercatat sebagai kewajiban. Tiket dan cetak belum siap.'),
                size=17, height=160, color=MUTED))
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
