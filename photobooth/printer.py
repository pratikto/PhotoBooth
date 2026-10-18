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


# Keep the names stable because operators select these values through an
# environment variable and the comparison helper prints them as labels.
DITHER_MODES = ("floyd-steinberg", "bayer", "threshold")
DEFAULT_DITHER_MODE = "floyd-steinberg"
DEFAULT_THRESHOLD = 128

# The 8 x 8 Bayer matrix distributes threshold values across the full range.
# A recursive definition avoids copying a long, error-prone table of numbers.
_BAYER_2X2 = ((0, 2), (3, 1))


def _build_bayer_matrix(size: int = 8) -> tuple[tuple[int, ...], ...]:
    """Build a standard power-of-two Bayer threshold matrix."""
    matrix = [[0]]
    while len(matrix) < size:
        current_size = len(matrix)
        next_matrix = [[0] * (current_size * 2) for _ in range(current_size * 2)]
        for y in range(current_size):
            for x in range(current_size):
                value = matrix[y][x] * 4
                next_matrix[y][x] = value + _BAYER_2X2[0][0]
                next_matrix[y][x + current_size] = value + _BAYER_2X2[0][1]
                next_matrix[y + current_size][x] = value + _BAYER_2X2[1][0]
                next_matrix[y + current_size][x + current_size] = value + _BAYER_2X2[1][1]
        matrix = next_matrix
    return tuple(tuple(row) for row in matrix)


_BAYER_8X8 = _build_bayer_matrix()


def _normalize_dither_mode(mode: str | None) -> str | None:
    """Normalize supported mode names and familiar aliases."""
    if mode is None:
        return None
    normalized = mode.strip().lower().replace("_", "-").replace(" ", "-")
    aliases = {
        "floyd": "floyd-steinberg",
        "fs": "floyd-steinberg",
        "floydsteinberg": "floyd-steinberg",
        "floyd-steinberg": "floyd-steinberg",
        "bayer": "bayer",
        "ordered": "bayer",
        "ordered-bayer": "bayer",
        "threshold": "threshold",
        "simple-threshold": "threshold",
    }
    return aliases.get(normalized)


def dither_image(image, mode: str, threshold: int = DEFAULT_THRESHOLD):
    """Convert an image to a one-bit thermal raster using the selected method.

    The function accepts any Pillow image mode and always returns mode ``1``.
    Floyd–Steinberg uses Pillow's native error-diffusion implementation;
    Bayer applies a deterministic 8 x 8 ordered screen; threshold performs a
    direct global luminance comparison. Resizing must happen before this step
    so each output pixel maps to one physical printer dot.
    """
    from PIL import Image

    normalized_mode = _normalize_dither_mode(mode)
    if normalized_mode is None:
        allowed_modes = ", ".join(DITHER_MODES)
        raise ValueError(f"Mode dithering harus salah satu dari: {allowed_modes}.")
    if not 0 <= threshold <= 255:
        raise ValueError("Nilai threshold harus berada di antara 0 dan 255.")

    grayscale = image.convert("L")
    if normalized_mode == "floyd-steinberg":
        # Pillow's one-bit Floyd–Steinberg conversion diffuses quantization
        # error to neighboring pixels to preserve perceived gray tones.
        dither = getattr(Image, "Dither", Image).FLOYDSTEINBERG
        return grayscale.convert("1", dither=dither)

    width, height = grayscale.size
    if hasattr(grayscale, "get_flattened_data"):
        source_pixels = list(grayscale.get_flattened_data())
    else:
        # Pillow versions before get_flattened_data expose flat pixels via
        # getdata; retain that fallback for older supported installations.
        source_pixels = list(grayscale.getdata())
    output_pixels: list[int] = []

    if normalized_mode == "threshold":
        # Keep the comparison explicit: pixels darker than the chosen cutoff
        # become black, while pixels at or above it remain white.
        output_pixels = [0 if value < threshold else 255 for value in source_pixels]
    else:
        # Each Bayer cell receives a threshold between 0 and 255. Comparing
        # luminance against a repeated matrix approximates gray with a stable
        # spatial dot pattern instead of diffusing error between pixels.
        matrix_size = len(_BAYER_8X8)
        for y in range(height):
            row_offset = y * width
            matrix_row = _BAYER_8X8[y % matrix_size]
            for x in range(width):
                matrix_value = matrix_row[x % matrix_size]
                cell_threshold = int((matrix_value + 0.5) * 256 / (matrix_size**2))
                output_pixels.append(
                    0 if source_pixels[row_offset + x] < cell_threshold else 255
                )

    result = Image.new("1", (width, height), color=255)
    result.putdata(output_pixels)
    return result


