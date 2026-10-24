"""Decorative adapter for the existing Meong camera/film compositor.

No game, ledger, camera or printer is instantiated. The original immutable
sprite supplies the small limb poses; native rectangles animate its existing
rainbow. Only bounded textures prepared once are used while the header flies.
"""
from functools import lru_cache
from math import sin

from kivy.clock import Clock
from kivy.graphics import Canvas, Color, Rectangle
from kivy.metrics import dp
from kivy.uix.stencilview import StencilView

from photobooth.meong_fly_gui import MeongFlyStage, kivy_texture
from photobooth.meong_fly_print_fx import InstantPhotoEmitter
from photobooth.meong_fly_sprite import CameraFrame, camera_frames, rotate_point, world_slot
from photobooth.meong_fly_visual_v3 import printed_photo_tile


@lru_cache(maxsize=1)
def flight_art():
    """Cache source-derived limb poses; never edit the shared original layers."""
    base = camera_frames()['level']
    frames, layers = {}, {}
    # Original source-pixel feet and rear appendage, clear of the film outlet.
    joints = ((43, 46, 49, 52), (56, 46, 62, 52), (4, 46, 10, 53))
    for phase in range(4):
        front = base.front.copy()
        for index, box in enumerate(joints):
            tile = base.front.crop(box)
            front.paste((0, 0, 0, 0), box)
            offset = (0, -1, 0, 1)[(phase + index * 2) % 4]
            front.alpha_composite(tile, (box[0], box[1] + offset))
        for pose, angle in (('level', 0), ('climb', -5), ('dive', 5)):
            name = f'{pose}-{phase}'
            rear = base.rear.rotate(-angle, center=(39, 29), expand=False)
            face = front.rotate(-angle, center=(39, 29), expand=False)
            frame = CameraFrame(rear, face, rotate_point(base.slot, (39, 29), angle),
                                base.slot_width, angle)
            frames[name] = frame
            layers[name] = (kivy_texture(frame.rear), kivy_texture(frame.front))
    return frames, layers, tuple(kivy_texture(printed_photo_tile(i)) for i in range(4))


class FlyingMeongArt(StencilView):
    """Moving camera, rainbow and attached/falling photos inside one header."""

    # Actual original camera/aperture/paper composition, not a replacement.
    _paint_camera = MeongFlyStage._paint_camera
    _paint_print_sheets = MeongFlyStage._paint_print_sheets

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._camera_frames, self._camera_layers, self._photo_tiles = flight_art()
        self._printer = InstantPhotoEmitter()
        self._printer_screen = 'header'
        self.elapsed = 0
        self.flight = 0
        self.direction = 1
        self.max_unit = dp(1.65)
        self._pose = 'level-0'
        self._disposed = False
        self._art_canvas = Canvas()
        self.canvas.add(self._art_canvas)
        self._redraw = Clock.create_trigger(self._draw, -1)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    @property
    def texture(self):
        return self._camera_layers['level-0'][1]

    @property
    def unit(self):
        return min(dp(1.65), self.max_unit, max(.01, self.height * .72 / 43.5))

    @property
    def sprite_width(self):
        return 130 * self.unit

    @property
    def travel(self):
        return max(0, self.width - 58.5 * self.unit)

    @property
    def body_x(self):
        return self.x + self.flight * self.travel

    @property
    def mascot_x(self):
        # The body travels edge to edge. Its rainbow can naturally enter/leave
        # through the header's existing stencil, leaving room for a larger cat.
        return self.body_x - (64.5 if self.direction > 0 else 7) * self.unit

    @property
    def body_box(self):
        unit = self.unit
        x = self.body_x
        bob = sin(self.elapsed * 2.4) * 1.5 * unit
        return x, self.center_y + bob - 43.5 * unit / 2, 58.5 * unit, 43.5 * unit

    def _viewport(self):
        scale = max(.001, self.width / 360)
        return self.x, self.top - 720 * scale, scale

    def _rect(self, box):
        x, y, w, h = box
        ox, oy, scale = self._viewport()
        return (ox + x * scale, oy + (720-y-h) * scale), (w*scale, h*scale)

    def _camera_context(self, _screen):
        x, y, w, h = self.body_box
        scale = self._viewport()[2]
        return self._pose, ((x-self.x)/scale, (self.top-y-h)/scale, w/scale, h/scale)

    def advance(self, flight, direction, dt=0):
        if self._disposed:
            return
        self.flight, self.direction = flight, direction
        self.elapsed += min(.05, max(0, dt))
        wave = sin(self.elapsed * 4.2)
        pose = 'climb' if wave > .55 else 'dive' if wave < -.55 else 'level'
        self._pose = f'{pose}-{int(self.elapsed * 8) % 4}'
        name, box = self._camera_context('header')
        frame = self._camera_frames[name]
        slot = world_slot(frame, box)
        if direction < 0:
            slot = (2*box[0]+box[2]-slot[0], slot[1])
        scale = self._viewport()[2]
        # Convert into the original emitter's 360-wide coordinates. The
        # detached sheet remains in header space as Meong flies away.
        self._printer.width = frame.slot_width * box[2] / frame.front.width * .90
        self._printer.height = self._printer.width * 41 / 32
        self._printer.GRAVITY = InstantPhotoEmitter.GRAVITY * self.unit / scale
        self._printer.INITIAL_FALL_SPEED = InstantPhotoEmitter.INITIAL_FALL_SPEED * self.unit / scale
        self._printer.update(dt, slot, self.height/scale + 22, angle=frame.angle*direction)
        self._redraw()

    def _draw(self, *_args):
        if self._disposed:
            return
        # Keep StencilView's own before/after instructions intact.
        self._art_canvas.clear()
        with self._art_canvas:
            # Same five-band wave/segment recipe as the original _draw_game;
            # that method also paints gameplay HUD/hazards, so only its small
            # trail geometry is adapted for the moving decorative body here.
            x, y, w, h = self.body_box
            unit = self.unit
            colors = ((1,.33,.58),(1,.68,.31),(1,.91,.48),(.42,.93,.68),(.31,.75,1))
            for band, color in enumerate(colors):
                for k in range(20):
                    distance = (k * 4.1 - 1) * unit
                    trail_x = x-distance if self.direction > 0 else x+w+distance
                    if not self.mascot_x <= trail_x <= self.mascot_x+self.sprite_width:
                        continue
                    trail_y = y+h/2+(band-2)*4.2*unit + sin(self.elapsed*9+k*.47)*3.2*unit
                    tw = (5 if k < 8 else 4 if k < 14 else 2) * unit
                    th = (4 if k < 11 else 3 if k < 17 else 2) * unit
                    Color(*color, max(.20, 1-k*.038))
                    Rectangle(pos=(trail_x if self.direction > 0 else trail_x-tw, trail_y), size=(tw,th))
            self._paint_camera('header')
        if self.direction < 0:
            rear, front = self._camera_layers[self._pose]
            for item in self._art_canvas.children:
                if isinstance(item, Rectangle) and item.texture in (rear, front):
                    uv = item.texture.tex_coords
                    item.tex_coords = (*uv[2:4], *uv[0:2], *uv[6:8], *uv[4:6])

    def reset_geometry(self):
        # A resize changes the emitter coordinate scale. Retire decorative
        # sheets rather than teleporting/replaying them; no real print occurs.
        self._printer.reset()

    def dispose(self):
        self._disposed = True
        self._redraw.cancel()
        self._printer.reset()
