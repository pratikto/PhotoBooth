"""Real HTTP boundary with isolated synthetic provider/camera/vault adapters."""
import os
import threading
from types import SimpleNamespace
from PIL import Image
from fastapi.testclient import TestClient
from photobooth.booth_auth import BoothAuthenticator
from photobooth.credential_vault import SyntheticAeadProtector
from photobooth.post_preview_api import create_app
from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.kiosk_v2.post_preview_checkout import PrivateCheckoutService
from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.checkout_store import CheckoutStore
from photobooth.booth_storage import BoothWorkspace
from photobooth.booth_sync import BoothDriveClient
from photobooth.drive_storage import AppsScriptDriveClient
from photobooth.printer import PrinterConfig
from photobooth.post_preview_authority import OriginalWorkerReadiness, authenticated_payment_readiness
from photobooth.post_preview_readiness import LocalChargeReadiness, ReadOnlyDriveReadiness
from tests import test_post_preview_payments as payment_fixtures


class ResponseAdapter:
    def __init__(self, response):
        self.response, self.status_code = response, response.status_code

    def iter_content(self, size):
        return self.response.iter_bytes(size)

    def close(self):
        self.response.close()


class SessionAdapter:
    def __init__(self, client):
        self.client = client
        self.lose_response = False

    def request(self, method, url, **kwargs):
        assert kwargs.pop('allow_redirects') is False
        assert kwargs.pop('stream') is True
        response = self.client.request(method, url, follow_redirects=False, **kwargs)
        if self.lose_response:
            self.lose_response = False
            response.close()
            raise OSError('Synthetic HTTP response loss')
        return ResponseAdapter(response)

    def close(self):
        self.client.close()


