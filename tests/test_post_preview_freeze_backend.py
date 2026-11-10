"""Authenticated original backend freeze, actual child/PhotoJobs; external I/O fake."""
from dataclasses import replace
import socket
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from photobooth.catalog import get_templates
from photobooth.post_preview_authority import authenticated_freeze_request,authenticated_freeze_readiness,authenticated_payment_readiness
from photobooth.post_preview_freeze import OriginalSandboxFreeze
from photobooth.post_preview_readiness import CheckObservation,TrustedFreezeReadiness,REQUIRED_CHECKS,ReadinessScope
from photobooth.post_preview_readiness_bridge import BackendChargeReadiness,WorkerReadinessClient,WorkerReadinessServer,DRIVE_CHECKS
from photobooth.post_preview_store import DraftHeld
from tests import test_post_preview_checkout as checkout_fixtures
from tests import test_post_preview_sandbox_visits as visit_fixtures


class OriginalFreezeCommitTests(unittest.TestCase):
    def setUp(self):
        self.f=checkout_fixtures.PreviewFreezeTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.f.approve_all();self.clock=[1000.];self.f.ledger.now=lambda:self.clock[0]
        self.scope=self.f.checkout.freeze_scope(self.f.lease,self.f.templates,
            revision=self.f.revision(),expected_amount=25000)
        native,backend=socket.socketpair()
        probes={name:lambda _:CheckObservation('READY',self.clock[0]) for name in REQUIRED_CHECKS}
        self.server=WorkerReadinessServer(native,lambda scope:TrustedFreezeReadiness.observe(scope,probes))
        self.server.start();self.addCleanup(self.server.stop)
        bridge=WorkerReadinessClient(backend,timeout=2);self.addCleanup(bridge.close)
        self.drive=SimpleNamespace(observe=lambda scope:{name:CheckObservation('READY',self.clock[0]) for name in DRIVE_CHECKS})
        readiness=BackendChargeReadiness(self.f.checkout,self.f.templates,bridge,drive_probe=self.drive)
        self.coordinator=OriginalSandboxFreeze(self.f.checkout,self.f.templates,readiness,'PB001')
    def freeze(self):
        return self.coordinator.freeze(self.f.lease,revision=self.scope.revision,
            expected_amount=self.scope.amount,expected_scope=self.scope)
    def empty(self):self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
    def test_freeze_authorization_is_independent_of_charge_and_always_retired(self):
        with self.assertRaises(DraftHeld):self.freeze()
        self.empty()
        charge=ReadinessScope('a'*32,'PB001',self.scope.contract_sha256,self.scope.generation)
        with authenticated_freeze_request(self.scope,self.clock[0]):
            self.assertEqual('READY',authenticated_freeze_readiness(self.scope).state)
            self.assertEqual('UNKNOWN',authenticated_payment_readiness(charge).state)
            result=self.freeze()
        self.assertEqual('CREATE_PREPARED',result['phase'])
        self.assertEqual('UNKNOWN',authenticated_freeze_readiness(self.scope).state)
    def test_staleness_during_atomic_media_io_rolls_back_without_an_intent(self):
        original_freeze=self.f.checkout.freeze;original_preview=self.f.checkout._preview
        def delayed_preview(*args):
            result=original_preview(*args);self.clock[0]+=3;return result
        def delayed_freeze(*args,**kwargs):
            with patch.object(self.f.checkout,'_preview',side_effect=delayed_preview):
                return original_freeze(*args,**kwargs)
        with authenticated_freeze_request(self.scope,self.clock[0]),patch.object(
                self.f.checkout,'freeze',side_effect=delayed_freeze):
            with self.assertRaises(DraftHeld):self.freeze()
        self.empty();self.assertEqual('OPEN',self.f.ledger.inspect(self.f.lease)['state'])
    def test_backend_drive_unknown_or_wrong_request_scope_never_freezes(self):
        with authenticated_freeze_request(replace(self.scope,visit_id='foreign'),self.clock[0]):
            with self.assertRaises(DraftHeld):self.freeze()
        self.drive.observe=lambda scope:{name:CheckObservation('UNKNOWN',None) for name in DRIVE_CHECKS}
        with authenticated_freeze_request(self.scope,self.clock[0]):
            with self.assertRaises(DraftHeld):self.freeze()
        self.empty()


