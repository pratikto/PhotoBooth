"""Pure navigation regression for the opt-in portrait GUI."""

import unittest

from photobooth.kiosk_v2.flow import (
    ADVERT, GAME_PREVIEW, TEMPLATES, TUTORIAL, NavigationError, VisitFlow,
)


class PortraitVisitFlowTests(unittest.TestCase):
    def test_first_photo_entry_always_requires_tutorial(self):
        visit = VisitFlow()
        self.assertEqual(visit.begin_photo(), TUTORIAL)
        self.assertFalse(visit.tutorial_seen)
        self.assertEqual(visit.complete_tutorial(), TEMPLATES)
        self.assertTrue(visit.tutorial_seen)

    def test_game_entry_is_same_advert_entry_not_a_second_home(self):
        visit = VisitFlow()
        self.assertEqual(visit.begin_game_preview("face_invitation"), GAME_PREVIEW)
        self.assertEqual(visit.entry_source, "face_invitation")
        self.assertEqual(visit.begin_photo("after_game_preview"), TUTORIAL)
        self.assertEqual(visit.complete_tutorial(), TEMPLATES)

    def test_tutorial_marked_only_after_real_completion(self):
        visit = VisitFlow()
        visit.begin_photo()
        self.assertFalse(visit.tutorial_seen)
        with self.assertRaises(NavigationError):
            visit.begin_game_preview()
        self.assertFalse(visit.tutorial_seen)

    def test_no_duplicate_completion_or_stale_taps(self):
        visit = VisitFlow()
        with self.assertRaises(NavigationError):
            visit.complete_tutorial()
        visit.begin_photo()
        visit.complete_tutorial()
        with self.assertRaises(NavigationError):
            visit.complete_tutorial()

    def test_return_to_advert_resets_only_visit_scoped_state(self):
        visit = VisitFlow()
        visit.begin_photo()
        visit.complete_tutorial()
        self.assertEqual(visit.to_advertising(), ADVERT)
        self.assertFalse(visit.tutorial_seen)
        self.assertIsNone(visit.entry_source)
        self.assertEqual(visit.begin_photo(), TUTORIAL)

    def test_inactivity_only_ends_browsing(self):
        visit = VisitFlow()
        self.assertFalse(visit.browse_timeout())
        visit.begin_game_preview()
        self.assertTrue(visit.browse_timeout())
        self.assertEqual(visit.page, ADVERT)
        visit.begin_photo()
        self.assertTrue(visit.browse_timeout())
        self.assertEqual(visit.page, ADVERT)

    def test_timeout_from_templates_resets_tutorial_and_entry_source(self):
        visit = VisitFlow()
        visit.begin_photo("manual")
        visit.complete_tutorial()
        self.assertTrue(visit.browse_timeout())
        self.assertEqual(visit.page, ADVERT)
        self.assertFalse(visit.tutorial_seen)
        self.assertIsNone(visit.entry_source)
        self.assertEqual(visit.begin_photo("new_visitor"), TUTORIAL)

    def test_rejected_stale_actions_leave_page_unchanged(self):
        visit = VisitFlow()
        visit.begin_photo()
        with self.assertRaises(NavigationError):
            visit.begin_photo()
        self.assertEqual(visit.page, TUTORIAL)
        with self.assertRaises(NavigationError):
            visit.begin_game_preview()
        self.assertEqual(visit.page, TUTORIAL)
        visit.complete_tutorial()
        with self.assertRaises(NavigationError):
            visit.complete_tutorial()
        self.assertEqual(visit.page, TEMPLATES)

    def test_game_preview_does_not_create_discount_or_checkout(self):
        visit = VisitFlow()
        visit.begin_game_preview()
        self.assertFalse(hasattr(visit, "discount_amount"))
        self.assertFalse(hasattr(visit, "paid"))
        self.assertFalse(hasattr(visit, "receipt_token"))
        self.assertEqual(visit.begin_photo(), TUTORIAL)


if __name__ == "__main__":
    unittest.main()
