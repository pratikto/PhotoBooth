"""Real protected facade/API, explicit fake merchant/Drive/key lookup/paper."""
import io
import json
import os
import socket
import tempfile
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from photobooth.booth_storage import BoothWorkspace
from photobooth.booth_sync import BoothDriveClient
from photobooth.catalog import get_templates
from photobooth.drive_storage import AppsScriptDriveClient
from photobooth.kiosk_v2.post_preview_protected_checkout import ProtectedCheckoutService
from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_readiness import ReadOnlyDriveReadiness
from photobooth.post_preview_readiness_bridge import WorkerReadinessClient, WorkerReadinessServer
from photobooth.post_preview_server import build_sandbox_app
from photobooth.printer import NetworkSendError, PrinterConfig, ThermalPrinter
from tests.post_preview_checkout_fixture import SessionAdapter
from tests.test_post_preview_payments import SyntheticProvider
from tests.test_post_preview_readiness import _bridge_ready


class ProtectedNativeHarness:
    def __init__(self, owner, quantities=None):
        temporary = tempfile.TemporaryDirectory()
        owner.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.clock = [1000.]
        self.client = PostPreviewClient('https://fixture.invalid', 'PB001', 'x'*48,
                                        expected_mode='sandbox')
        owner.addCleanup(self.client.close)
        self.service = ProtectedCheckoutService(self.root, payment_client=self.client,
            qr_loader=lambda _: Image.new('RGB', (200,200), 'white'))
        owner.addCleanup(self.service.ledger.close)
        self.ledger = self.service.ledger
        self.ledger.now = lambda: self.clock[0]
        self.templates = get_templates()
        self.service.start(self.templates, quantities or {'template_a':2, 'template_b':1})
        self.frame = np.zeros((32,48,3), dtype=np.uint8)
        self.frame[:,:24,0] = 200
        for _ in range(len(self.service.selected)):
            for _ in range(3):
                view = self.service.snapshot()
                self.service.capture(self.frame, view['capture_slot'], view['revision'],
                                     view['retake'], view['generation'])
            self.service.compose()
            self.service.next()
        # Existing trusted freeze primitive; this explicit fixture observation
        # is NOT a production native/backend freeze mounting or readiness claim.
        view = self.service.snapshot()
        self.intent = self.service.checkout.freeze(self.service.lease, self.templates,
            revision=view['revision'], expected_amount=view['amount'],
            readiness=ChargeReadiness(True,True,True,True,True,True,True,25))
        self.group = self.intent['purchase_group_id']
        self.lease = self.service.lease
        worker, backend = socket.socketpair()
        self.server = WorkerReadinessServer(worker, lambda scope: _bridge_ready(scope, self.clock[0]))
        self.server.start()
        self.bridge = WorkerReadinessClient(backend, timeout=2)
        owner.addCleanup(self.server.stop)
        owner.addCleanup(self.bridge.close)
        self.workspace = BoothWorkspace(self.root/'storage', 'PB001V2S2')
        self.workspace.prepare()
        self.binds = []
        self.bad_link = self.lost_bind = False
        def drive_post(_url, **kwargs):
            body = kwargs['json']
            if body['action'] == 'storage_readiness':
                result = dict(protocol_version=1,booth_id='PB001V2S2',read_only=True,
                    drive_api='READY',drive_sharing='READY',capacity_state='READY',
                    ready_count=25,checked_count=len(body['slots']))
                return SimpleNamespace(status_code=200,json=lambda:dict(ok=True,storage_layout=2,readiness=result))
            assert body['action'] == 'bind_transaction'
            self.binds.append(body['transaction_id'])
            if self.lost_bind:
                self.lost_bind=False
                raise OSError('Synthetic lost binding reply')
            return SimpleNamespace(status_code=200,json=lambda:dict(ok=True,storage_layout=2,
                photo_number_layout=1,transaction_id=body['transaction_id'],
                folder_id='syntheticNativeB5',folder_url='https://drive.google.com/drive/folders/syntheticNativeB5',
                link_verified=not self.bad_link))
        drive = BoothDriveClient(AppsScriptDriveClient(
            'https://script.google.com/macros/s/B5_FIXTURE/exec', 'synthetic-drive',
            session=SimpleNamespace(post=drive_post)), 'PB001V2S2')
        self.probe = ReadOnlyDriveReadiness(drive,self.workspace,now=self.ledger.now)
        self.remote = SyntheticProvider()
        def transport(request, timeout):
            assert request.full_url.startswith('https://api.sandbox.midtrans.com/v2/')
            if request.get_method() == 'POST' and request.full_url.endswith('/charge'):
                data = json.loads(request.data)['transaction_details']
                result = self.remote.create_qris(data['order_id'],data['gross_amount'])
            else:
                order, action = request.full_url.split('/')[-2:]
                result = self.remote.get_status(order) if action == 'status' else self.remote.cancel(order)
            return io.BytesIO(json.dumps(result).encode())
        self.sends = []
        self.uncertain = False
        self.receipt_entered = self.receipt_release = None
        lane = threading.Lock()
        def send(_host,_port,payload):
            assert lane.locked()
            self.sends.append(len(payload))  # Never retain private raster/bytes.
            if self.receipt_entered is not None:
                self.receipt_entered.set()
                assert self.receipt_release.wait(10)
            if self.uncertain:
                raise NetworkSendError('Synthetic partial bytes')
        printer = ThermalPrinter(PrinterConfig(lan_host='synthetic-b5'),network_sender=send)
        # Linux control-flow ONLY. Windows still uses actual current-user DPAPI.
        if os.name != 'nt':
            custody = patch('photobooth.linux_credential_vault._read_key',return_value=b'k'*32)
            custody.start();owner.addCleanup(custody.stop)
        self.app = build_sandbox_app(self.service.checkout,self.templates,self.bridge,self.probe,
            merchant_id='MTEST',server_key='Mid-server-SYNTHETIC',booth_id='PB001',booth_token='x'*48,
            provider_transport=transport,background_worker=False,receipt_printer=printer,
            printer_lane=lane,paid_delivery_enabled=True)
        # Backend worker identity is real; scheduling external upload is stubbed.
        self.actor = self.app.state.paid_delivery
        self.actor.worker.start = lambda: None
        self.actor.worker.notify_transaction = lambda _: None
        owner.addCleanup(self.actor.stop)
        self.http = TestClient(self.app)
        owner.addCleanup(self.http.close)
        self.client._transport.session.close()
        self.client._transport.session = SessionAdapter(self.http)

    def proof(self):
        view = self.service.accept_frozen_checkout(self.group)
        return self.service.ccp_visible(view['ccp_offer'])

    def paid(self):
        self.proof()
        pending = self.service.begin_payment()
        assert pending['phase'] == 'payment_pending', pending['phase']
        self.remote.state(pending['payment']['attempts'][-1]['provider_order_id'],'settlement')
        self.clock[0] += 10
        return self.service.check_payment('connectivity')

    def ticket(self):
        self.paid()
        view = self.service.prepare_ticket()
        self.service.ticket_visible(view['ticket_offer'])
        self.service.ticket_send_receipt()
        return self.service.ticket_dismiss()
