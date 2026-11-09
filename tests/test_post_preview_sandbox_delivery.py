"""Protected backend delivery using original cores and fake transport only."""
from dataclasses import replace
from types import SimpleNamespace
import threading
import unittest

from photobooth.booth_sync import BoothDriveClient
from photobooth.drive_storage import AppsScriptDriveClient
from photobooth.post_preview_paid_drive import OriginalPaidDriveBinding
from photobooth.post_preview_paid_media import OriginalPaidMediaImporter
from photobooth.post_preview_paid_strips import OriginalPaidStripPreparer
from photobooth.post_preview_paid_print import OriginalPaidPrintDispatcher
from photobooth.post_preview_paid_delivery import OriginalPaidDeliveryMonitor
from photobooth.post_preview_readiness import ReadOnlyDriveReadiness
from photobooth.post_preview_sandbox_delivery import OriginalSandboxPaidDriveBinding
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_ticket_presentation import OriginalRecoveryPresentation
from photobooth.printer import ThermalPrinter,PrinterConfig,NetworkSendError


class SandboxPaidDeliveryTests(unittest.TestCase):
    def setUp(self):
        # Actual fixed Sandbox HTTP/coordinator/API; Windows uses real DPAPI,
        # Linux uses the existing explicitly wrapped in-memory custody fixture.
        from tests.test_post_preview_api import SandboxBackendAssemblyTests
        self.h=SandboxBackendAssemblyTests(methodName='runTest');self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.payments=self.h.app.state.notification_inbox.payments
        self.ledger,self.lease,self.group=self.h.ledger,self.h.lease,self.h.group
        self.bind_requests=[];self.bad_link=False;self.lose_reply=False
        def post(_url,**kwargs):
            body=kwargs['json']
            self.assertEqual('bind_transaction',body['action'])
            self.bind_requests.append(body['transaction_id'])
            if self.lose_reply:
                self.lose_reply=False
                raise OSError('Synthetic accepted folder response loss')
            data=dict(ok=True,storage_layout=2,photo_number_layout=1,
                transaction_id=body['transaction_id'],folder_id='syntheticPaidFolderB4',
                folder_url='https://drive.google.com/drive/folders/syntheticPaidFolderB4',
                link_verified=not self.bad_link)
            return SimpleNamespace(status_code=200,json=lambda:data)
        drive=AppsScriptDriveClient('https://script.google.com/macros/s/B4_FIXTURE/exec',
            'synthetic-not-a-cloud-key',session=SimpleNamespace(post=post))
        client=BoothDriveClient(drive,'PB001V2S2')
        self.probe=ReadOnlyDriveReadiness(client,self.h.workspace,now=self.ledger.now)
        self.sends=0;self.uncertain=False
        self.lane=threading.Lock()
        def send(_host,_port,_payload):
            self.assertTrue(self.lane.locked())
            self.sends+=1
            if self.uncertain:raise NetworkSendError('Synthetic partial bytes')
        self.printer=ThermalPrinter(PrinterConfig(lan_host='synthetic-B4-no-device'),
            network_sender=send,usb_sender=lambda _:self.fail('No fallback'))
        self.presentation=OriginalRecoveryPresentation(
            OriginalRecoveryTicketService(self.payments,self.h.protector),
            printer=self.printer,shared_lane=self.lane)
        self.binder=self.new_binder()

    def new_binder(self):
        return OriginalSandboxPaidDriveBinding(self.payments,self.h.checkout,self.probe,self.presentation)

    def paid(self):
        pending=self.h.call('/begin').json()
        self.h.remote.state(self.h.order(pending),'settlement');self.h.clock[0]+=10
        self.assertTrue(self.h.call('/reconcile',{'trigger':'connectivity'}).json()['paid_verified'])

    def ticket(self,*,uncertain=False):
        self.paid()
        offer=self.presentation.offer(self.group,self.lease)
        self.presentation.visible(self.group,self.lease,offer.presentation_id)
        self.uncertain=uncertain
        self.presentation.receipt(self.group,self.lease,offer.presentation_id)
        self.uncertain=False
        self.presentation.dismiss(self.group,self.lease,offer.presentation_id)
        self.assertEqual(1,self.sends)

    def bind(self,binder=None):
        self.h.clock[0]+=31  # Exercise stale GET through the original polling floor.
        return (binder or self.binder).bind(self.lease,self.group,self.h.templates)

    def core(self):
        importer=OriginalPaidMediaImporter(self.binder)
        preparer=OriginalPaidStripPreparer(importer)
        return OriginalPaidDeliveryMonitor(preparer),OriginalPaidPrintDispatcher(preparer)

    def test_construction_has_no_provider_drive_or_printer_effect(self):
        self.core()
        self.assertEqual([],self.h.requests);self.assertEqual([],self.bind_requests)
        self.assertEqual(0,self.sends)
        self.assertFalse(self.h.http.get('/api/postpay/health').json()['fulfillment_enabled'])

    def test_original_mock_constructor_cannot_select_sandbox_with_fixture_flag(self):
        with self.assertRaises(DraftHeld):
            OriginalPaidDriveBinding(self.payments,self.h.checkout,self.h.workspace,
                self.probe.client,allow_incomplete_fixture=True)
        with self.assertRaises(DraftHeld):OriginalPaidMediaImporter(self.binder,allow_incomplete_fixture=True)

    def test_self_described_dependencies_and_wrong_backend_identity_are_refused(self):
        with self.assertRaises(DraftHeld):
            OriginalSandboxPaidDriveBinding(self.payments,self.h.checkout,
                SimpleNamespace(client=self.probe.client,workspace=self.h.workspace),self.presentation)
        original=self.presentation.credentials.payments
        try:
            self.presentation.credentials.payments=SimpleNamespace(mode='sandbox')
            with self.assertRaises(DraftHeld):self.new_binder()
        finally:self.presentation.credentials.payments=original
        self.assertEqual([],self.bind_requests)

    def test_unpaid_or_undismissed_ticket_does_not_consume_a_ready_folder(self):
        with self.assertRaises(DraftHeld):self.binder.bind(self.lease,self.group,self.h.templates)
        self.paid()
        with self.assertRaises(DraftHeld):self.binder.bind(self.lease,self.group,self.h.templates)
        offer=self.presentation.offer(self.group,self.lease)
        self.presentation.visible(self.group,self.lease,offer.presentation_id)
        with self.assertRaises(DraftHeld):self.binder.bind(self.lease,self.group,self.h.templates)
        self.assertEqual([],self.bind_requests)
        self.assertIsNone(self.ledger.db.execute('SELECT transaction_id FROM pp_paid_services').fetchone()[0])

    def test_fresh_independent_paid_get_and_restart_keep_one_original_folder(self):
        self.ticket();reads=self.h.remote.reads
        first=self.bind();second=self.bind(self.new_binder())
        self.assertEqual(first,second);self.assertGreaterEqual(self.h.remote.reads,reads+2)
        self.assertEqual(1,len(self.bind_requests));self.assertEqual(1,self.h.remote.charges)
        self.assertEqual(25,len(self.h.workspace.ready_slots()))
        self.assertEqual('OWED',self.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_lost_bind_response_retries_same_original_transaction_not_another_slot(self):
        self.ticket();self.lose_reply=True
        with self.assertRaises(DraftHeld):self.bind()
        original=self.bind_requests[0]
        self.assertEqual('UNKNOWN',self.ledger.db.execute('SELECT drive_state FROM pp_paid_services').fetchone()[0])
        self.assertEqual(original,self.bind()['transaction_id'])
        self.assertEqual([original,original],self.bind_requests)

    def test_unverified_link_and_lost_payment_authority_cannot_prepare_media(self):
        self.ticket();self.bad_link=True
        with self.assertRaises(DraftHeld):self.bind()
        self.assertFalse(list(self.h.workspace.root.rglob('strip.png')))
        self.bad_link=False;self.h.remote.outage=True
        with self.assertRaises(DraftHeld):self.bind()
        self.assertEqual(1,len(self.bind_requests))

    def test_wrong_owner_generation_and_retirement_precede_any_cloud_effect(self):
        self.ticket()
        for lease in (replace(self.lease,generation=2),replace(self.lease,booth_id='PB002')):
            with self.assertRaises(DraftHeld):self.binder.bind(lease,self.group,self.h.templates)
        self.payments.signal_lifecycle(self.lease,'APP_SUSPENDED')
        with self.assertRaises(DraftHeld):self.bind()
        self.assertEqual([],self.bind_requests)

    def test_original_media_strip_pending_upload_and_once_only_print_reuse_same_lane(self):
        self.ticket();bound=self.bind();monitor,dispatcher=self.core()
        pending=monitor.enqueue(self.lease,self.group,self.h.templates)
        self.assertEqual(bound['folder_url'],pending['folder_url'])
        self.assertEqual('NOT_CONFIGURED',pending['worker']);self.assertFalse(pending['drive_verified'])
        self.assertFalse(pending['physical_paper_verified'])
        result=dispatcher.send_once(self.lease,self.group,'template_a',self.printer,shared_lane=self.lane)
        self.assertEqual('SUBMITTED',result['state']);self.assertEqual(2,self.sends)
        with self.assertRaises(DraftHeld):
            dispatcher.send_once(self.lease,self.group,'template_a',self.printer,shared_lane=self.lane)
        self.assertEqual(2,self.sends)
        self.assertTrue(monitor.inspect(self.lease,self.group)['print_all_submitted'])

    def test_foreign_printer_lane_is_rejected_before_photo_bytes(self):
        self.ticket();self.bind();monitor,dispatcher=self.core()
        monitor.enqueue(self.lease,self.group,self.h.templates)
        with self.assertRaises(DraftHeld):
            dispatcher.send_once(self.lease,self.group,'template_a',self.printer,shared_lane=threading.Lock())
        self.assertEqual(1,self.sends)
        self.assertEqual('PREPARED',self.ledger.db.execute('SELECT state FROM pp_paid_strip_jobs').fetchone()[0])

    def test_uncertain_original_receipt_blocks_binding_without_pool_consumption(self):
        self.ticket(uncertain=True)
        with self.assertRaises(DraftHeld):self.bind()
        self.assertEqual([],self.bind_requests)

    def test_immediate_ticket_next_reuses_recent_get_without_breaking_provider_poll_floor(self):
        self.ticket();reads=self.h.remote.reads
        self.binder.bind(self.lease,self.group,self.h.templates)
        self.assertEqual(reads,self.h.remote.reads)
        self.assertEqual(1,len(self.bind_requests))

    def test_missing_os_custody_type_and_changed_provider_cannot_select_delivery(self):
        from photobooth.credential_vault import SyntheticAeadProtector
        original=self.presentation.credentials.protector
        try:
            self.presentation.credentials.protector=SyntheticAeadProtector(b'a'*32,fixture=True)
            with self.assertRaises(DraftHeld):self.new_binder()
        finally:self.presentation.credentials.protector=original
        original=self.payments.provider
        try:
            self.payments.provider=SimpleNamespace(mode='sandbox')
            with self.assertRaises(DraftHeld):self.new_binder()
        finally:self.payments.provider=original

    def test_partial_photo_bytes_remain_uncertain_and_owed_without_replay(self):
        self.ticket();self.bind();monitor,dispatcher=self.core()
        monitor.enqueue(self.lease,self.group,self.h.templates);self.uncertain=True
        result=dispatcher.send_once(self.lease,self.group,'template_a',self.printer,shared_lane=self.lane)
        self.assertEqual('UNCERTAIN',result['state']);self.assertEqual(2,self.sends)
        with self.assertRaises(DraftHeld):
            dispatcher.send_once(self.lease,self.group,'template_a',self.printer,shared_lane=self.lane)
        self.assertEqual(2,self.sends);self.assertTrue(monitor.inspect(self.lease,self.group)['needs_operator_review'])
        self.assertEqual('OWED',self.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])


if __name__=='__main__':unittest.main()
