# PhotoBooth source file
# Template definitions, preview artwork, and composition logic for the digital photo result.

"""Sample photobooth templates and local image composition.

The bundled template art is illustrative for the local MVP. Replace the sample
artwork when the final Meong Photobooth templates are ready.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont, ImageOps


@dataclass(frozen=True)
class BoothTemplate:
    # Describe one selectable photo template: its ID, display text, colors, layout, and optional
    # sample artwork used by the picker and result composer.
    template_id: str
    name: str
    description: str
    background: str
    card: str
    accent: str
    foreground: str
    preview_background: str


# Each quantity represents a separate three-photo session for one template.
# Keep the tariff in one place so gallery, cart, and payment cannot disagree.
PRICE_PER_SESSION = 5000

# All current templates use this exact photo aperture. Review thumbnails and
# the saved composition must share it; a full-camera thumbnail can otherwise
# show a face near an edge that the final center crop silently removes.
PHOTO_FRAME_SIZE = (470, 500)

TEMPLATES = (
    BoothTemplate(
        template_id="template_a",
        name="Template 1",
        description="Classic warm tones",
        background="#fff8ec",
        card="#ffffff",
        accent="#d88c55",
        foreground="#33251d",
        preview_background="#f3d8c2",
    ),
    BoothTemplate(
        template_id="template_b",
        name="Template 2",
        description="Cool blue tones",
        background="#edf4fb",
        card="#ffffff",
        accent="#4d78a6",
        foreground="#18365a",
        preview_background="#dce8f5",
    ),
    BoothTemplate(
        template_id="template_c",
        name="Template 3",
        description="Soft lilac tones",
        background="#f2eefb",
        card="#ffffff",
        accent="#8e78bd",
        foreground="#41345f",
        preview_background="#e8e0f5",
    ),
    BoothTemplate(
        template_id="template_d",
        name="Template 4",
        description="Fresh mint tones",
        background="#eaf6ef",
        card="#ffffff",
        accent="#4b9d79",
        foreground="#263e39",
        preview_background="#d9eee3",
    ),
)


def get_templates() -> tuple[BoothTemplate, ...]:
    """Return the ordered templates shown on the landing screen."""
    return TEMPLATES


def _font(size: int, bold: bool = False):
    """Load a common system font, falling back safely on minimal systems."""
    candidates = (
        ("arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf")
        if bold
        else ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf")
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def create_template_preview(
    template: BoothTemplate,
    size: tuple[int, int] = (380, 220),
) -> Image.Image:
    """Draw a sample card illustration in the style of the procedure mockups."""
    width, height = size
    image = Image.new("RGB", size, template.preview_background)
    draw = ImageDraw.Draw(image)

    # Two simple silhouettes act as neutral placeholders for customer photos.
    head_radius = max(12, height // 8)
    left_x = int(width * 0.19)
    right_x = int(width * 0.81)
    head_y = int(height * 0.34)
    draw.ellipse(
        (left_x - head_radius, head_y - head_radius, left_x + head_radius, head_y + head_radius),
        fill="#ffbb00",
    )
    draw.ellipse(
        (right_x - head_radius, head_y - head_radius, right_x + head_radius, head_y + head_radius),
        fill="#ffd28e",
    )

    body_top = head_y + head_radius // 2
    body_bottom = int(height * 0.83)
    body_width = int(width * 0.18)
    draw.rounded_rectangle(
        (left_x - body_width, body_top, left_x + body_width, body_bottom),
        radius=body_width // 2,
        fill="#1b3a60",
    )
    draw.rounded_rectangle(
        (right_x - body_width, body_top + 8, right_x + body_width, body_bottom - 6),
        radius=body_width // 2,
        fill="#6e91b4",
    )

    return image


def fit_result_photo(source: Image.Image) -> Image.Image:
    """Return the final frame pixels without changing the original capture.

    Keep the established center-crop and LANCZOS resampling in one place so
    review and composition cannot drift apart. This returns a new RGB image;
    raw captures, replacement files, and previously saved results stay intact.
    Every current template uses the same aperture, not the camera aspect ratio.
    """
    return ImageOps.fit(
        source.convert("RGB"),
        PHOTO_FRAME_SIZE,
        method=getattr(Image, "Resampling", Image).LANCZOS,
        centering=(0.5, 0.5),
    )


def compose_result(
    photo_paths: Sequence[Path],
    template: BoothTemplate,
    output_path: Path,
    transaction_id: str,
    session_id: str,
    folder_url: str | None = None,
) -> Path:
    """Compose three photos plus their stable transaction-folder QR.

    ``folder_url`` is captured in the transaction manifest before photography.
    It therefore works without a network request and stays the same when queued
    uploads resume. Local-only sessions have no real destination and must not
    contain a fabricated QR or a local machine path.
    """
    if len(photo_paths) != 3:
        raise ValueError("A session output must contain exactly three photos.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1800, 1000
    # Start from the selected template colors so every session output has the same visual theme.
    canvas = Image.new("RGB", (width, height), template.background)
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle(
        (42, 42, width - 42, height - 42),
        radius=34,
        outline=template.accent,
        width=8,
    )

    title_font = _font(48, bold=True)
    small_font = _font(24)
    draw.text((105, 48), "MEONG PHOTOBOOTH", fill=template.foreground, font=title_font)
    draw.text(
        (108, 112),
        template.name.upper(),
        fill=template.accent,
        font=_font(27, bold=True),
    )

    # Reserve a dedicated footer for the scannable QR. It must never overlap
    # faces or be cropped together with a photo. Output remains 1800x1000.
    photo_width, photo_height = PHOTO_FRAME_SIZE
    gap = 40
    # Center three fixed-size frames as a group instead of spacing them relative to the window.
    total_photos_width = photo_width * 3 + gap * 2
    left = (width - total_photos_width) // 2
    first_top = 195
    for index, photo_path in enumerate(photo_paths):
        photo_left = left + index * (photo_width + gap)
        top = first_top
        with Image.open(photo_path) as source:
            photo = fit_result_photo(source)
        draw.rounded_rectangle(
            (
                photo_left - 11,
                top - 11,
                photo_left + photo_width + 11,
                top + photo_height + 11,
            ),
            radius=18,
            fill=template.card,
        )
        canvas.paste(photo, (photo_left, top))

    footer_top = 735
    # Keep the transaction and session IDs on the image so customers can identify the result later.
    draw.line(
        (105, footer_top, width - 105, footer_top),
        fill=template.accent,
        width=4,
    )
    draw.text(
        (108, footer_top + 22),
        f"{transaction_id}  |  {session_id}",
        fill=template.foreground,
        font=small_font,
    )

    if folder_url:
        from photobooth.qr_code import create_qr_image
        from urllib.parse import urlparse
        parsed = urlparse(folder_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("The result QR requires a valid HTTPS folder URL.")
        # Render at the final footer scale so the full logo is resized only
        # once and every QR module keeps an integer width. The shared helper
        # also protects recognition patterns and the white scan margin.
        qr = create_qr_image(folder_url, max_size=210)
        qr_size = qr.width
        canvas.paste(qr, (width - 115 - qr_size, 750))
        draw.text((108, footer_top + 73), "SCAN UNTUK MEMBUKA FOLDER FOTO",
                  fill=template.foreground, font=_font(28, bold=True))
        draw.text((108, footer_top + 119), "Foto mentah dan hasil template ada di folder yang sama.",
                  fill=template.foreground, font=small_font)
    else:
        # Keep an honest label for local development. A QR for a Windows path
        # would be unusable on the customer's phone and is deliberately omitted.
        draw.text((108, footer_top + 78), "HASIL LOKAL - LINK FOLDER BELUM TERSEDIA",
                  fill=template.foreground, font=small_font)

    canvas.save(output_path, format="PNG")
    return output_path

