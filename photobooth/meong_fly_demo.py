"""Standalone FEAT-021 Kivy arcade prototype. Launch: python -m photobooth.meong_fly_demo"""
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from .meong_fly import MeongFly, WIDTH, HEIGHT, PIPE_WIDTH, GAP_HEIGHT, CAT_X, CAT_RADIUS


class GameBoard(Widget):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.bind(pos=lambda *_: self.redraw(), size=lambda *_: self.redraw())

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.game.status == "ready":
                self.game.start()
            else:
                self.game.flap()
            return True
        return super().on_touch_down(touch)

    def redraw(self):
        sx, sy = self.width / WIDTH, self.height / HEIGHT
        with self.canvas:
            self.canvas.clear()
            Color(0.62, 0.84, 0.98, 1)
            Rectangle(pos=self.pos, size=self.size)
            for pipe in self.game.pipes:
                Color(0.31, 0.69, 0.47, 1)
                bottom = pipe.gap_y - GAP_HEIGHT / 2
                top = pipe.gap_y + GAP_HEIGHT / 2
                Rectangle(pos=(self.x + pipe.x * sx, self.y), size=(PIPE_WIDTH * sx, bottom * sy))
                Rectangle(pos=(self.x + pipe.x * sx, self.y + top * sy),
                          size=(PIPE_WIDTH * sx, (HEIGHT - top) * sy))
            # Pixel-inspired gray cat with ears and a rainbow trail.
            cy = self.y + self.game.y * sy
            cx = self.x + CAT_X * sx
            for i, rgb in enumerate(((1, .25, .35), (1, .65, .15), (.98, .9, .3), (.3, .8, .55), (.35, .55, 1))):
                Color(*rgb, 1)
                Rectangle(pos=(cx - (65 + i * 4) * sx, cy - (12 - i * 5) * sy),
                          size=(65 * sx, 5 * sy))
            Color(.48, .5, .56, 1)
            Rectangle(pos=(cx - 16 * sx, cy - 13 * sy), size=(32 * sx, 27 * sy))
            Rectangle(pos=(cx - 13 * sx, cy + 9 * sy), size=(9 * sx, 11 * sy))
            Rectangle(pos=(cx + 5 * sx, cy + 9 * sy), size=(9 * sx, 11 * sy))
            Color(1, 1, 1, 1)
            Ellipse(pos=(cx + 1 * sx, cy), size=(6 * sx, 6 * sy))
            Ellipse(pos=(cx + 10 * sx, cy), size=(6 * sx, 6 * sy))
            Color(.1, .1, .15, 1)
            Ellipse(pos=(cx + 4 * sx, cy + sy), size=(3 * sx, 3 * sy))
            Ellipse(pos=(cx + 13 * sx, cy + sy), size=(3 * sx, 3 * sy))


class Demo(App):
    def build(self):
        self.game = MeongFly()
        Window.size = (540, 780)
        root = BoxLayout(orientation="vertical", padding=12, spacing=8)
        self.status = Label(text="MEONG FLY!  |  Tap to fly", size_hint_y=None, height=54, font_size=23)
        self.board = GameBoard(self.game)
        restart = Button(text="New game", size_hint_y=None, height=58)
        restart.bind(on_release=lambda *_: self.game.reset())
        root.add_widget(self.status)
        root.add_widget(self.board)
        root.add_widget(restart)
        Clock.schedule_interval(self.tick, 1 / 60)
        return root

    def tick(self, dt):
        self.game.step(dt)
        self.board.redraw()
        self.status.text = f"MEONG FLY!  |  Score {self.game.score}/6  |  {self.game.status.upper()}"


if __name__ == "__main__":
    Demo().run()
