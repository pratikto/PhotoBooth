"""Read-only review after actual fake-effects original process loss."""
from contextlib import nullcontext, ExitStack
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_bootstrap import backend_environment
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_interrupted_worker import read_interrupted_worker
from photobooth.post_preview_process_identity import OriginalProcessIdentity,original_process_exited
from photobooth.post_preview_store import DraftHeld


class InterruptedWorkerReviewTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.storage=Path(temporary.name)
        self.config=SandboxHostConfig(self.storage,'MTEST','PB001','Mid-server-DELIVERY-FIXTURE',
            'b'*48,'https://script.google.com/macros/s/INTERRUPTED_FIXTURE/exec','fixture-drive')
        self.root=self.config.private_root
        context=nullcontext() if os.name=='nt' else patch(
            'photobooth.linux_credential_vault._read_key',return_value=b'k'*32)
        context.__enter__(); self.addCleanup(context.__exit__,None,None,None)
        self.addCleanup(self.release_orphan)

    def release_orphan(self):
        if self.root.exists(): (self.root/'fixture-http-release').touch()
        deadline=time.monotonic()+10
        while self.root.exists():
            try:
                with LaunchLease(self.root/'backend-owner'): pass
                break
            except OSError:
                if time.monotonic()>deadline: self.fail('Actual original fixture backend retained its lease')
                time.sleep(.02)

    def produce(self,mode='unpaid'):
        result=subprocess.run([sys.executable,'-m','tests.post_preview_interrupted_process_fixture',
            str(self.storage),mode],cwd=Path(__file__).resolve().parents[1],
            env=backend_environment(os.environ),capture_output=True,text=True,timeout=35)
        self.assertEqual(73,result.returncode,result.stderr[-1500:])
        self.assertEqual('READY',result.stdout.strip())

    def acquire(self):
        stack=ExitStack(); self.addCleanup(stack.close)
        native=stack.enter_context(LaunchLease(self.root))
        deadline=time.monotonic()+10
        while True:
            try:
                backend=stack.enter_context(LaunchLease(self.root/'backend-owner'))
                # Kernel close can precede actual process exit by milliseconds.
                # Wait for the actual isolated fixture child; don't weaken the
                # production reader's independent old-process exit requirement.
                witness=json.loads(next((self.root/'worker-starts').iterdir()).read_bytes())['frame']
                child=OriginalProcessIdentity(witness['child_pid'],witness['child_birth'])
                while not original_process_exited(child):
                    if time.monotonic()>deadline: self.fail('Actual original fixture child did not exit')
                    time.sleep(.01)
                return native,backend
            except OSError:
                if time.monotonic()>deadline: raise
                time.sleep(.02)

    def snapshot(self):
        return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ('worker-custody','worker-starts') for p in (self.root/folder).iterdir()}

    def rows(self):
        with sqlite3.connect(self.root/'drafts.sqlite3') as db:
            return {name:db.execute('SELECT * FROM '+name).fetchall() for name in
                    ('pp_drafts','pp_worker_generations','pp_isolation_ops','pp_worker_retirements','pp_purchase_finance')}

    def held(self,owners,config=None):
        with self.assertRaises(DraftHeld) as caught: read_interrupted_worker(*owners,config or self.config)
        self.assertEqual('Original interrupted worker evidence is held',str(caught.exception))

    def test_actual_original_process_loss_review_is_read_only_and_grants_no_release(self):
        self.produce(); owners=self.acquire(); before=self.rows(); files=self.snapshot()
        with patch('photobooth.post_preview_store.PostPreviewStore.__init__',
                   side_effect=AssertionError('No replacement DB')),patch(
                   'requests.sessions.Session.request',side_effect=AssertionError('No network')):
            review=read_interrupted_worker(*owners,self.config)
        self.assertEqual('NO_PAYMENT',review.financial_class)
        self.assertFalse(hasattr(review,'key')); self.assertFalse(hasattr(review,'proof'))
        self.assertEqual(files,self.snapshot()); self.assertEqual(before,self.rows())
        self.assertEqual('PREPARED',before['pp_isolation_ops'][0][5])
        for root in (self.root,self.root/'backend-owner'):
            with self.assertRaises(OSError): LaunchLease(root)

    def test_paid_without_purchased_output_is_reviewed_but_still_needs_fresh_backend_confirmation(self):
        self.produce('paid'); owners=self.acquire(); before=self.rows()
        review=read_interrupted_worker(*owners,self.config)
        self.assertEqual('PAID_OWED',review.financial_class); self.assertEqual(before,self.rows())

    def test_missing_original_receipt_is_never_retroactively_signed(self):
        self.produce('missing-receipt'); owners=self.acquire(); before=self.rows(); files=self.snapshot()
        self.held(owners)
        self.assertEqual([],before['pp_worker_retirements'])
        self.assertEqual(before,self.rows()); self.assertEqual(files,self.snapshot())

    def test_original_backend_orphan_kernel_hold_precedes_review(self):
        self.produce('orphan'); before=self.snapshot()
        with LaunchLease(self.root),self.assertRaises(OSError): LaunchLease(self.root/'backend-owner')
        self.assertEqual(before,self.snapshot())
        self.release_orphan(); owners=self.acquire()
        deadline=time.monotonic()+8
        while True:
            try: review=read_interrupted_worker(*owners,self.config); break
            except DraftHeld:
                if time.monotonic()>deadline: raise
                time.sleep(.02)
        self.assertEqual('PAID_OWED',review.financial_class)

    def test_paid_delivery_history_is_held_until_upload_manifest_reconciliation_exists(self):
        self.produce('delivery'); owners=self.acquire(); before=self.rows(); files=self.snapshot()
        self.held(owners)
        self.assertEqual(before,self.rows()); self.assertEqual(files,self.snapshot())

    def test_missing_original_binding_or_ciphertext_never_creates_replacements(self):
        self.produce(); owners=self.acquire()
        with sqlite3.connect(self.root/'drafts.sqlite3') as db:
            db.execute('DROP TRIGGER pp_worker_generation_no_delete')
            db.execute('DELETE FROM pp_worker_generations')
        before=self.rows(); self.held(owners); self.assertEqual(before,self.rows())
        path=next((self.root/'worker-custody').iterdir()); path.write_bytes(b'{')
        self.held(owners); self.assertEqual(b'{',path.read_bytes())

    def test_unknown_process_exit_or_os_access_does_not_become_safe(self):
        self.produce(); owners=self.acquire(); before=self.rows()
        with patch('photobooth.post_preview_interrupted_worker.original_process_exited',
                   side_effect=RuntimeError('PRIVATE OS DIAGNOSTIC')): self.held(owners)
        with patch('photobooth.post_preview_worker_custody.platform_protector',
                   side_effect=RuntimeError('PRIVATE ACCOUNT DIAGNOSTIC')): self.held(owners)
        self.assertEqual(before,self.rows())

    def test_foreign_scope_or_closed_kernel_owner_is_held(self):
        self.produce(); owners=self.acquire(); before=self.rows()
        self.held(owners,replace(self.config,merchant_id='FOREIGN'))
        owners[1].close(); self.held(owners); self.assertEqual(before,self.rows())

    def test_partial_backend_verified_receipt_never_normalizes_original_prepare(self):
        self.produce(); owners=self.acquire()
        with sqlite3.connect(self.root/'drafts.sqlite3') as db:
            db.execute('UPDATE pp_worker_retirements SET backend_verified_at=?',(time.time(),))
        before=self.rows(); self.held(owners); self.assertEqual(before,self.rows())

    def test_actual_active_owner_is_not_retired_or_given_a_new_binding_on_boot(self):
        self.produce('active'); owners=self.acquire(); before=self.rows(); files=self.snapshot()
        self.held(owners)
        self.assertEqual(before,self.rows()); self.assertEqual(files,self.snapshot())

    def test_retired_without_original_prepare_is_not_given_an_operation_or_receipt(self):
        self.produce('unprepared'); owners=self.acquire(); before=self.rows()
        self.held(owners); self.assertEqual([],before['pp_isolation_ops'])
        self.assertEqual([],before['pp_worker_retirements']); self.assertEqual(before,self.rows())

    def test_original_customer_receipt_uncertainty_holds_despite_valid_native_retirement(self):
        self.produce('receipt'); owners=self.acquire()
        with sqlite3.connect(self.root/'drafts.sqlite3') as db:
            db.execute("UPDATE pp_ticket_presentations SET receipt_state='UNCERTAIN'")
        before=self.rows(); self.assertEqual(1,len(before['pp_worker_retirements']))
        self.held(owners); self.assertEqual(before,self.rows())


if __name__=='__main__': unittest.main()
