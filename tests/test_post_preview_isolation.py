"""PP-06 mock-only privacy fencing never resets a financial/print obligation."""
import threading
import unittest
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


if __name__=='__main__':unittest.main()
