"""Real-widget smoke for the isolated portrait v2 (run under Xvfb/Windows)."""

import os
import unittest

os.environ.setdefault("PHOTOBOOTH_AUDIO", "0")
os.environ.setdefault("PHOTOBOOTH_AD_VIDEO", "0")
os.environ.setdefault("KIVY_NO_ARGS", "1")

try:
    import kivy  # noqa: F401
except ImportError:
    HAS_KIVY = False
else:
    HAS_KIVY = True
    # After Kivy is installed, errors in v2 imports must FAIL, not be skipped.
    from photobooth.kiosk_v2.app import PortraitKioskV2App, SwipeGallery
    from photobooth.kiosk_v2.illustrations import TutorialIcon
    from photobooth.kiosk_v2.theme import ArcadeButton
    from photobooth.kiosk_v2.flow import ADVERT, TEMPLATES, TUTORIAL, GAME_PREVIEW


@unittest.skipUnless(HAS_KIVY, "Kivy not available in pure-Python test environment")
class PortraitKivySmokeTests(unittest.TestCase):
    def test_advert_game_invitation_tutorial_and_real_12_strip_gallery(self):
        from photobooth.workflow import quote_order

        app = PortraitKioskV2App()
        app.build()
        try:
            self.assertEqual(app.navigation.page, ADVERT)
            self.assertEqual(app.stage.current, ADVERT)
            self.assertIsNotNone(app._ad_player)
            # Invitation is a nonmodal overlay on the advertising media host.
            app._show_invitation()
            self.assertIs(app._invitation.parent, app._advert_host)
            self.assertEqual(app.navigation.page, ADVERT)
            app._choose_game("face_preview")
            self.assertEqual(app.navigation.page, GAME_PREVIEW)
            self.assertIsNone(app._ad_player)
            # Safe skip-to-photo: no receipt claim or discount in this prototype.
            app._choose_photo("skip_game")
            self.assertEqual(app.navigation.page, TUTORIAL)
            app._complete_tutorial()
            self.assertEqual(app.navigation.page, TEMPLATES)
            self.assertTrue(app.navigation.tutorial_seen)
            self.assertEqual(len(app.templates), 12)
            self.assertEqual(len(app._textures), 3)  # selected + adjacent master strips
            self.assertIsNotNone(app._preview.texture)
            self.assertEqual(app.quantities[app.templates[0].template_id], 0)
            app._change_copies(1)
            self.assertEqual(app.quantities[app.templates[0].template_id], 1)
            self.assertEqual(quote_order(app.templates, app.quantities).total_amount, 10000)
            app._shift_template(1)
            self.assertEqual(app.template_index, 1)
            self.assertEqual(len(app._textures), 4)  # only next new strip loaded
            app._return_ad()
            self.assertEqual(app.navigation.page, ADVERT)
            self.assertFalse(app.navigation.tutorial_seen)
            self.assertEqual(sum(app.quantities.values()), 0)
        finally:
            app.on_stop()


    def test_illustrated_tutorial_and_game_intro_are_real_pages_not_payment(self):
        app = PortraitKioskV2App()
        app.build()
        try:
            def widgets(root):
                yield root
                for child in root.children:
                    yield from widgets(child)

            app._choose_photo("help")
            self.assertEqual(app.navigation.page, TUTORIAL)
            figures = [w for w in widgets(app.stage)
                       if isinstance(w, TutorialIcon)]
            self.assertEqual({w.kind for w in figures},
                             {"template", "payment", "camera", "print"})
            app._return_ad()
            app._choose_game("manual")
            self.assertEqual(app.navigation.page, GAME_PREVIEW)
            buttons = [w for w in widgets(app.stage)
                       if isinstance(w, ArcadeButton)]
            scanner = [b for b in buttons if "SCAN STRUK" in b.text]
            self.assertEqual(len(scanner), 1)
            self.assertTrue(scanner[0].disabled)
            self.assertFalse(hasattr(app.navigation, "discount_amount"))
            self.assertFalse(hasattr(app.navigation, "paid"))
            app._choose_photo("skip_game")
            self.assertEqual(app.navigation.page, TUTORIAL)
        finally:
            app.on_stop()

    def test_shared_advert_entry_has_help_and_game_without_second_home(self):
        app = PortraitKioskV2App()
        app.build()
        try:
            def buttons(root):
                all_buttons = []
                if isinstance(root, ArcadeButton):
                    all_buttons.append(root)
                for child in root.children:
                    all_buttons.extend(buttons(child))
                return all_buttons

            labels = {w.text for w in buttons(app.stage)}
            self.assertIn("MULAI FOTO", labels)
            self.assertIn("MAIN MEONG FLY", labels)
            self.assertIn("CARA PAKAI", labels)
            app._show_invitation()
            self.assertEqual(app.stage.current, ADVERT)
            labels = {w.text for w in buttons(app._invitation)}
            self.assertEqual({"AYO FOTO", "MAIN MEONG FLY",
                              "NANTI SAJA"}, labels)
            app._return_ad()
            self.assertEqual(app.stage.current, ADVERT)
        finally:
            app.on_stop()


    def test_unavailable_actions_keep_readable_text_without_becoming_touchable(self):
        from photobooth.kiosk_v2.theme import MUTED, rgba
        button = ArcadeButton("PEMBAYARAN (BELUM TERHUBUNG)")
        button.disabled = True
        self.assertEqual(tuple(button.disabled_color), rgba(MUTED))
        self.assertTrue(button.disabled)

    def test_retired_buttons_and_swipes_cannot_change_next_visit(self):
        app = PortraitKioskV2App()
        app.build()
        try:
            app._choose_photo()
            old_done = next(w for w in app.stage.walk()
                            if isinstance(w, ArcadeButton) and w.text == "LANJUT PILIH TEMPLATE")
            app._complete_tutorial()
            old_gallery = next(w for w in app.stage.walk() if isinstance(w, SwipeGallery))
            app._return_ad()
            app._choose_photo()
            old_done.dispatch("on_release")
            self.assertEqual(app.navigation.page, TUTORIAL)
            self.assertFalse(app.navigation.tutorial_seen)
            app._complete_tutorial()
            old_gallery._on_swipe(1)
            self.assertEqual(app.template_index, 0)
        finally:
            app.on_stop()

    def test_pause_blocks_touch_and_timeout_resume_starts_fresh_idle_period(self):
        import time
        app = PortraitKioskV2App()
        app.build()
        try:
            app._choose_photo()
            done = next(w for w in app.stage.walk()
                        if isinstance(w, ArcadeButton) and w.text == "LANJUT PILIH TEMPLATE")
            app.on_pause()
            done.dispatch("on_release")
            app._last_activity = time.monotonic() - app.catalog.timing.landing_idle - 1
            app._tick(0)
            self.assertEqual(app.navigation.page, TUTORIAL)
            app.on_resume()
            app._tick(0)
            self.assertEqual(app.navigation.page, TUTORIAL)
            done.dispatch("on_release")
            self.assertEqual(app.navigation.page, TEMPLATES)
            app._change_copies(1)
            app._last_activity = time.monotonic() - app.catalog.timing.landing_idle - 1
            app._tick(0)
            self.assertEqual(app.navigation.page, ADVERT)
            self.assertEqual(sum(app.quantities.values()), 0)
            self.assertFalse(app.navigation.tutorial_seen)
        finally:
            app.on_stop()

    def test_touch_targets_and_tutorial_scroll_at_both_portrait_sizes(self):
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.input.motionevent import MotionEvent
        from kivy.uix.scrollview import ScrollView

        class Pointer(MotionEvent):
            def depack(self, args):
                self.sx, self.sy = args
                self.profile = ['pos']
                super().depack(args)

        def settle():
            for _ in range(4):
                EventLoop.idle()

        original = Window.size
        try:
            for width, height in ((800, 1280), (452, 900)):
                with self.subTest(viewport=(width, height)):
                    Window.size = (width, height)
                    app = PortraitKioskV2App()
                    Window.add_widget(app.build())
                    try:
                        settle()
                        start = next(w for w in app.stage.walk()
                                     if isinstance(w, ArcadeButton) and w.text == "MULAI FOTO")
                        x, y = start.to_window(*start.center)
                        event = Pointer('portrait-test', f'{width}',
                                        (x / Window.width, y / Window.height), is_touch=True)
                        EventLoop.post_dispatch_input('begin', event)
                        EventLoop.post_dispatch_input('end', event)
                        settle()
                        self.assertEqual(app.navigation.page, TUTORIAL)
                        guide = next(w for w in app.stage.walk() if isinstance(w, ScrollView))
                        guide.scroll_y = 0
                        settle()
                        final_icon = next(w for w in app.stage.walk()
                                          if isinstance(w, TutorialIcon) and w.kind == 'print')
                        _, icon_y = final_icon.to_window(*final_icon.center)
                        _, guide_y = guide.to_window(guide.x, guide.y)
                        self.assertGreater(icon_y, guide_y)
                        self.assertLess(icon_y, guide_y + guide.height)
                        for route in (lambda: None, app._complete_tutorial,
                                      app._return_ad, app._choose_game):
                            route()
                            settle()
                            for button in (w for w in app.stage.walk() if isinstance(w, ArcadeButton)):
                                x, y = button.to_window(button.x, button.y)
                                self.assertGreaterEqual(button.height, 48)
                                self.assertGreaterEqual(x, 0)
                                self.assertGreaterEqual(y, 0)
                                self.assertLessEqual(x + button.width, width + 1)
                                self.assertLessEqual(y + button.height, height + 1)
                    finally:
                        app.on_stop()
                        Window.remove_widget(app.stage)
        finally:
            Window.size = original

    def test_carousel_swipe_uses_horizontal_direction_and_rejects_vertical(self):
        self.assertEqual(SwipeGallery.swipe_step(-90, 5), 1)
        self.assertEqual(SwipeGallery.swipe_step(90, -4), -1)
        self.assertEqual(SwipeGallery.swipe_step(12, 0), 0)
        self.assertEqual(SwipeGallery.swipe_step(80, 160), 0)


if __name__ == "__main__":
    unittest.main()
