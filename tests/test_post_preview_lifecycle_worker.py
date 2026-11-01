"""Original-order background recovery; synthetic provider, no customer output."""
import hashlib
import json
import threading
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from photobooth.booth_auth import BoothAuthenticator
from photobooth.post_preview_api import create_app
from photobooth.post_preview_inbox import PostPreviewNotificationInbox
from photobooth.post_preview_checkout import canonical, digest
from photobooth.post_preview_lifecycle import PostPreviewLifecycleWorker
from tests import test_post_preview_payments as payment_fixtures


class LifecycleWorkerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = payment_fixtures.PostPreviewPaymentTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.service, self.ledger = self.fixture.service, self.fixture.ledger
        self.group = self.fixture.group
        self.inbox = PostPreviewNotificationInbox(self.service)
        self.worker = PostPreviewLifecycleWorker(self.service, self.inbox)
        self.addCleanup(self.worker.stop)

    def test_lost_create_reply_restart_and_unknown_keep_same_order_without_post(self):
        self.fixture.provider.lost_create = True
        self.fixture.provider.not_found = 1
        first = self.fixture.begin()
        self.assertEqual('UNKNOWN', first['state'])
        original = self.fixture.order()
        self.fixture.provider.outage = True
        self.worker.run_once()
        self.assertFalse(self.service.inspect(self.group, 'PB001')['paid_verified'])
        self.fixture.provider.outage = False
        restarted = PostPreviewLifecycleWorker(self.service, self.inbox)
        restarted.run_once()
        self.assertEqual('PENDING', self.service.inspect(self.group, 'PB001')['state'])
        self.assertEqual(original, self.fixture.order())
        self.assertEqual(1, self.fixture.provider.charges)

    def test_cancel_intent_survives_restart_and_settlement_race_owed_once(self):
        self.fixture.begin()
        self.fixture.provider.settle_on_cancel = True
        self.ledger.lifecycle_event(self.fixture.lease, 'USER_CANCEL')
        self.worker.run_once()
        first = self.service.inspect(self.group, 'PB001')
        for _ in range(3): self.worker.run_once()
        last = self.service.inspect(self.group, 'PB001')
        self.assertEqual('PAID_UNCLAIMED', last['state'])
        self.assertEqual(first['entitlement_id'], last['entitlement_id'])
        self.assertEqual('OWED', last['obligation_state'])
        self.assertFalse(last['fulfillment_authorized'])
        self.assertEqual(1, self.fixture.provider.cancels)
        self.assertEqual(0, self.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_suspension_and_expiry_never_renew_or_cancel_in_background(self):
        self.fixture.begin()
        self.service.signal_lifecycle(self.fixture.lease, 'APP_SUSPENDED')
        self.fixture.provider.state(self.fixture.order(), 'expire')
        self.worker.run_once()
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(0, self.fixture.provider.cancels)
        self.fixture.provider.state(self.fixture.order(), 'settlement')
        self.worker.run_once()
        self.assertEqual('PAID_UNCLAIMED', self.service.inspect(self.group, 'PB001')['state'])

    def test_no_prepared_create_is_dispatched_by_background_worker(self):
        self.fixture.offered()
        self.service._prepare(self.fixture.lease, observation=self.fixture.ready)
        self.worker.run_once()
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertIsNone(self.service.inspect(self.group, 'PB001')['entitlement_id'])

    def test_webhook_inbox_is_applied_by_independent_provider_get(self):
        self.fixture.begin()
        order = self.fixture.order()
        note = dict(order_id=order, status_code='200', gross_amount='10000', transaction_status='settlement')
        note['signature_key'] = hashlib.sha512((order+'200'+'10000'+self.fixture.key).encode()).hexdigest()
        self.inbox.accept(note)
        self.worker.run_once()
        self.assertIsNone(self.service.inspect(self.group, 'PB001')['entitlement_id'])
        self.assertEqual('APPLIED', self.ledger.db.execute('SELECT state FROM pp_notification_inbox').fetchone()[0])
        self.fixture.provider.state(order, 'settlement')
        self.worker.run_once()
        self.assertEqual('PAID_LIVE', self.service.inspect(self.group, 'PB001')['state'])

    def test_unavailable_inbox_does_not_prevent_original_order_reconciliation(self):
        self.fixture.begin()
        self.fixture.provider.state(self.fixture.order(), 'settlement')
        with patch.object(self.inbox, 'process_one', side_effect=OSError('private driver fixture')):
            report = self.worker.run_once()
        self.assertEqual(1, report['errors'])
        self.assertEqual('PAID_LIVE', self.service.inspect(self.group, 'PB001')['state'])
        self.assertNotIn('private driver fixture', repr(report))

    def test_provider_pacing_and_leased_reconciliation_remain_authoritative(self):
        self.fixture.begin()
        self.service.poll_seconds = 10
        self.worker.run_once()
        reads = self.fixture.provider.reads
        self.worker.run_once()
        self.assertEqual(reads, self.fixture.provider.reads)
        self.fixture.fixture.clock[0] += 10
        self.worker.run_once()
        self.assertEqual(reads+1, self.fixture.provider.reads)

    def test_round_robin_does_not_starve_later_groups(self):
        self.fixture.begin()
        # Additional isolated original finance scopes, without payable attempts.
        for index in (2, 3):
            lease = self.ledger.create('PB00'+str(index), 'visit', {'template_a': 1})
            contract = json.loads(self.fixture.fixture.intent['contract_json'])
            contract.update(draft_id=lease.draft_id, booth_id=lease.booth_id)
            with self.ledger.write():
                group = 'fixture_group_'+str(index)
                self.ledger.db.execute('INSERT INTO pp_checkout_intents VALUES(?,?,?,?,?,?,?)',
                    (group, lease.draft_id, contract['revision'], canonical(contract), digest(contract),
                     'CREATE_PREPARED', self.ledger.now()))
                self.ledger.db.execute('INSERT INTO pp_purchase_finance(purchase_group_id,merchant_id,provider_mode,amount) VALUES(?,?,?,?)',
                                      (group, 'MTEST', 'mock', 10000))
        self.worker = PostPreviewLifecycleWorker(self.service, self.inbox, max_groups=1)
        seen = []
        reconcile = self.service.reconcile_all
        def track(group, booth):
            seen.append(group)
            return reconcile(group, booth)
        with patch.object(self.service, 'reconcile_all', side_effect=track):
            for _ in range(6): self.worker.run_once()
        self.assertEqual(3, len(set(seen[:3])))
        self.assertEqual(seen[:3], seen[3:])

    def test_api_lifespan_stops_worker_before_shutdown_closes_ledger(self):
        self.fixture.begin()
        self.fixture.provider.state(self.fixture.order(), 'settlement')
        applied = threading.Event()
        reconcile = self.service.reconcile_all
        def track(*args, **kwargs):
            result = reconcile(*args, **kwargs)
            applied.set()
            return result
        app = create_app(self.service, BoothAuthenticator({'PB001': 'a'*48}), inbox=self.inbox,
                         on_shutdown=lambda: self.assertFalse(app.state.lifecycle_worker.running))
        with patch.object(self.service, 'reconcile_all', side_effect=track), TestClient(app):
            self.assertTrue(app.state.lifecycle_worker.running)
            self.assertTrue(applied.wait(3))
            self.assertEqual('PAID_LIVE', self.service.inspect(self.group, 'PB001')['state'])
        self.assertFalse(app.state.lifecycle_worker.running)

    def test_stop_timeout_preserves_running_worker_and_prevents_duplicate_start(self):
        entered, release = threading.Event(), threading.Event()
        with patch.object(self.worker, 'run_once', side_effect=lambda: (entered.set(), release.wait(5))):
            self.worker.start()
            self.assertTrue(entered.wait(2))
            try:
                self.assertFalse(self.worker.stop(timeout=0))
                self.assertTrue(self.worker.running)
                with self.assertRaises(RuntimeError): self.worker.start()
            finally:
                release.set()
                self.assertTrue(self.worker.stop(timeout=2))


if __name__ == '__main__': unittest.main()
