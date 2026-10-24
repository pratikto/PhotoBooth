"""Shared simulated quote: flat, bounded discount from a recorded game win."""

import unittest
from photobooth.kiosk_v2.game_offer import demo_amount,is_demo_winner


class GameOfferTests(unittest.TestCase):
    def test_flat_discount_for_one_or_multiple_copies_and_designs(self):
        for subtotal,total in ((10000,7500),(15000,12500),(25000,22500)):
            with self.subTest(subtotal=subtotal):
                amount=demo_amount(subtotal,True)
                self.assertEqual((amount.subtotal,amount.discount,amount.total),(subtotal,2500,total))

    def test_empty_small_and_ineligible_totals_never_become_negative(self):
        self.assertEqual(demo_amount(0,True).total,0)
        self.assertEqual(demo_amount(1000,True).total,0)
        self.assertEqual(demo_amount(10000,False).total,10000)

    def test_result_needs_completed_win_score_and_attempt_not_just_a_badge(self):
        won={'result':'won','score':10,'attempt_id':'recorded-attempt'}
        self.assertTrue(is_demo_winner(won))
        for result in (None,True,{'result':'won'},dict(won,score=True),dict(won,score=9),
                       dict(won,result='started'),dict(won,result='lost'),dict(won,attempt_id='')):
            with self.subTest(result=result):self.assertFalse(is_demo_winner(result))

    def test_invalid_amounts_do_not_reach_quote(self):
        for amount,eligible in ((-1,True),(True,True),(10.5,True),(10000,'yes')):
            with self.assertRaises(ValueError):demo_amount(amount,eligible)


if __name__=='__main__':unittest.main()
