"""Generate the transaction-folder QR with the approved full Meong logo.

Only the destination text is encoded into the QR. The PNG logo is a small
visual insert, not part of the URL, so the same bundled artwork can be reused
for every transaction without a network request. A logo hides some data dots;
high error correction and unobstructed recognition patterns are essential.
"""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
import qrcode
from qrcode.util import pattern_position


# Resolve the asset relative to this module, not the current working directory.
# Launching main.py from a shortcut or a different folder must still find it.
LOGO_PATH = Path(__file__).resolve().parent / "assets" / "meong_photobooth.png"
QUIET_ZONE_MODULES = 4
DEFAULT_BOX_SIZE = 8


@lru_cache(maxsize=1)
def _load_logo() -> Image.Image:
    """Read the local full-logo asset once, detached from its open file handle."""
    with Image.open(LOGO_PATH) as source:
        # Flatten future transparent assets onto white too. Transparent black
        # pixels must not become a black rectangle when a printer converts RGB.
        artwork = source.convert("RGBA")
        paper = Image.new("RGBA", artwork.size, "white")
        return Image.alpha_composite(paper, artwork).convert("RGB")


def _recognition_patterns(version: int, modules: int) -> Image.Image:
    """Mark grid cells that a logo must never cover, including their guards.

    Longer Drive URLs can require a QR with an alignment marker at its exact
    center. Blindly pasting a logo there can remove that marker. The placement
    search below instead finds the nearest free rectangle inside the QR.

    Args:
        version: QR version selected by the encoder, from 1 through 40.
        modules: Number of data-grid cells across the QR, excluding its border.

    Returns:
        A one-bit image with one pixel per QR module. Marked cells are reserved
        for recognition/metadata; unmarked cells may hold the small logo plate.
    """
    reserved = Image.new("1", (modules, modules), 0)
    draw = ImageDraw.Draw(reserved)

    # The three corner finders, separators, and nearby format-information bits.
    draw.rectangle((0, 0, 8, 8), fill=1)
    draw.rectangle((modules - 9, 0, modules - 1, 8), fill=1)
    draw.rectangle((0, modules - 9, 8, modules - 1), fill=1)
    # Timing patterns tell the reader where each row/column of data starts.
    draw.line((6, 0, 6, modules - 1), fill=1)
    draw.line((0, 6, modules - 1, 6), fill=1)

    positions = pattern_position(version)
    for row in positions:
        for column in positions:
            # These three combinations belong to finders, not alignment marks.
            if ((row == 6 and column in (6, modules - 7))
                    or (column == 6 and row == modules - 7)):
                continue
            # An alignment pattern is 5x5. Keep another module on each side so
            # the pasted white plate cannot merge with its outer black ring.
            draw.rectangle((column - 3, row - 3, column + 3, row + 3), fill=1)

    if version >= 7:
        # Higher versions carry additional version information near two corners.
        draw.rectangle((modules - 11, 0, modules - 9, 5), fill=1)
        draw.rectangle((0, modules - 11, 5, modules - 9), fill=1)
    return reserved


def _logo_box(version: int, modules: int, artwork: Image.Image) -> tuple[int, int, int, int]:
    """Choose a small module-aligned logo plate near the center of the QR.

    Bound the plate width to roughly one third of a short code, and at most
    fifteen modules for longer codes. Error correction percentages refer to
    data codewords, not to an arbitrary percentage of image area; keeping the
    plate small is still necessary even with level H.

    Args:
        version: Encoder-selected QR version, used to locate alignment markers.
        modules: QR grid width, excluding the white quiet zone.
        artwork: Full logo, used only to preserve the plate's aspect ratio.

    Returns:
        Pillow-style (left, top, right, bottom) bounds measured in QR modules.
        Right/bottom are exclusive. The outer quiet zone is not in these bounds.

    Raises:
        ValueError: No unobstructed data area can fit even the smallest plate.
    """
    reserved = _recognition_patterns(version, modules)
    # Odd dimensions keep the plate balanced around the center of an odd grid.
    # Bitwise OR with 1 leaves an odd number unchanged and increases an even
    # number by one. This keeps both plate axes aligned to whole grid cells.
    columns = min(15, max(7, int(modules * 0.32) | 1))
    for width in range(columns, 4, -2):
        height = max(5, round(width * artwork.height / artwork.width) | 1)
        # Sort by distance from the center. Multiplying each center coordinate
        # by two avoids fractions when comparing module positions. A free
        # central plate wins; a central marker moves the whole logo slightly.
        candidates = sorted(
            ((2 * left + width - modules) ** 2
             + (2 * top + height - modules) ** 2, top, left)
            for top in range(1, modules - height)
            for left in range(1, modules - width)
        )
        for _, top, left in candidates:
            box = (left, top, left + width, top + height)
            if reserved.crop(box).getbbox() is None:
                return box
    raise ValueError("There is no free data area for the Meong QR logo.")


