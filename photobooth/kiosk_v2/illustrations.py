"""Decorative, scalable pixel-arcade illustrations for the opt-in portrait GUI.

All four tutorial symbols are simple Kivy vector artwork. They intentionally
contain no customer data, payment code, QR payload, or new thermal print master.
Drawing happens only when an icon's bounds change, not on every animation tick.
"""

from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.widget import Widget

from .theme import CYAN, GOLD, INK, PANEL, PANEL_EDGE, PINK, PURPLE, WHITE, rgba


class TutorialIcon(Widget):
    """A lightweight image-like icon that still renders without PNG assets."""

    KINDS = frozenset({"template", "payment", "camera", "print"})

    def __init__(self, kind, **kwargs):
        if kind not in self.KINDS:
            raise ValueError("Unsupported tutorial illustration: " + str(kind))
        self.kind = kind
        super().__init__(**kwargs)
        self.bind(pos=self._paint, size=self._paint)
        self._paint()

    def _paint(self, *_args):
        self.canvas.before.clear()
        if self.width <= 0 or self.height <= 0:
            return
        dimension = min(self.width, self.height, dp(96))
        left = self.center_x - dimension / 2
        bottom = self.center_y - dimension / 2

        def box(x, y, w, h, color):
            Color(*rgba(color))
            Rectangle(
                pos=(left + x * dimension, bottom + y * dimension),
                size=(w * dimension, h * dimension),
            )

        with self.canvas.before:
            Color(*rgba(PANEL_EDGE))
            RoundedRectangle(pos=(left, bottom), size=(dimension, dimension),
                             radius=[dp(12)])
            Color(*rgba(PANEL))
            RoundedRectangle(pos=(left + dp(3), bottom + dp(3)),
                             size=(max(0, dimension - dp(6)),
                                   max(0, dimension - dp(6))),
                             radius=[dp(10)])

            if self.kind == "template":
                # Three portrait frames + final non-scannable QR placeholder.
                box(.34, .12, .43, .76, WHITE)
                box(.26, .19, .43, .69, PURPLE)
                box(.32, .13, .43, .74, WHITE)
                for yy in (.63, .43, .23):
                    box(.37, yy, .33, .17, CYAN)
                    box(.41, yy + .05, .11, .06, PINK)
                box(.47, .16, .14, .035, INK)
                box(.39, .82, .18, .025, GOLD)
            elif self.kind == "payment":
                box(.28, .14, .44, .73, WHITE)
                box(.33, .23, .34, .52, INK)
                for x, y in ((.37, .64), (.55, .64), (.37, .46),
                             (.55, .46), (.44, .55), (.50, .38)):
                    box(x, y, .075, .075, WHITE)
                box(.40, .18, .19, .035, CYAN)
                box(.43, .79, .13, .03, PINK)
            elif self.kind == "camera":
                box(.15, .32, .70, .44, WHITE)
                box(.27, .73, .27, .11, WHITE)
                box(.64, .78, .12, .035, GOLD)
                Color(*rgba(CYAN))
                Ellipse(pos=(left + .34 * dimension, bottom + .38 * dimension),
                        size=(.33 * dimension, .33 * dimension))
                Color(*rgba(INK))
                Line(circle=(left + .505 * dimension, bottom + .545 * dimension,
                             .12 * dimension), width=dp(3))
                Color(*rgba(PINK))
                Ellipse(pos=(left + .18 * dimension, bottom + .66 * dimension),
                        size=(.055 * dimension, .055 * dimension))
            else:
                box(.18, .53, .65, .28, PURPLE)
                box(.25, .67, .46, .21, WHITE)
                box(.26, .36, .45, .30, WHITE)
                for yy in (.53, .45):
                    box(.31, yy, .33, .055, CYAN)
                box(.36, .25, .23, .17, WHITE)
                # Symbolic, intentionally non-scannable QR mark.
                for x, y in ((.39, .31), (.50, .31), (.39, .39), (.50, .39)):
                    box(x, y, .055, .055, INK)
                box(.68, .68, .075, .06, GOLD)
