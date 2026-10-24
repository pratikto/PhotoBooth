"""V2 lifecycle and responsive-layout adapter for the unchanged Meong Fly.

All painting, camera/film composition, animation and physics come from the
original modules. Original static artwork is reflowed by the layout adapter;
input, async ledger and kiosk lifecycle stay under the v2 host.
"""

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, InstructionGroup, Quad, Rectangle
from kivy.uix.widget import Widget
from PIL import Image

from photobooth.meong_fly_flow import MeongFlyFlow
from photobooth.meong_fly_gui import MeongFlyStage, kivy_texture
from photobooth.meong_fly_painter import ACTIONS
from .game_layout import Layout, horizontal_slices, scene_art


class ClaimedAttempt:
    """Bridge original flow callbacks to the already durable v2 claim/result."""

    def __init__(self, host):
        self.host = host

    def claim(self, code):
        attempt = self.host._game_attempt
        return bool(attempt and attempt['token'] == code and attempt['result'] == 'started')

    def finish(self, code, won):
        attempt = self.host._game_attempt
        if attempt and attempt['token'] == code:
            self.host._finish_game_demo('won' if won else 'lost')


class KioskGameFlow(MeongFlyFlow):
    def __init__(self, host):
        self.host = host
        super().__init__(ClaimedAttempt(host), tutorial_seen=host.navigation.tutorial_seen)

    def flap(self):
        stage = self.host._game_field
        if stage is None or not stage.input_allowed():
            return False
        accepted = super().flap()
        if accepted:
            self.host.audio_v2.cue('button')
        return accepted

    def tick(self, dt):
        if self.host._closed or self.host._suspended or self.host._game_jobs.busy:
            return
        # Original tick owns physics, score and terminal transition. The ledger
        # callback queues persistence; v2 blocks result CTA until it is acked.
        super().tick(dt)


