"""Trusted original manager behind bounded async UI control; external I/O fake."""
import threading
import time
import unittest
from unittest.mock import patch
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_visit_control import VisitControl,TrustedVisitWorker,VisitControlOutcome,create_visit_control
from tests import test_post_preview_sandbox_visits as fixtures

class VisitControlTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.OriginalSandboxVisitTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.visits=self.fixture.visits
        self.control,self.worker=create_visit_control(self.visits)
        self.addCleanup(self.shutdown)
        self.assertTrue(self.control.start())
        self.assertEqual('READY',self.outcome().state)
    def shutdown(self):
        self.assertTrue(self.worker.stop(timeout=12),'Original trusted worker did not stop')
    def outcome(self):
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            result=self.control.poll()
            if result is not None:return result
            time.sleep(.02)
        self.fail('No bounded original control result')
    def idle(self):
        deadline=time.monotonic()+15
        while self.control.busy and time.monotonic()<deadline:time.sleep(.02)
        self.assertFalse(self.control.busy)
    def ready(self):
        self.assertTrue(self.control.ready());return self.outcome()
    def test_public_control_has_only_original_binding_and_no_private_manager_thread_or_keys(self):
        self.assertIs(self.control.binding,self.fixture.binding)
        values=vars(self.control).values()
        self.assertFalse(any(value is self.visits or value is self.worker or
            value is self.visits._config or isinstance(value,threading.Thread) for value in values))
        self.assertFalse(self.fixture.config.server_key in repr(vars(self.control)))
        self.assertEqual('READY',self.ready().state)
    def test_blocked_ready_does_not_block_privacy_or_publish_late_binding(self):
        entered,release=threading.Event(),threading.Event();original=self.visits.ensure_new_visitor_ready
        def held():entered.set();release.wait(5);return original()
        old=self.control.binding
        with patch.object(self.visits,'ensure_new_visitor_ready',side_effect=held):
            self.assertTrue(self.control.ready())
            try:
                self.assertTrue(entered.wait(2));started=time.monotonic()
                self.control.hide_private('APP_SUSPENDED')
                self.assertLess(time.monotonic()-started,.2)
                self.assertEqual({'phase':'hold'},old.service.snapshot())
                self.assertTrue(self.control.busy);self.assertFalse(self.control.ready())
            finally:release.set()
        self.idle();self.assertIsNone(self.control.poll())
        result=self.ready();self.assertEqual('READY',result.state)
        self.assertGreater(result.binding.epoch,old.epoch)
        self.assertEqual(0,self.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
    def test_forged_queue_record_cannot_complete_a_live_original_request(self):
        entered,release=threading.Event(),threading.Event();original=self.visits.ensure_new_visitor_ready
        def held():entered.set();release.wait(5);return original()
        with patch.object(self.visits,'ensure_new_visitor_ready',side_effect=held):
            self.assertTrue(self.control.ready())
            try:
                self.assertTrue(entered.wait(2))
                request=self.control._pending
                self.control._results.put_nowait(VisitControlOutcome(request[0],request[1],'ready','READY',self.control.binding))
                self.assertIsNone(self.control.poll());self.assertTrue(self.control.busy)
            finally:release.set()
        self.assertEqual('READY',self.outcome().state)
    def test_stop_true_flag_cannot_replace_actual_original_shutdown(self):
        with patch.object(self.visits,'stop',return_value=True):
            self.assertFalse(self.worker.stop(timeout=.1))
            self.assertFalse(self.control.stopped)
            with self.assertRaises(OSError):LaunchLease(self.fixture.config.private_root)
        self.assertTrue(self.worker.stop(timeout=12));self.assertTrue(self.control.stopped)

    def test_repeated_privacy_after_shutdown_starts_cannot_block_actual_drain(self):
        entered=threading.Event()
        def held():entered.set();return False
        with patch.object(self.visits,'_close_handles',side_effect=held):
            self.assertFalse(self.worker.stop(timeout=.2))
            self.assertTrue(entered.wait(2));self.assertTrue(self.visits._stopping)
            self.control.hide_private('APP_SUSPENDED')
            self.assertFalse(self.control.stopped)
            with self.assertRaises(OSError):LaunchLease(self.fixture.config.private_root)
        self.assertTrue(self.worker.stop(timeout=12))
        self.assertFalse(self.control.busy)

    def test_first_privacy_reason_survives_repeated_minimize_and_cancel(self):
        self.fixture.paid(self.control.binding)
        entered,release=threading.Event(),threading.Event()
        original=self.visits.retire_current
        def held(event):entered.set();release.wait(5);return original(event)
        with patch.object(self.visits,'retire_current',side_effect=held):
            self.control.hide_private('APP_SUSPENDED')
            try:
                self.assertTrue(entered.wait(2))
                self.control.hide_private('USER_CANCEL')
            finally:release.set()
            self.idle()
        self.assertEqual('APP_SUSPENDED',self.visits.ledger.db.execute(
            'SELECT lifecycle FROM pp_drafts').fetchone()[0])

    def test_private_exception_is_static_denial_without_proof_or_snapshot(self):
        proof='MEONG:CCP:1:PB001:'+('a'*32)+':'+('b'*43)
        with patch.object(self.visits,'recover_paid',side_effect=PermissionError(proof)):
            self.assertTrue(self.control.claim(proof))
            result=self.outcome()
        self.assertEqual('DENIED',result.state)
        self.assertIsNone(result.snapshot);self.assertIsNone(result.binding)
        self.assertNotIn(proof,repr(vars(self.control)))

    def test_stop_before_queued_claim_runs_drops_transient_proof_command(self):
        self.assertTrue(self.worker.stop(timeout=12))
        visits=self.fixture.manager()
        self.addCleanup(self.fixture.shutdown,visits)
        control=VisitControl();worker=TrustedVisitWorker(visits,control)
        proof='MEONG:CCP:1:PB001:'+('a'*32)+':'+('b'*43)
        self.assertTrue(control.claim(proof))
        control.request_stop();worker.start()
        try:
            self.assertTrue(worker.stop(timeout=12))
            self.assertTrue(control._commands.empty())
            self.assertFalse(control.busy)
        finally:self.assertTrue(worker.stop(timeout=12))
    def test_late_committed_claim_is_hidden_then_retired_without_public_private_result(self):
        group,proof=self.fixture.paid(self.control.binding)
        self.control.hide_private('RESULT_TIMEOUT');self.idle()
        self.assertEqual('READY',self.ready().state)
        service=self.control.binding.service
        entered,release=threading.Event(),threading.Event();original=service._handoff.claim
        def held(*args):
            grant=original(*args);entered.set();release.wait(5);return grant
        with patch.object(service._handoff,'claim',side_effect=held):
            self.assertTrue(self.control.claim(proof))
            try:
                self.assertTrue(entered.wait(12));self.control.hide_private('APP_SUSPENDED')
            finally:release.set()
        self.idle();self.assertIsNone(self.control.poll())
        self.assertEqual({'phase':'hold'},service.snapshot())
        self.assertFalse(proof in repr(vars(self.control)))
        self.assertEqual(('APP_SUSPENDED',5),tuple(service.ledger.db.execute('SELECT lifecycle,generation FROM pp_drafts').fetchone()))
        self.assertEqual('READY',self.ready().state)
        self.assertEqual(1,self.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])

    def test_privacy_during_accepted_old_ledger_close_finishes_rotation_without_dead_handle(self):
        self.fixture.paid(self.control.binding);service=self.control.binding.service
        service.retire('RESULT_TIMEOUT')
        entered,release=threading.Event(),threading.Event();original=service.ledger.close
        def held():entered.set();release.wait(8);return original()
        try:
            with patch.object(service.ledger,'close',side_effect=held):
                self.assertTrue(self.control.ready())
                self.assertTrue(entered.wait(12))
                self.control.hide_private('APP_SUSPENDED')
                deadline=time.monotonic()+5
                while self.control._pending is not None and time.monotonic()<deadline:time.sleep(.02)
                self.assertIsNone(self.control._pending)
                release.set();service.wait_closed(8)
                self.idle()
            self.assertIsNone(self.control.poll())
            self.assertEqual('READY',self.ready().state)
        finally:
            release.set();service.wait_closed(8)
            # Always drain this isolated fixture if the regression fails.
            if self.control.busy:
                self.fixture.shutdown(self.visits)
