"""FEAT-021/BUG-013: authored camera geometry shared by hero and gameplay.

Source coordinates refer to the bundled 224x152 owner artwork, not a guessed
fraction of a screen box. Optional external GIFs lack this geometry contract
and are deliberately not used by the v5 compositor. No original asset is edited.
"""
from dataclasses import dataclass
from functools import lru_cache
from math import cos, sin, radians
from pathlib import Path
from io import BytesIO
import base64

from PIL import Image, ImageDraw
from .meong_fly_print_fx import paper_corners

SOURCE_SIZE = (224, 152)
# Horizontal outlet under the blue lens: inner opening and foreground lip.
SLOT = (108.0, 124.0)
SLOT_WIDTH = 40.0
GAME_CROP = (64, 32, 224, 144)
HERO_BOXES = {
    "start": (35, 69, 290, 175),
    "won": (78, 190, 215, 160),
    "lost": (97, 264, 170, 118),
}


@dataclass(frozen=True)
class CameraFrame:
    rear: Image.Image
    front: Image.Image
    slot: tuple[float, float]
    slot_width: float
    angle: float = 0.0  # Clockwise in top-origin coordinates.


def rotate_point(point, center, angle):
    a = radians(angle)
    x, y = point[0] - center[0], point[1] - center[1]
    return (center[0] + x*cos(a) - y*sin(a),
            center[1] + x*sin(a) + y*cos(a))


def fit_rect(size, box):
    x, y, w, h = box
    scale = min(w/size[0], h/size[1])
    return (x+(w-size[0]*scale)/2, y+(h-size[1]*scale)/2,
            size[0]*scale, size[1]*scale)


def world_slot(frame, rect):
    x, y, w, h = rect
    return (x + frame.slot[0]*w/frame.front.width,
            y + frame.slot[1]*h/frame.front.height)


@lru_cache(maxsize=1)
def camera_frames():
    """Build all immutable layers once; crop/scale/rotate metadata with pixels."""
    path = Path(__file__).parent / "assets" / "meong_fly_gif_logo.b85"
    source = Image.open(BytesIO(base64.b85decode(path.read_text().strip()))).convert("RGBA")
    if source.size != SOURCE_SIZE:
        raise ValueError("Meong artwork changed: re-author slot metadata first")
    # This small slot treatment sits on the existing lower camera housing.
    # The aperture is transparent in the foreground; paper can only emerge
    # below the lip, with the opaque camera body occluding its hidden portion.
    front = source.copy()
    d = ImageDraw.Draw(front)
    d.rectangle((86, 119, 130, 126), fill=(5, 9, 24, 255))
    d.rectangle((88, 121, 128, 124), fill=(0, 0, 0, 0))
    d.line((86, 119, 130, 119), fill=(222, 234, 244, 255), width=2)
    rear = Image.new("RGBA", SOURCE_SIZE)
    ImageDraw.Draw(rear).rectangle((88, 121, 128, 126), fill=(4, 7, 19, 255))
    frames = {"hero": CameraFrame(rear, front, SLOT, SLOT_WIDTH)}
    cropped = [layer.crop(GAME_CROP) for layer in (rear, front)]
    # Aspect preserving fit inside the existing 78x58 engine sprite rectangle.
    fitted = fit_rect(cropped[0].size, (4, 5, 70, 48))
    x, y, w, h = (round(v) for v in fitted)
    layers = []
    for layer in cropped:
        out = Image.new("RGBA", (78, 58))
        out.alpha_composite(layer.resize((w, h), Image.Resampling.NEAREST), (x, y))
        layers.append(out)
    slot = (x+(SLOT[0]-GAME_CROP[0])*w/cropped[0].width,
            y+(SLOT[1]-GAME_CROP[1])*h/cropped[0].height)
    for name, angle in (("level", 0), ("climb", -5), ("dive", 5)):
        # Pillow positive angles are counterclockwise, opposite our y-down pose.
        rotated = [im.rotate(-angle, Image.Resampling.NEAREST,
                             center=(39, 29), expand=False) for im in layers]
        frames[name] = CameraFrame(*rotated, rotate_point(slot, (39, 29), angle),
                                   SLOT_WIDTH*w/cropped[0].width, angle)
    return frames

