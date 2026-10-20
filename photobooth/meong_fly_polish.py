"""FEAT-021 Batch A visual polish for Start and Scan (standalone only).

Pure Pillow drawing. Hit regions and the real editable Kivy TextInput remain
owned by meong_fly_painter / meong_fly_gui, respectively. No POS scanner.
"""
from math import sin, cos, pi
from pathlib import Path
from PIL import Image, ImageDraw


def arcade_card(draw, bounds, fill, edge, *, shadow=(3, 5), glow=None):
    """A consistent stepped arcade panel with bevel, inset and drop shadow."""
    x0, y0, x1, y1 = (int(z) for z in bounds)
    dx, dy = shadow
    draw.rectangle((x0 + 6 + dx, y0 + dy, x1 - 6 + dx, y1 + dy), fill=(3, 5, 26))
    draw.rectangle((x0 + dx, y0 + 6 + dy, x1 + dx, y1 - 6 + dy), fill=(3, 5, 26))
    draw.rectangle((x0 + 6, y0, x1 - 6, y1), fill=edge)
    draw.rectangle((x0, y0 + 6, x1, y1 - 6), fill=edge)
    draw.rectangle((x0 + 8, y0 + 4, x1 - 8, y1 - 4), fill=fill)
    draw.rectangle((x0 + 4, y0 + 9, x1 - 4, y1 - 9), fill=fill)
    # Distinct, restrained top shine and right/bottom pixel shadow.
    shine = glow if glow else (min(255, fill[0] + 28), min(255, fill[1] + 31), min(255, fill[2] + 39))
    draw.line((x0 + 12, y0 + 5, x1 - 12, y0 + 5), fill=shine, width=2)
    draw.line((x0 + 5, y0 + 13, x0 + 5, y1 - 14), fill=shine, width=1)
    draw.line((x0 + 12, y1 - 5, x1 - 12, y1 - 5), fill=(max(0, fill[0] - 24), max(0, fill[1] - 21), max(0, fill[2] - 16)), width=2)
    draw.line((x1 - 5, y0 + 13, x1 - 5, y1 - 14), fill=(max(0, fill[0] - 19), max(0, fill[1] - 17), max(0, fill[2] - 12)), width=1)


def arcade_button(draw, bounds, label, kind, painter, *, scale=2, icon=None):
    x, y, w, h = (int(z) for z in bounds)
    palette = {
        "pink": ((255, 83, 169), (255, 165, 218), (98, 20, 89)),
        "cyan": ((77, 204, 250), (175, 241, 255), (12, 75, 137)),
        "dark": ((27, 41, 91), (149, 148, 210), (9, 15, 51)),
    }
    base, edge, shadow = palette[kind]
    draw.rectangle((x + 8, y + h - 1, x + w - 5, y + h + 5), fill=shadow)
    arcade_card(draw, (x, y, x + w, y + h - 3), base, edge, shadow=(0, 2))
    text_color = painter.WHITE if kind == "dark" else painter.INK
    painter.pixel_text(draw, label, x + w / 2 + (13 if icon else 0),
                       y + (h - 7 * scale) / 2 - 3, scale=scale,
                       fill=text_color)
    if icon == "gamepad":
        painter._gamepad_icon(draw, x + 32, y + 15)
    if icon == "camera":
        painter._camera_icon(draw, x + 34, y + 15)
    if kind == "pink":
        draw.rectangle((x + w - 24, y + 10, x + w - 20, y + 14), fill=(255, 205, 233))
        draw.rectangle((x + w - 31, y + 17, x + w - 29, y + 20), fill=(255, 205, 233))


def sparkle(draw, x, y, size, color):
    draw.line((x - size, y, x + size, y), fill=color, width=1)
    draw.line((x, y - size, x, y + size), fill=color, width=1)
    draw.rectangle((x - 1, y - 1, x + 1, y + 1), fill=(250, 248, 255))


def halo(draw):
    """Subtle stepped hero aura is BEHIND the approved official logo."""
    for radius, color in ((132, (12, 17, 64)), (113, (18, 24, 77)),
                          (91, (28, 32, 91)), (69, (35, 38, 98))):
        draw.ellipse((180 - radius, 153 - radius * .61,
                      180 + radius, 153 + radius * .61), fill=color)
    for index in range(12):
        angle = index * 2 * pi / 12
        outer = 135 if index % 2 else 122
        px = int(180 + outer * cos(angle))
        py = int(154 + outer * .58 * sin(angle))
        sparkle(draw, px, py, 3 if index % 3 else 5,
                (132, 107, 220) if index % 2 else (91, 201, 250))


def scanner_corners(draw, x0=91, y0=253, x1=269, y1=432):
    """Decorative scanner brackets; no camera, QR parser or scanning implied."""
    for x, xs in ((x0, 1), (x1, -1)):
        for y, ys in ((y0, 1), (y1, -1)):
            tint = (255, 103, 184) if xs * ys == 1 else (101, 221, 255)
            draw.line((x, y, x + 22 * xs, y), fill=tint, width=5)
            draw.line((x, y, x, y + 22 * ys), fill=tint, width=5)
            draw.rectangle((x + xs * 4 - 2, y + ys * 4 - 2,
                            x + xs * 4 + 2, y + ys * 4 + 2), fill=(250, 248, 255))


