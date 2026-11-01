"""Genuine native paid-ticket visibility, role isolation and complete retirement."""
import unittest
from unittest.mock import Mock

from kivy.base import EventLoop
from kivy.core.window import Window
from PIL import Image

from photobooth.kiosk_v2.ccp_view import PrivateRecoveryTicketCard
from photobooth.post_preview_ticket import PendingRecoveryOffer
from photobooth.post_preview_ccp import PendingCCPOffer, render_private_ccp


class PrivateTicketCardTests(unittest.TestCase):
    def test_original_ticket_visible_once_at_two_portrait_sizes(self):
        for size in ((800,1280),(452,900)):
            with self.subTest(size=size):
                Window.size=size
                offer=PendingRecoveryOffer('fixture-permit','fixture-group',1,
                    'MEONG:RECOVERY:1:PB001:'+'a'*32+':'+'b'*43)
                callback=Mock()
                card=PrivateRecoveryTicketCard(
                    offer,render_private_ccp(offer),callback,is_current=lambda:True)
                Window.add_widget(card)
                try:
                    card._ready_at=0
                    for _ in range(5): EventLoop.idle()
                    card._rendered(0)
                    callback.assert_called_once_with(offer)
                    self.assertIsNotNone(card.qr_image.texture)
                    card._rendered(0)
                    callback.assert_called_once()
                finally:
                    card.retire()
                    Window.remove_widget(card)
                    self.assertIsNone(card.qr_image.texture)
                    self.assertEqual('',card.code.text)
                    self.assertIsNone(card._offer)

    def test_cross_type_claim_not_accepted_and_hidden_card_not_offered(self):
        ccp=PendingCCPOffer('f','g',1,'SYNTHETIC-CCP')
        with self.assertRaises(TypeError):
            PrivateRecoveryTicketCard(ccp,Image.new('RGB',(200,200)),Mock(),
                                      is_current=lambda:True)
        offer=PendingRecoveryOffer('fixture','group',1,'SYNTHETIC-RECOVERY')
        callback=Mock()
        card=PrivateRecoveryTicketCard(offer,Image.new('RGB',(256,256)),
                                       callback,is_current=lambda:True)
        try:
            Window.add_widget(card)
            card._ready_at=0
            card.opacity=0
            for _ in range(4): EventLoop.idle()
            card._rendered(0)
            callback.assert_not_called()
            Window.remove_widget(card)
            self.assertIsNone(card.qr_image.texture)
            self.assertEqual('',card.code.text)
        finally:
            card.retire()
            if card.parent is not None: Window.remove_widget(card)


if __name__ == '__main__': unittest.main()
