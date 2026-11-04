"""PP-06 mock-only privacy fencing never resets a financial/print obligation."""
import threading
import unittest
from unittest.mock import patch
import numpy as np
from pathlib import Path
import tempfile

from photobooth.catalog import get_templates
from photobooth.post_preview_store import PostPreviewStore,DraftHeld
from photobooth.post_preview_isolation import OriginalMockIsolation
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests.test_post_preview_checkout_worker import PrivateCheckoutWorkerTests


class OriginalMockIsolationTests(unittest.TestCase):
    final=PrivateCheckoutWorkerTests.final
    freeze=PrivateCheckoutWorkerTests.freeze
    ready=PrivateCheckoutWorkerTests.ready

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture=CheckoutFixture(Path(self.temp.name))
        self.addCleanup(self.fixture.close)
        self.service=self.fixture.service
        self.frame=np.zeros((32,48,3),dtype=np.uint8)
        self.lane=threading.Lock()
        self.iso=OriginalMockIsolation(
            self.service.ledger,self.fixture.backend,self.fixture.jobs,
            self.fixture.launch_lease,printer_lane=self.lane,
            allow_incomplete_fixture=True)

    def test_unpaid_retired_customer_needs_two_phase_ack_before_new_visit(self):
        self.service.prepare()
        self.service.start(get_templates(),{'template_a':1})
        self.service.retire('APP_SUSPENDED')
        key=self.iso.prepare('PB001')
        with self.assertRaises(DraftHeld):
            self.service.ledger.create('PB001','visitorB',{'template_a':1})
        self.assertTrue(self.iso.acknowledge('PB001',key))
        self.assertFalse(self.iso.acknowledge('PB001',key))
        new=self.service.ledger.create('PB001','visitorB',{'template_a':1})
        self.assertNotEqual(new.draft_id,self.service.lease.draft_id)
        self.assertEqual('ACKED',self.service.ledger.db.execute(
            'SELECT state FROM pp_isolation_ops').fetchone()[0])

    def test_pending_payment_blocks_isolation_even_after_privacy_retirement(self):
        self.fixture.enable_paid_ticket()
        self.ready()
        self.service.retire('APP_SUSPENDED')
        with self.assertRaises(DraftHeld):
            self.iso.prepare('PB001')
        self.assertEqual(0,self.service.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_paid_unclaimed_preserves_owed_and_original_ccp(self):
        self.fixture.enable_paid_ticket()
        v=self.ready()
        self.fixture.provider.state(v['payment']['attempts'][0]['provider_order_id'],'settlement')
        self.service.check_payment('connectivity')
        self.fixture.ticket.prepare(self.service.lease)
        ccp=self.service.ledger.db.execute('SELECT verifier,offered_at FROM pp_ccp_credentials').fetchone()
        self.service.retire('APP_SUSPENDED')
        key=self.iso.prepare('PB001')
        self.assertTrue(self.iso.acknowledge('PB001',key))
        self.assertEqual('OWED',self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual(ccp, self.service.ledger.db.execute(
            'SELECT verifier,offered_at FROM pp_ccp_credentials').fetchone())
        self.assertEqual(1,self.fixture.provider.charges)

    def test_printer_lane_blocks_release_and_prepared_receipt_cannot_bypass(self):
        self.service.prepare()
        self.service.start(get_templates(),{'template_a':1})
        self.service.retire('APP_SUSPENDED')
        self.assertTrue(self.lane.acquire(False))
        try:
            with self.assertRaises(DraftHeld):self.iso.prepare('PB001')
        finally:
            self.lane.release()
        key=self.iso.prepare('PB001')
        self.lane.acquire()
        try:
            with self.assertRaises(DraftHeld):self.iso.acknowledge('PB001',key)
        finally:self.lane.release()
        self.assertEqual(0,self.service.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_photo_job_inflight_never_releases(self):
        self.service.prepare()
        self.service.start(get_templates(),{'template_a':1})
        self.service.retire('APP_SUSPENDED')
        self.fixture.jobs.busy=True
        try:
            with self.assertRaises(DraftHeld):self.iso.prepare('PB001')
        finally:self.fixture.jobs.busy=False
        self.assertEqual(0,self.service.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])


    def test_acked_isolation_allows_next_visitor_without_reopening_old_media(self):
        self.fixture.enable_paid_ticket()
        self.service.prepare()
        first=self.service.start(get_templates(),{'template_a':1})
        old=self.service.lease
        stale_gen=first['generation']
        self.service.retire('APP_SUSPENDED')
        self.iso=OriginalMockIsolation(
            self.service.ledger,self.fixture.backend,self.fixture.jobs,self.fixture.launch_lease,
            printer_lane=self.service._receipt_lane,allow_incomplete_fixture=True)
        op=self.iso.prepare('PB001')
        with self.assertRaises(DraftHeld):
            self.service.reset_after_acked_isolation(op)
        self.assertTrue(self.iso.acknowledge('PB001',op))
        row=self.service.ledger.db.execute(
            'SELECT original_generation FROM pp_isolation_ops WHERE operation_id=?',
            (op,)).fetchone()
        self.assertEqual(old.generation+1,row[0])
        new_idle=self.service.reset_after_acked_isolation(op)
        self.assertEqual('confirm',new_idle['phase'])
        self.assertFalse(self.service._hidden.is_set())
        self.assertIsNone(self.service.lease)
        with self.assertRaises(DraftHeld):
            self.service.reset_after_acked_isolation(op)
        next_view=self.service.start(get_templates(),{'template_a':1})
        self.assertNotEqual(old.draft_id,self.service.lease.draft_id)
        self.assertGreater(next_view['generation'],stale_gen)
        with self.assertRaises(DraftHeld):
            self.service.ledger.inspect(old)
        self.assertEqual('ISOLATED',self.service.ledger.db.execute(
            'SELECT lifecycle FROM pp_drafts WHERE draft_id=?',(old.draft_id,)).fetchone()[0])

    def test_reuse_rejects_forged_or_unacknowledged_isolation(self):
        self.fixture.enable_paid_ticket()
        self.service.prepare()
        self.service.start(get_templates(),{'template_a':1})
        self.service.retire('APP_SUSPENDED')
        self.iso=OriginalMockIsolation(
            self.service.ledger,self.fixture.backend,self.fixture.jobs,self.fixture.launch_lease,
            printer_lane=self.service._receipt_lane,allow_incomplete_fixture=True)
        op=self.iso.prepare('PB001')
        for key in ('f'*32,op):
            with self.assertRaises(DraftHeld):
                self.service.reset_after_acked_isolation(key)
        self.assertTrue(self.service._hidden.is_set())
        self.assertIsNotNone(self.service.lease)

    def drive_isolation(self):
        self.fixture.enable_paid_ticket()
        self.fixture.enable_paid_delivery(real_drive=True)
        self.service.prepare()
        self.service.start(get_templates(),{'template_a':1})
        self.service.retire('APP_SUSPENDED')
        self.iso=OriginalMockIsolation(
            self.service.ledger,self.fixture.backend,self.fixture.jobs,
            self.fixture.launch_lease,printer_lane=self.service._receipt_lane,
            delivery=self.fixture.paid_monitor,allow_incomplete_fixture=True)
        worker=self.fixture.paid_monitor.worker
        def close_worker():
            worker.stop()
            if worker._thread.ident is not None:worker._thread.join(5)
            self.assertFalse(worker._thread.is_alive())
        self.addCleanup(close_worker)
        return worker

    def test_idle_live_Drive_worker_does_not_require_shutdown_to_ack_isolation(self):
        worker=self.drive_isolation()
        idle=threading.Event()
        original_wait=worker._wake.wait
        def waiting(timeout):
            idle.set()
            return original_wait(timeout)
        with patch.object(worker,'_maintain_reserves',return_value=None), \
                patch.object(worker._wake,'wait',side_effect=waiting):
            worker.start()
            self.assertTrue(idle.wait(3))
            self.assertTrue(worker._thread.is_alive())
            operation=self.iso.prepare('PB001')
            self.assertTrue(self.iso.acknowledge('PB001',operation))
            self.assertFalse(self.iso.acknowledge('PB001',operation))
            self.assertTrue(worker._thread.is_alive())
            self.assertFalse(worker._stop.is_set())
            self.assertEqual('ISOLATED',self.service.ledger.db.execute(
                'SELECT lifecycle FROM pp_drafts').fetchone()[0])
            worker.stop();worker._thread.join(3)

    def test_active_Drive_request_between_prepare_and_ack_still_blocks_release(self):
        worker=self.drive_isolation()
        idle,entered,release=threading.Event(),threading.Event(),threading.Event()
        active=[False]
        original_wait=worker._wake.wait
        def waiting(timeout):
            idle.set()
            return original_wait(timeout)
        def request():
            if active[0]:
                entered.set()
                if not release.wait(5):raise AssertionError('Synthetic request was not released')
        with patch.object(worker,'_maintain_reserves',side_effect=request), \
                patch.object(worker._wake,'wait',side_effect=waiting):
            worker.start()
            try:
                self.assertTrue(idle.wait(3))
                operation=self.iso.prepare('PB001')
                idle.clear();active[0]=True;worker.kick()
                self.assertTrue(entered.wait(3))
                with self.assertRaises(DraftHeld):self.iso.prepare('PB001')
                with self.assertRaises(DraftHeld):self.iso.acknowledge('PB001',operation)
                self.assertEqual('PREPARED',self.service.ledger.db.execute(
                    'SELECT state FROM pp_isolation_ops').fetchone()[0])
                self.assertEqual(0,self.service.ledger.db.execute(
                    'SELECT closed FROM pp_drafts').fetchone()[0])
                active[0]=False;release.set()
                self.assertTrue(idle.wait(3))
                self.assertTrue(self.iso.acknowledge('PB001',operation))
                self.assertTrue(worker._thread.is_alive())
                self.assertEqual(0,self.fixture.provider.charges)
                self.assertEqual([],self.fixture.receipt_sizes)
            finally:
                release.set();worker.stop();worker._thread.join(3)

    def test_Drive_fence_releases_on_financial_hold_without_stopping_retry_worker(self):
        worker=self.drive_isolation()
        idle=threading.Event()
        original_wait=worker._wake.wait
        def waiting(timeout):
            idle.set()
            return original_wait(timeout)
        with patch.object(worker,'_maintain_reserves',return_value=None), \
                patch.object(worker._wake,'wait',side_effect=waiting), \
                patch.object(self.iso,'_financial',side_effect=DraftHeld('Synthetic finance HOLD')):
            worker.start()
            try:
                self.assertTrue(idle.wait(3))
                with self.assertRaisesRegex(DraftHeld,'Synthetic finance HOLD'):
                    self.iso.prepare('PB001')
                self.assertEqual(0,self.service.ledger.db.execute(
                    'SELECT count(*) FROM pp_isolation_ops').fetchone()[0])
                self.assertEqual(0,self.service.ledger.db.execute(
                    'SELECT closed FROM pp_drafts').fetchone()[0])
                idle.clear();worker.kick()
                self.assertTrue(idle.wait(3))
                self.assertTrue(worker._thread.is_alive())
                self.assertFalse(worker._stop.is_set())
            finally:
                worker.stop();worker._thread.join(3)


if __name__=='__main__':unittest.main()
