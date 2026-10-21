"""Portrait-first Pixel Arcade Space design primitives.

All layouts/components in this package are newly authored for GUI v2. Only
approved logo and thermal template art are reused; no legacy page widgets.
"""

from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout

SPACE = "#050C2F"
PANEL = "#0B1543"
PANEL_EDGE = "#57499A"
INK = "#070D26"
WHITE = "#F8F8FF"
PINK = "#FF55AB"
CYAN = "#58D1FF"
GOLD = "#FFDC78"
PURPLE = "#B385FF"
MUTED = "#B9BFDE"

BUTTON_COLORS = {
    "primary": PINK,
    "secondary": CYAN,
    "tertiary": PANEL_EDGE,
    "muted": "#454764",
}


def rgba(hex_color, alpha=1.0):
    value = hex_color.strip("#")
    if len(value) != 6:
        raise ValueError("Theme color must have six hexadecimal digits.")
    return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)) + (alpha,)


class Starfield(FloatLayout):
    """Static pixel stars; repaint only on resize, no texture creation per frame."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._paint, size=self._paint)
        self._paint()

    def _paint(self, *_args):
        # Clear only the background layer so child touch targets are preserved.
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*rgba(SPACE))
            Rectangle(pos=self.pos, size=self.size)
            for index in range(87):
                x = ((index * 37 + 11) % 103) / 103
                y = ((index * 59 + 23) % 101) / 101
                color = CYAN if index % 8 == 0 else GOLD if index % 13 == 0 else (
                    PURPLE if index % 11 == 0 else WHITE
                )
                Color(*rgba(color, .52 if index % 3 else .86))
                px = self.x + x * self.width
                py = self.y + y * self.height
                if index % 12 == 0:
                    # Bright four-point pixel twinkles, never an animated CPU loop.
                    Rectangle(pos=(px, py), size=(dp(5), dp(5)))
                    Rectangle(pos=(px - dp(5), py + dp(1.5)),
                              size=(dp(15), dp(2)))
                    Rectangle(pos=(px + dp(1.5), py - dp(5)),
                              size=(dp(2), dp(15)))
                else:
                    size = dp(3 if index % 9 == 0 else 2)
                    Rectangle(pos=(px, py), size=(size, size))
            # Restrained planets/asteroids replace the v1-like solid side bars.
            # Keep ornaments near the edges, behind opaque interface panels.
            orbit = self.width * .25
            Color(*rgba("#7B4BA8", .38))
            Ellipse(pos=(self.x - orbit * .58, self.y + self.height * .67),
                    size=(orbit, orbit))
            Color(*rgba("#E774D6", .42))
            Line(ellipse=(self.x - orbit * .64, self.y + self.height * .70,
                          orbit * 1.13, orbit * .66), width=dp(3))
            Color(*rgba("#301D60", .65))
            Ellipse(pos=(self.x - orbit * .31, self.y + self.height * .77),
                    size=(orbit * .16, orbit * .16))
            Color(*rgba("#5488DD", .26))
            Ellipse(pos=(self.right - orbit * .55, self.y + self.height * .15),
                    size=(orbit, orbit))
            Color(*rgba("#8BE0FF", .38))
            Line(ellipse=(self.right - orbit * .68,
                          self.y + self.height * .18, orbit * 1.18,
                          orbit * .69), width=dp(2))
            # Tiny cratered rock at the upper side: cosmetic, not a game obstacle.
            Color(*rgba("#78709F", .54))
            Ellipse(pos=(self.right - orbit * .37, self.y + self.height * .87),
                    size=(orbit * .45, orbit * .45))
            Color(*rgba("#272955", .88))
            Ellipse(pos=(self.right - orbit * .27, self.y + self.height * .92),
                    size=(orbit * .12, orbit * .12))
            Ellipse(pos=(self.right - orbit * .05, self.y + self.height * .91),
                    size=(orbit * .10, orbit * .10))


class PixelCard(BoxLayout):
    """Pixel-stepped effect via opaque panel and offset shadow rectangles."""

    def __init__(self, *, fill=PANEL, padding=12, spacing=8, **kwargs):
        super().__init__(padding=dp(padding), spacing=dp(spacing), **kwargs)
        self._fill = fill
        self.bind(pos=self._paint, size=self._paint)
        self._paint()

    def _paint(self, *_args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*rgba(INK, .92))
            RoundedRectangle(pos=(self.x + dp(4), self.y - dp(4)),
                             size=self.size, radius=[dp(9)])
            Color(*rgba(PANEL_EDGE))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(9)])
            Color(*rgba(self._fill))
            RoundedRectangle(pos=(self.x + dp(3), self.y + dp(3)),
                             size=(max(0, self.width - dp(6)), max(0, self.height - dp(6))),
                             radius=[dp(7)])
            # Two small pixel corners add the approved arcade treatment
            # without obstructing children or ad/video media.
            if self.width >= dp(40) and self.height >= dp(36):
                Color(*rgba(PINK, .92))
                Rectangle(pos=(self.x + dp(12), self.top - dp(5)),
                          size=(dp(20), dp(3)))
                Color(*rgba(CYAN, .82))
                Rectangle(pos=(self.right - dp(5), self.top - dp(27)),
                          size=(dp(3), dp(17)))


class ArcadeButton(Button):
    """An accessible portrait-sized arcade CTA with pixel-corner accent.

    Text stays a native Kivy Button for keyboard/touch/accessibility bindings.
    The visual draw layer deliberately owns no touch events.
    """

    def __init__(self, text, *, variant="primary", height=62, **kwargs):
        if variant not in BUTTON_COLORS:
            raise ValueError("Unknown arcade button variant")
        self.variant = variant
        super().__init__(
            text=text, size_hint_y=None, height=dp(height),
            background_normal="", background_down="",
            background_color=(0, 0, 0, 0),
            font_size=dp(18), bold=True,
            color=rgba(INK if variant in {"primary", "secondary"} else WHITE),
            **kwargs,
        )
        self.bind(pos=self._paint, size=self._paint,
                  state=self._recolor, disabled=self._recolor)
        self._recolor()

    def _recolor(self, *_args):
        self.color = rgba(
            MUTED if self.disabled else
            INK if self.variant in {"primary", "secondary"} else WHITE
        )
        self._paint()

    def _paint(self, *_args):
        if self.width <= 0 or self.height <= 0:
            return
        fill = "#454764" if self.disabled else BUTTON_COLORS[self.variant]
        border = MUTED if self.disabled else CYAN if self.variant == "primary" else PINK
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*rgba(INK, .96))
            RoundedRectangle(pos=(self.x + dp(2), self.y - dp(4)),
                             size=self.size, radius=[dp(9)])
            Color(*rgba(border, .68))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(9)])
            Color(*rgba(fill, .57 if self.disabled else
                        .82 if self.state == "down" else 1.0))
            RoundedRectangle(pos=(self.x + dp(3), self.y + dp(3)),
                             size=(max(0, self.width - dp(6)),
                                   max(0, self.height - dp(6))),
                             radius=[dp(7)])
            if self.width > dp(48):
                Color(*rgba(WHITE, .53 if not self.disabled else .18))
                Rectangle(pos=(self.x + dp(12), self.top - dp(7)),
                          size=(min(dp(28), self.width / 4), dp(3)))
                Color(*rgba(INK, .30))
                Rectangle(pos=(self.right - dp(17), self.y + dp(8)),
                          size=(dp(8), dp(3)))


def text_label(text, *, size=16, height=36, color=WHITE, bold=False, align="center"):
    label = Label(
        text=text, size_hint_y=None, height=dp(height),
        font_size=dp(size), color=rgba(color), bold=bold,
        halign=align, valign="middle", shorten=False,
    )
    label.bind(size=lambda w, bounds: setattr(w, "text_size", (max(10, bounds[0] - dp(8)),
                                                              bounds[1])))
    return label
