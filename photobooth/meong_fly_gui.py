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
        self._screen_seen = None
        self._time = 0.0
        self._hover_action = None  # Decorative highlight, never affects game state.
        self._scan_tick = -1
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
            cursor_color=(.06, .43, .85, 1),
            hint_text_color=(.43, .42, .58, 1),
            selection_color=(.28, .73, .98, .38),
            size_hint=(None, None), write_tab=False,
        )
        self.receipt.bind(on_text_validate=lambda *_: self.validate_receipt())
        self.receipt.bind(focus=self._focus_changed)
        self.add_widget(self.receipt)
        self.notice = Label(
            text="", color=(1, .83, .44, 1),
            bold=True, halign="center", valign="middle",
            size_hint=(None, None),
        )
        self.add_widget(self.notice)
        self.bind(pos=self._resize, size=self._resize)
        self._resize()
        self._update_event = Clock.schedule_interval(self.update, 1 / 30)
        # Desktop hover is optional: mobile/touch controls work without it.
        Window.bind(mouse_pos=self._mouse_moved)

    def dispose(self):
        """Release the clock and mouse listener when this standalone stage closes."""
        if self._update_event is not None:
            self._update_event.cancel()
            self._update_event = None
        Window.unbind(mouse_pos=self._mouse_moved)

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

    def _focus_changed(self, *_):
        """Keep focus ring synchronized without ever clearing TextInput.canvas."""
        if self.flow.screen == "scan":
            self._refresh()

    def _action_at(self, window_position):
        """Map Window mouse coordinates to the exact shared logical hitbox."""
        if not self.collide_point(*window_position):
            return None
        ox, oy, scale = self._viewport()
        if scale <= 0:
            return None
        x = (window_position[0] - ox) / scale
        y = H - (window_position[1] - oy) / scale
        if not (0 <= x <= W and 0 <= y <= H):
            return None
        for action, (ax, ay, width, height) in ACTIONS.get(
                self.flow.screen, {}).items():
            if ax <= x <= ax + width and ay <= y <= ay + height:
                return action
        return None

    def _mouse_moved(self, _window, window_position):
        """Repaint only when the highlighted action actually changes."""
        if self.flow.screen not in ("start", "scan"):
            return
        hovered = self._action_at(window_position)
        if hovered != self._hover_action:
            self._hover_action = hovered
            self._refresh()

    def _border(self, logical_xywh, rgba, thickness=2):
        """Simple pixel border following the same letterbox transform as taps."""
        (x, y), (w, h) = self._rect(logical_xywh)
        t = max(1, thickness * self._viewport()[2])
        Color(*rgba)
        Rectangle(pos=(x, y), size=(w, t))
        Rectangle(pos=(x, y + h - t), size=(w, t))
        Rectangle(pos=(x, y), size=(t, h))
        Rectangle(pos=(x + w - t, y), size=(t, h))

    def _draw_menu_effects(self, screen):
        """Lightweight animated overlays: no Pillow/GPU texture creation."""
        if screen == "scan":
            # Demonstration animation only; no QR scanning or decoding.
            scan_y = 292 + (math.sin(self._time * 1.9) + 1) * 54
            pos, size = self._rect((112, scan_y, 136, 8))
            Color(.30, .82, 1, .15)
            Rectangle(pos=pos, size=size)
            pos, size = self._rect((112, scan_y + 3, 136, 2))
            Color(.34, .88, 1, .68)
            Rectangle(pos=pos, size=size)
            if self.flow.message:
                self._border(DEMO_ENTRY, (1, .45, .45, .9), 2)
            elif self.receipt.focus:
                self._border(DEMO_ENTRY, (.20, .82, 1, .95), 2)
        if self._hover_action in ACTIONS.get(screen, {}):
            self._border(ACTIONS[screen][self._hover_action],
                         (1, .97, .72, .86), 2)

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
        # Foreground stars drift at three parallax speeds without shifting hitboxes.
        for index in range(34):
            depth = 1 + index % 3
            star_x = (index * 89 - self._time * (8 + depth * 10)) % W
            star_y = 141 + ((index * 73) % 462)
            Color(.34 + depth * .17, .41 + depth * .13, 1, .85)
            Rectangle(pos=(ox + star_x * scale, oy + star_y * scale),
                      size=(depth * scale, depth * scale))
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
        """Repaint only the background layer; keep interactive child canvases.

        Kivy attaches the TextInput/Label canvases to this Widget's main
        canvas. Clearing that canvas removes the input's text and caret from
        rendering, even though its painted box and touch widget still exist.
        The static scene belongs in canvas.before, safely behind child widgets.
        """
        self._sync_overlays()
        self.canvas.before.clear()
        with self.canvas.before:
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
            if screen in ("start", "scan"):
                self._draw_menu_effects(screen)
        self._screen_seen = self.flow.screen

    def validate_receipt(self):
        if self.flow.claim_and_start(self.receipt.text):
            self.receipt.focus = False
        self._refresh()

    def update(self, dt):
        self._time += min(max(float(dt), 0), .1)
        self.flow.tick(dt)
        # Scan animates only its illustration beam; menus/results stay cached.
        tick = int(self._time * 15)
        animate_scan = self.flow.screen == "scan" and tick != self._scan_tick
        if animate_scan:
            self._scan_tick = tick
        if (self.flow.screen == "game" or animate_scan
                or self._screen_seen != self.flow.screen):
            self._refresh()

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

    def on_stop(self):
        if getattr(self, "stage", None) is not None:
            self.stage.dispose()
