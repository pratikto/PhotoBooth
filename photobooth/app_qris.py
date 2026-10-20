"""Opt-in QRIS controller that inherits the accepted camera/print/Drive flow.

DEMO is unchanged in app.py. This subclass replaces only payment admission and
service acknowledgement. Paid capture recovery is conservative: an uncertain
partially started session never automatically allocates or prints again.
"""
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import time
from kivy.clock import Clock

from photobooth import app as existing
from photobooth.qris_kiosk_client import QrisKioskClient
from photobooth.qris_session import KioskCheckout
from photobooth.qris_images import payment_qr_image
from photobooth.ui_qris import QrisPaymentPage


class QrisPhotoBoothApp(existing.PhotoBoothApp):
    def __init__(self, checkout=None):
        self.checkout = checkout or self.configured_checkout()
        self.qris_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='qris-kiosk')
        self.qris_future = None
        self.qris_page = None
        self.qris_event = None
        self.qris_next = 0
        self.qris_error = ''
        self.qris_image_order = None
        self.qris_wait_start = False
        self.qris_wait_finish = False
        try:
            super().__init__()
            self.qris_event = Clock.schedule_interval(self._qris_tick, .25)
            if self.checkout.active:
                self._show_qris_payment()
        except BaseException:
            self.qris_pool.shutdown(wait=True, cancel_futures=True)
            self.checkout.close()
            raise

    @staticmethod
    def configured_checkout():
        selected = os.environ.get('MEONG_PAYMENT_MODE', '')
        if selected not in {'qris-mock', 'qris-sandbox'}:
            raise RuntimeError('Explicit qris-mock or qris-sandbox mode required')
        mode = selected.removeprefix('qris-')
        endpoint = os.environ.get('MEONG_QRIS_API_URL', '')
        booth = os.environ.get('MEONG_QRIS_BOOTH_ID', '')
        if booth != existing.BOOTH_ID:
            raise ValueError('Payment booth ID must match PHOTOBOOTH_ID')
        client = QrisKioskClient(endpoint, booth, os.environ.get('MEONG_QRIS_BOOTH_TOKEN', ''),
            allow_local_http=os.environ.get('MEONG_QRIS_LOCAL_PREVIEW') == '1', expected_mode=mode)
        path = Path(os.environ.get('MEONG_QRIS_JOURNAL', str(existing.PROJECT_ROOT / 'data' / f'qris-{mode}-visit.json')))
        return KioskCheckout(path, client, mode=mode, booth_id=booth, endpoint=endpoint)

    def _open_dummy_payment(self, quantities):
        if self.ui.current_screen != 'templates' or self.transaction is not None:
            return
        selected = {key: value for key, value in quantities.items() if value}
        try:
            self.checkout.begin(selected)
        except (ValueError, RuntimeError, OSError):
            self.ui.show_error('Checkout belum siap', 'Periksa pilihan atau pulihkan transaksi sebelumnya. Jangan bayar ulang.')
            return
        self.qris_image_order = None
        self.qris_error = ''
        self._show_qris_payment()
        self.qris_next = 0

    def _show_qris_payment(self):
        self.qris_page = QrisPaymentPage(self.ui, self.checkout.snapshot(),
            retry=self._qris_retry, cancel=self._qris_cancel, edit=self._qris_edit)

    def _qris_retry(self):
        self.qris_next = 0

    def _qris_cancel(self):
        if self.qris_future is not None:
            return
        if self.checkout.snapshot()['phase'] == 'CANCELLED':
            self._qris_edit()
        else:
            self.checkout.request_cancel(); self.qris_next = 0

    def _qris_edit(self):
        if not self.checkout.active:
            super()._open_template_selection(self.checkout.snapshot()['quantities'])

    def _open_template_selection(self, quantities=None):
        if self.checkout.active:
            self._show_qris_payment()
            return
        super()._open_template_selection(quantities)

    def _return_to_advertisements(self):
        if not self.checkout.active:
            super()._return_to_advertisements()

    def _qris_work(self, loaded_image):
        data = self.checkout.refresh()
        image, image_order, image_error = None, None, False
        if data and data['phase'] == 'WAITING' and data['order']:
            order = data['order']
            if order['state'] == 'PENDING' and loaded_image != order['order_id']:
                try:
                    image = payment_qr_image(order)
                    image_order = order['order_id']
                except Exception:
                    # Order was persisted before image I/O. Retrying the image
                    # cannot silently create another payment.
                    image_error = True
        return data, image_order, image, image_error

    def _qris_tick(self, _dt=0):
        if self.is_closing:
            return
        if self.qris_future is not None and self.qris_future.done():
            future, self.qris_future = self.qris_future, None
            try:
                data, oid, image, image_error = future.result()
                self.qris_error = ('QR belum tampil. Order tetap tersimpan; mencoba lagi.' if image_error else '')
                if image is not None and self.ui.current_screen == 'payment' and self.qris_page:
                    self.qris_page.image(image); self.qris_image_order = oid
                self.qris_next = time.monotonic() + 3
            except Exception:
                self.qris_error = 'Koneksi belum terverifikasi. Order yang sama tetap disimpan.'
                self.qris_next = time.monotonic() + 5
        data = self.checkout.snapshot()
        if data is None:
            return
        phase = data['phase']
        if self.qris_future is None:
            if (phase == 'RESERVED' and self.transaction is None and self.camera_ready
                    and self.current_frame is not None and self.ui.current_screen == 'payment'):
                try:
                    self.checkout.prepare_capture()
                    self.qris_wait_start = True
                    if not self._start_transaction(data['quantities']):
                        raise RuntimeError('Capture storage could not be prepared')
                except Exception:
                    self.qris_wait_start = False
                    self.qris_error = 'Izin foto perlu pemulihan operator. Jangan bayar ulang.'
                    try:
                        self.checkout.require_recovery()
                    except OSError:
                        pass  # Journal remains STARTING; restart also fails closed.
                self.qris_next = 0
            elif phase == 'STARTED' and self.qris_wait_start:
                self.qris_wait_start = False
                super()._begin_current_session()
            elif phase == 'COMPLETED':
                if self.qris_wait_finish:
                    self.qris_wait_finish = False
                    super()._finish_transaction()
                elif self.transaction is None and self.ui.current_screen == 'payment':
                    self.ui.show_advertisement(self.camera_ready, self._storage_status_message())
            data = self.checkout.snapshot()
            if (data['phase'] not in {'STARTED', 'COMPLETED', 'CANCELLED', 'RECOVERY'}
                    and time.monotonic() >= self.qris_next):
                self.qris_future = self.qris_pool.submit(self._qris_work, self.qris_image_order)
        if self.ui.current_screen == 'payment' and self.qris_page:
            self.qris_page.update(data, self.qris_future is not None, self.qris_error)

    def _start_transaction(self, quantities):
        # No stale DEMO callback may bypass authoritative QRIS admission.
        state = self.checkout.snapshot()
        if not self.qris_wait_start or not state or state['phase'] != 'STARTING':
            return False
        return super()._start_transaction(quantities)

    def _begin_current_session(self):
        if self.qris_wait_start:
            transaction = self.transaction
            self.checkout.bind_transaction(transaction.transaction_id)
            visit = self.checkout.snapshot()
            transaction.manifest['payment'] = {
                'mode': visit['context']['mode'], 'order_id': visit['order']['order_id'],
                'checkout_key': visit['checkout_key'], 'grant_id': visit['order']['grant_id'],
                'amount': visit['amount'], 'state': 'PAID'}
            self.store._write_manifest(transaction)
            self.qris_next = 0
            return
        super()._begin_current_session()

    def _finish_transaction(self):
        if (self.transaction is None or self.ui.current_screen != 'result' or not self.sessions
                or self.session_index != len(self.sessions) - 1
                or self.current_session is not self.sessions[-1]
                or any(session.output_path is None for session in self.sessions)):
            return
        if self.checkout.snapshot()['phase'] == 'COMPLETED':
            return super()._finish_transaction()
        if self.qris_wait_finish:
            return
        try:
            # A reboot after requesting completion may safely retry the server
            # acknowledgement because the local output manifest is durable.
            self.store.complete_transaction(self.transaction)
            self.checkout.request_complete()
        except (OSError, RuntimeError):
            self.ui.show_error('Transaksi belum selesai', 'Catatan belum tersimpan. Hasil tidak dicetak ulang otomatis.')
            return
        self._cancel_completion_countdown()
        self.qris_wait_finish = True
        self.qris_next = 0
        self.ui.set_status('Hasil tersimpan. Menyelesaikan catatan pembayaran...')

    def _start_print_job(self, image_path, copies=1):
        if self.checkout.context['mode'] == 'mock' and os.environ.get('MEONG_QRIS_MOCK_PRINT') != '1':
            self.ui.set_print_status('MOCK: hasil tersimpan; cetak fisik dinonaktifkan.', busy=False)
            return
        super()._start_print_job(image_path, copies)

    def close(self):
        if getattr(self, 'is_closing', False):
            return
        if self.qris_event is not None:
            self.qris_event.cancel()
        self.qris_pool.shutdown(wait=True, cancel_futures=True)
        self.checkout.close()
        super().close()
