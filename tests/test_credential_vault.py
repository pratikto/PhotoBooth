"""Protected ciphertext unit tests; real Windows DPAPI only on Windows CI."""
import os
import unittest

from photobooth.credential_vault import (ProtectedCredential, SyntheticAeadProtector,
    VaultUnavailable, WindowsDPAPIProtector, platform_protector, protection_status)


class CredentialProtectionTests(unittest.TestCase):
    def setUp(self):
        self.key = os.urandom(32)
        self.protector = SyntheticAeadProtector(self.key, fixture=True)
        self.secret = b'synthetic-original-secret-never-redeemable'
        self.scope = b'fixture-merchant/PB001/purchase-group/CCP/v1'

    def test_aead_ciphertext_is_randomized_and_scope_authenticated(self):
        first = self.protector.protect(self.secret, self.scope)
        second = self.protector.protect(self.secret, self.scope)
        self.assertNotEqual(first.ciphertext, second.ciphertext)
        self.assertNotIn(self.secret, first.ciphertext)
        self.assertEqual(self.secret, self.protector.unprotect(first, self.scope))
        with self.assertRaises(VaultUnavailable): self.protector.unprotect(first, b'other-booth/group')

    def test_changed_ciphertext_or_key_never_recovers_a_credential(self):
        protected = self.protector.protect(self.secret, self.scope)
        corrupt = ProtectedCredential(protected.protector_id, protected.ciphertext[:-1]+bytes([protected.ciphertext[-1]^1]))
        with self.assertRaises(VaultUnavailable): self.protector.unprotect(corrupt, self.scope)
        other = SyntheticAeadProtector(os.urandom(32), fixture=True)
        with self.assertRaises(VaultUnavailable): other.unprotect(protected, self.scope)

    def test_original_fixture_key_can_restore_same_ciphertext_after_restart(self):
        protected = self.protector.protect(self.secret, self.scope)
        restarted = SyntheticAeadProtector(self.key, fixture=True)
        self.assertEqual(self.secret, restarted.unprotect(protected, self.scope))

    def test_repr_and_allowlisted_error_never_contain_secret_or_ciphertext(self):
        protected = self.protector.protect(self.secret, self.scope)
        representation = repr(protected)+repr(self.protector)
        self.assertNotIn(self.secret.decode(), representation)
        self.assertNotIn(protected.ciphertext.hex(), representation)
        try:
            self.protector.unprotect(protected, b'wrong-scope')
        except VaultUnavailable as error:
            self.assertEqual('Original credential authentication failed', str(error))

    def test_synthetic_adapter_requires_explicit_fixture_and_bounded_key(self):
        with self.assertRaises(VaultUnavailable): SyntheticAeadProtector(self.key)
        with self.assertRaises(VaultUnavailable): SyntheticAeadProtector(b'short', fixture=True)

    def test_windows_dpapi_or_explicit_unsupported_platform_without_fallback(self):
        if os.name == 'nt':
            protector = platform_protector()
            protected = protector.protect(self.secret, self.scope)
            self.assertEqual(self.secret, WindowsDPAPIProtector().unprotect(protected, self.scope))
            self.assertNotIn(self.secret, protected.ciphertext)
            with self.assertRaises(VaultUnavailable): protector.unprotect(protected, b'wrong-order')
        else:
            with self.assertRaises(VaultUnavailable): platform_protector()
            self.assertEqual('UNSUPPORTED', protection_status()['os_protection'])
        self.assertEqual('NOT_VERIFIED', protection_status()['device_acceptance'])

    def test_invalid_envelope_shape_size_type_or_protector_is_rejected(self):
        for secret, scope in ((b'', self.scope), (b'x'*8193, self.scope),
                              ('plaintext', self.scope), (self.secret, b'')):
            with self.subTest(secret_type=type(secret).__name__), self.assertRaises(VaultUnavailable):
                self.protector.protect(secret, scope)
        with self.assertRaises(VaultUnavailable):
            self.protector.unprotect(ProtectedCredential('another-protector', b'data'), self.scope)


if __name__ == '__main__': unittest.main()
