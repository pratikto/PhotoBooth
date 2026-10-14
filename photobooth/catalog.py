"""Sample photobooth templates and local image composition.

The bundled template art is illustrative for the local MVP. Replace the sample
artwork when the final Meong Photo Booth templates are ready.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont, ImageOps


@dataclass(frozen=True)
class BoothTemplate:
    template_id: str
    name: str
    description: str
    background: str
    card: str
    accent: str
    foreground: str
    preview_background: str


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


def compose_result(
    photo_paths: Sequence[Path],
    template: BoothTemplate,
    output_path: Path,
    transaction_id: str,
    session_id: str,
) -> Path:
    """Compose the three selected images into a portrait digital photo strip."""
    if len(photo_paths) != 3:
        raise ValueError("A session output must contain exactly three photos.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1800, 1000
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
    draw.text((105, 48), "MEONGS PHOTOBOOTH", fill=template.foreground, font=title_font)
    draw.text(
        (108, 112),
        template.name.upper(),
        fill=template.accent,
        font=_font(27, bold=True),
    )

    photo_width = 470
    photo_height = 610
    gap = 40
    total_photos_width = photo_width * 3 + gap * 2
    left = (width - total_photos_width) // 2
    first_top = 195
    resampling = getattr(Image, "Resampling", Image).LANCZOS

    for index, photo_path in enumerate(photo_paths):
        photo_left = left + index * (photo_width + gap)
        top = first_top
        with Image.open(photo_path) as source:
            photo = ImageOps.fit(
                source.convert("RGB"),
                (photo_width, photo_height),
                method=resampling,
                centering=(0.5, 0.5),
            )
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

    footer_top = 850
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

    canvas.save(output_path, format="PNG")
    return output_path

