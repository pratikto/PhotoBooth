"""QR payment slips for a configured LAN ESC/POS thermal printer.

This is intentionally independent of photograph dithering and of the separate
thermal-printer branch. Every QR module occupies an integer number of dots,
with four clear modules on all sides. A preview/ESC-POS spool is kept locally
for diagnostics. With no printer host, the result explicitly says PREVIEW;
it never claims paper was printed. TCP send success means sent, not a sensor
confirmation that the printer physically delivered the slip.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
from queue import Empty, SimpleQueue
import re
import socket
import threading
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont
import qrcode


def render_payment_slip(attempt, width=576):
    """Render an 80 mm-class receipt using native dot dimensions, never dithering."""
    if not 384 <= width <= 832 or width % 8:
        raise ValueError('Printer width must be a multiple of eight dots between 384 and 832.')
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4, box_size=1)
    code.add_data(attempt.payload)
    code.make(fit=True)
    modules = len(code.get_matrix())
    box = min(width - 48, 448) // modules
    if box < 3:
        raise ValueError('QR payload is too dense for the configured paper width.')
    code.box_size = box
    qr = code.make_image(fill_color='black', back_color='white').convert('1')
    canvas = Image.new('1', (width, qr.height + 274), 1)
    draw = ImageDraw.Draw(canvas)
    def line(text, y, size=19):
        try:
            font = ImageFont.truetype('DejaVuSans.ttf', size)
        except OSError:
            font = ImageFont.load_default(size=size)
        draw.text((width / 2, y), text, anchor='mt', font=font, fill=0)
    line('MEONG PHOTOBOOTH', 16, 25)
    line('DEMO - BUKAN UNTUK TRANSFER' if attempt.demo else 'PINDAI UNTUK MEMBAYAR', 53, 17)
    line('Rp ' + f'{attempt.amount:,}'.replace(',', '.'), 86, 29)
    line(attempt.attempt_id, 126, 16)
    canvas.paste(qr, ((width - qr.width) // 2, 155))
    y = 155 + qr.height
    deadline = attempt.expires_at.astimezone(ZoneInfo('Asia/Jakarta')).strftime('%d/%m/%Y %H:%M:%S WIB')
    line('Berlaku sampai ' + deadline, y + 15, 16)
    line('Status: Menunggu pembayaran', y + 44, 17)
    line('Selesaikan pembayaran di booth ini.', y + 72, 16)
    return canvas


def escpos_raster(image):
    """Encode GS v 0 raster bytes: black pixels are one bits on the printer."""
    image = image.convert('1', dither=Image.Dither.NONE)
    width_bytes = (image.width + 7) // 8
    padded = Image.new('1', (width_bytes * 8, image.height), 1)
    padded.paste(image, (0, 0))
    data = bytes(value ^ 255 for value in padded.tobytes())
    return (b'\x1b@\x1d\x76\x30\x00' + width_bytes.to_bytes(2, 'little')
            + image.height.to_bytes(2, 'little') + data + b'\n\n\n\x1dV\x01')


@dataclass(frozen=True)
class PrintResult:
    attempt_id: str
    status: str
    message: str
    preview: Path | None = None


class QrisPrinterWorker:
    """One off-thread job; no automatic retries after a possibly partial send."""

    def __init__(self, directory, host=None, port=None, width=None, printer_config_provider=None):
        self.directory = Path(directory)
        # When provided by the kiosk, use its saved printer settings for QR slips.
        # Legacy standalone LAN settings remain supported for existing callers.
        self.printer_config_provider = printer_config_provider
        self.host = os.environ.get('PHOTOBOOTH_PRINTER_HOST', '') if host is None else host
        self._configuration_error = None
        try:
            self.port = int(port if port is not None else os.environ.get('PHOTOBOOTH_PRINTER_PORT', '9100'))
            self.width = int(width if width is not None else os.environ.get('PHOTOBOOTH_PRINTER_DOTS', '576'))
            if not 1 <= self.port <= 65535 or not 384 <= self.width <= 832 or self.width % 8:
                raise ValueError('Invalid printer port or native dot width.')
        except (ValueError, TypeError) as error:
            # An operator typo must disable this optional output, not checkout.
            self._configuration_error = str(error)
        self._lock = threading.Lock()
        self._busy = False
        self._closed = False
        self._cancelled = set()
        self._results = SimpleQueue()

    @property
    def busy(self):
        with self._lock:
            return self._busy

    def submit(self, attempt):
        """The UI validates status first; snapshot and recheck expiry before sending."""
        with self._lock:
            if self._busy or self._closed:
                return False
            self._busy = True
        threading.Thread(target=self._run, args=(attempt.snapshot(),),
                         name='photobooth-qris-printer', daemon=True).start()
        return True

    def cancel(self, attempt_id):
        with self._lock:
            self._cancelled.add(attempt_id)

    def _allowed(self, attempt):
        with self._lock:
            return (not self._closed and attempt.attempt_id not in self._cancelled
                    and attempt.state == 'pending' and attempt.remaining() > 0)

    def _run(self, attempt):
        preview = None
        sending = False
        try:
            if self._configuration_error:
                raise ValueError('Pengaturan printer tidak valid: ' + self._configuration_error)
            if not self._allowed(attempt):
                raise ValueError('Kode tidak aktif. Periksa status pembayaran dahulu.')
            self.directory.mkdir(parents=True, exist_ok=True)
            name = re.sub(r'[^A-Za-z0-9_-]', '_', attempt.attempt_id)
            preview = self.directory / f'{name}.png'
            config = self.printer_config_provider() if self.printer_config_provider else None
            slip = render_payment_slip(attempt, config.print_width_dots if config else self.width)
            payload = escpos_raster(slip)
            slip.save(preview)
            (self.directory / f'{name}.bin').write_bytes(payload)
            if not self._allowed(attempt):
                raise ValueError('Pencetakan dibatalkan karena status pembayaran berubah.')
            if config is not None:
                # Reuse the very same network/Windows USB transport as the
                # successfully printed photograph strip. No LAN-only fallback.
                from photobooth.printer import ThermalPrinter
                printer = ThermalPrinter(config)
                if config.lan_host:
                    sender = lambda: printer._send_network(config.lan_host, config.lan_port, payload)
                elif config.wifi_host:
                    sender = lambda: printer._send_network(config.wifi_host, config.wifi_port, payload)
                elif config.windows_printer_name or config.usb_vendor_id is not None:
                    sender = lambda: printer._send_usb(payload)
                else:
                    sender = None
                if sender is None:
                    result = PrintResult(attempt.attempt_id, 'preview',
                                         'Pratinjau siap. Pilih printer di Settings.', preview)
                else:
                    if not self._allowed(attempt):
                        raise ValueError('Pencetakan dibatalkan karena status pembayaran berubah.')
                    sending = True
                    sender()
                    result = PrintResult(attempt.attempt_id, 'sent',
                                         'QR dikirim ke printer. Ambil kertas, lalu pindai.', preview)
            elif not self.host:
                result = PrintResult(attempt.attempt_id, 'preview',
                                     'Pratinjau siap. Printer LAN belum dikonfigurasi.', preview)
            else:
                with socket.create_connection((self.host, self.port), timeout=4) as printer:
                    printer.settimeout(4)
                    if not self._allowed(attempt):
                        raise ValueError('Pencetakan dibatalkan karena status pembayaran berubah.')
                    sending = True
                    printer.sendall(payload)
                result = PrintResult(attempt.attempt_id, 'sent',
                                     'QR dikirim ke printer. Ambil kertas, lalu pindai.', preview)
        except Exception as error:
            result = PrintResult(attempt.attempt_id, 'unknown' if sending else 'error',
                                 ('Pengiriman terputus. Periksa kertas sebelum mencetak ulang.'
                                  if sending else f'QR belum dicetak: {error}'),
                                 preview if preview and preview.is_file() else None)
        finally:
            with self._lock:
                if self._closed:
                    self._busy = False
                else:
                    # Retain the submission lock until the UI has consumed the
                    # result. A very fast printer must not reopen a race window
                    # between two queued releases of the same print button.
                    self._results.put(result)

    def poll(self):
        try:
            result = self._results.get_nowait()
            with self._lock:
                self._busy = False
            return result
        except Empty:
            return None

    def close(self):
        """Invalidate pending work; a TCP buffer already sent cannot be recalled."""
        with self._lock:
            self._closed = True
