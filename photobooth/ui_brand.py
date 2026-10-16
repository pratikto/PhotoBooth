"""MEONG's visual system and cyclic template browsing widgets.

The approved pixel camera-cat is the brand source. Cool paper, dark camera-body
ink, lens blue, and a small cheek-pink accent are reused across every screen.
No new mascot or substitute wordmark is drawn. Artwork is resolved relative to
this module so launching the application from another directory remains safe.
"""

from functools import lru_cache
from pathlib import Path

from PIL import Image
from photobooth.branding import LOGO_PATH, load_logo
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.widget import Widget


PAPER = (0.953, 0.961, 0.980, 1)          # Cool off-white thermal paper.
WHITE = (1, 1, 1, 1)
INK = (0.067, 0.086, 0.125, 1)            # Camera-body black, without pure-black glare.
BLUE = (0.125, 0.310, 0.910, 1)           # The approved mascot's camera lens.
SOFT = (0.906, 0.937, 1, 1)
GREY = (0.365, 0.408, 0.482, 1)
EDGE = (0.824, 0.855, 0.914, 1)
DISABLED_INK = (0.255, 0.302, 0.384, 1)
PINK = (1, 0.710, 0.839, 1)
CYAN = (0.77, 0.945, 1, 1)
BLUSH = (1, 0.91, 0.955, 1)
ROSE = (0.663, 0.149, 0.345, 1)
LIGHT_INK = (0.75, 0.80, 0.89, 1)


def picture(image, *, crisp=False):
    """Create a local RGB texture without network loading or asset mutation."""
    rgb = image.convert('RGB')
    texture = Texture.create(size=rgb.size, colorfmt='rgb')
    texture.flip_vertical()
    texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
    if crisp:
        texture.mag_filter = texture.min_filter = 'nearest'
    return KivyImage(texture=texture, fit_mode='contain')


@lru_cache(maxsize=1)
def brand_parts():
    """Read the original logo, keeping its mascot and original wordmark intact.

    The header arranges the two existing parts horizontally so both remain
    readable on a kiosk. The complete unmodified logo is used on welcome.
    These are display crops only; the QR resolves the same shared source.
    """
    logo = load_logo().copy()
    width, height = logo.size
    mascot = logo.crop((0, 0, width, round(height * .635)))
    wordmark = logo.crop((round(width * .04), round(height * .65),
                          round(width * .96), height))
    return logo, mascot, wordmark


class Panel(BoxLayout):
    """A restrained card with a hairline border and optional focus outline.

    Shadow, outline, and fill follow geometry. Selected receipt cards use blue
    only at their boundary; the white artwork and its scan margin remain white.
    Root surfaces opt out of radius/shadow rather than looking like giant cards.
    """
    selected = BooleanProperty(False)

    def __init__(self, fill=WHITE, radius=16, shadow=False, border=True, **kwargs):
        super().__init__(**kwargs)
        self._default_fill = tuple(fill)
        self._radius = dp(radius)
        self._show_border = border
        with self.canvas.before:
            self._shadow_color = Color(0.055, 0.08, 0.15, .055 if shadow else 0)
            self._shadow = RoundedRectangle(radius=[self._radius])
            self._fill_color = Color(*fill)
            self._background = RoundedRectangle(radius=[self._radius])
            self._line_color = Color(*EDGE[:3], .62 if border else 0)
            self._outline = Line(width=dp(.65))
            self._selection_color = Color(*BLUE[:3], 0)
            self._selection_outline = Line(width=dp(1.7))
        self.bind(pos=self._paint, size=self._paint, selected=self._paint)
        self._paint()

    def _paint(self, *_args):
        """Keep all painted elements aligned after any responsive resize."""
        self._shadow.pos = (self.x, self.y - dp(3))
        self._shadow.size = self.size
        self._background.pos, self._background.size = self.pos, self.size
        self._fill_color.rgba = self._default_fill
        box = (self.x + dp(1), self.y + dp(1), max(0, self.width - dp(2)),
               max(0, self.height - dp(2)), self._radius)
        self._outline.rounded_rectangle = box
        self._selection_outline.rounded_rectangle = box
        self._selection_color.rgba = BLUE if self.selected else (*BLUE[:3], 0)


