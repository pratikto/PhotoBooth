"""Native strip gesture/motion; no page routing or order state in this widget."""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.stencilview import StencilView

class SwipeGallery(BoxLayout):
    """Real horizontal touch gesture for the approved strip carousel.

    Grab each pointer stream until release so Windows touch/pen providers keep
    delivering its move/up events. Only gestures ending inside turn a template.
    Predominantly vertical and short motions are ignored.
    """

    def __init__(self, on_swipe, **kwargs):
        self._on_swipe = on_swipe
        self._touch_origins = {}
        super().__init__(**kwargs)

    @staticmethod
    def swipe_step(dx, dy, *, threshold=None):
        if abs(dx) < (dp(54) if threshold is None else threshold) or abs(dx) <= abs(dy) * 1.35:
            return 0
        return -1 if dx > 0 else 1

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if not self.collide_point(*touch.pos) or touch.is_mouse_scrolling:
            return False
        if self._touch_origins:
            return True  # One active gesture, including multi-touch devices.
        # Normalized window coordinates survive Kivy's parent/local transforms.
        self._touch_origins[touch.uid] = (touch, touch.sx, touch.sy, tuple(Window.size))
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self or touch.uid in self._touch_origins:
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        # Kivy sends both normal and grabbed dispatch; consume only the latter.
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        origin = self._touch_origins.pop(touch.uid, None)
        touch.ungrab(self)
        if origin is None or not self.collide_point(*touch.pos):
            return True
        _, sx, sy, viewport = origin
        if tuple(Window.size) != viewport:
            return True  # A resize in the middle of a drag is not a swipe.
        x0, _ = self.to_window(0, 0)
        x1, _ = self.to_window(dp(54), 0)
        step = self.swipe_step((touch.sx - sx) * Window.width,
                               (touch.sy - sy) * Window.height,
                               threshold=abs(x1 - x0))
        if step:
            self._on_swipe(step)
        return True

    def cancel_motion(self):
        """A retired/suspended page must not retain a native pointer grab."""
        for touch, _sx, _sy, _viewport in self._touch_origins.values():
            touch.ungrab(self)
        self._touch_origins.clear()

    def dispose(self):
        self.cancel_motion()


class StripCarousel(SwipeGallery):
    """Three true 1:3 strips; drag follows the finger and release eases to a slot.

    Five pooled Images let the incoming neighbour slide in without allocating
    widgets per frame. The application commits one selection immediately; rapid
    inputs replace current motion instead of queuing stale navigation callbacks.
    """

    offset = NumericProperty(0)

    def __init__(self, on_swipe, **kwargs):
        super().__init__(on_swipe, **kwargs)
        self.viewport = StencilView()
        self.add_widget(self.viewport)
        self._images = {}
        for rank in (-2, 2, -1, 1, 0):
            image = Image(fit_mode='contain', size_hint=(None, None))
            self._images[rank] = image
            self.viewport.add_widget(image)
        self.previous_image = self._images[-1]
        self.selected_image = self._images[0]
        self.next_image = self._images[1]
        self._textures = None
        self._animation = None
        self._moving = self._disposed = False
        self._drag_uid = None
        self._layout_trigger = Clock.create_trigger(self._arrange, -1)
        self.bind(offset=self._arrange)
        self.viewport.bind(pos=self._bounds_changed, size=self._bounds_changed)
        self._arrange()

    def _bounds_changed(self, *_args):
        if self._disposed:
            return
        self.cancel_motion()
        self._layout_trigger()

    def _slot(self, rank):
        width, height = self.viewport.size
        hero_width = max(1, min(width * .38, height * .94 / 3))
        centers = (-.25, .15, .5, .85, 1.25)
        scales = (.60, .72, 1, .72, .60)
        alphas = (0, .78, 1, .78, 0)
        index = max(0, min(4, rank + 2))
        lo = int(index)
        hi = min(4, lo + 1)
        fraction = index - lo
        mix = lambda values: values[lo] + (values[hi] - values[lo]) * fraction
        strip_width = hero_width * mix(scales)
        left, bottom = self.viewport.pos
        return (left + width * mix(centers) - strip_width / 2,
                bottom + (height - strip_width * 3) / 2,
                strip_width, strip_width * 3, mix(alphas))

    def _arrange(self, *_args):
        if self._disposed:
            return
        for rank, image in self._images.items():
            x, y, width, height, alpha = self._slot(rank + self.offset)
            image.pos = (x, y)
            image.size = (width, height)
            image.opacity = alpha if image.texture is not None else 0

    def _settle(self, *_args):
        if self._animation is not None:
            self._animation.cancel(self)
        self._animation = None
        self._moving = False
        if self._textures is not None:
            for rank, image in self._images.items():
                image.texture = self._textures[rank + 2]
        self.offset = 0
        self._arrange()

    def show(self, textures, *, step=0):
        if self._disposed:
            return
        textures = tuple(textures)
        old = self._textures
        drag_offset = self.offset if self._drag_uid is not None and not self._moving else 0
        self._settle()
        self._textures = textures
        if old is None or step not in (-1, 1):
            self._settle()
            return
        # Both offscreen neighbours must already exist during a held drag.
        # Keep the old five-picture window through release, then rebase it in
        # _settle; this also preserves the incoming picture when reversing.
        for rank, image in self._images.items():
            image.texture = old[rank + 2]
        self.offset = drag_offset
        self._moving = True
        self._arrange()
        self._animation = Animation(offset=-step, duration=.20, t='out_cubic')
        self._animation.bind(on_complete=self._settle)
        self._animation.start(self)

    def on_touch_down(self, touch):
        handled = super().on_touch_down(touch)
        if touch.uid in self._touch_origins and self._drag_uid is None:
            self._settle()
            self._drag_uid = touch.uid
        return handled

    def on_touch_move(self, touch):
        handled = super().on_touch_move(touch)
        origin = self._touch_origins.get(touch.uid)
        if origin is None or self._drag_uid != touch.uid or self._disposed:
            return handled
        _, sx, sy, viewport = origin
        if tuple(Window.size) != viewport:
            self.cancel_motion()
            return handled
        dx, dy = (touch.sx - sx) * Window.width, (touch.sy - sy) * Window.height
        if abs(dx) > abs(dy) * 1.35:
            left, _ = self.to_window(self.x, self.y)
            right, _ = self.to_window(self.right, self.y)
            self.offset = max(-.95, min(.95, dx / max(1, (right - left) * .35)))
        elif abs(dy) > dp(6):
            self.offset = 0
        return handled

    def on_touch_up(self, touch):
        owned = touch.grab_current is self and touch.uid in self._touch_origins
        handled = super().on_touch_up(touch)
        if owned:
            self._drag_uid = None
            if not self._moving and not self._disposed and self.offset:
                self._animation = Animation(offset=0, duration=.12, t='out_cubic')
                self._animation.bind(on_complete=self._settle)
                self._animation.start(self)
        return handled

    def cancel_motion(self):
        super().cancel_motion()
        self._drag_uid = None
        if hasattr(self, '_images'):
            self._settle()

    def dispose(self):
        self.cancel_motion()
        self._disposed = True
        self._layout_trigger.cancel()


