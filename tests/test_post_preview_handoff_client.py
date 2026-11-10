"""Typed native claim/restore seam over original authenticated API and journals."""
from dataclasses import replace
import hashlib
import threading
import time
import unittest
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image
from photobooth.booth_auth import BoothAuthenticator
from photobooth.kiosk_v2.post_preview_protected_checkout import ProtectedCheckoutService
from photobooth.post_preview_api import create_app
from photobooth.post_preview_handoff_client import PostPreviewHandoffClient
from photobooth.post_preview_presentation import OriginalCCPPresentation
from photobooth.post_preview_sandbox_delivery import OriginalSandboxPaidDelivery
from photobooth.post_preview_sandbox_handoff import OriginalSandboxIsolation
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_checkout_fixture import SessionAdapter
from tests.post_preview_handoff_fixture import ProtectedHandoffHarness


class ProtectedHandoffClientTests(unittest.TestCase):
    def setUp(self):
        self.h=ProtectedHandoffHarness(self,delivery=True)
        self.f=self.h.f
        self.request=uuid.uuid4().hex
        self.fresh=ProtectedCheckoutService(self.f.root,payment_client=self.f.client,
            qr_loader=lambda _:Image.new('RGB',(200,200),'white'))
        self.addCleanup(self.fresh.ledger.close)
        self.mount(self.f.actor,self.h.isolation)

    def mount(self,actor,isolation):
        app=create_app(self.h.payments,BoothAuthenticator({'PB001':'x'*48}),background_worker=False,
            ccp_presentation=OriginalCCPPresentation(self.h.claim.ccp),
            ticket_presentation=actor.binder.presentation,paid_delivery=actor,
            protected_isolation=isolation,protected_claim=self.h.claim)
        http=TestClient(app);self.addCleanup(http.close)
        self.adapter=SessionAdapter(http)
        self.f.client._transport.session=self.adapter

    def release(self):
        client=self.fresh._handoff
        retired=replace(self.f.lease,generation=2)
        self.f.clock[0]+=2
        operation=client.prepare(retired)
        self.assertEqual('PREPARED',operation.state)
        with self.assertRaises(DraftHeld):client.acknowledge(operation)
        self.h.native.publish(operation.operation_id,timeout=1)
        self.f.clock[0]+=2
        ack=client.acknowledge(operation)
        self.assertEqual('ACKED',ack.state)
        self.assertEqual(ack,client.acknowledge(ack))
        return ack

    def claim(self):
        self.f.clock[0]+=2
        return self.fresh.claim_original(self.f.group,self.h.proof,self.request)

    def test_protected_restore_keeps_original_hashes_ticket_folder_and_no_resends(self):
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (self.f.root/'media').rglob('*') if p.is_file()}
        financial=self.h.payments.inspect(self.f.group,'PB001')
        old=self.f.ledger.db.execute('SELECT * FROM pp_paid_services').fetchone()
        sends=len(self.f.sends);self.release()
        # Explicit next trusted backend actor, not a claim of launcher rotation.
        actor=OriginalSandboxPaidDelivery(self.f.actor.binder,self.f.templates)
        actor.worker.start=lambda:None;actor.worker.notify_transaction=lambda _:None
        self.addCleanup(actor.stop)
        isolation=OriginalSandboxIsolation(self.h.payments,actor,self.h.receipts)
        self.mount(actor,isolation)
        view=self.claim()
        self.assertEqual('paid_hold',view['phase']);self.assertTrue(view['ticket_dismissed'])
        self.assertEqual(financial['entitlement_id'],view['payment']['entitlement_id'])
        self.assertEqual(4,self.fresh.lease.generation)
        self.assertEqual(self.f.lease.draft_id,self.fresh.lease.draft_id)
        self.assertEqual(old['folder_url'],self.fresh.prepare_paid_delivery()['delivery']['folder_url'])
        self.assertTrue(self.fresh.paid_print_next()['delivery']['print_all_submitted'])
        self.assertEqual(sends,len(self.f.sends));self.assertEqual(1,self.f.remote.charges)
        self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in before})
        self.assertIsNone(self.fresh._handoff._grant)
        self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_lost_claim_reply_retries_same_original_request_without_second_grant(self):
        self.release();self.adapter.lose_response=True
        with self.assertRaises(DraftHeld):self.claim()
        self.assertIsNone(self.fresh.lease);self.assertIsNone(self.fresh._handoff._grant)
        self.assertEqual('REACQUIRED',self.f.ledger.db.execute('SELECT state FROM pp_protected_claim_ops').fetchone()[0])
        self.assertEqual('paid_hold',self.claim()['phase'])
        self.assertEqual(4,self.fresh.lease.generation);self.assertEqual(1,self.f.remote.charges)
        self.assertEqual(1,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])

    def test_original_busy_wait_never_restores_or_contacts_provider(self):
        reads=self.f.remote.reads
        self.assertEqual(dict(state='WAIT',reason='BOOTH_BUSY'),self.claim())
        self.assertIsNone(self.fresh.lease);self.assertEqual('confirm',self.fresh.phase)
        self.assertEqual(reads,self.f.remote.reads)

    def test_foreign_or_reconstructed_grant_cannot_restore_even_same_original_lease(self):
        self.release();self.f.clock[0]+=2
        grant=self.fresh._handoff.claim(self.f.group,self.h.proof,self.request)
        self.assertNotIn(self.h.proof,repr(grant))
        for invalid in (replace(grant),grant.lease,dict(lease=grant.lease)):
            with self.assertRaises(DraftHeld):self.fresh._handoff.consume(invalid,lambda _:self.fail('Forged grant'))
        foreign=PostPreviewHandoffClient(self.f.client)
        with self.assertRaises(DraftHeld):foreign.consume(grant,lambda _:self.fail('Cross-client grant'))
        self.assertEqual('paid_hold',self.fresh.recover_original_owed(grant)['phase'])
        with self.assertRaises(DraftHeld):self.fresh.recover_original_owed(grant)

    def test_expired_genuine_grant_is_held_and_cannot_reveal_private_snapshot(self):
        self.release();self.f.clock[0]+=2
        grant=self.fresh._handoff.claim(self.f.group,self.h.proof,self.request)
        with patch('photobooth.post_preview_handoff_client.time.monotonic',return_value=grant.observed_at+31):
            with self.assertRaises(DraftHeld):self.fresh.recover_original_owed(grant)
        self.assertEqual({'phase':'hold'},self.fresh.snapshot());self.assertIsNone(self.fresh.lease)

    def test_original_media_tamper_after_paid_grant_holds_without_print_or_charge(self):
        self.release();self.f.clock[0]+=2
        grant=self.fresh._handoff.claim(self.f.group,self.h.proof,self.request)
        photo=next((self.f.root/'media').rglob('photo_01.jpg'))
        photo.write_bytes(b'Synthetic original hash mismatch')
        sends=len(self.f.sends)
        with self.assertRaises(DraftHeld):self.fresh.recover_original_owed(grant)
        self.assertEqual({'phase':'hold'},self.fresh.snapshot());self.assertIsNone(self.fresh.lease)
        self.assertEqual(sends,len(self.f.sends));self.assertEqual(1,self.f.remote.charges)

    def test_stale_owner_after_genuine_grant_cannot_restore_original_pixels(self):
        self.release();self.f.clock[0]+=2
        grant=self.fresh._handoff.claim(self.f.group,self.h.proof,self.request)
        self.f.ledger.db.execute('UPDATE pp_drafts SET generation=generation+1')
        with self.assertRaises(DraftHeld):self.fresh.recover_original_owed(grant)
        self.assertEqual({'phase':'hold'},self.fresh.snapshot());self.assertIsNone(self.fresh.lease)

    def test_valid_shaped_http_lease_without_durable_original_result_cannot_restore(self):
        self.release()
        self.assertEqual('REACQUIRED',self.h.recover()['state'])
        response=self.response()
        with patch.object(self.f.client._transport,'_call',return_value=response):
            with self.assertRaises(DraftHeld):self.claim()
        self.assertEqual({'phase':'hold'},self.fresh.snapshot());self.assertIsNone(self.fresh.lease)
        self.assertEqual((0,4),tuple(self.f.ledger.db.execute('SELECT closed,generation FROM pp_drafts').fetchone()))

    def test_lost_original_ack_reply_retries_same_operation_without_another_release(self):
        client=self.fresh._handoff;self.f.clock[0]+=2
        operation=client.prepare(replace(self.f.lease,generation=2))
        self.h.native.publish(operation.operation_id,timeout=1)
        self.f.clock[0]+=2;self.adapter.lose_response=True
        with self.assertRaises(DraftHeld):client.acknowledge(operation)
        self.assertEqual((1,3),tuple(self.f.ledger.db.execute('SELECT closed,generation FROM pp_drafts').fetchone()))
        accepted=client.acknowledge(operation)
        self.assertEqual(operation.operation_id,accepted.operation_id)
        with self.assertRaises(DraftHeld):client.acknowledge(replace(accepted))
        self.assertEqual((1,3),tuple(self.f.ledger.db.execute('SELECT closed,generation FROM pp_drafts').fetchone()))

    def test_cross_scope_release_and_caller_ready_flags_never_become_ack_observation(self):
        lease=replace(self.f.lease,generation=2)
        valid=dict(kind='ORIGINAL_ISOLATION',operation_id='a'*32,booth_id='PB001',
            draft_id=lease.draft_id,visit_id=lease.visit_id,generation=2,state='PREPARED',
            mode='sandbox',order_version='post_preview_v1')
        for response in (dict(valid,generation=True),dict(valid,visit_id='foreign'),
                dict(valid,booth_id='PB002'),dict(valid,state='ACKED'),dict(valid,worker_ready=True)):
            with patch.object(self.f.client._transport,'_call',return_value=response):
                with self.assertRaises(DraftHeld):self.fresh._handoff.prepare(lease)
                self.assertIsNone(self.fresh._handoff._operation)

    def test_actual_original_photojobs_restores_without_storing_or_returning_customer_proof(self):
        from photobooth.kiosk_v2.photos import PhotoJobs
        self.release();self.f.clock[0]+=2
        jobs=PhotoJobs(self.fresh)
        self.assertTrue(jobs.submit('claim_original',self.f.group,self.h.proof,self.request))
        jobs._thread.join(5);self.assertFalse(jobs._thread.is_alive())
        outcome=jobs.poll();self.assertIsNone(outcome.error)
        self.assertEqual('paid_hold',outcome.value['phase'])
        self.assertNotIn(self.h.proof,repr(outcome))
        self.assertNotIn(self.h.proof,repr(vars(self.fresh._handoff)))
        self.assertEqual(4,self.fresh.lease.generation)
        self.assertTrue(jobs.retire(timeout=1))

    def test_owner_change_during_payment_inspect_is_rechecked_before_restored_snapshot(self):
        self.release();self.f.clock[0]+=2
        grant=self.fresh._handoff.claim(self.f.group,self.h.proof,self.request)
        original=self.f.client.inspect
        def changed(group):
            result=original(group)
            self.f.ledger.db.execute('UPDATE pp_drafts SET generation=generation+1')
            return result
        with patch.object(self.f.client,'inspect',side_effect=changed):
            with self.assertRaises(DraftHeld):self.fresh.recover_original_owed(grant)
        self.assertEqual({'phase':'hold'},self.fresh.snapshot())
        self.assertEqual(5,self.f.ledger.db.execute('SELECT generation FROM pp_drafts').fetchone()[0])

    def response(self):
        return dict(kind='ORIGINAL_CLAIM',request_id=self.request,purchase_group_id=self.f.group,
            booth_id='PB001',mode='sandbox',order_version='post_preview_v1',state='REACQUIRED',
            lease=dict(draft_id=self.f.lease.draft_id,booth_id='PB001',visit_id=self.f.lease.visit_id,generation=4),
            entitlement_id=self.h.payments.inspect(self.f.group,'PB001')['entitlement_id'],service_still_owed=True)

    def test_malformed_cross_scope_and_paid_flags_cannot_issue_any_claim_grant(self):
        valid=self.response()
        mutations=[dict(valid,request_id='a'*32),dict(valid,purchase_group_id='a'*32),
            dict(valid,booth_id='PB002'),dict(valid,mode='mock'),dict(valid,service_still_owed=1),
            dict(valid,fulfillment_authorized=True),dict(valid,entitlement_id='bad'),
            dict(valid,lease=dict(valid['lease'],generation=True)),
            dict(valid,lease=dict(valid['lease'],booth_id='PB002')),
            dict(valid,state='WAIT',reason='BOOTH_BUSY')]
        for response in mutations:
            with self.subTest(fields=set(response)),patch.object(self.f.client._transport,'_call',return_value=response):
                with self.assertRaises(DraftHeld):self.fresh._handoff.claim(self.f.group,self.h.proof,self.request)
                self.assertIsNone(self.fresh._handoff._grant)
        self.assertIsNone(self.fresh.lease)

    def test_hidden_inflight_claim_returns_no_grant_and_privacy_hide_never_waits_for_network(self):
        self.release();self.f.clock[0]+=2
        original=self.f.client._transport._call
        entered=threading.Event();release=threading.Event();outcomes=[]
        def blocked(*args,**kwargs):
            result=original(*args,**kwargs);entered.set();release.wait(5);return result
        def claim():
            try:outcomes.append(self.fresh.claim_original(self.f.group,self.h.proof,self.request))
            except DraftHeld:outcomes.append('HELD')
        with patch.object(self.f.client._transport,'_call',side_effect=blocked):
            worker=threading.Thread(target=claim);worker.start()
            try:
                self.assertTrue(entered.wait(3))
                start=time.monotonic();self.fresh.hide_private()
                self.assertLess(time.monotonic()-start,.2)
                self.assertEqual({'phase':'hold'},self.fresh.snapshot())
            finally:release.set();worker.join(6)
        self.assertFalse(worker.is_alive());self.assertEqual(['HELD'],outcomes)
        self.assertIsNone(self.fresh.lease);self.assertIsNone(self.fresh._handoff._grant)


if __name__=='__main__':unittest.main()
