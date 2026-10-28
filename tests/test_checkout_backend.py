"""End-to-end service + SQLite with realistic offline Midtrans responses."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from photobooth.checkout_backend import CheckoutBackend, ProviderUnavailable
from photobooth.checkout_store import CheckoutStore, CheckoutConflict

KEY = 'sandbox-test-key'
MERCHANT = 'M12345'


class FakeProvider:
    def __init__(self):
        self.rows, self.charges, self.reads = {}, 0, 0
        self.outage = False
        self.lost_charge = False

    def create_qris(self, order_id, amount):
        self.charges += 1
        self.rows[order_id] = dict(order_id=order_id, gross_amount=str(amount),
            transaction_id='txn-' + order_id, merchant_id=MERCHANT, currency='IDR',
            payment_type='qris', fraud_status='accept', status_code='201',
            transaction_status='pending', expiry_time='2026-10-20 23:00:00')
        if self.lost_charge: raise TimeoutError('response lost')
        return self.rows[order_id].copy()

    def get_status(self, order_id):
        self.reads += 1
        if self.outage: raise TimeoutError('provider outage')
        return self.rows[order_id].copy()

    def cancel(self, order_id):
        if self.rows[order_id]['transaction_status'] != 'settlement':
            self.rows[order_id].update(transaction_status='cancel', status_code='202')


class CheckoutBackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.clock = [1000.0]
        self.store = CheckoutStore(Path(self.tmp.name) / 'orders.db', now=lambda: self.clock[0])
        self.provider = FakeProvider()
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        self.key = 'a' * 32
        self.order = self.backend.create_order('PB001', {'template_a': 2}, self.key)
        self.oid = self.order['order_id']

    def tearDown(self):
        self.store.close(); self.tmp.cleanup()

    def paid(self):
        self.provider.rows[self.oid].update(transaction_status='settlement', status_code='200')

    def callback(self, state='settlement'):
        data = dict(order_id=self.oid, gross_amount='15000.00', status_code='200', transaction_status=state)
        data['signature_key'] = hashlib.sha512((self.oid + '20015000.00' + KEY).encode()).hexdigest()
        return data

    def test_missing_webhook_is_reconciled_by_poll(self):
        self.paid()
        self.assertEqual(self.backend.status(self.oid, 'PB001')['state'], 'PAID')

    def test_repeat_create_never_charges_again(self):
        for _ in range(3):
            self.assertEqual(self.backend.create_order('PB001', {'template_a': 2}, self.key)['order_id'], self.oid)
        self.assertEqual(self.provider.charges, 1)

    def test_provider_outage_is_unknown_not_declined(self):
        self.provider.outage = True
        result = self.backend.status(self.oid, 'PB001')
        self.assertTrue(result['verification_pending']); self.assertEqual(result['state'], 'PENDING')

    def test_lost_charge_response_is_recovered_with_same_key(self):
        other = 'PB002'
        self.provider.lost_charge = True
        with self.assertRaises(ProviderUnavailable):
            self.backend.create_order(other, {'template_a': 2}, self.key)
        self.provider.lost_charge = False
        recovered = self.backend.create_order(other, {'template_a': 2}, self.key)
        self.assertEqual(recovered['state'], 'PENDING'); self.assertEqual(self.provider.charges, 2)
        self.assertEqual(recovered['qr_url'], 'https://api.sandbox.midtrans.com/v2/qris/' +
                         self.provider.rows[recovered['order_id']]['transaction_id'] + '/qr-code')

    def test_expire_deny_cancel_are_applied(self):
        for booth, state, target in [('PB002', 'expire', 'EXPIRED'), ('PB003', 'deny', 'FAILED'), ('PB004', 'cancel', 'CANCELLED')]:
            with self.subTest(state=state):
                order = self.backend.create_order(booth, {'template_a': 2}, self.key)
                self.provider.rows[order['order_id']].update(transaction_status=state, status_code='202')
                self.assertEqual(self.backend.status(order['order_id'], booth)['state'], target)

    def test_bad_evidence_cannot_unlock(self):
        self.paid()
        for field, value in [('gross_amount','1'),('currency','USD'),('payment_type','credit_card'),('merchant_id','OTHER'),('transaction_id','WRONG'),('fraud_status','challenge')]:
            with self.subTest(field=field):
                old = self.provider.rows[self.oid][field]
                self.provider.rows[self.oid][field] = value
                self.clock[0] += 4
                result = self.backend.status(self.oid, 'PB001')
                self.assertEqual(result['state'], 'PENDING')
                self.provider.rows[self.oid][field] = old

    def test_webhook_outage_is_retry_not_success(self):
        self.provider.outage = True
        with self.assertRaises(ProviderUnavailable): self.backend.process_notification(self.callback())
        self.assertEqual(self.store.db.execute('SELECT outcome FROM checkout_events').fetchone()[0], 'RETRY')

    def test_delayed_pending_callback_uses_latest_provider_state(self):
        self.paid()
        self.assertTrue(self.backend.process_notification(self.callback('pending')))
        self.assertEqual(self.backend.status(self.oid, 'PB001')['state'], 'PAID')

    def test_tampered_signature_never_calls_provider(self):
        data = self.callback(); data['signature_key'] = '0' * 128
        with self.assertRaises(ValueError): self.backend.process_notification(data)
        self.assertEqual(self.provider.reads, 0)

    def test_duplicate_settlement_and_claim_return_same_grant(self):
        self.paid()
        for _ in range(2): self.backend.process_notification(self.callback())
        a = self.backend.claim(self.oid, 'PB001', self.key)
        b = self.backend.claim(self.oid, 'PB001', self.key)
        self.assertEqual(a['grant_id'], b['grant_id'])

    def test_cancel_racing_payment_never_discards_paid(self):
        self.paid()
        with self.assertRaises(CheckoutConflict): self.backend.cancel(self.oid, 'PB001')
        self.assertEqual(self.backend.status(self.oid, 'PB001')['state'], 'PAID')

    def test_no_new_order_until_provider_cancel_confirmed(self):
        self.backend.cancel(self.oid, 'PB001')
        self.assertTrue(self.backend.create_order('PB001', {'template_a': 2}, 'b' * 32)['order_id'])

    def test_provider_qr_url_never_allows_external_host_or_port(self):
        for url in ['https://evil.test/qr','https://api.sandbox.midtrans.com:444/v2/qris/abc/qr-code']:
            from photobooth.qris_evidence import sandbox_qr_url
            with self.assertRaises(ValueError): sandbox_qr_url(url)

    def test_expiry_407_is_terminal_not_unknown(self):
        self.provider.rows[self.oid].update(transaction_status='expire', status_code='407')
        self.assertEqual(self.backend.status(self.oid, 'PB001')['state'], 'EXPIRED')

    def test_fraud_denial_is_failed_not_paid(self):
        self.provider.rows[self.oid].update(transaction_status='deny', status_code='202', fraud_status='deny')
        self.assertEqual(self.backend.status(self.oid, 'PB001')['state'], 'FAILED')

    def test_successful_status_request_does_not_mean_paid(self):
        self.provider.rows[self.oid].update(transaction_status='pending', status_code='200')
        self.assertEqual(self.backend.status(self.oid, 'PB001')['state'], 'PENDING')

    def test_expiry_code_cannot_authorize_settlement(self):
        self.provider.rows[self.oid].update(transaction_status='settlement', status_code='407')
        result = self.backend.status(self.oid, 'PB001')
        self.assertEqual(result['state'], 'PENDING')
        self.assertTrue(result['verification_pending'])


class PendingQrPollingTests(unittest.TestCase):
    """Real SQLite; charge supplies an image action that GET Status omits."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'orders.db'
        self.clock = [1000.0]
        self.store = CheckoutStore(self.path, now=lambda: self.clock[0])
        self.provider = FakeProvider()
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        self.key = 'a' * 32
        original_create = self.provider.create_qris
        def create(order_id, amount):
            data = original_create(order_id, amount)
            data['actions'] = [self.action(order_id)]
            return data
        self.provider.create_qris = create
        self.order = self.backend.create_order('PB001', {'template_a': 2}, self.key)
        self.oid = self.order['order_id']
        self.url = self.order['qr_url']

    @staticmethod
    def action(order_id):
        # The image reference need not equal the provider transaction ID.
        return {'name': 'generate-qr-code', 'method': 'GET',
                'url': 'https://api.sandbox.midtrans.com/v4/qris/image-' + order_id + '/qr-code'}

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def poll(self):
        self.clock[0] += 4
        return self.backend.status(self.oid, 'PB001')

    def test_repeated_missing_null_empty_or_unrelated_actions_keep_charge_image(self):
        for actions in (None, [], [{'name': 'unrelated'}]):
            self.provider.rows[self.oid]['actions'] = actions
            result = self.poll()
            self.assertEqual(result['qr_url'], self.url)
            self.assertFalse(result['verification_pending'])
            self.assertEqual(result['state'], 'PENDING')
            self.assertEqual(result['order_id'], self.oid)
            self.assertEqual(result['checkout_key'], self.key)
        del self.provider.rows[self.oid]['actions']
        self.assertEqual(self.poll()['qr_url'], self.url)
        self.assertEqual(self.provider.charges, 1)
        self.assertEqual(self.provider.reads, 4)

    def test_backend_restart_retains_the_same_durable_image(self):
        self.store.close()
        self.store = CheckoutStore(self.path, now=lambda: self.clock[0])
        self.backend = CheckoutBackend(self.store, self.provider, KEY, MERCHANT)
        result = self.backend.create_order('PB001', {'template_a': 2}, self.key)
        self.assertEqual(result['qr_url'], self.url)
        self.assertEqual(result['order_id'], self.oid)
        self.assertEqual(self.provider.charges, 1)

    def test_explicit_verified_replacement_is_retained_by_later_polls(self):
        action = self.action('replacement-image')
        self.provider.rows[self.oid]['actions'] = [action]
        self.assertEqual(self.poll()['qr_url'], action['url'])
        del self.provider.rows[self.oid]['actions']
        self.assertEqual(self.poll()['qr_url'], action['url'])

    def test_invalid_explicit_action_does_not_fall_back_to_cached_image(self):
        for change in ({'url': 'https://evil.test/qr'}, {'method': 'POST'}):
            with self.subTest(change=change):
                action = dict(self.action(self.oid), **change)
                self.provider.rows[self.oid]['actions'] = [action]
                result = self.poll()
                self.assertTrue(result['verification_pending'])
                self.assertEqual(self.store.get(self.oid)['qr_url'], self.url)
                self.assertEqual(result['state'], 'PENDING')
                self.assertIsNone(result['grant_id'])
        self.assertEqual(self.provider.charges, 1)

    def test_cached_image_url_is_revalidated_before_reuse(self):
        self.store.save_qr(self.oid, 'https://evil.test/qr')
        result = self.poll()
        self.assertTrue(result['verification_pending'])
        self.assertIsNone(result['grant_id'])
        self.assertEqual(self.provider.charges, 1)

    def test_terminal_provider_states_still_remove_the_public_qr(self):
        for status, code, state in (('expire', '407', 'EXPIRED'),
                                    ('settlement', '200', 'PAID')):
            with self.subTest(status=status):
                # A separate booth/order avoids changing a terminal order back.
                order = self.backend.create_order('PB-' + status, {'template_a': 2}, self.key)
                oid = order['order_id']
                self.provider.rows[oid].update(transaction_status=status, status_code=code)
                self.clock[0] += 4
                result = self.backend.status(oid, 'PB-' + status)
                self.assertEqual(result['state'], state)
                self.assertIsNone(result['qr_url'])
