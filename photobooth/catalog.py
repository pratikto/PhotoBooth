"""Approved 80 mm receipt templates and their shared Pillow renderer.

The gallery, review thumbnails, command-line compositor, and accepted result
all read the same local artwork, millimetre geometry, and explicit masks.
Customer captures are opened read-only. The selected template controls both
the crop and the clipping shape; a heart is never filled with a rectangle.
"""

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont, ImageOps


ASSET_ROOT = Path(__file__).resolve().parent / "assets" / "templates"
PRICE_PER_SESSION = 5000
# FEAT-001: one chosen frame requires one 3-photo session, and each requested
# physical paper copy adds a separate print fee. Demo QR amounts use both fees.
PRICE_PER_PRINT_COPY = 5000
# The source artwork is exactly 8 printer dots/mm. 203.2 dpi preserves 80 mm
# physically; using 203 dpi would introduce a small but unnecessary size error.
DOTS_PER_MM = 8
PRINT_DPI = DOTS_PER_MM * 25.4
CANVAS_SIZE = (640, 1920)


@dataclass(frozen=True)
class PhotoAperture:
    """One exclusive-right/bottom pixel rectangle and its grayscale clip mask."""

    box: tuple[int, int, int, int]
    mask_path: Path
    shape: str

    @property
    def size(self) -> tuple[int, int]:
        """Return the crop size required by this individual photo window."""
        left, top, right, bottom = self.box
        return right - left, bottom - top


@dataclass(frozen=True)
class BoothTemplate:
    """A selectable design with all information needed to render it offline.

    IDs remain template_a through template_l so existing order/manifests that
    refer to the original four keys stay readable. source_id is the approved
    pack's 01–12 design number. Previously saved images are never recomposed.
    """

    template_id: str
    name: str
    description: str
    source_id: str
    artwork_path: Path
    apertures: tuple[PhotoAperture, ...]
    qr_box: tuple[int, int, int, int]
    # These presentation tokens also support the historical Tkinter gallery.
    background: str = "#ffffff"
    card: str = "#ffffff"
    accent: str = "#295e4d"
    foreground: str = "#1a302e"
    preview_background: str = "#ffffff"


def _pixel_box(spec: dict) -> tuple[int, int, int, int]:
    """Convert absolute physical edges once, avoiding accumulated rounding."""
    x, y = spec["x_mm"], spec["y_from_top_mm"]
    return (round(x * DOTS_PER_MM), round(y * DOTS_PER_MM),
            round((x + spec["width_mm"]) * DOTS_PER_MM),
            round((y + spec["height_mm"]) * DOTS_PER_MM))


def _read_catalog() -> tuple[BoothTemplate, ...]:
    """Load the committed layout and fail visibly if a design is incomplete."""
    data = json.loads((ASSET_ROOT / "layout_80mm.json").read_text(encoding="utf-8"))
    result = []
    for index, entry in enumerate(data["templates"]):
        frames = tuple(PhotoAperture(_pixel_box(frame), ASSET_ROOT / frame["mask_file"],
                                     frame["shape"]) for frame in entry["photo_apertures"])
        artwork = ASSET_ROOT / entry["png_file"]
        if len(frames) != 3 or not artwork.is_file() or any(
                not frame.mask_path.is_file() for frame in frames):
            raise ValueError(f"Incomplete assets for receipt template {entry['id']}.")
        result.append(BoothTemplate(
            template_id=f"template_{chr(ord('a') + index)}", name=entry["name"],
            description="3 foto · thermal 80 mm", source_id=entry["id"],
            artwork_path=artwork, apertures=frames, qr_box=_pixel_box(entry["qr_area"])))
    return tuple(result)


TEMPLATES = _read_catalog()
# Kept as a public convenience for older integrations. New review/composition
# code uses the actual template and index because aperture sizes can differ.
PHOTO_FRAME_SIZE = TEMPLATES[0].apertures[0].size


def get_templates() -> tuple[BoothTemplate, ...]:
    """Return all twelve approved designs in their established order."""
    return TEMPLATES


@lru_cache(maxsize=12)
def _artwork(template: BoothTemplate) -> Image.Image:
    """Cache immutable masters; callers must copy before drawing into them."""
    with Image.open(template.artwork_path) as source:
        image = source.convert("RGB")
    if image.size != CANVAS_SIZE:
        raise ValueError(f"Template {template.name} must be 640 × 1920 pixels.")
    return image


@lru_cache(maxsize=36)
def _mask(aperture: PhotoAperture) -> Image.Image:
    """Load a checked clip mask without retaining an open file handle."""
    with Image.open(aperture.mask_path) as source:
        mask = source.convert("L")
    if mask.size != aperture.size:
        raise ValueError(f"Photo mask does not match its aperture: {aperture.mask_path.name}")
    return mask


