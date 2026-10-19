"""Regression tests for mandatory tutorial entry from advertising."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from photobooth.ui_kiosk import KioskExperienceMixin


class TutorialEntryTests(unittest.TestCase):
    def test_both_advertising_entry_routes_open_guide_before_layout(self):
        for source in ("manual", "face_prompt"):
            with self.subTest(source=source):
                events = Mock()
                forbidden_direct_layout = Mock()
                ui = SimpleNamespace(
                    current_screen="advert",
                    _ad_player=SimpleNamespace(ad_id="sample-video"),
                    _camera_ready=True,
                    callbacks={"on_home_start": forbidden_direct_layout},
                    ad_events=events,
                )

                def show_welcome(camera_ready, status):
                    self.assertTrue(camera_ready)
                    self.assertIn("layout", status)
                    ui.current_screen = "welcome"

                ui.show_welcome = show_welcome
                KioskExperienceMixin._enter_from_ad(ui, source)
                forbidden_direct_layout.assert_not_called()
                events.write.assert_called_once_with(
                    "photo_entry", ad_id="sample-video",
                    placement="idle", source=source,
                )
                self.assertEqual(ui.current_screen, "welcome")

    def test_stale_entry_callback_cannot_leave_another_page(self):
        ui = SimpleNamespace(
            current_screen="payment", show_welcome=Mock(),
            ad_events=Mock(),
        )
        KioskExperienceMixin._enter_from_ad(ui, "manual")
        ui.show_welcome.assert_not_called()


if __name__ == "__main__":
    unittest.main()
