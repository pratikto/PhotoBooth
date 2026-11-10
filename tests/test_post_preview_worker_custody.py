"""Original worker custody crypto only; never orphan/ACK/OS-owner acceptance."""
from contextlib import nullcontext
from dataclasses import replace
import hashlib
import hmac
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from photobooth.credential_vault import (
    ProtectedCredential, SyntheticAeadProtector, VaultUnavailable, platform_protector)
from photobooth.post_preview_bootstrap import backend_environment
from photobooth.post_preview_worker_custody import (
    ProtectedWorkerKey, WorkerCustodyScope, protect_worker_key, restore_worker_key)
from photobooth.post_preview_worker_fence import WorkerFenceKey, canonical


class WorkerCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.scope = WorkerCustodyScope(self.root/'private', 'fixture-merchant', 'PB001',
                                       'a'*32, os.getpid(), 'declared-birth-only-123')
        context = (nullcontext() if os.name == 'nt' else
                   patch('photobooth.linux_credential_vault._read_key', return_value=b'k'*32))
        context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)
        self.key = WorkerFenceKey.create()
        self.protector = platform_protector()
        self.envelope = protect_worker_key(self.key, self.scope)

    def held(self, action):
        with self.assertRaises(VaultUnavailable) as caught:
            action()
        self.assertEqual(str(caught.exception), 'Original worker custody is unavailable')

    def test_roundtrip_preserves_original_hmac_without_creating_files(self):
        restored = restore_worker_key(self.envelope, self.scope)
        vector = {'kind': 'CUSTODY_TEST_NO_RELEASE_AUTHORITY'}
        self.assertEqual(restored.key_id, self.key.key_id)
        self.assertTrue(hmac.compare_digest(restored.sign(vector), self.key.sign(vector)))
        self.assertFalse(self.scope.private_root.exists())
        self.assertEqual(WorkerCustodyScope.from_record(self.scope.to_record()), self.scope)

    def test_only_ciphertext_and_metadata_serialize_with_redacted_repr(self):
        record = self.envelope.to_record()
        restored = ProtectedWorkerKey.from_record(record)
        self.assertTrue(hmac.compare_digest(
            restore_worker_key(restored, self.scope).sign({'test': 1}), self.key.sign({'test': 1})))
        representation = repr(self.envelope)+repr(self.scope)+repr(self.key)+json.dumps(record)
        self.assertFalse(self.key.secret.hex() in representation)
        self.assertFalse(str(self.root) in repr(self.scope))
        self.assertFalse(self.envelope.credential.ciphertext.hex() in repr(self.envelope))
        other = protect_worker_key(self.key, self.scope)
        self.assertFalse(hmac.compare_digest(self.envelope.credential.ciphertext, other.credential.ciphertext))

    def test_all_scope_bindings_reject_same_ciphertext(self):
        changes = dict(private_root=self.root/'another', merchant_id='another', booth_id='PB002',
                       worker_epoch='b'*32, owner_pid=self.scope.owner_pid+1, process_birth='another-birth')
        for name, value in changes.items():
            with self.subTest(field=name):
                changed = replace(self.scope, **{name: value})
                self.held(lambda: restore_worker_key(self.envelope, changed))
                # Rewriting the public digest cannot bypass OS authenticated entropy.
                forged = replace(self.envelope, scope_sha256=hashlib.sha256(changed.entropy()).hexdigest())
                self.held(lambda: restore_worker_key(forged, changed))

    def test_ciphertext_and_header_tampering_is_held(self):
        raw = self.envelope.credential.ciphertext
        corrupt = ProtectedCredential(self.envelope.credential.protector_id,
                                      raw[:-1]+bytes([raw[-1]^1]))
        for envelope in (replace(self.envelope, credential=corrupt),
                         replace(self.envelope, key_id='b'*32),
                         replace(self.envelope, scope_sha256='b'*64)):
            self.held(lambda: restore_worker_key(envelope, self.scope))

    def test_foreign_role_malformed_duplicate_or_noncanonical_plaintext_is_held(self):
        payload = dict(version=1, kind='ORIGINAL_WORKER_KEY', key_id=self.key.key_id,
                       scope_sha256=self.envelope.scope_sha256, secret_hex=self.key.secret.hex())
        valid = canonical(payload)
        changes = ({'kind': 'CCP'}, {'version': True}, {'key_id': 'b'*32},
                   {'scope_sha256': 'b'*64}, {'secret_hex': 'short'}, {'extra': 1})
        raws = [canonical(dict(payload, **change)).encode() for change in changes]
        raws += [b'[]', b'null', b'{', b'\xff', b' '+valid.encode(),
                 (valid[:-1]+',"version":1}').encode()]
        for index, raw in enumerate(raws):
            with self.subTest(case=index):
                envelope = replace(self.envelope, credential=self.protector.protect(raw, self.scope.entropy()))
                self.held(lambda: restore_worker_key(envelope, self.scope))

    def test_scope_record_has_exact_typed_bounded_fields(self):
        for change in ({'version': True}, {'mode': 'production'}, {'kind': 'CCP'},
                       {'order_version': 'legacy'}, {'owner_pid': True}, {'owner_pid': 0},
                       {'owner_pid': 2**32}, {'worker_epoch': 'A'*32}, {'process_birth': 'x'*129},
                       {'merchant_id': 'old'}, {'booth_id': '001'}, {'extra': 1},
                       {'private_root': 'relative'}, {'private_root': str(self.root/'old'/'x')}):
            self.held(lambda: WorkerCustodyScope.from_record(dict(self.scope.to_record(), **change)))
        record = self.scope.to_record()
        del record['process_birth']
        self.held(lambda: WorkerCustodyScope.from_record(record))

    def test_invalid_envelope_records_and_bounds_are_held(self):
        for change in ({'version': True}, {'kind': 'CCP'}, {'protector_id': 'synthetic-aesgcm-fixture-v1'},
                       {'ciphertext': ''}, {'ciphertext': '!'}, {'ciphertext': 'A'*87385},
                       {'ciphertext': 'AB=='}, {'ciphertext': 12}, {'key_id': 'invalid'},
                       {'scope_sha256': 'invalid'}, {'extra': 1}):
            self.held(lambda: ProtectedWorkerKey.from_record(dict(self.envelope.to_record(), **change)))
        for raw in (b'', b'x'*65537, 'not-bytes'):
            self.held(lambda: replace(self.envelope,
                credential=ProtectedCredential(self.envelope.credential.protector_id, raw)))

    def test_synthetic_forged_or_subclass_protectors_never_accepted(self):
        class Forged:
            synthetic = False
            protector_id = self.protector.protector_id
            def protect(*args):
                raise AssertionError('Must never be called')
        class Subclass(type(self.protector)):
            pass
        for value in (Forged(), SyntheticAeadProtector(b'k'*32, fixture=True), Subclass()):
            self.held(lambda: protect_worker_key(self.key, self.scope, protector=value))
            self.held(lambda: restore_worker_key(self.envelope, self.scope, protector=value))

    def test_missing_custody_fails_closed_with_no_key_creation(self):
        # Exercise default selection denial on both platforms without replacing OS crypto.
        with patch('photobooth.post_preview_worker_custody.platform_protector',
                   side_effect=VaultUnavailable('PRIVATE OS DETAIL')), \
             patch.object(WorkerFenceKey, 'create', side_effect=AssertionError('No replacement')):
            self.held(lambda: restore_worker_key(self.envelope, self.scope))
            self.held(lambda: protect_worker_key(self.key, self.scope))
        if os.name != 'nt':
            with patch('photobooth.linux_credential_vault._read_key', return_value=b'z'*32):
                self.held(lambda: restore_worker_key(self.envelope, self.scope))
            with patch('photobooth.linux_credential_vault._read_key', side_effect=VaultUnavailable('Locked')):
                self.held(lambda: restore_worker_key(self.envelope, self.scope))

    def test_independent_process_restores_original_nonrelease_hmac(self):
        record = dict(scope=self.scope.to_record(), envelope=self.envelope.to_record())
        command = [sys.executable, '-m', 'tests.post_preview_worker_custody_process_fixture']
        result = subprocess.run(command, input=json.dumps(record), text=True, capture_output=True,
                                timeout=20, cwd=Path(__file__).resolve().parents[1],
                                env=backend_environment(os.environ))
        self.assertEqual(result.returncode, 0, 'Protected child must return non-secret evidence')
        value = json.loads(result.stdout)
        self.assertEqual(value['state'], 'RESTORED_TEST_VECTOR_ONLY')
        self.assertEqual(value['key_id'], self.key.key_id)
        self.assertTrue(hmac.compare_digest(value['mac'],
            self.key.sign({'kind': 'CUSTODY_TEST_NO_RELEASE_AUTHORITY'})))
        self.assertFalse(value['kivy_loaded'])
        record['scope']['process_birth'] = 'foreign-birth'
        denied = subprocess.run(command, input=json.dumps(record), text=True, capture_output=True,
                                timeout=20, cwd=Path(__file__).resolve().parents[1],
                                env=backend_environment(os.environ))
        self.assertEqual(denied.returncode, 3)
        self.assertEqual(json.loads(denied.stdout), {'state': 'CUSTODY_HELD'})
