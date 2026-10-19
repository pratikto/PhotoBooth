"""Generate a centered, independently checked Meong transaction-folder QR.

The bundled full logo is a visual insert; only the folder URL is encoded.
Each new transaction keeps its own destination, and QR generation stays offline.
The insert covers a few QR cells, so level-H error correction, a small white
plate, an intact outer quiet zone, and independent decoding checks are required.
"""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageOps
from photobooth.branding import LOGO_PATH, load_logo
import qrcode


# Resolve the artwork from the module, so shortcuts and different working
# directories still find the approved full MEONG PHOTOBOOTH logo.
QUIET_ZONE_MODULES = 4
DEFAULT_BOX_SIZE = 8
# The separate Kivy result QR is displayed in a 180px square at normal density.
# A readable full-size source can become unreadable when shown at this size.
SMALL_PREVIEW_SIZE = 180


@lru_cache(maxsize=1)
def _load_logo() -> Image.Image:
    """Read the local logo once and close its original file handle."""
    return load_logo().copy()


def _logo_box(modules: int, artwork: Image.Image) -> tuple[int, int, int, int]:
    """Return an EXACTLY centered, small logo plate in QR-grid coordinates.

    Args:
        modules: QR grid width without its surrounding white quiet zone.
        artwork: The complete approved logo; its aspect ratio is retained.

    Returns:
        (left, top, right, bottom), with exclusive right/bottom bounds.
        All coordinates refer to complete modules, not individual pixels.

    A QR grid has odd dimensions. Odd plate dimensions make both margins equal
    in whole modules. The full plate is centered even when this overlays an
    alignment marker at the center of a longer code. The previous search for a
    marker-free rectangle moved the logo upwards, which was visibly incorrect.
    Recognition/readability is now checked on the final candidate pixels.

    Keep the plate to roughly one third of a short code and at most fifteen
    modules on larger codes. Level-H recovery percentages refer to codewords,
    not to arbitrary image area; they do not justify covering a large logo area.
    """
    columns = min(15, max(7, int(modules * 0.32)))
    if columns % 2 == 0:
        columns += 1
    rows = max(5, round(columns * artwork.height / artwork.width))
    if rows % 2 == 0:
        rows += 1
    left = (modules - columns) // 2
    top = (modules - rows) // 2
    return left, top, left + columns, top + rows