def voucher(draw, p):
    arcade_card(draw, (44, 412, 316, 519), (255, 218, 127), (255, 163, 70),
                shadow=(2, 4), glow=(255, 244, 191))
    # Cut-out ticket notches at both sides, kept outside the printed copy.
    for x in (45, 314):
        draw.rectangle((x - 3, 450, x + 3, 465), fill=(6, 12, 48))
    draw.line((62, 442, 298, 442), fill=(230, 154, 73), width=1)
    draw.line((62, 496, 298, 496), fill=(230, 154, 73), width=1)
    p.pixel_text(draw, "MENANG = DAPAT DISKON", 180, 424, 2, fill=p.INK)
    p.pixel_text(draw, "RP 2.500", 180, 451, 4, fill=(236, 57, 127),
                 shadow=(255, 168, 125))
    p.pixel_text(draw, "UNTUK PHOTOBOOTH!", 180, 476, 2, fill=p.INK)
    p.pixel_text(draw, "SIMULASI - BELUM AKTIF", 180, 504, 1,
                 fill=(107, 52, 73))


def paint_polished_menu(screen, logo_path):
    """Paint the v2 Start/Scan frame without changing hit target geometry."""
    from . import meong_fly_painter as p
    if screen not in ("start", "scan"):
        raise ValueError("Batch A supports only Start/Scan")
    canvas = Image.new("RGBA", (p.W, p.H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)
    p.draw_common(draw, screen)
    if screen == "start":
        halo(draw)
        sparkle(draw, 41, 240, 4, p.GOLD)
        sparkle(draw, 331, 249, 3, p.CYAN)
        logo, _ = p.logo_parts(str(Path(logo_path)))
        p.place_art(canvas, logo, 27, 59, 306, 207)
        draw = ImageDraw.Draw(canvas)
        arcade_card(draw, (24, 274, 336, 398), p.PANEL, p.OUTLINE,
                    glow=(137, 112, 207))
        draw.rectangle((44, 290, 51, 297), fill=p.PINK)
        draw.rectangle((309, 378, 316, 385), fill=p.CYAN)
        p.pixel_text(draw, "MEONG FLY!", 180, 292, 4, fill=p.PURPLE,
                     shadow=(71, 36, 121))
        draw.line((93, 332, 267, 332), fill=(71, 68, 143), width=2)
        p.pixel_text(draw, "TERBANG DI LUAR ANGKASA", 180, 347, 2)
        p.pixel_text(draw, "DAN HINDARI ASTEROID!", 180, 370, 2)
        voucher(draw, p)
        arcade_button(draw, p.ACTIONS["start"]["game"], "MAIN GAME", "pink", p,
                      scale=3, icon="gamepad")
        arcade_button(draw, p.ACTIONS["start"]["photo"], "LANGSUNG FOTO", "cyan", p,
                      scale=2, icon="camera")
        p.pixel_text(draw, "DEMO - DISKON BELUM AKTIF", 180, 690, 1,
                     fill=(211, 205, 239))
    else:
        sparkle(draw, 51, 87, 5, (180, 143, 253))
        p.pixel_text(draw, "02 / VALIDASI DEMO", 180, 101, 1,
                     fill=(177, 157, 240))
        arcade_card(draw, (24, 135, 336, 450), p.PANEL, p.OUTLINE,
                    glow=(113, 96, 188))
        p.pixel_text(draw, "SCAN STRUK KAFE", 180, 155, 3)
        draw.line((71, 187, 289, 187), fill=(71, 69, 139), width=2)
        p.pixel_text(draw, "QR ASLI BELUM TERHUBUNG", 180, 198, 2,
                     fill=p.GOLD)
        p.pixel_text(draw, "PAKAI KODE DEMO DI BAWAH", 180, 223, 1,
                     fill=(220, 215, 255))
        arcade_card(draw, (96, 257, 264, 429), (237, 239, 253),
                    (194, 174, 229), shadow=(0, 2), glow=(255, 255, 255))
        # Real-looking finder patterns stay decorative, clearly labelled.
        p._fake_qr(draw, 117, 281, 6)
        scanner_corners(draw)
        p.pixel_text(draw, "ILUSTRASI QR", 180, 439, 1, fill=p.GOLD)
        p.pixel_text(draw, "KODE STRUK DEMO", 180, 455, 2, fill=p.WHITE)
        x, y, w, h = p.DEMO_ENTRY
        arcade_card(draw, (x, y, x+w, y+h), (246, 246, 255),
                    (150, 139, 209), shadow=(1, 2), glow=(255, 255, 255))
        draw.line((x+12, y+6, x+w-12, y+6), fill=(222, 221, 244), width=1)
        arcade_button(draw, p.ACTIONS["scan"]["validate"],
                      "VALIDASI DEMO 1X", "pink", p, scale=2)
        arcade_button(draw, p.ACTIONS["scan"]["back"], "KEMBALI", "dark", p,
                      scale=2)
        p.pixel_text(draw, "DEMO-123 / 1 KODE 1 PERMAINAN", 180, 691, 1,
                     fill=(213, 203, 243))
    return canvas
