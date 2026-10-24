"""Offline tests for booth-to-order credential isolation."""
import unittest
from photobooth.booth_auth import BoothAuthenticator


class BoothAuthenticatorTests(unittest.TestCase):
    def setUp(self):
        self.auth = BoothAuthenticator({
            "PB001": "first-booth-secret-with-32-or-more-characters",
            "PB002": "second-booth-secret-with-32-or-more-characters",
        })

    def test_valid_bearer(self):
        self.assertEqual(
            self.auth.authenticate("PB001", "Bearer first-booth-secret-with-32-or-more-characters"),
            "PB001")

    def test_wrong_booth_cannot_reuse_token(self):
        self.assertIsNone(self.auth.authenticate(
            "PB002", "Bearer first-booth-secret-with-32-or-more-characters"))

    def test_wrong_token_rejected(self):
        self.assertIsNone(self.auth.authenticate("PB001", "Bearer incorrect"))

    def test_missing_or_malformed_header_rejected(self):
        for header in (None, "", "Basic abc", "Bearer ", "Bearer  extra"):
            with self.subTest(header=header):
                self.assertIsNone(self.auth.authenticate("PB001", header))

    def test_unknown_booth_rejected(self):
        self.assertIsNone(self.auth.authenticate(
            "PB999", "Bearer first-booth-secret-with-32-or-more-characters"))

    def test_weak_configuration_rejected(self):
        with self.assertRaises(ValueError):
            BoothAuthenticator({"PB001": "short"})


if __name__ == "__main__":
    unittest.main()
