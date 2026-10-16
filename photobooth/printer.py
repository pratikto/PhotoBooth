"""Thermal-printer transport for the booth's final photo compositions.

The app tries configured raw ESC/POS TCP routes in order: wired LAN, Wi-Fi,
then USB. It falls back to the next route only if opening a TCP connection
fails before any print bytes have been sent. If sending starts and then fails,
the job status is uncertain and is reported without an automatic retry because
the printer may already have received part of the job.
"""

from __future__ import annotations

import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping


@dataclass(frozen=True)
class PrinterConfig:
    """Runtime settings for the booth's LAN, Wi-Fi, and USB printer routes.

    LAN and Wi-Fi hosts are IP addresses assigned to their respective printer
    network interfaces. Empty hosts disable that route. The app never needs the
    Wi-Fi SSID or password to print; those credentials belong in the printer's
    own network configuration.
    """

    lan_host: str = ""
    lan_port: int = 9100
    wifi_host: str = ""
    wifi_port: int = 9100
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
        legacy_wifi_timeout = _read_float(
            values, "PHOTOBOOTH_PRINTER_WIFI_TIMEOUT", 2.0, 0.1, 30.0
        )
        return cls(
            lan_host=values.get("PHOTOBOOTH_PRINTER_LAN_HOST", "").strip(),
            lan_port=_read_int(
                values, "PHOTOBOOTH_PRINTER_LAN_PORT", 9100, 1, 65535
            ),
            wifi_host=values.get("PHOTOBOOTH_PRINTER_WIFI_HOST", "").strip(),
            wifi_port=_read_int(
                values, "PHOTOBOOTH_PRINTER_WIFI_PORT", 9100, 1, 65535
            ),
            network_timeout=_read_float(
                values,
                "PHOTOBOOTH_PRINTER_NETWORK_TIMEOUT",
                legacy_wifi_timeout,
                0.1,
                30.0,
            ),
            usb_vendor_id=_read_hex_id(
                values.get("PHOTOBOOTH_PRINTER_USB_VENDOR_ID")
            ),
            usb_product_id=_read_hex_id(
                values.get("PHOTOBOOTH_PRINTER_USB_PRODUCT_ID")
            ),
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
        if self.success:
            return self.message
        return f"Gagal mencetak: {self.message}"


class NetworkConnectionError(OSError):
    """The TCP connection failed before any print data could be sent."""


class NetworkSendError(OSError):
    """A TCP write failed after a connection opened; job completion is unknown."""


class ThermalPrinter:
    """Render an image and send it through LAN, Wi-Fi, then USB.

    Empty network hosts are skipped. A network connection failure can safely
    try the next route because no print bytes have been sent. Once a connection
    opens and a write fails, the result is uncertain, so the app avoids
    automatic retries that could create duplicate or partial receipts.

    Optional callables make route order testable without hardware. Production
    defaults build a raster job with python-escpos and use a raw TCP socket or
    python-escpos USB/file transports.
    """

    def __init__(
        self,
        config: PrinterConfig | None = None,
        *,
        payload_builder: Callable[[Path], bytes] | None = None,
        network_sender: Callable[[str, int, bytes], None] | None = None,
        usb_sender: Callable[[bytes], None] | None = None,
    ) -> None:
        self.config = config or PrinterConfig.from_environment()
        self._payload_builder = payload_builder or self._build_payload
        self._network_sender = network_sender or self._send_network
        self._usb_sender = usb_sender or self._send_usb

    def print_image(self, image_path: str | Path) -> PrintResult:
        """Try configured LAN, then Wi-Fi, then USB for one saved composition."""
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

        routes = (
            ("LAN", self.config.lan_host, self.config.lan_port),
            ("Wi-Fi", self.config.wifi_host, self.config.wifi_port),
        )
        connection_errors: list[tuple[str, str, int, NetworkConnectionError]] = []

        for transport, host, port in routes:
            if not host:
                continue

            try:
                self._network_sender(host, port, payload)
            except NetworkConnectionError as error:
                # No print bytes were sent, so trying the next route is safe.
                connection_errors.append((transport, host, port, error))
                continue
            except NetworkSendError as error:
                # A partial write can produce a partial receipt. Do not send
                # the same job again on another interface without user action.
                return PrintResult(
                    False,
                    transport,
                    f"Koneksi {transport} terbuka tetapi pengiriman terputus; "
                    "status cetak tidak pasti "
                    f"({error}). Tekan CETAK ULANG jika kertas tidak keluar.",
                )
            except Exception as error:
                # Unknown network errors are also treated as uncertain because
                # the code cannot prove that the printer received zero bytes.
                return PrintResult(
                    False,
                    transport,
                    f"Pengiriman melalui {transport} gagal; status cetak tidak "
                    f"pasti ({error}). Tekan CETAK ULANG jika kertas tidak keluar.",
                )

            message = f"Data cetakan terkirim via {transport}."
            if connection_errors:
                failed_routes = ", ".join(
                    route_transport
                    for route_transport, _, _, _ in connection_errors
                )
                message = f"{failed_routes} gagal; {message}"
            return PrintResult(
                True,
                transport,
                message,
                fell_back=bool(connection_errors),
            )

        try:
            self._usb_sender(payload)
        except Exception as error:
            if connection_errors:
                failed_routes = "; ".join(
                    f"{transport} {host}:{port} ({network_error})"
                    for transport, host, port, network_error in connection_errors
                )
                return PrintResult(
                    False,
                    "USB",
                    f"Koneksi jaringan gagal ({failed_routes}); "
                    f"cadangan USB juga gagal ({error}).",
                )
            return PrintResult(
                False,
                "USB",
                f"Periksa kabel dan pengaturan USB ({error}).",
            )

        if connection_errors:
            failed_transports = ", ".join(
                transport
                for transport, _, _, _ in connection_errors
            )
            message = (
                f"{failed_transports} tidak tersambung; "
                "data cetakan terkirim via USB."
            )
        else:
            message = "Data cetakan terkirim via USB."
        return PrintResult(
            True,
            "USB",
            message,
            fell_back=bool(connection_errors),
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

    def _send_network(self, host: str, port: int, payload: bytes) -> None:
        """Write raw ESC/POS bytes to a configured printer TCP endpoint."""
        try:
            connection = socket.create_connection(
                (host, port),
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
