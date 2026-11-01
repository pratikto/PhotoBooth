"""Private worker + real authenticated HTTP API + SQLite integration."""
from dataclasses import replace
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import numpy as np
from photobooth.catalog import get_templates
from photobooth.kiosk_v2.post_preview_checkout import PrivateCheckoutService
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_checkout_fixture import CheckoutFixture


class PrivateCheckoutWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = CheckoutFixture(Path(self.temp.name))
        self.addCleanup(self.fixture.close)
        self.service = self.fixture.service
        self.frame = np.zeros((32,48,3), dtype=np.uint8)

    def final(self):
        self.service.prepare()
        view = self.service.start(get_templates(), {'template_a':1})
        for _ in range(3):
            view = self.service.capture(self.frame, view['capture_slot'], view['revision'], view['retake'], view['generation'])
        self.service.compose()
        return self.service.next()

    def freeze(self):
        view = self.final()
        return self.service.freeze_checkout(view['revision'], view['amount'])

    def ready(self):
        view = self.freeze()
        self.service.ccp_visible(view['ccp_offer'])
        return self.service.begin_payment()

    def test_frozen_proof_creation_is_not_visible_and_cannot_begin_charge(self):
        view = self.freeze()
        self.assertEqual('claim_proof', view['phase'])
        with self.assertRaises(DraftHeld): self.service.begin_payment()
        with self.assertRaises(DraftHeld): self.service.edit()
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertIsNone(self.service.ledger.db.execute('SELECT offered_at FROM pp_ccp_credentials').fetchone()[0])

    def test_live_visible_proof_then_http_payment_preserves_exact_purchase(self):
        view = self.ready()
        self.assertEqual('payment_pending', view['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertIsNotNone(view['payment_qr'])
        self.assertNotIn('ccp_offer', view)
        self.assertNotIn('thumbnails', view)
        self.assertFalse(view['fulfillment_authorized'])
        order = view['payment']['attempts'][0]['provider_order_id']
        self.fixture.provider.state(order, 'settlement')
        paid = self.service.check_payment('connectivity')
        self.assertEqual('paid_hold', paid['phase'])
        self.assertTrue(paid['payment']['paid_verified'])
        self.assertFalse(paid['fulfillment_authorized'])
        self.assertNotIn('payment_qr', paid)

    def test_lost_http_response_cannot_downgrade_already_verified_paid_obligation(self):
        view = self.ready()
        self.fixture.provider.state(view['payment']['attempts'][0]['provider_order_id'], 'settlement')
        paid = self.service.check_payment('connectivity')
        self.fixture.session.lose_response = True
        held = self.service.check_payment('connectivity')
        self.assertEqual('paid_hold', held['phase'])
        self.assertEqual(paid['payment']['entitlement_id'], held['payment']['entitlement_id'])
        self.assertEqual('OWED', held['payment']['obligation_state'])

    def test_lost_http_response_recovers_same_original_without_create_replay(self):
        view = self.freeze(); self.service.ccp_visible(view['ccp_offer'])
        self.fixture.session.lose_response = True
        self.assertEqual('payment_hold', self.service.begin_payment()['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual('payment_pending', self.service.check_payment('restart')['phase'])
        self.assertEqual(1, self.fixture.provider.charges)

    def test_failed_readiness_prevents_freeze_and_server_rechecks_before_charge(self):
        view = self.final()
        self.fixture.ready = replace(self.fixture.ready, drive_sharing=False)
        with self.assertRaises(DraftHeld): self.service.freeze_checkout(view['revision'], view['amount'])
        self.assertEqual('OPEN', self.service.ledger.inspect(self.service.lease)['state'])
        self.fixture.ready = replace(self.fixture.ready, drive_sharing=True)
        view = self.service.freeze_checkout(view['revision'], view['amount'])
        self.service.ccp_visible(view['ccp_offer'])
        self.fixture.ready = replace(self.fixture.ready, unclaimed_ready_capacity=0)
        self.assertEqual('payment_hold', self.service.begin_payment()['phase'])
        self.assertEqual(0, self.fixture.provider.charges)

    def test_qr_render_failure_does_not_create_a_new_attempt(self):
        self.service.qr_loader = lambda _: (_ for _ in ()).throw(ValueError('synthetic image failure'))
        view = self.ready()
        self.assertIsNone(view['payment_qr'])
        self.service.check_payment('connectivity')
        self.assertEqual(1, self.fixture.provider.charges)

    def test_reoffer_after_render_failure_keeps_original_proof_and_expiry(self):
        original = self.final()
        with patch('photobooth.kiosk_v2.post_preview_checkout.render_private_ccp', side_effect=ValueError('synthetic decoder failure')):
            with self.assertRaises(ValueError): self.service.freeze_checkout(original['revision'], original['amount'])
        before = dict(self.service.ledger.db.execute('SELECT * FROM pp_ccp_credentials').fetchone())
        view = self.service.offer_claim()
        after = dict(self.service.ledger.db.execute('SELECT * FROM pp_ccp_credentials').fetchone())
        self.assertEqual(before, after)
        self.assertEqual('claim_proof', view['phase'])
        self.assertEqual(0, self.fixture.provider.charges)

    def test_late_paid_http_after_hide_cannot_restore_private_pixels(self):
        view = self.ready()
        self.fixture.provider.state(view['payment']['attempts'][0]['provider_order_id'], 'settlement')
        entered, release = threading.Event(), threading.Event()
        original = self.fixture.provider.get_status
        def blocked(order):
            entered.set(); release.wait(3)
            return original(order)
        results = []
        with patch.object(self.fixture.provider, 'get_status', side_effect=blocked):
            thread = threading.Thread(target=lambda: results.append(self.service.check_payment('connectivity')))
            thread.start()
            self.assertTrue(entered.wait(3))
            started = time.monotonic(); self.service.hide_private()
            self.assertLess(time.monotonic()-started, .1)
            self.assertEqual({'phase':'hold'}, self.service.snapshot())
            release.set(); thread.join(5)
        self.assertEqual([{'phase':'hold'}], results)
        self.service.retire('APP_SUSPENDED')
        owed = self.fixture.backend.inspect(self.service.group, 'PB001')
        self.assertEqual('PAID_UNCLAIMED', owed['state'])
        self.assertEqual('OWED', owed['obligation_state'])
        self.assertEqual(0, self.fixture.provider.cancels)

    def test_cancel_and_suspend_have_different_original_financial_effects(self):
        self.ready()
        self.service.hide_private()
        self.assertEqual({'phase':'hold'}, self.service.retire('USER_CANCEL'))
        self.assertEqual(1, self.fixture.provider.cancels)
        row = self.service.ledger.db.execute('SELECT closed,lifecycle FROM pp_drafts').fetchone()
        self.assertEqual((0,'USER_CANCEL'), tuple(row))

    def test_incomplete_fixture_rejects_sandbox_or_implicit_activation(self):
        options = dict(payment_client=self.fixture.client, protector=self.fixture.protector,
                       merchant_id='MTEST', readiness=lambda:self.fixture.ready, qr_loader=lambda _:None)
        with self.assertRaises(DraftHeld): PrivateCheckoutService(Path(self.temp.name)/'other', **options)
        with patch.object(self.fixture.client._transport, 'expected_mode', 'sandbox'):
            with self.assertRaises(DraftHeld):
                PrivateCheckoutService(Path(self.temp.name)/'other', allow_incomplete_fixture=True, **options)
