"""Small native illustrations and page-owned motion for the MEONG interface.

All artwork here is an instruction symbol (camera, receipt, hand, phone), not a
replacement mascot or a fake payment QR. Vector geometry scales cleanly on the
kiosk and needs no emoji font, internet connection, or raster asset downloads.
One 24 Hz Clock event serves the currently visible page. Retiring that page
cancels its event and animations, preventing an unattended booth from slowly
accumulating timers.
"""

import math
import os
import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle, Triangle
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

from photobooth.ui_brand import BLUE, CYAN, EDGE, INK, PINK, SOFT, WHITE

PURPLE = (.65, .30, .94, 1)
CORAL = (1, .48, .38, 1)
LEMON = (1, .89, .35, 1)
TEAL = (.13, .72, .68, 1)


class MotionScope:
    """Own only visual timing; never schedule a shutter or change an order."""

    def __init__(self):
        self.enabled = os.environ.get("PHOTOBOOTH_ANIMATIONS", "1").lower() not in {"0", "false", "no"}
        self.widgets = []
        self._entry = []
        self._event = None
        self._elapsed = 0.0
        self.retired = False

    def add(self, widget):
        """Register an illustration/dial with this page's shared animation clock."""
        self.widgets.append(widget)
        if self.enabled and self._event is None:
            self._event = Clock.schedule_interval(self._tick, 1 / 24)
        return widget

    def enter(self, widget):
        """Use a short fade without moving touch targets or delaying input."""
        if self.enabled:
            widget.opacity = .86
            Animation(opacity=1, duration=.22, t="out_quad").start(widget)
            self._entry.append(widget)

    def _tick(self, dt):
        if self.retired:
            return False
        self._elapsed += min(dt, .1)
        for widget in self.widgets:
            widget.phase = (self._elapsed / 2.4) % 1
        return True

    def retire(self):
        """Release the entire previous page before the controller rebuilds it."""
        self.retired = True
        if self._event is not None:
            self._event.cancel()
            self._event = None
        for widget in self._entry + self.widgets:
            Animation.cancel_all(widget)
        self._entry.clear()
        self.widgets.clear()


class GuideGlyph(Widget):
    """A friendly, low-detail pictogram with a subtle moving accent."""

    phase = NumericProperty(0)
    kind = StringProperty("camera")

    def __init__(self, kind="camera", **kwargs):
        super().__init__(**kwargs)
        self.kind = kind
        self.bind(size=self._draw, pos=self._draw, phase=self._draw, kind=self._draw)
        self._draw()

    def _draw(self, *_args):
        """Draw in a normalized 100-unit square so geometry retains its ratio."""
        self.canvas.clear()
        scale = max(0, min(self.width, self.height)) / 100
        x, y = self.center_x - 50 * scale, self.center_y - 50 * scale
        wobble = math.sin(self.phase * math.tau)
        def rect(px, py, width, height, color, radius=5):
            Color(*color)
            RoundedRectangle(pos=(x + px * scale, y + py * scale),
                             size=(width * scale, height * scale), radius=[radius * scale])
        def circle(px, py, radius, color):
            Color(*color)
            Ellipse(pos=(x + (px - radius) * scale, y + (py - radius) * scale),
                    size=(radius * 2 * scale, radius * 2 * scale))
        def stroke(points, color=BLUE, width=2):
            Color(*color)
            Line(points=[value for px, py in points for value in
                         (x + px * scale, y + py * scale)], width=max(.6, width * scale),
                 cap="round", joint="round")
        def photo(px, py, color):
            rect(px, py, 35, 50, WHITE, 4)
            rect(px + 4, py + 12, 27, 33, color, 2)
            circle(px + 22, py + 35, 4, LEMON)
            Color(*WHITE)
            Triangle(points=(x + (px + 5) * scale, y + (py + 14) * scale,
                             x + (px + 17) * scale, y + (py + 30) * scale,
                             x + (px + 30) * scale, y + (py + 14) * scale))
        with self.canvas:
            if self.kind == "frames":
                circle(50, 49, 41, SOFT)
                photo(15, 25, PINK)
                photo(43, 17 + wobble * 2, PURPLE)
                circle(76, 26, 12, BLUE)
                stroke(((71, 26), (75, 22), (82, 30)), WHITE, 2.4)
            elif self.kind == "pay":
                circle(50, 48, 42, CYAN)
                rect(29, 9, 43, 79, INK, 7)
                rect(33, 18, 35, 63, WHITE, 4)
                for px, py in ((38, 59), (52, 59), (38, 45)):
                    rect(px, py, 11, 11, BLUE, 1)
                    rect(px + 3, py + 3, 5, 5, WHITE, 0)
                rect(52, 45, 10, 10, PURPLE, 1)
                stroke(((36, 31 + wobble * 5), (65, 31 + wobble * 5)), TEAL, 2)
                circle(72, 22, 13, TEAL)
                stroke(((66, 22), (70, 18), (79, 27)), WHITE, 2.4)
            elif self.kind in {"camera", "effects"}:
                circle(50, 49, 40, (1, .93, .78, 1))
                rect(15, 25, 69, 48, PURPLE, 9)
                rect(29, 70, 27, 10, PURPLE, 3)
                circle(49, 49, 21, WHITE)
                circle(49, 49, 16, BLUE)
                circle(49, 49, 9, INK)
                circle(44, 54, 4, CYAN)
                rect(68, 61, 10, 6, LEMON, 2)
                stroke(((81, 82), (81, 94)), CORAL, 2)
                stroke(((75, 88), (87, 88)), CORAL, 2)
                circle(16, 80 + wobble * 3, 3, PINK)
            elif self.kind in {"result", "review", "check"}:
                circle(50, 48, 42, (1, .91, .95, 1))
                rect(15, 29, 70, 42, BLUE, 8)
                rect(25, 61, 50, 22, SOFT, 4)
                rect(26, 9 + wobble * 2, 48, 48, WHITE, 3)
                rect(33, 31 + wobble * 2, 34, 18, CYAN, 2)
                rect(33, 14 + wobble * 2, 34, 11, PINK, 2)
                circle(75, 59, 3, LEMON)
                if self.kind in {"review", "check"}:
                    circle(75, 23, 14, TEAL)
                    stroke(((68, 23), (73, 18), (82, 28)), WHITE, 2.5)
            elif self.kind == "hand":
                circle(50, 48, 41, SOFT)
                rect(32, 15, 39, 40, PINK, 12)
                for px, bottom, top in ((31, 42, 72), (41, 49, 84), (51, 49, 89), (61, 47, 81)):
                    rect(px, bottom, 9, top - bottom, PINK, 4)
                stroke(((35, 36), (23, 50), (19, 48), (27, 30), (39, 21)), PINK, 4)
                stroke(((78, 59), (84, 63), (86, 70)), BLUE, 2)
            elif self.kind == "gear":
                circle(50, 50, 24, BLUE)
                for index in range(8):
                    angle = index * math.pi / 4
                    stroke(((50 + 21 * math.cos(angle), 50 + 21 * math.sin(angle)),
                            (50 + 32 * math.cos(angle), 50 + 32 * math.sin(angle))), BLUE, 7)
                circle(50, 50, 12, WHITE)
            elif self.kind == "music":
                stroke(((40, 29), (40, 75), (73, 82), (73, 37)), PURPLE, 5)
                stroke(((40, 64), (73, 71)), PURPLE, 5)
                circle(30, 28, 13, PURPLE)
                circle(63, 36, 13, PURPLE)
            elif self.kind == "tap":
                circle(49, 55, 29 + wobble * 2, CYAN)
                circle(49, 55, 18, BLUE)
                stroke(((51, 24), (51, 53), (58, 53), (58, 37), (72, 32), (69, 15)), PINK, 6)
            else:
                circle(50, 50, 30, SOFT)
                stroke(((33, 50), (45, 38), (68, 63)), BLUE, 4)


