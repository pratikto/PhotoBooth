"""Display-only Meong Fly artwork in a shared native portrait brand lockup.

The camera PNG is decoded byte-for-byte from the read-only reference artwork.
No game/scanner module is imported, and original booth/QR logos are unchanged.
"""
from pathlib import Path

from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
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
    """One transparent camera-cat and legible wordmark, without a white tile."""

    def __init__(self, *, hero=False, **kwargs):
        self.hero = hero
        super().__init__(**kwargs)
        self.art = Image(source=str(CAMERA_ART), fit_mode="contain", size_hint=(None, None))
        self.art.bind(texture=self._nearest)
        self._nearest(self.art, self.art.texture)
        self.wordmark = PixelWordmark(text='MEONG', size_hint=(None, None))
        self.caption = PixelWordmark(text='PHOTOBOOTH', ink=CYAN, shadow='#142951',
                                     size_hint=(None, None))
        for widget in (self.art, self.wordmark, self.caption):
            self.add_widget(widget)
        # Arrange after parent size/position aliases have settled for this frame.
        self._trigger_arrange = Clock.create_trigger(self._arrange, -1)
        self.bind(pos=self._trigger_arrange, size=self._trigger_arrange)
        self._trigger_arrange()

    @staticmethod
    def _nearest(_image, texture):
        if texture is not None:
            texture.mag_filter = texture.min_filter = "nearest"

    def _arrange(self, *_args):
        width, height = max(1, self.width), max(1, self.height)
        center_x, center_y = self.x + width / 2, self.y + height / 2
        if self.hero:
            art_h = min(height * .64, width * .60)
            art_w = art_h * 224 / 152
            self.art.size = (art_w, art_h)
            self.art.pos = (center_x - art_w / 2, self.y + height * .33)
            self.wordmark.size = (width, height * .20)
            self.wordmark.pos = (self.x, self.y + height * .12)
            self.wordmark.font_size = min(dp(48), width / 4.5, height * .15)
            self.caption.size = (width, height * .11)
            self.caption.pos = (self.x, self.y + height * .02)
            self.caption.font_size = min(dp(16), width / 15, height * .10)
        else:
            art_h = min(height * .95, width * .31)
            art_w = art_h * 224 / 152
            word_w = max(1, min(dp(230), width - art_w - dp(12)))
            left = center_x - (art_w + dp(12) + word_w) / 2
            self.art.size = (art_w, art_h)
            self.art.pos = (left, center_y - art_h / 2)
            self.wordmark.size = (word_w, height * .58)
            self.wordmark.pos = (left + art_w + dp(12), self.y + height * .32)
            self.wordmark.font_size = min(dp(42), word_w / 3.8, height * .42)
            self.caption.size = (word_w, height * .27)
            self.caption.pos = (self.wordmark.x, self.y + height * .10)
            self.caption.font_size = min(dp(16), word_w / 10, height * .22)
        # The aura and glints are native decoration behind the immutable art.
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*rgba(PURPLE, .12))
            Ellipse(pos=(self.art.x, self.art.y + self.art.height * .12),
                    size=(self.art.width, self.art.height * .76))
            Color(*rgba(CYAN, .75))
            for x, y in ((self.art.x + self.art.width * .12, self.art.top - dp(5)),
                         (self.art.right - dp(6), self.art.y + self.art.height * .22)):
                Rectangle(pos=(x, y), size=(dp(3), dp(3)))
