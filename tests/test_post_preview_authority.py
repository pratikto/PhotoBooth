"""Trusted request/worker readiness, never customer-supplied ready flags."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from photobooth.post_preview_authority import authenticated_payment_readiness
from photobooth.post_preview_readiness import ReadinessScope
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests import test_post_preview_checkout_worker as worker_fixtures


class OriginalAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.fixture = CheckoutFixture(Path(self.temp.name))
        self.addCleanup(self.fixture.close)
        worker = worker_fixtures.PrivateCheckoutWorkerTests()
        worker.fixture, worker.service = self.fixture, self.fixture.service
        import numpy as np
        worker.frame = np.zeros((32,48,3), dtype=np.uint8)
        view = worker.freeze()
        self.service = worker.service
        self.service.ccp_visible(view['ccp_offer'])
        self.scope = ReadinessScope(self.service.group, 'PB001',
            self.service.ledger.db.execute('SELECT contract_sha256 FROM pp_checkout_intents').fetchone()[0],
            self.service.lease.generation)

    def test_authenticated_route_is_observed_but_direct_call_has_no_request_authority(self):
        self.assertEqual('UNKNOWN', authenticated_payment_readiness(self.scope).state)
        with self.assertRaises(DraftHeld): self.fixture.backend.begin(self.service.lease)
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertEqual('payment_pending', self.service.begin_payment()['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual('UNKNOWN', authenticated_payment_readiness(self.scope).state)

    def test_wrong_worker_generation_other_customer_and_missing_owner_hold(self):
        probe = self.fixture.authority
        self.assertEqual('READY', probe(self.scope).state)
        self.assertEqual('NOT_READY', probe(replace(self.scope, generation=2)).state)
        self.assertEqual('NOT_READY', probe(replace(self.scope, booth_id='PB002')).state)
        probe.jobs = None
        self.assertEqual('UNKNOWN', probe(self.scope).state)
        self.assertEqual('payment_hold', self.service.begin_payment()['phase'])
        self.assertEqual(0, self.fixture.provider.charges)

    def test_capture_worker_or_retired_launch_cannot_admit_charge(self):
        self.fixture.authority.jobs.busy = True
        self.fixture.authority.jobs.current_action = 'capture'
        self.assertEqual('NOT_READY', self.fixture.authority(self.scope).state)
        self.fixture.authority.jobs.busy = False
        self.fixture.launch_lease.close()
        self.assertEqual('NOT_READY', self.fixture.authority(self.scope).state)
        self.assertEqual(0, self.fixture.provider.charges)

    def test_unresolved_legacy_purchase_is_not_a_free_booth(self):
        from photobooth.payment_quote import quote_checkout
        quote = quote_checkout({'template_a':1})
        self.fixture.legacy.begin('PB001', {'template_a':1}, quote.total_amount, 'legacy-original-fixture')
        before = self.fixture.legacy.db.total_changes
        self.assertEqual('NOT_READY', self.fixture.authority(self.scope).state)
        self.assertEqual('payment_hold', self.service.begin_payment()['phase'])
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertEqual(before, self.fixture.legacy.db.total_changes)

    def test_missing_legacy_journal_or_privacy_retirement_never_claims_ready(self):
        legacy = self.fixture.authority.legacy
        self.fixture.authority.legacy = None
        self.assertEqual('UNKNOWN', self.fixture.authority(self.scope).state)
        self.fixture.authority.legacy = legacy
        self.service.hide_private()
        self.assertEqual('NOT_READY', self.fixture.authority(self.scope).state)

    def test_original_async_mailbox_is_checked_fresh_without_opening_another_camera(self):
        from photobooth.kiosk_v2.devices import AsyncCamera
        from unittest.mock import Mock
        clock = [10.0]
        factory = Mock(side_effect=AssertionError('No camera open during readiness'))
        camera = AsyncCamera(factory=factory, clock=lambda: clock[0])
        camera._frame, camera._stamp, camera._state = object(), 10.0, 'ready'
        self.fixture.camera = camera
        clock[0] = 13.0
        self.assertEqual('payment_hold', self.service.begin_payment()['phase'])
        self.assertEqual(0, self.fixture.provider.charges)
        camera._stamp = 13.0
        self.assertEqual('payment_pending', self.service.begin_payment()['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        factory.assert_not_called()
        self.assertIsNone(camera._thread)

    def test_request_authority_is_retired_even_when_readiness_fails(self):
        def fail(group):
            self.assertEqual('READY', authenticated_payment_readiness(self.scope).state)
            raise OSError('synthetic unavailable check')
        self.fixture.backend.readiness = fail
        self.assertEqual('payment_hold', self.service.begin_payment()['phase'])
        self.assertEqual('UNKNOWN', authenticated_payment_readiness(self.scope).state)
        self.assertEqual(0, self.fixture.provider.charges)


if __name__ == '__main__': unittest.main()
