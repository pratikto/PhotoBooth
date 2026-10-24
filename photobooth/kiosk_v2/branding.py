"""Display-only Meong Fly artwork in a shared native portrait brand lockup.

The camera PNG is decoded byte-for-byte from the read-only reference artwork.
No game/scanner module is imported, and original booth/QR logos are unchanged.
"""
from math import pi, sin
from pathlib import Path

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, PopMatrix, PushMatrix, Rectangle, Scale, Translate
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from .theme import CYAN, GOLD, PURPLE, rgba
from .pixel_type import BRAND_GLYPHS

CAMERA_ART = Path(__file__).parent / "assets" / "meong-fly-camera.png"


class PixelWordmark(Widget):
    """Native 5x7 title cells and offset shadow, matching the mini-game style."""

    text = StringProperty('MEONG')
    ink = StringProperty(PURPLE)
    shadow = StringProperty('#472479')
    font_size = NumericProperty(42)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._repaint = Clock.create_trigger(self._paint, -1)
        self.bind(pos=self._repaint, size=self._repaint, text=self._repaint,
                  ink=self._repaint, shadow=self._repaint, font_size=self._repaint)
        self._repaint()

    def _paint(self, *_args):
        self.canvas.clear()
        if not self.text or self.width <= 0 or self.height <= 0:
            return
        columns = len(self.text) * 6
        cell = min(self.width / columns, self.height / 8, self.font_size / 7)
        # Half-pixel steps also keep the compact caption legible after scaling.
        cell = max(.25, int(cell * 2) / 2)
        left = self.x + (self.width - columns * cell) / 2
        bottom = self.y + (self.height - 8 * cell) / 2
        cells = [(left + (index * 6 + x) * cell, bottom + (7 - y) * cell)
                 for index, letter in enumerate(self.text)
                 for y, row in enumerate(BRAND_GLYPHS[letter])
                 for x, bit in enumerate(row) if bit == '1']
        with self.canvas:
            Color(*rgba(self.shadow))
            for x, y in cells:
                Rectangle(pos=(x + cell, y - cell), size=(cell, cell))
            Color(*rgba(self.ink))
            for x, y in cells:
                stroke = min(dp(1), cell / 4) if cell >= 2 else 0
                Rectangle(pos=(x, y), size=(cell + stroke, cell))


class MeongLogo(FloatLayout):
    """Centered wordmark and the existing mascot flying above its lettering."""

    flight = NumericProperty(0)

    def __init__(self, *, hero=False, **kwargs):
        self.hero = hero
        self._flight_anim = None
        self._flight_direction = 1
        self._flight_active = True
        self._disposed = False
        self._flight_geometry = None
        super().__init__(**kwargs)
        self.art = Image(source=str(CAMERA_ART), fit_mode="contain", size_hint=(None, None))
        self.art.bind(texture=self._nearest)
        self._nearest(self.art, self.art.texture)
        # Flip this image's draw transform on the return flight. The shared
        # source texture stays immutable, including the game/QR/v1 artwork.
        with self.art.canvas.before:
            PushMatrix()
            self._pivot = Translate()
            self._direction = Scale(1, 1, 1)
            self._unpivot = Translate()
        with self.art.canvas.after:
            PopMatrix()
        self.wordmark = PixelWordmark(text='MEONG', size_hint=(None, None))
        self.caption = PixelWordmark(text='PHOTOBOOTH', ink=CYAN, shadow='#142951',
                                     size_hint=(None, None))
        for widget in (self.art, self.wordmark, self.caption):
            self.add_widget(widget)
        # Arrange after parent size/position aliases have settled for this frame.
        self._trigger_arrange = Clock.create_trigger(self._arrange, -1)
        self.bind(pos=self._trigger_arrange, size=self._trigger_arrange)
        self.bind(flight=self._fly, parent=self._trigger_arrange)
        self._trigger_arrange()

    @staticmethod
    def _nearest(_image, texture):
        if texture is not None:
            texture.mag_filter = texture.min_filter = "nearest"

    def _arrange(self, *_args):
        if self._disposed:
            return
        geometry = (*self.pos, *self.size)
        if ((geometry != self._flight_geometry or self.parent is None) and
                self._flight_anim is not None):
            self._flight_anim.cancel(self)
            self._flight_anim = None
        self._flight_geometry = geometry
        width, height = max(1, self.width), max(1, self.height)
        self.art.size = (height * .36 * 224 / 152, height * .36)
        self.wordmark.size = (width, height * .43)
        self.wordmark.pos = (self.x, self.y + height * .18)
        self.wordmark.font_size = min(dp(42), width / 5, height * .42)
        self.caption.size = (width, height * .20)
        self.caption.pos = (self.x, self.y)
        self.caption.font_size = min(dp(16), width / 14, height * .20)
        self._fly()
        self._start_flight()

    def _fly(self, *_args):
        if self._disposed:
            return
        self.art.pos = (self.x + self.flight * max(0, self.width - self.art.width),
                        self.y + self.height * .63 + sin(self.flight * pi * 6) * self.height * .01)
        self._pivot.x, self._pivot.y = self.art.center
        self._unpivot.x, self._unpivot.y = -self.art.center_x, -self.art.center_y
        self._direction.x = self._flight_direction

    def _start_flight(self):
        if (self._disposed or not self._flight_active or self.parent is None or
                self._flight_anim is not None):
            return
        target = 1 if self._flight_direction > 0 else 0
        distance = abs(target-self.flight) * max(1, self.width-self.art.width)
        self._flight_anim = Animation(flight=target, duration=max(.1, distance/dp(65)),
                                      t='linear', step=1/30)
        self._flight_anim.bind(on_complete=self._turn)
        self._flight_anim.start(self)

    def _turn(self, *_args):
        self._flight_anim = None
        self._flight_direction *= -1
        self._fly()
        self._start_flight()

    def set_active(self, active):
        self._flight_active = active
        if not active and self._flight_anim is not None:
            self._flight_anim.cancel(self)
            self._flight_anim = None
        elif active:
            self._start_flight()

    def dispose(self):
        self.set_active(False)
        self._disposed = True
        self._trigger_arrange.cancel()
