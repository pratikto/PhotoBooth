"""Private child fulfillment bundle; fake external effects, real original host."""
from dataclasses import asdict,replace
from contextlib import nullcontext
import os
from pathlib import Path
import socket
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

import numpy as np
from PIL import Image
import requests

from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.health_service import CachedCamera
from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.post_preview_protected_checkout import ProtectedCheckoutService
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_authority import OriginalWorkerReadiness
from photobooth.post_preview_bootstrap import SandboxBackendProcess,run_child
from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_handoff_client import PostPreviewHandoffClient
from photobooth.post_preview_host import SandboxHostConfig,SandboxHostRuntime
from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment
from photobooth.post_preview_readiness import LocalChargeReadiness
from photobooth.post_preview_readiness_bridge import WorkerReadinessClient,WorkerReadinessServer,_send
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_worker_fence import WorkerFenceKey,NativeWorkerRetirement
from photobooth.printer import PrinterConfig


class PrivateHostFulfillmentTests(unittest.TestCase):
    def setUp(self):
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        self.root=Path(directory.name)
        self.config=SandboxHostConfig(self.root,'MTEST','PB001','Mid-server-DELIVERY-FIXTURE',
            'b'*48,'https://script.google.com/macros/s/PRIVATE_HOST_FIXTURE/exec','synthetic-private-drive')
        self.key=WorkerFenceKey.create()
        self.printer=PrinterConfig(lan_host='fixture-printer',usb_device_path=None)
        self.bundle=SandboxHostFulfillment(self.printer,self.key)

    def test_exact_private_roundtrip_hides_capability_and_printer_from_repr(self):
        original=self.bundle.to_private_startup()
        restored=SandboxHostFulfillment.from_private_startup(original)
        self.assertEqual(self.key,restored.worker_key)
        self.assertEqual(asdict(self.printer),asdict(restored.printer_config))
        for private in (self.key.secret.hex(),self.printer.lan_host):
            self.assertNotIn(private,repr(self.bundle))
            self.assertNotIn(private,repr(SandboxBackendProcess(self.config,fulfillment=self.bundle)))
        self.assertFalse(self.config.private_root.exists())

    def test_partial_foreign_and_untyped_private_protocol_is_rejected_without_fallback(self):
        good=self.bundle.to_private_startup()
        malformed=[dict(good,version=True),dict(good,worker_ready=True),
            dict(good,worker_key={'key_id':self.key.key_id}),dict(good,printer={}),
            dict(good,worker_key=dict(good['worker_key'],secret_hex='A'*64))]
        for field,value in [('network_timeout',True),('lan_port',True),('print_width_dots',384),
                ('dither_mode','unknown'),('dither_threshold',300),('usb_device_path','/tmp/private.png'),
                ('usb_vendor_id',123),('windows_printer_name','queue\nprivate'),('lan_host','https://foreign')]:
            malformed.append(dict(good,printer=dict(good['printer'],**{field:value})))
        for value in malformed:
            with self.subTest(field=set(value)),self.assertRaises(ValueError) as error:
                SandboxHostFulfillment.from_private_startup(value)
            self.assertNotIn(self.key.secret.hex(),str(error.exception))
        self.assertFalse(self.config.private_root.exists())

    def test_untrusted_dependency_is_rejected_before_host_root_creation(self):
        worker,peer=socket.socketpair();self.addCleanup(worker.close);self.addCleanup(peer.close)
        bridge=WorkerReadinessClient(peer);self.addCleanup(bridge.close)
        for constructor in (lambda:SandboxHostRuntime(self.config,bridge,fulfillment=object()),
                            lambda:SandboxBackendProcess(self.config,fulfillment=object()),
                            lambda:SandboxHostFulfillment(self.printer,True)):
            with self.assertRaises(ValueError):constructor()
        self.assertFalse(self.config.private_root.exists())

    def test_original_host_shares_exact_printer_lane_and_default_stays_unmounted(self):
        worker,peer=socket.socketpair();self.addCleanup(worker.close)
        bridge=WorkerReadinessClient(peer);self.addCleanup(bridge.close)
        custody=patch('photobooth.linux_credential_vault._read_key',return_value=b'k'*32) if os.name!='nt' else nullcontext()
        with custody,patch('photobooth.midtrans_sandbox.MidtransSandboxClient._request',side_effect=AssertionError('No provider I/O')) as io:
            host=SandboxHostRuntime(self.config,bridge,fulfillment=self.bundle);self.addCleanup(host.close)
            actor=host.app.state.paid_delivery
            self.assertEqual(self.printer,actor.binder.presentation._printer.config)
            self.assertIsNotNone(actor.binder.presentation._printer_lane)
            self.assertIn('/api/postpay/isolation/{operation}/ack',{r.path for r in host.app.routes})
            self.assertTrue(host.close());io.assert_not_called()
        worker2,peer2=socket.socketpair();self.addCleanup(worker2.close)
        bridge2=WorkerReadinessClient(peer2);self.addCleanup(bridge2.close)
        with custody:
            default=SandboxHostRuntime(self.config,bridge2);self.addCleanup(default.close)
            self.assertIsNone(default.app.state.paid_delivery)
            self.assertNotIn('/api/postpay/groups/{group}/claim',{r.path for r in default.app.routes})

    def test_malformed_private_startup_never_creates_original_host(self):
        control,child=socket.socketpair();worker,readiness=socket.socketpair()
        for channel in (control,child,worker,readiness):self.addCleanup(channel.close)
        from photobooth.post_preview_bootstrap import _config_data
        invalid=self.bundle.to_private_startup();invalid['worker_key'].pop('secret_hex')
        _send(control,dict(version=1,kind='START',nonce=uuid.uuid4().hex,
            config=_config_data(self.config),fulfillment=invalid),time.monotonic()+1)
        with patch('photobooth.post_preview_bootstrap.logging.disable'):
            self.assertEqual(2,run_child(child,readiness))
        self.assertFalse(self.config.private_root.exists())

    def retry(self,call):
        deadline=time.monotonic()+6
        while True:
            try:return call()
            except DraftHeld:
                if time.monotonic()>=deadline:raise
                time.sleep(.1)  # Original merchant pacing; never modify its clock/journal.

    def test_actual_private_child_accepts_only_original_native_receipt_then_same_proof_claim(self):
        worker,child=socket.socketpair();self.addCleanup(worker.close)
        process=SandboxBackendProcess(self.config,fulfillment=self.bundle)
        def stop():
            self.assertTrue(process.stop(timeout=8),'Original fixture child did not exit gracefully')
        self.addCleanup(stop)
        with patch('photobooth.post_preview_bootstrap.CHILD_MODULE','tests.post_preview_host_process_fixture'):
            process.start(child,timeout=20)
        self.assertNotIn(self.key.secret.hex(),' '.join(process.process.args))
        session=requests.Session();session.trust_env=False
        client=PostPreviewClient(process.endpoint,'PB001',self.config.booth_token,
            expected_mode='sandbox',allow_local_http=True,session=session);self.addCleanup(client.close)
        service=ProtectedCheckoutService(self.config.private_root,payment_client=client,
            qr_loader=lambda _:Image.new('RGB',(200,200),'white'));self.addCleanup(service.ledger.close)
        from photobooth.catalog import get_templates
        templates=get_templates();service.start(templates,{'template_a':1})
        frame=np.zeros((24,32,3),dtype=np.uint8)
        for _ in range(3):
            view=service.snapshot()
            service.capture(frame,view['capture_slot'],view['revision'],view['retake'],view['generation'])
        service.compose();service.next();view=service.snapshot()
        # Existing fixture freeze only; protected production freeze is still gated.
        intent=service.checkout.freeze(service.lease,templates,revision=view['revision'],
            expected_amount=view['amount'],readiness=ChargeReadiness(True,True,True,True,True,True,True,25))
        group=intent['purchase_group_id'];lease=service.lease
        jobs=PhotoJobs(service);launcher=LaunchLease(self.config.private_root);self.addCleanup(launcher.close)
        legacy=CheckoutStore(self.config.private_root/'legacy.sqlite3');self.addCleanup(legacy.close)
        ownership=OriginalWorkerReadiness(service,jobs,launcher,legacy)
        collector=LocalChargeReadiness(service.checkout,templates,probes={'worker_ownership':ownership},
            camera=CachedCamera(frame,0),printer_config=self.printer,
            printer_dial=lambda *_:SimpleNamespace(close=lambda:None))
        server=WorkerReadinessServer.from_original_worker(worker,collector)
        server.start();self.addCleanup(server.stop)
        view=service.accept_frozen_checkout(group);proof=view['ccp_offer'].qr_payload
        service.ccp_visible(view['ccp_offer']);service.begin_payment()
        def settled():
            view=service.check_payment('connectivity')
            if service.phase!='paid_hold':raise DraftHeld('Original settlement pacing')
            return view
        self.retry(settled)
        self.assertEqual('paid_hold',service.phase)
        view=service.prepare_ticket();service.ticket_visible(view['ticket_offer'])
        service.ticket_send_receipt();service.ticket_dismiss()
        service.retire('RESULT_TIMEOUT')
        handoff=PostPreviewHandoffClient(client)
        prepared=self.retry(lambda:handoff.prepare(replace(lease,generation=lease.generation+1)))
        with self.assertRaises(DraftHeld):handoff.acknowledge(prepared)
        native=NativeWorkerRetirement(jobs,server,launcher,self.key)
        native.publish(prepared.operation_id,timeout=1)
        self.assertEqual('ACKED',self.retry(lambda:handoff.acknowledge(prepared)).state)
        fresh=ProtectedCheckoutService(self.config.private_root,payment_client=client,
            qr_loader=lambda _:Image.new('RGB',(200,200),'white'));self.addCleanup(fresh.ledger.close)
        request=uuid.uuid4().hex
        restored=self.retry(lambda:fresh.claim_original(group,proof,request))
        self.assertEqual('paid_hold',restored['phase']);self.assertTrue(restored['ticket_dismissed'])
        self.assertEqual(4,fresh.lease.generation)
        self.assertEqual('1',(self.config.private_root/'fixture-output-send-count').read_text())
        self.assertEqual(1,fresh.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
        self.assertEqual(1,fresh.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])
        self.assertEqual('OWED',restored['payment']['obligation_state'])
        self.assertTrue(process.stop(timeout=8))
        for name in ('drafts.sqlite3','drafts.sqlite3-wal','host-context.json'):
            path=self.config.private_root/name
            if path.exists():self.assertNotIn(self.key.secret.hex().encode(),path.read_bytes())


if __name__=='__main__':unittest.main()
