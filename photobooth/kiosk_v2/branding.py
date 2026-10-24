"""Display-only Meong Fly artwork in a shared native portrait brand lockup.

The read-only game artwork/compositor supplies the decorative flying camera.
No game, scanner or real printer is started; original booth/QR logos are unchanged.
"""
from math import pi, sin
from pathlib import Path

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, PopMatrix, PushMatrix, Rectangle, Rotate
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

from .theme import CYAN, GOLD, PURPLE, rgba
from .pixel_type import BRAND_GLYPHS
from .brand_flight import FlyingMeongArt

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
    """Original mascot flies into a centered wordmark, giving it one playful spin."""

    flight = NumericProperty(0)
    spin = NumericProperty(0)

    def __init__(self, *, hero=False, **kwargs):
        self.hero = hero
        self._flight_anim = None
        self._spin_anim = None
        self._spin_target = 0
        self._hit_this_pass = False
        self._flight_direction = 1
        self._flight_active = True
        self._disposed = False
        self._flight_geometry = None
        self._pose_time = None
        super().__init__(**kwargs)
        self.art = FlyingMeongArt(size_hint=(None, None))
        self.wordmark = PixelWordmark(text='MEONG', size_hint=(None, None))
        self.caption = PixelWordmark(text='PHOTOBOOTH', ink=CYAN, shadow='#142951',
                                     size_hint=(None, None))
        self.lettering = FloatLayout(size_hint=(None, None))
        # Rotate the existing native glyphs as one sign. A vertical-axis flip
        # fits compact headers throughout the turn; no raster uploads per tick.
        with self.lettering.canvas.before:
            PushMatrix()
            self._word_spin = Rotate(axis=(0, 1, 0))
            self._word_tilt = Rotate()
        with self.lettering.canvas.after:
            PopMatrix()
        self.lettering.add_widget(self.wordmark)
        self.lettering.add_widget(self.caption)
        self.add_widget(self.lettering)
        self.add_widget(self.art)  # Meong passes in front of the lettering.
        # Arrange after parent size/position aliases have settled for this frame.
        self._trigger_arrange = Clock.create_trigger(self._arrange, -1)
        self.bind(pos=self._trigger_arrange, size=self._trigger_arrange)
        self.bind(flight=self._fly, parent=self._trigger_arrange)
        self.bind(spin=self._rotate_words)
        self._trigger_arrange()

    def _arrange(self, *_args):
        if self._disposed:
            return
        geometry = (*self.pos, *self.size)
        if ((geometry != self._flight_geometry or self.parent is None) and
                self._flight_anim is not None):
            self._flight_anim.cancel(self)
            self._flight_anim = None
        if geometry != self._flight_geometry:
            self.art.reset_geometry()
        self._flight_geometry = geometry
        self._pose_time = Clock.get_time()
        width, height = max(1, self.width), max(1, self.height)
        cell = max(.5, int(min(dp(6), height * .56 / 8, width / 50) * 2) / 2)
        caption_cell = max(.5, int(min(dp(16)/7, cell * .36) * 2) / 2)
        self.lettering.size = (30 * cell, 8 * (cell + caption_cell))
        self.lettering.center = self.center
        self.wordmark.size = (self.lettering.width, 8 * cell)
        self.wordmark.pos = (self.lettering.x, self.lettering.y + 8 * caption_cell)
        self.wordmark.font_size = 7 * cell
        self.caption.size = (self.lettering.width, 8 * caption_cell)
        self.caption.pos = self.lettering.pos
        self.caption.font_size = 7 * caption_cell
        # Leave a real approach on both sides even in a tall/narrow header;
        # otherwise the first frame can already overlap the lettering and miss
        # its contact event. Keep the original sprite's proportions.
        self.art.max_unit = max(.01, (self.lettering.x-self.x-dp(8)) / 123)
        self.art.pos, self.art.size = self.pos, self.size
        self._rotate_words()
        self._fly(detect_impact=False)
        if self.parent is None and self._spin_anim is not None:
            self._spin_anim.cancel(self)
            self._spin_anim = None
        self._start_flight()
        self._start_spin()

    def _fly(self, *_args, detect_impact=True):
        if self._disposed:
            return
        x, _, w, _ = self.art.body_box
        previous = x if self._flight_direction < 0 else x+w
        now = Clock.get_time()
        dt = (max(0, now-self._pose_time) if self._pose_time is not None and
              detect_impact and self._flight_active else 0)
        self._pose_time = now
        self.art.advance(self.flight, self._flight_direction, dt)
        x, _, w, _ = self.art.body_box
        # The wordmark occupies its actual pixel grid width, so contact is
        # measured at the lettering rather than an invisible full-width box.
        crossed = (previous <= self.lettering.x < x+w if self._flight_direction > 0
                   else previous >= self.lettering.right > x)
        if (detect_impact and crossed and not self._hit_this_pass and
                self._flight_active and self.parent is not None):
            self._hit_wordmark()

    def _hit_wordmark(self):
        self._hit_this_pass = True
        if self._spin_anim is not None:
            self._spin_anim.cancel(self)
            self._spin_anim = None
        self.spin = 0
        self._spin_target = 360 * self._flight_direction
        self._start_spin()

    def _rotate_words(self, *_args):
        for rotation in (self._word_spin, self._word_tilt):
            rotation.origin = (*self.lettering.center, 0)
        self._word_spin.angle = self.spin
        self._word_tilt.angle = sin(self.spin * pi / 180) * 4

    def _start_spin(self):
        if (self._disposed or not self._flight_active or self.parent is None or
                self._spin_anim is not None or self._spin_target == 0):
            return
        remaining = abs(self._spin_target - self.spin) / 360
        self._spin_anim = Animation(spin=self._spin_target, duration=max(.02, .65 * remaining),
                                    t='out_cubic', step=1/30)
        self._spin_anim.bind(on_complete=self._settle_words)
        self._spin_anim.start(self)

    def _settle_words(self, *_args):
        self._spin_anim = None
        self._spin_target = 0
        self.spin = 0

    def _start_flight(self):
        if (self._disposed or not self._flight_active or self.parent is None or
                self._flight_anim is not None):
            return
        target = 1 if self._flight_direction > 0 else 0
        distance = abs(target-self.flight) * max(1, self.art.travel)
        self._flight_anim = Animation(flight=target, duration=max(.1, distance/dp(65)),
                                      t='linear', step=1/30)
        self._flight_anim.bind(on_complete=self._turn)
        self._flight_anim.start(self)

    def _turn(self, *_args):
        self._flight_anim = None
        self._flight_direction *= -1
        self._hit_this_pass = False
        self._fly(detect_impact=False)
        self._start_flight()

    def set_active(self, active):
        self._flight_active = active
        self._pose_time = Clock.get_time()
        if not active:
            for name in ('_flight_anim', '_spin_anim'):
                animation = getattr(self, name)
                if animation is not None:
                    animation.cancel(self)
                    setattr(self, name, None)
        else:
            self._start_flight()
            self._start_spin()

    def dispose(self):
        self.set_active(False)
        self._disposed = True
        self._trigger_arrange.cancel()
        self.art.dispose()
