"""Actual original recovery-only child then fresh native epoch; external fakes."""
from contextlib import closing
import json
import time
import unittest
from unittest.mock import patch

from PIL import Image

from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_launch import ProtectedSandboxLaunch,ProtectedLaunchHeld
from photobooth.post_preview_process_identity import OriginalProcessIdentity,original_process_exited
from photobooth.post_preview_recovery_start import read_recovery_start
from photobooth.post_preview_worker_custody import restore_worker_key
from photobooth.post_preview_worker_escrow import read_worker_escrow
from photobooth.printer import PrinterConfig
from photobooth.qris_kiosk_client import QrisKioskClient
from tests import test_post_preview_interrupted_worker as fixtures


class InterruptedOriginalRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.InterruptedWorkerReviewTests(methodName='runTest');self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        child=patch('photobooth.post_preview_bootstrap.CHILD_MODULE','tests.post_preview_host_process_fixture')
        child.start();self.addCleanup(child.stop)
        self.owner=ProtectedSandboxLaunch(self.f.storage/'project')
        self.addCleanup(self.shutdown)

    def shutdown(self):
        # Cooperatively release this test's fake provider only; never force-kill.
        if self.f.root.exists(): (self.f.root/'fixture-http-release').touch()
        deadline=time.monotonic()+15
        while not self.owner.stop(timeout=.2):
            if time.monotonic()>deadline:self.fail('Actual original recovery child did not drain')
            time.sleep(.02)

    def produce(self,mode='unpaid'):
        private=self.f.produce(mode)
        native,backend=self.f.acquire();backend.close();native.close()
        return private

    def start(self,**kwargs):
        return self.owner.start(self.f.config,PrinterConfig(lan_host='fixture-printer',usb_device_path=None),
            legacy_path=self.f.storage/'legacy.sqlite3',qr_loader=lambda _:Image.new('RGB',(200,200),'white'),
            camera_enabled=False,durable_worker_epochs=True,**kwargs)

    def test_actual_original_ack_then_recovery_child_exit_precedes_fresh_native_epoch(self):
        self.produce();before=self.f.rows();mac=before['pp_worker_retirements'][0][3]
        control=self.start();ledger=self.owner._visits.ledger
        self.assertEqual('READY',control.state);self.assertIsNone(control.binding.service.lease)
        self.assertEqual('ACKED',ledger.db.execute('SELECT state FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual(mac,ledger.db.execute('SELECT mac FROM pp_worker_retirements').fetchone()[0])
        self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_worker_retirements').fetchone()[0])
        self.assertIsNone(self.owner._recovery._backend)
        files=list((self.f.root/'worker-recoveries').glob('*.intent.json'));self.assertEqual(1,len(files))
        value=json.loads(files[0].read_bytes());epoch=value['frame']['worker_epoch'];nonce=value['frame']['nonce']
        stored=read_worker_escrow(self.owner._visits._launcher,epoch)
        key=restore_worker_key(stored.envelope,stored.scope)
        frame=read_recovery_start(self.f.config,key,nonce)
        self.assertTrue(original_process_exited(OriginalProcessIdentity(frame['child_pid'],frame['child_birth'])))
        self.assertNotEqual(epoch,self.owner._visits._key.key_id)

    def test_lost_ack_reply_retries_same_original_operation_without_new_receipt(self):
        self.produce();original=QrisKioskClient._call;calls=[]
        def lose(client,method,path,**kwargs):
            result=original(client,method,path,**kwargs)
            if path.endswith('/ack') and '/isolation/' in path:
                calls.append(True)
                if len(calls)==1:raise OSError('Synthetic lost exact ACK reply')
            return result
        with patch.object(QrisKioskClient,'_call',lose):control=self.start()
        self.assertEqual('READY',control.state);self.assertEqual(2,len(calls))
        ledger=self.owner._visits.ledger
        self.assertEqual(1,ledger.db.execute("SELECT COUNT(*) FROM pp_events WHERE event='PROTECTED_ISOLATION_ACKED'").fetchone()[0])
        self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_worker_retirements').fetchone()[0])

    def test_paid_restart_stays_neutral_until_original_proof_and_fresh_settlement(self):
        private=self.produce('claim');self.start();manager=self.owner._visits
        self.assertIsNone(manager._service.lease);self.assertEqual('confirm',manager._service.phase)
        with self.assertRaises(PermissionError):manager.recover_paid('wrong role')
        deadline=time.monotonic()+12
        while True:
            try:restored=manager.recover_paid(private['proof']);break
            except Exception:
                if time.monotonic()>deadline:raise
                time.sleep(.05)
        self.assertEqual('RESTORED',restored['state']);self.assertEqual(4,manager._service.lease.generation)
        self.assertEqual(1,manager.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
        self.assertFalse((self.f.root/'fixture-output-send-count').exists())

    def test_missing_original_receipt_holds_before_process_camera_or_replacement_key(self):
        self.produce('missing-receipt');before=self.f.rows();files=self.f.snapshot()
        with self.assertRaises(ProtectedLaunchHeld):self.start()
        self.assertIsNone(self.owner._recovery._backend);self.assertIsNone(self.owner._camera)
        self.assertIsNone(self.owner._visits);self.assertEqual(before,self.f.rows());self.assertEqual(files,self.f.snapshot())
        self.assertFalse((self.f.root/'worker-recoveries').exists())
        with self.assertRaises(OSError):LaunchLease(self.owner.project_root)

    def test_purchased_delivery_stays_held_without_replaying_original_paper(self):
        self.produce('delivery');before=self.f.rows()
        count=(self.f.root/'fixture-output-send-count').read_bytes()
        with self.assertRaises(ProtectedLaunchHeld):self.start()
        self.assertEqual(before,self.f.rows());self.assertEqual(count,(self.f.root/'fixture-output-send-count').read_bytes())
        self.assertIsNone(self.owner._camera);self.assertFalse((self.f.root/'worker-recoveries').exists())

    def test_recovery_http_role_denies_charge_proof_upload_print_and_unrelated_ack(self):
        private=self.produce('claim');original=QrisKioskClient._call;observed=[]
        def inspect(client,method,path,**kwargs):
            if path.endswith('/ack') and '/isolation/' in path and not observed:
                targets=['/api/postpay/groups/'+private['group']+'/begin',
                    '/api/postpay/groups/'+private['group']+'/claim',
                    '/api/postpay/groups/'+private['group']+'/delivery/prepare',
                    '/api/postpay/groups/'+private['group']+'/delivery/print-next',
                    '/api/postpay/webhooks/midtrans','/api/postpay/isolation/'+'f'*32+'/ack',
                    '/api/postpay/drafts/'+'a'*32+'/worker-binding','/docs','/openapi.json']
                for target in targets:
                    with closing(client.session.post(client.base_url+target,json={},headers=client.headers,timeout=3)) as response:
                        self.assertEqual(404,response.status_code)
                        self.assertEqual('no-store',response.headers['Cache-Control'])
                observed.append(True)
            return original(client,method,path,**kwargs)
        with patch.object(QrisKioskClient,'_call',inspect):self.start()
        self.assertEqual([True],observed)
        self.assertEqual(1,self.owner._visits.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
        self.assertFalse((self.f.root/'fixture-output-send-count').exists())

    def test_blocked_actual_recovery_http_retains_global_and_both_child_leases_until_real_exit(self):
        self.produce('paid');(self.f.root/'fixture-force-http-hold').touch()
        release=self.f.root/'fixture-http-release';release.unlink()
        try:
            with self.assertRaises(ProtectedLaunchHeld):self.start(timeout=5)
            self.assertIsNone(self.owner._camera)
            self.assertFalse(self.owner.stop(timeout=.1))
            with self.assertRaises(OSError):LaunchLease(self.owner.project_root)
            for root in (self.f.root,self.f.root/'backend-owner'):
                with self.assertRaises(OSError):LaunchLease(root)
        finally:
            release.touch();self.shutdown()
        with LaunchLease(self.owner.project_root):pass

    def test_recovery_intent_sync_failure_withholds_popen_and_preserves_original_obligation(self):
        self.produce();before=self.f.rows()
        with patch('photobooth.post_preview_recovery_start.os.fsync',side_effect=OSError('PRIVATE SYNC ERROR')),patch(
                'photobooth.post_preview_bootstrap.subprocess.Popen',side_effect=AssertionError('No spawn before durable intent')) as spawn:
            with self.assertRaises(ProtectedLaunchHeld):self.start()
        self.assertEqual(0,spawn.call_count);self.assertIsNone(self.owner._camera)
        self.assertEqual(before,self.f.rows())
        self.assertEqual(1,len(list((self.f.root/'worker-recoveries').glob('*.intent.json'))))
        self.assertEqual(0,len([p for p in (self.f.root/'worker-recoveries').iterdir() if not p.name.endswith('.intent.json')]))

    def test_recovery_child_rejects_same_id_replacement_key_without_new_retirement(self):
        from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment
        from photobooth.post_preview_worker_fence import WorkerFenceKey
        import os
        self.produce();before=self.f.rows()
        def wrong(printer,key,**kwargs):
            return SandboxHostFulfillment(printer,WorkerFenceKey(key.key_id,os.urandom(32)),**kwargs)
        with patch('photobooth.post_preview_interrupted_recovery.SandboxHostFulfillment',side_effect=wrong):
            with self.assertRaises(ProtectedLaunchHeld):self.start()
        self.assertEqual(before,self.f.rows());self.assertIsNone(self.owner._camera)


if __name__=='__main__':unittest.main()
