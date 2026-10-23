"""MOCK authority, concurrency and restart tests; no provider or money."""

from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
import unittest

from photobooth.kiosk_v2.mock_checkout import MockCheckoutError, MockCheckoutStore


class MockCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.now = 1000
        self.store = self.reopen()

    def reopen(self):
        return MockCheckoutStore(self.temp.name, templates=['a', 'b'],
                                 pricing=lambda q: sum(q.values())*10000, clock=lambda:self.now)

    def order(self, key='request-key-00000001', attempt=None, quantities=None):
        return self.store.create(quantities or {'a':1}, key, attempt)

    def win(self, code='DEMO-WIN'):
        attempt = self.store.claim(code)['attempt_id']
        self.store.finish(attempt, 'won', 10)
        return attempt

    def test_regular_quote_is_authoritative_and_qr_cannot_be_paid(self):
        view=self.order(quantities={'b':2,'a':1})
        self.assertEqual((view['subtotal'],view['discount'],view['total']),(30000,0,30000))
        self.assertEqual(view['mode'],'MOCK')
        self.assertTrue(view['qr_payload'].startswith('MEONG MOCK ONLY - NOT QRIS - '))
        self.assertNotIn('paid',view)

    def test_win_candidate_is_read_from_ledger_and_reserved_once(self):
        attempt=self.win();view=self.order(attempt=attempt)
        self.assertEqual((view['subtotal'],view['discount'],view['total']),(10000,2500,7500))
        self.store.transition(view['order_id'],'confirm');self.store.admit(view['order_id'])
        with self.assertRaisesRegex(MockCheckoutError,'promo-used'):
            self.order('request-key-00000002',attempt)

    def test_lost_started_abandoned_candidates_never_discount(self):
        for result in ('lost','started','abandoned'):
            with self.subTest(result=result):
                attempt=self.store.claim('DEMO-'+result)['attempt_id']
                if result!='started':self.store.finish(attempt,result,0)
                view=self.order('request-key-'+result,attempt)
                self.assertEqual(view['discount'],0)
                self.store.transition(view['order_id'],'cancel')

    def test_forged_attempt_or_amount_never_creates_an_order(self):
        with self.assertRaisesRegex(MockCheckoutError,'invalid-attempt'):self.order(attempt='fake-win')
        for quantities in ({'a':True},{'a':-1},{'a':10},{'unknown':1},{'a':1,'total':1},{'a':0},{},None):
            with self.subTest(quantities=quantities),self.assertRaises(MockCheckoutError):
                self.store.create(quantities,'request-key-invalid')
        self.assertIsNone(self.store.recover())

    def test_invalid_keys_and_pricing_fail_closed(self):
        for key in ('',None,'short','x'*81,'abc!000000000000000000'):
            with self.assertRaises(MockCheckoutError):self.order(key)
        self.store.pricing=lambda _:True
        with self.assertRaisesRegex(MockCheckoutError,'invalid-quote'):self.order()

    def test_same_key_retries_return_same_order_and_changed_payload_is_rejected(self):
        first=self.order()
        self.assertEqual(self.reopen().create({'a':1,'b':0},first['request_key']),first)
        with self.assertRaisesRegex(MockCheckoutError,'key-conflict'):
            self.order(quantities={'a':2})

    def test_concurrent_retries_make_one_order(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            views=list(pool.map(lambda _:self.order(),range(16)))
        self.assertEqual(len({v['order_id'] for v in views}),1)

    def test_second_active_order_blocked_and_recovery_preserves_original_cart(self):
        first=self.order(quantities={'a':2})
        with self.assertRaisesRegex(MockCheckoutError,'outstanding-order'):self.order('request-key-00000002')
        recovered=self.reopen().open_checkout({'b':9},'request-key-00000002')
        self.assertEqual(recovered,first)

    def test_expiry_does_not_admit_or_revive_the_same_key(self):
        first=self.order();self.now+=181
        self.assertEqual(self.store.status(first['order_id'])['state'],'EXPIRED')
        self.assertIsNone(self.store.recover())
        self.assertEqual(self.order()['state'],'EXPIRED')
        with self.assertRaises(MockCheckoutError):self.store.transition(first['order_id'],'confirm')
        with self.assertRaises(MockCheckoutError):self.store.admit(first['order_id'])

    def test_cancelled_unused_promo_can_be_reserved_in_new_order(self):
        attempt=self.win();first=self.order(attempt=attempt)
        cancelled=self.store.transition(first['order_id'],'cancel')
        self.assertEqual(self.store.transition(first['order_id'],'cancel'),cancelled)
        self.assertEqual(self.order('request-key-00000002',attempt)['discount'],2500)

    def test_unknown_survives_expiry_restart_and_blocks_cancel_or_capture(self):
        first=self.order();oid=first['order_id'];self.store.transition(oid,'unknown');self.now+=999
        self.assertEqual(self.reopen().recover()['state'],'UNKNOWN')
        with self.assertRaisesRegex(MockCheckoutError,'unresolved'):self.store.transition(oid,'cancel')
        with self.assertRaises(MockCheckoutError):self.store.admit(oid)
        self.assertEqual(self.store.transition(oid,'reject')['state'],'CANCELLED')

    def test_confirm_and_pending_never_automatically_admit(self):
        first=self.order();oid=first['order_id']
        with self.assertRaises(MockCheckoutError):self.store.admit(oid)
        confirmed=self.store.transition(oid,'confirm')
        self.assertEqual(self.store.transition(oid,'confirm'),confirmed)
        self.assertIsNone(confirmed['admission_id'])
        self.assertEqual(self.reopen().recover()['state'],'CONFIRMED')
        with self.assertRaises(MockCheckoutError):self.store.transition(oid,'cancel')

    def test_concurrent_admission_is_one_time_and_restart_does_not_replay(self):
        oid=self.order()['order_id'];self.store.transition(oid,'confirm')
        def admit(_):
            try:return self.store.admit(oid)
            except MockCheckoutError:return None
        with ThreadPoolExecutor(max_workers=8) as pool:views=list(pool.map(admit,range(16)))
        self.assertEqual(sum(v is not None for v in views),1)
        self.assertEqual(self.reopen().status(oid)['state'],'ADMITTED')
        with self.assertRaises(MockCheckoutError):self.reopen().admit(oid)
        self.assertIsNone(self.reopen().recover())

    def test_unknown_can_only_be_resolved_explicitly_before_single_admission(self):
        oid=self.order()['order_id'];self.store.transition(oid,'unknown')
        self.store.transition(oid,'confirm');self.assertEqual(self.store.admit(oid)['state'],'ADMITTED')
        for action in ('confirm','unknown','cancel','reject','paid'):
            with self.assertRaises(MockCheckoutError):self.store.transition(oid,action)

    def test_unknown_order_never_invents_result(self):
        for method,args in ((self.store.status,('missing',)),(self.store.admit,('missing',)),
                            (self.store.transition,('missing','confirm'))):
            with self.assertRaises(MockCheckoutError):method(*args)


if __name__=='__main__':unittest.main()
