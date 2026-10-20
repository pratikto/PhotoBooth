"""Failure/restart coverage for the authoritative checkout ledger, no network."""
from concurrent.futures import ThreadPoolExecutor
import tempfile
from pathlib import Path
import unittest
from photobooth.checkout_store import CheckoutStore, CheckoutConflict, CheckoutMissing


class CheckoutDurabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'checkout.db'
        self.store = CheckoutStore(self.path)
        self.key = 'visit-a-' + 'a' * 24
        self.order, self.fresh = self.store.begin('PB001', {'template_a': 1}, 10000, self.key)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def evidence(self, state='settlement'):
        return {'order_id': self.order['id'], 'amount': 10000, 'transaction_id': 'provider-1',
                'merchant_id': 'merchant-1', 'transaction_status': state}

    def test_repeated_create_has_same_identity_after_restart(self):
        self.store.close(); self.store = CheckoutStore(self.path)
        order, fresh = self.store.begin('PB001', {'template_a': 1}, 10000, self.key)
        self.assertEqual(order['id'], self.order['id']); self.assertFalse(fresh)

    def test_same_key_cannot_change_cart(self):
        with self.assertRaises(CheckoutConflict):
            self.store.begin('PB001', {'template_a': 2}, 15000, self.key)

    def test_new_key_cannot_replace_active_payment(self):
        with self.assertRaises(CheckoutConflict):
            self.store.begin('PB001', {'template_a': 1}, 10000, 'b' * 32)

    def test_unpaid_and_other_booth_cannot_claim(self):
        with self.assertRaises(CheckoutConflict): self.store.grant(self.order['id'], 'PB001', self.key)
        with self.assertRaises(CheckoutMissing): self.store.get(self.order['id'], 'PB002')

    def test_lost_claim_response_replays_same_grant(self):
        self.store.apply_evidence(self.order['id'], self.evidence())
        grant = self.store.grant(self.order['id'], 'PB001', self.key)['grant_id']
        self.store.close(); self.store = CheckoutStore(self.path)
        self.assertEqual(self.store.grant(self.order['id'], 'PB001', self.key)['grant_id'], grant)

    def test_concurrent_grants_return_one_permit(self):
        self.store.apply_evidence(self.order['id'], self.evidence())
        with ThreadPoolExecutor(max_workers=16) as pool:
            grants = list(pool.map(lambda _: self.store.grant(self.order['id'], 'PB001', self.key)['grant_id'], range(64)))
        self.assertEqual(len(set(grants)), 1)

    def test_independent_connection_grant_race(self):
        self.store.apply_evidence(self.order['id'], self.evidence())
        second = CheckoutStore(self.path)
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                grants = list(pool.map(lambda s: s.grant(self.order['id'], 'PB001', self.key)['grant_id'], (self.store, second)))
            self.assertEqual(grants[0], grants[1])
        finally: second.close()

    def test_late_paid_is_review_not_next_customer(self):
        self.store.apply_evidence(self.order['id'], self.evidence('expire'))
        self.store.close_visit(self.order['id'], 'PB001')
        new, _ = self.store.begin('PB001', {'template_a': 1}, 10000, 'b' * 32)
        old = self.store.apply_evidence(self.order['id'], self.evidence())
        self.assertEqual(old['state'], 'REVIEW_REQUIRED')
        self.assertEqual(self.store.get(new['id'])['state'], 'CREATED')
        with self.assertRaises(CheckoutConflict): self.store.grant(self.order['id'], 'PB001', self.key)

    def test_terminal_and_paid_statuses_do_not_regress(self):
        self.store.apply_evidence(self.order['id'], self.evidence())
        self.assertEqual(self.store.apply_evidence(self.order['id'], self.evidence('pending'))['state'], 'PAID')

    def test_service_replay_cannot_allocate_different_capture(self):
        self.store.apply_evidence(self.order['id'], self.evidence())
        grant = self.store.grant(self.order['id'], 'PB001', self.key)['grant_id']
        for _ in range(2):
            self.store.service_transition(self.order['id'], 'PB001', grant, 'STARTED', 'PB001_00000001')
        with self.assertRaises(CheckoutConflict):
            self.store.service_transition(self.order['id'], 'PB001', grant, 'STARTED', 'PB001_00000002')
        self.store.service_transition(self.order['id'], 'PB001', grant, 'COMPLETED', 'PB001_00000001')
        new, fresh = self.store.begin('PB001', {'template_a': 1}, 10000, 'b' * 32)
        self.assertTrue(fresh)

    def test_event_deduplication(self):
        one = self.store.event(self.evidence(), 'RETRY')
        self.assertEqual(one, self.store.event(self.evidence(), 'APPLIED'))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkout_events').fetchone()[0], 1)

    def test_poll_reservation_throttles_independent_calls(self):
        self.assertTrue(self.store.reserve_check(self.order['id']))
        self.assertFalse(self.store.reserve_check(self.order['id']))

    def test_partial_refund_freezes_fulfillment(self):
        self.store.apply_evidence(self.order['id'], self.evidence())
        result = self.store.apply_evidence(self.order['id'], self.evidence('partial_refund'))
        self.assertEqual(result['state'], 'REVIEW_REQUIRED')

    def test_prior_prototype_orders_are_not_forgotten(self):
        from photobooth.payment_orders import OrderStore
        path = Path(self.tmp.name) / 'legacy.db'
        old = OrderStore(path)
        old_id = old.create('PB001', {'template_a': 1}, 10000)
        old.close()
        migrated = CheckoutStore(path)
        try:
            self.assertEqual(migrated.get(old_id)['state'], 'REVIEW_REQUIRED')
            with self.assertRaises(CheckoutConflict):
                migrated.begin('PB001', {'template_a': 1}, 10000, self.key)
        finally: migrated.close()
