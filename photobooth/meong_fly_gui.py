"""FEAT-021: isolated mockup-matched Kivy GUI; no production photobooth wiring.

All five screens are real painted pixel UI, not pasted screenshot hotspots.
A uniform 360x720 viewport is used for BOTH artwork and touch coordinates.
"""
import math
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from PIL import Image, ImageDraw

from .branding import LOGO_PATH
from .meong_fly import (
    CAT_BOTTOM, CAT_LEFT, CAT_RIGHT, CAT_TOP, CAT_X,
    GAP_HEIGHT, HEIGHT, PIPE_WIDTH, TARGET_SCORE, WIDTH,
)
from .meong_fly_flow import MeongFlyFlow
from .meong_fly_painter import (
    ACTIONS, DEMO_ENTRY, H, W, GOLD,
    logo_parts, make_asteroid_tile, paint_static_screen, pixel_text,
)
from .meong_fly_receipts import DemoReceiptLedger


def kivy_texture(image):
    """Upload the original pixels at nearest-neighbor scale, like ui_brand."""
    rgba = image.convert("RGBA")
    texture = Texture.create(size=rgba.size, colorfmt="rgba")
    texture.flip_vertical()
    texture.blit_buffer(rgba.tobytes(), colorfmt="rgba", bufferfmt="ubyte")
    texture.min_filter = texture.mag_filter = "nearest"
    return texture