def _paint_qr(qr: qrcode.QRCode, artwork: Image.Image | None,
              monochrome: bool) -> Image.Image:
    """Render one matrix and paste its optional full logo at the final scale.

    The caller has already selected an integer pixel size for each module.
    Only the artwork is resampled; QR data cells and the four-module white
    border never receive smoothing or dithering. Passing no artwork returns
    the separate, plain payment-demo QR without loading any brand asset.
    """
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    # These in-memory encoder facts let pixel-level tests reconstruct the
    # unmodified matrix. They are not displayed or added to the encoded URL.
    image.info["qr_version"] = qr.version
    image.info["qr_mask_pattern"] = qr.mask_pattern
    if artwork is None:
        return image

    left, top, right, bottom = _logo_box(qr.modules_count, artwork)
    plate = Image.new("RGB", ((right - left) * qr.box_size,
                              (bottom - top) * qr.box_size), "white")
    inset = max(1, qr.box_size // 2)
    insert = artwork.copy()
    insert.thumbnail((plate.width - 2 * inset, plate.height - 2 * inset),
                     Image.Resampling.LANCZOS)
    if monochrome:
        # Thermal paper has black dots rather than gray/color ink. Dither the
        # inserted artwork only; keep the surrounding QR matrix binary.
        insert = ImageOps.grayscale(insert).convert(
            "1", dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")
    plate.paste(insert, ((plate.width - insert.width) // 2,
                         (plate.height - insert.height) // 2))
    image.paste(plate, ((left + QUIET_ZONE_MODULES) * qr.box_size,
                       (top + QUIET_ZONE_MODULES) * qr.box_size))
    return image


@lru_cache(maxsize=16)
def _render_qr(content: str, with_logo: bool, max_size: int | None,
               monochrome: bool) -> Image.Image:
    """Encode, render, and check a bounded set of candidates for one URL.

    QR permits eight mask patterns: different valid black/white arrangements
    carrying the same content. The library's automatic choice is tried first.
    A centered logo can make that choice difficult for a reader, so alternate
    masks are tried without moving the logo, changing the URL, or increasing
    the QR version/density. No remote scan service or new dependency is used.
    """
    qr = qrcode.QRCode(
        # Version 4 gives the complete wordmark room on short links. Longer
        # destinations select their required version automatically. This also
        # keeps the bounded center plate clear of corner and timing patterns.
        version=4 if with_logo else None,
        error_correction=(qrcode.constants.ERROR_CORRECT_H if with_logo
                          else qrcode.constants.ERROR_CORRECT_M),
        box_size=DEFAULT_BOX_SIZE,
        border=QUIET_ZONE_MODULES,
    )
    qr.add_data(content)
    qr.make(fit=True)

    total_modules = qr.modules_count + 2 * QUIET_ZONE_MODULES
    if max_size is not None:
        if max_size < total_modules:
            raise ValueError("QR size is too small to preserve its modules and white margin.")
        # Select the dot size BEFORE rendering. Arbitrary resizing of a QR to
        # fit its footer would introduce uneven or blurred data cells.
        qr.box_size = max_size // total_modules

    if not with_logo:
        return _paint_qr(qr, None, monochrome)

    # OpenCV/NumPy are existing camera dependencies. Import them only for the
    # branded path, where an independent reader must check the overlaid result.
    import cv2
    import numpy as np

    detector = cv2.QRCodeDetector()
    artwork = _load_logo()
    for mask in (None, 0, 1, 2, 3, 4, 5, 6, 7):
        if mask is not None:
            qr.mask_pattern = mask
            # Version/data capacity is already established. A mask changes the
            # module arrangement only, leaving the destination and size intact.
            qr.make(fit=False)
        image = _paint_qr(qr, artwork, monochrome)
        decoded, _, _ = detector.detectAndDecode(np.asarray(image))
        if decoded != content:
            continue
        if max_size is None:
            # The unbounded image is the source of the separate GUI QR. Check
            # its nearest-filtered 180px preview too; print-sized requests are
            # instead verified at their actual integer-dot resolution.
            preview = image.resize((SMALL_PREVIEW_SIZE, SMALL_PREVIEW_SIZE),
                                   Image.Resampling.NEAREST)
            decoded, _, _ = detector.detectAndDecode(np.asarray(preview))
            if decoded != content:
                continue
        return image
    raise ValueError("A readable centered Meong QR could not be generated at this size.")


def create_qr_image(content: str, *, with_logo: bool = True,
                    max_size: int | None = None, monochrome: bool = False) -> Image.Image:
    """Return a detached RGB QR image with the full logo exactly at its center.

    Args:
        content: Cached folder URL or explicit demo text. Empty text fails.
        with_logo: Include the complete approved camera-cat, approved trail,
            and MEONG PHOTOBOOTH wordmark. False keeps payment-demo codes plain;
            this helper never edits a payment provider's actual QRIS artwork.
        max_size: Optional pixel bound INCLUDING the four-module white margin.
            The square can be smaller to retain integer module widths. The
            80 mm receipt allocation uses 384px; legacy footers use 210px.
        monochrome: Dither only the logo into black/white thermal dots. The
            standard digital/result-screen QR retains the approved accent colors.

    Returns:
        An independent Pillow RGB image for a GUI or saved photo composition.
        Encoder version/mask metadata is available in its in-memory info dict.

    Raises:
        ValueError: Empty content, an invalid/insufficient pixel bound, or no
            centered candidate that the independent local reader can decode.
        FileNotFoundError: The bundled approved logo is missing.
        qrcode.exceptions.DataOverflowError: Content exceeds QR capacity.

    All work is local, so cached folder URLs keep working while offline. The
    decoder validates pixels without opening the URL. A small recent-result
    cache avoids repeated scans during GUI status polls; returning a copy keeps
    one caller's drawing or resizing from corrupting the cached original.
    Physical printer/phone-camera verification is still a separate device test.
    """
    if not isinstance(content, str) or not content.strip():
        raise ValueError("QR code content cannot be empty.")
    if max_size is not None and (isinstance(max_size, bool)
                                or not isinstance(max_size, int) or max_size <= 0):
        raise ValueError("QR size must be a positive integer number of pixels.")
    return _render_qr(content.strip(), with_logo, max_size, monochrome).copy()
