"""Real-widget smoke for the isolated portrait v2 (run under Xvfb/Windows)."""

import os
import unittest

os.environ.setdefault("PHOTOBOOTH_AUDIO", "0")
os.environ.setdefault("PHOTOBOOTH_AD_VIDEO", "0")
os.environ.setdefault("KIVY_NO_ARGS", "1")

try:
    from photobooth.kiosk_v2.app import PortraitKioskV2App
    from photobooth.kiosk_v2.flow import ADVERT, TEMPLATES, TUTORIAL, GAME_PREVIEW
    HAS_KIVY = True
except ImportError:
    HAS_KIVY = False


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
            self.assertEqual(len(app._textures), 1)  # lazy texture caching
            self.assertIsNotNone(app._preview.texture)
            self.assertEqual(app.quantities[app.templates[0].template_id], 0)
            app._change_copies(1)
            self.assertEqual(app.quantities[app.templates[0].template_id], 1)
            self.assertEqual(quote_order(app.templates, app.quantities).total_amount, 10000)
            app._shift_template(1)
            self.assertEqual(app.template_index, 1)
            self.assertEqual(len(app._textures), 2)
            app._return_ad()
            self.assertEqual(app.navigation.page, ADVERT)
            self.assertFalse(app.navigation.tutorial_seen)
            self.assertEqual(sum(app.quantities.values()), 0)
        finally:
            app.on_stop()


if __name__ == "__main__":
    unittest.main()
