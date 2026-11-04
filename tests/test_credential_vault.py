"""Protected ciphertext unit tests; real Windows DPAPI only on Windows CI."""
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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

    def run_platform_process(self, path, action):
        result = subprocess.run(
            [sys.executable, '-m', 'tests.credential_vault_process_fixture', str(path), action],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True, timeout=20)
        self.assertIn(result.returncode, (0, 78), result.stderr[-2000:])
        return result.returncode, json.loads(result.stdout)

    def test_independent_os_process_restores_same_protected_bytes_or_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'original.protected'
            code, original = self.run_platform_process(path, 'seal')
            if os.name != 'nt':
                self.assertEqual((78, {'state': 'VAULT_UNAVAILABLE'}), (code, original))
                self.assertEqual([], list(Path(folder).iterdir()))
                return
            self.assertEqual(0, code)
            sealed = path.read_bytes()
            self.assertTrue(sealed)
            for _ in range(2):
                code, restored = self.run_platform_process(path, 'open')
                self.assertEqual(0, code)
                self.assertEqual(original, restored)
                self.assertEqual(sealed, path.read_bytes())

    def test_independent_os_process_wrong_scope_or_corrupt_ciphertext_never_restores(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'original.protected'
            code, original = self.run_platform_process(path, 'seal')
            if os.name != 'nt':
                self.assertEqual((78, {'state': 'VAULT_UNAVAILABLE'}), (code, original))
                self.assertFalse(path.exists())
                return
            self.assertEqual(0, code)
            sealed = path.read_bytes()
            self.assertEqual((78, {'state': 'VAULT_UNAVAILABLE'}),
                             self.run_platform_process(path, 'wrong-scope'))
            self.assertEqual(sealed, path.read_bytes())
            corrupt = sealed[:-1] + bytes([sealed[-1] ^ 1])
            path.write_bytes(corrupt)
            self.assertEqual((78, {'state': 'VAULT_UNAVAILABLE'}),
                             self.run_platform_process(path, 'open'))
            self.assertEqual(corrupt, path.read_bytes())


if __name__ == '__main__': unittest.main()
