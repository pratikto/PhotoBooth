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
from .meong_fly_visual_v3 import (
    meong_animation_frames, printed_photo_tile,
    camera_cat_from_latest_logo, photo_feed_frames,
)
from .meong_fly_print_fx import InstantPhotoEmitter
from .meong_fly_flow import MeongFlyFlow
from .meong_fly_game_art import (
    GAME_FIELD_TOP, GAME_FIELD_BOTTOM, ROCK_VARIANTS, camera_cat_poses,
    make_rock_tile, asteroid_screen_rects, camera_screen_rect,
)
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
        self._cat_poses = {
            name: kivy_texture(image)
            for name, image in camera_cat_poses(camera_cat_from_latest_logo(self._logo_path)).items()
        }
        self._cat = self._cat_poses["level"]  # Preserve optional caller compatibility.
        self._asteroids = [kivy_texture(make_rock_tile(i)) for i in range(ROCK_VARIANTS)]
        # Real owner GIF if installed; otherwise a 10-frame print-drop loop
        # composed from its bundled official image, never from the old mascot.
        self._hero_frames = [kivy_texture(img) for img in
                             meong_animation_frames(self._logo_path)]
        self._animated_gif = len(self._hero_frames) > 1
        # Every print stage is pre-rendered once. During gameplay we upload
        # NO PIL pixels; only camera-anchored cached textures are drawn.
        self._photo_tiles = [kivy_texture(printed_photo_tile(i))
                             for i in range(4)]
        self._photo_reveals = [
            [kivy_texture(frame) for frame in
             photo_feed_frames(printed_photo_tile(i))]
            for i in range(4)
        ]
        self._printer = InstantPhotoEmitter()
        self._printer_screen = None
        self._score_tex = {}
        self._score_fx_since = -10.0
        self._score_fx_y = 300.0
        self._impact_until = -1.0
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

    # The hero image boxes mirror paint_poster_screen; no second layout map.
    _HERO_BOXES = {
        "start": (35, 69, 290, 175),
        "won": (78, 219, 215, 160),
        "lost": (97, 264, 170, 118),
    }

    def _hero_rect(self, screen):
        """Fit the actual logo to the painted box, without stretching pixels."""
        box_x, box_y, box_w, box_h = self._HERO_BOXES[screen]
        natural_w, natural_h = self._hero_frames[0].size
        scale = min(box_w / natural_w, box_h / natural_h)
        w, h = natural_w * scale, natural_h * scale
        return (box_x + (box_w - w) / 2,
                box_y + (box_h - h) / 2, w, h)

    def _printer_context(self, screen):
        """Physical paper slot is under the lens/body in the *current* sprite."""
        if screen == "game":
            x, y, w, h = camera_screen_rect(self.flow.game.y)
            return ((x + w * .42, y + h * .87),
                    GAME_FIELD_BOTTOM - 5)
        x, y, w, h = self._hero_rect(screen)
        # The approved camera-cat GIF frame includes its rainbow on the left.
        return ((x + w * .53, y + h * .78),
                271 if screen == "start" else 390)

    def _advance_printer(self, dt):
        """Reset on each scene transition; never spawn across other screens."""
        screen = self.flow.screen
        active = screen if screen in ("start", "game", "won") else None
        if active != self._printer_screen:
            self._printer.reset()
            self._printer.MAX_SHEETS = 1 if active == "won" else 2
            self._printer_screen = active
        if active is not None:
            slot, floor = self._printer_context(active)
            self._printer.update(
                dt, slot, floor,
                paused=(active == "game" and self.flow.paused),
            )

    def _paint_print_sheets(self, screen):
        """Show *only* film emerging at Meong's body, then falling beneath it."""
        if screen != self._printer_screen:
            return
        for pose in self._printer.poses():
            style = pose.serial % len(self._photo_tiles)
            if pose.attached:
                stages = self._photo_reveals[style]
                step = min(len(stages) - 1,
                           max(0, int(pose.reveal * len(stages)) - 1))
                texture = stages[step]
            else:
                texture = self._photo_tiles[style]
            Color(1, 1, 1, pose.opacity)
            pos, size = self._rect(
                (pose.x, pose.y, pose.width, pose.height))
            Rectangle(texture=texture, pos=pos, size=size)

    def _paint_hero(self, screen):
        """Animate a clean camera frame above the physically-fed photo."""
        if screen in ("start", "won"):
            self._paint_print_sheets(screen)
        if self._animated_gif:
            texture = self._hero_frames[int(self._time * 8) %
                                        len(self._hero_frames)]
            Color(1, 1, 1, 1)
            pos, size = self._rect(self._hero_rect(screen))
            Rectangle(texture=texture, pos=pos, size=size)

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

    def _draw_game(self, show_impact=False):
        """Paint a live frame using the unchanged physics geometry and cached art.

        Art textures are prepared in __init__; no Pillow calls per frame.
        """
        game = self.flow.game
        elapsed = game.elapsed  # Frozen during pause and after terminal result.

        # Three parallax layers only inside the playing area.
        for index in range(42):
            depth = 1 + index % 3
            x = (index * 89 - elapsed * (7 + 11 * depth)) % W
            y = GAME_FIELD_TOP + 14 + ((index * 73) % (
                GAME_FIELD_BOTTOM - GAME_FIELD_TOP - 29))
            Color(.30 + depth * .14, .39 + depth * .13, 1, .72)
            pos, size = self._rect((x, y, depth, depth))
            Rectangle(pos=pos, size=size)

        # Quiet background comet; cosmetic, no score or collision.
        comet_x = W + 52 - (elapsed * 17) % (W + 108)
        comet_y = 201 + math.sin(elapsed * .36) * 11
        for i in range(6):
            Color(.28 + .07 * (5 - i), .59 + .03 * (5 - i), 1,
                  .25 + .11 * (5 - i))
            pos, size = self._rect((comet_x + i * 4, comet_y + i * 2, 3, 2))
            Rectangle(pos=pos, size=size)

        for index, obstacle in enumerate(game.pipes):
            for part, (bx, by, bw, bh) in asteroid_screen_rects(
                    obstacle.x, obstacle.gap_y):
                if bh <= 0:
                    continue
                # Clip the belt as an obstacle enters/exits the viewport.
                left = max(0, bx)
                right = min(W, bx + bw)
                visible_width = right - left
                if visible_width <= 0:
                    continue
                pos, size = self._rect((left, by, visible_width, bh))
                # The whole low-contrast belt communicates the true rectangular
                # collision box; individual decorative rocks have alpha edges.
                Color(.27, .22, .42, .88)
                Rectangle(pos=pos, size=size)
                self._border((left, by, visible_width, bh),
                             (.57, .49, .77, .34), 1)

                tile_height = 46.0
                tile_index = 0
                while tile_index * tile_height < bh:
                    filled = tile_index * tile_height
                    tile_h = min(tile_height, bh - filled)
                    variant = (index * 3 + (2 if part == "upper" else 0)
                               + tile_index) % len(self._asteroids)
                    texture = self._asteroids[variant]
                    pos, size = self._rect((left, by + filled,
                                            visible_width, tile_h))
                    Color(1, 1, 1, .99)
                    Rectangle(texture=texture, pos=pos, size=size)
                    tile_index += 1

                # Exact gap boundary: rocks never protrude beyond the hitbox.
                edge_y = by if part == "lower" else by + bh - 3
                pos, size = self._rect((left, edge_y, visible_width, 3))
                Color(.80, .68, .96, 1)
                Rectangle(pos=pos, size=size)

        bx, by, bw, bh = camera_screen_rect(game.y)
        center_y = by + bh / 2
        bands = ((1, .33, .58), (1, .68, .31), (1, .91, .48),
                 (.42, .93, .68), (.31, .75, 1))
        for band, color in enumerate(bands):
            for k in range(20):
                trail_x = bx + 1 - k * 4.1
                if trail_x < -5:
                    break
                trail_y = (center_y + (band - 2) * 4.2
                           + math.sin(elapsed * 9 + k * .47) * 3.2)
                trail_w = 5 if k < 8 else 4 if k < 14 else 2
                trail_h = 4 if k < 11 else 3 if k < 17 else 2
                Color(*color, max(.20, 1 - k * .038))
                pos, size = self._rect((trail_x, trail_y, trail_w, trail_h))
                Rectangle(pos=pos, size=size)

        # Paper originates at the *current* camera body slot, feeds out,
        # detaches, then falls independently. Keep it behind Meong's body.
        if not show_impact:
            self._paint_print_sheets("game")

        # Rotation follows visual movement, NOT a new game physics direction.
        pose = ("climb" if game.velocity > 130 else
                "dive" if game.velocity < -100 else "level")
        Color(1, 1, 1, 1)
        pos, size = self._rect((bx, by, bw, bh))
        Rectangle(texture=self._cat_poses[pose], pos=pos, size=size)
        if int(elapsed * 9) % 4 == 0:
            Color(1, .92, .65, .88)
            pos, size = self._rect((bx + bw * .67, by - 5, 2, 2))
            Rectangle(pos=pos, size=size)

        self._draw_score(game.score, 161, 50, width=94, height=29, scale=4)
        effect_age = self._time - self._score_fx_since
        if 0 <= effect_age < .36 and not show_impact:
            progress = effect_age / .36
            texture = self._score_texture("+1", size=2, color=GOLD)
            top = max(GAME_FIELD_TOP + 10,
                      self._score_fx_y - 50 - progress * 22)
            Color(1, 1, 1, 1 - progress)
            pos, size = self._rect((bx + bw + 5, top, 41, 20))
            Rectangle(texture=texture, pos=pos, size=size)
            for j in range(5):
                Color(1, .80 + j * .03, .33, 1 - progress)
                px = bx + bw + 10 + j * 7
                py = top + 17 + math.sin(j * 1.8) * 5 - progress * 9
                dot_pos, dot_size = self._rect((px, py, 2, 2))
                Rectangle(pos=dot_pos, size=dot_size)

        if show_impact:
            # Flow has already saved the loss exactly once. 220 ms of particles
            # are only a cosmetic transition to the existing result screen.
            progress = 1 - max(0, self._impact_until - self._time) / .22
            for j in range(16):
                angle = j * math.tau / 16
                distance = 5 + max(0, progress) * (13 + j % 4 * 4)
                px = bx + bw / 2 + math.cos(angle) * distance
                py = center_y + math.sin(angle) * distance
                rgb = (1, .68, .27) if j % 3 else (1, .34, .63)
                Color(*rgb, max(0, 1 - progress))
                dot_pos, dot_size = self._rect(
                    (px, py, 2 + j % 2, 2 + j % 2))
                Rectangle(pos=dot_pos, size=dot_size)

        if self.flow.paused:
            Color(.02, .04, .13, .88)
            pos, size = self._rect((0, GAME_FIELD_TOP, W,
                                    GAME_FIELD_BOTTOM - GAME_FIELD_TOP))
            Rectangle(pos=pos, size=size)
            self._draw_score("PAUSED", 180, 309, width=240,
                             height=48, scale=4)
            self._border(ACTIONS["game"]["pause"],
                         (1, .87, .49, .97), 2)

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
            show_impact = (self.flow.screen == "lost"
                           and self._time < self._impact_until)
            screen = ("game" if show_impact else
                      self.flow.screen if self.flow.screen in self._backdrops
                      else "start")
            pos, size = self._rect((0, 0, W, H))
            Color(1, 1, 1, 1)
            Rectangle(texture=self._backdrops[screen], pos=pos, size=size)
            if screen == "game":
                self._draw_game(show_impact=show_impact)
            elif screen == "lost":
                self._draw_score(
                    f"{self.flow.game.score}/{TARGET_SCORE}",
                    180, 442, width=180, height=36, scale=3,
                )
            if screen in ("start", "scan"):
                self._draw_menu_effects(screen)
            if screen in ("start", "won", "lost"):
                self._paint_hero(screen)
        self._screen_seen = screen  # Track displayed game during brief impact.

    def validate_receipt(self):
        if self.flow.claim_and_start(self.receipt.text):
            self.receipt.focus = False
        self._refresh()

    def update(self, dt):
        self._time += min(max(float(dt), 0), .1)
        before_screen = self.flow.screen
        before_score = self.flow.game.score
        self.flow.tick(dt)
        self._advance_printer(dt)
        if before_screen == "game" and self.flow.game.score > before_score:
            self._score_fx_since = self._time
            self._score_fx_y = (GAME_FIELD_BOTTOM -
                                self.flow.game.y * W / WIDTH)
        if before_screen == "game" and self.flow.screen == "lost":
            self._impact_until = self._time + .22
        # Scan is decorative; it does not scan a real cafe receipt.
        tick = int(self._time * 15)
        animate_scan = self.flow.screen == "scan" and tick != self._scan_tick
        animate_paper = self.flow.screen in ("start", "won", "lost")
        animate_paper = animate_paper and tick != self._scan_tick
        if animate_scan or animate_paper:
            self._scan_tick = tick
        if (self.flow.screen == "game" or animate_scan or animate_paper
                or self._time < self._impact_until
                or self._screen_seen != self.flow.screen):
            self._refresh()

    def on_touch_down(self, touch):
        # Prevent invisible result CTA activation during the 220 ms burst.
        if self.flow.screen == "lost" and self._time < self._impact_until:
            return True
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
        elif action == "tutorial_done":
            if self.flow.finish_tutorial():
                # Standalone-only on-disk flag; production onboarding is separate.
                marker = Path.home() / ".meong_fly_tutorial_seen"
                try:
                    marker.write_text("1", encoding="ascii")
                except OSError:
                    # Continue this session; do not block customers on disk failure.
                    pass
        elif action.startswith("layout_"):
            self.flow.select_layout(int(action.split("_")[1]))
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
        tutorial_seen = (Path.home() / ".meong_fly_tutorial_seen").is_file()
        self.flow = MeongFlyFlow(ledger, tutorial_seen=tutorial_seen)
        self.stage = MeongFlyStage(self.flow)
        return self.stage

    def on_stop(self):
        if getattr(self, "stage", None) is not None:
            self.stage.dispose()
