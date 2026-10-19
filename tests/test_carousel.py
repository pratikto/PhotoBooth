"""Drive MEONG's looping selector through actual pointer events and widgets.

No webcam, Drive account, payment, or customer photos are used. These checks
exercise the native swipe recognizer, cyclic boundaries, quantity isolation,
responsive layout, and retirement of a page while its carousel is animating.
"""

import os
from pathlib import Path
import tempfile
import unittest


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class CarouselTests(unittest.TestCase):
    def setUp(self):
        """Attach the real widget tree to the offscreen desktop window."""
        from kivy.core.window import Window
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        self.original_size = Window.size
        self.orders = []
        self.ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(),
                               on_start=self.orders.append, on_home_start=lambda: None)
        Window.add_widget(self.ui.shell)
        self.ui.show_template_selection(True, 'Ready')
        self.settle()

    def tearDown(self):
        """Retire any touch grab/animation before another UI test starts."""
        from kivy.core.window import Window
        if self.ui.template_carousel is not None:
            self.ui.template_carousel.deactivate()
        Window.remove_widget(self.ui.shell)
        Window.size = self.original_size

    def settle(self, frames=None, seconds=.35):
        """Let real Clock animations and layouts advance without blocking sleep."""
        from kivy.base import EventLoop
        import time
        if frames is not None:
            for _ in range(frames):
                EventLoop.idle()
        else:
            # Idle duration varies with renderer/vsync. Count real time rather
            # than assuming that eighteen frames always exceed a 220ms snap.
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                EventLoop.idle()
            # A software-rendered frame can itself consume the remaining wall
            # budget. Flush the deferred layout of its newly attached controls.
            EventLoop.idle()
            EventLoop.idle()

    def pointer(self, x, y, button=None):
        """Create a real normalized MotionEvent for Window's input pipeline."""
        from kivy.core.window import Window
        from kivy.input.motionevent import MotionEvent
        class Pointer(MotionEvent):
            def depack(self, args):
                self.sx, self.sy = args
                self.profile = ['pos']
                super().depack(args)
        event = Pointer('meong-carousel-test', str(id(self)),
                        (x / Window.width, y / Window.height), is_touch=True)
        if button:
            event.button = button
            event.profile.append('button')
        return event

    def tap(self, widget):
        """Use hit testing and grabs; do not bypass the button with dispatch."""
        from kivy.base import EventLoop
        x, y = widget.to_window(*widget.center)
        event = self.pointer(x, y)
        EventLoop.post_dispatch_input('begin', event)
        EventLoop.post_dispatch_input('end', event)
        self.settle()

    def drag(self, start, end):
        """Move far enough to distinguish a deliberate swipe from a tap."""
        from kivy.base import EventLoop
        from kivy.core.window import Window
        event = self.pointer(*start)
        EventLoop.post_dispatch_input('begin', event)
        for fraction in (.10, .25, .50, .75, 1.0):
            x = start[0] + (end[0] - start[0]) * fraction
            y = start[1] + (end[1] - start[1]) * fraction
            event.move((x / Window.width, y / Window.height))
            EventLoop.post_dispatch_input('update', event)
            self.settle(1)
        EventLoop.post_dispatch_input('end', event)
        self.settle()

    def test_arrows_wrap_both_ends_and_keep_every_frame_reachable(self):
        """First←last and last→first must work at all supported monitor sizes."""
        from kivy.core.window import Window
        for size in ((800, 600), (1200, 800), (1920, 1080)):
            with self.subTest(size=size):
                Window.size = size
                carousel = self.ui.template_carousel
                carousel.index = 0
                self.settle()
                self.tap(self.ui.carousel_previous)
                self.assertEqual(carousel.index, 11)
                self.assertEqual(self.ui.template_counter.text, '12 / 12')
                self.assertEqual(self.ui.template_name.text, 'Celebrate')
                self.tap(self.ui.carousel_next)
                self.assertEqual(carousel.index, 0)
                self.assertEqual(self.ui.template_counter.text, '01 / 12')
                self.assertEqual(self.ui.template_name.text, 'Special Day')
                self.assertEqual(sum(self.ui.quantities.values()), 0)
                self.assertTrue(self.ui.start_button.disabled)
        # Check all twelve forward destinations, not only the boundary pair.
        seen = []
        for _ in range(12):
            seen.append(self.ui.template_name.text)
            self.tap(self.ui.carousel_next)
        self.assertEqual(seen, [template.name for template in self.ui.templates])
        self.assertEqual(self.ui.template_carousel.index, 0)

    def test_actual_swipes_are_horizontal_cyclic_and_do_not_add_sessions(self):
        """Window-delivered finger motion must browse without changing payment."""
        carousel = self.ui.template_carousel
        x, y = carousel.to_window(*carousel.pos)
        left, right = x + carousel.width * .15, x + carousel.width * .85
        middle = y + carousel.height * .5
        self.drag((left, middle), (right, middle))
        self.assertEqual(carousel.index, 11)
        self.drag((right, middle), (left, middle))
        self.assertEqual(carousel.index, 0)
        self.drag((right, middle), (left, middle))
        self.assertEqual(carousel.index, 1)
        self.assertEqual(self.ui.template_name.text, 'Stitched Hearts')
        # A vertical drag over a receipt is not a request for another template.
        self.drag((x + carousel.width * .5, y + carousel.height * .2),
                  (x + carousel.width * .5, y + carousel.height * .8))
        self.assertEqual(carousel.index, 1)
        self.assertEqual(self.ui.cart_total.text, 'Rp0')
        self.assertFalse(self.orders)

    def test_quantity_buttons_are_independent_of_swipes_and_preserve_each_order(self):
        """Browse, add another design, wrap around, and edit the original count."""
        first, second = self.ui.templates[:2]
        self.tap(self.ui.quantity_buttons[first.template_id][1])
        self.assertEqual(self.ui.quantities[first.template_id], 1)
        self.assertEqual(self.ui.template_carousel.index, 0)
        self.tap(self.ui.carousel_next)
        self.tap(self.ui.quantity_buttons[second.template_id][1])
        self.tap(self.ui.quantity_buttons[second.template_id][1])
        self.assertEqual(self.ui.cart_total.text, 'Rp25.000')
        self.tap(self.ui.carousel_previous)
        self.assertEqual(self.ui.quantity_labels[first.template_id].text, '1 cetak')
        self.tap(self.ui.quantity_buttons[first.template_id][0])
        self.assertEqual(self.ui.cart_total.text, 'Rp15.000')
        self.assertEqual(self.ui.quantities[second.template_id], 2)
        self.assertTrue(self.ui.quantity_buttons[first.template_id][0].disabled)
        self.tap(self.ui.start_button)
        self.assertEqual(self.orders, [{second.template_id: 2}])

    def test_resize_preserves_focus_and_order_and_caps_wide_screen_content(self):
        """A maximized monitor must not recreate the screenshot's giant rows."""
        from kivy.core.window import Window
        from kivy.metrics import dp
        carousel = self.ui.template_carousel
        carousel.index = 7
        self.ui._change_quantity(self.ui.templates[7].template_id, 2)
        start = self.ui.start_button
        for size in ((800, 600), (1200, 800), (1920, 1080), (800, 600)):
            Window.size = size
            self.settle()
            self.assertIs(self.ui.template_carousel, carousel)
            self.assertIs(self.ui.start_button, start)
            self.assertEqual(carousel.index, 7)
            self.assertEqual(self.ui.template_name.text, 'Scrapbook Memories')
            self.assertEqual(self.ui.cart_total.text, 'Rp15.000')
            self.assertLessEqual(self.ui.shell.width - self.ui.shell.padding[0]
                                 - self.ui.shell.padding[2], dp(1440) + 1)
            for widget in (self.ui.carousel_previous, self.ui.carousel_next, start):
                x, y = widget.to_window(*widget.pos)
                self.assertGreaterEqual(x, -1)
                self.assertGreaterEqual(y, -1)
                self.assertLessEqual(x + widget.width, Window.width + 1)
                self.assertLessEqual(y + widget.height, Window.height + 1)

    def test_retired_carousel_cannot_change_payment_or_a_new_customers_focus(self):
        """Animations and queued arrow releases retire with the picker page."""
        carousel = self.ui.template_carousel
        old_next = self.ui.carousel_next
        carousel.load_next()
        self.ui.show_payment('Special Day × 1', 1, 5000, lambda: None, lambda: None)
        self.settle()
        self.assertTrue(carousel.disabled)
        old_next.dispatch('on_release')
        self.settle()
        self.assertEqual(self.ui.current_screen, 'payment')
        self.assertEqual(self.ui.payment_total, 5000)
        self.ui.show_welcome(True, 'Ready')
        self.ui.show_template_selection(True, 'Ready')
        self.settle()
        self.assertEqual(self.ui.template_carousel.index, 0)
        self.assertEqual(self.ui.cart_total.text, 'Rp0')

    def test_fast_arrow_releases_do_not_restart_a_snap_indefinitely(self):
        """A burst of clicks must complete a slide rather than freeze between two."""
        from kivy.clock import Clock
        for delay in (0, .05, .10, .15):
            Clock.schedule_once(lambda _dt: self.ui.carousel_next.dispatch('on_release'), delay)
        self.settle(seconds=.33)
        self.assertEqual(self.ui.template_carousel.index, 1)
        self.assertEqual(self.ui.template_name.text, 'Stitched Hearts')
        self.assertEqual(self.ui.cart_total.text, 'Rp0')

    def test_rendered_cart_is_bright_blue_and_logo_source_is_unchanged(self):
        """Inspect painted pixels for the requested colorful product theme."""
        from PIL import Image
        from kivy.core.window import Window
        from photobooth.ui_brand import LOGO_PATH
        before = LOGO_PATH.read_bytes()
        cart = self.ui.cart_total.parent
        x, y = cart.to_window(*cart.pos)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'brand.png'
            self.ui.shell.export_to_png(str(path))
            with Image.open(path) as screenshot:
                red, green, blue = screenshot.convert('RGB').getpixel(
                    (round(x + 12), round(Window.height - y - 28)))
        self.assertGreater(blue, red + 100)
        self.assertGreater(blue, green + 80)
        self.assertEqual(LOGO_PATH.read_bytes(), before)
        self.assertEqual(self.ui.brand.text, 'MEONG PHOTOBOOTH')
