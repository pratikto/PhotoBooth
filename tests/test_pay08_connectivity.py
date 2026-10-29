"""PAY-08 OS-edge → real API/client/SQLite; synthetic provider, no real network."""
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.connectivity import ConnectivityRestoration
from photobooth.kiosk_v2.sandbox_checkout import SandboxCheckout
from photobooth.qris_api import create_app
from photobooth.qris_kiosk_client import QrisKioskClient
from photobooth.qris_session import KioskCheckout
from tests.qris_v2_fixture import Fixture, InProcessSession
from tests.test_checkout_backend import KEY, MERCHANT


class ConnectivityRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = Fixture(Path(self.tmp.name))
        self.addCleanup(self.fixture.close)
        # Direct service calls do not initialize jobs.store. Explicitly close
        # the current (possibly reopened) GUI flow before Windows temp cleanup.
        self.addCleanup(lambda: self.fixture.flow.close())
        self.now = [1000.0]
        self.fixture.store.now = lambda: self.now[0]
        clock_patch = patch('photobooth.qris_session.time', SimpleNamespace(monotonic=lambda: self.now[0]))
        clock_patch.start()
        self.addCleanup(clock_patch.stop)
        self.online = [False]
        self.read = Mock(side_effect=lambda: self.online[0])
        self.fixture.service.connectivity = ConnectivityRestoration(read=self.read, clock=lambda: self.now[0])
        self.fixture.service.begin({'template_a': 1})
        self.ticket = self.fixture.flow.customer_ticket()
        self.fixture.paid()
        self.fixture.service.check()
        self.fixture.flow.lock_customer()
        self.fixture.flow.require_recovery()
        self.fixture.provider.outage = True
        self.fixture.service.check()  # First failed provider read, restart priority.
        self.now[0] += 12
        self.fixture.service.check()  # Second failure, longer backoff.
        self.now[0] += 23
        self.fixture.service.check()  # Third failure, ~40s backoff.
        self.before = self.fixture.flow.snapshot()
        self.reads = self.fixture.provider.reads
        self.now[0] += 5

    def restore_connection(self):
        self.online[0] = True
        self.fixture.provider.outage = False
        return self.fixture.service.check()

    def assert_original_private_hold(self, view):
        self.assertEqual(view['phase'], 'RECOVERY')
        self.assertEqual(view['checkout_key'], self.before['checkout_key'])
        for field in ('order_id', 'grant_id', 'service_state', 'local_transaction_id'):
            self.assertEqual(view['order'][field], self.before['order'][field])
        self.assertTrue(view['customer_claim_required'])
        self.assertFalse(view['resume_ready'])
        self.assertIsNone(view['qr_rgb'])
        self.assertEqual(self.fixture.provider.charges, 1)
        self.assertEqual(self.fixture.store.db.execute('SELECT count(*) FROM checkouts').fetchone()[0], 1)
        self.assertEqual(self.fixture.store.db.execute('SELECT count(*) FROM checkout_fulfillments').fetchone()[0], 1)
        self.assertEqual(self.fixture.store.fulfillment(view['order']['order_id'], 'PB001')['obligation_state'], 'OWED')

    def test_pay08_observed_restoration_bypasses_backoff_with_one_get_and_no_new_effects(self):
        self.assertLess(self.now[0], self.fixture.flow._reconcile_at)
        view = self.restore_connection()
        self.assertEqual(self.fixture.provider.reads, self.reads + 1)
        self.assertTrue(view['order']['reconciliation']['checked'])
        self.assertEqual(view['order']['reconciliation']['outcome'], 'paid')
        self.assert_original_private_hold(view)
        for _ in range(30):
            self.fixture.service.check()
        self.assertEqual(self.fixture.provider.reads, self.reads + 1)
        with self.assertRaises(RuntimeError):
            self.fixture.flow.resume_permit()
        self.assertFalse((self.fixture.root / 'photo-tests').exists())

    def test_repeated_signal_and_database_reopen_cannot_bypass_persisted_priority(self):
        self.restore_connection()
        self.now[0] += 1
        self.assertTrue(self.fixture.flow.connectivity_restored())
        self.assertEqual(self.fixture.provider.reads, self.reads + 1)
        self.fixture.flow.close()
        self.fixture.store.close()
        self.fixture.store = CheckoutStore(self.fixture.root / 'orders.sqlite', now=lambda: self.now[0])
        self.fixture.backend = CheckoutBackend(self.fixture.store, self.fixture.provider, KEY, MERCHANT)
        session = InProcessSession(create_app(self.fixture.backend, BoothAuthenticator({'PB001': 'a' * 48})))
        client = QrisKioskClient('http://127.0.0.1:8765', 'PB001', 'a' * 48,
                                 allow_local_http=True, session=session)
        self.fixture.flow = KioskCheckout(self.fixture.root / 'visit.json', client,
            mode='sandbox', booth_id='PB001', endpoint=client.base_url)
        self.fixture.service.flow = self.fixture.flow
        self.assertTrue(self.fixture.flow.connectivity_restored())
        self.assertEqual(self.fixture.provider.reads, self.reads + 1)
        self.assertFalse(self.fixture.flow.snapshot()['order']['reconciliation']['checked'])
        self.assert_original_private_hold(self.fixture.service.view())

    def test_inflight_provider_lease_cannot_be_bypassed_by_restoration(self):
        oid = self.before['order']['order_id']
        reservation = self.fixture.store.begin_reconciliation(oid, urgent=True)
        self.assertIsNotNone(reservation)
        view = self.restore_connection()
        self.assertEqual(self.fixture.provider.reads, self.reads)
        self.assertFalse(view['order']['reconciliation']['checked'])
        self.assert_original_private_hold(view)
        self.fixture.store.finish_reconciliation(oid, reservation)

    def test_online_hint_with_provider_still_offline_or_refunded_never_authorizes_resume(self):
        self.online[0] = True
        view = self.fixture.service.check()
        self.assertEqual(self.fixture.provider.reads, self.reads + 1)
        self.assertFalse(view['order']['reconciliation']['checked'])
        self.assert_original_private_hold(view)
        self.online[0] = False
        self.now[0] += 5
        self.fixture.service.check()
        self.online[0] = True
        self.now[0] += 5
        self.fixture.provider.outage = False
        self.fixture.provider.rows[self.before['order']['order_id']].update(transaction_status='refund')
        view = self.fixture.service.check()
        self.assertEqual(view['order']['state'], 'REVIEW_REQUIRED')
        self.assertEqual(view['order']['grant_id'], self.before['order']['grant_id'])
        self.assertTrue(view['customer_claim_required'])
        self.assertFalse(view['resume_ready'])
        with self.assertRaises(RuntimeError):
            self.fixture.flow.resume_permit()
        self.assertEqual(self.fixture.provider.charges, 1)

    def test_unknown_hint_and_no_edge_preserve_existing_retry_schedule(self):
        self.online[0] = None
        for _ in range(30):
            self.fixture.service.check()
        self.assertEqual(self.fixture.provider.reads, self.reads)
        self.assertEqual(self.fixture.flow.snapshot()['order'], self.before['order'])

    def test_reader_uses_single_checkout_worker_and_cannot_return_private_media_after_lock(self):
        entered, release = threading.Event(), threading.Event()
        main_thread = threading.get_ident()
        def read():
            self.assertNotEqual(threading.get_ident(), main_thread)
            entered.set()
            if not release.wait(3):
                raise AssertionError('Synthetic reader barrier timed out')
            return True
        self.read.side_effect = read
        self.fixture.provider.outage = False
        self.assertTrue(self.fixture.jobs.submit('check', 1))
        try:
            self.assertTrue(entered.wait(1))
            self.assertFalse(self.fixture.jobs.submit('check', 1))
            self.fixture.flow.lock_customer()
            self.assertEqual(self.fixture.flow.snapshot()['checkout_key'], self.before['checkout_key'])
        finally:
            release.set()
        self.fixture.jobs.wait_closed(timeout=3)
        outcome = self.fixture.jobs.poll()
        self.assertIsNotNone(outcome)
        self.assertIsNone(outcome.error)
        self.assert_original_private_hold(outcome.value)
        self.assertEqual(self.fixture.provider.reads, self.reads + 1)

    def test_mock_and_no_active_order_do_not_sample_os_or_send_reconciliation(self):
        for mode, active, order in (('mock', True, {'verification_pending': True}),
                                    ('sandbox', False, None)):
            with self.subTest(mode=mode, active=active):
                flow = Mock(context={'mode': mode}, active=active)
                flow.snapshot.return_value = {'phase': 'RECOVERY', 'order': order}
                observer = Mock()
                adapter = SandboxCheckout(flow, connectivity=observer)
                with patch.object(adapter, 'view', return_value={}):
                    adapter.check()
                observer.poll.assert_not_called()
                flow.connectivity_restored.assert_not_called()
