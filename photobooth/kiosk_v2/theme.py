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
            for index in range(63):
                x = ((index * 37 + 11) % 103) / 103
                y = ((index * 59 + 23) % 101) / 101
                Color(*rgba(CYAN if index % 8 == 0 else PURPLE if index % 11 == 0 else WHITE,
                            .50 if index % 3 else .85))
                size = dp(3 if index % 9 == 0 else 2)
                Rectangle(pos=(self.x + x * self.width, self.y + y * self.height),
                          size=(size, size))
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


class ArcadeButton(Button):
    """Large touch-safe CTA with consistent press and disabled appearance."""

    def __init__(self, text, *, variant="primary", height=62, **kwargs):
        self.variant = variant
        super().__init__(
            text=text, size_hint_y=None, height=dp(height),
            background_normal="", background_down="",
            font_size=dp(18), bold=True,
            color=rgba(INK if variant in {"primary", "secondary"} else WHITE),
            **kwargs,
        )
        self.bind(state=self._recolor, disabled=self._recolor)
        self._recolor()

    def _recolor(self, *_args):
        color = BUTTON_COLORS[self.variant]
        self.background_color = rgba(
            "454764" if self.disabled else color,
            .65 if self.disabled else .76 if self.state == "down" else 1.0,
        )
        self.color = rgba(MUTED if self.disabled else
                          INK if self.variant in {"primary", "secondary"} else WHITE)


def text_label(text, *, size=16, height=36, color=WHITE, bold=False, align="center"):
    label = Label(
        text=text, size_hint_y=None, height=dp(height),
        font_size=dp(size), color=rgba(color), bold=bold,
        halign=align, valign="middle", shorten=False,
    )
    label.bind(size=lambda w, bounds: setattr(w, "text_size", (max(10, bounds[0] - dp(8)),
                                                              bounds[1])))
    return label
