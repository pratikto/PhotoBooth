"""Native v2 presentation; QRIS client and durable admission are reused unchanged."""
import time

from kivy.core.clipboard import Clipboard
from kivy.uix.image import Image
from kivy.uix.widget import Widget

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

    def _sandbox_submit(self, action, *args):
        if self._closed or self._suspended or not self._sandbox_jobs:
            return False
        if self._sandbox_jobs.submit(action, self._view_revision, *args):
            self._sandbox_error = ''
            return True
        return False

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
            self._sandbox_submit('begin', dict(self.quantities))
            self._show()

    def _sandbox_retry(self):
        self._sandbox_submit('boot' if not self._sandbox_view else 'check')
        self._show()

    def _sandbox_ticket_saved(self):
        if (self._sandbox_view or {}).get('ticket_required'):
            self._sandbox_submit('ticket_saved')
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
        if phase not in {'IDLE','QUOTE','CANCELLED','COMPLETED'}:
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
                 and self._sandbox_view.get('transaction_id') == self._photo_view.get('transaction_id')))

    def _poll_sandbox(self):
        if not self._sandbox_jobs or self._closed or self._suspended:
            return
        outcome = self._sandbox_jobs.poll()
        if outcome is not None:
            if outcome.error:
                if outcome.action != 'boot':
                    self._sandbox_view = {'phase':'UNCERTAIN'}
                self._sandbox_error = 'Status belum pasti. Cek lagi; jangan membuat pesanan atau membayar ulang.'
            else:
                self._sandbox_view = outcome.value
                phase = (outcome.value or {}).get('phase')
                if outcome.action == 'boot' and phase in {'IDLE','COMPLETED','CANCELLED'}:
                    self._sandbox_leave()
                    return
                if outcome.action == 'prepare' and phase == 'STARTING':
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
            self._show()
        phase = (self._sandbox_view or {}).get('phase')
        if (self.navigation.page == SANDBOX_CHECKOUT and not self._sandbox_jobs.busy and
                phase in {'CREATING','WAITING','CANCELLING','STARTING','COMPLETING','RECOVERY','UNCERTAIN'} and
                not (self._photo_jobs and self._photo_jobs.busy) and
                time.monotonic() >= self._sandbox_refresh_at):
            self._sandbox_refresh_at = time.monotonic()+2
            self._sandbox_submit('check')

    def _build_sandbox_checkout(self, canvas):
        view = self._sandbox_view or {}
        if view.get('ticket_required'):
            return self._build_recovery_ticket(canvas,view)
        if view.get('customer_claim_required'):
            return self._build_customer_claim(canvas,view)
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
        card.add_widget(text_label(message,size=15,height=110,color=MUTED))
        shell.add_widget(card)
        feedback = self._sandbox_link_feedback
        status = self._sandbox_error or (feedback[1] if feedback and feedback[0] == simulator_url else '')
        shell.add_widget(text_label(status,size=13,height=60,color=GOLD))
        def action(title,callback,variant='secondary'):
            shell.add_widget(self._action(title,callback,variant=variant,height=48,disabled=self._sandbox_jobs.busy))
        if phase == 'QUOTE':
            action('LANJUT SANDBOX TANPA PROMO',self._sandbox_begin,'primary')
            action('KEMBALI PILIH TEMPLATE',self._sandbox_leave,'tertiary')
        elif phase == 'RESERVED':
            action('LANJUT KE PERSETUJUAN FOTO',self._sandbox_photo_consent,'primary')
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
        self._brand(shell,'SIMPAN TIKET PEMULIHAN','MODE UJI • BUKAN QR PEMBAYARAN')
        card=PixelCard(orientation='vertical',padding=12,spacing=8)
        rgb=view.get('ticket_qr_rgb')
        if rgb:
            from PIL import Image as PILImage
            texture=image_texture(PILImage.frombytes('RGB',rgb[0],rgb[1]))
            texture.mag_filter=texture.min_filter='nearest'
            card.add_widget(Image(texture=texture,fit_mode='contain'))
        card.add_widget(text_label('Scan atau simpan QR ini di ponsel.\nTiket rahasia ini diperlukan jika sesi terputus.\nBerlaku 24 jam untuk uji Sandbox.',size=15,height=120,color=MUTED))
        shell.add_widget(card)
        shell.add_widget(text_label(self._sandbox_error,size=13,height=60,color=GOLD))
        shell.add_widget(self._action('SUDAH SIMPAN • TAMPILKAN QRIS',self._sandbox_ticket_saved,
            height=52,disabled=self._sandbox_jobs.busy or not rgb))

    def _build_customer_claim(self,canvas,view):
        shell=self._frame(canvas,brand_height=48)
        self._brand(shell,'SESI TERSIMPAN','TIKET PELANGGAN DIPERLUKAN')
        card=PixelCard(orientation='vertical',padding=12,spacing=8)
        card.add_widget(Widget())
        card.add_widget(text_label('Pesanan tetap tersimpan.\nFoto tidak ditampilkan tanpa bukti pemilik.\nGunakan tiket pemulihan atau bantuan operator.',size=16,height=150,color=MUTED))
        shell.add_widget(card)
        shell.add_widget(self._action('PERIKSA STATUS',self._sandbox_retry,height=52,disabled=self._sandbox_jobs.busy))
