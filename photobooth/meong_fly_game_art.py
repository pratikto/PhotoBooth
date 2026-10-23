"""FEAT-021 Batch B: pixel-arcade Gameplay art and pre-rendered sprite states.

Pure Pillow. Kivy uploads each image exactly once on stage creation. The rock
textures are decorative and must be displayed entirely inside the existing
rectangular asteroid collision fields; no game physics or receipt code here.
"""
from math import cos, pi, sin
from random import Random

from PIL import Image, ImageDraw

GAME_FIELD_TOP = 106
GAME_FIELD_BOTTOM = 586
ROCK_VARIANTS = 5
CAT_POSES = ("climb", "level", "dive")


def _shimmer(draw, x, y, radius, color):
    draw.line((x-radius, y, x+radius, y), fill=color, width=1)
    draw.line((x, y-radius, x, y+radius), fill=color, width=1)
    draw.point((x, y), fill=(252, 250, 255))


def _nebula(draw, cx, cy, radius, tint):
    """Stepped, subdued pixel-nebula rings; no blur or dynamic textures."""
    colors = (
        tuple(max(0, int(v * .20)) for v in tint),
        tuple(max(0, int(v * .28)) for v in tint),
        tuple(max(0, int(v * .40)) for v in tint),
        tuple(max(0, int(v * .52)) for v in tint),
    )
    for step, color in enumerate(colors):
        r = radius - step * 14
        draw.ellipse((cx-r, cy-r*.55, cx+r, cy+r*.55), fill=color)
    rng = Random(cx * 109 + cy)
    for index in range(22):
        x = cx + rng.randrange(-radius + 12, radius - 11)
        y = cy + rng.randrange(-radius // 3, radius // 3 + 1)
        draw.rectangle((x, y, x+index%3, y+index%3), fill=(74, 65, 127))


def _pixel_moon(draw, cx, cy, radius, palette):
    """Low-contrast celestial object belonging to background, not a hazard."""
    dark, base, light = palette
    draw.ellipse((cx-radius-2, cy-radius-2, cx+radius+2, cy+radius+2), fill=dark)
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=base)
    draw.polygon(((cx-radius*.76, cy-radius*.42),
                  (cx-radius*.14, cy-radius*.85),
                  (cx+radius*.26, cy-radius*.55),
                  (cx-radius*.19, cy-radius*.08)), fill=light)
    for a, b, rr in ((-.39, .25, .22), (.33, -.17, .16)):
        x, y, r = cx+a*radius, cy+b*radius, radius*rr
        draw.ellipse((x-r, y-r, x+r, y+r), fill=dark)
        draw.arc((x-r, y-r, x+r, y+r), 190, 310, fill=light, width=1)


