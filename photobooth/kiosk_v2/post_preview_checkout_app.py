"""Native checkout integration fixture, explicitly unavailable to Sandbox money.

Reuses original portrait shell/controls and private proof card. No launcher or
production configuration mounts this incomplete paid-delivery flow.
"""
import math
import time

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from .ccp_view import PrivateCCPCard, PrivateRecoveryTicketCard
from photobooth.post_preview_ticket_window import VisibleTicketWindow
from .flow import ADVERT, RESULT
from .photo_views import image_texture
from .post_preview_app import PrivatePreviewApp
from .post_preview_checkout import CHECKOUT_PHASES, TICKET_PHASES, PrivateCheckoutService
from .theme import GOLD, MUTED, PixelCard, text_label
from photobooth.post_preview_pilot_admission import OriginalPilotAdmission
from photobooth.post_preview_store import DraftHeld


class _CheckoutAppBase(PrivatePreviewApp):
    """Shared original checkout controls; concrete profiles validate authority."""
    _sandbox_transport = False

    def _validate_checkout_service(self, service):
        raise TypeError('Concrete checkout profile required')

    def __init__(self, private_root, *, private_service, synthetic_pay_callback=None,
                 synthetic_drive_url=True, **kwargs):
        if synthetic_pay_callback is not None and not callable(synthetic_pay_callback):
            raise TypeError('An explicit synthetic paid fixture must be callable')
        if type(synthetic_drive_url) is not bool:
            raise TypeError('Explicit Drive display mode must be boolean')
        self._synthetic_drive_url = synthetic_drive_url
        self._synthetic_pay_callback = synthetic_pay_callback
        self._validate_checkout_service(private_service)
        self._claim_card = self._claim_pending = None
        self._ticket_card = self._ticket_pending = None
        self._ticket_window = self._ticket_next_button = None
        self._ticket_countdown = self._ticket_status = None
        self._ticket_receipt_pending = self._ticket_dismiss_pending = False
        self._payment_check_at = 0
        self._paid_result_deadline = None
        self._paid_result_countdown = None
        self._pilot_admission = None
        self._pilot_note = ''
        self._pilot_popup = self._pilot_input = None
        super().__init__(private_root, private_service=private_service, **kwargs)

    def _close_pilot_popup(self):
        if self._pilot_input is not None:
            self._pilot_input.text = ''
            self._pilot_input = None
        popup,self._pilot_popup=self._pilot_popup,None
        if popup is not None:
            popup.dismiss()

    def _show(self):
        # Status refreshes/resize retain this visit's original result deadline.
        # Leaving it retires the timer, so it cannot affect a later customer.
        if (self.navigation.page != RESULT
                or self._photo_view.get('phase') != 'paid_delivery'):
            self._paid_result_deadline = None
        self._paid_result_countdown = None
        self._close_pilot_popup()
        if self._claim_card is not None:
            self._claim_card.retire()
            self._claim_card = None
        if self._ticket_card is not None:
            self._ticket_card.retire()
            self._ticket_card = None
        return super()._show()

    def _private_hold(self):
        self._close_pilot_popup()
        self._claim_pending = self._ticket_pending = None
        self._ticket_receipt_pending = self._ticket_dismiss_pending = False
        if self._ticket_window is not None:
            self._ticket_window.retire()
        if self._ticket_card is not None:
            self._ticket_card.retire()
            self._ticket_card = None
        result = super()._private_hold(show_ads=self._pilot_admission is not None)
        if self._pilot_admission is not None:
            self._pilot_note = ''
        return result

    def attach_synthetic_pilot_admission(self, coordinator):
        """Only the explicit owner MOCK pilot can enable private Ads admission."""
        if (not isinstance(coordinator,OriginalPilotAdmission)
                or self._pilot_admission is not None
                or coordinator.jobs is not self._photo_jobs
                or coordinator.claim.ledger is not self._photo_jobs.service.ledger):
            raise DraftHeld('Exact synthetic pilot coordinator required')
        self._pilot_admission=coordinator
        if self.navigation.page==ADVERT:
            self._show()

    def _pilot_prepare_new(self):
        if self._pilot_admission is None or self.navigation.page!=ADVERT:
            return True
        try:
            self._pilot_admission.ensure_new_visitor_ready()
        except (DraftHeld,ValueError,OSError,RuntimeError):
            self._pilot_note='Sesi sebelumnya belum bisa diamankan. Pembayaran baru ditahan.'
            self._show()
            return False
        self._pilot_note=''
        # A successful PREPARE/ACK is the only point at which a new visitor
        # may start. Reset all transient gallery/game/tutorial state from A;
        # never inherit A's template quantities or one-visit tutorial flag.
        # Do not touch A's durable PAID/OWED, media or customer proof journals.
        self._reset_visit()
        self.navigation.tutorial_seen=False
        self.navigation.entry_source=None
        self._photo_view={'phase':'confirm'}
        self._ticket_window=self._ticket_card=self._ticket_pending=None
        self._ticket_receipt_pending=self._ticket_dismiss_pending=False
        return True

    def _choose_photo(self, source='manual'):
        if self._pilot_prepare_new():
            return super()._choose_photo(source)

    def _choose_game(self, source='manual'):
        if self._pilot_prepare_new():
            return super()._choose_game(source)

    def _build_advert(self, canvas):
        super()._build_advert(canvas)
        if self._pilot_admission is None:
            return
        shell=self._advert_host.parent.parent
        shell.add_widget(self._photo_action(
            'PUNYA TIKET PEMULIHAN • SIMULASI',self._pilot_open_claim,
            variant='tertiary',height=dp(44)))
        if self._pilot_note:
            shell.add_widget(text_label(self._pilot_note,size=12,height=dp(50),color=GOLD))

    def _pilot_open_claim(self):
        if (self._pilot_admission is None or self.navigation.page!=ADVERT
                or self._closed or self._suspended):
            return
        self._close_pilot_popup()
        panel=BoxLayout(orientation='vertical',padding=dp(12),spacing=dp(10))
        panel.add_widget(text_label(
            'Scan tiket asli atau masukkan kode lengkap. '
            'Kode tidak disimpan di aplikasi.',
            size=14,height=dp(85),color=MUTED))
        field=TextInput(multiline=False,password=True,hint_text='CCP atau Recovery Ticket',
                        size_hint_y=None,height=dp(52))
        panel.add_widget(field)
        panel.add_widget(self._photo_action(
            'VALIDASI TIKET',lambda: self._pilot_submit_claim(field.text),height=dp(50)))
        panel.add_widget(self._photo_action(
            'BATAL',self._close_pilot_popup,variant='tertiary',height=dp(48)))
        popup=Popup(title='PEMULIHAN PRIVAT • SIMULASI',content=panel,
                    size_hint=(.92,.65),auto_dismiss=False)
        self._pilot_input,self._pilot_popup=field,popup
        popup.open()
        field.focus=True

    def _pilot_submit_claim(self,payload):
        if self._pilot_admission is None or self.navigation.page!=ADVERT:
            return
        self._close_pilot_popup()
        try:
            result=self._pilot_admission.recover_paid(
                payload.strip() if isinstance(payload,str) else '')
        except (PermissionError,DraftHeld,ValueError,OSError,RuntimeError):
            self._pilot_note='Tiket tidak dapat diverifikasi. Foto privat tetap terlindungi.'
            self._show()
            return
        if result['state']=='WAIT':
            self._pilot_note='Photobooth sedang digunakan. Silakan coba lagi nanti.'
            self._show()
            return
        if result['state']!='RESTORED':
            self._pilot_note='Pemulihan sementara belum tersedia.'
            self._show()
            return
        self._pilot_note=''
        self._ticket_window=None
        self._ticket_pending=self._ticket_card=None
        self._ticket_receipt_pending=self._ticket_dismiss_pending=False
        self._photo_view=result['snapshot']
        self._photo_error=''
        self.navigation.page=RESULT
        self._show()
        if not self._photo_view.get('ticket_dismissed'):
            self._photo_submit('prepare_ticket')

    def _photo_action(self, title, callback, **kwargs):
        if title == 'PEMBAYARAN BELUM TERHUBUNG':
            if self._sandbox_transport:
                title = 'CHECKOUT SANDBOX BELUM DIAKTIFKAN'
            else:
                title, callback = 'LANJUT CHECKOUT SIMULASI', self._freeze_checkout
                kwargs['disabled'] = False
        return super()._photo_action(title, callback, **kwargs)

    def _freeze_checkout(self):
        view = self._photo_view
        self._photo_submit('freeze_checkout', view.get('revision'), view.get('amount'))

    def _simulate_verified_paid(self):
        """Explicit in-process test provider ONLY; no Midtrans API request."""
        if (self._synthetic_pay_callback is None
                or self._photo_view.get('phase')!='payment_pending'
                or self._closed or self._suspended or self._photo_jobs.busy):
            return
        payment=self._photo_view.get('payment')
        if not isinstance(payment,dict) or not payment.get('attempts'):
            return
        self._synthetic_pay_callback(payment)
        self._photo_submit('check_payment','connectivity')

    def _sandbox_photo_outcome(self, outcome):
        if self._pilot_admission is not None and outcome.action=='retire':
            self.navigation.page=ADVERT
            self._reset_visit()
            self._show()
            return True
        if (self._private_pending_event is not None
                or self._photo_jobs.service._hidden.is_set()):
            # A result timeout hides pixels immediately, even with a live
            # worker. Its late delivery reply must not reopen A over Ads/B.
            return super()._sandbox_photo_outcome(outcome)
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

    def _ticket_current(self, offer, *, visible_ack=False):
        service = self._photo_jobs.service
        return (not self._closed and not self._suspended and not service._hidden.is_set()
                and self.navigation.page == RESULT
                and self._photo_view.get('phase') in TICKET_PHASES
                and (visible_ack or not self._ticket_dismiss_pending)
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
        if self._closed or self._suspended:
            return
        if self._poll_paid_result_timeout():
            return
        super()._poll_photos()
        if self._closed or self._suspended:
            return
        # QR lifetime belongs to the visible UI, not the serialized printer
        # worker. A slow receipt send must not freeze the countdown or leave
        # the original private code onscreen after its 30-second deadline.
        # Only the later durable dismissal waits for the original send to end.
        if self._photo_view.get('phase') == 'ticket_visible':
            self._update_ticket_countdown()
            if (self._ticket_window is not None and self._ticket_window.active
                    and self._ticket_window.remaining() == 0):
                self._ticket_next(user=False)
        if self._photo_jobs.busy:
            return
        if self._claim_pending is not None:
            offer, self._claim_pending = self._claim_pending, None
            if self._claim_current(offer):
                self._photo_submit('ccp_visible', offer)
        elif self._ticket_pending is not None:
            offer, self._ticket_pending = self._ticket_pending, None
            if self._ticket_current(offer, visible_ack=True):
                self._photo_submit('ticket_visible', offer)
        elif (self._photo_view.get('phase') in {'payment_pending', 'payment_hold'}
                and time.monotonic() >= self._payment_check_at):
            self._payment_check_at = time.monotonic()+10
            self._photo_submit('check_payment')
        if self._photo_view.get('phase') == 'ticket_visible':
            # Direct PhotoJobs submit (not _photo_submit) keeps NEXT usable
            # during the slow physical send, while maintaining single-flight.
            if self._ticket_receipt_pending and not self._photo_jobs.busy:
                if self._photo_jobs.submit('ticket_send_receipt'):
                    self._ticket_receipt_pending = False
            elif (self._ticket_dismiss_pending and
                  not self._ticket_receipt_pending and not self._photo_jobs.busy):
                if self._photo_jobs.submit('ticket_dismiss'):
                    self._ticket_dismiss_pending = False
        elif (self.navigation.page == RESULT
                and self._photo_view.get('phase') == 'paid_delivery'
                and not self._photo_jobs.busy and not self._photo_error
                and self._private_pending_event is None
                and not self._photo_jobs.service._hidden.is_set()):
            delivery = self._photo_view.get('delivery') or {}
            # Only PREPARED original jobs advance. The serialized service
            # rechecks PAID, URL, ticket, ownership and the durable print lane;
            # SENDING/UNCERTAIN holds every remaining design without replay.
            if (not delivery.get('needs_operator_review')
                    and 'PREPARED' in (delivery.get('print_states') or {}).values()):
                self._photo_submit('paid_print_next')

    def _poll_paid_result_timeout(self):
        if (self._paid_result_deadline is None
                or self.navigation.page != RESULT
                or self._photo_view.get('phase') != 'paid_delivery'):
            return False
        remaining = max(0, math.ceil(self._paid_result_deadline - time.monotonic()))
        if self._paid_result_countdown is not None:
            self._paid_result_countdown.text = (
                f'Kembali ke halaman utama dalam {remaining} detik.\n'
                'Pesanan tetap tersimpan.')
        if remaining:
            return False
        # Reuse privacy retirement and the existing separate PREPARE/ACK
        # admission gate. This event never cancels/refunds/discharges PAID.
        self._queue_private_retirement('RESULT_TIMEOUT')
        return True

    def _build_ticket_page(self, canvas):
        self._live_image = None
        self._camera_texture = None
        self._last_live_frame = self._last_preview = None
        shell = self._frame(canvas, brand_height=65)
        self._brand(shell, 'TIKET PEMULIHAN',
            'SANDBOX • SIMPAN QR SEBELUM LANJUT' if self._sandbox_transport else
            'SIMULASI • SIMPAN QR SEBELUM LANJUT')
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
        if self._paid_result_deadline is None:
            self._paid_result_deadline = time.monotonic() + 30
        # A synthetic Drive QR exercises rendering but is NOT a real download link.
        # Keep the actual opt-in test Drive route distinct and visible to the owner.
        subtitle = ('SANDBOX • STATUS LAYANAN' if self._sandbox_transport else
                    'QR DEMO • BUKAN LINK DOWNLOAD' if self._synthetic_drive_url
                    else 'DRIVE TEST • BAYAR SIMULASI')
        self._brand(shell, 'HASIL FOTO BERBAYAR', subtitle)
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
        # A transport timeout may still mean paper left the printer. Do not
        # offer another paid batch until the original physical outcome is
        # classified by the approved recovery/operator path.
        if ('PREPARED' in states.values() and not data.get('needs_operator_review')):
            shell.add_widget(text_label(
                'Foto dicetak otomatis sesuai jumlah yang dibeli.',
                size=13, height=45, color=MUTED))
        shell.add_widget(self._photo_action(
            'CEK STATUS UPLOAD',lambda: self._photo_submit('paid_delivery_status'),
            variant='secondary'))
        self._paid_result_countdown = text_label('', size=12,height=48,color=MUTED)
        shell.add_widget(self._paid_result_countdown)
        self._paid_result_countdown.text = (
            f'Kembali ke halaman utama dalam {max(0, math.ceil(self._paid_result_deadline - time.monotonic()))} detik.\n'
            'Pesanan tetap tersimpan.')
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
        self._brand(shell, 'CHECKOUT PRIVAT', 'MIDTRANS SANDBOX • UJI PEMBAYARAN' if
                    self._sandbox_transport else 'SIMULASI • BUKAN PEMBAYARAN QRIS')
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
            shell.add_widget(self._photo_action('SUDAH SIMPAN BUKTI • LANJUT QRIS' if
                self._sandbox_transport else 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI',
                lambda: self._photo_submit('begin_payment'), disabled=phase != 'checkout_ready'))
        elif phase == 'paid_hold':
            shell.add_widget(text_label('PEMBAYARAN SANDBOX TERVERIFIKASI' if self._sandbox_transport
                else 'PEMBAYARAN SIMULASI TERVERIFIKASI', size=20, height=100, color=GOLD))
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
            shell.add_widget(text_label('MENUNGGU PEMBAYARAN SANDBOX' if self._sandbox_transport
                else 'MENUNGGU PEMBAYARAN SIMULASI', size=19, height=65, color=GOLD))
            if phase == 'payment_pending' and self._sandbox_transport:
                qr = view.get('payment_qr')
                if qr is not None:
                    shell.add_widget(Image(texture=image_texture(qr),fit_mode='contain',
                                           size_hint_y=None,height=dp(240)))
                else:
                    shell.add_widget(text_label('QR pesanan asli belum tersedia. Periksa status.',
                                               size=17,height=120,color=MUTED))
            elif phase == 'payment_pending':
                # This service accepts only mock authority. Its white fixture
                # image is not a payment QR; do not present a blank scanner target.
                card = PixelCard(orientation='vertical', padding=dp(16), spacing=dp(8))
                card.add_widget(text_label('SIMULASI PEMBAYARAN • TANPA TRANSFER',
                                           size=20, height=90, color=GOLD))
                card.add_widget(text_label(
                    'QRIS asli belum terhubung. Tidak perlu scan atau transfer uang.',
                    size=17, height=95, color=MUTED))
                card.add_widget(text_label(
                    'Gunakan SIMULASI PAID di bawah untuk melanjutkan uji.'
                    if self._synthetic_pay_callback is not None else
                    'Status diperiksa melalui penyedia simulasi.',
                    size=15, height=85, color=MUTED))
                shell.add_widget(card)
            else:
                shell.add_widget(text_label('Status belum pasti. Pesanan asli tetap dilindungi.',
                                           size=18, height=120, color=MUTED))
            shell.add_widget(self._photo_action('PERIKSA STATUS',
                lambda: self._photo_submit('check_payment', 'connectivity'), variant='secondary'))
            attempts = payment.get('attempts') or []
            if phase == 'payment_hold' and (
                    not payment or payment.get('state') == 'NOT_CREATED'
                    or payment.get('state') == 'UNKNOWN' and attempts
                    and attempts[-1].get('create_phase') == 'PREPARED'):
                # An initial readiness/HTTP hold may precede provider I/O.
                # Explicit original-owner action reuses backend begin: only
                # PREPARED can send; SENT/UNKNOWN reconcile without a new POST.
                # Status polling itself must never create a payment attempt.
                shell.add_widget(self._photo_action('COBA LAGI CHECKOUT ASLI',
                    lambda: self._photo_submit('begin_payment')))
            if phase == 'payment_pending' and self._synthetic_pay_callback is not None:
                shell.add_widget(self._photo_action(
                    'SIMULASI PAID • TANPA TRANSFER',
                    self._simulate_verified_paid, variant='secondary'))
            if payment.get('state') == 'EXPIRED_UNPAID':
                if len(payment.get('attempts') or []) < 3:
                    shell.add_widget(self._photo_action('LANJUTKAN PESANAN ASLI',
                        lambda: self._photo_submit('continue_payment', True)))
                else:
                    shell.add_widget(text_label(
                        'Batas 3 QR tercapai. Tidak ada QRIS baru. '
                        'Pesanan asli tetap tercatat untuk pemeriksaan.',
                        size=14,height=74,color=GOLD))
        shell.add_widget(self._photo_action('BATAL • LINDUNGI SESI',
                                            lambda: self._photo_submit('abort'), variant='tertiary'))
        self._photo_message = text_label(self._photo_error, size=13, height=62, color=GOLD)
        shell.add_widget(self._photo_message)


class PrivateCheckoutFixtureApp(_CheckoutAppBase):
    """Original explicit mock-only application; no Sandbox guard is relaxed."""
    def _validate_checkout_service(self, service):
        if not isinstance(service, PrivateCheckoutService):
            raise TypeError('Explicit incomplete mock checkout service required')