class MeongFlyStage(Widget):
    """A responsive five-screen stage with gameplay/receipt-state isolation."""

    def __init__(self, flow, logo_path=LOGO_PATH, **kwargs):
        super().__init__(**kwargs)
        self.flow = flow
        self._time = 0.0
        self._logo_path = Path(logo_path)
        self._backdrops = {
            name: kivy_texture(paint_static_screen(name, self._logo_path))
            for name in ACTIONS
        }
        self._cat = kivy_texture(logo_parts(str(self._logo_path))[1])
        self._asteroids = [kivy_texture(make_asteroid_tile(i)) for i in range(3)]
        self._score_tex = {}
        self.receipt = TextInput(
            hint_text="DEMO-123", multiline=False,
            background_normal="", background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=(.04, .06, .20, 1),
            cursor_color=(.13, .36, .83, 1),
            size_hint=(None, None), write_tab=False,
        )
        self.receipt.bind(on_text_validate=lambda *_: self.validate_receipt())
        self.add_widget(self.receipt)
        self.notice = Label(
            text="", color=(1, .83, .44, 1),
            bold=True, halign="center", valign="middle",
            size_hint=(None, None),
        )
        self.add_widget(self.notice)
        self.bind(pos=self._resize, size=self._resize)
        self._resize()
        Clock.schedule_interval(self.update, 1 / 30)

    def _viewport(self):
        scale = (min(self.width / W, self.height / H)
                 if self.width and self.height else 1.0)
        return (
            self.x + (self.width - W * scale) / 2,
            self.y + (self.height - H * scale) / 2,
            scale,
        )

    def _rect(self, logical_xywh):
        x, y, w, h = logical_xywh
        ox, oy, scale = self._viewport()
        return (
            (ox + x * scale, oy + (H - y - h) * scale),
            (w * scale, h * scale),
        )

    def _resize(self, *_):
        self.receipt.pos, self.receipt.size = self._rect(DEMO_ENTRY)
        _, _, scale = self._viewport()
        self.receipt.font_size = max(12, 16 * scale)
        self.receipt.padding = [12 * scale, max(3, 11 * scale), 8 * scale, 0]
        self.notice.pos, self.notice.size = self._rect((30, 595, 300, 28))
        self.notice.font_size = max(10, 11 * scale)
        self.notice.text_size = self.notice.size
        self._refresh()

    def _sync_overlays(self):
        active = self.flow.screen == "scan"
        self.receipt.opacity = int(active)
        self.receipt.disabled = not active
        self.notice.opacity = int(active)
        self.notice.text = self.flow.message if active else ""
        if not active and self.receipt.focus:
            self.receipt.focus = False

    def _score_texture(self, value, size=4, color=GOLD):
        key = (str(value), size, color)
        if key not in self._score_tex:
            label = str(value)
            image_width = max(32, (len(label) * 6 - 1) * size + 6)
            image_height = 7 * size + 6
            im = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(im)
            pixel_text(draw, label, image_width / 2, 3, scale=size, fill=color)
            self._score_tex[key] = kivy_texture(im)
        return self._score_tex[key]

    def _draw_score(self, value, x, top, width=120, height=37, scale=3):
        texture = self._score_texture(value, size=scale)
        # Preserve each bitmap glyph's aspect ratio, including '6/10' and PAUSE.
        natural_width = height * texture.size[0] / texture.size[1]
        shown_width = min(width, natural_width)
        pos, size = self._rect((x - shown_width / 2, top,
                                shown_width, height))
        Color(1, 1, 1, 1)
        Rectangle(texture=texture, pos=pos, size=size)

    def _draw_game(self):
        game = self.flow.game
        ox, oy, scale = self._viewport()
        board_bottom = 134.0
        wx = W / WIDTH
        wy = wx  # Hitbox, camera sprite and asteroid textures must not stretch.
        for index, obstacle in enumerate(game.pipes):
            x = obstacle.x * wx
            w = PIPE_WIDTH * wx
            low_y = obstacle.gap_y - GAP_HEIGHT / 2
            high_y = obstacle.gap_y + GAP_HEIGHT / 2
            for part, (bottom, top) in enumerate(((0, low_y),
                                                  (high_y, HEIGHT))):
                if top <= bottom:
                    continue
                bound_y = board_bottom + bottom * wy
                bound_h = (top - bottom) * wy
                # Filled rock belt makes the WHOLE rectangle hitbox visible.
                Color(.28, .22, .44, .86)
                Rectangle(pos=(ox + x * scale, oy + bound_y * scale),
                          size=(w * scale, bound_h * scale))
                tile_size = 46.0
                filled = 0.0
                while filled < bound_h:
                    segment = min(tile_size, bound_h - filled)
                    texture = self._asteroids[
                        (index + part + int(filled / tile_size)) % len(self._asteroids)
                    ]
                    Color(1, 1, 1, .96)
                    # Every tile is bounded by the exact physics collision box.
                    Rectangle(texture=texture,
                              pos=(ox + x * scale,
                                   oy + (bound_y + filled) * scale),
                              size=(w * scale, segment * scale))
                    filled += tile_size
                Color(.67, .55, .85, 1)
                edge_y = (bound_y + bound_h - 3) if part == 0 else bound_y
                Rectangle(pos=(ox + x * scale, oy + edge_y * scale),
                          size=(w * scale, 3 * scale))

        cy = board_bottom + game.y * wy
        body_x = (CAT_X - CAT_LEFT) * wx
        body_y = board_bottom + (game.y - CAT_BOTTOM) * wy
        # The rainbow is decorative: collision is the exact logo body only.
        palette = (
            (1, .38, .65), (1, .65, .31), (1, .90, .45),
            (.40, .92, .66), (.35, .79, 1),
        )
        for band, rgb in enumerate(palette):
            Color(*rgb, 1)
            for k in range(20):
                x = body_x - 3 - k * 4.0
                y = cy + (band - 2) * 4 + math.sin(self._time * 9 + k * .4) * 3
                Rectangle(pos=(ox + x * scale, oy + y * scale),
                          size=(5 * scale, 4 * scale))
        Color(1, 1, 1, 1)
        Rectangle(texture=self._cat,
                  pos=(ox + body_x * scale, oy + body_y * scale),
                  size=((CAT_LEFT + CAT_RIGHT) * wx * scale,
                        (CAT_BOTTOM + CAT_TOP) * wy * scale))
        self._draw_score(game.score, 181, 43, width=92, height=31, scale=4)

        if self.flow.paused:
            Color(.02, .03, .11, .85)
            Rectangle(pos=(ox, oy + 124 * scale),
                      size=(W * scale, 510 * scale))
            self._draw_score("PAUSE", 180, 321, width=230, height=50, scale=4)

    def _refresh(self):
        self._sync_overlays()
        self.canvas.clear()
        with self.canvas:
            Color(.01, .025, .105, 1)
            Rectangle(pos=self.pos, size=self.size)
            screen = (self.flow.screen if self.flow.screen in self._backdrops
                      else "start")
            pos, size = self._rect((0, 0, W, H))
            Color(1, 1, 1, 1)
            Rectangle(texture=self._backdrops[screen], pos=pos, size=size)
            if screen == "game":
                self._draw_game()
            elif screen == "lost":
                self._draw_score(
                    f"{self.flow.game.score}/{TARGET_SCORE}",
                    180, 412, width=180, height=36, scale=3,
                )

    def validate_receipt(self):
        if self.flow.claim_and_start(self.receipt.text):
            self.receipt.focus = False
        self._refresh()

    def update(self, dt):
        self._time += min(max(float(dt), 0), .1)
        self.flow.tick(dt)
        self._refresh()  # Refresh animating stars/rainbow/asteroids and transitions.

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        # The real TextInput takes priority over the scanned-QR illustration.
        if self.flow.screen == "scan" and self.receipt.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        ox, oy, scale = self._viewport()
        x = (touch.x - ox) / scale
        y = H - (touch.y - oy) / scale
        if not (0 <= x <= W and 0 <= y <= H):
            return super().on_touch_down(touch)
        for action, (ax, ay, width, height) in ACTIONS.get(
                self.flow.screen, {}).items():
            if ax <= x <= ax + width and ay <= y <= ay + height:
                self._handle_action(action)
                return True
        if self.flow.screen == "game":
            self.flow.flap()
            return True
        return super().on_touch_down(touch)

    def _handle_action(self, action):
        if action == "game":
            self.flow.open_scan()
        elif action == "photo":
            self.flow.direct_photo()
        elif action == "back":
            self.flow.back()
        elif action == "validate":
            self.validate_receipt()
            return
        elif action == "pause":
            self.flow.toggle_pause()
        elif action == "continue":
            self.flow.continue_from_result()
        if self.flow.screen == "exit":
            Clock.schedule_once(lambda *_: App.get_running_app().stop(), 0)
        self._refresh()


class MeongFlyStandaloneApp(App):
    """Not registered inside the production PhotoBooth welcome screen."""

    def build(self):
        Window.size = (450, 900)
        Window.clearcolor = (.015, .02, .10, 1)
        self.title = "Meong Fly! - Standalone Demo"
        ledger = DemoReceiptLedger(Path.home() / ".meong_fly_demo.sqlite3")
        self.flow = MeongFlyFlow(ledger)
        self.stage = MeongFlyStage(self.flow)
        return self.stage