class KioskGameStage(MeongFlyStage):
    def __init__(self, host, flow, **kwargs):
        self.host = host
        self._mounted = self._disposed = False
        self._mount_revision = -1
        self._responsive_scenes = None
        super().__init__(flow, scanner=None, **kwargs)
        self._responsive_scenes = {}
        # The original renderer still owns dynamic art. Static UI is extracted
        # from its exact painter pixels and reflowed separately below.
        blank = kivy_texture(Image.new('RGBA', (1, 1)))
        for scene in ('start', 'scan', 'game', 'won', 'lost'):
            self._backdrops[scene] = blank
        self._resize()
        self.detach()

    def input_allowed(self):
        return (not self._disposed and self._mounted and not self.host._closed and
                not self.host._suspended and not self.host._game_jobs.busy and
                self.host._game_field is self and self._mount_revision == self.host._view_revision)

    def mount(self):
        if self._disposed:
            raise RuntimeError('Cannot mount a retired Meong Fly stage.')
        self._mounted = True
        self._mount_revision = self.host._view_revision
        if self._update_event is None:
            self._update_event = Clock.schedule_interval(self.update, 1/30)
            Window.bind(mouse_pos=self._mouse_moved)
        self._refresh()

    def detach(self):
        self._mounted = False
        if self._update_event is not None:
            self._update_event.cancel()
            self._update_event = None
        Window.unbind(mouse_pos=self._mouse_moved)
        self.receipt.focus = False
        self.receipt.disabled = True
        if self.parent is not None:
            self.parent.remove_widget(self)

    def dispose(self):
        self.detach()
        self._disposed = True
        super().dispose()

    def update(self, dt):
        if self._mounted and not self._disposed and not self.host._closed and not self.host._suspended:
            super().update(dt)

    def _refresh(self):
        if self._responsive_scenes is None:
            return super()._refresh()
        scene = ('game' if self.flow.screen == 'lost' and self._time < self._impact_until
                 else self.flow.screen)
        self._layout = Layout(self.width, self.height, scene)
        super()._refresh()
        group = self._static_scene(scene)
        # After the original opaque plate, before original camera/rocks/FX.
        plate_index = next(i for i, item in enumerate(self.canvas.before.children)
                           if isinstance(item, Rectangle))
        self.canvas.before.insert(plate_index + 1, group)
        # Original film compositor uses viewport points rather than _rect.
        # Remap those same quads, preserving its UV crop, depth and animation.
        scale = self._layout.scale
        for item in self.canvas.before.children:
            if isinstance(item, Quad):
                points = []
                for px, py in zip(item.points[::2], item.points[1::2]):
                    x, y = (px-self.x)/scale, (self.top-py)/scale
                    if scene == 'game':
                        x = self._layout.world_x(x)
                        y += self._layout.extra[1]/2
                    else:
                        x += self._layout.extra[0]/2
                        y += self._layout.menu_offset(self._camera_context(scene)[1])
                    points.extend((self.x+x*scale, self.top-y*scale))
                item.points = points

    def _viewport(self):
        if self._responsive_scenes is None:
            return super()._viewport()
        scale = Layout(self.width, self.height, self.flow.screen).scale
        return self.x, self.top-720*scale, scale

    def _rect(self, box):
        if self._responsive_scenes is None:
            return super()._rect(box)
        scene = ('game' if self.flow.screen == 'lost' and self._time < self._impact_until
                 else self.flow.screen)
        layout = getattr(self, '_layout', None)
        if layout is None or (layout.width, layout.height, layout.scene) != (self.width, self.height, scene):
            layout = self._layout = Layout(self.width, self.height, scene)
        x, y, w, h = layout.rect(box)
        return (self.x+x*layout.scale, self.top-(y+h)*layout.scale), (w*layout.scale, h*layout.scale)

    def _static_scene(self, scene):
        if scene not in self._responsive_scenes:
            bg, patches = scene_art(scene, self._logo_path)
            group = InstructionGroup()
            group.add(Color(1, 1, 1, 1))
            background = Rectangle(texture=kivy_texture(bg))
            group.add(background)
            instructions = []
            for box, wide, anchor, pixels in patches:
                slices = []
                for sx, sw, _, _ in horizontal_slices(pixels.width, 1 if wide else 0,
                                                       cap=20 if anchor == 'footer' else 12):
                    tile = pixels.crop((sx, 0, sx+sw, pixels.height))
                    rect = Rectangle(texture=kivy_texture(tile))
                    group.add(rect)
                    slices.append(rect)
                instructions.append((box, wide, anchor, slices))
            self._responsive_scenes[scene] = (group, background, bg.size, instructions, None)
        group, bg, bg_size, instructions, previous = self._responsive_scenes[scene]
        geometry = (*self.pos, *self.size)
        if previous != geometry:
            # Cover-crop one continuous original sky; no separately painted sides.
            bg.pos, bg.size = self.pos, self.size
            ratio = (self.width/self.height) / (bg_size[0]/bg_size[1])
            uw, vh = (1, 1/ratio) if ratio >= 1 else (ratio, 1)
            left, bottom = (1-uw)/2, (1-vh)/2
            bg.tex_coords = (left, bottom+vh, left+uw, bottom+vh,
                             left+uw, bottom, left, bottom)
            layout = Layout(self.width, self.height, scene)
            for box, wide, anchor, rects in instructions:
                x, y, w, h = layout.patch(box, wide, anchor)
                extra = w-box[2]
                specs = horizontal_slices(box[2], max(.01, extra) if wide else 0,
                                          cap=20 if anchor == 'footer' else 12)
                for rect, (_, _, dx, dw) in zip(rects, specs):
                    rect.pos = (self.x+(x+dx)*layout.scale,
                                self.top-(y+h)*layout.scale)
                    rect.size = (dw*layout.scale, h*layout.scale)
            self._responsive_scenes[scene] = (group, bg, bg_size, instructions, geometry)
        return group

    def _action_at(self, position):
        if not self.collide_point(*position):
            return None
        for action, box in ACTIONS.get(self.flow.screen, {}).items():
            (x, y), (w, h) = self._rect(box)
            if x <= position[0] <= x+w and y <= position[1] <= y+h:
                return action
        return None

    def _sync_overlays(self):
        super()._sync_overlays()
        self.receipt.disabled = self.receipt.disabled or self.host._game_jobs.busy or not self._mounted
        if self.flow.screen == 'scan':
            self.notice.text = (self.host._game_error or
                                ('Memeriksa kode DEMO…' if self.host._game_jobs.busy else
                                 'Scanner nonaktif. Ketik kode DEMO baru.'))

    def validate_receipt(self):
        if self.input_allowed():
            self.host._claim_game_demo()
            self._refresh()

    def _handle_action(self, action):
        if not self.input_allowed() or action not in ACTIONS.get(self.flow.screen, {}):
            return
        callbacks = {
            'game': self.host._open_game_demo,
            'photo': lambda:self.host._choose_photo('skip_game'),
            'back': self.host._back_game_intro,
            'validate': self.validate_receipt,
            'pause': self.host._toggle_game_pause,
            'continue': self.host._continue_game_photo,
        }
        callback = callbacks.get(action)
        if callback is not None:
            self.host.audio_v2.cue('button')
            callback()

    def _mouse_moved(self, window, position):
        if self.input_allowed():
            super()._mouse_moved(window, self.to_widget(*position))

    def on_touch_down(self, touch):
        if (not self.input_allowed() or getattr(touch, 'is_mouse_scrolling', False) or
                getattr(touch, 'button', 'left') in {'right', 'middle'}):
            return False
        if not self.collide_point(*touch.pos):
            return False
        if self.flow.screen == 'lost' and self._time < self._impact_until:
            return True
        if Widget.on_touch_down(self, touch):
            return True
        action = self._action_at(touch.pos)
        if action is not None:
            self._handle_action(action)
        elif self.flow.screen == 'game':
            self.flow.flap()
        return True
