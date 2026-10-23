"""Native, clipped Meong Fly display; fixed canvas objects, no per-frame uploads."""

from kivy.core.image import Image as CoreImage
from pathlib import Path
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stencilview import StencilView

from .branding import CAMERA_ART
from .game_engine import WIDTH, HEIGHT, CAT_X, CAT_LEFT, CAT_RIGHT, CAT_BOTTOM, CAT_TOP, GAP_HEIGHT, PIPE_WIDTH
from .theme import rgba, PANEL, PURPLE, GOLD, CYAN


class GameField(FloatLayout):
    def __init__(self, engine, flap, **kwargs):
        super().__init__(**kwargs)
        self.engine, self._flap, self._disposed = engine, flap, False
        self._asteroids = [CoreImage(str(Path(__file__).parent/'assets'/'p4'/f'asteroid-{i}.png')).texture
                           for i in range(5)]
        for texture in self._asteroids:
            texture.wrap = 'repeat'
            texture.mag_filter = texture.min_filter = 'nearest'
        self.arena = StencilView(size_hint=(None, None))
        self.add_widget(self.arena)
        with self.arena.canvas:
            Color(*rgba(PANEL))
            self.background = Rectangle()
            Color(*rgba(CYAN, .5))
            self.stars = [Rectangle() for _ in range(28)]
            self.rocks = []
            for i in range(8):
                # A faint belt exposes the whole rectangular collision field.
                Color(*rgba(PURPLE, .18))
                upper, lower = Rectangle(), Rectangle()
                Color(1, 1, 1, 1)
                upper_rocks = Rectangle(texture=self._asteroids[i%5])
                lower_rocks = Rectangle(texture=self._asteroids[(i+2)%5])
                self.rocks.append((upper, lower, upper_rocks, lower_rocks))
            Color(1, 1, 1, 1)
            self.cat = Rectangle(texture=CoreImage(str(CAMERA_ART)).texture)
        self.bind(size=self._fit, pos=self._fit)
        self._fit()

    def _fit(self, *_):
        self.scale = min(self.width / WIDTH, self.height / HEIGHT)
        self.arena.size = (WIDTH*self.scale, HEIGHT*self.scale)
        self.arena.pos = (self.center_x-self.arena.width/2, self.center_y-self.arena.height/2)
        self.draw()

    def draw(self):
        if self._disposed:
            return
        x, y = self.arena.pos
        s = self.scale
        self.background.pos, self.background.size = self.arena.pos, self.arena.size
        for i, star in enumerate(self.stars):
            star.pos = (x+((i*73+17)%WIDTH)*s, y+((i*137+29)%HEIGHT)*s)
            star.size = (2*s, 2*s)
        self.cat.pos = (x+(CAT_X-CAT_LEFT)*s, y+(HEIGHT-self.engine.y-CAT_TOP)*s)
        self.cat.size = ((CAT_LEFT+CAT_RIGHT)*s, (CAT_BOTTOM+CAT_TOP)*s)
        for i, (upper, lower, upper_rocks, lower_rocks) in enumerate(self.rocks):
            if i >= len(self.engine.pipes):
                upper.size = lower.size = upper_rocks.size = lower_rocks.size = (0, 0)
                continue
            pipe = self.engine.pipes[i]
            top_height = max(0, pipe.gap_y-GAP_HEIGHT/2)
            bottom_height = max(0, HEIGHT-pipe.gap_y-GAP_HEIGHT/2)
            upper.pos, upper.size = (x+pipe.x*s, y+(HEIGHT-top_height)*s), (PIPE_WIDTH*s, top_height*s)
            lower.pos, lower.size = (x+pipe.x*s, y), (PIPE_WIDTH*s, bottom_height*s)
            for rocks, band, height in ((upper_rocks, upper, top_height), (lower_rocks, lower, bottom_height)):
                rocks.pos, rocks.size = band.pos, band.size
                repeats = height/PIPE_WIDTH
                rocks.tex_coords = (0, 0, 1, 0, 1, repeats, 0, repeats)
        self.canvas.ask_update()

    def on_touch_down(self, touch):
        if getattr(touch, 'is_mouse_scrolling', False):
            return False
        if not self._disposed and self.arena.collide_point(*touch.pos):
            self._flap()
            return True
        return super().on_touch_down(touch)

    def dispose(self):
        self._disposed = True