class CheckoutFixture:
    def __init__(self, root, *, protector=None, windows_protected_mock=False):
        self.ready = ChargeReadiness(True, True, True, True, True, True, True, 25)
        self.client = PostPreviewClient('https://fixture.invalid', 'PB001', 'SYNTHETIC-BOOTH-'+'a'*48,
                                        expected_mode='mock')
        self.protector = protector if protector is not None else SyntheticAeadProtector(os.urandom(32), fixture=True)
        self.service = PrivateCheckoutService(root, payment_client=self.client, protector=self.protector,
            merchant_id='MTEST', readiness=lambda: self.ready,
            qr_loader=lambda _: Image.new('RGB', (180,180), 'white'), allow_incomplete_fixture=True,
            allow_windows_protected_mock=windows_protected_mock)
        self.jobs = PhotoJobs(self.service)
        self.launch_lease = LaunchLease(root)
        self.legacy = CheckoutStore(root/'legacy-fixture.sqlite3')
        self.authority = OriginalWorkerReadiness(self.service, self.jobs, self.launch_lease, self.legacy)
        self.workspace = BoothWorkspace(root/'synthetic-drive', 'PB001V2S2')
        self.workspace.prepare()
        self.camera = SimpleNamespace(capture=SimpleNamespace(isOpened=lambda: True), read=lambda: object())
        self.drive = BoothDriveClient(AppsScriptDriveClient(
            'https://script.google.com/macros/s/SYNTHETIC/exec', 'SYNTHETIC-NONDEPLOYED',
            session=SimpleNamespace(post=self._drive_read)), 'PB001V2S2')
        self.provider = payment_fixtures.SyntheticProvider()
        self.backend = PostPreviewPayments(self.service.ledger, self.provider, 'MTEST',
            readiness=self._readiness, poll_seconds=0)
        auth = BoothAuthenticator({'PB001':'SYNTHETIC-BOOTH-'+'a'*48})
        self.http = TestClient(create_app(self.backend, auth))
        self.session = SessionAdapter(self.http)
        self.client._transport.session.close()
        self.client._transport.session = self.session

    def enable_paid_ticket(self):
        """Synthetic original ticket and bitmap-only receipt; no device or network."""
        from photobooth.post_preview_ticket import OriginalRecoveryTicketService
        if hasattr(self,'ticket'):
            raise AssertionError('Original paid ticket already bound')
        self.ticket = OriginalRecoveryTicketService(
            self.backend,self.protector,allow_synthetic=True)
        self.receipt_sizes = []
        self.receipt_entered = self.receipt_release = None
        def send(bitmap, *, copies):
            assert copies == 1 and bitmap.mode == '1'
            if self.receipt_entered is not None: self.receipt_entered.set()
            if self.receipt_release is not None: self.receipt_release.wait(10)
            self.receipt_sizes.append(bitmap.size)  # never store bitmap/token
            return SimpleNamespace(success=True)
        printer=SimpleNamespace(config=SimpleNamespace(print_width_dots=576),
                                print_bitmap=send)
        self.service.attach_paid_ticket(
            self.ticket, printer=printer, shared_lane=threading.Lock())


    def enable_paid_delivery(self, *, real_drive=False):
        """Synthetic payment, optional opt-in actual Drive transport for pilot."""
        from photobooth.post_preview_paid_drive import OriginalPaidDriveBinding
        from photobooth.post_preview_paid_media import OriginalPaidMediaImporter
        from photobooth.post_preview_paid_strips import OriginalPaidStripPreparer
        from photobooth.post_preview_paid_delivery import OriginalPaidDeliveryMonitor
        from photobooth.post_preview_paid_print import OriginalPaidPrintDispatcher
        if not hasattr(self,'ticket') or hasattr(self,'paid_monitor'):
            raise AssertionError('One original paid ticket fixture required first')
        def simulated_remote(manifest):
            # The supervised pilot can serve more than one visitor in the
            # same process. Reusing a folder across distinct transaction IDs
            # correctly trips the original binder's privacy guard. Keep the
            # historical first fixture URL, then allocate stable unique fakes.
            transaction=manifest['transaction_id']
            first=self.workspace.booth_id+'_00000001'
            folder='syntheticPaidFolder123'+('' if transaction==first else '_'+transaction)
            return {'transaction_id':manifest['transaction_id'],
                    'folder_id':folder,
                    'folder_url':'https://drive.google.com/drive/folders/'+folder,
                    'link_verified':True,'photo_number_layout':1}
        # Only an explicit pilot override may use the actual Apps Script
        # client. Default unit tests keep every cloud operation synthetic.
        if not real_drive:
            self.drive.bind_transaction=simulated_remote
        self.paid_binder=OriginalPaidDriveBinding(
            self.backend,self.service.checkout,self.workspace,self.drive,
            allow_incomplete_fixture=True)
        importer=OriginalPaidMediaImporter(self.paid_binder,allow_incomplete_fixture=True)
        preparer=OriginalPaidStripPreparer(importer,allow_incomplete_fixture=True)
        from photobooth.booth_sync import BoothDriveWorker
        worker=BoothDriveWorker(self.workspace,self.drive) if real_drive else None
        self.paid_monitor=OriginalPaidDeliveryMonitor(
            preparer,worker=worker,allow_incomplete_fixture=True)
        self.paid_dispatcher=OriginalPaidPrintDispatcher(
            preparer,allow_incomplete_fixture=True)
        self.paid_print_sends=[]
        def photo_send(path,*,copies):
            self.paid_print_sends.append((str(path),copies))
            return SimpleNamespace(success=True)
        printer=SimpleNamespace(print_image=photo_send)
        self.service.attach_paid_delivery(
            self.paid_monitor,self.paid_dispatcher,printer=printer,
            shared_lane=self.service._receipt_lane)

    def _drive_read(self, _url, **kwargs):
        body = kwargs['json']
        if body['action'] != 'storage_readiness':
            raise AssertionError('Fixture readiness must not mutate Drive')
        count = self.ready.unclaimed_ready_capacity
        count = min(count, len(body['slots'])) if type(count) is int and count > 0 else 0
        api = 'READY' if self.ready.drive_authenticated else 'NOT_READY'
        sharing = 'READY' if self.ready.drive_sharing and api == 'READY' else 'NOT_READY'
        if sharing != 'READY': count = 0
        status = dict(protocol_version=1, booth_id=body['booth_id'], read_only=True,
                      drive_api=api, drive_sharing=sharing, capacity_state='READY' if count else 'NOT_READY',
                      ready_count=count, checked_count=len(body['slots']))
        return SimpleNamespace(status_code=200, json=lambda: dict(ok=True, storage_layout=2, readiness=status))

    def _readiness(self, group):
        adapter = LocalChargeReadiness(self.service.checkout, self.service.templates,
            probes={'payment_authorization': authenticated_payment_readiness,
                    'worker_ownership': self.authority}, camera=self.camera,
            printer_config=PrinterConfig(lan_host='synthetic-no-paper'),
            printer_dial=lambda *args: SimpleNamespace(close=lambda: None),
            drive_probe=ReadOnlyDriveReadiness(self.drive, self.workspace, now=self.service.ledger.now))
        return adapter(group)

    def bind_app(self, app):
        self.authority.jobs = app._photo_jobs
        self.camera = app.camera_device

    def close(self):
        self.service.close()
        self.service.wait_closed(10)
        self.client.close()
        self.legacy.close()
        self.launch_lease.close()