class BrandLockup(BoxLayout):
    """Use the real approved mascot AND its pixel-lettered product name."""

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(10), **kwargs)
        self.text = 'MEONG PHOTOBOOTH'  # Readable public identity for hosts/tests.
        _, mascot, wordmark = brand_parts()
        self.mascot = picture(mascot)
        self.mascot.size_hint_x = None
        self.mascot.width = dp(100)
        self.add_widget(self.mascot)
        self.wordmark = picture(wordmark)
        self.add_widget(self.wordmark)



class FlowSteps(BoxLayout):
    """Four compact progress tabs with one clear active blue step."""

    def __init__(self, **kwargs):
        super().__init__(spacing=dp(6), **kwargs)
        self.tabs = []
        for number, name in enumerate(('Pilih', 'Bayar', 'Foto', 'Hasil'), 1):
            card = Panel(fill=PAPER, radius=8, border=False, padding=dp(6))
            label = Label(text=f'{number:02d}  {name}', font_size=dp(12), bold=True,
                          color=GREY, halign='center', valign='middle')
            label.bind(size=lambda w, size: setattr(w, 'text_size', size))
            card.add_widget(label)
            self.add_widget(card)
            self.tabs.append((card, label))
        self.set_active(1)
        self.bind(width=self._fit)

    def _fit(self, *_args):
        """Keep the four steps readable together at the 800-pixel breakpoint."""
        for _, label in self.tabs:
            label.font_size = dp(11 if self.width < dp(390) else 12)

    def set_active(self, active):
        """Change only presentation; navigation still belongs to the controller."""
        for index, (card, label) in enumerate(self.tabs, 1):
            card._default_fill = BLUE if index == active else WHITE
            card._paint()
            label.color = WHITE if index == active else (INK if index < active else GREY)


