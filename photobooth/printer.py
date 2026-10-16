"""Thermal-printer transport for the booth's final photo compositions.

Network printing uses raw ESC/POS over TCP, usually port 9100. A failed
connection falls back to USB before any print bytes have been sent. If sending
starts and then fails, the result is deliberately reported as uncertain instead
of retrying over USB, because the printer may already have received part of the
job and a second copy could be produced.
"""

from __future__ import annotations

import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping


@dataclass(frozen=True)
class PrinterConfig:
    """Runtime settings for a network-first ESC/POS printer connection.

    A blank network host disables the network probe. Set the printer's Wi-Fi
    IP address here to make the J-82ULW network interface the primary route.
    """

    network_host: str = ""
    network_port: int = 9100
    network_timeout: float = 2.0
    usb_vendor_id: int | None = None
    usb_product_id: int | None = None
    usb_device_path: str | None = "/dev/usb/lp0"
    print_width_dots: int = 576

    @classmethod
    def from_environment(
        cls, environ: Mapping[str, str] | None = None
    ) -> "PrinterConfig":
        """Read non-secret printer settings without making app startup fragile."""
        values = os.environ if environ is None else environ
        return cls(
            network_host=values.get("PHOTOBOOTH_PRINTER_WIFI_HOST", "").strip(),
            network_port=_read_int(values, "PHOTOBOOTH_PRINTER_WIFI_PORT", 9100, 1, 65535),
            network_timeout=_read_float(
                values, "PHOTOBOOTH_PRINTER_WIFI_TIMEOUT", 2.0, 0.1, 30.0
            ),
            usb_vendor_id=_read_hex_id(values.get("PHOTOBOOTH_PRINTER_USB_VENDOR_ID")),
            usb_product_id=_read_hex_id(values.get("PHOTOBOOTH_PRINTER_USB_PRODUCT_ID")),
            usb_device_path=(
                values.get("PHOTOBOOTH_PRINTER_USB_DEVICE", "/dev/usb/lp0").strip()
                or None
            ),
            print_width_dots=_read_int(
                values, "PHOTOBOOTH_PRINTER_WIDTH_DOTS", 576, 128, 1024
            ),
        )


@dataclass(frozen=True)
class PrintResult:
    """Outcome of sending one saved composition to the configured printer."""

    success: bool
    transport: str
    message: str
    fell_back: bool = False

    @property
    def user_message(self) -> str:
        """Return concise Indonesian status text for the result screen."""
        if self.success and self.fell_back:
            return "Wi-Fi tidak tersambung; data cetakan terkirim via USB."
        if self.success:
            return f"Data cetakan terkirim via {self.transport}."
        return f"Gagal mencetak: {self.message}"


class NetworkConnectionError(OSError):
    """The TCP connection failed before any print data could be sent."""


class NetworkSendError(OSError):
    """A TCP write failed after a connection opened; job completion is unknown."""


