"""Connected original financial/worker journal experiments, never actual refunds."""
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest

from photobooth.post_preview_refund_simulation import MockRefundCoordinator, SimulatedRefundProvider
from photobooth.post_preview_refund_assessment import OriginalRefundEvidence, VerifiedPaidAttempt
from photobooth.post_preview_isolation import OriginalMockIsolation
from photobooth.post_preview_store import DraftHeld


class MockRefundLifecycleTests(unittest.TestCase):
    def setUp(self):
        from tests.test_post_preview_checkout_ticket import PrivateTicketCheckoutTests
        self.helper=PrivateTicketCheckoutTests(methodName='runTest');self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.f=self.helper.fixture;self.s=self.f.service
        frozen=self.helper.freeze();self.proof=frozen['ccp_offer'].qr_payload
        self.s.ccp_visible(frozen['ccp_offer']);view=self.s.begin_payment()
        self.f.provider.state(view['payment']['attempts'][0]['provider_order_id'],'settlement')
        self.s.check_payment('connectivity');self.s.prepare_ticket()
        self.group=self.s.group;self.booth='PB001'
        self.s.retire('APP_SUSPENDED')
        self.iso=OriginalMockIsolation(self.s.ledger,self.f.backend,self.f.jobs,self.f.launch_lease,
            printer_lane=self.s._receipt_lane,allow_incomplete_fixture=True)
        self.provider=SimulatedRefundProvider(Path(self.helper.temp.name)/'remote.sqlite3',simulation=True)
        self.addCleanup(self.provider.close)
        self.c=MockRefundCoordinator(self.f.backend,self.provider,isolation=self.iso,simulation=True)
        finance=self.s.ledger.db.execute('SELECT * FROM pp_purchase_finance').fetchone()
        attempt=self.s.ledger.db.execute('SELECT * FROM pp_payment_attempts').fetchone()
        self.e=OriginalRefundEvidence(self.group,'MTEST',finance['amount'],
            VerifiedPaidAttempt(attempt['attempt_id'],attempt['provider_ref'],'MTEST',finance['amount'],True),
            reason='IRRECOVERABLE_MERCHANT_SERVICE',service_irrecoverable=True,
            financial_integrity_verified=True,all_external_workers_fenced=True,
            merchant_refund_feature_verified=True,approved_commercial_policy=True,approved_abuse_limit=True)

    def key(self,intent):
        return self.s.ledger.db.execute('SELECT refund_key FROM pp_mock_refund_intents WHERE intent_id=?',(intent,)).fetchone()[0]

    def prepare(self):return self.c.prepare(self.e,self.booth)

    def test_unique_intent_precedes_any_simulator_request_and_identity_is_immutable(self):
        intent=self.prepare();self.assertEqual(intent,self.prepare())
        self.assertEqual('PREPARED',self.c.status(intent,self.group,self.booth)['state'])
        self.assertEqual(0,self.provider.db.execute('SELECT count(*) FROM simulated_refunds').fetchone()[0])
        with self.assertRaises(sqlite3.IntegrityError),self.s.ledger.write():
            self.s.ledger.db.execute('UPDATE pp_mock_refund_intents SET amount=1')

    def test_requested_processing_confirmed_never_claim_actual_money_or_free_booth(self):
        intent=self.prepare();state=self.c.submit(intent,self.group,self.booth)
        self.assertEqual('REQUESTED',state['state']);self.assertFalse(state['money_returned'])
        for stage in ('PROCESSING','CONFIRMED'):
            self.provider.advance(self.key(intent),stage)
            state=self.c.reconcile(intent,self.group,self.booth)
            self.assertEqual(stage,state['state']);self.assertTrue(state['simulation_only']);self.assertFalse(state['money_returned'])
        self.assertEqual(0,self.s.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual('OWED',self.s.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual('PAID',self.s.ledger.db.execute('SELECT payment_state FROM pp_payment_attempts').fetchone()[0])
        self.assertEqual(0,self.s.ledger.db.execute('SELECT count(*) FROM pp_isolation_ops').fetchone()[0])

    def test_lost_reply_and_repeated_notifications_reconcile_same_key_without_second_request(self):
        intent=self.prepare();self.provider.lose_reply=True
        self.assertEqual('REQUESTED',self.c.submit(intent,self.group,self.booth)['state'])
        for _ in range(5):self.c.submit(intent,self.group,self.booth)
        row=self.provider.db.execute('SELECT * FROM simulated_refunds').fetchone()
        self.assertEqual(self.key(intent),row['refund_key']);self.assertEqual(1,row['requests'])
        self.assertEqual(1,self.provider.db.execute('SELECT count(*) FROM simulated_refunds').fetchone()[0])

    def test_uncertain_send_before_provider_is_never_blindly_reposted(self):
        intent=self.prepare()
        def fail(_):raise RuntimeError('Synthetic process boundary before provider receives request')
        with self.assertRaises(RuntimeError):self.c.submit(intent,self.group,self.booth,checkpoint=fail)
        for _ in range(3):self.assertEqual('SENT_UNKNOWN',self.c.submit(intent,self.group,self.booth)['state'])
        self.assertEqual(0,self.provider.db.execute('SELECT count(*) FROM simulated_refunds').fetchone()[0])

    def test_wrong_charge_provider_evidence_requires_review_and_does_not_downgrade_confirmed(self):
        intent=self.prepare();self.c.submit(intent,self.group,self.booth)
        self.provider.advance(self.key(intent),'CONFIRMED');self.c.reconcile(intent,self.group,self.booth)
        self.provider.advance(self.key(intent),'REQUESTED')
        self.assertEqual('CONFIRMED',self.c.reconcile(intent,self.group,self.booth)['state'])
        wrong=self.provider.lookup(self.key(intent));wrong['charge_ref']='foreign-charge'
        self.provider.response_override=wrong
        self.assertEqual('REVIEW_REQUIRED',self.c.reconcile(intent,self.group,self.booth)['state'])

    def test_eligibility_unknown_and_forged_settlement_facts_never_prepare_or_send(self):
        for eligibility in (False,None):
            self.provider.eligible=eligibility
            with self.assertRaises(DraftHeld):self.prepare()
        self.provider.eligible=True
        forged=replace(self.e,original=replace(self.e.original,provider_ref='foreign-charge'))
        with self.assertRaises(DraftHeld):self.c.prepare(forged,self.booth)
        self.assertEqual(0,self.s.ledger.db.execute('SELECT count(*) FROM pp_mock_refund_intents').fetchone()[0])

    def test_busy_or_uncertain_original_paper_cannot_commit_full_refund_intent(self):
        with self.s._receipt_lane:
            with self.assertRaises(DraftHeld):self.prepare()
        with self.s.ledger.write():self.s.ledger.db.execute("UPDATE pp_ticket_presentations SET receipt_state='UNCERTAIN'")
        with self.assertRaises(DraftHeld):self.prepare()
        self.assertEqual(0,self.s.ledger.db.execute('SELECT count(*) FROM pp_mock_refund_intents').fetchone()[0])

    def test_full_refund_intent_prevents_original_private_claim_after_safe_machine_ack(self):
        from photobooth.post_preview_claim import OriginalMockClaim
        from photobooth.post_preview_ccp import OriginalCCPService
        from photobooth.post_preview_ticket import OriginalRecoveryTicketService
        intent=self.prepare();self.c.submit(intent,self.group,self.booth)
        self.provider.advance(self.key(intent),'CONFIRMED');self.c.reconcile(intent,self.group,self.booth)
        op=self.iso.prepare(self.booth);self.iso.acknowledge(self.booth,op)
        claim=OriginalMockClaim(self.f.backend,
            OriginalCCPService(self.s.ledger,self.f.protector,'MTEST',allow_synthetic=True),
            OriginalRecoveryTicketService(self.f.backend,self.f.protector,allow_synthetic=True),allow_incomplete_fixture=True)
        with self.assertRaises(DraftHeld):claim.claim(self.group,self.booth,self.proof)
        self.assertEqual(1,self.s.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual(0,len(self.f.receipt_sizes))

    def test_foreign_booth_or_group_cannot_read_status_and_status_contains_no_charge_or_proof(self):
        intent=self.prepare()
        with self.assertRaises(DraftHeld):self.c.status(intent,self.group,'PB002')
        with self.assertRaises(DraftHeld):self.c.status(intent,'f'*32,self.booth)
        payload=json.dumps(self.c.status(intent,self.group,self.booth))
        self.assertNotIn(self.e.original.provider_ref,payload);self.assertNotIn(self.proof,payload)
        self.assertFalse(self.c.status(intent,self.group,self.booth)['media_authorized'])

    def test_multiple_coordinators_cannot_duplicate_original_simulator_request(self):
        intent=self.prepare();other=MockRefundCoordinator(self.f.backend,self.provider,isolation=self.iso,simulation=True)
        barrier=threading.Barrier(2);errors=[]
        def send(c):
            barrier.wait()
            try:c.submit(intent,self.group,self.booth)
            except DraftHeld:pass
            except Exception as error:errors.append(type(error).__name__)
        threads=[threading.Thread(target=send,args=(c,)) for c in (self.c,other)]
        for t in threads:t.start()
        for t in threads:t.join(10);self.assertFalse(t.is_alive())
        self.assertEqual([],errors)
        self.assertEqual('REQUESTED',self.c.reconcile(intent,self.group,self.booth)['state'])
        self.assertEqual(1,self.provider.db.execute('SELECT requests FROM simulated_refunds').fetchone()[0])

    def test_eligibility_loss_after_durable_intent_stops_request_without_new_key(self):
        intent=self.prepare();key=self.key(intent)
        self.provider.eligible=None
        with self.assertRaises(DraftHeld):self.c.submit(intent,self.group,self.booth)
        self.assertEqual('PREPARED',self.c.status(intent,self.group,self.booth)['state'])
        self.assertEqual(0,self.provider.db.execute('SELECT count(*) FROM simulated_refunds').fetchone()[0])
        self.provider.eligible=True
        self.assertEqual('REQUESTED',self.c.submit(intent,self.group,self.booth)['state'])
        self.assertEqual(key,self.key(intent))

    def test_original_refund_after_ack_does_not_preempt_new_active_visitor(self):
        op=self.iso.prepare(self.booth);self.iso.acknowledge(self.booth,op)
        self.s.reset_after_acked_isolation(op)
        next_view=self.helper.freeze();self.s.ccp_visible(next_view['ccp_offer'])
        self.s.begin_payment()
        new_owner=self.s.lease
        intent=self.prepare()
        self.assertEqual('REQUESTED',self.c.submit(intent,self.group,self.booth)['state'])
        self.assertEqual(new_owner,self.s.lease)
        self.assertEqual('ACTIVE',self.s.ledger.db.execute('SELECT lifecycle FROM pp_drafts WHERE draft_id=?',(new_owner.draft_id,)).fetchone()[0])
        self.assertEqual(2,self.f.provider.charges)

    def test_excess_refund_targets_only_extra_settled_charge_and_keeps_rightful_service(self):
        from tests.test_post_preview_checkout_ticket import PrivateTicketCheckoutTests
        h=PrivateTicketCheckoutTests(methodName='runTest');h.setUp();self.addCleanup(h.doCleanups)
        f=h.fixture;s=f.service
        view=h.freeze();s.ccp_visible(view['ccp_offer']);first=s.begin_payment()
        f.provider.state(first['payment']['attempts'][0]['provider_order_id'],'expire')
        s.check_payment('connectivity')
        second=s.continue_payment(True)['payment']
        for a in second['attempts']:f.provider.state(a['provider_order_id'],'settlement')
        f.backend.reconcile_all(s.group,'PB001',force=True);s.check_payment('connectivity')
        finance=s.ledger.db.execute('SELECT * FROM pp_purchase_finance').fetchone()
        rows=[dict(x) for x in s.ledger.db.execute('SELECT * FROM pp_payment_attempts')]
        original=next(x for x in rows if x['attempt_id']==finance['legitimate_paid_attempt'])
        extra=next(x for x in rows if x is not original)
        def paid(x):return VerifiedPaidAttempt(x['attempt_id'],x['provider_ref'],'MTEST',finance['amount'],True)
        e=OriginalRefundEvidence(s.group,'MTEST',finance['amount'],paid(original),excess=(paid(extra),),
            reason='EXCESS_SETTLED_ATTEMPTS',financial_integrity_verified=True,
            merchant_refund_feature_verified=True,approved_commercial_policy=True,approved_abuse_limit=True)
        c=MockRefundCoordinator(f.backend,self.provider,simulation=True)
        intent=c.prepare(e,'PB001');c.submit(intent,s.group,'PB001')
        row=self.provider.db.execute('SELECT * FROM simulated_refunds').fetchone()
        self.assertEqual(extra['provider_ref'],row['charge_ref'])
        self.assertNotEqual(original['provider_ref'],row['charge_ref'])
        self.provider.advance(row['refund_key'],'CONFIRMED');c.reconcile(intent,s.group,'PB001')
        self.assertEqual('ticket_offer',s.prepare_ticket()['phase'])
        self.assertEqual(finance['entitlement_id'],s.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0])

    def test_simulator_cannot_accept_a_generic_or_real_provider(self):
        with self.assertRaises(DraftHeld):MockRefundCoordinator(self.f.backend,object(),simulation=True)
        with self.assertRaises(DraftHeld):MockRefundCoordinator(self.f.backend,self.provider,isolation=self.iso)
        original=self.f.backend.mode
        try:
            self.f.backend.mode='sandbox'
            with self.assertRaises(DraftHeld):MockRefundCoordinator(self.f.backend,self.provider,isolation=self.iso,simulation=True)
        finally:self.f.backend.mode=original


class MockRefundProcessTests(unittest.TestCase):
    def probe(self, boundary, state, requests):
        with tempfile.TemporaryDirectory() as folder:
            cmd=[sys.executable, '-m', 'tests.post_preview_refund_process_fixture', folder]
            cwd=Path(__file__).resolve().parents[1]
            before=subprocess.run(cmd+['produce',boundary], text=True, capture_output=True, cwd=cwd, timeout=60)
            self.assertEqual(73,before.returncode,before.stderr[-2000:])
            after=subprocess.run(cmd+['consume',boundary], input=before.stdout, text=True,
                                 capture_output=True, cwd=cwd, timeout=60)
            self.assertEqual(0,after.returncode,after.stderr[-2000:])
            observed=json.loads(after.stdout)
            self.assertEqual(state,observed['state'])
            self.assertEqual(requests,observed['provider_requests'])
            self.assertEqual(requests,observed['provider_rows'])
            self.assertEqual(1,observed['intents'])
            self.assertEqual(0,observed['new_charges'])
            self.assertEqual(0,observed['active'])
            self.assertEqual('OWED',observed['owed'])
            self.assertEqual('PAID',observed['payment'])
            self.assertTrue(observed['simulation_only'])
            self.assertFalse(observed['money_returned'])
            self.assertFalse(observed['media_authorized'])

    def test_prepared_intent_survives_hard_exit_before_any_request(self):
        self.probe('PREPARED','REQUESTED',1)

    def test_sent_unknown_hard_exit_before_provider_never_blindly_reposts(self):
        self.probe('SENT_BEFORE_SIMULATOR','SENT_UNKNOWN',0)

    def test_accepted_request_hard_exit_before_local_reply_reconciles_once(self):
        self.probe('SIMULATOR_REPLY_BOUNDARY','REQUESTED',1)


class MockRefundWorkerFenceTests(unittest.TestCase):
    def setUp(self):
        from tests.test_post_preview_journey_matrix import CustomerJourneyMatrixTests
        self.h=CustomerJourneyMatrixTests(methodName='runTest');self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.h.ready_to_print()
        self.f=self.h.fixture;self.s=self.f.service
        self.iso=OriginalMockIsolation(self.s.ledger,self.f.backend,self.f.jobs,self.f.launch_lease,
            printer_lane=self.s._receipt_lane,delivery=self.f.paid_monitor,allow_incomplete_fixture=True)
        self.provider=SimulatedRefundProvider(Path(self.h.temp.name)/'mock-refund.sqlite3',simulation=True)
        self.addCleanup(self.provider.close)
        self.c=MockRefundCoordinator(self.f.backend,self.provider,isolation=self.iso,simulation=True)
        finance=self.s.ledger.db.execute('SELECT * FROM pp_purchase_finance').fetchone()
        paid=self.s.ledger.db.execute('SELECT * FROM pp_payment_attempts').fetchone()
        self.e=OriginalRefundEvidence(self.s.group,'MTEST',finance['amount'],
            VerifiedPaidAttempt(paid['attempt_id'],paid['provider_ref'],'MTEST',finance['amount'],True),
            reason='IRRECOVERABLE_MERCHANT_SERVICE',service_irrecoverable=True,
            financial_integrity_verified=True,all_external_workers_fenced=True,
            merchant_refund_feature_verified=True,approved_commercial_policy=True,approved_abuse_limit=True)

    def test_original_inflight_photo_send_denies_full_refund_without_freeing_or_replaying(self):
        from types import SimpleNamespace
        entered=threading.Event();release=threading.Event();errors=[]
        def send(*args,**kwargs):
            entered.set()
            if not release.wait(10):raise TimeoutError('Synthetic printer barrier')
            return SimpleNamespace(success=True)
        printer=SimpleNamespace(print_image=send)
        lease=self.s.lease;group=self.s.group
        def dispatch():
            try:self.f.paid_dispatcher.send_once(lease,group,'template_a',printer,shared_lane=self.s._receipt_lane)
            except DraftHeld:pass  # retirement may fence completion, never repeat bytes
            except Exception as error:errors.append(type(error).__name__)
        worker=threading.Thread(target=dispatch)
        worker.start()
        try:
            self.assertTrue(entered.wait(5))
            self.s.retire('APP_SUSPENDED')
            with self.assertRaises(DraftHeld):self.c.prepare(self.e,'PB001')
            self.assertEqual(0,self.s.ledger.db.execute('SELECT count(*) FROM pp_mock_refund_intents').fetchone()[0])
            self.assertEqual(0,self.provider.db.execute('SELECT count(*) FROM simulated_refunds').fetchone()[0])
            self.assertEqual('SENDING',self.s.ledger.db.execute('SELECT state FROM pp_paid_strip_jobs').fetchone()[0])
        finally:
            release.set();worker.join(10)
        self.assertFalse(worker.is_alive());self.assertEqual([],errors)
        with self.assertRaises(DraftHeld):self.c.prepare(self.e,'PB001')
        self.assertEqual('OWED',self.s.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_existing_cloud_worker_is_conservatively_outside_simulator_fence(self):
        from photobooth.booth_sync import BoothDriveWorker
        worker=BoothDriveWorker(self.f.workspace,self.f.drive)
        self.f.paid_monitor.worker=worker
        self.s.retire('APP_SUSPENDED')
        with self.assertRaisesRegex(DraftHeld,'Live cloud worker'):
            self.c.prepare(self.e,'PB001')
        self.assertEqual(0,self.provider.db.execute('SELECT count(*) FROM simulated_refunds').fetchone()[0])


if __name__=='__main__':unittest.main()
