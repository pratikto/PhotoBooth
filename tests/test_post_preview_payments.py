"""Synthetic normalized-provider faults; never real Midtrans/charge/refund/Drive."""
import hashlib
import sqlite3
from dataclasses import replace
import threading
import unittest

from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_store import DraftHeld, PostPreviewStore


class SyntheticProvider:
    mode = 'mock'

    def __init__(self):
        self.rows = {}
        self.charges = self.cancels = self.reads = 0
        self.lost_create = False
        self.not_found = 0
        self.outage = False
        self.settle_on_cancel = False
        self.create_entered = self.create_release = None
        self.get_entered = self.get_release = None
        self.get_block_once = False
        self.lose_cancel_response = False

    def create_qris(self, order_id, amount):
        self.charges += 1
        row = dict(order_id=order_id, gross_amount=str(amount), transaction_status='pending',
                   status_code='201', currency='IDR', payment_type='qris', merchant_id='MTEST',
                   transaction_id='fixture_'+order_id, fraud_status='accept')
        self.rows[order_id] = row
        if self.create_entered:
            self.create_entered.set(); self.create_release.wait(5)
        if self.lost_create: raise OSError('synthetic lost create response')
        return dict(row, actions=[{'name': 'generate-qr-code', 'method': 'GET',
            'url': 'https://api.sandbox.midtrans.com/v4/qris/'+row['transaction_id']+'/qr-code'}])

    def get_status(self, order_id):
        self.reads += 1
        if self.get_block_once:
            self.get_block_once = False
            response = dict(self.rows[order_id])
            self.get_entered.set(); self.get_release.wait(5)
            return response
        if self.outage: raise OSError('synthetic provider outage')
        if self.not_found:
            self.not_found -= 1
            return {'status_code': '404'}
        return dict(self.rows.get(order_id, {'status_code': '404'}))

    def state(self, order_id, state):
        self.rows[order_id].update(transaction_status=state, status_code='200')

    def cancel(self, order_id):
        self.cancels += 1
        self.state(order_id, 'settlement' if self.settle_on_cancel else 'cancel')
        if self.lose_cancel_response: raise OSError('synthetic lost cancellation response')
        return dict(self.rows[order_id])


