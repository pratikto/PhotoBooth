"""QRIS payment panel inside the existing branded Kivy kiosk shell."""
import time
from PIL import Image
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from photobooth.ui_brand import BLUE, GREY, WHITE, Panel


class QrisPaymentPage:
    def __init__(self, ui, snapshot, *, retry, cancel, edit):
        self.ui, self.edit = ui, edit
        page = ui._reset('payment', 'Bayar, lalu berfoto.')
        self.mode = snapshot['context']['mode']
        stage = FloatLayout()
        ui._add_advertisement(stage, 'payment')
        ads = Panel(fill=WHITE, orientation='vertical', padding=dp(12), spacing=dp(6))
        ads.add_widget(ui._label('MEONG PARTNERS', 10, 18, bold=True, color=BLUE))
        ads.add_widget(stage)
        ads.add_widget(ui._label('Pembayaran terverifikasi -> sesi foto otomatis', 12, 30,
                                 align='center', color=GREY))
        detail = Panel(fill=WHITE, orientation='vertical', padding=dp(12), spacing=dp(6))
        label = 'MOCK / BUKAN UNTUK TRANSFER' if self.mode == 'mock' else 'MIDTRANS SANDBOX / UJI COBA'
        detail.add_widget(ui._label(label, 11, 24, bold=True, color=BLUE, align='center'))
        detail.add_widget(ui._label('Rp ' + f"{snapshot['amount']:,}".replace(',', '.'),
                                   27, 40, bold=True, align='center'))
        self.qr = ui._display(Image.new('RGB', (320, 320), 'white'), crisp=True)
        detail.add_widget(self.qr)
        self.status = ui._label('Menyiapkan pembayaran...', 13, 50, bold=True, align='center')
        detail.add_widget(self.status)
        self.reference = ui._label('', 10, 22, color=GREY, align='center')
        detail.add_widget(self.reference)
        detail.add_widget(ui._label('Status diperiksa otomatis. Jangan bayar QR lama.', 10, 28,
                                   color=GREY, align='center'))
        self.error = ui._label('', 11, 42, color=GREY, align='center')
        detail.add_widget(self.error)
        page.add_widget(ui._responsive_row(ads, detail, 360, 480))
        self.cancel = ui._button('BATAL / UBAH PESANAN', cancel, secondary=True)
        self.retry = ui._button('PERIKSA ULANG', retry)
        page.add_widget(ui._actions(self.cancel, self.retry))
        # Existing camera readiness callbacks may update this compatibility
        # button; this page refreshes its own enabled state on the next tick.
        ui.payment_confirm = self.retry
        ui._payment_submitted = False
        self.last_phase = None
        self.update(snapshot, False, '')

    def image(self, image):
        self.ui._display(image, self.qr, crisp=True)

    def update(self, snapshot, busy, message):
        phase, order = snapshot['phase'], snapshot.get('order') or {}
        messages = {'CREATING': 'Membuat order yang aman...', 'WAITING': 'Menunggu pembayaran',
                    'RESERVED': 'Pembayaran terverifikasi. Menyiapkan kamera...',
                    'STARTING': 'Menyimpan izin sesi foto...', 'STARTED': 'Sesi foto siap',
                    'COMPLETING': 'Menyelesaikan catatan transaksi...',
                    'COMPLETED': 'Sesi selesai', 'CANCELLING': 'Memastikan pembatalan...',
                    'CANCELLED': 'Pembayaran berakhir. Pesanan boleh diubah.',
                    'RECOVERY': 'Pemulihan operator diperlukan. Jangan bayar ulang.'}
        text = messages.get(phase, 'Memeriksa pembayaran...')
        if phase == 'WAITING' and order.get('expires_at'):
            remaining = max(0, int(order['expires_at'] - time.time()))
            text += f'\n{remaining // 60:02d}:{remaining % 60:02d}'
        self.status.text = text
        self.reference.text = 'Order: ' + order.get('order_id', snapshot['checkout_key'])[:24]
        self.error.text = message
        self.qr.opacity = 1 if phase == 'WAITING' else .15
        self.retry.disabled = busy or phase in {'STARTED', 'COMPLETED', 'RECOVERY'}
        self.cancel.disabled = busy or phase not in {'WAITING', 'CANCELLED'}
        self.cancel.text = 'UBAH PESANAN' if phase == 'CANCELLED' else 'BATAL / UBAH PESANAN'
        self.last_phase = phase
