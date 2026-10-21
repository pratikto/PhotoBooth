"""Demo-only tutorial and 12-layout handoff screens for FEAT-021.

Actual thermal templates remain in the production photobooth application.
These pictograms are explicitly a navigation preview, not print templates.
"""
from PIL import Image, ImageDraw


def photo_handoff_screen(screen, logo_path):
    from . import meong_fly_painter as p
    from .meong_fly_polish import arcade_card, arcade_button
    if screen not in ("tutorial", "layouts"):
        raise ValueError(screen)
    canvas = Image.new("RGBA", (p.W, p.H), (0, 0, 0, 255))
    d = ImageDraw.Draw(canvas)
    p.stars(d, seed=47 if screen == "tutorial" else 48)
    p.planet(d, 330, 62, 39, (143, 84, 207))
    p.asteroid(d, 40, 620, 23, seed=11)
    arcade_card(d, (19, 111, 341, 637), p.PANEL, p.OUTLINE)
    if screen == "tutorial":
        p.pixel_text(d, "TUTORIAL FOTO", 180, 141, scale=3, fill=p.CYAN)
        p.pixel_text(d, "SEBELUM PILIH LAYOUT", 180, 189, scale=2)
        # Three vertically arranged photo-taking instructions.
        for number, (y, title, sub) in enumerate(((252, "PILIH LAYOUT", "TENTUKAN DESAIN"),
                                                    (365, "AMBIL 3 FOTO", "IKUTI HITUNG MUNDUR"),
                                                    (478, "CETAK & QR", "UNDUH VIA DRIVE")), 1):
            arcade_card(d, (43, y-18, 317, y+80), (17, 36, 84),
                        (77, 91, 162), shadow=(0, 1))
            p.pixel_text(d, str(number), 75, y+7, scale=3, fill=p.GOLD)
            p.pixel_text(d, title, 197, y+3, scale=2, fill=p.WHITE)
            p.pixel_text(d, sub, 198, y+38, scale=1, fill=p.CYAN)
        arcade_button(d, (35, 644, 290, 55), "PILIH LAYOUT FOTO", "pink",
                      p, scale=2)
    else:
        p.pixel_text(d, "PILIH LAYOUT", 180, 133, scale=3, fill=p.CYAN)
        p.pixel_text(d, "12 PILIHAN DEMO", 180, 177, scale=2, fill=p.GOLD)
        # Fixed 3x4 grid. Each card previews a *generic* three-photo strip.
        # Do not imply these are the production 12 approved thermal assets.
        for index in range(12):
            col, row = index % 3, index // 3
            x, y = 40 + col * 99, 227 + row * 99
            arcade_card(d, (x, y, x+82, y+87),
                        (20, 40, 84), (84, 96, 160), shadow=(0, 1))
            for photo in range(3):
                yy = y + 8 + photo * 17
                d.rectangle((x+23, yy, x+59, yy+13),
                            fill=(112+index%4*19, 177-photo*19, 216),
                            outline=(242, 242, 255), width=1)
            d.rectangle((x+37, y+63, x+45, y+71), fill=p.GOLD)
            p.pixel_text(d, str(index+1), x+41, y+74, scale=1)
        p.pixel_text(d, "CONTOH SAJA - BELUM CETAK", 180, 648,
                     scale=1, fill=p.GOLD)
        p.pixel_text(d, "PILIH NOMOR UNTUK AKHIRI DEMO", 180, 680,
                     scale=1, fill=p.WHITE)
    return canvas


def layout_hitboxes():
    return {f"layout_{index+1}": (40+(index%3)*99, 227+(index//3)*99, 82, 87)
            for index in range(12)}
