"""Opt-in offline inbox: no public route/listener, real merchant or service grant."""
from unittest import TestCase
from contextlib import closing
import hashlib,json
from photobooth.notification_inbox import LegacyNotificationInbox
from photobooth.checkout_store import CheckoutStore
import tests.test_checkout_fulfillment as fixture

class NotificationInboxTests(TestCase):
    def setUp(self):
        fixture.FulfillmentTests.setUp(self);self.now=[1000.0];self.store.now=lambda:self.now[0]
        self.inbox=LegacyNotificationInbox(self.backend)
        self.message={'order_id':self.oid,'status_code':'200','gross_amount':'15000.00',
                      'transaction_status':'settlement','customer_email':'not-persisted@example.invalid'}
        self.message['signature_key']=hashlib.sha512((self.oid+'20015000.00'+fixture.KEY).encode()).hexdigest()
    def test_intake_is_durable_deduplicated_private_and_does_not_wait_for_provider(self):
        before=self.provider.reads;event=self.inbox.accept(self.message)
        self.assertEqual(self.inbox.accept(self.message),event);self.assertEqual(self.provider.reads,before)
        with closing(CheckoutStore(self.path)) as reopened:
            row=reopened.db.execute('SELECT * FROM checkout_notification_inbox').fetchone()
            self.assertEqual(row['state'],'NEW');self.assertNotIn('customer_email',row['payload'])
        self.provider.rows[self.oid].update(transaction_status='settlement',status_code='200')
        self.inbox.process_one();self.assertEqual(self.store.get(self.oid)['state'],'PAID')
        self.assertIsNone(self.store.get(self.oid)['grant_id'])
        self.assertFalse(self.inbox.process_one())
    def test_outage_retries_then_quarantines_without_false_payment_or_hot_loop(self):
        self.inbox.accept(self.message);self.provider.outage=True
        for delay in (10,20,40,60,60):
            self.assertTrue(self.inbox.process_one());self.assertFalse(self.inbox.process_one());self.now[0]+=delay
        row=self.store.db.execute('SELECT * FROM checkout_notification_inbox').fetchone()
        self.assertEqual(row['state'],'QUARANTINED');self.assertEqual(row['attempts'],5)
        self.assertNotEqual(self.store.get(self.oid)['state'],'PAID')
    def test_lost_worker_and_late_callback_are_fenced_after_lease_expiry(self):
        self.inbox.accept(self.message);old=self.inbox.claim();self.now[0]+=46
        current=self.inbox.claim();self.assertNotEqual(old['token'],current['token'])
        self.assertFalse(self.inbox.finish(old,True));self.assertTrue(self.inbox.finish(current,True))
    def test_bad_signature_capacity_and_bisnap_adapter_are_rejected(self):
        with self.assertRaises(ValueError):self.inbox.accept(dict(self.message,signature_key='bad'))
        with self.assertRaises(ValueError):LegacyNotificationInbox(self.backend,adapter='bi-snap')
        limited=LegacyNotificationInbox(self.backend,capacity=1);limited.accept(self.message)
        with self.assertRaises(RuntimeError):limited.accept(dict(self.message,transaction_status='pending'))
    def test_stale_callback_queries_current_refund_without_new_grant(self):
        fixture.FulfillmentTests.paid(self)
        self.provider.rows[self.oid].update(transaction_status='refund')
        self.inbox.accept(self.message);self.inbox.process_one()
        self.assertEqual(self.store.get(self.oid)['state'],'REVIEW_REQUIRED')
        self.assertIsNone(self.store.get(self.oid)['grant_id'])
    def test_repeated_worker_crashes_eventually_quarantine_without_sixth_attempt(self):
        self.inbox.accept(self.message)
        for _ in range(5):
            self.assertIsNotNone(self.inbox.claim());self.now[0]+=46
        self.assertIsNone(self.inbox.claim())
        self.assertEqual(self.store.db.execute('SELECT state FROM checkout_notification_inbox').fetchone()[0],'QUARANTINED')