class ThermalPrinter:
    """Render one image as ESC/POS and send it over network, then USB.

    The optional callables make transport order testable without printer
    hardware. Production defaults build a raster job with python-escpos and use
    a raw TCP socket or python-escpos USB/file transports to send it.
    """

    def __init__(
        self,
        config: PrinterConfig | None = None,
        *,
        payload_builder: Callable[[Path], bytes] | None = None,
        network_sender: Callable[[bytes], None] | None = None,
        usb_sender: Callable[[bytes], None] | None = None,
    ) -> None:
        self.config = config or PrinterConfig.from_environment()
        self._payload_builder = payload_builder or self._build_payload
        self._network_sender = network_sender or self._send_network
        self._usb_sender = usb_sender or self._send_usb

    def print_image(self, image_path: str | Path) -> PrintResult:
        """Send a saved result over Wi-Fi first, falling back to USB on connect failure."""
        path = Path(image_path)
        if not path.is_file():
            return PrintResult(False, "USB", f"File hasil tidak ditemukan: {path}")

        try:
            payload = self._payload_builder(path)
        except Exception as error:
            return PrintResult(
                False,
                "USB",
                "Tidak dapat menyiapkan data ESC/POS. Pastikan python-escpos "
                f"terpasang dan file PNG dapat dibuka ({error}).",
            )

        network_error: NetworkConnectionError | None = None
        if self.config.network_host:
            try:
                self._network_sender(payload)
                return PrintResult(True, "Wi-Fi", "Data ESC/POS terkirim.")
            except NetworkConnectionError as error:
                # The connection did not open, so no print bytes reached the
                # network printer. Falling back cannot duplicate this job.
                network_error = error
            except NetworkSendError as error:
                # A partial write can leave a partially printed receipt. Do
                # not send the same job again over USB without user action.
                return PrintResult(
                    False,
                    "Wi-Fi",
                    "Koneksi terbuka tetapi pengiriman terputus; status cetak "
                    f"tidak pasti ({error}). Tekan CETAK ULANG jika kertas tidak keluar.",
                )
            except Exception as error:
                return PrintResult(
                    False,
                    "Wi-Fi",
                    f"Pengiriman melalui jaringan gagal ({error}); status cetak tidak pasti.",
                )

        try:
            self._usb_sender(payload)
        except Exception as error:
            if network_error is not None:
                return PrintResult(
                    False,
                    "USB",
                    f"Wi-Fi tidak tersambung ke {self.config.network_host}:"
                    f"{self.config.network_port} ({network_error}); "
                    f"cadangan USB juga gagal ({error}).",
                )
            return PrintResult(False, "USB", f"Periksa kabel dan pengaturan USB ({error}).")

        return PrintResult(
            True,
            "USB",
            "Data ESC/POS terkirim.",
            fell_back=network_error is not None,
        )

    def _build_payload(self, image_path: Path) -> bytes:
        """Convert the 80 mm composition to the configured monochrome dot width."""
        try:
            from escpos.printer import Dummy
        except ImportError as error:
            raise RuntimeError(
                "python-escpos belum terpasang. Jalankan "
                "python -m pip install -r requirements.txt."
            ) from error

        from PIL import Image

        with Image.open(image_path) as source:
            bitmap = source.convert("RGB")

        if bitmap.width > self.config.print_width_dots:
            height = max(
                1,
                round(bitmap.height * self.config.print_width_dots / bitmap.width),
            )
            resampling = getattr(Image, "Resampling", Image)
            bitmap = bitmap.resize(
                (self.config.print_width_dots, height),
                resampling.LANCZOS,
            )

        # The J-82ULW supports 58 mm and 80 mm thermal rolls. Its 80 mm print
        # width is commonly 576 dots (about 72 mm printable area); retain the
        # 640 px master ratio while fitting the print head. python-escpos
        # converts photos to monochrome raster and adds the cutter command.
        job = Dummy()
        job.image(bitmap, impl="bitImageRaster", fragment_height=960)
        job.cut()
        return job.output

    def _send_network(self, payload: bytes) -> None:
        """Write raw ESC/POS bytes to a printer listening on TCP port 9100."""
        try:
            connection = socket.create_connection(
                (self.config.network_host, self.config.network_port),
                timeout=self.config.network_timeout,
            )
        except OSError as error:
            raise NetworkConnectionError(str(error)) from error

        try:
            connection.settimeout(self.config.network_timeout)
            connection.sendall(payload)
        except OSError as error:
            raise NetworkSendError(str(error)) from error
        finally:
            connection.close()

    def _send_usb(self, payload: bytes) -> None:
        """Send through native USB IDs, or Linux's /dev/usb/lp* device node."""
        try:
            from escpos.printer import File, Usb
        except ImportError as error:
            raise RuntimeError(
                "python-escpos[usb] belum terpasang. Jalankan "
                "python -m pip install -r requirements.txt."
            ) from error

        vendor_id = self.config.usb_vendor_id
        product_id = self.config.usb_product_id
        if (vendor_id is None) != (product_id is None):
            raise ValueError(
                "Isi kedua PHOTOBOOTH_PRINTER_USB_VENDOR_ID dan "
                "PHOTOBOOTH_PRINTER_USB_PRODUCT_ID."
            )

        if vendor_id is not None and product_id is not None:
            printer = Usb(vendor_id, product_id)
        else:
            device_path = self.config.usb_device_path
            if not device_path or not Path(device_path).exists():
                raise FileNotFoundError(
                    f"Perangkat {device_path or '/dev/usb/lp0'} tidak ditemukan. "
                    "Isi VID/PID USB printer atau sambungkan perangkat."
                )
            printer = File(devfile=device_path)

        try:
            printer._raw(payload)
        finally:
            # Release a claimed USB interface or close the device node even if
            # the printer reports an error while accepting the job.
            close = getattr(printer, "close", None)
            if close is not None:
                close()


def _read_int(
    environ: Mapping[str, str], name: str, default: int, minimum: int, maximum: int
) -> int:
    """Parse bounded decimal settings, falling back instead of breaking startup."""
    try:
        value = int(environ.get(name, str(default)).strip())
    except (TypeError, ValueError):
        return default
    return value if minimum <= value <= maximum else default


def _read_float(
    environ: Mapping[str, str], name: str, default: float, minimum: float, maximum: float
) -> float:
    """Parse bounded timeout settings, falling back instead of breaking startup."""
    try:
        value = float(environ.get(name, str(default)).strip())
    except (TypeError, ValueError):
        return default
    return value if minimum <= value <= maximum else default


def _read_hex_id(value: str | None) -> int | None:
    """Parse USB IDs as hexadecimal, matching the format printed by lsusb."""
    if not value or not value.strip():
        return None
    normalized = value.strip().lower()
    if normalized.startswith("0x"):
        normalized = normalized[2:]
    try:
        return int(normalized, 16)
    except ValueError:
        return None
