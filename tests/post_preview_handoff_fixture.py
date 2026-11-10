"""Protected handoff fixture: original API/core, separate native/backend DBs."""
import socket
from unittest.mock import patch

from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_authority import OriginalWorkerReadiness
from photobooth.post_preview_ccp import OriginalCCPService
from photobooth.post_preview_checkout import PrivateDraftCheckout
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_readiness import LocalChargeReadiness
from photobooth.post_preview_readiness_bridge import WorkerReadinessServer
from photobooth.post_preview_sandbox_handoff import OriginalSandboxIsolation,OriginalSandboxClaim
from photobooth.post_preview_store import PostPreviewStore
from photobooth.post_preview_worker_fence import WorkerFenceKey,WorkerReceiptVerifier,NativeWorkerRetirement
from tests.post_preview_protected_fixture import ProtectedNativeHarness


class ProtectedHandoffHarness:
    def __init__(self, owner, *, settled=True, delivery=False,
                 uncertain_receipt=False, uncertain_photo=False,retire_event=None):
        self.f=ProtectedNativeHarness(owner,{'template_a':1})
        self.source=self.f.service
        self.proof=self.ticket_proof=None
        original=self.source.ccp_visible
        original_ticket=self.source.ticket_visible
        def visible(offer):self.proof=offer.qr_payload;return original(offer)
        def ticket_visible(offer):self.ticket_proof=offer.qr_payload;return original_ticket(offer)
        self.f.uncertain=uncertain_receipt
        with patch.object(self.source,'ccp_visible',side_effect=visible),patch.object(
                self.source,'ticket_visible',side_effect=ticket_visible):
            if settled:self.f.ticket()
            else:self.f.proof();self.source.begin_payment()
        self.f.uncertain=False
        if delivery:
            self.source.prepare_paid_delivery()
            self.f.uncertain=uncertain_photo
            self.source.paid_print_next()
            self.f.uncertain=False
        native=PostPreviewStore(self.f.root/'drafts.sqlite3',now=lambda:self.f.clock[0])
        owner.addCleanup(native.close)
        self.source.ledger=native
        self.source.photos=PrivateDraftPhotos(native,self.f.root/'media')
        self.source.checkout=PrivateDraftCheckout(self.source.photos)
        self.jobs=PhotoJobs(self.source)
        self.launcher=LaunchLease(self.f.root);owner.addCleanup(self.launcher.close)
        legacy=CheckoutStore(self.f.root/'legacy.sqlite3');owner.addCleanup(legacy.close)
        authority=OriginalWorkerReadiness(self.source,self.jobs,self.launcher,legacy)
        collector=LocalChargeReadiness(self.source.checkout,self.f.templates,
                                      probes={'worker_ownership':authority})
        worker,backend=socket.socketpair();owner.addCleanup(backend.close)
        self.server=WorkerReadinessServer.from_original_worker(worker,collector)
        self.server.start();owner.addCleanup(self.server.stop)
        self.key=WorkerFenceKey.create()
        self.receipts=WorkerReceiptVerifier(self.f.ledger,self.key)
        self.payments=self.f.actor.binder.payments
        self.isolation=OriginalSandboxIsolation(self.payments,self.f.actor,self.receipts)
        self.native=NativeWorkerRetirement(self.jobs,self.server,self.launcher,self.key)
        ticket=self.f.actor.binder.presentation.credentials
        self.claim=OriginalSandboxClaim(self.payments,
            OriginalCCPService(self.f.ledger,ticket.protector,'MTEST'),ticket)
        self.source.retire(retire_event or ('RESULT_TIMEOUT' if settled else 'APP_SUSPENDED'))

    def prepare(self):
        self.f.clock[0]+=2
        return self.isolation.prepare('PB001')

    def ack(self, operation):
        self.native.publish(operation,timeout=1)
        self.f.clock[0]+=2
        return self.isolation.acknowledge('PB001',operation)

    def recover(self, payload=None):
        self.f.clock[0]+=2
        return self.claim.claim(self.f.group,'PB001',self.proof if payload is None else payload)
