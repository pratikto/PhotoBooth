"""Exact original worker retirement, not a caller-supplied readiness flag."""
from dataclasses import replace
import json
import socket
import sqlite3
import threading
import unittest
import uuid
from unittest.mock import patch

from photobooth.post_preview_worker_fence import (
    WorkerFenceKey, NativeWorkerRetirement, WorkerReceiptVerifier, install_worker_receipts)
from photobooth.post_preview_store import DraftHeld,PostPreviewStore
from photobooth.post_preview_checkout import PrivateDraftCheckout
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_authority import OriginalWorkerReadiness
from photobooth.post_preview_readiness import LocalChargeReadiness
from photobooth.post_preview_readiness_bridge import WorkerReadinessServer,WorkerReadinessClient
from photobooth.checkout_store import CheckoutStore
from tests.post_preview_protected_fixture import ProtectedNativeHarness


class WorkerFenceKeyTests(unittest.TestCase):
    def test_private_capability_never_appears_in_repr(self):
        key=WorkerFenceKey.create()
        self.assertNotIn(key.secret.hex(),repr(key))
        self.assertEqual(32,len(key.secret))


class WorkerFenceTests(unittest.TestCase):
    def setUp(self):
        self.f=ProtectedNativeHarness(self,{'template_a':1})
        self.f.ticket()
        self.service=self.f.service
        # SAME original file, distinct actual native/backend SQL connections.
        native=PostPreviewStore(self.f.root/'drafts.sqlite3',now=lambda:self.f.clock[0])
        self.addCleanup(native.close)
        self.service.ledger=native
        self.service.photos=PrivateDraftPhotos(native,self.f.root/'media')
        self.service.checkout=PrivateDraftCheckout(self.service.photos)
        self.jobs=PhotoJobs(self.service)
        self.launcher=LaunchLease(self.f.root);self.addCleanup(self.launcher.close)
        legacy=CheckoutStore(self.f.root/'legacy.sqlite3');self.addCleanup(legacy.close)
        self.authority=OriginalWorkerReadiness(self.service,self.jobs,self.launcher,legacy)
        self.collector=LocalChargeReadiness(self.service.checkout,self.f.templates,
            probes={'worker_ownership':self.authority})
        worker,backend=socket.socketpair()
        self.server=WorkerReadinessServer.from_original_worker(worker,self.collector)
        self.server.start();self.addCleanup(self.server.stop)
        self.client=WorkerReadinessClient(backend,timeout=2);self.addCleanup(self.client.close)
        self.key=WorkerFenceKey.create()
        install_worker_receipts(self.f.ledger)
        self.issuer=NativeWorkerRetirement(self.jobs,self.server,self.launcher,self.key)
        self.verifier=WorkerReceiptVerifier(self.f.ledger,self.key)
        self.service.retire('RESULT_TIMEOUT')
        self.operation=uuid.uuid4().hex
        # Explicit PREPARED fixture only. Backend preparation/ACK is the NEXT
        # increment; no test fixture row enables a customer merchant profile.
        self.f.ledger.db.execute('''INSERT INTO pp_isolation_ops
            (draft_id,operation_id,booth_id,original_generation,financial_class,state,prepared_at)
            VALUES(?,?,'PB001',2,'PAID_OWED','PREPARED',?)''',
            (self.f.lease.draft_id,self.operation,self.f.clock[0]))

    def count(self):
        return self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_worker_retirements').fetchone()[0]

    def test_original_retirement_is_signed_once_without_backend_ack_or_closed_db(self):
        self.assertEqual(self.operation,self.issuer.publish(self.operation,timeout=1))
        receipt=self.verifier.verify(self.operation)
        self.assertIsNone(receipt['backend_verified_at'])
        self.assertEqual(1,self.count())
        self.assertFalse(self.server._thread.is_alive())
        self.assertFalse(self.jobs.submit('snapshot'))
        self.f.clock[0]+=1
        self.issuer.publish(self.operation)
        self.assertEqual(receipt,self.verifier.verify(self.operation))
        self.assertEqual('PREPARED',self.f.ledger.db.execute('SELECT state FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual(0,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual(1,self.f.remote.charges)
        self.assertNotIn(self.key.secret.hex(),json.dumps(dict(receipt)))

    def test_still_active_collector_cannot_publish_a_worker_receipt(self):
        from tests.test_post_preview_readiness import _bridge_ready
        entered,release=threading.Event(),threading.Event()
        scope=self.f.service.checkout.ledger.db.execute(
            'SELECT contract_sha256 FROM pp_checkout_intents').fetchone()[0]
        from photobooth.post_preview_readiness import ReadinessScope
        actual=ReadinessScope(self.f.group,'PB001',scope,1)
        def blocked(_collector,group):
            entered.set();release.wait(5)
            return _bridge_ready(actual,self.f.clock[0])
        with patch.object(LocalChargeReadiness,'__call__',new=blocked):
            observer=threading.Thread(target=lambda:self.client.observe(actual))
            observer.start()
            try:
                self.assertTrue(entered.wait(2))
                with self.assertRaises(DraftHeld):self.issuer.publish(self.operation)
                self.assertTrue(self.server._thread.is_alive());self.assertEqual(0,self.count())
            finally:release.set();observer.join(5)
        self.issuer.publish(self.operation,timeout=1)
        self.assertEqual(1,self.count())

    def test_still_active_photo_worker_never_loses_sqlite_or_creates_receipt(self):
        self.assertTrue(self.server.stop(timeout=1))
        entered,release=threading.Event(),threading.Event()
        original=self.service.snapshot
        def blocked():entered.set();release.wait(5);return original()
        with patch.object(self.service,'snapshot',side_effect=blocked):
            self.assertTrue(self.jobs.submit('snapshot'))
            try:
                self.assertTrue(entered.wait(2))
                with self.assertRaises(DraftHeld):self.issuer.publish(self.operation)
                self.assertFalse(self.jobs.submit('snapshot'))
                self.assertEqual(0,self.count())
                self.assertEqual(1,self.service.ledger.db.execute('SELECT COUNT(*) FROM pp_drafts').fetchone()[0])
            finally:release.set();self.jobs.wait_closed(5)
        self.issuer.publish(self.operation)
        self.assertEqual(1,self.count())
        self.assertIsNone(self.jobs.poll())

    def test_foreign_capability_and_mutating_signed_receipt_are_denied(self):
        self.issuer.publish(self.operation,timeout=1)
        with self.assertRaises(DraftHeld):
            WorkerReceiptVerifier(self.f.ledger,WorkerFenceKey.create()).verify(self.operation)
        for sql in ("UPDATE pp_worker_retirements SET mac='"+'0'*64+"'",
                    'DELETE FROM pp_worker_retirements',
                    'UPDATE pp_worker_retirements SET frame_json=\'{}\''):
            with self.assertRaises(sqlite3.IntegrityError):self.f.ledger.db.execute(sql)
        self.assertEqual(1,self.count())

    def test_forged_preexisting_receipt_is_not_replaced_or_accepted(self):
        self.f.ledger.db.execute('INSERT INTO pp_worker_retirements '
            '(operation_id,key_id,frame_json,mac) VALUES(?,?,?,?)',
            (self.operation,self.key.key_id,'{}','0'*64))
        with self.assertRaises(DraftHeld):self.verifier.verify(self.operation)
        with self.assertRaises(DraftHeld):self.issuer.publish(self.operation,timeout=1)
        self.assertEqual('{}',self.f.ledger.db.execute('SELECT frame_json FROM pp_worker_retirements').fetchone()[0])

    def test_wrong_generation_or_closed_kernel_lease_cannot_retire_original(self):
        original=self.service.lease
        self.service.lease=replace(original,generation=2)
        with self.assertRaises(DraftHeld):self.issuer.publish(self.operation)
        self.service.lease=original
        self.launcher.close()
        with self.assertRaises(DraftHeld):self.issuer.publish(self.operation)
        self.assertEqual(0,self.count())

    def test_unbound_collector_cannot_supply_a_retirement_authority(self):
        worker,backend=socket.socketpair();self.addCleanup(backend.close)
        unrelated=WorkerReadinessServer(worker,lambda _:None);self.addCleanup(unrelated.stop)
        with self.assertRaises(DraftHeld):
            NativeWorkerRetirement(self.jobs,unrelated,self.launcher,self.key)

    def test_no_ack_receipt_while_original_visit_is_live(self):
        self.service._hidden.clear()
        with self.assertRaises(DraftHeld):self.issuer.publish(self.operation)
        self.assertEqual(0,self.count())

    def test_invalid_retirement_deadlines_and_unknown_operations_have_no_effect(self):
        for timeout in (True,-1,6,float('nan')):
            with self.assertRaises(ValueError):self.issuer.publish(self.operation,timeout=timeout)
        with self.assertRaises(DraftHeld):self.issuer.publish('a'*32)
        self.assertEqual(0,self.count())

    def test_even_authenticated_wrong_scope_or_timestamps_cannot_ack_another_operation(self):
        self.issuer.publish(self.operation,timeout=1)
        frame=json.loads(self.verifier.verify(self.operation)['frame_json'])
        for change in ({'booth_id':'PB002'},{'generation':True},{'version':True},
                       {'visit_id':'visitorB'},{'purchase_group_id':'a'*32},
                       {'observed_at':self.f.clock[0]+1},{'observed_at':self.f.clock[0]-1},
                       {'closed':True}):
            key=WorkerFenceKey.create()
            forged=dict(frame,key_id=key.key_id,**change)
            from photobooth.post_preview_worker_fence import canonical
            self.f.ledger.db.execute('INSERT INTO pp_worker_retirements '
                '(operation_id,key_id,frame_json,mac) VALUES(?,?,?,?)',
                (self.operation,key.key_id,canonical(forged),key.sign(forged)))
            with self.subTest(fields=tuple(change)),self.assertRaises(DraftHeld):
                WorkerReceiptVerifier(self.f.ledger,key).verify(self.operation)

    def test_partially_existing_receipt_schema_is_preserved_and_held(self):
        for index,ddl in enumerate(('original TEXT',
                'operation_id TEXT,key_id TEXT,frame_json TEXT,mac TEXT,backend_verified_at REAL')):
            ledger=PostPreviewStore(self.f.root/('partial%s.sqlite3'%index));self.addCleanup(ledger.close)
            ledger.db.execute('CREATE TABLE pp_worker_retirements ('+ddl+')')
            first='original' if index==0 else 'operation_id'
            ledger.db.execute('INSERT INTO pp_worker_retirements ('+first+") VALUES('preserved')")
            with self.subTest(shape=index),self.assertRaises(DraftHeld):install_worker_receipts(ledger)
            self.assertEqual('preserved',ledger.db.execute('SELECT '+first+' FROM pp_worker_retirements').fetchone()[0])

    def test_submit_and_retire_are_serialized_before_actual_worker_drain(self):
        start_entered,start_release=threading.Event(),threading.Event()
        work_entered,work_release=threading.Event(),threading.Event()
        results=[]
        original_start=threading.Thread.start
        def start(thread):
            if thread.name=='portrait-v2-photo-io':
                start_entered.set();start_release.wait(5)
            return original_start(thread)
        def blocked():work_entered.set();work_release.wait(5);return {'phase':'hold'}
        with patch.object(threading.Thread,'start',new=start),patch.object(self.service,'snapshot',side_effect=blocked):
            submitter=threading.Thread(target=lambda:self.jobs.submit('snapshot'))
            submitter.start()
            retiree=None
            try:
                self.assertTrue(start_entered.wait(2))
                retiree=threading.Thread(target=lambda:results.append(self.jobs.retire()))
                retiree.start()
                start_release.set()
                self.assertTrue(work_entered.wait(2))
                submitter.join(2);retiree.join(2)
                self.assertEqual([False],results)
                self.assertFalse(self.jobs.submit('snapshot'))
            finally:
                start_release.set();work_release.set();submitter.join(5)
                if retiree is not None:retiree.join(5)
                self.jobs.wait_closed(5)
        self.assertTrue(self.jobs.retire())
        self.assertIsNone(self.jobs.poll())


if __name__=='__main__':unittest.main()