class PostPreviewPaymentTests(unittest.TestCase):
    def setUp(self):
        from tests.test_post_preview_ccp import OriginalCCPTests
        self.fixture = OriginalCCPTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.ledger, self.lease = self.fixture.ledger, self.fixture.lease
        self.group = self.fixture.intent['purchase_group_id']
        self.provider = SyntheticProvider()
        self.ready = ChargeReadiness(True, True, True, True, True, True, True, 25)
        self.service = self.new_service()
        self.key = 'SYNTHETIC-NONMERCHANT-SIGNATURE-KEY'
        self.service._server_key = self.key

    def new_service(self, **kwargs):
        return PostPreviewPayments(self.ledger, self.provider, kwargs.get('merchant', 'MTEST'),
            readiness=lambda group: self.ready, poll_seconds=0)

    def offered(self):
        offer = self.fixture.offer()
        self.fixture.service.mark_visible(self.lease, offer)

    def begin(self):
        self.offered()
        return self.service.begin(self.lease)

    def order(self, view=None):
        view = view or self.service.inspect(self.group, 'PB001')
        return view['attempts'][-1]['provider_order_id']

    def test_no_payment_without_genuinely_offered_original_ccp(self):
        self.assertEqual('NOT_CREATED', self.service.inspect(self.group, 'PB001')['state'])
        self.fixture.issue()
        with self.assertRaises(DraftHeld): self.service.begin(self.lease)
        self.assertEqual(0, self.provider.charges)
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_purchase_finance').fetchone()[0])

    def test_one_pending_attempt_preserves_verified_create_action_and_frozen_cart(self):
        view = self.begin()
        self.assertEqual('PENDING', view['state'])
        self.assertEqual(10000, view['amount'])
        self.assertIn('/v4/qris/', view['qr_url'])
        original = self.order(view)
        for _ in range(3): self.service.begin(self.lease)
        self.assertEqual(1, self.provider.charges)
        self.assertEqual(original, self.order())
        self.assertIsNone(view['entitlement_id'])
        self.assertFalse(view['fulfillment_authorized'])

    def test_lost_post_reply_and_404_reconcile_same_original_after_restart(self):
        self.provider.lost_create = True
        self.provider.not_found = 1
        view = self.begin()
        self.assertEqual('UNKNOWN', view['state'])
        original = self.order(view)
        restarted = self.new_service()
        view = restarted.begin(self.lease)
        self.assertEqual('PENDING', view['state'])
        self.assertEqual(original, self.order(view))
        self.assertEqual(1, self.provider.charges)

    def test_unknown_status_is_not_unpaid_or_permission_for_replacement(self):
        self.begin()
        self.provider.outage = True
        with self.assertRaises(DraftHeld): self.service.continue_expired(self.lease, actively_continuing=True)
        self.assertEqual(1, self.provider.charges)
        self.assertFalse(self.service.reconcile(self.group, 'PB001', force=True)['fresh_checked'])

    def test_qr1_qr2_qr3_require_fresh_expiry_same_customer_and_never_qr4(self):
        view = self.begin()
        contract = self.ledger.db.execute('SELECT contract_json FROM pp_checkout_intents').fetchone()[0]
        for ordinal in (2, 3):
            self.provider.state(self.order(view), 'expire')
            view = self.service.continue_expired(self.lease, actively_continuing=True)
            self.assertEqual(ordinal, view['attempts'][-1]['ordinal'])
            self.assertEqual(10000, view['amount'])
        self.provider.state(self.order(view), 'expire')
        with self.assertRaises(DraftHeld): self.service.continue_expired(self.lease, actively_continuing=True)
        self.assertEqual(3, self.provider.charges)
        self.assertEqual(contract, self.ledger.db.execute('SELECT contract_json FROM pp_checkout_intents').fetchone()[0])
        self.assertEqual(3, len(self.provider.rows))

    def test_cancel_unpaid_never_renews_even_if_previous_order_later_expires(self):
        view = self.begin()
        self.service.signal_lifecycle(self.lease, 'USER_CANCEL')
        self.assertEqual(1, self.provider.cancels)
        self.provider.state(self.order(view), 'expire')
        self.service.signal_lifecycle(self.lease, 'USER_CANCEL')
        with self.assertRaises(DraftHeld): self.service.continue_expired(self.lease, actively_continuing=True)
        self.assertEqual(1, self.provider.charges)
        self.assertEqual(1, self.provider.cancels)

    def test_cancel_racing_settlement_preserves_paid_unclaimed_owed_without_release(self):
        self.begin()
        self.provider.settle_on_cancel = True
        view = self.service.signal_lifecycle(self.lease, 'USER_CANCEL')
        self.assertEqual('PAID_UNCLAIMED', view['state'])
        self.assertEqual('OWED', view['obligation_state'])
        self.assertIsNotNone(view['entitlement_id'])
        self.assertIsNone(view['qr_url'])
        self.assertFalse(view['fulfillment_authorized'])
        self.assertEqual(0, self.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_suspend_does_not_cancel_or_renew_and_late_paid_is_private(self):
        view = self.begin()
        self.service.signal_lifecycle(self.lease, 'APP_SUSPENDED')
        self.assertEqual(0, self.provider.cancels)
        self.provider.state(self.order(view), 'settlement')
        result = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual('PAID_UNCLAIMED', result['state'])
        self.assertTrue(result['paid_verified'])
        self.assertIsNone(result['qr_url'])
        with self.assertRaises(DraftHeld): self.service.begin(self.lease)
        self.assertEqual(1, self.provider.charges)

    def test_explicit_abandonment_recovers_cancel_intent_after_interrupted_finance_write(self):
        self.begin()
        # Crash seam: lifecycle committed; finance cancel update never ran.
        self.ledger.lifecycle_event(self.lease, 'VISIT_ABANDONED')
        self.new_service().reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual(1, self.provider.cancels)
        self.assertEqual('CANCELLED_UNPAID', self.service.inspect(self.group, 'PB001')['state'])
        self.assertEqual(0, self.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_duplicate_settlements_get_exactly_one_entitlement_and_record_excess(self):
        first = self.begin()
        order1 = self.order(first)
        self.provider.state(order1, 'expire')
        second = self.service.continue_expired(self.lease, actively_continuing=True)
        order2 = self.order(second)
        self.provider.state(order1, 'settlement')
        paid = self.service.reconcile_all(self.group, 'PB001', force=True)
        entitlement = paid['entitlement_id']
        self.assertEqual('PAID_LIVE', paid['state'])
        self.provider.state(order2, 'settlement')
        for _ in range(3):
            paid = self.service.reconcile_all(self.group, 'PB001', force=True)
            self.assertEqual(entitlement, paid['entitlement_id'])
            self.assertEqual(1, len(paid['excess_paid_attempts']))
        self.assertEqual(1, self.ledger.db.execute('SELECT count(entitlement_id) FROM pp_purchase_finance').fetchone()[0])
        self.assertEqual(2, self.provider.charges)

    def test_unsigned_or_stale_notification_never_grants_without_fresh_get(self):
        view = self.begin()
        order = self.order(view)
        note = {'order_id': order, 'status_code': '200', 'gross_amount': '10000',
                'transaction_status': 'settlement', 'signature_key': '0'*128}
        reads = self.provider.reads
        with self.assertRaises(ValueError): self.service.notification(note)
        self.assertEqual(reads, self.provider.reads)
        note['signature_key'] = hashlib.sha512((order+'200'+'10000'+self.key).encode()).hexdigest()
        result = self.service.notification(note)
        self.assertEqual('PENDING', result['state'])
        self.assertIsNone(result['entitlement_id'])
        self.provider.state(order, 'settlement')
        result = self.service.notification(note)
        self.assertTrue(result['paid_verified'])
        original = result['entitlement_id']
        self.assertEqual(original, self.service.notification(note)['entitlement_id'])

    def test_amount_or_merchant_mismatch_enters_review_without_service_or_new_charge(self):
        view = self.begin()
        self.provider.rows[self.order(view)].update(transaction_status='settlement', status_code='200', gross_amount='99999')
        result = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual('REVIEW_REQUIRED', result['state'])
        self.assertIsNone(result['entitlement_id'])
        self.assertFalse(result['fulfillment_authorized'])
        self.assertEqual(1, self.provider.charges)

    def test_context_change_or_missing_attempt_journal_cannot_create_another_payment(self):
        self.begin()
        with self.assertRaises(DraftHeld): self.new_service(merchant='OTHER').begin(self.lease)
        self.ledger.db.execute('DELETE FROM pp_payment_attempts')
        with self.assertRaises(DraftHeld): self.service.begin(self.lease)
        self.assertEqual(1, self.provider.charges)

    def test_concurrent_begin_uses_one_durable_send_and_original_provider_order(self):
        self.offered()
        entered, release = threading.Event(), threading.Event()
        self.provider.create_entered, self.provider.create_release = entered, release
        outcomes = []
        errors = []
        def begin():
            try: outcomes.append(self.service.begin(self.lease))
            except Exception as error: errors.append(type(error).__name__)
        thread = threading.Thread(target=begin)
        thread.start()
        self.assertTrue(entered.wait(3))
        other_ledger = PostPreviewStore(self.fixture.root/'drafts.db', now=lambda: self.fixture.clock[0])
        self.addCleanup(other_ledger.close)
        second = PostPreviewPayments(other_ledger, self.provider, 'MTEST', readiness=lambda _: self.ready, poll_seconds=0)
        try: outcomes.append(second.begin(self.lease))
        finally: release.set(); thread.join(5)
        self.assertEqual([], errors)
        self.assertEqual(1, self.provider.charges)
        self.assertEqual(1, len({self.order(v) for v in outcomes}))

    def test_prepared_before_send_can_send_once_but_sent_unknown_is_never_reposted(self):
        self.offered()
        group, attempt = self.service._prepare(self.lease, observation=self.ready)
        self.assertEqual(0, self.provider.charges)
        self.new_service().begin(self.lease)
        self.assertEqual(1, self.provider.charges)
        self.assertEqual(attempt['provider_order_id'], self.order())

    def test_reconciliation_after_paid_outage_never_relabels_cached_paid_fresh(self):
        view = self.begin()
        self.provider.state(self.order(view), 'settlement')
        paid = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.provider.outage = True
        unknown = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual(paid['entitlement_id'], unknown['entitlement_id'])
        self.assertEqual('OWED', unknown['obligation_state'])
        self.assertFalse(unknown['fresh_checked'])
        self.assertFalse(unknown['paid_verified'])

    def test_known_unavailable_precharge_readiness_blocks_new_attempt_but_not_reconciliation(self):
        self.offered()
        self.ready = replace(self.ready, drive_authenticated=False)
        with self.assertRaises(DraftHeld): self.service.begin(self.lease)
        self.assertEqual(0, self.provider.charges)
        self.ready = replace(self.ready, drive_authenticated=True)
        view = self.service.begin(self.lease)
        self.ready = replace(self.ready, printer_route=False)
        self.assertEqual(self.order(view), self.order(self.service.begin(self.lease)))
        self.assertEqual(1, self.provider.charges)

    def test_verified_cancel_or_absent_customer_never_gets_expiry_renewal(self):
        view = self.begin()
        self.provider.state(self.order(view), 'expire')
        with self.assertRaises(DraftHeld): self.service.continue_expired(self.lease, actively_continuing=False)
        self.provider.state(self.order(view), 'cancel')
        with self.assertRaises(DraftHeld): self.service.continue_expired(self.lease, actively_continuing=True)
        self.assertEqual(1, self.provider.charges)

    def test_lost_cancel_response_restarts_same_cancel_reconciliation_without_second_post(self):
        self.begin()
        self.provider.lose_cancel_response = True
        self.provider.outage = True
        self.service.signal_lifecycle(self.lease, 'USER_CANCEL')
        self.assertEqual(1, self.provider.cancels)
        self.provider.outage = False
        result = self.new_service().reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual('CANCELLED_UNPAID', result['state'])
        self.assertEqual(1, self.provider.cancels)
        self.assertEqual(1, self.provider.charges)

    def test_qr1_settles_during_qr2_create_without_second_entitlement(self):
        first = self.begin()
        order1 = self.order(first)
        self.provider.state(order1, 'expire')
        entered, release = threading.Event(), threading.Event()
        self.provider.create_entered, self.provider.create_release = entered, release
        outcomes, errors = [], []
        def renew():
            try: outcomes.append(self.service.continue_expired(self.lease, actively_continuing=True))
            except Exception as error: errors.append(type(error).__name__)
        thread = threading.Thread(target=renew)
        thread.start()
        self.assertTrue(entered.wait(3))
        try:
            self.provider.state(order1, 'settlement')
            paid = self.new_service().reconcile_all(self.group, 'PB001', force=True)
        finally:
            release.set(); thread.join(5)
        self.assertEqual([], errors)
        self.assertEqual(paid['entitlement_id'], outcomes[0]['entitlement_id'])
        self.assertEqual(2, self.provider.charges)
        self.assertFalse(outcomes[0]['fulfillment_authorized'])

    def test_stale_pending_after_paid_preserves_money_but_cannot_authorize_live_service(self):
        view = self.begin()
        order = self.order(view)
        self.provider.state(order, 'settlement')
        paid = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.provider.state(order, 'pending')
        stale = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual(paid['entitlement_id'], stale['entitlement_id'])
        self.assertEqual('OWED', stale['obligation_state'])
        self.assertFalse(stale['paid_verified'])

    def test_expired_reconciliation_lease_retains_observed_paid_as_owed_not_fresh_access(self):
        view = self.begin()
        order = self.order(view)
        self.provider.state(order, 'settlement')
        entered, release = threading.Event(), threading.Event()
        self.provider.get_entered, self.provider.get_release = entered, release
        self.provider.get_block_once = True
        results = []
        thread = threading.Thread(target=lambda: results.append(self.service.reconcile(self.group, 'PB001', force=True)))
        thread.start()
        self.assertTrue(entered.wait(3))
        self.fixture.clock[0] += 46
        release.set(); thread.join(5)
        self.assertFalse(results[0]['fresh_checked'])
        self.assertFalse(results[0]['paid_verified'])
        self.assertEqual('OWED', results[0]['obligation_state'])
        self.assertIsNotNone(results[0]['entitlement_id'])
        self.assertFalse(results[0]['fulfillment_authorized'])

    def test_signed_notification_wrong_amount_rejected_before_status_read(self):
        view = self.begin()
        order = self.order(view)
        note = {'order_id': order, 'status_code': '200', 'gross_amount': '99999',
                'transaction_status': 'settlement'}
        note['signature_key'] = hashlib.sha512((order+'200'+'99999'+self.key).encode()).hexdigest()
        reads = self.provider.reads
        with self.assertRaises(ValueError): self.service.notification(note)
        self.assertEqual(reads, self.provider.reads)

    def test_schema_enforces_immutable_frozen_contract_attempt_and_original_entitlement(self):
        view = self.begin()
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute("UPDATE pp_checkout_intents SET contract_sha256='changed'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute("UPDATE pp_payment_attempts SET provider_order_id='other-order'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute('UPDATE pp_purchase_finance SET amount=99999')
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute("UPDATE pp_drafts SET visit_id='visitorB'")
        self.provider.state(self.order(view), 'settlement')
        paid = self.service.reconcile_all(self.group, 'PB001', force=True)
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute("UPDATE pp_purchase_finance SET entitlement_id='another-entitlement'")
        self.assertEqual(paid['entitlement_id'], self.service.inspect(self.group, 'PB001')['entitlement_id'])

    def test_revoked_proof_after_prepare_withholds_unsent_charge_without_reissue(self):
        self.offered()
        group, attempt = self.service._prepare(self.lease, observation=self.ready)
        self.fixture.service.revoke(self.lease)
        self.service._send_original(group, 'PB001', attempt['attempt_id'])
        view = self.service.inspect(group, 'PB001')
        self.assertEqual('NOT_CREATED', view['state'])
        self.assertEqual(0, self.provider.charges)
        self.assertEqual(1, len(view['attempts']))

    def test_inactivity_expiry_does_not_cancel_until_distinct_abandonment_is_recorded(self):
        self.begin()
        self.service.signal_lifecycle(self.lease, 'INACTIVITY_EXPIRED')
        self.service.reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual(0, self.provider.cancels)
        self.assertEqual('INACTIVITY_EXPIRED', self.ledger.db.execute('SELECT lifecycle FROM pp_drafts').fetchone()[0])
        self.service.signal_lifecycle(self.lease, 'VISIT_ABANDONED')
        self.assertEqual(1, self.provider.cancels)
        events = [r[0] for r in self.ledger.db.execute('SELECT event FROM pp_events ORDER BY sequence')]
        self.assertLess(events.index('INACTIVITY_EXPIRED'), events.index('VISIT_ABANDONED'))
        self.assertEqual(0, self.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_original_paid_anchor_never_extends_on_status_poll_or_restart(self):
        view = self.begin()
        self.provider.state(self.order(view), 'settlement')
        first = self.service.reconcile_all(self.group, 'PB001', force=True)
        self.fixture.clock[0] += 100
        second = self.new_service().reconcile_all(self.group, 'PB001', force=True)
        self.assertEqual(first['paid_first_observed_at'], second['paid_first_observed_at'])
        self.assertEqual(1000, second['paid_first_observed_at'])
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute('UPDATE pp_purchase_finance SET paid_first_observed_at=2000')


if __name__ == '__main__': unittest.main()
