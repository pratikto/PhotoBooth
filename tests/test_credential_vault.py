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
        elif sys.platform.startswith('linux'):
            from unittest.mock import patch
            from photobooth.linux_credential_vault import LinuxSecretServiceProtector
            with patch('photobooth.linux_credential_vault._read_key', side_effect=VaultUnavailable('Missing key')):
                with self.assertRaises(VaultUnavailable): platform_protector()
            with patch('photobooth.linux_credential_vault._read_key', return_value=self.key):
                protector = platform_protector()
                self.assertIs(type(protector), LinuxSecretServiceProtector)
                protected = protector.protect(self.secret, self.scope)
                self.assertEqual(self.secret, protector.unprotect(protected, self.scope))
            self.assertEqual('LINUX_SECRET_SERVICE', protection_status()['os_protection'])
            self.assertEqual('NOT_CHECKED', protection_status()['readiness'])
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
            if os.name != 'nt' and code == 78:
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
            if os.name != 'nt' and code == 78:
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




class LinuxSecretServiceProtectionTests(unittest.TestCase):
    """Fake keyring fixtures; no real account key is read or provisioned."""
    def setUp(self):
        from unittest.mock import patch
        from photobooth import linux_credential_vault as linux
        self.linux = linux
        self.key = os.urandom(32)
        self.reader_patch = patch.object(linux, '_read_key', side_effect=lambda key_id:self.key)
        self.reader = self.reader_patch.start()
        self.addCleanup(self.reader_patch.stop)
        self.protector = linux.LinuxSecretServiceProtector()
        self.secret = b'synthetic-private-claim'
        self.scope = b'fixture/merchant/PB001/purchase/CCP'

    def item(self, key=None):
        from types import SimpleNamespace
        return SimpleNamespace(is_locked=lambda:False,
            get_attributes=lambda:self.linux._attributes(self.linux.DEFAULT_KEY_ID),
            get_secret=lambda:self.key if key is None else key)

    def test_scoped_randomized_envelope_survives_new_adapter_instances(self):
        first = self.protector.protect(self.secret, self.scope)
        second = self.protector.protect(self.secret, self.scope)
        self.assertNotEqual(first.ciphertext, second.ciphertext)
        restored = self.linux.LinuxSecretServiceProtector().unprotect(first, self.scope)
        self.assertEqual(self.secret, restored)
        self.assertNotIn(self.secret, first.ciphertext)
        with self.assertRaises(VaultUnavailable): self.protector.unprotect(first, b'other/order')

    def test_keyring_is_rechecked_per_operation_without_caching_or_auto_provision(self):
        from unittest.mock import patch
        protected = self.protector.protect(self.secret, self.scope)
        self.assertGreaterEqual(self.reader.call_count, 2)
        self.reader.side_effect = VaultUnavailable('Keyring locked')
        with patch.object(self.linux.LinuxSecretServiceProtector, 'provision') as provision:
            with self.assertRaises(VaultUnavailable): self.protector.protect(self.secret, self.scope)
            with self.assertRaises(VaultUnavailable): self.protector.unprotect(protected, self.scope)
            provision.assert_not_called()

    def test_wrong_key_ciphertext_protector_or_key_identity_never_unlocks(self):
        protected = self.protector.protect(self.secret, self.scope)
        corrupt = ProtectedCredential(protected.protector_id, protected.ciphertext[:-1]+bytes([protected.ciphertext[-1]^1]))
        with self.assertRaises(VaultUnavailable): self.protector.unprotect(corrupt, self.scope)
        other = self.linux.LinuxSecretServiceProtector('other-key-v1')
        with self.assertRaises(VaultUnavailable): other.unprotect(protected, self.scope)
        self.key = os.urandom(32)
        with self.assertRaises(VaultUnavailable): self.protector.unprotect(protected, self.scope)
        with self.assertRaises(VaultUnavailable):
            self.protector.unprotect(ProtectedCredential('other-protector',protected.ciphertext),self.scope)

    def test_bounded_secret_key_id_and_envelope_validation(self):
        for key_id in ('', '../another', 'x'*65, 7):
            with self.subTest(key_id_type=type(key_id).__name__), self.assertRaises(VaultUnavailable):
                self.linux.LinuxSecretServiceProtector(key_id)
        for secret, scope in ((b'', self.scope), (b'x'*8193,self.scope), (self.secret,b'')):
            with self.assertRaises(VaultUnavailable): self.protector.protect(secret,scope)
        for value in (b'', b'x'*31, b'x'*33, 'not-bytes'):
            self.reader.side_effect = lambda key_id, value=value:value
            with self.assertRaises(VaultUnavailable): self.linux.LinuxSecretServiceProtector()

    def test_diagnostics_do_not_include_private_key_secret_or_ciphertext(self):
        protected = self.protector.protect(self.secret,self.scope)
        self.assertNotIn(self.key.hex(), repr(self.protector))
        self.assertNotIn(protected.ciphertext.hex(), repr(protected))
        self.reader.side_effect = OSError(self.key.hex())
        with self.assertRaises(VaultUnavailable) as caught: self.protector.protect(self.secret,self.scope)
        self.assertEqual('Original Ubuntu vault key is unavailable',str(caught.exception))

    def test_explicit_provision_reuses_existing_key_without_overwrite(self):
        from contextlib import contextmanager, nullcontext
        from types import SimpleNamespace
        from unittest.mock import patch
        @contextmanager
        def collection():
            yield SimpleNamespace(search_items=lambda attrs:iter([self.item()]))
        with patch.object(self.linux,'_collection',collection), \
             patch.object(self.linux,'_provision_lock',return_value=nullcontext()), \
             patch.object(self.linux,'_create_without_prompt') as create:
            protector = self.linux.LinuxSecretServiceProtector.provision()
            self.assertEqual(self.linux.DEFAULT_KEY_ID,protector.key_id)
            create.assert_not_called()

    def test_explicit_first_provision_creates_once_and_verifies_original_readback(self):
        from contextlib import contextmanager, nullcontext
        from types import SimpleNamespace
        from unittest.mock import patch
        items=[]
        from photobooth.post_preview_store import PostPreviewStore
        folder=tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        ledger=PostPreviewStore(Path(folder.name)/'drafts.sqlite3')
        self.addCleanup(ledger.close)
        @contextmanager
        def collection():
            yield SimpleNamespace(search_items=lambda attrs:iter(items))
        def create(collection,key_id,key):
            items.append(self.item(key))
        self.reader.side_effect=lambda key_id:items[0].get_secret()
        with patch.object(self.linux,'_collection',collection), \
             patch.object(self.linux,'_provision_lock',side_effect=nullcontext), \
             patch.object(self.linux,'_create_without_prompt',side_effect=create) as write:
            self.linux.LinuxSecretServiceProtector.provision(ledger=ledger)
            self.linux.LinuxSecretServiceProtector.provision()
            self.assertEqual(1,len(items))
            self.assertEqual(1,write.call_count)

    def test_missing_key_with_existing_customer_proof_cannot_be_reprovisioned(self):
        from contextlib import contextmanager, nullcontext
        from types import SimpleNamespace
        from unittest.mock import patch
        from tests.test_post_preview_ccp import OriginalCCPTests
        original=OriginalCCPTests();original.setUp()
        self.addCleanup(original.doCleanups)
        original.issue()
        @contextmanager
        def collection():
            yield SimpleNamespace(search_items=lambda attrs:iter([]))
        with patch.object(self.linux,'_collection',collection), \
             patch.object(self.linux,'_provision_lock',return_value=nullcontext()), \
             patch.object(self.linux,'_create_without_prompt') as create:
            with self.assertRaises(VaultUnavailable):
                self.linux.LinuxSecretServiceProtector.provision(ledger=original.ledger)
            create.assert_not_called()
        self.assertEqual(1,original.ledger.db.execute('SELECT count(*) FROM pp_ccp_credentials').fetchone()[0])

    def test_duplicate_or_changed_key_items_are_not_replaced_or_deleted(self):
        from contextlib import contextmanager, nullcontext
        from types import SimpleNamespace
        from unittest.mock import patch
        @contextmanager
        def collection():
            yield SimpleNamespace(search_items=lambda attrs:iter([self.item(),self.item()]))
        with patch.object(self.linux,'_collection',collection), \
             patch.object(self.linux,'_provision_lock',return_value=nullcontext()), \
             patch.object(self.linux,'_create_without_prompt') as create:
            with self.assertRaises(VaultUnavailable): self.linux.LinuxSecretServiceProtector.provision()
            create.assert_not_called()

    def test_persistent_provider_schema_keeps_exact_required_key_identity(self):
        item = self.item()
        attributes = dict(self.linux._attributes(self.linux.DEFAULT_KEY_ID),
                          **{'xdg:schema':'org.freedesktop.Secret.Generic'})
        item.get_attributes = lambda: attributes
        self.assertEqual(self.key, self.linux._item_key(item, self.linux.DEFAULT_KEY_ID))
        for name in self.linux._attributes(self.linux.DEFAULT_KEY_ID):
            original = attributes[name]
            attributes[name] = 'foreign'
            with self.subTest(field=name), self.assertRaises(VaultUnavailable):
                self.linux._item_key(item, self.linux.DEFAULT_KEY_ID)
            attributes[name] = original

    def test_runtime_kernel_lock_is_exclusive_and_contains_no_key_bytes(self):
        import sys
        from unittest.mock import patch
        if not sys.platform.startswith('linux'):
            with self.assertRaises(VaultUnavailable):
                with self.linux._provision_lock(): pass
            return
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{'XDG_RUNTIME_DIR':folder}):
            with self.linux._provision_lock():
                with self.assertRaises(VaultUnavailable):
                    with self.linux._provision_lock(): pass
            path=Path(folder)/'meong-photobooth'/'vault-provision.lock'
            self.assertEqual(b'',path.read_bytes())
            self.assertEqual(0o600,path.stat().st_mode & 0o777)
            with self.linux._provision_lock(): pass

    def test_insecure_runtime_or_remote_session_bus_is_refused_before_secret_access(self):
        from unittest.mock import patch
        import sys
        if not sys.platform.startswith('linux'):
            with self.assertRaises(VaultUnavailable):
                with self.linux._collection(): pass
            return
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{
                'XDG_RUNTIME_DIR':folder, 'DBUS_SESSION_BUS_ADDRESS':'tcp:host=untrusted,port=1234'}):
            with self.assertRaises(VaultUnavailable):
                with self.linux._collection(): pass
            os.chmod(folder,0o755)
            with self.assertRaises(VaultUnavailable): self.linux._runtime()
            os.chmod(folder,0o700)

    def test_locked_collection_or_plain_session_never_reads_a_secret(self):
        import sys
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        if not sys.platform.startswith('linux'):
            with self.assertRaises(VaultUnavailable):
                with self.linux._collection(): pass
            return
        for encrypted,locked in ((False,False),(True,True)):
            with self.subTest(encrypted=encrypted,locked=locked), tempfile.TemporaryDirectory() as folder:
                connection=SimpleNamespace(close=Mock())
                collection=Mock();collection.is_locked.return_value=locked
                with patch.dict(os.environ,{'XDG_RUNTIME_DIR':folder,
                        'DBUS_SESSION_BUS_ADDRESS':'unix:path='+folder+'/bus'}), \
                     patch('jeepney.io.blocking.open_dbus_connection',return_value=connection), \
                     patch('secretstorage.util.open_session',return_value=SimpleNamespace(encrypted=encrypted)), \
                     patch('secretstorage.collection.Collection',return_value=collection):
                    with self.assertRaises(VaultUnavailable):
                        with self.linux._collection(): pass
                collection.search_items.assert_not_called()
                connection.close.assert_called_once()

    def test_key_creation_refuses_prompt_and_replace_semantics(self):
        import sys
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        if not sys.platform.startswith('linux'):
            with self.assertRaises(VaultUnavailable):
                with self.linux._provision_lock(): pass
            return
        address=Mock();address.call.return_value=('/','/org/freedesktop/secrets/prompt/test')
        collection=SimpleNamespace(is_locked=lambda:False,session=SimpleNamespace(encrypted=True),_collection=address)
        with patch('secretstorage.util.format_secret',return_value=('session',b'iv',b'encrypted','application/octet-stream')), \
             patch('secretstorage.util.exec_prompt') as prompt:
            with self.assertRaises(VaultUnavailable):
                self.linux._create_without_prompt(collection,self.linux.DEFAULT_KEY_ID,self.key)
            self.assertIs(address.call.call_args.args[-1],False)
            prompt.assert_not_called()

    def test_session_calls_have_one_absolute_deadline(self):
        from unittest.mock import Mock,patch
        connection=Mock()
        with patch.object(self.linux.time,'monotonic',return_value=10):
            bus=self.linux._BoundedBus(connection)
        with patch.object(self.linux.time,'monotonic',return_value=13),self.assertRaises(TimeoutError):
            bus.send_and_get_reply(object())
        connection.send_and_get_reply.assert_not_called()


if __name__ == '__main__': unittest.main()
