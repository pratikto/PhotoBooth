"""Trusted original manager with actual child replacement; external effects fake."""
import hashlib
from contextlib import closing
from dataclasses import replace
import sqlite3
from pathlib import Path
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from photobooth.catalog import get_templates
from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.health_service import CachedCamera
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_sandbox_visits import OriginalSandboxVisits,NativeVisitBinding
from photobooth.post_preview_store import DraftHeld
from photobooth.printer import PrinterConfig


class OriginalSandboxVisitTests(unittest.TestCase):
    def test_witness_sync_failure_withholds_start_and_retains_original_handles(self):
        import photobooth.post_preview_bootstrap as bootstrap
        self.shutdown(self.visits)
        manager = self.manager(); self.addCleanup(self.shutdown, manager)
        original = bootstrap._send; sent = []
        def send(channel, frame, deadline):
            sent.append(frame['kind'])  # Static kind only, never key/config/proof.
            return original(channel, frame, deadline)
        with patch.object(bootstrap, '_send', side_effect=send), patch(
                'photobooth.post_preview_worker_start.os.fsync', side_effect=OSError('PRIVATE IO DETAIL')):
            with self.assertRaises(DraftHeld): manager.start()
        self.assertNotIn('START', sent)
        self.assertIsNotNone(manager._backend)
        self.assertIsNone(manager._backend._worker_start_frame)
        self.assertFalse(manager._admitted)
        path = self.config.private_root/'worker-starts'/(manager._key.key_id+'.json')
        self.assertTrue(path.is_file())
        with self.assertRaises(OSError): LaunchLease(self.config.private_root)
        process = manager._backend.process
        self.shutdown(manager)
        self.assertIsNotNone(process.poll())
        self.assertTrue(path.is_file())

    def test_original_child_identity_is_durable_before_private_start(self):
        import photobooth.post_preview_bootstrap as bootstrap
        self.shutdown(self.visits)
        manager = self.manager(); self.addCleanup(self.shutdown, manager)
        original = bootstrap._send
        observed = []
        def send(channel, frame, deadline):
            if frame.get('kind') == 'START':
                key_id = frame['fulfillment']['worker_key']['key_id']
                observed.append((self.config.private_root/'worker-starts'/(key_id+'.json')).is_file())
            return original(channel, frame, deadline)
        with patch.object(bootstrap, '_send', side_effect=send):
            manager.start()
        self.assertEqual([True], observed, 'Original witness must precede private START')

    def saved_row(self, query, parameters=()):
        path = self.config.private_root/'drafts.sqlite3'
        with closing(sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)) as db:
            db.row_factory = sqlite3.Row
            row = db.execute(query, parameters).fetchone()
            return dict(row) if row else None

    def test_constructor_validates_original_printer_without_minting_a_key(self):
        self.shutdown(self.visits)
        with patch('photobooth.post_preview_sandbox_visits.WorkerFenceKey.create',
                   side_effect=AssertionError('Validation is not an epoch')) as mint:
            manager = self.manager()
            self.addCleanup(self.shutdown, manager)
            self.assertEqual(0, mint.call_count)
        self.assertIsNone(manager._key)

    def test_unacked_boot_holds_before_minting_a_replacement_key_or_child(self):
        service = self.binding.service
        service.start(get_templates(), {'template_a': 1})
        service.retire('USER_CANCEL')
        draft = dict(service.ledger.db.execute('SELECT * FROM pp_drafts').fetchone())
        self.shutdown(self.visits)
        manager = self.manager()
        self.addCleanup(self.shutdown, manager)
        with patch('photobooth.post_preview_sandbox_visits.WorkerFenceKey.create',
                   side_effect=AssertionError('Unknown boot must not mint a key')) as mint:
            with self.assertRaises(DraftHeld):
                manager.start()
            self.assertEqual(0, mint.call_count)
        self.assertIsNone(manager._backend)
        self.assertEqual(draft, self.saved_row('SELECT * FROM pp_drafts'))

    def test_actual_live_backend_orphan_holds_before_key_or_second_child(self):
        from tests.test_post_preview_host import SandboxHostTests
        self.shutdown(self.visits)
        helper = SandboxHostTests(methodName='runTest')
        self.addCleanup(helper.doCleanups)
        orphan = helper.launch(self.config)
        manager = self.manager()
        self.addCleanup(self.shutdown, manager)
        with patch('photobooth.post_preview_sandbox_visits.WorkerFenceKey.create',
                   side_effect=AssertionError('Live orphan cannot mint')) as mint:
            with self.assertRaises(DraftHeld):
                manager.start()
            self.assertEqual(0, mint.call_count)
        self.assertIsNone(manager._backend)
        self.assertIsNone(orphan.process.poll())
        self.assertTrue(orphan.stop(timeout=10))

    def test_corrupt_original_context_holds_before_key_and_is_preserved(self):
        self.shutdown(self.visits)
        path = self.config.private_root/'host-context.json'
        path.write_bytes(b'{"version":1,"version":1}')  # Isolated corrupt fixture.
        manager = self.manager(); self.addCleanup(self.shutdown, manager)
        with patch('photobooth.post_preview_sandbox_visits.WorkerFenceKey.create') as mint:
            with self.assertRaises(DraftHeld): manager.start()
            self.assertEqual(0, mint.call_count)
        self.assertTrue(path.read_bytes() == b'{"version":1,"version":1}')
        self.assertIsNone(manager._backend)

    def test_missing_db_orphan_wal_and_unknown_root_never_create_history(self):
        for merchant, name in (('MWAL', 'drafts.sqlite3-wal'), ('MUNKNOWN', 'customer-photo.jpg')):
            config = replace(self.config, merchant_id=merchant)
            manager = self.manager(config); self.addCleanup(self.shutdown, manager)
            path = config.private_root/name
            path.write_bytes(b'original-public-fixture-preserved')
            with patch('photobooth.post_preview_sandbox_visits.WorkerFenceKey.create') as mint:
                with self.assertRaises(DraftHeld): manager.start()
                self.assertEqual(0, mint.call_count)
            self.assertIsNone(manager._backend)
            self.assertFalse((config.private_root/'drafts.sqlite3').exists())
            self.assertTrue(path.read_bytes() == b'original-public-fixture-preserved')

    def test_readonly_review_observes_unacked_owner_committed_in_original_wal(self):
        from photobooth.post_preview_store import PostPreviewStore
        self.shutdown(self.visits)
        store = PostPreviewStore(self.config.private_root/'drafts.sqlite3')
        self.addCleanup(store.close)
        lease = store.create('PB001', 'wal-original-owner', {'template_a': 1})
        path = self.config.private_root/'drafts.sqlite3'
        wal = Path(str(path)+'-wal'); shm = Path(str(path)+'-shm')
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (path, wal)}
        self.assertTrue(shm.exists())
        manager = self.manager(); self.addCleanup(self.shutdown, manager)
        with patch('photobooth.post_preview_sandbox_visits.WorkerFenceKey.create') as mint:
            with self.assertRaises(DraftHeld): manager.start()
            self.assertEqual(0, mint.call_count)
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before})
        self.assertTrue(shm.exists())
        self.assertEqual(lease.draft_id, self.saved_row('SELECT * FROM pp_drafts')['draft_id'])

    def test_late_history_after_precheck_still_hits_original_post_open_hold(self):
        from photobooth.post_preview_store import PostPreviewStore
        from photobooth.post_preview_visit_history import review_before_original_worker
        self.shutdown(self.visits)
        manager = self.manager(); self.addCleanup(self.shutdown, manager)
        def changed(*args):
            review_before_original_worker(*args)
            store = PostPreviewStore(self.config.private_root/'drafts.sqlite3')
            try: store.create('PB001', 'late-original-owner', {'template_a': 1})
            finally: store.close()
        with patch('photobooth.post_preview_sandbox_visits.review_before_original_worker', side_effect=changed):
            with self.assertRaises(DraftHeld): manager.start()
        self.assertIsNotNone(manager._backend)
        self.assertFalse(manager._admitted)
        self.assertIsNone(manager._service.lease)
        self.assertEqual('late-original-owner', self.saved_row('SELECT * FROM pp_drafts')['visit_id'])


    def setUp(self):
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        self.root=Path(directory.name)
        self.legacy=CheckoutStore(self.root/'legacy.sqlite3');self.addCleanup(self.legacy.close)
        self.config=SandboxHostConfig(self.root,'MTEST','PB001','Mid-server-DELIVERY-FIXTURE',
            'b'*48,'https://script.google.com/macros/s/VISIT_FIXTURE/exec','synthetic-visit-drive')
        self.frame=np.zeros((24,32,3),dtype=np.uint8);self.frame[:,:16,0]=180
        self.printer=PrinterConfig(lan_host='fixture-printer',usb_device_path=None)
        child=patch('photobooth.post_preview_bootstrap.CHILD_MODULE','tests.post_preview_host_process_fixture')
        child.start();self.addCleanup(child.stop)
        self.visits=self.manager()
        self.addCleanup(self.shutdown,self.visits)
        self.binding=self.visits.start()

    def manager(self,config=None):
        return OriginalSandboxVisits(config or self.config,self.printer,self.legacy,
            camera=CachedCamera(self.frame,0),qr_loader=lambda _:Image.new('RGB',(200,200),'white'),
            printer_dial=lambda *_:SimpleNamespace(close=lambda:None))

    def shutdown(self,manager):
        deadline=time.monotonic()+12
        while not manager.stop():
            if time.monotonic()>=deadline:self.fail('Original visit handles did not gracefully finish')
            time.sleep(.05)

    def retry(self,call):
        deadline=time.monotonic()+12
        while True:
            try:return call()
            except DraftHeld:
                if time.monotonic()>=deadline:raise
                time.sleep(.05)

    def frozen(self,binding,quantities=None):
        service=binding.service;templates=get_templates()
        service.start(templates,quantities or {'template_a':1})
        for _ in range(len(service.selected)):
            for _ in range(3):
                view=service.snapshot()
                service.capture(self.frame,view['capture_slot'],view['revision'],view['retake'],view['generation'])
            service.compose();service.next()
        view=service.snapshot()
        # Existing trusted fixture boundary only; no production freeze enabled.
        intent=service.checkout.freeze(service.lease,templates,revision=view['revision'],
            expected_amount=view['amount'],readiness=ChargeReadiness(True,True,True,True,True,True,True,25))
        group=intent['purchase_group_id']
        view=service.accept_frozen_checkout(group);proof=view['ccp_offer'].qr_payload
        service.ccp_visible(view['ccp_offer'])
        return group,proof

    def paid(self,binding,quantities=None):
        service=binding.service
        group,proof=self.frozen(binding,quantities)
        service.begin_payment()
        def settle():
            view=service.check_payment('connectivity')
            if view['phase']!='paid_hold':raise DraftHeld('Original settlement pacing')
            return view
        self.retry(settle)
        view=service.prepare_ticket();service.ticket_visible(view['ticket_offer'])
        service.ticket_send_receipt();service.ticket_dismiss();service.prepare_paid_delivery()
        for _ in range(len(service.selected)):service.paid_print_next()
        return group,proof

    def output_count(self):
        return int((self.config.private_root/'fixture-output-send-count').read_text())

    def test_actual_A_to_B_to_A_uses_new_children_workers_and_same_original_output(self):
        a=self.binding;group,proof=self.paid(a,{'template_a':2,'template_b':1})
        original=a.service.snapshot()['delivery'];old_lease=a.service.lease
        old_process=self.visits._backend.process;old_key=self.visits._key;old_server=self.visits._server
        hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                (self.config.private_root/'media'/old_lease.draft_id).rglob('*') if p.is_file()}
        sends=self.output_count()
        a.service.retire('RESULT_TIMEOUT')
        b=self.retry(self.visits.ensure_new_visitor_ready)
        self.assertEqual(0,old_process.returncode);self.assertNotEqual(old_process.pid,self.visits._backend.process.pid)
        self.assertNotEqual(old_key.key_id,self.visits._key.key_id)
        self.assertEqual(old_key.secret!=self.visits._key.secret,True)
        self.assertTrue(a.jobs._closed);self.assertTrue(old_server._stop.is_set())
        with self.assertRaises(RuntimeError):old_server.start()
        self.assertFalse(a.jobs.submit('prepare'))
        self.assertEqual(a.epoch+1,b.epoch);self.assertIsNone(b.service.lease)
        b.service.start(get_templates(),{'template_b':1})
        view=b.service.snapshot()
        b.service.capture(self.frame,view['capture_slot'],view['revision'],view['retake'],view['generation'])
        b_lease=b.service.lease
        self.assertEqual(dict(state='WAIT',reason='BOOTH_BUSY'),self.visits.recover_paid(proof))
        self.assertEqual(b_lease,b.service.lease)
        b.service.retire('USER_CANCEL')
        b_process=self.visits._backend.process
        returned=self.retry(lambda:self.visits.recover_paid(proof))
        self.assertEqual('RESTORED',returned['state'])
        self.assertEqual(0,b_process.returncode)
        c=returned['binding'];self.assertIsInstance(c,NativeVisitBinding)
        self.assertEqual(b.epoch+1,c.epoch);self.assertTrue(returned['snapshot']['ticket_dismissed'])
        self.assertEqual(old_lease.draft_id,c.service.lease.draft_id)
        self.assertEqual(4,c.service.lease.generation)
        self.assertEqual(original['folder_url'],c.service.prepare_paid_delivery()['delivery']['folder_url'])
        self.assertTrue(c.service.paid_print_next()['delivery']['print_all_submitted'])
        self.assertEqual(sends,self.output_count())
        self.assertEqual(hashes,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in hashes})
        self.assertEqual(1,c.service.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
        self.assertEqual('OWED',c.service.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertNotIn(self.config.server_key,repr(vars(c.service)))
        self.assertNotIn(proof,repr(returned))

    def test_actual_live_photo_worker_keeps_manager_child_and_root_owner_held(self):
        service=self.binding.service;service.start(get_templates(),{'template_a':1})
        entered=threading.Event();release=threading.Event();original=service.snapshot
        def blocked():entered.set();release.wait(6);return original()
        old_process=self.visits._backend.process
        with patch.object(service,'snapshot',side_effect=blocked):
            self.assertTrue(self.binding.jobs.submit('snapshot'))
            try:
                self.assertTrue(entered.wait(2));service.retire('USER_CANCEL')
                with self.assertRaises(DraftHeld):self.visits.ensure_new_visitor_ready()
                self.assertIs(old_process,self.visits._backend.process)
                self.assertEqual(0,service.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
                with self.assertRaises(OSError):LaunchLease(self.config.private_root)
            finally:release.set();self.binding.jobs._thread.join(6)
        fresh=self.retry(self.visits.ensure_new_visitor_ready)
        self.assertEqual(self.binding.epoch+1,fresh.epoch)

    def test_lost_actual_ack_reply_replays_same_operation_before_child_rotation(self):
        service=self.binding.service;service.start(get_templates(),{'template_a':1})
        service.retire('USER_CANCEL')
        original=self.visits._client._transport._call;lost=[]
        def reply(*args,**kwargs):
            result=original(*args,**kwargs)
            if args[1].endswith('/ack') and not lost:
                lost.append(True);raise OSError('Synthetic lost ACK response')
            return result
        old=self.visits._backend.process
        with patch.object(self.visits._client._transport,'_call',side_effect=reply):
            fresh=self.retry(self.visits.ensure_new_visitor_ready)
        self.assertTrue(lost);self.assertEqual(0,old.returncode)
        self.assertEqual(1,fresh.service.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual((1,3),tuple(fresh.service.ledger.db.execute('SELECT closed,generation FROM pp_drafts').fetchone()))

    def test_returning_paid_claim_finishes_lost_ack_before_preflight_can_reacquire_old_owner(self):
        group,proof=self.paid(self.binding);self.binding.service.retire('RESULT_TIMEOUT')
        original=self.visits._client._transport._call;lost=[]
        def reply(*args,**kwargs):
            result=original(*args,**kwargs)
            if args[1].endswith('/ack') and not lost:
                lost.append(True);raise OSError('Synthetic lost original ACK reply')
            return result
        with patch.object(self.visits._client._transport,'_call',side_effect=reply):
            def lost_ack():
                try:self.visits.recover_paid(proof)
                except DraftHeld:
                    if lost:return
                    raise
                self.fail('Expected original ACK response loss')
            self.retry(lost_ack)
            result=self.retry(lambda:self.visits.recover_paid(proof))
        self.assertEqual('RESTORED',result['state'])
        service=result['binding'].service
        self.assertEqual(4,service.lease.generation)
        self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])
        self.assertEqual(1,service.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual('OWED',service.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_true_stop_flag_without_actual_child_exit_cannot_publish_new_binding(self):
        service=self.binding.service;service.start(get_templates(),{'template_a':1});service.retire('USER_CANCEL')
        process=self.visits._backend
        with patch.object(process,'stop',return_value=True):
            def held():
                try:self.visits.ensure_new_visitor_ready()
                except DraftHeld:
                    if self.visits._acked:return
                    raise
                self.fail('A stop flag published a binding before actual child exit')
            self.retry(held)
            with self.assertRaises(DraftHeld):self.visits.ensure_new_visitor_ready()
            self.assertIsNone(process.process.poll())
            self.assertIs(self.binding,self.visits._binding)
        fresh=self.retry(self.visits.ensure_new_visitor_ready)
        self.assertEqual(self.binding.epoch+1,fresh.epoch)

    def test_invalid_proof_cannot_release_a_retired_original_paid_visit(self):
        group,proof=self.paid(self.binding)
        self.binding.service.retire('RESULT_TIMEOUT')
        wrong=proof[:-1]+('A' if proof[-1]!='A' else 'B')
        with self.assertRaises(DraftHeld):self.visits.recover_paid(wrong)
        self.assertEqual(0,self.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual(0,self.visits.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.assertEqual('RESTORED',self.retry(lambda:self.visits.recover_paid(proof))['state'])

    def test_lost_original_claim_response_is_recovered_with_same_persisted_request(self):
        group,proof=self.paid(self.binding)
        self.binding.service.retire('RESULT_TIMEOUT')
        fresh=self.retry(self.visits.ensure_new_visitor_ready)
        original=self.visits._client._transport._call;lost=[]
        def reply(*args,**kwargs):
            result=original(*args,**kwargs)
            if args[1].endswith('/claim') and not lost:
                lost.append(True);raise OSError('Synthetic lost original claim response')
            return result
        with patch.object(self.visits._client._transport,'_call',side_effect=reply):
            restored=self.retry(lambda:self.visits.recover_paid(proof))
        self.assertTrue(lost);self.assertEqual('RESTORED',restored['state'])
        self.assertIs(fresh,restored['binding'])
        self.assertEqual(1,fresh.service.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])
        self.assertEqual(4,fresh.service.lease.generation)

    def test_original_boot_owner_stays_held_without_tokenless_adoption_or_new_root(self):
        service=self.binding.service;service.start(get_templates(),{'template_a':1})
        lease=service.lease
        self.shutdown(self.visits)
        other=self.manager();self.addCleanup(self.shutdown,other)
        with self.assertRaises(DraftHeld):other.start()
        with self.assertRaises(DraftHeld):other.ensure_new_visitor_ready()
        self.assertIsNone(other._service)
        self.assertIsNone(other._backend)
        row=self.saved_row('SELECT * FROM pp_drafts')
        self.assertEqual(lease.draft_id,row['draft_id']);self.assertEqual(0,row['closed'])
        self.assertEqual('APP_SUSPENDED',row['lifecycle'])
        self.assertFalse(other._admitted)

    def test_actual_original_collector_callback_must_exit_before_any_release_or_new_child(self):
        service=self.binding.service;self.frozen(self.binding)
        server=self.visits._server;old=self.visits._backend.process
        entered=threading.Event();release=threading.Event();outcomes=[]
        original=server._collector
        def blocked(scope):entered.set();release.wait(6);return original(scope)
        def begin():
            try:outcomes.append(service.begin_payment())
            except Exception as error:outcomes.append(type(error).__name__)
        with patch.object(server,'_collector',side_effect=blocked):
            call=threading.Thread(target=begin);call.start()
            try:
                self.assertTrue(entered.wait(3));service.retire('USER_CANCEL')
                with self.assertRaises(DraftHeld):self.visits.ensure_new_visitor_ready()
                self.assertTrue(server._thread.is_alive())
                self.assertIs(old,self.visits._backend.process)
                self.assertEqual(0,service.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
                with self.assertRaises(OSError):LaunchLease(self.config.private_root)
            finally:release.set();call.join(8)
        self.assertFalse(call.is_alive());self.assertEqual([{'phase':'hold'}],outcomes)
        fresh=self.retry(self.visits.ensure_new_visitor_ready)
        self.assertEqual(self.binding.epoch+1,fresh.epoch)
        self.assertEqual(0,fresh.service.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])

    def test_slow_original_native_ledger_close_cannot_reopen_pixels_or_block_same_claim_forever(self):
        group,proof=self.paid(self.binding);service=self.binding.service
        service.retire('RESULT_TIMEOUT')
        entered=threading.Event();release=threading.Event();original=service.ledger.close
        def blocked():entered.set();release.wait(8);return original()
        with patch.object(service.ledger,'close',side_effect=blocked):
            def closing():
                try:self.visits.ensure_new_visitor_ready()
                except DraftHeld:
                    if entered.is_set():return
                    raise
                self.fail('A closing original ledger published a new binding')
            try:
                self.retry(closing)
                self.assertTrue(self.visits._closing)
                with self.assertRaises(DraftHeld):self.visits.recover_paid(proof)
                self.assertEqual({'phase':'hold'},service.snapshot())
            finally:release.set();service.wait_closed(8)
        returned=self.retry(lambda:self.visits.recover_paid(proof))
        self.assertEqual('RESTORED',returned['state'])
        self.assertEqual(group,returned['purchase_group_id'])
        self.assertEqual(4,returned['binding'].service.lease.generation)

    def test_foreign_booth_row_in_original_root_is_preserved_and_holds_new_admission(self):
        lease=self.visits.ledger.create('PB002','foreign-visit',{'template_a':1})
        with self.assertRaises(DraftHeld):self.visits.ensure_new_visitor_ready()
        row=self.visits.ledger.db.execute('SELECT * FROM pp_drafts WHERE draft_id=?',(lease.draft_id,)).fetchone()
        self.assertEqual(('PB002',0,'ACTIVE'),(row['booth_id'],row['closed'],row['lifecycle']))
        self.assertIsNone(self.binding.service.lease)

    def test_invalid_proof_after_ack_can_finish_only_original_close_without_media_grant(self):
        group,proof=self.paid(self.binding);self.binding.service.retire('RESULT_TIMEOUT')
        process=self.visits._backend
        with patch.object(process,'stop',return_value=False):
            def acked():
                try:self.visits.ensure_new_visitor_ready()
                except DraftHeld:
                    if self.visits._acked:return
                    raise
                self.fail('Unstopped original child published a binding')
            self.retry(acked)
        wrong=proof[:-1]+('A' if proof[-1]!='A' else 'B')
        def denied_after_close():
            try:self.visits.recover_paid(wrong)
            except DraftHeld:
                if self.visits._service is not None and not self.visits._service._hidden.is_set():return
                raise
            self.fail('Invalid original proof restored private media')
        self.retry(denied_after_close)
        self.assertIsNone(self.visits._service.lease)
        self.assertEqual((1,3),tuple(self.visits.ledger.db.execute('SELECT closed,generation FROM pp_drafts').fetchone()))
        self.assertEqual('OWED',self.visits.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual('RESTORED',self.retry(lambda:self.visits.recover_paid(proof))['state'])

    def test_changed_financial_review_after_ack_holds_new_binding_over_same_root(self):
        self.paid(self.binding);self.binding.service.retire('RESULT_TIMEOUT')
        process=self.visits._backend
        with patch.object(process,'stop',return_value=False):
            def acked():
                try:self.visits.ensure_new_visitor_ready()
                except DraftHeld:
                    if self.visits._acked:return
                    raise
                self.fail('Unstopped original child published a binding')
            self.retry(acked)
            self.visits.ledger.db.execute('UPDATE pp_purchase_finance SET review_required=1')
        original_epoch=self.binding.epoch
        def review_holds():
            try:self.visits.ensure_new_visitor_ready()
            except DraftHeld:
                if self.visits._service is None:return
                raise
            self.fail('Financial review permitted new native admission')
        self.retry(review_holds)
        with self.assertRaises(DraftHeld):self.visits.ensure_new_visitor_ready()
        self.assertEqual(original_epoch,self.visits._epoch)
        self.assertIsNone(self.visits._service)
        self.assertIsNone(self.visits._backend)
        self.assertEqual(1,self.saved_row('SELECT review_required FROM pp_purchase_finance')['review_required'])

    def test_fresh_native_command_blocks_new_admission_without_rotating_original_child(self):
        service=self.binding.service;old=self.visits._backend.process
        entered=threading.Event();release=threading.Event();original=service.snapshot
        def blocked():entered.set();release.wait(5);return original()
        with patch.object(service,'snapshot',side_effect=blocked):
            self.assertTrue(self.binding.jobs.submit('snapshot'))
            try:
                self.assertTrue(entered.wait(2))
                with self.assertRaises(DraftHeld):self.visits.ensure_new_visitor_ready()
                self.assertIs(old,self.visits._backend.process)
            finally:release.set();self.binding.jobs._thread.join(6)
        self.binding.jobs.poll()
        self.assertIs(self.binding,self.visits.ensure_new_visitor_ready())

    def test_pending_fresh_native_snapshot_must_finish_before_original_claim_mutates_facade(self):
        group,proof=self.paid(self.binding);self.binding.service.retire('RESULT_TIMEOUT')
        fresh=self.retry(self.visits.ensure_new_visitor_ready)
        service=fresh.service;entered=threading.Event();release=threading.Event();original=service.snapshot
        def blocked():entered.set();release.wait(5);return original()
        with patch.object(service,'snapshot',side_effect=blocked):
            self.assertTrue(fresh.jobs.submit('snapshot'))
            try:
                self.assertTrue(entered.wait(2))
                self.assertEqual(dict(state='WAIT',reason='BOOTH_BUSY'),self.visits.recover_paid(proof))
                self.assertIsNone(service.lease)
                self.assertEqual(0,service.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])
            finally:release.set();fresh.jobs._thread.join(6)
        fresh.jobs.poll()
        self.assertEqual('RESTORED',self.retry(lambda:self.visits.recover_paid(proof))['state'])


    def test_empty_hidden_facade_rotates_without_inventing_customer_ack(self):
        old=self.binding;process=self.visits._backend.process
        old.service.hide_private()
        self.retry(lambda:self.visits.retire_current('APP_SUSPENDED'))
        fresh=self.retry(self.visits.ensure_new_visitor_ready)
        self.assertEqual(old.epoch+1,fresh.epoch)
        self.assertEqual(0,process.returncode)
        self.assertTrue(old.jobs._closed)
        self.assertIsNone(fresh.service.lease)
        self.assertEqual(0,self.visits.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])

    def test_late_original_claim_can_retire_only_its_exact_durable_owner_without_media(self):
        group,proof=self.paid(self.binding);self.binding.service.retire('RESULT_TIMEOUT')
        fresh=self.retry(self.visits.ensure_new_visitor_ready)
        service=fresh.service;entered=threading.Event();release=threading.Event();errors=[]
        original=service._handoff.claim
        def blocked(*args):
            grant=original(*args);entered.set();release.wait(6);return grant
        def claim():
            deadline=time.monotonic()+12
            while True:
                try:self.visits.recover_paid(proof);return
                except DraftHeld:
                    if entered.is_set():errors.append('held');return
                    if time.monotonic()>=deadline:errors.append('preflight held');return
                    time.sleep(.05)
        with patch.object(service._handoff,'claim',side_effect=blocked):
            worker=threading.Thread(target=claim);worker.start()
            try:
                self.assertTrue(entered.wait(12));service.hide_private()
            finally:release.set();worker.join(8)
        self.assertEqual(['held'],errors);self.assertIsNone(service.lease)
        with patch.object(service.photos,'inspect',side_effect=AssertionError('No media for retirement')):
            self.retry(lambda:self.visits.retire_current('APP_SUSPENDED'))
        self.assertEqual({'phase':'hold'},service.snapshot())
        self.assertEqual(group,service.group)
        self.assertEqual(4,service.lease.generation)
        row=service.ledger.db.execute('SELECT * FROM pp_drafts WHERE draft_id=?',(service.lease.draft_id,)).fetchone()
        self.assertEqual(('APP_SUSPENDED',5),(row['lifecycle'],row['generation']))
        self.visits.retire_current('USER_CANCEL')
        self.assertEqual('APP_SUSPENDED',service.ledger.db.execute('SELECT lifecycle FROM pp_drafts WHERE draft_id=?',
            (service.lease.draft_id,)).fetchone()[0])
        newest=self.retry(self.visits.ensure_new_visitor_ready)
        self.assertIsNone(newest.service.lease)
        self.assertEqual(1,newest.service.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])

    def test_unknown_active_owner_cannot_be_adopted_for_privacy_retirement(self):
        owner=self.visits.ledger.create('PB001','unknown-owner',{'template_a':1})
        self.binding.service.hide_private()
        with self.assertRaises(DraftHeld):self.visits.retire_current('APP_SUSPENDED')
        self.assertIsNone(self.binding.service.lease)
        row=self.visits.ledger.db.execute('SELECT * FROM pp_drafts WHERE draft_id=?',(owner.draft_id,)).fetchone()
        self.assertEqual(('ACTIVE',1,0),(row['lifecycle'],row['generation'],row['closed']))
        with self.assertRaises(DraftHeld):self.visits.ensure_new_visitor_ready()


    def test_privacy_retirement_waits_for_original_photo_thread_before_durable_event(self):
        service=self.binding.service;service.start(get_templates(),{'template_a':1})
        entered,release=threading.Event(),threading.Event();original=service.snapshot
        def blocked():entered.set();release.wait(6);return original()
        with patch.object(service,'snapshot',side_effect=blocked):
            self.assertTrue(self.binding.jobs.submit('snapshot'))
            try:
                self.assertTrue(entered.wait(2));service.hide_private()
                with self.assertRaises(DraftHeld):self.visits.retire_current('APP_SUSPENDED')
                row=service.ledger.db.execute('SELECT * FROM pp_drafts').fetchone()
                self.assertEqual(('ACTIVE',1),(row['lifecycle'],row['generation']))
                self.assertTrue(self.binding.jobs._thread.is_alive())
            finally:release.set();self.binding.jobs._thread.join(7)
        self.retry(lambda:self.visits.retire_current('APP_SUSPENDED'))
        self.assertEqual('APP_SUSPENDED',service.ledger.db.execute('SELECT lifecycle FROM pp_drafts').fetchone()[0])

    def test_foreign_pending_claim_metadata_cannot_retire_original_owner(self):
        group,proof=self.paid(self.binding);self.binding.service.retire('RESULT_TIMEOUT')
        fresh=self.retry(self.visits.ensure_new_visitor_ready);service=fresh.service;interrupted=[]
        def interrupt(_grant):
            interrupted.append(True);service.hide_private();raise DraftHeld('Synthetic lost native claim response')
        with patch.object(service,'recover_original_owed',side_effect=interrupt):
            def acquire():
                try:self.visits.recover_paid(proof)
                except DraftHeld:
                    if interrupted:return
                    raise
                self.fail('Expected original restore interruption')
            self.retry(acquire)
        pending=self.visits._pending_claim
        self.assertFalse(proof in repr(pending));self.assertIsNone(service.lease)
        self.assertTrue(self.visits._server.stop(timeout=2));self.assertTrue(fresh.jobs.retire(timeout=0))
        for changed in (('0'*32,*pending[1:]),(pending[0],'0'*32,*pending[2:]),
                        (*pending[:2],'0'*64,pending[3]),(*pending[:3],pending[3]+1)):
            self.visits._pending_claim=changed
            with self.assertRaises(DraftHeld):self.visits.retire_current('APP_SUSPENDED')
            self.assertIsNone(service.lease)
            self.assertEqual(('ACTIVE',4),tuple(service.ledger.db.execute(
                'SELECT lifecycle,generation FROM pp_drafts').fetchone()))
        self.visits._pending_claim=pending
        self.retry(lambda:self.visits.retire_current('APP_SUSPENDED'))
        self.assertEqual(4,service.lease.generation)


if __name__=='__main__':unittest.main()
