"""Actual native render callbacks with fixture-only private proofs, no screenshots."""
import os
import time
import unittest
from unittest.mock import Mock
from types import SimpleNamespace

from kivy.base import EventLoop
from kivy.core.window import Window
from PIL import Image

from photobooth.kiosk_v2.ccp_view import PrivateCCPCard, render_private_ccp
from photobooth.post_preview_ccp import PendingCCPOffer
from photobooth.qr_code import _render_qr, create_qr_image


class CCPViewTests(unittest.TestCase):
    def test_private_encoder_bypasses_shared_recent_content_cache(self):
        _render_qr.cache_clear()
        before = _render_qr.cache_info()
        image = create_qr_image('SYNTHETIC-PRIVATE-ENCODER-FIXTURE', with_logo=False, max_size=320, cache=False)
        self.assertEqual('RGB', image.mode)
        self.assertEqual(before, _render_qr.cache_info())
        create_qr_image('SYNTHETIC-PUBLIC-FOLDER-FIXTURE', with_logo=False, cache=True)
        self.assertEqual(before.currsize+1, _render_qr.cache_info().currsize)

    def test_actual_visible_private_card_notifies_once_and_retirement_wipes_code_texture(self):
        for size in ((800, 1280), (452, 900)):
            with self.subTest(size=size):
                Window.size = size
                offer = PendingCCPOffer('fixture-permit', 'fixture-group', 1, 'SYNTHETIC-NONREDEEMABLE-CLAIM-PROOF')
                visible = Mock()
                card = PrivateCCPCard(offer, render_private_ccp(offer),
                                      visible, is_current=lambda: True)
                Window.add_widget(card)
                try:
                    card._ready_at = 0
                    for _ in range(5): EventLoop.idle()
                    card._rendered(0)
                    visible.assert_called_once_with(offer)
                    card._rendered(0)
                    visible.assert_called_once()
                    card.retire()
                    self.assertEqual('', card.code.text)
                    self.assertIsNone(card.qr_image.texture)
                    self.assertIsNone(card._offer)
                finally:
                    card.retire(); Window.remove_widget(card)

    def test_loading_unattached_hidden_and_retired_cards_cannot_claim_offer(self):
        visible = Mock()
        offer = PendingCCPOffer('fixture', 'group', 1, 'SYNTHETIC-NONREDEEMABLE')
        current = [True]
        card = PrivateCCPCard(offer, Image.new('RGB', (256, 256)), visible,
                              is_current=lambda: current[0])
        try:
            card._rendered(0)
            visible.assert_not_called()
            Window.add_widget(card)
            card.opacity = 0
            card._ready_at = 0
            for _ in range(3): EventLoop.idle()
            card._rendered(0)
            visible.assert_not_called()
            current[0] = False
            card.opacity = 1
            card._rendered(0)
            visible.assert_not_called()
            self.assertIsNone(card.qr_image.texture)
        finally:
            card.retire(); Window.remove_widget(card)

    def test_visible_callback_uses_original_worker_and_records_genuine_offer_once(self):
        from tests.test_post_preview_ccp import OriginalCCPTests
        from photobooth.kiosk_v2.photos import PhotoJobs
        fixture = OriginalCCPTests()
        fixture.setUp()
        card = None
        try:
            offer = fixture.offer()
            service = SimpleNamespace(mark_visible=lambda value: {
                'offered_at': fixture.service.mark_visible(fixture.lease, value)})
            jobs = PhotoJobs(service=service)
            def visible(value):
                self.assertTrue(jobs.submit('mark_visible', value))
            card = PrivateCCPCard(offer, render_private_ccp(offer), visible,
                                  is_current=lambda: True)
            Window.add_widget(card)
            card._ready_at = 0
            outcome = None
            deadline = time.monotonic()+10
            while outcome is None and time.monotonic() < deadline:
                EventLoop.idle()
                outcome = jobs.poll()
            self.assertIsNotNone(outcome)
            self.assertIsNone(outcome.error)
            self.assertEqual(1000, fixture.row()['offered_at'])
            card.retire()
            self.assertEqual(1, fixture.ledger.db.execute(
                "SELECT count(*) FROM pp_events WHERE event='CCP_OFFERED'").fetchone()[0])
        finally:
            if card is not None:
                card.retire(); Window.remove_widget(card)
            fixture.doCleanups()

    def test_clipped_full_code_and_detached_card_never_leave_a_live_credential(self):
        visible = Mock()
        offer = PendingCCPOffer('fixture', 'group', 1, 'SYNTHETIC-NONREDEEMABLE')
        card = PrivateCCPCard(offer, Image.new('RGB', (256, 256)), visible,
                              is_current=lambda: True)
        card._ready_at = time.monotonic()+1000
        card.code.text = 'SYNTHETIC-FULL-CODE '*200
        Window.add_widget(card)
        try:
            for _ in range(4): EventLoop.idle()
            self.assertGreater(card.code.texture_size[1], card.code.height)
            card._ready_at = 0
            card._rendered(0)
            visible.assert_not_called()
            Window.remove_widget(card)
            self.assertIsNone(card.qr_image.texture)
            self.assertEqual('', card.code.text)
            self.assertIsNone(card._offer)
        finally:
            card.retire()
            if card.parent is not None: Window.remove_widget(card)


if __name__ == '__main__': unittest.main()