def paint_game_background():
    """Create one cached 360x720 parallax-ready Gameplay background."""
    from . import meong_fly_painter as p
    from .meong_fly_polish import arcade_card

    canvas = Image.new("RGBA", (p.W, p.H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)
    # Mid-screen stays quiet so the actual camera-cat and collision gap pop.
    for y in range(p.H):
        draw.line((0, y, p.W, y), fill=(4, 10 + int(y/150), 36 + int(y/40)), width=1)
    _nebula(draw, 266, 304, 104, (73, 59, 151))
    _nebula(draw, 70, 467, 89, (42, 53, 136))
    _nebula(draw, 307, 558, 106, (102, 43, 143))

    rng = Random(21021)
    for k in range(138):
        x, y = rng.randrange(3, p.W-2), rng.randrange(90, 657)
        tone = rng.choice(((121, 108, 224), (89, 164, 237),
                           (242, 184, 122), (209, 178, 255)))
        if k % 14 == 0:
            _shimmer(draw, x, y, 3 + k % 2, tone)
        else:
            draw.rectangle((x, y, x + (k % 5 == 0), y + (k % 5 == 0)), fill=tone)

    # Distant ringed planet, small cool moon, spiral galaxy and Earth horizon.
    p.planet(draw, 323, 583, 51, (149, 70, 180))
    p.galaxy(draw, 66, 523, 46)
    _pixel_moon(draw, 311, 164, 21,
                ((48, 49, 109), (98, 117, 187), (139, 166, 218)))
    _pixel_moon(draw, 23, 245, 12,
                ((42, 44, 91), (83, 78, 138), (125, 106, 169)))
    p.earth(draw, 3, 804, 123)

    # Thin boundaries help players understand the actual bounded play field.
    draw.line((17, GAME_FIELD_TOP, 343, GAME_FIELD_TOP), fill=(51, 66, 128), width=1)
    draw.line((17, GAME_FIELD_BOTTOM, 343, GAME_FIELD_BOTTOM),
              fill=(51, 66, 128), width=1)
    for x in range(18, 345, 18):
        draw.rectangle((x, GAME_FIELD_TOP, x+2, GAME_FIELD_TOP+1), fill=(81, 94, 165))
        draw.rectangle((x, GAME_FIELD_BOTTOM-1, x+2, GAME_FIELD_BOTTOM),
                       fill=(81, 94, 165))

    # All three HUD cards share the Start/Scan pixel material system.
    arcade_card(draw, (15, 18, 63, 64), (18, 32, 78), (169, 173, 225),
                shadow=(1, 2), glow=(204, 207, 250))
    p.pixel_text(draw, "II", 39, 28, scale=3, fill=p.WHITE)
    arcade_card(draw, (91, 17, 231, 87), (15, 28, 78), (99, 85, 164),
                shadow=(1, 3), glow=(125, 113, 194))
    arcade_card(draw, (246, 17, 347, 87), (13, 33, 81), (88, 154, 198),
                shadow=(1, 3), glow=(140, 216, 240))
    p.pixel_text(draw, "SCORE", 161, 29, scale=2, fill=p.WHITE)
    p.pixel_text(draw, "TARGET", 296, 29, scale=2, fill=p.CYAN)
    from .meong_fly import TARGET_SCORE
    p.pixel_text(draw, str(TARGET_SCORE), 296, 52, scale=3, fill=p.CYAN)

    draw.rectangle((0, 635, p.W, 719), fill=(8, 16, 51))
    draw.line((16, 643, 344, 643), fill=(61, 69, 132), width=2)
    p.pixel_text(draw, "TAP UNTUK TERBANG!", 180, 656, scale=2, fill=p.GOLD)
    p.pixel_text(draw, "DEMO - 1 STRUK 1 KESEMPATAN", 180, 694, scale=1,
                 fill=(193, 189, 232))
    for x, y, c in ((28, 662, p.CYAN), (331, 670, p.PINK),
                    (338, 142, p.GOLD), (18, 561, p.CYAN)):
        _shimmer(draw, x, y, 3, c)
    return canvas


def make_rock_tile(variant=0):
    """Five deterministic alpha asteroid sprites, bounded by 64x64 pixels.

    Kivy paints a faint full-width belt to communicate the rectangular hitbox.
    """
    palette = (
        ((42, 39, 83), (131, 119, 173), (193, 173, 207)),
        ((50, 43, 92), (122, 92, 170), (180, 144, 221)),
        ((68, 43, 67), (165, 105, 103), (224, 158, 135)),
        ((40, 48, 88), (99, 133, 177), (151, 178, 204)),
        ((52, 43, 82), (145, 119, 158), (216, 181, 195)),
    )
    dark, base, light = palette[variant % len(palette)]
    rng = Random(951 + variant % ROCK_VARIANTS * 103)
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    polygon = []
    for index in range(14):
        angle = 2*pi*index/14
        radius = 27 + rng.randrange(-4, 3)
        polygon.append((int(32 + radius * cos(angle)),
                        int(32 + radius * sin(angle))))
    draw.polygon([(x+2, y+3) for x, y in polygon], fill=(8, 10, 37))
    draw.polygon(polygon, fill=dark)
    inset = [(32 + int((x-32)*.91), 32 + int((y-32)*.91))
             for x, y in polygon]
    draw.polygon(inset, fill=base)
    draw.polygon(((15, 21), (25, 10), (39, 14), (27, 27), (20, 30)), fill=light)
    for x, y, radius in ((22, 38, 9), (41, 33, 7), (33, 49, 5), (40, 18, 4)):
        ox = (variant * 3) % 5 - 2
        draw.ellipse((x+ox-radius, y-radius, x+ox+radius, y+radius), fill=dark)
        draw.arc((x+ox-radius, y-radius, x+ox+radius, y+radius),
                 160, 270, fill=light, width=2)
    for x, y in ((13, 32), (53, 37), (22, 55)):
        draw.rectangle((x, y, x+2, y+2), fill=light)
    return image


def camera_cat_poses(body):
    """Keep the approved camera-cat recognizable inside SAME engine hitbox.

    Five-degree cosmetic rotations remain in its existing collision rectangle.
    """
    source = body.convert("RGBA").resize((70, 48), Image.Resampling.NEAREST)
    base = Image.new("RGBA", (78, 58), (0, 0, 0, 0))
    base.alpha_composite(source, (4, 5))
    return {
        "level": base,
        "climb": base.rotate(5, Image.Resampling.NEAREST, expand=False,
                             fillcolor=(0, 0, 0, 0)),
        "dive": base.rotate(-5, Image.Resampling.NEAREST, expand=False,
                            fillcolor=(0, 0, 0, 0)),
    }


def asteroid_screen_rects(obstacle_x, gap_y):
    """Exact top-origin 360x720 boxes for the unchanged 480x640 engine."""
    from .meong_fly import GAP_HEIGHT, HEIGHT, PIPE_WIDTH, WIDTH
    scale = 360 / WIDTH
    x = obstacle_x * scale
    w = PIPE_WIDTH * scale
    lower = max(0.0, gap_y - GAP_HEIGHT / 2) * scale
    upper = max(0.0, HEIGHT - (gap_y + GAP_HEIGHT / 2)) * scale
    return (
        ("lower", (x, GAME_FIELD_BOTTOM - lower, w, lower)),
        ("upper", (x, GAME_FIELD_TOP, w, upper)),
    )


def camera_screen_rect(y):
    """Top-origin camera body box matching CAT_LEFT/RIGHT/TOP/BOTTOM."""
    from .meong_fly import CAT_BOTTOM, CAT_LEFT, CAT_RIGHT, CAT_TOP, CAT_X, WIDTH
    scale = 360 / WIDTH
    return ((CAT_X - CAT_LEFT) * scale,
            GAME_FIELD_BOTTOM - (y + CAT_TOP) * scale,
            (CAT_LEFT + CAT_RIGHT) * scale,
            (CAT_BOTTOM + CAT_TOP) * scale)