@lru_cache(maxsize=16)
def _render_qr(content: str, with_logo: bool, max_size: int | None,
               monochrome: bool) -> Image.Image:
    """Cache a few recent destinations so GUI status polls do not re-encode.

    This internal image belongs to the cache. The public helper always returns
    a copy so a caller's resizing/drawing cannot damage later QR displays.
    """
    qr = qrcode.QRCode(
        # A minimum of version 4 gives the full wordmark room on short demo
        # links. Longer real URLs automatically choose the required version.
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
        # Choose an INTEGER number of pixels per module before rendering.
        # Resizing a finished QR to an arbitrary width can blur its data dots.
        if max_size < total_modules:
            raise ValueError("QR size is too small to preserve its modules and white margin.")
        qr.box_size = max_size // total_modules
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    if with_logo:
        artwork = _load_logo()
        left, top, right, bottom = _logo_box(qr.version, qr.modules_count, artwork)
        plate = Image.new("RGB", ((right - left) * qr.box_size,
                                  (bottom - top) * qr.box_size), "white")
        # Resize only the artwork. The QR matrix itself is never smoothed.
        inset = max(1, qr.box_size // 2)
        insert = artwork.copy()
        insert.thumbnail((plate.width - 2 * inset, plate.height - 2 * inset),
                         Image.Resampling.LANCZOS)
        if monochrome:
            # A thermal printer has black dots, not gray/color ink. Dither the
            # logo alone; applying image effects to QR dots would damage them.
            insert = ImageOps.grayscale(insert).convert(
                "1", dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")
        plate.paste(insert, ((plate.width - insert.width) // 2,
                             (plate.height - insert.height) // 2))
        position = ((left + QUIET_ZONE_MODULES) * qr.box_size,
                    (top + QUIET_ZONE_MODULES) * qr.box_size)
        image.paste(plate, position)

    return image


def create_qr_image(content: str, *, with_logo: bool = True,
                    max_size: int | None = None, monochrome: bool = False) -> Image.Image:
    """Return an independent RGB QR image for this transaction's destination.

    Args:
        content: A cached folder URL (or explicit demo text). Empty text fails.
        with_logo: Insert the approved FULL Meong logo, including its name and
            grayscale trail. Set False for the separate payment-demo QR; this
            helper does not modify a payment provider's actual QRIS artwork.
        max_size: Optional pixel bound, including the four-module white margin.
            The returned square may be smaller to keep every module equally
            wide. For example, the saved template footer requests 210 pixels.
        monochrome: Render only the logo as black/white dots for a future
            thermal print path. Normal result images retain the logo colors.

    Returns:
        A detached RGB Pillow image, suitable for Kivy/Tkinter display or for
        pasting directly into the saved photo composition.

    Raises:
        ValueError: Empty content, an invalid pixel bound, or a bound too small
            to contain all QR modules and their mandatory white quiet zone.
        FileNotFoundError: The bundled logo is missing from this installation.
        qrcode.exceptions.DataOverflowError: The payload exceeds QR capacity.

    No network request is made. Existing assigned folder URLs remain usable
    offline, and creating a QR does not change a URL or register a transaction.
    """
    if not isinstance(content, str) or not content.strip():
        raise ValueError("QR code content cannot be empty.")
    if max_size is not None and (isinstance(max_size, bool)
                                or not isinstance(max_size, int) or max_size <= 0):
        raise ValueError("QR size must be a positive integer number of pixels.")
    # Callers may paste, resize, or draw on their image without corrupting the
    # cached source that another result screen/session will receive later.
    return _render_qr(content.strip(), with_logo, max_size, monochrome).copy()
