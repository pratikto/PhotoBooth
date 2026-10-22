"""Display-only Meong Fly artwork in a shared native portrait brand lockup.

The camera PNG is decoded byte-for-byte from the read-only reference artwork.
No game/scanner module is imported, and original booth/QR logos are unchanged.
"""
from pathlib import Path

from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from .theme import CYAN, GOLD, PURPLE, rgba

CAMERA_ART = Path(__file__).parent / "assets" / "meong-fly-camera.png"


class MeongLogo(FloatLayout):
    """One transparent camera-cat and legible wordmark, without a white tile."""

    def __init__(self, *, hero=False, **kwargs):
        self.hero = hero
        super().__init__(**kwargs)
        self.art = Image(source=str(CAMERA_ART), fit_mode="contain", size_hint=(None, None))
        self.art.bind(texture=self._nearest)
        self._nearest(self.art, self.art.texture)
        self.wordmark = Label(text="MEONG", bold=True, color=rgba(GOLD),
                              size_hint=(None, None))
        self.caption = Label(text="P H O T O B O O T H", color=rgba(CYAN),
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
            self.caption.font_size = min(dp(13), width / 22, height * .085)
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
            self.caption.font_size = min(dp(12), word_w / 19, height * .18)
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
