"""Original PAID folder reservation identity: no replay, no pool leakage."""
from pathlib import Path
import tempfile
import unittest

from photobooth.booth_storage import BoothWorkspace


class OriginalPaidDriveReservationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.workspace=BoothWorkspace(self.root,'PB001V2S2')
        self.workspace.prepare()

    def test_exact_original_claim_and_restart_return_same_reserved_folder(self):
        original=self.workspace.ready_slots()[0]
        first=self.workspace.claim_exact(original['transaction_id'],original['claim_token'])
        self.assertEqual(original['transaction_id'],first['transaction_id'])
        self.assertTrue(Path(first['staging_path']).is_dir())
        self.assertEqual(25,len(self.workspace.ready_slots()))
        restarted=BoothWorkspace(self.root,'PB001V2S2')
        again=restarted.claim_exact(original['transaction_id'],original['claim_token'])
        self.assertEqual(first,again)
        self.assertEqual(25,len(restarted.ready_slots()))
        self.assertNotIn(original['transaction_id'],
                         {s['transaction_id'] for s in restarted.ready_slots()})

    def test_other_claim_token_and_foreign_booth_identity_are_rejected(self):
        original=self.workspace.ready_slots()[0]
        with self.assertRaises(ValueError):
            self.workspace.claim_exact(original['transaction_id'],'f'*32)
        with self.assertRaises(ValueError):
            self.workspace.claim_exact('PB002V2S2_00000001',original['claim_token'])
        self.assertEqual(25,len(self.workspace.ready_slots()))

    def test_cannot_skip_reserve_queue_head_or_claim_nonempty_slot(self):
        original, later=self.workspace.ready_slots()[:2]
        with self.assertRaises(ValueError):
            self.workspace.claim_exact(later['transaction_id'],later['claim_token'])
        path=self.workspace.root/original['transaction_id']
        (path/'foreign.jpg').write_bytes(b'OTHER')
        with self.assertRaises(ValueError):
            self.workspace.claim_exact(original['transaction_id'],original['claim_token'])
        self.assertEqual(25,len(self.workspace.ready_slots()))

    def test_missing_previously_claimed_path_fails_closed(self):
        original=self.workspace.ready_slots()[0]
        self.workspace.claim_exact(original['transaction_id'],original['claim_token'])
        (self.workspace.root/original['transaction_id']).rmdir()
        with self.assertRaises(ValueError):
            self.workspace.claim_exact(original['transaction_id'],original['claim_token'])
        self.assertEqual(25,len(self.workspace.ready_slots()))



    def paid_fixture(self):
        """Use the original synthetic merchant, media and source payment states."""
        import numpy as np
        from tests.post_preview_checkout_fixture import CheckoutFixture
        from photobooth.catalog import get_templates
        fixture=CheckoutFixture(self.root/'postpay')
        self.addCleanup(fixture.close)
        fixture.enable_paid_ticket()  # Explicit authority must be attached BEFORE checkout admission.
        service=fixture.service
        frame=np.zeros((32,48,3),dtype=np.uint8)
        service.prepare()
        view=service.start(get_templates(),{'template_a':1})
        for _ in range(3):
            view=service.capture(frame,view['capture_slot'],view['revision'],view['retake'],view['generation'])
        service.compose()
        view=service.next()
        view=service.freeze_checkout(view['revision'],view['amount'])
        service.ccp_visible(view['ccp_offer'])
        view=service.begin_payment()
        self.assertEqual('payment_pending',view['phase'])
        fixture.provider.state(view['payment']['attempts'][0]['provider_order_id'],'settlement')
        service.check_payment('connectivity')
        fixture.ticket.prepare(service.lease)
        return fixture

    def binder(self,fixture):
        from photobooth.post_preview_paid_drive import OriginalPaidDriveBinding
        return OriginalPaidDriveBinding(
            fixture.backend,fixture.service.checkout,self.workspace,fixture.drive,
            allow_incomplete_fixture=True)

    def test_original_paid_drive_binding_once_and_same_url_after_restart(self):
        from unittest.mock import patch
        fixture=self.paid_fixture()
        sent=[]
        def bind(manifest):
            sent.append(dict(manifest))
            return dict(transaction_id=manifest['transaction_id'],
                        folder_id='syntheticAAA123',photo_number_layout=1,link_verified=True,
                        folder_url='https://drive.google.com/drive/folders/syntheticAAA123')
        with patch.object(fixture.drive,'bind_transaction',side_effect=bind):
            first=self.binder(fixture).bind(
                fixture.service.lease,fixture.service.group,fixture.service.templates)
            second=self.binder(fixture).bind(
                fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertEqual(first,second)
        self.assertEqual('VERIFIED',first['drive_state'])
        self.assertEqual(1,len(sent))
        self.assertEqual('OWED',fixture.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        self.assertEqual(25,len(self.workspace.ready_slots()))
        self.assertFalse(any((self.workspace.root/slot['transaction_id']).is_file()
                             for slot in self.workspace.ready_slots()))

    def test_paid_drive_network_failure_holds_original_claim_and_never_claims_second(self):
        from unittest.mock import patch
        fixture=self.paid_fixture()
        bind=self.binder(fixture)
        with patch.object(fixture.drive,'bind_transaction',side_effect=OSError('synthetic outage')):
            with self.assertRaisesRegex(Exception,'must be verified'):
                bind.bind(fixture.service.lease,fixture.service.group,fixture.service.templates)
        row=fixture.service.ledger.db.execute('SELECT * FROM pp_paid_services').fetchone()
        self.assertEqual('UNKNOWN',row['drive_state'])
        first=row['transaction_id']
        self.assertEqual(25,len(self.workspace.ready_slots()))
        def success(manifest):
            self.assertEqual(first,manifest['transaction_id'])
            return dict(transaction_id=first,folder_id='syntheticBBB456',
                        folder_url='https://drive.google.com/drive/folders/syntheticBBB456',
                        photo_number_layout=1,link_verified=True)
        with patch.object(fixture.drive,'bind_transaction',side_effect=success):
            result=bind.bind(fixture.service.lease,fixture.service.group,fixture.service.templates)
        self.assertEqual(first,result['transaction_id'])
        self.assertEqual('VERIFIED',result['drive_state'])
        self.assertEqual(25,len(self.workspace.ready_slots()))

    def test_wrong_folder_url_mismatch_cannot_be_marked_verified(self):
        from unittest.mock import patch
        fixture=self.paid_fixture()
        binder=self.binder(fixture)
        def wrong(manifest):
            return dict(transaction_id=manifest['transaction_id'],folder_id='syntheticZZZ',
                        folder_url='https://attacker.invalid/foreign',link_verified=True,
                        photo_number_layout=1)
        with patch.object(fixture.drive,'bind_transaction',side_effect=wrong):
            with self.assertRaisesRegex(Exception,'must be verified'):
                binder.bind(fixture.service.lease,fixture.service.group,fixture.service.templates)
        row=fixture.service.ledger.db.execute('SELECT drive_state,folder_id,folder_url FROM pp_paid_services').fetchone()
        self.assertEqual(('UNKNOWN',None,None),tuple(row))

    def test_unpaid_draft_cannot_claim_any_ready_folder(self):
        from photobooth.post_preview_paid_drive import OriginalPaidDriveBinding
        from tests.post_preview_checkout_fixture import CheckoutFixture
        fixture=CheckoutFixture(self.root/'unpaid')
        self.addCleanup(fixture.close)
        binder=OriginalPaidDriveBinding(
            fixture.backend,fixture.service.checkout,self.workspace,fixture.drive,
            allow_incomplete_fixture=True)
        before=self.workspace.ready_slots()
        with self.assertRaises(Exception):
            binder.bind(fixture.service.lease,'f'*32,[])
        self.assertEqual(before,self.workspace.ready_slots())

    def test_missing_remote_binding_never_fabricates_customer_url(self):
        from unittest.mock import patch
        fixture=self.paid_fixture()
        with patch.object(fixture.drive,'bind_transaction',return_value={
                'transaction_id':'wrong','folder_id':'other','link_verified':True,
                'photo_number_layout':1,'folder_url':'https://drive.google.com/drive/folders/other'}):
            with self.assertRaises(Exception):
                self.binder(fixture).bind(fixture.service.lease,fixture.service.group,fixture.service.templates)
        row=fixture.service.ledger.db.execute('SELECT folder_url,status FROM pp_paid_services').fetchone()
        self.assertIsNone(row['folder_url'])
        self.assertEqual('OWED',row['status'])

if __name__=='__main__': unittest.main()
