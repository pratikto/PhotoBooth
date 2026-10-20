"""Standalone Meong Fly Space Edition: demo voucher, one attempt, asteroid dodging."""
import random
import math
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
        self.stars = [(random.Random(i).uniform(0, WIDTH), random.Random(i+999).uniform(0, HEIGHT), 1 + (i % 3)) for i in range(85)]
        self.bind(pos=lambda *_: self.redraw(), size=lambda *_: self.redraw())

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.game.flap()  # Never start a second attempt from a screen tap.
            return True
        return super().on_touch_down(touch)

    def redraw(self):
        if not self.width or not self.height:
            return
        # Uniform scaling prevents stretched cats and deceptive collision visuals.
        scale = min(self.width / WIDTH, self.height / HEIGHT)
        ox = self.x + (self.width - WIDTH * scale) / 2
        oy = self.y + (self.height - HEIGHT * scale) / 2
        sx = sy = scale
        t = self.game.elapsed
        def rect(x, y, w, h):
            Rectangle(pos=(ox + x*sx, oy + y*sy), size=(w*sx, h*sy))
        def circle(x, y, radius):
            Ellipse(pos=(ox+(x-radius)*sx, oy+(y-radius)*sy),
                    size=(2*radius*sx, 2*radius*sy))
        with self.canvas:
            self.canvas.clear()
            Color(.025, .026, .12, 1)
            rect(0, 0, WIDTH, HEIGHT)
            # Subtle moving star field: cosmetic only, never changes collisions.
            for x, y, depth in self.stars:
                Color(.35 + .16*depth, .45 + .12*depth, 1, 1)
                px = (x - t*(7+depth*10)) % WIDTH
                rect(px, y, depth, depth)
            # Distant purple planet with ring, and blue horizon.
            Color(.19, .12, .40, 1)
            circle(395, 538, 57)
            Color(.54, .31, .75, 1)
            Ellipse(pos=(ox+329*sx, oy+525*sy), size=(132*sx, 22*sy))
            Color(.31, .17, .56, 1)
            circle(395, 538, 48)
            Color(.06, .18, .42, 1)
            circle(40, -40, 126)
            Color(.08, .28, .53, 1)
            circle(35, -48, 111)
            # Asteroid columns: rocky edges, crater details, no green pipes.
            # Their hitboxes remain identical to the physics engine.
            for idx, obstacle in enumerate(self.game.pipes):
                for part, (low, high) in enumerate(((0, obstacle.gap_y-GAP_HEIGHT/2),
                                                      (obstacle.gap_y+GAP_HEIGHT/2, HEIGHT))):
                    if high <= low:
                        continue
                    Color(.23, .21, .36, 1)
                    rect(obstacle.x, low, PIPE_WIDTH, high-low)
                    Color(.42, .38, .56, 1)
                    rect(obstacle.x+5, low, PIPE_WIDTH-10, high-low)
                    # Crater positions are deterministic and remain decorative.
                    for j in range(int((high-low)//40)+1):
                        cy = low + 20 + j*39
                        if cy > high-8:
                            continue
                        cx = obstacle.x + 17 + ((j*19+idx*11+part*7)%29)
                        Color(.17, .15, .30, 1)
                        circle(cx, cy, 10)
                        Color(.61, .55, .69, 1)
                        circle(cx-3, cy+3, 4)
                    Color(.62, .56, .72, 1)
                    rect(obstacle.x, high-7 if part==0 else low, PIPE_WIDTH, 7)
            cx, cy = CAT_X, self.game.y
            # Five-color wavy rainbow exhaust; small time-based animation.
            for j, rgb in enumerate(((1,.26,.39),(1,.60,.16),(.98,.86,.23),
                                     (.26,.84,.57),(.27,.57,1))):
                Color(*rgb, 1)
                for segment in range(13):
                    px = cx-90 + segment*6
                    wave = math.sin(t*10 + segment*.6)*3
                    rect(px, cy-13+j*5+wave, 7, 5)
            # Pixel camera-cat based on Meong brand silhouette: white outline,
            # gray camera body, prominent blue lens, pink cheeks, camera flash.
            Color(0,0,0,1)
            rect(cx-24,cy-25,78,51)
            rect(cx-12,cy+25,21,8)
            rect(cx+25,cy+19,24,13)
            Color(1,1,1,1)
            rect(cx-21,cy-22,72,45)
            rect(cx-9,cy+23,15,7)
            rect(cx+28,cy+18,18,11)
            Color(.58,.61,.68,1)
            rect(cx-17,cy-18,64,37)
            Color(.90,.93,.96,1)
            rect(cx-17,cy-18,40,37)
            Color(.06,.08,.16,1)
            circle(cx-1,cy,17)
            Color(.05,.33,.82,1)
            circle(cx-1,cy,14)
            Color(.10,.72,1,1)
            circle(cx+2,cy+2,8)
            Color(.02,.09,.24,1)
            circle(cx+3,cy+1,5)
            Color(1,1,1,1)
            rect(cx+26,cy+13,7,6)
            Color(.1,.84,1,1)
            rect(cx+27,cy+14,5,4)
            # Cat ears and face are integral to the camera silhouette.
            Color(.54,.57,.64,1)
            rect(cx+25,cy+19,9,10)
            rect(cx+42,cy+19,9,10)
            rect(cx+22,cy-15,30,31)
            Color(.08,.08,.12,1)
            rect(cx+29,cy+3,3,4)
            rect(cx+43,cy+3,3,4)
            rect(cx+35,cy-5,6,3)
            Color(1,.48,.72,1)
            rect(cx+24,cy-5,5,4)
            rect(cx+46,cy-5,5,4)
            # Tiny printed-photo slot at the bottom of the camera.
            Color(.06,.07,.12,1)
            rect(cx-12,cy-22,28,4)


class Demo(App):
    def build(self):
        Window.size = (540, 780)
        self.game = MeongFly()
        self.ledger = DemoReceiptLedger(Path.home() / ".meong_fly_demo.sqlite3")
        self.active_receipt = None
        self.result_recorded = False
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
        self.result_recorded = False
        self.receipt.disabled = True
        self.scan.disabled = True
        self.game.start()

    def tick(self, dt):
        self.game.step(dt)
        self.board.redraw()
        if self.active_receipt and not self.result_recorded and self.game.status in ("won", "lost"):
            self.ledger.finish(self.active_receipt, self.game.status == "won")
            self.result_recorded = True
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
