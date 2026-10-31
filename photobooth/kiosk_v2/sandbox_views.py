"""Native v2 presentation; QRIS client and durable admission are reused unchanged."""
import time

from kivy.core.clipboard import Clipboard
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput

from photobooth.advertising import PROJECT_ROOT
from .flow import ADVERT, TEMPLATES, PHOTO_CONFIRM, SANDBOX_CHECKOUT
from .photo_views import image_texture
from .theme import PixelCard, text_label, GOLD, CYAN, MUTED
from .sandbox_checkout import SandboxJobs, configured_sandbox, sandbox_enabled, simulator_qr_url


class SandboxViews:
    def _init_sandbox(self):
        self._sandbox_enabled = sandbox_enabled()
        self._sandbox_jobs = (self._provided_sandbox_jobs or SandboxJobs(lambda:configured_sandbox(PROJECT_ROOT))) if self._sandbox_enabled else None
        self._sandbox_view = None
        self._sandbox_error = ''
        self._sandbox_link_feedback = None
        self._sandbox_refresh_at = 0
        self._sandbox_consent = False
        self._sandbox_privacy_epoch = 0
        self._sandbox_action_epoch = 0
        self._sandbox_claim_input = None
        self._sandbox_claim_controls = []
        self._sandbox_pending_issue = None
        self._sandbox_operator_mode = False
        self._sandbox_operator_input = None
        self._sandbox_isolation = None
        self._sandbox_legacy_confirm = False
        self._sandbox_isolation_epoch = 0
        self._sandbox_qr_idle_key=None
        self._sandbox_qr_idle_deadline=0

    def _sandbox_submit(self, action, *args):
        if self._closed or self._suspended or not self._sandbox_jobs:
            return False
        if self._sandbox_jobs.submit(action, self._view_revision, *args):
            self._sandbox_action_epoch = self._sandbox_privacy_epoch
            self._sandbox_error = ''
            self._sync_sandbox_claim_controls()
            return True
        return False

    def _sync_sandbox_claim_controls(self):
        busy=bool(self._closed or self._suspended or not self._sandbox_jobs or self._sandbox_jobs.busy)
        for button in self._sandbox_claim_controls:
            button.disabled=busy

    def _sandbox_lock_customer(self):
        jobs=self._sandbox_jobs
        if jobs and jobs.store and jobs.store.flow.qr_renewal_enabled and not jobs.store.flow.active:
            jobs.store.flow.invalidate_qr_renewal(retire=True)
        if not self._sandbox_enabled or not jobs or not jobs.store or not jobs.store.flow.active:
            return
        self._sandbox_privacy_epoch += 1
        jobs.store.flow.lock_customer()
        jobs.store.qr=jobs.store.qr_identity=None
        jobs.store.ticket_qr=jobs.store.ticket_identity=None
        if self._photo_jobs and self._photo_jobs.service:
            self._photo_jobs.service.hide_private()
        if self._sandbox_claim_input:
            self._sandbox_claim_input.text=''
        if self._sandbox_operator_input:
            self._sandbox_operator_input.text=''
        self._sandbox_operator_input=None
        self._sandbox_operator_mode=False
        self._sandbox_isolation=None
        self._sandbox_legacy_confirm=False
        self._sandbox_claim_input=None
        self._cancel_countdown()
        self._sandbox_consent=False
        self._photo_view={}
        self._last_live_frame=self._last_preview=self._camera_texture=None
        self._sandbox_view={'phase':'RECOVERY','customer_claim_required':True}
        self.navigation.page=SANDBOX_CHECKOUT
        self._show()

    def _sandbox_operator_open(self):
        if self._sandbox_jobs.busy or not self._sandbox_jobs.store:
            return
        self._sandbox_lock_customer()
        self._sandbox_operator_mode=True
        self._show()

    def _sandbox_operator_close(self):
        self._sandbox_lock_customer()

    def _sandbox_operator_inspect(self):
        field=self._sandbox_operator_input
        if field is None or self._sandbox_jobs.busy:
            return
        pin=field.text;field.text=''
        self._sandbox_submit('operator_inspect',pin)
        self._show()

    def _sandbox_operator_release(self):
        if (not self._sandbox_operator_mode or self._sandbox_jobs.busy
                or (self._photo_jobs and self._photo_jobs.busy) or not self._sandbox_operator_input):
            return
        order=(self._sandbox_view or {}).get('order') or {}
        legacy=(order.get('mode')=='sandbox' and order.get('state')=='PAID'
                and order.get('customer_capability_bound') is False)
        if legacy and not self._sandbox_isolation and not self._sandbox_legacy_confirm:
            self._sandbox_operator_input.text=''
            self._sandbox_legacy_confirm=True
            self._sandbox_error='Konfirmasi arsip uji lama. Foto tetap terkunci; hak dan data tidak dihapus.'
            self._show()
            return
        pin=self._sandbox_operator_input.text;self._sandbox_operator_input.text=''
        if self._sandbox_isolation:
            receipt=self._sandbox_isolation;self._sandbox_isolation=None
            self._sandbox_submit('acknowledge_release',pin,receipt)
        else:
            self._sandbox_submit('prepare_legacy_release' if legacy else 'prepare_release',pin)
        self._show()

    def _sandbox_cancel_legacy_release(self):
        if self._sandbox_jobs.busy or self._sandbox_isolation:
            return
        if self._sandbox_operator_input:
            self._sandbox_operator_input.text=''
        self._sandbox_legacy_confirm=False
        self._sandbox_error='Pengarsipan belum dilakukan. Sesi lama tetap disimpan.'
        self._show()

    def _sandbox_open_saved(self):
        if (not self._sandbox_enabled or not self._sandbox_jobs.store or self._sandbox_jobs.busy
                or self._sandbox_jobs.store.flow.active or (self._photo_jobs and self._photo_jobs.busy)):
            return
        if self._photo_jobs and self._photo_jobs.service and self._photo_jobs.service.transaction:
            if self._photo_jobs.service.phase!='done':
                return
            self._photo_jobs.submit('reset')
        self._sandbox_operator_mode=False;self._sandbox_consent=False
        self._photo_view={}
        self._sandbox_view={'phase':'CLAIM_LOOKUP','customer_claim_required':True}
        self.navigation.page=SANDBOX_CHECKOUT
        self._show()

    def _sandbox_report_issue(self, reason):
        jobs=self._sandbox_jobs
        if not self._sandbox_enabled or not jobs or not jobs.store:
            return False
        order=(jobs.store.flow.snapshot() or {}).get('order') or {}
        if (order.get('fulfillment') or {}).get('obligation_state')!='OWED':
            return False
        self._sandbox_lock_customer()
        self._sandbox_pending_issue=reason
        if self._sandbox_submit('fulfillment_issue',reason):
            self._sandbox_pending_issue=None
        return True

    def _sandbox_claim(self):
        field=self._sandbox_claim_input
        if field is None or self._sandbox_jobs.busy:
            return
        ticket=field.text
        field.text=''
        self._sandbox_submit('customer_claim',ticket)
        self._show()

    def _sandbox_scan_claim(self):
        if self._sandbox_jobs.busy:
            return
        frame=self.camera_device.read()
        if frame is None:
            self._sandbox_error='Kamera belum siap. Gunakan isi tiket atau bantuan operator.'
        else:
            self._sandbox_submit('scan_claim',frame.copy())
        self._show()

    def _sandbox_resume(self):
        if (self._sandbox_view or {}).get('resume_ready') and not self._sandbox_jobs.busy:
            self._sandbox_submit('resume')
            self._show()

    def _open_sandbox(self):
        if not self._sandbox_enabled or self.navigation.page != TEMPLATES or not any(self.quantities.values()):
            return
        self._sandbox_consent = False
        self.navigation.page = SANDBOX_CHECKOUT
        # Show the undiscounted server price and request explicit confirmation.
        # No order is created by opening this page, even following a local win.
        self._sandbox_view = {'phase':'QUOTE'}
        self._show()

    def _sandbox_begin(self):
        if self._sandbox_view and self._sandbox_view['phase'] == 'QUOTE':
            frame=self.camera_device.read()
            valid=(frame is not None and getattr(frame,'ndim',0)==3
                   and frame.shape[2]==3 and frame.size>0)
            self._sandbox_submit('begin_ready', dict(self.quantities),bool(valid),time.monotonic())
            self._show()

    def _sandbox_retry(self):
        self._sandbox_submit('boot' if not self._sandbox_view else 'check')
        if not ((self._sandbox_view or {}).get('customer_claim_required') and self._sandbox_claim_input):
            self._show()

    def _sandbox_ticket_saved(self):
        if (self._sandbox_view or {}).get('ticket_required'):
            self._sandbox_submit('ticket_saved')
            self._show()

    def _sandbox_renew_qr(self, automatic=False):
        view=self._sandbox_view or {}
        if (view.get('phase')!='CANCELLED' or not view.get('qr_expiry_verified')
                or self._sandbox_jobs.busy or self._closed or self._suspended):
            return
        self._sandbox_qr_idle_key=None;self._sandbox_qr_idle_deadline=0
        self._sandbox_submit('verify_renewal',view['checkout_key'],bool(automatic))
        self._show()

    def _sandbox_renew_ready(self, automatic):
        view=self._sandbox_view or {}
        frame=self.camera_device.read()
        valid=(frame is not None and getattr(frame,'ndim',0)==3 and frame.shape[2]==3 and frame.size>0)
        self._sandbox_submit('renew_ready',view['checkout_key'],bool(automatic),bool(valid),time.monotonic())
        self._show()

    def _sandbox_cancel(self):
        self._sandbox_submit('cancel')
        self._show()

    def _sandbox_copy_link(self):
        if (self._closed or self._suspended or not self._sandbox_enabled
                or self.navigation.page != SANDBOX_CHECKOUT or self._sandbox_jobs.busy):
            return
        url = simulator_qr_url(self._sandbox_view)
        if not url:
            return
        try:
            Clipboard.copy(url)
            message = 'Link QRIS tersalin. Paste di simulator Midtrans.'
        except Exception:
            message = 'Gagal menyalin. Coba lagi atau gunakan link di terminal.'
        self._sandbox_link_feedback = (url, message)
        self._show()

    def _sandbox_leave(self):
        if self._sandbox_jobs.busy:
            return
        phase = (self._sandbox_view or {}).get('phase')
        if phase not in {'IDLE','QUOTE','CANCELLED','COMPLETED','SUSPENDED','CLAIM_LOOKUP'}:
            return
        if phase=='CLAIM_LOOKUP' and self._sandbox_jobs.store.flow.active:
            return
        self._sandbox_view = None
        self.navigation.page = TEMPLATES if phase == 'QUOTE' else PHOTO_CONFIRM
        if phase == 'QUOTE':
            self._show()
        else:
            self._return_ad()

    def _sandbox_photo_consent(self):
        if (self._sandbox_jobs.busy or (self._sandbox_view or {}).get('phase') != 'RESERVED'
                or (self._sandbox_view or {}).get('ticket_required')
                or (self._sandbox_view or {}).get('customer_claim_required')):
            return
        cart = self._sandbox_view['quantities']
        self.quantities = {t.template_id:cart.get(t.template_id,0) for t in self.templates}
        self.navigation.page = TEMPLATES
        self.navigation.tutorial_seen = True
        self._sandbox_consent = True
        self._enter_photo_test()

    def _sandbox_prepare_photo(self):
        if self._sandbox_jobs.busy or not self._sandbox_consent:
            return
        self._sandbox_submit('prepare')
        self.navigation.page = SANDBOX_CHECKOUT
        self._show()

    def _sandbox_photo_outcome(self, outcome):
        """Called before photo navigation. No server ACK means no camera countdown."""
        if self._sandbox_enabled and outcome.action=='isolate':
            self._photo_view={}
            if (self._sandbox_operator_mode and self._sandbox_isolation_epoch==self._sandbox_privacy_epoch):
                if outcome.error:
                    self._sandbox_error='Isolasi belum terbukti. Periksa pekerjaan perangkat; booth tetap ditahan.'
                else:
                    self._sandbox_isolation=outcome.value['isolation']
                    self._sandbox_error='Sesi lokal sudah diisolasi. Masukkan PIN lagi untuk konfirmasi pelepasan.'
                self._show()
            return True
        if self._sandbox_enabled and outcome.error:
            reason=('CAPTURE_FAILED' if outcome.action=='capture' else
                    'COMPOSITION_FAILED' if outcome.action=='compose' else 'PHOTO_STATE_UNAVAILABLE')
            if self._sandbox_report_issue(reason):
                return True
        if (self._sandbox_enabled and self._sandbox_jobs.store and
                self._sandbox_jobs.store.flow.customer_claim_required):
            if self._photo_jobs and self._photo_jobs.service:
                self._photo_jobs.service.hide_private()
            self._photo_view={}
            return True
        if self._sandbox_enabled and outcome.action in {'restore','restore_allocated'}:
            self.navigation.page=SANDBOX_CHECKOUT
            if outcome.error:
                self._photo_view={}
                self._sandbox_error='Foto asli belum dapat dipulihkan. Pesanan tetap tersimpan; hubungi operator.'
                self._sandbox_consent=False
            else:
                self._sandbox_submit('resumed',outcome.value['transaction_id'],outcome.value['phase'])
            self._show()
            return True
        if not self._sandbox_enabled or not self._sandbox_consent:
            return False
        if outcome.action in {'start', 'start_bound'}:
            self.navigation.page = SANDBOX_CHECKOUT
            tx = (outcome.value or {}).get('transaction_id')
            self._sandbox_submit('recover' if outcome.error or not tx else 'started', *([] if outcome.error or not tx else [tx]))
            self._show()
            return True
        if (outcome.value or {}).get('phase') == 'done':
            self.navigation.page = SANDBOX_CHECKOUT
            self._sandbox_submit('complete' if outcome.action == 'next' and not outcome.error else 'recover')
            self._show()
            return True
        return False

    def _sandbox_can_capture(self):
        return (not self._sandbox_enabled or
                (self._sandbox_consent and (self._sandbox_view or {}).get('phase') == 'STARTED'
                 and not self._sandbox_jobs.store.flow.customer_claim_required
                 and (self._sandbox_view.get('order') or {}).get('service_state') == 'STARTED'
                 and self._sandbox_view.get('transaction_id') == self._photo_view.get('transaction_id')))

    def _poll_sandbox(self):
        if not self._sandbox_jobs or self._closed or self._suspended:
            return
        if self._sandbox_expired_idle_tick():
            return
        outcome = self._sandbox_jobs.poll()
        self._sync_sandbox_claim_controls()
        if outcome is not None:
            if self._sandbox_action_epoch != self._sandbox_privacy_epoch:
                self._sandbox_refresh_at=time.monotonic()+2
                return
            if outcome.error:
                if outcome.action in {'verify_renewal','renew_ready'}:
                    self._sandbox_jobs.store.flow.invalidate_qr_renewal()
                    current=self._sandbox_jobs.store.flow.snapshot() or {}
                    if current.get('checkout_key')!=(self._sandbox_view or {}).get('checkout_key'):
                        self._sandbox_view={'phase':'UNCERTAIN'}
                        self._sandbox_refresh_at=0
                    self._sandbox_error='QR belum dapat diperbarui. Periksa kamera dan koneksi, lalu coba lagi.'
                    self._show()
                    return
                if outcome.action in {'operator_inspect','prepare_release','prepare_legacy_release','acknowledge_release'}:
                    self._sandbox_error='Pemeriksaan ditolak atau provider belum tersedia. Periksa PIN dan koneksi.'
                    self._show()
                    return
                if (outcome.action=='begin_ready' and self._sandbox_jobs.store
                        and not self._sandbox_jobs.store.flow.active):
                    self._sandbox_view={'phase':'QUOTE'}
                    self._sandbox_error='Kamera, penyimpanan atau template belum siap. Periksa perangkat lalu coba lagi.'
                    self._show()
                    return
                if outcome.action in {'customer_claim','scan_claim','resume','resumed'}:
                    self._sandbox_lock_customer()
                elif outcome.action != 'boot':
                    self._sandbox_view = {'phase':'UNCERTAIN'}
                self._sandbox_error = 'Status belum pasti. Cek lagi; jangan membuat pesanan atau membayar ulang.'
            else:
                if outcome.action in {'prepare_release','prepare_legacy_release'}:
                    self._sandbox_view=outcome.value
                    self._ensure_photo_jobs()
                    data=outcome.value;release=data['order']['release']
                    self._sandbox_isolation_epoch=self._sandbox_privacy_epoch
                    self._photo_jobs.submit('isolate',data['order']['order_id'],data.get('transaction_id'),release['generation'])
                    self._show()
                    return
                if outcome.action=='acknowledge_release':
                    self._sandbox_view=outcome.value;self._sandbox_consent=False
                    self._sandbox_operator_mode=False;self._sandbox_isolation=None
                    self._sandbox_legacy_confirm=False
                    self._photo_prepared=True
                    self._sandbox_leave()
                    return
                if outcome.action=='resume':
                    payload=outcome.value
                    self._sandbox_view=payload['view']
                    self._ensure_photo_jobs()
                    self._photo_jobs.submit('restore_allocated',self.templates,payload['quantities'],
                        payload['binding'],payload['permit'],payload['service_state'])
                    self._show()
                    return
                self._sandbox_view = outcome.value
                phase = (outcome.value or {}).get('phase')
                if outcome.action=='operator_inspect' and phase=='CANCELLED':
                    self._sandbox_operator_mode=False;self._sandbox_legacy_confirm=False
                expired=(phase=='CANCELLED' and self._sandbox_view.get('qr_expiry_verified') is True)
                if expired and self._sandbox_view.get('qr_renewal_count',0)>=2:
                    self._sandbox_leave()
                    return
                if (outcome.action == 'boot' and phase in {'IDLE','COMPLETED','CANCELLED','SUSPENDED'}
                        and not expired):
                    self._sandbox_leave()
                    return
                if outcome.action=='verify_renewal' and self._sandbox_view.get('qr_renewal_ready'):
                    self._sandbox_renew_ready(self._sandbox_view.get('renewal_automatic',False))
                    return
                if outcome.action=='renew_ready':
                    self.quantities=dict(self._sandbox_view['quantities'])
                    self._sandbox_link_feedback=None
                if (outcome.action in {'boot','check'} and phase=='CANCELLED' and self._sandbox_view.get('qr_renewal_auto')
                        and self._sandbox_jobs.store.flow.expiry_auto_available
                        and not self._sandbox_operator_mode):
                    self._sandbox_renew_qr(automatic=True)
                    return
                if outcome.action=='resumed':
                    self._sandbox_consent=True
                if outcome.action == 'prepare' and phase == 'STARTING' and self._sandbox_consent:
                    # STARTING journal is durable before one local transaction is allocated.
                    self.navigation.page = PHOTO_CONFIRM
                    order = self._sandbox_view.get('order') or {}
                    allocation = order.get('fulfillment') or {}
                    if allocation.get('allocation_operation_id'):
                        binding = {key: allocation[key] for key in
                            ('fulfillment_id', 'transaction_id', 'allocation_operation_id', 'contract_hash',
                             'booth_id', 'merchant_id')}
                        binding.update(order_id=order['order_id'], grant_id=order['grant_id'])
                        self._photo_submit('start_bound', self.templates, dict(self._sandbox_view['quantities']), binding)
                    else:
                        self._photo_submit('start', self.templates, dict(self._sandbox_view['quantities']))
                    self.navigation.page = SANDBOX_CHECKOUT
                elif phase == 'STARTED' and self._sandbox_consent:
                    self.navigation.page = PHOTO_CONFIRM
                    self.navigation.photo_step(self._photo_view['phase'])
                elif phase == 'COMPLETED':
                    self._sandbox_consent = False
            self._sandbox_refresh_at = time.monotonic()+2
            # Background observations must not destroy a ticket being typed.
            if not (outcome.action=='check' and self._sandbox_claim_input is not None
                    and (self._sandbox_view or {}).get('customer_claim_required')):
                self._show()
        phase = (self._sandbox_view or {}).get('phase')
        if self._sandbox_pending_issue and not self._sandbox_jobs.busy:
            if self._sandbox_submit('fulfillment_issue',self._sandbox_pending_issue):
                self._sandbox_pending_issue=None
            return
        if (self.navigation.page == SANDBOX_CHECKOUT and not self._sandbox_jobs.busy and
                not self._sandbox_operator_mode and
                phase in {'CREATING','WAITING','CANCELLING','STARTING','COMPLETING','RECOVERY','UNCERTAIN','VERIFYING_QR'} and
                not (self._photo_jobs and self._photo_jobs.busy) and
                time.monotonic() >= self._sandbox_refresh_at):
            self._sandbox_refresh_at = time.monotonic()+2
            self._sandbox_submit('check')

    def _sandbox_expired_idle_tick(self):
        view=self._sandbox_view or {};store=self._sandbox_jobs.store if self._sandbox_jobs else None
        current=store.flow.snapshot() if store else None
        eligible=(self.navigation.page==SANDBOX_CHECKOUT and not self._sandbox_operator_mode
                  and view.get('phase')=='CANCELLED' and view.get('qr_expiry_verified') is True
                  and current and current.get('phase')=='CANCELLED' and not store.flow.active
                  and (current.get('order') or {}).get('state')=='EXPIRED'
                  and (current.get('order') or {}).get('service_state')=='NONE'
                  and not (current.get('order') or {}).get('grant_id')
                  and not (current.get('order') or {}).get('fulfillment')
                  and current.get('checkout_key')==view.get('checkout_key'))
        if not eligible:
            self._sandbox_qr_idle_key=None;self._sandbox_qr_idle_deadline=0
            return False
        if self._sandbox_jobs.busy or (self._photo_jobs and self._photo_jobs.busy):
            return False
        if self._sandbox_qr_idle_key!=view['checkout_key']:
            self._sandbox_qr_idle_key=view['checkout_key'];self._sandbox_qr_idle_deadline=time.monotonic()+30
        if time.monotonic()>=self._sandbox_qr_idle_deadline:
            self._sandbox_qr_idle_key=None;self._sandbox_qr_idle_deadline=0
            self._sandbox_leave()
            return True
        return False

    def _build_sandbox_checkout(self, canvas):
        self._sandbox_claim_controls=[]
        view = self._sandbox_view or {}
        if self._sandbox_operator_mode:
            return self._build_sandbox_operator(canvas,view)
        if view.get('ticket_required'):
            return self._build_recovery_ticket(canvas,view)
        if view.get('customer_claim_required') or view.get('resume_ready'):
            return self._build_customer_claim(canvas,view)
        self._sandbox_claim_input=None
        shell = self._frame(canvas, brand_height=48)
        shell.spacing = 8
        self._brand(shell, 'QRIS SANDBOX', 'MODE UJI • GUNAKAN SIMULATOR SANDBOX')
        view = self._sandbox_view or {'phase':'LOADING'}
        phase = view['phase']
        simulator_url = simulator_qr_url(view)
        card = PixelCard(orientation='vertical', padding=12, spacing=6)
        money = lambda n:'Rp'+f'{n:,}'.replace(',','.')
        if phase == 'QUOTE':
            from photobooth.payment_quote import quote_checkout
            amount = quote_checkout({k:v for k,v in self.quantities.items() if v}).total_amount
        else:
            amount = view.get('amount')
        if amount:
            card.add_widget(text_label(money(amount), size=30, height=52, color=GOLD, bold=True))
        titles = {'QUOTE':'KONFIRMASI PESANAN UJI', 'WAITING':'MENUNGGU SIMULATOR',
                  'RESERVED':'PEMBAYARAN UJI TERKONFIRMASI', 'RECOVERY':'PERLU BANTUAN OPERATOR',
                  'COMPLETED':'SESI FOTO SELESAI', 'CANCELLED':'PESANAN UJI DITUTUP',
                  'STARTING':'MENYIAPKAN IZIN FOTO', 'COMPLETING':'MENYELESAIKAN SESI',
                  'CANCELLING':'MEMASTIKAN PEMBATALAN'}
        if view.get('qr_expiry_verified') and phase=='CANCELLED':
            titles['CANCELLED']='QR PEMBAYARAN KEDALUWARSA'
        titles['VERIFYING_QR']='MEMERIKSA STATUS QR'
        card.add_widget(text_label(titles.get(phase,'MEMERIKSA PESANAN UJI'),size=18,height=54,color=CYAN,bold=True))
        qr = view.get('qr_rgb')
        if qr:
            from PIL import Image as PILImage
            image = PILImage.frombytes('RGB', qr[0], qr[1])
            texture = image_texture(image)
            texture.mag_filter = texture.min_filter = 'nearest'
            card.add_widget(Image(texture=texture,fit_mode='contain'))
        else:
            card.add_widget(Widget())
        message = 'Gunakan simulator resmi Midtrans Sandbox.\nJangan memakai aplikasi bank atau dompet asli.'
        if simulator_url:
            message = 'Salin link QRIS, lalu paste di simulator Midtrans.\nJangan memakai aplikasi bank atau dompet asli.'
        if phase == 'QUOTE':
            message = 'Harga uji tanpa promo game.\nPromo DEMO belum berlaku pada QRIS Sandbox.\nPesanan dibuat setelah kamu memilih lanjut.'
        elif phase == 'RECOVERY':
            message = 'Pesanan dan foto tetap disimpan.\nOperator perlu memeriksa status sebelum lanjut.\nTidak ada sesi atau cetak yang diulang otomatis.'
        elif phase == 'RESERVED':
            message = 'Izin satu sesi pesanan tersedia.\nFoto dimulai setelah persetujuan kamu.'
        elif view.get('qr_expiry_verified') and phase=='CANCELLED':
            message = 'Pilihan desain dan jumlah lembar tetap.\nPilih BUAT QR BARU untuk melanjutkan.\nTanpa pilihan, kembali ke iklan dalam 30 detik.'
        elif phase=='VERIFYING_QR':
            message = 'Status pembayaran sedang diperiksa.\nQR pengganti menunggu hasil Midtrans.'
        card.add_widget(text_label(message,size=15,height=110,color=MUTED))
        shell.add_widget(card)
        feedback = self._sandbox_link_feedback
        status = self._sandbox_error or (feedback[1] if feedback and feedback[0] == simulator_url else '')
        if not status and view.get('qr_replaces') and phase=='WAITING':
            status='QR sebelumnya kedaluwarsa. Silakan gunakan QR terbaru.'
        shell.add_widget(text_label(status,size=13,height=60,color=GOLD))
        def action(title,callback,variant='secondary'):
            shell.add_widget(self._action(title,callback,variant=variant,height=48,disabled=self._sandbox_jobs.busy))
        if phase == 'QUOTE':
            action('LANJUT SANDBOX TANPA PROMO',self._sandbox_begin,'primary')
            action('KEMBALI PILIH TEMPLATE',self._sandbox_leave,'tertiary')
        elif phase == 'RESERVED':
            action('LANJUT KE PERSETUJUAN FOTO',self._sandbox_photo_consent,'primary')
        elif phase=='CANCELLED' and view.get('qr_expiry_verified'):
            action('BUAT QR BARU',self._sandbox_renew_qr,'primary')
            action('KEMBALI KE HALAMAN AWAL',self._sandbox_leave,'tertiary')
        elif phase in {'COMPLETED','CANCELLED','IDLE'}:
            action('SELESAI / KEMBALI IKLAN',self._sandbox_leave,'primary')
        elif phase in {'CREATING','WAITING','CANCELLING'}:
            if simulator_url:
                action('SALIN LINK QRIS',self._sandbox_copy_link,'primary')
            action('CEK STATUS',self._sandbox_retry)
            action('BATALKAN PESANAN UJI',self._sandbox_cancel,'tertiary')
        elif phase != 'RECOVERY':
            action('COBA PEMERIKSAAN LAGI',self._sandbox_retry,'tertiary')

    def _build_recovery_ticket(self,canvas,view):
        shell=self._frame(canvas,brand_height=48)
        self._brand(shell,'SIMPAN TIKET PEMULIHAN','PEMBAYARAN TERKONFIRMASI • BUKAN QR PEMBAYARAN')
        card=PixelCard(orientation='vertical',padding=12,spacing=8)
        rgb=view.get('ticket_qr_rgb')
        if rgb:
            from PIL import Image as PILImage
            texture=image_texture(PILImage.frombytes('RGB',rgb[0],rgb[1]))
            texture.mag_filter=texture.min_filter='nearest'
            card.add_widget(Image(texture=texture,fit_mode='contain'))
        message='Pembayaran diterima. Simpan tiket ini di ponsel.\nTiket diperlukan jika sesi foto terputus.\nBerlaku 24 jam untuk uji Sandbox.'
        card.add_widget(text_label(message,size=15,height=120,color=MUTED))
        shell.add_widget(card)
        shell.add_widget(text_label(self._sandbox_error,size=13,height=60,color=GOLD))
        shell.add_widget(self._action('SUDAH SIMPAN • LANJUT',self._sandbox_ticket_saved,
            height=52,disabled=self._sandbox_jobs.busy or not rgb))

    def _build_customer_claim(self,canvas,view):
        shell=self._frame(canvas,brand_height=48)
        ready=view.get('resume_ready')
        self._brand(shell,'SESI TERSIMPAN','BUKTI PEMILIK TERVERIFIKASI' if ready else 'TIKET PELANGGAN DIPERLUKAN')
        card=PixelCard(orientation='vertical',padding=12,spacing=8)
        message=('Tiket sesuai dengan pesanan asli.\nPilih pulihkan untuk memeriksa foto tersimpan.\nKamera tidak memotret otomatis.' if ready else
                 'Pesanan tetap tersimpan.\nFoto tidak ditampilkan tanpa bukti pemilik.\nGunakan tiket pemulihan atau bantuan operator.')
        if (view.get('order') or {}).get('fulfillment_issue'):
            message+='\nLayanan tertunda tercatat. Simpan tiket; hubungi operator.'
        card.add_widget(text_label(message,size=16,height=180,color=MUTED))
        self._sandbox_claim_input=None
        if not ready:
            field=TextInput(multiline=False,password=True,hint_text='Isi tiket pemulihan lengkap',
                size_hint_y=None,height=52,font_size=18)
            self._sandbox_claim_input=field
            card.add_widget(field)
        card.add_widget(Widget())
        shell.add_widget(card)
        shell.add_widget(text_label(self._sandbox_error,size=13,height=76,color=GOLD))
        def action(title,callback,variant='secondary',height=52):
            button=self._action(title,callback,variant=variant,height=height,disabled=self._sandbox_jobs.busy)
            self._sandbox_claim_controls.append(button)
            shell.add_widget(button)
        if ready:
            action('PULIHKAN SESI FOTO ASLI',self._sandbox_resume)
        else:
            action('VERIFIKASI TIKET',self._sandbox_claim)
            action('SCAN QR TIKET DI KAMERA',self._sandbox_scan_claim)
        action('PERIKSA STATUS',self._sandbox_retry)
        action('BANTUAN OPERATOR',self._sandbox_operator_open,variant='tertiary',height=48)
        if view.get('phase')=='CLAIM_LOOKUP':
            action('KEMBALI KE IKLAN',self._sandbox_leave,variant='tertiary',height=48)

    def _build_sandbox_operator(self,canvas,view):
        shell=self._frame(canvas,brand_height=48)
        self._brand(shell,'OPERATOR SANDBOX','PEMERIKSAAN STATUS • BUKAN PENGEMBALIAN DANA')
        card=PixelCard(orientation='vertical',padding=12,spacing=8)
        order=view.get('order') or {}
        legacy=(order.get('mode')=='sandbox' and order.get('state')=='PAID'
                and order.get('customer_capability_bound') is False)
        message=('Uji lama tanpa tiket pemulihan.\nArsip menyimpan pesanan, foto dan kewajiban.\nFoto tetap terkunci; bukan refund atau selesai.\nGunakan PIN launcher terbaru.' if legacy else
                 'Masukkan PIN dari terminal launcher lokal.\nPIN berbeda dari tiket pelanggan.')
        card.add_widget(text_label(message,size=14 if legacy else 16,height=90,color=MUTED))
        field=TextInput(multiline=False,password=True,hint_text='PIN operator 8 digit',
            input_filter='int',size_hint_y=None,height=52,font_size=18)
        self._sandbox_operator_input=field
        card.add_widget(field)
        report=view.get('operator_report')
        if report:
            details='Pembayaran: '+report['payment']+'\nLayanan: '+report['service']
            details+='\nKewajiban: '+str(report['obligation'] or '—')
            details+='\nMasalah: '+str(report['issue'] or '—')
            card.add_widget(text_label(details,size=16,height=112 if legacy else 180,color=CYAN))
        card.add_widget(Widget())
        shell.add_widget(card)
        shell.add_widget(text_label(self._sandbox_error,size=13,height=90,color=GOLD))
        shell.add_widget(self._action('PERIKSA STATUS OPERATOR',self._sandbox_operator_inspect,height=52,disabled=self._sandbox_jobs.busy))
        release_ready=bool(self._sandbox_isolation or legacy or (order.get('state')=='PAID' and order.get('customer_capability_bound')))
        title=('LEPAS BOOTH • HAK TETAP DISIMPAN' if self._sandbox_isolation else
               'KONFIRMASI ISOLASI UJI' if legacy and self._sandbox_legacy_confirm else
               'ARSIPKAN UJI TANPA TIKET' if legacy else 'ISOLASI SESI LAMA')
        shell.add_widget(self._action(title,
            self._sandbox_operator_release,height=52,disabled=self._sandbox_jobs.busy or
            bool(self._photo_jobs and self._photo_jobs.busy) or not release_ready))
        if legacy and self._sandbox_legacy_confirm and not self._sandbox_isolation:
            shell.add_widget(self._action('BATALKAN PENGARSIPAN UJI',self._sandbox_cancel_legacy_release,
                height=48,variant='tertiary',disabled=self._sandbox_jobs.busy))
        shell.add_widget(self._action('KEMBALI KE TIKET PELANGGAN',self._sandbox_operator_close,height=52,
            variant='tertiary',disabled=self._sandbox_jobs.busy))
