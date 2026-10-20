"""Standalone Meong Fly Space Edition: demo voucher, one attempt, asteroid dodging."""
import random
from pathlib import Path
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from .meong_fly import MeongFly, WIDTH, HEIGHT, PIPE_WIDTH, GAP_HEIGHT, CAT_X
from .meong_fly_receipts import DemoReceiptLedger


class SpaceBoard(Widget):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.stars = [(random.Random(i).uniform(0, WIDTH), random.Random(i+999).uniform(0, HEIGHT)) for i in range(75)]
        self.bind(pos=lambda *_: self.redraw(), size=lambda *_: self.redraw())

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.game.flap()  # Never start a second attempt from a screen tap.
            return True
        return super().on_touch_down(touch)

    def redraw(self):
        if not self.width or not self.height:
            return
        sx, sy = self.width / WIDTH, self.height / HEIGHT
        def rect(x, y, w, h):
            Rectangle(pos=(self.x + x*sx, self.y + y*sy), size=(w*sx, h*sy))
        with self.canvas:
            self.canvas.clear()
            Color(.025, .035, .15, 1)
            rect(0, 0, WIDTH, HEIGHT)
            for x, y in self.stars:
                Color(.7, .8, 1, 1)
                rect(x, y, 2, 2)
            Color(.36, .2, .6, 1)
            Ellipse(pos=(self.x + 360*sx, self.y + 530*sy), size=(80*sx, 80*sy))
            for obstacle in self.game.pipes:
                # Rocky asteroid fields occupy the top and bottom of each gap.
                for low, high in ((0, obstacle.gap_y-GAP_HEIGHT/2),
                                  (obstacle.gap_y+GAP_HEIGHT/2, HEIGHT)):
                    if high <= low:
                        continue
                    Color(.36, .34, .53, 1)
                    rect(obstacle.x, low, PIPE_WIDTH, high-low)
                    Color(.55, .51, .68, 1)
                    for j in range(3):
                        cy = low + (high-low)*(j+1)/4
                        Ellipse(pos=(self.x+(obstacle.x+10+j*9)*sx, self.y+cy*sy),
                                size=(14*sx, 12*sy))
            cx, cy = CAT_X, self.game.y
            # Pixel-art rainbow exhaust from the camera-cat's rear.
            for j, rgb in enumerate(((1,.27,.42),(1,.63,.2),(.98,.88,.28),(.3,.85,.6),(.35,.55,1))):
                Color(*rgb, 1)
                rect(cx-77, cy-13+j*5, 64, 5)
            Color(0,0,0,1)
            rect(cx-19,cy-21,64,43)
            Color(1,1,1,1)
            rect(cx-16,cy-18,58,37)
            Color(.58,.6,.67,1)
            rect(cx-12,cy-14,52,29)
            # White instant camera with a large blue lens and cat face.
            Color(.05,.23,.55,1)
            Ellipse(pos=(self.x+(cx-9)*sx,self.y+(cy-11)*sy),size=(23*sx,23*sy))
            Color(.05,.62,1,1)
            Ellipse(pos=(self.x+(cx-4)*sx,self.y+(cy-6)*sy),size=(13*sx,13*sy))
            Color(.55,.57,.64,1)
            rect(cx+16,cy-12,25,25)
            rect(cx+18,cy+9,7,11)
            rect(cx+32,cy+9,7,11)
            Color(.07,.07,.12,1)
            rect(cx+23,cy+2,3,4)
            rect(cx+34,cy+2,3,4)
            rect(cx+28,cy-5,5,3)
            Color(1,.42,.7,1)
            rect(cx+19,cy-4,4,4)
            rect(cx+37,cy-4,4,4)


class Demo(App):
    def build(self):
        Window.size = (540, 780)
        self.game = MeongFly()
        self.ledger = DemoReceiptLedger(Path.home() / ".meong_fly_demo.sqlite3")
        self.active_receipt = None
        root = BoxLayout(orientation="vertical", padding=12, spacing=8)
        self.title_label = Label(text="MEONG FLY! SPACE EDITION", size_hint_y=None, height=50, font_size=22)
        self.receipt = TextInput(hint_text="Kode struk demo: DEMO-123", multiline=False,
                                 size_hint_y=None, height=48)
        self.scan = Button(text="VALIDASI STRUK & MAIN (1X)", size_hint_y=None, height=52)
        self.scan.bind(on_release=self.start_attempt)
        self.board = SpaceBoard(self.game)
        self.status = Label(text="Masukkan voucher demo untuk mulai", size_hint_y=None, height=65)
        self.continue_button = Button(text="LANJUT FOTO (DEMO: tutup game)", size_hint_y=None, height=52)
        self.continue_button.bind(on_release=lambda *_: self.stop())
        for item in (self.title_label, self.receipt, self.scan, self.board, self.status, self.continue_button):
            root.add_widget(item)
        Clock.schedule_interval(self.tick, 1/60)
        return root

    def start_attempt(self, *_):
        code = self.receipt.text.strip()
        if self.active_receipt is not None:
            self.status.text = "Kesempatan sudah digunakan. Tidak ada Main Lagi."
            return
        if not self.ledger.claim(code):
            self.status.text = "Struk demo tidak valid atau sudah pernah digunakan."
            return
        self.active_receipt = code
        self.receipt.disabled = True
        self.scan.disabled = True
        self.game.start()

    def tick(self, dt):
        self.game.step(dt)
        self.board.redraw()
        if self.active_receipt and self.game.status in ("won", "lost"):
            self.ledger.finish(self.active_receipt, self.game.status == "won")
        if self.game.status == "won":
            self.status.text = "MENANG! Simulasi diskon Rp2.500 (belum aktif)"
        elif self.game.status == "lost":
            self.status.text = "GAME OVER - lanjut foto harga normal, tanpa retry"
        elif self.game.status == "playing":
            self.status.text = f"Hindari asteroid! Skor {self.game.score}/6"
        elif self.active_receipt is None:
            self.status.text = "Scan kode demo DEMO-... untuk 1 kesempatan"


if __name__ == "__main__":
    Demo().run()
