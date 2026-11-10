"""Protected finance + native/backend actual worker evidence; fake external I/O."""
import hashlib
import threading
import unittest
from unittest.mock import patch

from photobooth.post_preview_claim import OriginalMockClaim
from photobooth.post_preview_sandbox_delivery import OriginalSandboxPaidDelivery
from photobooth.post_preview_sandbox_handoff import OriginalSandboxClaim,OriginalSandboxIsolation
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_worker_fence import WorkerReceiptVerifier,WorkerFenceKey
from tests.post_preview_handoff_fixture import ProtectedHandoffHarness


class ProtectedSandboxHandoffTests(unittest.TestCase):
    def fixture(self, **kwargs):
        self.h=ProtectedHandoffHarness(self,**kwargs)
        self.f=self.h.f
        return self.h

    def test_original_worker_receipt_ack_and_proof_restore_same_paid_output(self):
        h=self.fixture(delivery=True)
        entitlement=self.f.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0]
        files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.f.service.photos.root.rglob('*.jpg')}
        original=self.f.ledger.db.execute('SELECT transaction_id,folder_url FROM pp_paid_services').fetchone()
        op=h.prepare()
        with self.assertRaises(DraftHeld):h.isolation.acknowledge('PB001',op)
        self.assertFalse(self.f.actor._closing.is_set())
        self.assertTrue(h.ack(op))
        self.assertFalse(h.isolation.acknowledge('PB001',op))
        result=h.recover()
        self.assertEqual('REACQUIRED',result['state'])
        self.assertEqual(entitlement,result['entitlement_id'])
        self.assertEqual(self.f.lease.draft_id,result['lease'].draft_id)
        self.assertEqual(4,result['lease'].generation)
        actor=OriginalSandboxPaidDelivery(self.f.actor.binder,self.f.templates)
        self.addCleanup(actor.stop);actor.worker.start=lambda:None;actor.worker.notify_transaction=lambda _:None
        view=actor.prepare(self.f.group,result['lease'])
        actor.print_next(self.f.group,result['lease'])
        self.assertTrue(view['print_all_submitted'])
        self.assertEqual(original,self.f.ledger.db.execute('SELECT transaction_id,folder_url FROM pp_paid_services').fetchone())
        self.assertEqual(files,{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.f.service.photos.root.rglob('*.jpg')})
        self.assertEqual(2,len(self.f.sends));self.assertEqual(1,len(self.f.binds));self.assertEqual(1,self.f.remote.charges)
        self.assertEqual(1,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_ticket_credentials').fetchone()[0])

    def test_busy_original_or_B_returns_wait_without_provider_io_or_preemption(self):
        h=self.fixture()
        self.assertEqual('WAIT',h.recover()['state'])
        op=h.prepare();h.ack(op)
        b=self.f.ledger.create('PB001','visitor-B',{'template_a':1})
        reads=self.f.remote.reads
        self.f.remote.outage=True
        result=h.recover()
        self.assertEqual('WAIT',result['state']);self.assertEqual(reads,self.f.remote.reads)
        self.assertEqual(b.draft_id,self.f.ledger.db.execute('SELECT draft_id FROM pp_drafts WHERE closed=0').fetchone()[0])

    def test_pending_unknown_and_outage_hold_original_before_any_release(self):
        h=self.fixture(settled=False)
        with self.assertRaises(DraftHeld):h.prepare()
        self.f.remote.outage=True
        with self.assertRaises(DraftHeld):h.prepare()
        self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual(0,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual(1,self.f.remote.charges)

    def test_late_original_paid_can_isolate_and_claim_without_ticket_reissue(self):
        h=self.fixture(settled=False)
        order=self.f.ledger.db.execute('SELECT provider_order_id FROM pp_payment_attempts').fetchone()[0]
        self.f.remote.state(order,'settlement')
        op=h.prepare();h.ack(op)
        self.assertEqual('REACQUIRED',h.recover()['state'])
        self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_ticket_credentials').fetchone()[0])
        self.assertEqual(1,self.f.remote.charges)

    def test_receipt_uncertainty_and_photo_uncertainty_never_prepare_release(self):
        for mode in ('receipt','photo'):
            h=self.fixture(delivery=mode=='photo',uncertain_receipt=mode=='receipt',uncertain_photo=mode=='photo')
            with self.subTest(mode=mode),self.assertRaises(DraftHeld):h.prepare()
            table,column=('pp_ticket_presentations','receipt_state') if mode=='receipt' else ('pp_paid_strip_jobs','state')
            self.assertEqual('UNCERTAIN',self.f.ledger.db.execute('SELECT '+column+' FROM '+table).fetchone()[0])
            self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])

    def test_live_backend_thread_keeps_ack_false_and_owed_after_native_receipt(self):
        h=self.fixture();op=h.prepare();h.native.publish(op,timeout=1)
        entered,release=threading.Event(),threading.Event()
        def live():entered.set();release.wait(5)
        self.f.actor.worker._thread=threading.Thread(target=live)
        self.f.actor.worker._thread.start()
        try:
            self.assertTrue(entered.wait(2));self.f.clock[0]+=2
            with self.assertRaises(DraftHeld):h.isolation.acknowledge('PB001',op)
            self.assertEqual('PREPARED',self.f.ledger.db.execute('SELECT state FROM pp_isolation_ops').fetchone()[0])
            self.assertIsNone(self.f.ledger.db.execute('SELECT backend_verified_at FROM pp_worker_retirements').fetchone()[0])
            self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        finally:release.set();self.f.actor.worker._thread.join(5)
        self.assertTrue(h.isolation.acknowledge('PB001',op))

    def test_foreign_worker_key_cannot_ack_a_genuine_other_receipt(self):
        h=self.fixture();op=h.prepare();h.native.publish(op,timeout=1)
        wrong=OriginalSandboxIsolation(h.payments,self.f.actor,WorkerReceiptVerifier(self.f.ledger,WorkerFenceKey.create()))
        with self.assertRaises(DraftHeld):wrong.acknowledge('PB001',op)
        self.assertEqual(0,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_wrong_proof_role_wrong_booth_and_forgery_cannot_reacquire(self):
        h=self.fixture();op=h.prepare();h.ack(op)
        for payload in ('MEONG:QRIS:1:bad',h.proof[:-1]+('A' if h.proof[-1]!='A' else 'B')):
            with self.subTest(role=payload.split(':')[1]),self.assertRaises(PermissionError):h.recover(payload)
        with self.assertRaises((PermissionError,DraftHeld)):
            h.claim.claim(self.f.group,'PB002',h.proof)
        self.assertEqual(1,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_provider_outage_after_ack_preserves_closed_owed_and_original_proof(self):
        h=self.fixture();op=h.prepare();h.ack(op);self.f.remote.outage=True
        with self.assertRaises(DraftHeld):h.recover()
        self.assertEqual(1,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_original_paid_ticket_is_a_valid_distinct_claim_role(self):
        h=self.fixture();op=h.prepare();h.ack(op)
        self.assertEqual('REACQUIRED',h.recover(h.ticket_proof)['state'])

    def test_forged_ack_row_without_backend_validated_worker_cannot_grant_claim(self):
        h=self.fixture();op=h.prepare()
        self.f.ledger.db.execute("UPDATE pp_drafts SET closed=1,lifecycle='ISOLATED',generation=3")
        self.f.ledger.db.execute("UPDATE pp_isolation_ops SET state='ACKED',acknowledged_at=?",(self.f.clock[0],))
        with self.assertRaises(DraftHeld):h.recover()
        self.assertEqual(1,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_mock_constructor_still_rejects_protected_sandbox_context(self):
        h=self.fixture()
        with self.assertRaises(DraftHeld):
            OriginalMockClaim(h.payments,h.claim.ccp,h.claim.ticket,allow_incomplete_fixture=True)
        with self.assertRaises(DraftHeld):OriginalSandboxClaim(object(),h.claim.ccp,h.claim.ticket)

    def test_same_original_ack_retries_after_provider_pacing_without_new_operation(self):
        h=self.fixture();op=h.prepare();h.native.publish(op,timeout=1)
        with self.assertRaises(DraftHeld):h.isolation.acknowledge('PB001',op)
        self.assertEqual('PREPARED',self.f.ledger.db.execute('SELECT state FROM pp_isolation_ops').fetchone()[0])
        self.f.clock[0]+=2
        self.assertTrue(h.isolation.acknowledge('PB001',op))
        self.assertEqual(1,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual(1,self.f.remote.charges)

    def test_financial_review_after_prepare_cannot_be_acked_as_safe_release(self):
        h=self.fixture();op=h.prepare();h.native.publish(op,timeout=1)
        order=self.f.ledger.db.execute('SELECT provider_order_id FROM pp_payment_attempts').fetchone()[0]
        self.f.remote.state(order,'refund');self.f.clock[0]+=2
        with self.assertRaises(DraftHeld):h.isolation.acknowledge('PB001',op)
        self.assertEqual('PREPARED',self.f.ledger.db.execute('SELECT state FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual(0,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_new_backend_verifiers_preserve_durably_validated_original_receipt_and_proof(self):
        from photobooth.post_preview_ccp import OriginalCCPService
        from photobooth.post_preview_ticket import OriginalRecoveryTicketService
        h=self.fixture();op=h.prepare();h.ack(op)
        original=h.claim.ticket.protector
        restarted=OriginalSandboxClaim(h.payments,OriginalCCPService(self.f.ledger,original,'MTEST'),
                                       OriginalRecoveryTicketService(h.payments,original))
        self.f.clock[0]+=2
        self.assertEqual('REACQUIRED',restarted.claim(self.f.group,'PB001',h.proof)['state'])
        self.assertEqual(1,self.f.remote.charges)

    def test_clock_rollback_during_ack_cannot_close_original_occupancy(self):
        h=self.fixture();op=h.prepare();h.native.publish(op,timeout=1);self.f.clock[0]+=2
        original=h.isolation._financial
        def rollback(draft):
            result=original(draft);self.f.clock[0]-=60;return result
        with patch.object(h.isolation,'_financial',side_effect=rollback),self.assertRaises(DraftHeld):
            h.isolation.acknowledge('PB001',op)
        self.assertEqual(0,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual('PREPARED',self.f.ledger.db.execute('SELECT state FROM pp_isolation_ops').fetchone()[0])

    def test_late_paid_after_verified_unpaid_isolation_preserves_original_proof_claim(self):
        h=self.fixture(settled=False)
        order=self.f.ledger.db.execute('SELECT provider_order_id FROM pp_payment_attempts').fetchone()[0]
        self.f.remote.state(order,'expire')
        op=h.prepare();h.ack(op)
        self.assertEqual('TERMINAL_UNPAID',self.f.ledger.db.execute('SELECT financial_class FROM pp_isolation_ops').fetchone()[0])
        self.f.remote.state(order,'settlement')
        result=h.recover()
        self.assertEqual('REACQUIRED',result['state'])
        self.assertEqual(self.f.lease.draft_id,result['lease'].draft_id)
        self.assertEqual(1,self.f.remote.charges)
        self.assertEqual('OWED',h.payments.inspect(self.f.group,'PB001')['obligation_state'])


class ProtectedOriginalCancelHandoffTests(unittest.TestCase):
    def test_cancel_reply_alone_and_pending_get_never_create_release_or_resend_cancel(self):
        h=ProtectedHandoffHarness(self,settled=False,retire_event='USER_CANCEL')
        def ignored(order):
            h.f.remote.cancels+=1
            return dict(h.f.remote.rows[order],transaction_status='cancel')
        with patch.object(h.f.remote,'cancel',side_effect=ignored):
            for _ in range(2):
                with self.assertRaises(DraftHeld):h.prepare()
        self.assertEqual(1,h.f.remote.cancels)
        self.assertEqual(0,h.f.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual(0,h.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual('PENDING',h.f.ledger.db.execute('SELECT payment_state FROM pp_payment_attempts').fetchone()[0])

    def test_cancel_then_get_outage_keeps_original_occupancy_until_fresh_terminal_observed(self):
        h=ProtectedHandoffHarness(self,settled=False,retire_event='USER_CANCEL')
        h.f.remote.outage=True
        with self.assertRaises(DraftHeld):h.prepare()
        self.assertEqual(1,h.f.remote.cancels)
        self.assertEqual(0,h.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        h.f.remote.outage=False
        op=h.prepare();h.ack(op)
        self.assertEqual(1,h.f.remote.cancels);self.assertEqual(1,h.f.remote.charges)

    def test_minimize_and_result_timeout_never_cancel_a_pending_original_attempt(self):
        for event in ('APP_SUSPENDED','RESULT_TIMEOUT'):
            with self.subTest(event=event):
                h=ProtectedHandoffHarness(self,settled=False,retire_event=event)
                with self.assertRaises(DraftHeld):h.prepare()
                self.assertEqual(0,h.f.remote.cancels)
                self.assertEqual(0,h.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_explicit_pending_cancel_is_reconciled_without_a_background_scheduler_tick(self):
        h=ProtectedHandoffHarness(self,settled=False,retire_event='USER_CANCEL')
        op=h.prepare()
        self.assertEqual(1,h.f.remote.cancels)
        self.assertEqual('TERMINAL_UNPAID',h.f.ledger.db.execute('SELECT financial_class FROM pp_isolation_ops').fetchone()[0])
        h.ack(op)
        self.assertEqual((1,3),tuple(h.f.ledger.db.execute('SELECT closed,generation FROM pp_drafts').fetchone()))
        self.assertEqual(1,h.f.remote.charges);self.assertEqual(1,h.f.remote.cancels)

    def test_lost_original_cancel_reply_still_requires_independent_get_and_never_resends(self):
        h=ProtectedHandoffHarness(self,settled=False,retire_event='USER_CANCEL')
        h.f.remote.lose_cancel_response=True
        op=h.prepare();h.ack(op)
        self.assertEqual(1,h.f.remote.cancels)
        self.assertEqual('CANCELLED_UNPAID',h.f.ledger.db.execute('SELECT payment_state FROM pp_payment_attempts').fetchone()[0])
        self.assertGreaterEqual(h.f.remote.reads,2)

    def test_settlement_racing_original_cancel_keeps_owed_proof_and_claim_identity(self):
        h=ProtectedHandoffHarness(self,settled=False,retire_event='USER_CANCEL')
        h.f.remote.settle_on_cancel=True
        op=h.prepare();h.ack(op)
        self.assertEqual('PAID_OWED',h.f.ledger.db.execute('SELECT financial_class FROM pp_isolation_ops').fetchone()[0])
        result=h.recover();self.assertEqual('REACQUIRED',result['state'])
        self.assertEqual(h.f.lease.draft_id,result['lease'].draft_id)
        self.assertEqual(1,h.f.remote.charges);self.assertEqual(1,h.f.remote.cancels)


if __name__=='__main__':unittest.main()