def _add_binary_header(image, label: str):
    """Add a crisp one-bit label above a comparison print's image raster."""
    from PIL import Image, ImageDraw, ImageFont

    try:
        # Larger default bitmap text is supported by current Pillow releases.
        font = ImageFont.load_default(size=18)
    except TypeError:
        # Older Pillow versions expose the default font without a size option.
        font = ImageFont.load_default()

    measurement = ImageDraw.Draw(Image.new("1", (1, 1), color=255))
    bounds = measurement.textbbox((0, 0), label, font=font)
    text_height = max(1, bounds[3] - bounds[1])
    header_height = max(32, text_height + 16)
    header = Image.new("1", (image.width, header_height), color=255)
    draw = ImageDraw.Draw(header)
    draw.text(
        (8, (header_height - text_height) // 2 - bounds[1]),
        label,
        fill=0,
        font=font,
    )

    result = Image.new("1", (image.width, image.height + header_height), color=255)
    result.paste(header, (0, 0))
    result.paste(image, (0, header_height))
    return result


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
    windows_printer_name: str = ""
    usb_vendor_id: int | None = None
    usb_product_id: int | None = None
    usb_device_path: str | None = "/dev/usb/lp0"
    print_width_dots: int = 576
    dither_mode: str = DEFAULT_DITHER_MODE
    dither_threshold: int = DEFAULT_THRESHOLD

    def __post_init__(self) -> None:
        """Normalize direct constructor values so bad modes do not break startup."""
        normalized_mode = _normalize_dither_mode(self.dither_mode)
        object.__setattr__(
            self,
            "dither_mode",
            normalized_mode or DEFAULT_DITHER_MODE,
        )
        if not 0 <= self.dither_threshold <= 255:
            object.__setattr__(self, "dither_threshold", DEFAULT_THRESHOLD)

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
            windows_printer_name=values.get("PHOTOBOOTH_PRINTER_WINDOWS_NAME", "").strip(),
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
            dither_mode=(
                _normalize_dither_mode(
                    values.get("PHOTOBOOTH_PRINTER_DITHER", DEFAULT_DITHER_MODE)
                )
                or DEFAULT_DITHER_MODE
            ),
            dither_threshold=_read_int(
                values,
                "PHOTOBOOTH_PRINTER_THRESHOLD",
                DEFAULT_THRESHOLD,
                0,
                255,
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
        self._payload_builder = payload_builder
        self._network_sender = network_sender or self._send_network
        self._usb_sender = usb_sender or self._send_usb

    def print_image(
        self,
        image_path: str | Path,
        *,
        dither_mode: str | None = None,
        header_label: str | None = None,
        copies: int = 1,
    ) -> PrintResult:
        """Submit an entire identical-copy order as ONE ESC/POS transport job.

        ``dither_mode`` can override the configured mode for a single test
        print. ``header_label`` adds a crisp identifier above test rasters.

        Previously FEAT-001 called print_image repeatedly, creating a separate
        Windows RAW spool document for each requested sheet. The spooler can
        acknowledge those jobs before the physical POS printer finishes, so
        device output may not match the number of accepted jobs. Rendering the
        exact same payload once and repeating its image+cut byte sequence in a
        *single* spool document avoids per-copy job-boundary races and saves
        redundant photo dithering. The single send still cannot prove that
        every physical sheet emerged: on partial write, do not retry blindly.
        """
        if isinstance(copies, bool) or not isinstance(copies, int) or copies < 1:
            return PrintResult(False, "printer", "Jumlah lembar cetak tidak valid.")
        path = Path(image_path)
        if not path.is_file():
            return PrintResult(False, "USB", f"File hasil tidak ditemukan: {path}")

        try:
            if self._payload_builder is not None and dither_mode is None and not header_label:
                # Retain the one-argument injection point used by transport
                # tests; production mode overrides use the full renderer.
                payload = self._payload_builder(path)
            else:
                payload = self._build_payload(
                    path,
                    dither_mode=dither_mode,
                    header_label=header_label,
                )
        except Exception as error:
            return PrintResult(
                False,
                "USB",
                "Tidak dapat menyiapkan data ESC/POS. Pastikan python-escpos "
                f"terpasang dan file PNG dapat dibuka ({error}).",
            )

        # The base stream already includes ESC/POS image bytes followed by
        # one physical cut. Repeating the *complete* stream produces N strips
        # with N independent cuts in a single RAW spool/transport submission.
        # Use one immutable payload rather than N separate print_image calls.
        if copies > 1:
            payload = payload * copies

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

    def print_comparison(self, image_path: str | Path) -> tuple[PrintResult, ...]:
        """Print one saved image with every supported method, in a fixed order.

        The same source file is used for all three outputs. Printing stops on
        the first failed result so an uncertain partial job is never followed
        by more comparison prints automatically.
        """
        results: list[PrintResult] = []
        for mode in DITHER_MODES:
            label = f"DITHER TEST: {mode.upper()}"
            result = self.print_image(
                image_path,
                dither_mode=mode,
                header_label=label,
            )
            results.append(result)
            if not result.success:
                break
        return tuple(results)

    def _build_payload(
        self,
        image_path: Path,
        *,
        dither_mode: str | None = None,
        header_label: str | None = None,
    ) -> bytes:
        """Render one image as a native-width, one-bit ESC/POS raster."""
        try:
            from escpos.printer import Dummy
        except ImportError as error:
            raise RuntimeError(
                "python-escpos belum terpasang. Jalankan "
                "python -m pip install -r requirements.txt."
            ) from error

        from PIL import Image

        with Image.open(image_path) as source:
            # A transparent PNG should reveal white thermal paper underneath,
            # not turn transparent pixels into accidental black areas.
            rgba = source.convert("RGBA")
            white_background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            bitmap = Image.alpha_composite(white_background, rgba).convert("L")

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

        selected_mode = _normalize_dither_mode(dither_mode or self.config.dither_mode)
        if selected_mode is None:
            raise ValueError(f"Mode dithering tidak dikenal: {dither_mode}.")
        # Resize in grayscale before converting to one bit. Once pixels have
        # been dithered, scaling would blur physical dots and create artifacts.
        # Explicit owner choice: use the calibrated Floyd photo profile by
        # default, exactly as exported by the three-way tuning laboratory.
        # Comparison prints with a dither_mode override remain untouched.
        # Setting PHOTOBOOTH_PHOTO_TUNING=legacy restores the prior behavior,
        # without changing printer settings or the payment QR pipeline.
        if (
            dither_mode is None
            and selected_mode == "floyd-steinberg"
            and os.environ.get("PHOTOBOOTH_PHOTO_TUNING", "owner-floyd").lower() != "legacy"
        ):
            from photobooth.dither_lab import DitherProfile, render_thermal_image

            # An 80 mm profile was calibrated at 576 dots. For a deliberately
            # narrower 384-dot printhead, preserve the tuning factors and use
            # its physical width; other non-lab widths stay on legacy behavior.
            if self.config.print_width_dots in (384, 576):
                profile = DitherProfile(
                    mode="floyd-steinberg",
                    width_dots=self.config.print_width_dots,
                    brightness=0.652,
                    contrast=2.104,
                    gamma=2.352,
                    sharpness=2.073,
                    threshold=128,
                )
                thermal_bitmap = render_thermal_image(bitmap, profile)
            else:
                thermal_bitmap = dither_image(
                    bitmap, selected_mode, threshold=self.config.dither_threshold
                )
        else:
            thermal_bitmap = dither_image(
                bitmap, selected_mode, threshold=self.config.dither_threshold
            )
        if header_label:
            thermal_bitmap = _add_binary_header(thermal_bitmap, header_label)

        # The J-82ULW supports 58 mm and 80 mm thermal rolls. Its 80 mm print
        # width is commonly 576 dots (about 72 mm printable area); retain the
        # 640 px master ratio while fitting the print head. The bitmap is
        # already one bit so python-escpos does not choose a second halftone.
        job = Dummy()
        job.image(thermal_bitmap, impl="bitImageRaster", fragment_height=960)
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

    @staticmethod
    def _send_windows_raw(name: str, payload: bytes) -> None:
        """Submit a RAW ESC/POS job via an installed Windows printer queue.

        The job reaching the spooler is not proof of physical paper output.
        A partial write has uncertain printing status: do not auto-retry.
        """
        try:
            import win32print
        except ImportError as error:
            raise RuntimeError(
                "pywin32 belum terpasang. Jalankan python -m pip install pywin32."
            ) from error
        handle = win32print.OpenPrinter(name)
        try:
            win32print.StartDocPrinter(handle, 1, ("Meong Photobooth ESC/POS", None, "RAW"))
            try:
                win32print.StartPagePrinter(handle)
                try:
                    written = win32print.WritePrinter(handle, payload)
                    if written != len(payload):
                        raise OSError(
                            f"Windows spooler menerima {written}/{len(payload)} bytes."
                        )
                finally:
                    win32print.EndPagePrinter(handle)
            finally:
                # A RAW spool document MUST be finalized with EndDocPrinter.
                # Closing the handle instead left the job unfinished and
                # doubled ClosePrinter, so Windows could report accepted bytes
                # without reliably releasing the queued physical print.
                win32print.EndDocPrinter(handle)
        finally:
            # Close the opened handle exactly once, including when StartDoc
            # or a write raises. Never automatically retry a partial send.
            win32print.ClosePrinter(handle)

    def _send_usb(self, payload: bytes) -> None:
        """Send through native USB IDs, or Linux's /dev/usb/lp* device node."""
        # Use the already-installed Windows POS80ENG/USB001 driver when
        # explicitly configured. No WinUSB driver replacement is necessary.
        if os.name == "nt" and self.config.windows_printer_name:
            self._send_windows_raw(self.config.windows_printer_name, payload)
            return
        if os.name == "nt" and not self.config.windows_printer_name:
            raise RuntimeError(
                "USB Windows belum dikonfigurasi. Buka Settings > "
                "PENGATURAN PRINTER, pilih USB Windows, isi nama antrean "
                "printer (misalnya POS80 Printer), lalu tekan SIMPAN. "
                "Jangan gunakan /dev/usb/lp0 di Windows."
            )
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
