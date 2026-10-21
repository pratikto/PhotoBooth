"""FEAT-021 poster-inspired v3: bolder arcade screens and printing-photo sprites.

Standalone demo only. The approved print-drop GIF is read from a local asset
when available; neither this renderer nor the animated photographs imply a
real printer, photo capture, QRIS transaction, or online scanner.
"""
import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw

PHOTO_GIF_NAME = "meong_photobooth_print_drop.gif"


def animation_gif_path():
    """Prefer a bundled asset; allow a local override without modifying source."""
    override = os.environ.get("MEONG_FLY_ANIM_GIF", "")
    if override and Path(override).is_file():
        return Path(override)
    bundled = Path(__file__).resolve().parent / "assets" / PHOTO_GIF_NAME
    return bundled if bundled.is_file() else None


def synth_print_frames(approved_frame, count=10):
    """Animate camera-cat hovering, without baking extra photos into its art.

    The ONE print emitter in Kivy is responsible for the paper feeding and
    falling sequence. This removes the old double-print overlay.
    """
    from math import sin, pi
    sprite = approved_frame.convert("RGBA")
    sprite.thumbnail((224, 150), Image.Resampling.NEAREST)
    frames = []
    for idx in range(count):
        out = Image.new("RGBA", (244, 184), (0, 0, 0, 0))
        dy = round(sin(idx * 2 * pi / count) * 3)
        out.alpha_composite(sprite, (10, 9 + dy))
        frames.append(out)
    return tuple(frames)

@lru_cache(maxsize=4)
def meong_animation_frames(logo_path, limit=15):
    """Return cropped native GIF frames, or approved PNG sprite as fallback.

    Downsampling keeps pixel edges crisp and pre-rendered texture count bounded.
    """
    from .meong_fly_painter import logo_parts
    source = animation_gif_path()
    if source is not None:
        with Image.open(source) as gif:
            # Decode only the clean first frame: later GIF frames already
            # contain a print and would double-up with the new paper emitter.
            gif.seek(0)
            frame = gif.convert("RGBA")
            w, h = frame.size
            frame = frame.crop((round(w*.08), round(h*.07),
                                round(w*.92), round(h*.57)))
            return synth_print_frames(frame, count=min(limit, 10))
    # Always prefer the actual owner's new GIF-derived cropped camera-cat.
    # Encoded as ASCII to preserve binary fidelity through text-only GitHub tools.
    # This frame is bundled, even when the animated GIF isn't installed locally.
    try:
        import base64
        from io import BytesIO
        asset = Path(__file__).resolve().parent / "assets" / "meong_fly_gif_logo.b85"
        image = Image.open(BytesIO(base64.b85decode(
            asset.read_text(encoding="ascii").strip()))).convert("RGBA")
        return synth_print_frames(image)
    except (OSError, ValueError, EOFError):
        # Old official PNG is only a last-resort fallback.
        _, body = logo_parts(str(logo_path))
        return synth_print_frames(body.convert("RGBA"))


def camera_cat_from_latest_logo(logo_path):
    """Extract the flying camera-cat, without the rainbow, for game hitboxes."""
    frame = meong_animation_frames(logo_path)[0]
    w, h = frame.size
    # User's new GIF artwork has the camera-cat at the right of its trail.
    return frame.crop((round(w*.24), round(h*.05),
                       round(w*.96), round(h*.96)))


def printed_photo_tile(index=0):
    """Generate cheerful instant-film pixels for the in-space print cascade."""
    import random
    rng = random.Random(5129 + index * 107)
    image = Image.new("RGBA", (32, 41), (0, 0, 0, 0))
    d = ImageDraw.Draw(image)
    d.rectangle((2, 2, 30, 39), fill=(6, 9, 36))
    d.rectangle((0, 0, 28, 37), fill=(248, 247, 255))
    d.rectangle((3, 3, 25, 27), fill=(160, 212, 255))
    d.rectangle((3, 20, 25, 27), fill=(132, 112, 222))
    # Gray cat with pointed ears, expressive eyes and pink cheeks.
    d.polygon(((6, 15), (7, 7), (13, 12), (18, 12),
               (23, 7), (24, 21), (20, 25), (9, 25)), fill=(88, 93, 131))
    d.rectangle((11, 16, 12, 18), fill=(255, 255, 255))
    d.rectangle((19, 16, 20, 18), fill=(255, 255, 255))
    d.rectangle((14, 21, 17, 22), fill=(21, 22, 49))
    d.rectangle((8, 20, 10, 21), fill=(255, 123, 176))
    d.rectangle((21, 20, 23, 21), fill=(255, 123, 176))
    d.rectangle((6, 32, 22, 33), fill=(210, 199, 238))
    if rng.randrange(2):
        d.rectangle((24, 30, 25, 32), fill=(252, 104, 166))
    return image