class CountdownDial(FloatLayout):
    """A rotating circular sweep around the existing readable countdown Label."""

    phase = NumericProperty(0)

    def __init__(self, label, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.seconds = None
        self._tick_at = time.monotonic()
        self.add_widget(label)
        label.pos_hint = {"x": 0, "y": 0}
        self.bind(size=self._draw, pos=self._draw, phase=self._draw)

    def set_seconds(self, seconds):
        """Visual interpolation follows, and never owns, the controller timer."""
        self.seconds = max(0, int(seconds))
        self._tick_at = time.monotonic()
        Animation.cancel_all(self.label, "font_size")
        if os.environ.get("PHOTOBOOTH_ANIMATIONS", "1").lower() not in {"0", "false", "no"}:
            (Animation(font_size=dp(52), duration=.08)
             + Animation(font_size=dp(44), duration=.16, t="out_quad")).start(self.label)
        self._draw()

    def _draw(self, *_args):
        self.canvas.before.clear()
        radius = max(1, min(self.width, self.height) * .39)
        angle = self.phase * 360
        elapsed = min(1, max(0, time.monotonic() - self._tick_at))
        fraction = .18 if self.seconds is None else max(0, (self.seconds - elapsed) / 5)
        with self.canvas.before:
            Color(*EDGE)
            Line(circle=(*self.center, radius), width=dp(2))
            Color(*(PURPLE if self.seconds is None else BLUE))
            Line(circle=(*self.center, radius, angle, angle + max(8, fraction * 360)),
                 width=dp(4), cap="round")
            dot_angle = math.radians(90 - angle)
            Color(*TEAL)
            Ellipse(pos=(self.center_x + math.cos(dot_angle) * radius - dp(4),
                         self.center_y + math.sin(dot_angle) * radius - dp(4)),
                    size=(dp(8), dp(8)))


class FlashEffect(EventDispatcher):
    """A brief screen overlay that survives the immediate post-capture rebuild."""

    alpha = NumericProperty(0)

    def __init__(self, target):
        super().__init__()
        self.target = target
        with target.canvas.after:
            self._color = Color(1, 1, 1, 0)
            self._rectangle = Rectangle(pos=target.pos, size=target.size)
        self.bind(alpha=self._paint)
        target.bind(pos=self._paint, size=self._paint)

    def _paint(self, *_args):
        self._color.a = self.alpha
        self._rectangle.pos, self._rectangle.size = self.target.pos, self.target.size

    def pulse(self):
        """A single quiet flash; continuous flashing is deliberately avoided."""
        Animation.cancel_all(self)
        (Animation(alpha=.22, duration=.04) + Animation(alpha=0, duration=.20)).start(self)

    def close(self):
        Animation.cancel_all(self)
        self.alpha = 0
