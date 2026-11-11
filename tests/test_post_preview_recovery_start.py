"""Distinct NEW recovery process provenance; no original receipt/admission."""
from contextlib import nullcontext
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_bootstrap import backend_environment
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_process_identity import observe_process
from photobooth.post_preview_recovery_start import (
    record_recovery_intent,record_recovery_start,read_recovery_start,review_recovery_processes)
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_worker_custody import WorkerCustodyScope
from photobooth.post_preview_worker_escrow import write_new_worker_escrow
from photobooth.post_preview_worker_fence import WorkerFenceKey,canonical

CHILD='''import os,sys
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_recovery_start import review_recovery_processes
print('READY',flush=True)
if sys.stdin.readline().strip()!='CHECK':raise SystemExit(0)
config=SandboxHostConfig(Path(sys.argv[1]),'MTEST','PB001','Mid-server-RECOVERY-FIXTURE',
 'b'*48,'https://script.google.com/macros/s/RECOVERY_FIXTURE/exec','fixture-drive')
context=nullcontext() if os.name=='nt' else patch('photobooth.linux_credential_vault._read_key',return_value=b'k'*32)
with context,LaunchLease(config.private_root) as owner:
 review_recovery_processes(owner,config,current_nonce=sys.argv[2])
 print('VERIFIED',flush=True)
'''


class RecoveryProcessStartTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.storage=Path(temporary.name)
        self.config=SandboxHostConfig(self.storage,'MTEST','PB001','Mid-server-RECOVERY-FIXTURE',
            'b'*48,'https://script.google.com/macros/s/RECOVERY_FIXTURE/exec','fixture-drive')
        self.native=LaunchLease(self.config.private_root);self.addCleanup(self.native.close)
        self.global_owner=LaunchLease(self.storage/'project');self.addCleanup(self.global_owner.close)
        context=nullcontext() if os.name=='nt' else patch(
            'photobooth.linux_credential_vault._read_key',return_value=b'k'*32)
        context.__enter__();self.addCleanup(context.__exit__,None,None,None)
        self.key=WorkerFenceKey.create();self.nonce='c'*32;self.operation='a'*32
        scope=WorkerCustodyScope(self.config.private_root,'MTEST','PB001',self.key.key_id,
            os.getpid(),observe_process(os.getpid()).birth)
        write_new_worker_escrow(self.native,self.key,scope)
        record_recovery_intent(self.global_owner,self.config,self.key,self.operation,self.nonce)
        self.child=subprocess.Popen([sys.executable,'-c',CHILD,str(self.storage),self.nonce],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            text=True,env=backend_environment(os.environ))
        self.addCleanup(self.stop_child);self.assertEqual('READY',self.child.stdout.readline().strip())
        self.folder=self.config.private_root/'worker-recoveries'

    def stop_child(self):
        if self.child.poll() is None:self.child.communicate('',timeout=10)
        else:self.child.stdin.close();self.child.stdout.close()

    def record(self):
        return record_recovery_start(self.global_owner,self.config,self.key,self.operation,self.nonce,self.child)

    def held(self,action):
        with self.assertRaises(DraftHeld):action()

    def test_distinct_new_process_role_links_original_operation_and_actual_birth(self):
        frame=self.record()
        self.assertEqual('ORIGINAL_RECOVERY_PROCESS_START',frame['kind'])
        self.assertEqual(self.child.pid,frame['child_pid']);self.assertEqual(os.getpid(),frame['parent_pid'])
        self.assertEqual(self.operation,frame['operation_id'])
        self.assertEqual(frame,read_recovery_start(self.config,self.key,self.nonce))
        raw=b''.join(path.read_bytes() for path in self.folder.iterdir())
        for secret in (self.key.secret.hex(),self.config.server_key,self.config.booth_token,self.config.drive_token):
            self.assertNotIn(secret.encode(),raw)

    def test_live_child_and_parent_cannot_use_current_nonce_to_skip_exit(self):
        self.record()
        self.held(lambda:review_recovery_processes(self.native,self.config))
        self.held(lambda:review_recovery_processes(self.native,self.config,current_nonce=self.nonce))
        self.stop_child();review_recovery_processes(self.native,self.config)

    def test_only_actual_current_child_can_use_its_original_private_bootstrap_nonce(self):
        self.record();self.native.close()
        stdout,_=self.child.communicate('CHECK\n',timeout=15)
        self.assertEqual(0,self.child.returncode);self.assertEqual('VERIFIED',stdout.strip())

    def test_unmatched_pre_spawn_intent_is_retained_and_never_assumed_safe(self):
        path=self.folder/(self.nonce+'.intent.json');before=path.read_bytes()
        self.stop_child()
        self.held(lambda:review_recovery_processes(self.native,self.config))
        self.assertEqual(before,path.read_bytes());self.assertFalse((self.folder/(self.nonce+'.json')).exists())
        self.held(self.record)  # Cannot retroactively sign a now-dead process.

    def test_same_original_owner_and_child_retry_preserves_both_records(self):
        self.record();before={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.folder.iterdir()}
        with patch.object(WorkerFenceKey,'create',side_effect=AssertionError('No replacement')):
            record_recovery_intent(self.global_owner,self.config,self.key,self.operation,self.nonce)
            self.record()
        self.assertEqual(before,{p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.folder.iterdir()})

    def test_failed_sync_preserves_complete_original_record_for_same_process_retry(self):
        with patch('photobooth.post_preview_recovery_start.os.fsync',side_effect=OSError('PRIVATE IO')):
            self.held(self.record)
        path=self.folder/(self.nonce+'.json');raw=path.read_bytes()
        self.record();self.assertEqual(raw,path.read_bytes())

    def test_valid_mac_cannot_impersonate_old_native_retirement_role(self):
        self.record();path=self.folder/(self.nonce+'.json');value=json.loads(path.read_bytes())
        value['frame']['kind']='ORIGINAL_WORKER_RETIRED';value['mac']=self.key.sign(value['frame'])
        raw=canonical(value).encode();path.write_bytes(raw)  # Isolated public role-confusion fixture.
        self.held(lambda:read_recovery_start(self.config,self.key,self.nonce))
        self.assertEqual(raw,path.read_bytes())

    def test_missing_intent_wrong_key_and_hardlinked_original_record_are_held(self):
        self.record()
        wrong=WorkerFenceKey(self.key.key_id,os.urandom(32))
        self.held(lambda:read_recovery_start(self.config,wrong,self.nonce))
        path=self.folder/(self.nonce+'.json');alias=self.storage/'alias.json';os.link(path,alias)
        self.held(lambda:read_recovery_start(self.config,self.key,self.nonce))
        self.assertEqual(path.read_bytes(),alias.read_bytes())


if __name__=='__main__':unittest.main()