class OriginalFreezeBackendTests(unittest.TestCase):
    def setUp(self):
        self.f=visit_fixtures.OriginalSandboxVisitTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.service=self.f.binding.service;self.jobs=self.f.binding.jobs
        self.service.start(get_templates(),{'template_a':2,'template_b':1})
        for _ in range(len(self.service.selected)):
            for _ in range(3):
                v=self.service.snapshot();self.service.capture(self.f.frame,v['capture_slot'],v['revision'],v['retake'],v['generation'])
            self.service.compose();self.service.next()
        self.view=self.service.snapshot();self.client=self.service.client
    def submit(self):
        self.assertTrue(self.jobs.submit('freeze_checkout',self.view['revision'],self.view['amount']))
        return self.outcome()
    def outcome(self):
        deadline=time.monotonic()+12
        while time.monotonic()<deadline:
            result=self.jobs.poll()
            if result is not None:return result
            time.sleep(.01)
        self.fail('Original native freeze did not finish')
    def no_money(self):
        for table in ('pp_payment_attempts','pp_purchase_finance','pp_paid_services'):
            self.assertEqual(0,self.service.ledger.db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0])
        self.assertFalse((self.f.config.private_root/'fixture-output-send-count').exists())
    def test_actual_native_freeze_and_original_ccp_offer_do_not_charge_print_or_allocate_drive(self):
        result=self.submit();self.assertIsNone(result.error)
        self.assertEqual('claim_proof',result.value['phase'])
        self.assertTrue(result.value['ccp_offer'].qr_payload.startswith('MEONG:CCP:1:PB001:'))
        self.no_money()
        self.assertEqual(1,self.service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
        self.assertEqual(1,self.service.ledger.db.execute('SELECT COUNT(*) FROM pp_ccp_credentials').fetchone()[0])
        with self.assertRaises(DraftHeld):self.service.edit()
    def test_idle_native_or_forged_flags_wrong_owner_quote_and_revision_hold_before_group_creation(self):
        with self.assertRaises(RuntimeError):self.service.freeze_checkout(self.view['revision'],self.view['amount'])
        payload=dict(visit_id=self.service.lease.visit_id,generation=self.service.lease.generation,
            revision=self.view['revision'],expected_amount=self.view['amount'])
        path='/api/postpay/drafts/'+self.service.lease.draft_id+'/freeze'
        transport=self.client._transport
        response=transport.session.post(transport.base_url+path,json=payload,
            headers={'x-booth-id':'PB001','Authorization':'Bearer wrong'},timeout=2)
        try:self.assertEqual(401,response.status_code)
        finally:response.close()
        for extra,status in (({'ready':True},422),({'generation':self.service.lease.generation+1},409),
                      ({'revision':self.view['revision']+1},409),({'expected_amount':1},409),({'expected_amount':True},422)):
            with self.subTest(extra=extra),self.assertRaisesRegex(RuntimeError,'HTTP '+str(status)):
                self.client._transport._call('POST',path,payload=dict(payload,**extra))
        self.assertEqual(0,self.service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
        self.no_money()
    def test_lost_http_freeze_reply_retries_original_group_and_keeps_photos_immutable(self):
        original=self.client._transport._call;lost=[True]
        def dropped(method,path,**kwargs):
            result=original(method,path,**kwargs)
            if path.endswith('/freeze') and lost[0]:lost[0]=False;raise OSError('Synthetic lost freeze reply')
            return result
        with patch.object(self.client._transport,'_call',side_effect=dropped):
            result=self.submit();self.assertEqual('OSError',result.error)
            group=self.service.ledger.db.execute('SELECT purchase_group_id FROM pp_checkout_intents').fetchone()[0]
            self.assertEqual('final_preview',self.service.phase);self.no_money()
            result=self.submit();self.assertIsNone(result.error);self.assertEqual(group,self.service.group)
        self.assertEqual(1,self.service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
        self.no_money()
    def test_privacy_during_committed_freeze_reply_never_offers_ccp_and_original_unpaid_visit_can_retire(self):
        original=self.client._transport._call;entered,release=threading.Event(),threading.Event()
        def blocked(method,path,**kwargs):
            result=original(method,path,**kwargs)
            if path.endswith('/freeze'):entered.set();release.wait(8)
            return result
        try:
            with patch.object(self.client._transport,'_call',side_effect=blocked):
                self.assertTrue(self.jobs.submit('freeze_checkout',self.view['revision'],self.view['amount']))
                self.assertTrue(entered.wait(5));self.service.hide_private();release.set()
                result=self.outcome();self.assertEqual({'phase':'hold'},result.value)
            self.no_money()
            self.assertEqual(0,self.service.ledger.db.execute('SELECT COUNT(*) FROM pp_ccp_credentials').fetchone()[0])
            self.f.retry(lambda:self.f.visits.retire_current('APP_SUSPENDED'))
            binding=self.f.retry(self.f.visits.ensure_new_visitor_ready)
            self.assertIsNone(binding.service.lease)
            self.assertEqual(1,binding.service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
        finally:release.set()
    def test_client_binds_complete_typed_freeze_response_and_native_requires_original_durable_intent(self):
        scope=self.service.checkout.freeze_scope(self.service.lease,self.service.templates,
            revision=self.view['revision'],expected_amount=self.view['amount'])
        response=dict(kind='FROZEN_CHECKOUT',purchase_group_id='a'*32,draft_id=scope.draft_id,
            booth_id=scope.booth_id,visit_id=scope.visit_id,generation=scope.generation,
            revision=scope.revision,amount=scope.amount,mode='sandbox',order_version='post_preview_v1',
            phase='CREATE_PREPARED',fulfillment_authorized=False,contract_sha256=scope.contract_sha256)
        for change in ({'amount':True},{'mode':'mock'},{'booth_id':'PB002'},{'generation':True},
                       {'purchase_group_id':'foreign'},{'contract_sha256':'bad'},{'ready':True}):
            with patch.object(self.client._transport,'_call',return_value=dict(response,**change)):
                with self.subTest(change=change),self.assertRaises(ValueError):
                    self.client.freeze_checkout(self.service.lease,revision=scope.revision,expected_amount=scope.amount)
        with patch.object(self.client._transport,'_call',return_value=response):
            result=self.submit();self.assertEqual('DraftHeld',result.error)
        self.assertIsNone(self.service.group);self.no_money()
