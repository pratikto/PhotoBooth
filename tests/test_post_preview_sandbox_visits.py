"""Trusted original manager with actual child replacement; external effects fake."""
import hashlib
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

    def manager(self):
        return OriginalSandboxVisits(self.config,self.printer,self.legacy,
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
        self.assertIsNone(other._service.lease)
        row=other.ledger.db.execute('SELECT * FROM pp_drafts').fetchone()
        self.assertEqual(lease.draft_id,row['draft_id']);self.assertEqual(0,row['closed'])
        self.assertEqual('APP_SUSPENDED',row['lifecycle'])
        self.assertEqual(self.config.private_root,other._service.root)

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
                if self.visits._epoch>original_epoch:return
                raise
            self.fail('Financial review permitted new native admission')
        self.retry(review_holds)
        with self.assertRaises(DraftHeld):self.visits.ensure_new_visitor_ready()
        self.assertIsNone(self.visits._service.lease)
        self.assertEqual(self.config.private_root,self.visits._service.root)
        self.assertEqual(1,self.visits.ledger.db.execute('SELECT review_required FROM pp_purchase_finance').fetchone()[0])

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


if __name__=='__main__':unittest.main()
