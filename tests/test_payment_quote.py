"""FEAT-020 independent checkout validation; no payment provider calls."""
import unittest
from photobooth.payment_quote import quote_checkout


class PaymentQuoteTests(unittest.TestCase):
    def test_one_template_one_copy(self):
        quote = quote_checkout({"template_a": 1})
        self.assertEqual((quote.session_count, quote.print_copy_count, quote.total_amount), (1, 1, 10000))

    def test_two_copies_same_template(self):
        self.assertEqual(quote_checkout({"template_a": 2}).total_amount, 15000)

    def test_multiple_templates_have_separate_session_fees(self):
        self.assertEqual(quote_checkout({"template_a": 1, "template_b": 2}).total_amount, 25000)

    def test_invalid_templates_and_counts_fail_closed(self):
        for value in ({}, {"unknown": 1}, {"template_a": 0},
                      {"template_a": -1}, {"template_a": True},
                      {"template_a": 1.0}, {"template_a": 11},
                      {"template_a": "1"}, {"template_a": 1, "bad": 1}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                quote_checkout(value)

    def test_does_not_accept_client_total(self):
        with self.assertRaises(ValueError):
            quote_checkout({"template_a": 1, "total_amount": 1})


if __name__ == "__main__":
    unittest.main()