def fit_result_photo(source: Image.Image, template: BoothTemplate | None = None,
                     photo_index: int = 0) -> Image.Image:
    """Cover/crop to the selected window, preserving source aspect and EXIF.

    Portrait phone pictures can carry their rotation in metadata rather than
    pixels. Apply that rotation to a detached copy before cropping. Never save
    over a raw capture, and never stretch faces to fit a differently shaped box.
    """
    template = template or TEMPLATES[0]
    frame = template.apertures[photo_index]
    oriented = ImageOps.exif_transpose(source)
    return ImageOps.fit(oriented.convert("RGB"), frame.size,
                        method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def render_photo_frame(source: Image.Image, template: BoothTemplate,
                       photo_index: int, *, mirror_photo: bool = False) -> Image.Image:
    """Return exactly the frame pixels used by both review and saved output.

    Paper and ink outside the aperture remain from the master. The same rule
    protects a heart's corners and any decorative shapes intruding into a box.
    """
    frame = template.apertures[photo_index]
    result = _artwork(template).crop(frame.box)
    photo = fit_result_photo(source, template, photo_index)
    if mirror_photo:
        photo = ImageOps.mirror(photo)
    result.paste(photo, (0, 0), _mask(frame))
    return result


@lru_cache(maxsize=24)
def _preview(template: BoothTemplate, size: tuple[int, int]) -> Image.Image:
    """Contain the full strip so gallery previews never cut off its footer."""
    artwork = _artwork(template).copy()
    left, top, right, bottom = template.qr_box
    # Gallery artwork is a design sample, not a fake customer download link.
    # Remove the source's 'QR FOTO / LOGO' construction placeholder entirely.
    artwork.paste("white", template.qr_box)
    draw = ImageDraw.Draw(artwork)
    draw.text(((left + right) // 2, (top + bottom) // 2), "QR FOTO",
              font=_font(22), fill="#6f7972", anchor="mm")
    return ImageOps.pad(artwork, size, method=Image.Resampling.LANCZOS, color="white")


def create_template_preview(template: BoothTemplate,
                            size: tuple[int, int] = (120, 360)) -> Image.Image:
    """Return a detached gallery thumbnail of the actual approved design."""
    return _preview(template, size).copy()


def _font(size: int, bold: bool = False):
    """Use available system fonts on Windows/Linux without requiring downloads."""
    names = ("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _download_area(canvas: Image.Image, template: BoothTemplate,
                   folder_url: str | None, transaction_id: str, session_id: str):
    """Replace the whole QR placeholder while leaving themed borders intact."""
    left, top, right, bottom = template.qr_box
    canvas.paste("white", template.qr_box)
    draw = ImageDraw.Draw(canvas)
    if folder_url:
        from photobooth.qr_code import create_qr_image
        # Integer printer dots per module and the complete four-module quiet
        # zone are chosen by the shared QR generator BEFORE it paints pixels.
        # The logo is monochrome inside this thermal receipt; it stays centered.
        qr = create_qr_image(folder_url, max_size=min(right - left, bottom - top),
                             monochrome=True)
        canvas.paste(qr, (left + (right - left - qr.width) // 2,
                          top + (bottom - top - qr.height) // 2))
    else:
        # Local development has no public download destination. Keep an honest
        # empty-state message and do not encode a local path or dummy website.
        draw.multiline_text(((left + right) // 2, (top + bottom) // 2),
                            "MODE LOKAL\nFoto tersimpan\ndi perangkat ini",
                            font=_font(20), fill="#38483d", anchor="mm", align="center", spacing=9)
        # All approved masters reserve their two caption lines directly below
        # the QR. Clear only their central text area, preserving the outer art.
        draw.rectangle((128, bottom + 22, 512, bottom + 61), fill="white")
        draw.text((320, bottom + 41), "HASIL TERSIMPAN DI PERANGKAT",
                  font=_font(15, True), fill="black", anchor="mm")
    # Replace the construction note with the stable order/session reference.
    # It stays outside the QR white margin and inside the existing caption band.
    draw.rectangle((128, bottom + 62, 512, bottom + 86), fill="white")
    draw.text((320, bottom + 74), f"{transaction_id} · {session_id}",
              font=_font(13), fill="black", anchor="mm")


def compose_result(photo_paths: Sequence[Path], template: BoothTemplate,
                   output_path: Path, transaction_id: str, session_id: str,
                   folder_url: str | None = None, *, mirror_photos: bool = False) -> Path:
    """Save three photos inside the chosen 80 × 240 mm design as a PNG.

    PNG density is 203.2 dpi (640 × 1920 dots). Photos retain their colors for
    the digital download; the receipt art and QR are monochrome. A future
    printer adapter can dither photos separately without damaging QR modules.
    The destination is the transaction's cached real folder URL, so composing
    and showing results never depends on a new network request.
    Optional photo mirroring happens before masking; artwork and QR never flip.
    The default preserves existing v1 and command-line callers.
    """
    if len(photo_paths) != 3:
        raise ValueError("A session output must contain exactly three photos.")
    if folder_url is not None:
        parsed = urlparse(folder_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("The result QR requires a valid HTTPS folder URL.")
    canvas = _artwork(template).copy()
    for index, path in enumerate(photo_paths):
        with Image.open(path) as source:
            frame = render_photo_frame(source, template, index, mirror_photo=mirror_photos)
        canvas.paste(frame, template.apertures[index].box[:2])
    _download_area(canvas, template, folder_url, transaction_id, session_id)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", dpi=(PRINT_DPI, PRINT_DPI))
    return output_path
