"""AR-00 baseline contracts, not certification of future autonomous resume."""
from contextlib import closing
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutConflict, CheckoutStore
from photobooth.qris_evidence import provider_evidence
from photobooth.qris_mock import MockQrisProvider
from photobooth.qris_session import KioskCheckout
from tests.test_qris_session import LocalClient


class AutonomousBaselineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.now = [1000.0]

    def backend(self):
        store = CheckoutStore(self.root / 'orders.sqlite', now=lambda: self.now[0])
        provider = MockQrisProvider(self.root / 'provider.sqlite', scenario='pending',
                                    now=lambda: self.now[0])
        self.addCleanup(provider.close)
        self.addCleanup(store.close)
        return CheckoutBackend(store, provider, 'offline-fixture', 'MOCK')

    def interrupted(self, boundary):
        # A different process exits without close()/finally. Reopen actual WAL.
        result = subprocess.run([sys.executable, '-m', 'tests.recovery_crash_fixture',
                                 str(self.root), boundary], cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 71 if boundary == 'before_send' else 72,
                         result.stderr)
        return self.backend()

    def test_pay01_crash_before_provider_call_holds_original_order(self):
        backend = self.interrupted('before_send')
        row = backend.store.db.execute('SELECT * FROM checkouts').fetchone()
        with patch.object(backend.provider, 'create_qris', side_effect=AssertionError('No resend')):
            for _ in range(3):
                self.now[0] += 4
                view = backend.create_order('PB001', {'template_a': 2}, 'a' * 32)
                self.assertEqual(view['order_id'], row['id'])
                self.assertEqual(view['state'], 'CREATED')
                self.assertTrue(view['verification_pending'])
                self.assertIsNone(view['grant_id'])
        self.assertEqual(backend.provider.db.execute('SELECT count(*) FROM mock_orders').fetchone()[0], 0)
        with self.assertRaises(CheckoutConflict):
            backend.create_order('PB001', {'template_a': 2}, 'b' * 32)

    def test_pay02_crash_after_acceptance_recovers_without_another_post(self):
        backend = self.interrupted('after_acceptance')
        with patch.object(backend.provider, 'create_qris', side_effect=AssertionError('No resend')):
            view = backend.create_order('PB001', {'template_a': 2}, 'a' * 32)
        self.assertEqual(view['state'], 'PENDING')
        self.assertFalse(view['verification_pending'])
        self.assertEqual(backend.provider.db.execute('SELECT id,amount FROM mock_orders').fetchone(),
                         (view['order_id'], 15000))
        self.assertEqual(backend.store.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_pay03_04_missing_or_lagging_provider_state_never_replaces_order(self):
        backend = self.backend()
        row, _ = backend.store.begin('PB001', {'template_a': 2}, 15000, 'a' * 32)
        with patch.object(backend.provider, 'get_status', return_value={'status_code': '404'}), \
             patch.object(backend.provider, 'create_qris', side_effect=AssertionError('No resend')):
            for _ in range(4):
                self.now[0] += 4
                result = backend.create_order('PB001', {'template_a': 2}, 'a' * 32)
                self.assertEqual(result['order_id'], row['id'])
                self.assertTrue(result['verification_pending'])
                self.assertEqual(result['state'], 'CREATED')
                with self.assertRaises(CheckoutConflict):
                    backend.claim(row['id'], 'PB001', 'a' * 32)

    def test_pay14_absent_fraud_field_and_explicit_accept_are_valid(self):
        backend = self.backend()
        row, _ = backend.store.begin('PB001', {'template_a': 2}, 15000, 'a' * 32)
        data = backend.provider.create_qris(row['id'], 15000)
        data.update(transaction_status='settlement', status_code='200')
        for absent in (True, False):
            candidate = dict(data)
            if absent:
                del candidate['fraud_status']
            self.assertEqual(provider_evidence(candidate, row, 'MOCK')['transaction_status'], 'settlement')

    def test_pay14_present_invalid_fraud_never_authorizes_settlement(self):
        backend = self.backend()
        row, _ = backend.store.begin('PB001', {'template_a': 2}, 15000, 'a' * 32)
        data = backend.provider.create_qris(row['id'], 15000)
        data.update(transaction_status='settlement', status_code='200')
        for value in ('deny', 'challenge', None, '', True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                provider_evidence(dict(data, fraud_status=value), row, 'MOCK')

    def test_capture_restart_retains_binding_and_never_reenters_capture(self):
        backend = self.backend()
        client = LocalClient(backend)
        context = dict(mode='mock', booth_id='PB001', endpoint='http://127.0.0.1:8765')
        with closing(KioskCheckout(self.root / 'visit.json', client, **context)) as flow:
            flow.begin({'template_a': 2})
            order = flow.refresh()['order']
            backend.provider.db.execute("UPDATE mock_orders SET state='settlement'")
            self.now[0] += 4
            reserved = flow.refresh()
            flow.prepare_capture()
            flow.bind_transaction('PB001_00000001')
            flow.refresh()
        with closing(KioskCheckout(self.root / 'visit.json', client, **context)) as restarted:
            with patch.object(client, 'status', side_effect=AssertionError('Held baseline does no I/O')):
                recovered = restarted.refresh()
            self.assertEqual(recovered['phase'], 'RECOVERY')
            self.assertEqual(recovered['transaction_id'], 'PB001_00000001')
            self.assertEqual(recovered['order']['order_id'], order['order_id'])
            self.assertEqual(recovered['order']['grant_id'], reserved['order']['grant_id'])
            with self.assertRaises(RuntimeError):
                restarted.prepare_capture()
            self.assertEqual(json.loads((self.root / 'visit.json').read_text())['phase'], 'RECOVERY')


if __name__ == '__main__':
    unittest.main()
