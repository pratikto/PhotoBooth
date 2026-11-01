"""Real process death across local journal and persistent synthetic remote ledger."""
from pathlib import Path
import subprocess
import sys
import unittest

from photobooth.post_preview_inbox import PostPreviewNotificationInbox
from photobooth.post_preview_payments import PostPreviewPayments
from tests import test_post_preview_api as api_fixtures
from tests.post_preview_payment_crash_fixture import PersistentSyntheticProvider


class PostPreviewPaymentCrashTests(unittest.TestCase):
    def setUp(self):
        self.fixture = api_fixtures.PostPreviewApiTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.pay = self.fixture.fixture
        self.pay.offered()
        self.ledger = self.pay.ledger
        self.group = self.pay.group
        self.provider_path = self.pay.fixture.root/'synthetic-provider.db'
        self.provider = PersistentSyntheticProvider(self.provider_path)
        self.addCleanup(self.provider.close)
        self.service = PostPreviewPayments(self.ledger, self.provider, 'MTEST',
            readiness=lambda _: self.pay.ready, server_key=self.pay.key, poll_seconds=0)

    def crash(self, fault):
        child = subprocess.run([sys.executable, str(Path(__file__).with_name('post_preview_payment_crash_fixture.py')),
            str(self.pay.fixture.root/'drafts.db'), str(self.provider_path), self.group, fault],
            capture_output=True, timeout=20)
        self.assertEqual(73, child.returncode, child.stderr.decode(errors='replace'))
        self.pay.fixture.clock[0] += 46

    def test_prepared_before_send_can_send_same_original_exactly_once(self):
        self.crash('after_prepare')
        view = self.service.begin(self.pay.lease)
        self.assertEqual('PENDING', view['state'])
        self.service.begin(self.pay.lease)
        self.assertEqual(1, self.provider.count('create'))
        self.assertEqual(1, len(view['attempts']))

    def test_sent_before_remote_commit_is_unknown_and_never_reposted(self):
        self.crash('before_remote_create')
        view = self.service.begin(self.pay.lease)
        self.assertEqual('UNKNOWN', view['state'])
        self.assertEqual(0, self.provider.count('create'))
        self.assertEqual(1, len(view['attempts']))

    def test_remote_commit_without_response_recovers_same_order_without_create(self):
        self.crash('after_remote_create')
        view = self.service.begin(self.pay.lease)
        self.assertEqual('PENDING', view['state'])
        self.assertEqual(1, self.provider.count('create'))
        self.assertEqual(1, len(view['attempts']))

    def test_paid_get_interrupted_before_local_apply_preserves_one_entitlement(self):
        view = self.service.begin(self.pay.lease)
        self.provider.state(view['attempts'][0]['provider_order_id'], 'settlement')
        self.crash('after_remote_get')
        self.assertIsNone(self.service.inspect(self.group, 'PB001')['entitlement_id'])
        first = self.service.reconcile_all(self.group, 'PB001', force=True)
        second = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.assertTrue(first['paid_verified'])
        self.assertEqual(first['entitlement_id'], second['entitlement_id'])
        self.assertEqual(1, self.provider.count('create'))

    def test_cancel_remote_commit_without_response_is_not_sent_twice(self):
        self.service.begin(self.pay.lease)
        self.crash('after_remote_cancel')
        view = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual('CANCELLED_UNPAID', view['state'])
        self.assertEqual(1, self.provider.count('cancel'))
        self.assertFalse(view['fulfillment_authorized'])

    def test_acknowledged_inbox_claim_survives_killed_worker(self):
        view = self.service.begin(self.pay.lease)
        self.provider.state(view['attempts'][0]['provider_order_id'], 'settlement')
        inbox = PostPreviewNotificationInbox(self.service)
        inbox.accept(self.fixture.notification())
        self.crash('after_inbox_claim')
        self.assertTrue(inbox.process_one())
        self.assertEqual('APPLIED', self.ledger.db.execute('SELECT state FROM pp_notification_inbox').fetchone()[0])
        self.assertEqual('PAID_LIVE', self.service.inspect(self.group, 'PB001')['state'])
