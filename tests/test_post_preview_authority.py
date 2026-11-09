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


    def test_private_process_bridge_keeps_original_worker_and_backend_authorities(self):
        import socket
        from types import SimpleNamespace
        from photobooth.post_preview_authority import authenticated_charge_request
        from photobooth.post_preview_readiness import LocalChargeReadiness, ReadOnlyDriveReadiness
        from photobooth.post_preview_readiness_bridge import (
            BackendChargeReadiness, WorkerReadinessClient, WorkerReadinessServer)
        from photobooth.printer import PrinterConfig
        local = LocalChargeReadiness(self.service.checkout, self.service.templates,
            probes={'worker_ownership':self.fixture.authority}, camera=self.fixture.camera,
            printer_config=PrinterConfig(lan_host='synthetic-no-paper'),
            printer_dial=lambda *args: SimpleNamespace(close=lambda:None))
        backend, worker = socket.socketpair()
        server = WorkerReadinessServer.from_original_worker(worker, local)
        client = WorkerReadinessClient(backend, timeout=2)
        self.addCleanup(server.stop)
        self.addCleanup(client.close)
        server.start()
        self.fixture.backend.readiness = BackendChargeReadiness(
            self.service.checkout, self.service.templates, client,
            drive_probe=ReadOnlyDriveReadiness(self.fixture.drive, self.fixture.workspace,
                                             now=self.service.ledger.now))
        # The worker channel cannot substitute for authenticated backend scope.
        with self.assertRaises(DraftHeld): self.fixture.backend.begin(self.service.lease)
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertEqual('payment_pending', self.service.begin_payment()['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        # A later capture worker is not a valid original charge owner, even
        # though payment authorization and Drive are independently healthy.
        self.fixture.jobs.busy = True
        self.fixture.jobs.current_action = 'capture'
        try:
            with authenticated_charge_request(self.scope, self.service.ledger.now()):
                report = self.fixture.backend.readiness(self.service.group)
            with self.assertRaises(DraftHeld):
                report.require(self.scope, now=self.service.ledger.now())
        finally:
            self.fixture.jobs.busy = False
            self.fixture.jobs.current_action = None
        self.assertEqual(1, self.fixture.provider.charges)


class HandoffChargeAuthorityTests(unittest.TestCase):
    """PP-063/064: actual second checkout after exact original isolation ACK."""
    final=worker_fixtures.PrivateCheckoutWorkerTests.final
    freeze=worker_fixtures.PrivateCheckoutWorkerTests.freeze
    ready=worker_fixtures.PrivateCheckoutWorkerTests.ready

    def setUp(self):
        import numpy as np
        from photobooth.post_preview_isolation import OriginalMockIsolation
        self.temp=TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.fixture=CheckoutFixture(Path(self.temp.name))
        self.addCleanup(self.fixture.close)
        self.fixture.enable_paid_ticket()
        self.service=self.fixture.service
        self.frame=np.zeros((32,48,3),dtype=np.uint8)
        self.isolation=OriginalMockIsolation(
            self.service.ledger,self.fixture.backend,self.fixture.jobs,
            self.fixture.launch_lease,printer_lane=self.service._receipt_lane,
            allow_incomplete_fixture=True)

    def next_checkout(self, *, paid):
        first=self.ready()
        old=self.service.lease
        group=self.service.group
        if paid:
            order=first['payment']['attempts'][0]['provider_order_id']
            self.fixture.provider.state(order,'settlement')
            self.service.check_payment('connectivity')
            offer=self.service.prepare_ticket()['ticket_offer']
            self.service.ticket_visible(offer)
            self.service.ticket_send_receipt()
            self.service.ticket_dismiss()
        self.service.retire('APP_SUSPENDED' if paid else 'USER_CANCEL')
        op=self.isolation.prepare('PB001')
        self.isolation.acknowledge('PB001',op)
        self.service.reset_after_acked_isolation(op)
        original=dict(self.fixture.backend.inspect(group,'PB001'))
        view=self.freeze()
        self.service.ccp_visible(view['ccp_offer'])
        contract=self.service.ledger.db.execute(
            'SELECT contract_sha256 FROM pp_checkout_intents WHERE purchase_group_id=?',
            (self.service.group,)).fetchone()[0]
        scope=ReadinessScope(self.service.group,'PB001',contract,self.service.lease.generation)
        self.assertNotEqual(old.draft_id,self.service.lease.draft_id)
        return old,group,op,scope,original

    def test_B_can_pay_after_paid_A_is_safely_acked_without_erasing_A_owed(self):
        old,group,op,scope,original=self.next_checkout(paid=True)
        before=self.service.ledger.db.total_changes
        self.assertEqual('READY',self.fixture.authority(scope).state)
        self.assertEqual(before,self.service.ledger.db.total_changes)
        second=self.service.begin_payment()
        self.assertEqual('payment_pending',second['phase'])
        self.assertEqual(2,self.fixture.provider.charges)
        self.assertEqual(original,self.fixture.backend.inspect(group,'PB001'))
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services WHERE purchase_group_id=?',(group,)).fetchone()[0])
        self.assertEqual(1,len(self.fixture.receipt_sizes))
        self.assertEqual(1,self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_isolation_ops WHERE operation_id=? AND state='ACKED'",(op,)
        ).fetchone()[0])
        with self.assertRaises(DraftHeld):self.service.ledger.inspect(old)

    def test_B_can_pay_after_verified_cancelled_A_is_safely_acked(self):
        old,group,op,scope,original=self.next_checkout(paid=False)
        self.assertEqual('NONE',original['obligation_state'])
        self.assertEqual('READY',self.fixture.authority(scope).state)
        self.assertEqual('payment_pending',self.service.begin_payment()['phase'])
        self.assertEqual(2,self.fixture.provider.charges)
        self.assertEqual(original,self.fixture.backend.inspect(group,'PB001'))
        self.assertEqual([],self.fixture.receipt_sizes)

    def test_generation_mismatch_after_old_ack_still_blocks_B_charge(self):
        old,group,op,scope,original=self.next_checkout(paid=True)
        with self.service.ledger.write():
            self.service.ledger.db.execute(
                'UPDATE pp_drafts SET generation=generation+1 WHERE draft_id=?',(old.draft_id,))
        self.assertEqual('NOT_READY',self.fixture.authority(scope).state)
        self.assertEqual('payment_hold',self.service.begin_payment()['phase'])
        self.assertEqual(1,self.fixture.provider.charges)

    def test_ack_without_completion_timestamp_is_not_a_safe_prior_release(self):
        old,group,op,scope,original=self.next_checkout(paid=True)
        with self.service.ledger.write():
            self.service.ledger.db.execute(
                'UPDATE pp_isolation_ops SET acknowledged_at=NULL WHERE operation_id=?',(op,))
        self.assertEqual('NOT_READY',self.fixture.authority(scope).state)
        self.assertEqual('payment_hold',self.service.begin_payment()['phase'])
        self.assertEqual(1,self.fixture.provider.charges)

    def test_financial_conflict_after_ack_still_blocks_B_charge(self):
        old,group,op,scope,original=self.next_checkout(paid=True)
        with self.service.ledger.write():
            self.service.ledger.db.execute(
                'UPDATE pp_purchase_finance SET review_required=1 WHERE purchase_group_id=?',(group,))
        self.assertEqual('NOT_READY',self.fixture.authority(scope).state)
        self.assertEqual('payment_hold',self.service.begin_payment()['phase'])
        self.assertEqual(1,self.fixture.provider.charges)

    def test_missing_exact_ack_still_blocks_B_charge(self):
        old,group,op,scope,original=self.next_checkout(paid=True)
        with self.service.ledger.write():
            self.service.ledger.db.execute(
                'DELETE FROM pp_isolation_ops WHERE operation_id=?',(op,))
        self.assertEqual('NOT_READY',self.fixture.authority(scope).state)
        self.assertEqual('payment_hold',self.service.begin_payment()['phase'])
        self.assertEqual(1,self.fixture.provider.charges)

    def test_future_ack_timestamp_still_blocks_B_charge(self):
        old,group,op,scope,original=self.next_checkout(paid=True)
        with self.service.ledger.write():
            self.service.ledger.db.execute(
                'UPDATE pp_isolation_ops SET acknowledged_at=? WHERE operation_id=?',
                (self.service.ledger.now()+3600,op))
        self.assertEqual('NOT_READY',self.fixture.authority(scope).state)
        self.assertEqual('payment_hold',self.service.begin_payment()['phase'])
        self.assertEqual(1,self.fixture.provider.charges)


if __name__ == '__main__': unittest.main()