def photo_feed_frames(tile, steps=8):
    """Pre-render 8 physical reveal stages, never squash photo pixels.

    The top of each photograph peeks out of Meong's camera slot first.
    Texture bytes are prepared only at screen construction, not each frame.
    """
    width, height = tile.size
    result = []
    for index in range(1, steps + 1):
        exposed = max(1, round(height * index / steps))
        paper = Image.new("RGBA", tile.size, (0, 0, 0, 0))
        paper.alpha_composite(tile.crop((0, 0, width, exposed)), (0, 0))
        result.append(paper)
    return tuple(result)


def _hero(image, frame, box):
    from .meong_fly_painter import place_art
    x,y,w,h=box
    place_art(image, frame, x,y,w,h)


def paint_poster_screen(screen, logo_path):
    """Poster-aligned Start / Win / Game Over cards with concise bold copy."""
    from . import meong_fly_painter as p
    from .meong_fly_polish import arcade_card, arcade_button, sparkle
    if screen not in ("start", "won", "lost"):
        raise ValueError(screen)
    frame = Image.new("RGBA", (p.W, p.H), (0, 0, 0, 255))
    d=ImageDraw.Draw(frame)
    p.draw_common(d,screen)
    # Additional high contrast sparkle depth.
    for x,y,color in ((45,95,p.GOLD),(305,128,p.CYAN),
                      (16,349,p.PINK),(335,472,p.GOLD),(298,646,p.CYAN)):
        sparkle(d,x,y,4,color)
    if screen=="start":
        d.ellipse((42,73,318,287),fill=(16, 25, 81))
        d.ellipse((67,91,294,262),fill=(27, 31, 100))
        # Leave a real print-drop pocket between the camera and MEONG title.
        _hero(frame, meong_animation_frames(logo_path)[0],(35,69,290,175))
        d=ImageDraw.Draw(frame)
        # Big two-line white title: deliberately NOT a black wordmark on navy.
        p.pixel_text(d,"MEONG",180,278,scale=7,fill=p.WHITE,
                     shadow=(55,82,166))
        p.pixel_text(d,"FLY!",180,339,scale=7,fill=p.GOLD,
                     shadow=(146,57,128))
        arcade_card(d,(36,421,324,459),(13,30,79),(95,91,189))
        p.pixel_text(d,"HINDARI ASTEROID!",180,435,scale=2,fill=p.CYAN)
        arcade_card(d,(38,469,322,534),(255,218,126),(255,154,65),
                    glow=(255,250,187))
        p.pixel_text(d,"DISKON",180,476,scale=2,fill=p.INK)
        p.pixel_text(d,"RP 2.500",180,497,scale=4,fill=(238,40,120))
        arcade_button(d,p.ACTIONS["start"]["game"],"MAIN GAME","pink",p,
                      scale=3,icon="gamepad")
        arcade_button(d,p.ACTIONS["start"]["photo"],"LANGSUNG FOTO","cyan",p,
                      scale=2,icon="camera")
        p.pixel_text(d,"DISKON HANYA SIMULASI",180,688,scale=1,fill=p.WHITE)
    elif screen=="won":
        for idx in range(18):
            x=180+round(142*__import__("math").cos(idx*.349))
            y=276+round(128*__import__("math").sin(idx*.349))
            d.line((180,282,x,y),fill=(57,49,128),width=3)
        p.pixel_text(d,"SELAMAT!",180,114,scale=5,fill=p.GOLD,
                     shadow=(230,82,116))
        _hero(frame,meong_animation_frames(logo_path)[0],(78,219,215,160))
        d=ImageDraw.Draw(frame)
        p.pixel_text(d,"TARGET TERCAPAI!",180,390,scale=2,fill=p.WHITE)
        arcade_card(d,(36,425,324,537),(255,221,129),(255,155,66))
        p.pixel_text(d,"DISKON",180,438,scale=3,fill=p.INK)
        p.pixel_text(d,"RP 2.500",180,477,scale=4,fill=(236,42,120))
        p.pixel_text(d,"SIMULASI - BELUM AKTIF",180,514,scale=1,
                     fill=(120,44,63))
        arcade_button(d,p.ACTIONS["won"]["continue"],
                      "PILIH LAYOUT FOTO","cyan",p,scale=2)
    else:
        p.pixel_text(d,"GAME",180,110,scale=6,fill=(255,115,168),
                     shadow=(98,34,104))
        p.pixel_text(d,"OVER",180,173,scale=6,fill=(255,115,168),
                     shadow=(98,34,104))
        _hero(frame,meong_animation_frames(logo_path)[0],(97,264,170,118))
        d=ImageDraw.Draw(frame)
        arcade_card(d,(45,393,315,491),(16,28,76),(174,89,164))
        p.pixel_text(d,"SCORE",180,402,scale=3,fill=p.WHITE)
        p.pixel_text(d,"TETAP BISA FOTO!",180,514,scale=2,fill=p.WHITE)
        arcade_button(d,p.ACTIONS["lost"]["continue"],
                      "PILIH LAYOUT FOTO","cyan",p,scale=2)
        p.pixel_text(d,"TANPA DISKON",180,650,scale=2,fill=p.GOLD)
    return frame


def animation_tick(t, duration=2.4):
    """Pure function; Kivy uses it to select an immutable cached GIF frame."""
    return int(max(0,t)*10) % max(1,round(duration*10))