class PixelRule(Widget):
    """A small lens-blue/pink pixel signature, used instead of generic artwork."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._draw, pos=self._draw)
        self._draw()

    def _draw(self, *_args):
        self.canvas.clear()
        with self.canvas:
            for index, color in enumerate((INK, BLUE, PINK)):
                Color(*color)
                Rectangle(pos=(self.x + index * dp(15), (self.y + self.height / 2) - dp(4)),
                          size=(dp(8), dp(8)))


class CarouselDots(Widget):
    """Pixel-sized position markers that update without rebuilding the deck."""
    index = NumericProperty(0)

    def __init__(self, count, **kwargs):
        super().__init__(**kwargs)
        self.count = count
        self.bind(size=self._draw, pos=self._draw, index=self._draw)

    def _draw(self, *_args):
        self.canvas.clear()
        gap, dot = dp(12), dp(5)
        left = self.x + self.width / 2 - (self.count - 1) * gap / 2
        with self.canvas:
            for index in range(self.count):
                Color(*(BLUE if index == self.index else EDGE))
                Rectangle(pos=(left + index * gap - dot / 2, self.y + self.height / 2 - dot / 2),
                          size=(dot, dot))


class ReceiptSlide(FloatLayout):
    """A focused receipt plus two smaller previews of its cyclic neighbors.

    Preview artwork stays in its 1:3 ratio at every size. Quantity controls live
    outside the swipe surface, preventing a drag from accidentally adding a
    session. Only one central card per actual template owns selection state.
    """

    def __init__(self, center, previous, following, **kwargs):
        super().__init__(**kwargs)
        # Bright lens-blue, cyan, and cheek-pink surfaces belong to the GUI.
        # The actual thermal receipt artwork remains the customer's approved
        # design; these accents never become part of the exported photograph.
        with self.canvas.before:
            Color(*SOFT)
            self._stage = RoundedRectangle(radius=[dp(26)])
            Color(*CYAN)
            self._cyan = Ellipse()
            Color(*BLUSH)
            self._blush = Ellipse()
        self.center_card = Panel(radius=9, shadow=True, padding=dp(10),
                                 size_hint=(None, None))
        self.center_card.add_widget(picture(center))
        self.side_cards = []
        for preview in (previous, following):
            side = Panel(radius=8, padding=dp(7), size_hint=(None, None), opacity=.82)
            side.add_widget(picture(preview))
            self.side_cards.append(side)
            self.add_widget(side)
        self.add_widget(self.center_card)
        self.bind(size=self._arrange, pos=self._arrange)

    def _arrange(self, *_args):
        """Use the available HEIGHT to size thermal strips, never stretch them."""
        height = max(dp(60), self.height - dp(14))
        self._stage.pos = (self.x + self.width * .04, self.y + self.height * .12)
        self._stage.size = (self.width * .92, self.height * .70)
        self._cyan.pos = (self.x + self.width * .07, self.y + self.height * .14)
        self._cyan.size = (min(dp(150), self.width * .3), min(dp(150), self.height * .6))
        self._blush.pos = (self.right - self.width * .28, self.y + self.height * .50)
        self._blush.size = (min(dp(120), self.width * .23), min(dp(120), self.height * .44))
        width = max(dp(40), (height - dp(20)) / 3 + dp(20))
        self.center_card.size = (width, height)
        self.center_card.pos = (self.x + self.width / 2 - width / 2, self.y + self.height / 2 - height / 2)
        for index, side in enumerate(self.side_cards):
            side.size = (width * .73, height * .73)
            side.pos = (self.x + self.width * (.16 if index == 0 else .84) - side.width / 2,
                        self.y + self.height / 2 - side.height / 2)


class TemplateCarousel(Carousel):
    """Kivy's native swipe recognizer, with explicit looping and mouse support.

    Kivy owns drag thresholds, touch grabs, snapping, and animation. We do not
    simulate a swipe with a click counter. The surrounding arrows offer the
    same navigation to a mouse user, while wheel events are handled here.
    """

    def __init__(self, **kwargs):
        super().__init__(direction='right', loop=True, anim_move_duration=.22,
                         anim_cancel_duration=.16, min_move=.12,
                         scroll_distance=dp(18), scroll_timeout=180,
                         ignore_perpendicular_swipes=True, **kwargs)
        self._navigation_busy = False
        self._navigation_guard = None
        self._focus_event = None
        self._requested_index = None
        self.bind(index=self._finish_navigation)

    def _finish_navigation(self, *_args):
        """Unlock as soon as the native carousel commits the new visible index."""
        self._navigation_busy = False
        if self._navigation_guard is not None:
            self._navigation_guard.cancel()
            self._navigation_guard = None

    def navigate(self, direction):
        """Snap once per deliberate arrow/wheel action, including at the ends.

        Restarting Kivy's current animation on every rapid arrow release can
        prevent it from ever reaching the next index. Ignore duplicate actions
        during a short snap; leave native finger-drag recognition independent.
        """
        if (self.disabled or self._navigation_busy or self._touch is not None
                or abs(self._offset) > dp(.5)):
            return
        self._navigation_busy = True
        if direction > 0:
            self.load_next()
        else:
            self.load_previous()
        def release(_dt):
            self._navigation_busy = False
            self._navigation_guard = None
        self._navigation_guard = Clock.schedule_once(release, self.anim_move_duration + .05)

    def request_index(self, index):
        """Animate to an ordered design; the latest click wins during a swipe.

        Cart navigation never edits quantities. A request waits for an active
        finger drag or snap to finish instead of corrupting Kivy's touch state.
        A single retry event is retired along with the page.
        """
        if self.disabled or not self.slides:
            return
        self._requested_index = int(index) % len(self.slides)
        self._schedule_focus()

    def _schedule_focus(self):
        if self._focus_event is None and not self.disabled:
            self._focus_event = Clock.schedule_once(self._apply_focus, .06)

    def _apply_focus(self, _dt):
        self._focus_event = None
        if self.disabled or self._requested_index is None:
            return
        if self._navigation_busy or self._touch is not None or abs(self._offset) > dp(.5):
            self._schedule_focus()
            return
        index, self._requested_index = self._requested_index, None
        if index != self.index:
            self._navigation_busy = True
            self.load_slide(self.slides[index])
            self._navigation_guard = Clock.schedule_once(
                self._finish_navigation, self.anim_move_duration + .06)

    def on_touch_down(self, touch):
        """Allow a mouse wheel to browse the same cyclic list as a finger drag."""
        if self.disabled:
            return False
        if self.collide_point(*touch.pos) and getattr(touch, 'is_mouse_scrolling', False):
            if touch.button in ('scrolldown', 'scrollright'):
                self.navigate(1)
            else:
                self.navigate(-1)
            return True
        return super().on_touch_down(touch)

    def deactivate(self):
        """Retire animations and grabs when the controller leaves this screen."""
        self.disabled = True
        self._requested_index = None
        if self._focus_event is not None:
            self._focus_event.cancel()
            self._focus_event = None
        Animation.cancel_all(self)
        if self._navigation_guard is not None:
            self._navigation_guard.cancel()
            self._navigation_guard = None
        if self._change_touch_mode_ev is not None:
            self._change_touch_mode_ev.cancel()
        if self._touch is not None:
            self._touch.ungrab(self)
            self._touch = None
