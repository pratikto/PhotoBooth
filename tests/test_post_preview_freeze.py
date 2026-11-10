"""Original pre-freeze candidate/private worker evidence; external I/O fake."""
from dataclasses import replace
import json
import socket
import sqlite3
import threading
import unittest
from unittest.mock import patch

from photobooth.catalog import get_templates
from photobooth.capture_journal import CaptureRecoveryRequired
from photobooth.post_preview_readiness import (FreezeScope,ReadinessScope,CheckObservation,
    TrustedChargeReadiness,TrustedFreezeReadiness,REQUIRED_CHECKS)
from photobooth.post_preview_readiness_bridge import WorkerReadinessClient,WorkerReadinessServer,LOCAL_CHECKS
from photobooth.post_preview_store import DraftHeld
from tests import test_post_preview_checkout as checkout_fixtures
from tests import test_post_preview_sandbox_visits as visit_fixtures


class FreezeCandidateTests(unittest.TestCase):
    def setUp(self):
        self.f=checkout_fixtures.PreviewFreezeTests();self.f.setUp()
        self.addCleanup(self.f.doCleanups)
    def scope(self,**kwargs):
        args=dict(revision=self.f.revision(),expected_amount=25000);args.update(kwargs)
        return self.f.checkout.freeze_scope(self.f.lease,self.f.templates,**args)
    def empty_intents(self):
        self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
    def test_candidate_binds_original_approved_bytes_without_creating_group_or_changing_journals(self):
        self.f.approve_all();before=self.f.ledger.db.total_changes
        scope=self.scope();self.assertEqual(scope,self.scope())
        self.assertEqual(before,self.f.ledger.db.total_changes);self.empty_intents()
        self.assertEqual('OPEN',self.f.ledger.inspect(self.f.lease)['state'])
        result=self.f.freeze(expected_contract_sha256=scope.contract_sha256)
        self.assertEqual(result['contract_sha256'],scope.contract_sha256)
        self.assertEqual({'template_a':2,'template_b':1},json.loads(result['contract_json'])['quantities'])
    def test_every_design_and_exact_quote_revision_owner_are_required_before_candidate(self):
        with self.assertRaises(DraftHeld):self.scope()
        self.f.approve_all();original=self.scope()
        for args in ({'expected_amount':True},{'expected_amount':24999},{'revision':original.revision+1}):
            with self.subTest(args=args),self.assertRaises(DraftHeld):self.scope(**args)
        self.f.ledger.lifecycle_event(self.f.lease,'APP_SUSPENDED')
        with self.assertRaises(DraftHeld):self.scope()
        self.empty_intents()
    def test_candidate_drift_cannot_cross_atomic_create_prepared(self):
        self.f.approve_all();scope=self.scope()
        with self.assertRaises(DraftHeld):self.f.freeze(expected_contract_sha256='0'*64)
        self.empty_intents()
        self.f.ledger.edit(self.f.lease,{'template_a':1,'template_b':1},revision=self.f.revision())
        with self.assertRaises(DraftHeld):self.f.freeze(revision=scope.revision,
            expected_contract_sha256=scope.contract_sha256)
        self.empty_intents()
    def test_lost_freeze_response_reinspects_exact_original_intent_without_another_group(self):
        self.f.approve_all();scope=self.scope();intent=self.f.freeze(expected_contract_sha256=scope.contract_sha256)
        self.assertEqual(scope,self.scope())
        self.assertEqual(intent,self.f.freeze(expected_contract_sha256=scope.contract_sha256))
        self.assertEqual(1,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
        with self.assertRaises(DraftHeld):self.f.freeze(expected_contract_sha256='0'*64)
    def test_media_corruption_holds_candidate_without_repair_or_freeze(self):
        self.f.approve_all();media=self.f.photos.inspect(self.f.lease,self.f.a)
        manifest=json.loads(media['manifest_path'].read_text())
        path=media['manifest_path'].parent/manifest['sessions'][0]['raw_photos'][0]['path']
        path.write_bytes(b'corrupt original fixture')
        with self.assertRaises((CaptureRecoveryRequired,DraftHeld,OSError,ValueError)):self.scope()
        self.assertEqual(b'corrupt original fixture',path.read_bytes());self.empty_intents()
    def test_retirement_during_existing_frozen_reinspection_cannot_return_a_live_candidate(self):
        self.f.approve_all();self.f.freeze();original=self.f.checkout.verify_frozen
        def retired(*args):
            result=original(*args)
            self.f.ledger.lifecycle_event(self.f.lease,'APP_SUSPENDED')
            return result
        with patch.object(self.f.checkout,'verify_frozen',side_effect=retired):
            with self.assertRaises(DraftHeld):self.scope()
    def test_existing_intent_bytes_cannot_change_under_candidate_hash(self):
        self.f.approve_all();scope=self.scope();intent=self.f.freeze()
        contract=json.loads(intent['contract_json']);contract['quantities']['template_a']=1
        with self.assertRaises(sqlite3.IntegrityError):
            self.f.ledger.db.execute('UPDATE pp_checkout_intents SET contract_json=?',(json.dumps(contract),))
        self.assertEqual(scope,self.scope())
        self.assertEqual(intent,self.f.freeze(expected_contract_sha256=scope.contract_sha256))
    def test_freeze_and_charge_reports_cannot_authorize_each_other_or_stale_wrong_scope(self):
        self.f.approve_all();scope=self.scope();now=1000.
        probes={name:lambda _:CheckObservation('READY',now) for name in REQUIRED_CHECKS}
        report=TrustedFreezeReadiness.observe(scope,probes);report.require(scope,now=now)
        charge=ReadinessScope('a'*32,scope.booth_id,scope.contract_sha256,scope.generation)
        for expected in (charge,replace(scope,visit_id='another'),replace(scope,amount=1),replace(scope,revision=scope.revision+1)):
            with self.assertRaises(DraftHeld):report.require(expected,now=now)
        with self.assertRaises(DraftHeld):TrustedChargeReadiness.observe(scope,probes).require(scope,now=now)
        with self.assertRaises(DraftHeld):report.require(scope,now=now+3)
        probes['drive_api']=lambda _:True
        with self.assertRaises(DraftHeld):TrustedFreezeReadiness.observe(scope,probes).require(scope,now=now)
        self.empty_intents()
    def test_pre_freeze_scope_rejects_boolean_numbers_and_malformed_hash(self):
        self.f.approve_all();scope=self.scope()
        for args in ({'generation':True},{'revision':0},{'amount':True},{'contract_sha256':'not-a-hash'}):
            with self.subTest(args=args),self.assertRaises(ValueError):replace(scope,**args)


class OriginalFreezeWorkerTests(unittest.TestCase):
    def setUp(self):
        self.f=visit_fixtures.OriginalSandboxVisitTests();self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.service=self.f.binding.service;self.jobs=self.f.binding.jobs
        self.service.start(get_templates(),{'template_a':2,'template_b':1})
        for _ in range(len(self.service.selected)):
            for _ in range(3):
                v=self.service.snapshot();self.service.capture(self.f.frame,v['capture_slot'],v['revision'],v['retake'],v['generation'])
            self.service.compose();self.service.next()
        v=self.service.snapshot();self.scope=self.service.checkout.freeze_scope(self.service.lease,
            self.service.templates,revision=v['revision'],expected_amount=v['amount'])
        self.collector=self.f.visits._server._original_collector
        native,child=socket.socketpair()
        self.server=WorkerReadinessServer.from_original_worker(native,self.collector);self.server.start()
        self.bridge=WorkerReadinessClient(child,timeout=2)
        self.addCleanup(self.server.stop);self.addCleanup(self.bridge.close)
    def busy_freeze(self):
        entered,release=threading.Event(),threading.Event()
        def held(*_args):entered.set();release.wait(8);return {'phase':'hold'}
        patched=patch.object(self.service,'freeze_checkout',side_effect=held);patched.start()
        self.addCleanup(patched.stop)
        self.addCleanup(self.jobs.retire,timeout=5);self.addCleanup(release.set)
        self.assertTrue(self.jobs.submit('freeze_checkout',self.scope.revision,self.scope.amount))
        self.assertTrue(entered.wait(2))
        return release
    def assert_no_intent(self):
        self.assertEqual(0,self.service.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])
    def test_private_original_worker_checks_final_preview_scope_and_actual_freeze_action(self):
        idle=self.bridge.observe(self.scope)
        self.assertEqual('NOT_READY',idle['worker_ownership'].state)
        self.busy_freeze()
        values=self.bridge.observe(self.scope)
        self.assertEqual(LOCAL_CHECKS,set(values))
        self.assertTrue(all(v.state=='READY' for v in values.values()),values)
        self.assert_no_intent()
    def test_wrong_private_candidate_and_privacy_never_assert_readiness_or_freeze(self):
        self.busy_freeze()
        for scope in (replace(self.scope,contract_sha256='0'*64),replace(self.scope,visit_id='foreign'),
                      replace(self.scope,generation=self.scope.generation+1),replace(self.scope,amount=1)):
            with self.subTest(scope=scope):
                self.assertTrue(all(v.state=='UNKNOWN' for v in self.bridge.observe(scope).values()))
        self.service.hide_private()
        self.assertEqual('NOT_READY',self.bridge.observe(self.scope)['worker_ownership'].state)
        self.assert_no_intent()
    def test_closed_original_launcher_cannot_assert_pre_freeze_worker_ownership(self):
        self.busy_freeze();self.f.visits._launcher.close()
        self.assertEqual('NOT_READY',self.bridge.observe(self.scope)['worker_ownership'].state)
        self.assert_no_intent()
