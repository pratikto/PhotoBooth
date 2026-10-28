"""AR-01 migration, request-boundary durability and immutable creation scope."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from photobooth.checkout_backend import CheckoutBackend, ProviderUnavailable
from photobooth.checkout_store import CheckoutConflict, CheckoutStore
from tests.test_checkout_backend import FakeProvider, KEY, MERCHANT


class CreationAttemptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'orders.sqlite'
        self.store = CheckoutStore(self.path, now=lambda: 1000)
        self.addCleanup(self.store.close)
        self.provider = FakeProvider()
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        self.key = 'a' * 32

    def create(self):
        return self.backend.create_order('PB001', {'template_a': 2}, self.key)

    def attempt(self, oid):
        return self.store.creation_attempt(oid)

    def test_identity_and_sent_boundary_are_committed_before_provider_io(self):
        original = self.provider.create_qris
        observed = []
        def inspect(oid, amount):
            with closing(CheckoutStore(self.path)) as other:
                row = other.get(oid)
                attempt = other.creation_attempt(oid)
                observed.append(attempt)
                self.assertEqual((row['booth_id'], row['checkout_key'], row['amount']),
                                 ('PB001', self.key, amount))
                self.assertEqual(attempt['merchant_id'], MERCHANT)
                self.assertEqual(attempt['provider_mode'], 'sandbox')
                self.assertEqual(attempt['phase'], 'SENT')
                self.assertEqual(len(attempt['request_hash']), 64)
                self.assertEqual(attempt['sent_at'], 1000)
            return original(oid, amount)
        self.provider.create_qris = inspect
        view = self.create()
        self.assertEqual(len(observed), 1)
        self.assertEqual(self.attempt(view['order_id'])['phase'], 'VERIFIED')

    def test_lost_response_uncertainty_survives_reopen_and_status_recovers(self):
        self.provider.lost_charge = True
        with self.assertRaises(ProviderUnavailable):
            self.create()
        oid = next(iter(self.provider.rows))
        before = self.attempt(oid)
        self.assertEqual(before['phase'], 'UNCERTAIN')
        with closing(CheckoutStore(self.path, now=lambda: 1010)) as reopened:
            backend = CheckoutBackend(reopened, self.provider, KEY, MERCHANT)
            result = backend.create_order('PB001', {'template_a': 2}, self.key)
            self.assertEqual(result['order_id'], oid)
            self.assertEqual(reopened.creation_attempt(oid)['phase'], 'VERIFIED')
            self.assertEqual(reopened.creation_attempt(oid)['request_hash'], before['request_hash'])
        self.assertEqual(self.provider.charges, 1)

    def test_provider_never_received_call_and_repeated_404_remain_uncertain(self):
        with patch.object(self.provider, 'create_qris', side_effect=TimeoutError('not delivered')):
            with self.assertRaises(ProviderUnavailable):
                self.create()
        oid = self.store.db.execute('SELECT id FROM checkouts').fetchone()[0]
        with patch.object(self.provider, 'get_status', return_value={'status_code': '404'}), \
             patch.object(self.provider, 'create_qris', side_effect=AssertionError('No repeat charge')):
            for _ in range(4):
                result = self.create()
                self.assertEqual(result['order_id'], oid)
                self.assertTrue(result['verification_pending'])
        self.assertEqual(self.attempt(oid)['phase'], 'UNCERTAIN')
        self.assertIsNone(self.store.get(oid)['grant_id'])
        with self.assertRaises(CheckoutConflict):
            self.backend.create_order('PB001', {'template_a': 2}, 'b' * 32)

    def test_different_merchant_or_mode_cannot_reuse_old_order_or_call_provider(self):
        oid = self.create()['order_id']
        for merchant, mode in (('OTHER', 'sandbox'), (MERCHANT, 'mock')):
            with self.subTest(merchant=merchant, mode=mode):
                self.provider.mode = mode
                backend = CheckoutBackend(self.store, self.provider, KEY, merchant)
                with patch.object(self.provider, 'get_status', side_effect=AssertionError('Scope must fail before I/O')):
                    with self.assertRaises(CheckoutConflict):
                        backend.create_order('PB001', {'template_a': 2}, self.key)
                    with self.assertRaises(CheckoutConflict):
                        backend.status(oid, 'PB001')
        self.assertEqual(self.provider.charges, 1)

    def test_fingerprint_mismatch_blocks_provider_io(self):
        oid = self.create()['order_id']
        self.store.db.execute('UPDATE checkout_create_attempts SET request_hash=? WHERE order_id=?',
                              ('0' * 64, oid))
        with patch.object(self.provider, 'get_status', side_effect=AssertionError('No I/O')):
            with self.assertRaises(CheckoutConflict):
                self.create()

    def test_concurrent_independent_backends_send_once(self):
        second = CheckoutStore(self.path)
        self.addCleanup(second.close)
        backend2 = CheckoutBackend(second, self.provider, KEY, MERCHANT)
        entered, release = threading.Event(), threading.Event()
        original = self.provider.create_qris
        def slow(*args):
            entered.set()
            if not release.wait(5):
                raise TimeoutError('test barrier')
            return original(*args)
        self.provider.create_qris = slow
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(self.create)
            try:
                self.assertTrue(entered.wait(3))
                duplicate = pool.submit(backend2.create_order, 'PB001', {'template_a': 2}, self.key).result(3)
                self.assertTrue(duplicate['verification_pending'])
            finally:
                release.set()
            result = first.result(3)
        self.assertEqual(result['order_id'], duplicate['order_id'])
        self.assertEqual(self.provider.charges, 1)

    def test_exception_after_payment_commit_does_not_regress_verified_attempt(self):
        with patch.object(self.store, 'save_qr', side_effect=OSError('unavailable')):
            with self.assertRaises(ProviderUnavailable):
                self.create()
        oid = next(iter(self.provider.rows))
        self.assertEqual(self.store.get(oid)['state'], 'PENDING')
        self.assertEqual(self.attempt(oid)['phase'], 'VERIFIED')

    def test_upgrade_and_old_writer_rows_are_held_without_guessing_or_resend(self):
        # Frozen pre-AR checkouts DDL from f6736b7. No git-history dependency:
        # CI checkouts can be shallow, and fixtures never run historical code.
        old_path = Path(self.tmp.name) / 'legacy.sqlite'
        with closing(sqlite3.connect(old_path, isolation_level=None)) as old:
            old.row_factory = sqlite3.Row
            old.execute('''CREATE TABLE checkouts (
                id TEXT PRIMARY KEY, booth_id TEXT NOT NULL, checkout_key TEXT NOT NULL,
                quantities TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>0),
                state TEXT NOT NULL DEFAULT 'CREATED', created_at REAL NOT NULL,
                expires_at REAL, qr_url TEXT, provider_ref TEXT UNIQUE, merchant_id TEXT,
                grant_id TEXT UNIQUE, service_state TEXT NOT NULL DEFAULT 'NONE',
                local_transaction_id TEXT, closed INTEGER NOT NULL DEFAULT 0,
                check_after REAL NOT NULL DEFAULT 0, verified_at REAL,
                UNIQUE(booth_id,checkout_key))''')
            old.execute('''INSERT INTO checkouts
                (id,booth_id,checkout_key,quantities,amount,created_at) VALUES(?,?,?,?,?,?)''',
                ('legacy-order', 'PB001', self.key, '{"template_a":2}', 15000, 900))
            before = dict(old.execute('SELECT * FROM checkouts').fetchone())
        with closing(CheckoutStore(old_path)) as upgraded:
            self.assertEqual(dict(upgraded.db.execute('SELECT * FROM checkouts').fetchone()), before)
            attempt = upgraded.creation_attempt('legacy-order')
            self.assertEqual(attempt['phase'], 'LEGACY_UNCERTAIN')
            self.assertIsNone(attempt['request_hash'])
            backend = CheckoutBackend(upgraded, self.provider, KEY, MERCHANT)
            with patch.object(self.provider, 'get_status', return_value={'status_code': '404'}):
                self.assertTrue(backend.create_order('PB001', {'template_a': 2}, self.key)['verification_pending'])
            self.assertEqual(self.provider.charges, 0)
        # Older source remains readable/writable; additive table is never dropped.
        with closing(sqlite3.connect(old_path, isolation_level=None)) as old:
            self.assertEqual(old.execute('SELECT checkout_key FROM checkouts WHERE id=?',
                                        ('legacy-order',)).fetchone()[0], self.key)
            old.execute('''INSERT INTO checkouts
                (id,booth_id,checkout_key,quantities,amount,created_at) VALUES(?,?,?,?,?,?)''',
                ('rollback-writer', 'PB002', self.key, '{"template_a":2}', 15000, 1000))
        with closing(CheckoutStore(old_path)) as reopened:
            self.assertEqual(reopened.creation_attempt('rollback-writer')['phase'], 'LEGACY_UNCERTAIN')
            self.assertEqual(reopened.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_pay01_abrupt_exit_after_prepared_does_not_authorize_resubmission(self):
        crash_root = Path(self.tmp.name) / 'prepared-crash'
        result = subprocess.run([sys.executable, '-m', 'tests.recovery_crash_fixture',
                                 str(crash_root), 'prepared'],
                                cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 73, result.stderr)
        with closing(CheckoutStore(crash_root / 'orders.sqlite')) as reopened:
            oid = reopened.db.execute('SELECT id FROM checkouts').fetchone()[0]
            self.assertEqual(reopened.creation_attempt(oid)['phase'], 'PREPARED')
            # Matching synthetic context, but a restart is never the first call.
            self.provider.mode = 'mock'
            backend = CheckoutBackend(reopened, self.provider, KEY, 'MOCK')
            with patch.object(self.provider, 'get_status', return_value={'status_code': '404'}):
                self.assertTrue(backend.create_order('PB001', {'template_a': 2}, self.key)['verification_pending'])
            self.assertEqual(self.provider.charges, 0)
            self.assertEqual(reopened.creation_attempt(oid)['phase'], 'PREPARED')


if __name__ == '__main__':
    unittest.main()
