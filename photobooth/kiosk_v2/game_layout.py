"""Reflow the original 360×720 artwork without stretching its pixel glyphs.

The standalone painter is a fixed poster, so its working renderer cannot
resize individual controls. This adapter extracts its existing UI into cached
patches, widens only plain card material, and uses one background over the
whole stage. Physics, sprite composition and animation remain upstream-owned.
"""

from dataclasses import dataclass
from functools import lru_cache

from PIL import Image, ImageChops, ImageDraw

from photobooth.meong_fly_painter import ACTIONS, DEMO_ENTRY, draw_common, paint_static_screen


@dataclass(frozen=True)
class Layout:
    width: float
    height: float
    scene: str

    @property
    def scale(self):
        return max(.001, min(self.width / 360, self.height / 720))

    @property
    def extra(self):
        return self.width / self.scale - 360, self.height / self.scale - 720

    def world_x(self, x):
        """Translate the complete original world without warping its motion.

        Center the complete playable world inside the continuous sky. Right
        alignment pushed Meong toward the far edge on wide windows (BUG-016).
        HUD and menus can still reflow independently. A shared translation
        preserves speed, wave spacing, sprites and reaction time everywhere,
        including the approach and exit, at every window size (BUG-015).
        """
        return x + self.extra[0] / 2

    def rect(self, box):
        x, y, w, h = box
        ew, eh = self.extra
        if tuple(box) == (0, 0, 360, 720):
            return 0, 0, 360 + ew, 720 + eh
        if self.scene == 'game':
            if y < 100:
                # Pause stays left, target stays right; score remains central.
                x += ew if x >= 240 else ew / 2 if x >= 70 else 0
            elif y >= 630:
                x += 0 if w == 360 else ew / 2
                w += ew if w == 360 else 0
                y += eh
            elif w == 360:
                x = 0
                w += ew
                y += eh / 2
            elif y == 309 and h == 48:  # Existing PAUSED glyph texture.
                x += ew / 2
                y += eh / 2
            else:
                x = self.world_x(x)
                y += eh / 2
        else:
            expanded = list(ACTIONS.get(self.scene, {}).values())
            if self.scene == 'scan':
                expanded += [DEMO_ENTRY, (30, 595, 300, 28)]
            if tuple(box) in expanded:
                w += ew
            else:
                x += ew / 2
            # A panel and everything inside it share a vertical anchor.
            y += self.menu_offset(box)
        return x, y, w, h

    def menu_offset(self, box):
        _, eh = self.extra
        x, y, w, h = box
        if self.scene == 'lost' and 240 < y < 385:
            return eh * 264 / 720
        for (gx, gy, gw, gh), _, _ in GROUPS.get(self.scene, ()):
            if gx <= x+w/2 <= gx+gw and gy <= y+h/2 <= gy+gh:
                return eh * gy / 720
        return eh * y / 720

    def patch(self, box, widen=False, anchor=None):
        x, y, w, h = box
        ew, eh = self.extra
        if anchor == 'left':
            return x, y, w, h
        if anchor == 'right':
            return x + ew, y, w, h
        if anchor == 'hud':
            return x + ew / 2, y, w, h
        if anchor == 'footer':
            return x, y + eh, w + ew, h
        if anchor == 'field':
            return x, y + eh / 2, w + ew, h
        return (x if widen else x + ew / 2, y + eh * y / 720,
                w + ew if widen else w, h)


# Original art groups, including their shadows. Values are source XYWH.
# Wide patches preserve their central glyphs and both decorative edge caps.
GROUPS = {
    'start': [((20, 65, 320, 345), False, None),
              ((33, 418, 296, 45), True, None),
              ((35, 466, 294, 72), True, None),
              ((32, 539, 299, 65), True, None),
              ((32, 609, 299, 65), True, None),
              ((25, 682, 310, 25), False, None)],
    'scan': [((20, 95, 320, 22), False, None),
             ((20, 132, 323, 320), True, None),
             ((35, 450, 290, 24), False, None),
             ((42, 475, 278, 55), True, None),
             ((42, 537, 279, 65), True, None),
             ((60, 624, 242, 60), True, None),
             ((20, 687, 320, 25), False, None)],
    'won': [((15, 106, 330, 307), False, None),
            ((32, 421, 299, 122), True, None),
            ((30, 560, 301, 74), True, None)],
    'lost': [((28, 103, 304, 124), False, None),
             ((41, 390, 281, 110), True, None),
             ((25, 509, 310, 26), False, None),
             ((30, 562, 301, 74), True, None),
             ((30, 645, 300, 30), False, None)],
    'game': [((12, 15, 55, 54), False, 'left'),
             ((87, 14, 149, 79), False, 'hud'),
             ((242, 14, 110, 79), False, 'right'),
             ((16, 105, 329, 3), True, 'field'),
             ((16, 585, 329, 3), True, 'field'),
             ((0, 635, 360, 85), True, 'footer')],
}


@lru_cache(maxsize=5)
def scene_art(scene, logo_path):
    """Original pixels, prepared once, never regenerated on resize/frame ticks."""
    source = paint_static_screen(scene, logo_path)
    if scene == 'game':
        # This original-art crop contains only sky, nebulae and planets.
        background = source.crop((0, 108, 360, 584))
        base = Image.new('RGBA', source.size)
        d = ImageDraw.Draw(base)
        for y in range(720):
            d.line((0, y, 360, y), fill=(4, 10 + int(y/150), 36 + int(y/40), 255))
    else:
        background = Image.new('RGBA', source.size, (0, 0, 0, 255))
        draw_common(ImageDraw.Draw(background), scene)
        base = background
    # Alpha out only the old sky, leaving the original cards/glyphs untouched.
    delta = ImageChops.difference(source.convert('RGB'), base.convert('RGB'))
    r, g, b = delta.split()
    mask = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v else 0)
    foreground = source.copy()
    foreground.putalpha(mask)
    patches = []
    for box, wide, anchor in GROUPS[scene]:
        x, y, w, h = box
        # The game footer has its own original solid material, not the gradient.
        art = source if anchor in ('footer', 'field') else foreground
        patches.append((box, wide, anchor, art.crop((x, y, x+w, y+h))))
    return background, tuple(patches)


def horizontal_slices(width, extra, cap=12):
    """Five slices: unchanged caps/glyphs and two expandable plain-fill strips."""
    if extra <= .001:
        return [(0, width, 0, width)]
    return [(0, cap, 0, cap),
            (cap, 1, cap, 1 + extra / 2),
            (cap + 1, width - 2*cap - 2, cap + 1 + extra / 2, width - 2*cap - 2),
            (width-cap-1, 1, width-cap-1 + extra / 2, 1 + extra / 2),
            (width-cap, cap, width-cap + extra, cap)]
