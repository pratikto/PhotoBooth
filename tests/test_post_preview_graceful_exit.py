"""Original trusted normal-exit ACK, same-root restart and uncertainty holds."""
from contextlib import contextmanager,closing
import hashlib
import sqlite3
import threading
import time
import unittest
from unittest.mock import patch

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_visit_control import create_visit_control
from tests import test_post_preview_sandbox_visits as fixtures


class ProtectedGracefulExitTests(unittest.TestCase):
    @contextmanager
    def fixture(self):
        f=fixtures.OriginalSandboxVisitTests(methodName='runTest');f.setUp()
        control,worker=create_visit_control(f.visits,finish_on_stop=True)
        try:
            self.assertTrue(control.start());deadline=time.monotonic()+12;result=None
            while result is None and time.monotonic()<deadline:
                result=control.poll();time.sleep(.01)
            self.assertIsNotNone(result);self.assertEqual('READY',result.state)
            yield f,control,worker
        finally:
            # Fault cases deliberately remain un-ACKed. Existing abrupt close
            # drains their real handles and preserves the held original rows;
            # it is NOT counted as a graceful release or restart acceptance.
            if not worker.stop(timeout=.1):f.shutdown(f.visits)
            self.assertTrue(worker.stop(timeout=12));f.doCleanups()

    def rows(self,f,query,args=()):
        with closing(sqlite3.connect((f.config.private_root/'drafts.sqlite3').as_uri()+'?mode=ro',uri=True)) as db:
            return db.execute(query,args).fetchall()

    def test_unpaid_original_raw_and_exact_receipt_survive_graceful_stop_and_same_root_restart(self):
        with self.fixture() as (f,control,worker):
            service=control.binding.service;service.start(get_templates(),{'template_a':1})
            view=service.snapshot();lease=service.lease
            service.capture(f.frame,view['capture_slot'],view['revision'],view['retake'],view['generation'])
            files=list((f.config.private_root/'media'/lease.draft_id).rglob('*.jpg'))
            self.assertEqual(1,len(files))
            before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            old=f.visits._backend.process
            self.assertTrue(worker.stop(timeout=12));self.assertIsNotNone(old.poll())
            self.assertEqual([(1,'ISOLATED',3)],self.rows(f,'SELECT closed,lifecycle,generation FROM pp_drafts'))
            self.assertEqual([('ACKED','NO_PAYMENT')],self.rows(f,'SELECT state,financial_class FROM pp_isolation_ops'))
            self.assertEqual([(1,)],self.rows(f,'SELECT COUNT(*) FROM pp_worker_retirements WHERE backend_verified_at IS NOT NULL'))
            self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
            again=f.manager();f.addCleanup(f.shutdown,again);binding=again.start()
            self.assertIsNone(binding.service.lease)
            self.assertEqual([(0,)],self.rows(f,'SELECT COUNT(*) FROM pp_payment_attempts'))

    def test_paid_original_entitlement_owed_and_proof_return_after_same_root_restart_without_reprint(self):
        with self.fixture() as (f,control,worker):
            group,proof=f.paid(control.binding,{'template_a':2,'template_b':1})
            original=f.visits.ledger.db.execute('SELECT entitlement_id,legitimate_paid_attempt FROM pp_purchase_finance').fetchone()
            sends=f.output_count();self.assertEqual(3,sends)
            self.assertTrue(worker.stop(timeout=12))
            self.assertEqual([tuple(original)],self.rows(f,'SELECT entitlement_id,legitimate_paid_attempt FROM pp_purchase_finance'))
            self.assertEqual([('OWED',)],self.rows(f,'SELECT status FROM pp_paid_services'))
            self.assertEqual([('ACKED','PAID_OWED')],self.rows(f,'SELECT state,financial_class FROM pp_isolation_ops'))
            again=f.manager();f.addCleanup(f.shutdown,again);again.start()
            restored=f.retry(lambda:again.recover_paid(proof))
            self.assertEqual('RESTORED',restored['state']);self.assertEqual(group,restored['purchase_group_id'])
            self.assertEqual(sends,f.output_count())
            self.assertEqual([(1,)],self.rows(f,'SELECT COUNT(*) FROM pp_payment_attempts'))
            self.assertEqual([(2,'SUBMITTED'),(1,'SUBMITTED')],self.rows(f,'SELECT copies,state FROM pp_paid_strip_jobs ORDER BY template_id'))

    def test_lost_shutdown_ack_reply_reuses_exact_operation_and_never_opens_a_new_child(self):
        with self.fixture() as (f,control,worker):
            control.binding.service.start(get_templates(),{'template_a':1})
            transport=f.visits._client._transport;original=transport._call;lost=[];pid=f.visits._backend.process.pid
            def reply(*args,**kwargs):
                result=original(*args,**kwargs)
                if args[1].endswith('/ack') and not lost:
                    lost.append(True);raise OSError('Synthetic lost shutdown ACK')
                return result
            with patch.object(transport,'_call',side_effect=reply),patch.object(f.visits,'_open',side_effect=AssertionError('No new child on shutdown')):
                self.assertTrue(worker.stop(timeout=12))
            self.assertTrue(lost);self.assertGreater(pid,0)
            self.assertEqual([(1,)],self.rows(f,'SELECT COUNT(*) FROM pp_isolation_ops'))
            self.assertEqual([('ACKED',)],self.rows(f,'SELECT state FROM pp_isolation_ops'))
            self.assertEqual([(1,)],self.rows(f,'SELECT COUNT(*) FROM pp_worker_retirements'))

    def test_live_original_photo_worker_blocks_shutdown_ack_and_kernel_release(self):
        with self.fixture() as (f,control,worker):
            service=control.binding.service;service.start(get_templates(),{'template_a':1})
            entered=threading.Event();release=threading.Event()
            def held():entered.set();release.wait(6);return {'phase':'confirm'}
            try:
                with patch.object(service,'snapshot',side_effect=held):
                    control.binding.jobs.submit('snapshot');self.assertTrue(entered.wait(2))
                    self.assertFalse(worker.stop(timeout=.1))
                    self.assertEqual([(0,)],self.rows(f,"SELECT COUNT(*) FROM pp_isolation_ops WHERE state='ACKED'"))
                    with self.assertRaises(OSError):LaunchLease(f.config.private_root)
                    release.set();self.assertTrue(worker.stop(timeout=12))
            finally:release.set()

    def test_repeated_privacy_during_committed_lost_shutdown_ack_never_deadlocks_or_reopens_child(self):
        with self.fixture() as (f,control,worker):
            control.binding.service.start(get_templates(),{'template_a':1})
            transport=f.visits._client._transport;original=transport._call
            committed=threading.Event();release=threading.Event();lost=[]
            def reply(*args,**kwargs):
                result=original(*args,**kwargs)
                if args[1].endswith('/ack') and not lost:
                    lost.append(True);committed.set();release.wait(6)
                    raise OSError('Synthetic committed ACK response lost')
                return result
            try:
                with patch.object(transport,'_call',side_effect=reply),patch.object(f.visits,'_open',side_effect=AssertionError('No shutdown re-open')):
                    self.assertFalse(worker.stop(timeout=.01));self.assertTrue(committed.wait(3))
                    control.hide_private('APP_SUSPENDED')  # New GUI epoch AFTER durable ACK.
                    release.set()
                    self.assertTrue(worker.stop(timeout=3),'Original committed ACK must finish same shutdown')
                self.assertEqual([(1,)],self.rows(f,'SELECT COUNT(*) FROM pp_isolation_ops'))
                self.assertEqual([('ACKED',)],self.rows(f,'SELECT state FROM pp_isolation_ops'))
            finally:release.set()

    def test_uncertain_original_paper_holds_shutdown_without_ack_or_lost_owed(self):
        with self.fixture() as (f,control,worker):
            service=control.binding.service
            # Prepare original paid jobs but keep them PREPARED. Never edit an
            # immutable SUBMITTED job to manufacture a test state.
            with patch.object(service,'paid_print_next',return_value={}):
                group,_=f.paid(control.binding)
            (f.config.private_root/'fixture-output-uncertain-after-send').write_text('synthetic fixture only')
            service.paid_print_next()  # Original SENDING -> uncertain transport -> UNCERTAIN.
            sends=f.output_count()
            self.assertFalse(worker.stop(timeout=.3));self.assertFalse(control.stopped)
            self.assertEqual([(0,)],self.rows(f,"SELECT COUNT(*) FROM pp_isolation_ops WHERE state='ACKED'"))
            self.assertEqual([('OWED',)],self.rows(f,'SELECT status FROM pp_paid_services'))
            self.assertEqual([('UNCERTAIN',)],self.rows(f,'SELECT state FROM pp_paid_strip_jobs'))
            self.assertEqual(sends,f.output_count())
            with self.assertRaises(OSError):LaunchLease(f.config.private_root)

    def test_empty_normal_exit_does_not_invent_customer_release(self):
        with self.fixture() as (f,control,worker):
            self.assertTrue(worker.stop(timeout=12))
            self.assertEqual([(0,)],self.rows(f,'SELECT COUNT(*) FROM pp_drafts'))
            self.assertEqual([(0,)],self.rows(f,'SELECT COUNT(*) FROM pp_isolation_ops'))

    def test_live_visible_owner_cannot_skip_privacy_even_with_trusted_finish_method(self):
        with self.fixture() as (f,control,worker):
            control.binding.service.start(get_templates(),{'template_a':1})
            with self.assertRaises(DraftHeld):f.visits.finish_for_shutdown()
            self.assertEqual([(0,)],self.rows(f,'SELECT COUNT(*) FROM pp_isolation_ops'))
            self.assertTrue(worker.stop(timeout=12))


if __name__=='__main__':unittest.main()
