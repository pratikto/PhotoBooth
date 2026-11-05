"""Original-service process restart; Windows OS protection vs synthetic plumbing."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from photobooth.credential_vault import SyntheticAeadProtector, WindowsDPAPIProtector
from photobooth.kiosk_v2.post_preview_checkout import PrivateCheckoutService
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_store import DraftHeld


class OriginalProtectedRestoreTests(unittest.TestCase):
    def assert_rejected(self, protector, *, protected=True):
        with tempfile.TemporaryDirectory() as folder:
            client = PostPreviewClient('https://fixture.invalid', 'PB001', 'SYNTHETIC-BOOTH-'+'a'*48, expected_mode='mock')
            try:
                with self.assertRaises(DraftHeld):
                    PrivateCheckoutService(Path(folder), payment_client=client, protector=protector,
                        merchant_id='MTEST', readiness=lambda: None, qr_loader=lambda _: None,
                        allow_incomplete_fixture=True, allow_windows_protected_mock=protected)
                self.assertEqual([], list(Path(folder).iterdir()))
            finally:
                client.close()

    def test_protected_mode_rejects_self_described_non_os_protector_before_opening_root(self):
        self.assert_rejected(SimpleNamespace(synthetic=False, protector_id='windows-dpapi-current-user-v1'))

    def test_protected_mode_cannot_silently_use_ephemeral_synthetic_key(self):
        self.assert_rejected(SyntheticAeadProtector(os.urandom(32), fixture=True))

    def test_default_worker_rejects_os_protector_without_explicit_mock_opt_in(self):
        # On Linux even a forged uninitialized DPAPI instance may not turn OS
        # protection on. Windows uses the real current-user adapter.
        protector = WindowsDPAPIProtector() if os.name == 'nt' else object.__new__(WindowsDPAPIProtector)
        self.assert_rejected(protector, protected=False)
        if os.name != 'nt':
            self.assert_rejected(protector)

    def restored_process(self, action):
        with tempfile.TemporaryDirectory() as folder:
            command = [sys.executable, '-m', 'tests.post_preview_restore_process_fixture', folder]
            produced = subprocess.run(command+['produce'], input='{}', text=True, capture_output=True,
                                      cwd=Path(__file__).resolve().parents[1], timeout=60)
            # Never include the producer stdout (private simulated customer
            # proof/key) in assertion messages or shared logs.
            self.assertEqual(73, produced.returncode, produced.stderr[-2000:])
            private_context = json.loads(produced.stdout)
            restored = subprocess.run(command+[action], input=json.dumps(private_context), text=True,
                                     capture_output=True, cwd=Path(__file__).resolve().parents[1], timeout=60)
            self.assertEqual(0, restored.returncode, restored.stderr[-2000:])
            observed = json.loads(restored.stdout)
            self.assertEqual('WINDOWS_DPAPI_MOCK_SERVICE' if os.name=='nt' else 'SYNTHETIC_PIPE_KEY_ONLY', observed['scope'])
            self.assertFalse(observed['boot_private_offer'])
            self.assertEqual(0, observed['new_charges'])
            self.assertEqual(0, observed['new_receipt_sends'])
            self.assertGreaterEqual(observed['provider_reads'], 2)
            self.assertTrue(observed['media_unchanged'])
            self.assertEqual('OWED', observed['owed'])
            self.assertEqual(1, observed['attempts'])
            self.assertEqual(1, observed['retakes'])
            self.assertEqual(2, observed['copies'])
            self.assertEqual(1, observed['ticket_issues'])
            self.assertEqual('PREPARED', observed['receipt_state'])
            self.assertTrue(observed['original_ack'])
            return observed

    def test_independent_process_restores_original_paid_service_only_after_customer_proof(self):
        view = self.restored_process('restore')
        self.assertEqual('REACQUIRED', view['state'])
        self.assertEqual('paid_hold', view['phase'])
        self.assertTrue(view['entitlement_matches'])
        self.assertTrue(view['same_original_ticket'])
        self.assertEqual(view['old_generation']+1, view['generation'])

    def test_independent_process_valid_original_proof_waits_while_B_owns_booth(self):
        view = self.restored_process('busy')
        self.assertEqual('WAIT', view['state'])
        self.assertNotIn('same_original_ticket', view)

    def test_independent_process_unavailable_vault_fails_closed_without_reissue(self):
        view = self.restored_process('vault-failure')
        self.assertEqual('VAULT_HOLD', view['state'])
        self.assertNotIn('same_original_ticket', view)


if __name__ == '__main__':
    unittest.main()
