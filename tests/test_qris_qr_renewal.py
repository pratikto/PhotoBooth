"""BUG-026: original HTTP/client/SQLite checkout expiry and replacement rights."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from tests.qris_v2_fixture import Fixture


class QrRenewalTests(TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.f=Fixture(self.root,recovery_pin='12345678');self.addCleanup(lambda:self.f.close())
        self.f.flow.qr_renewal_enabled=True
        self.f.service.begin({'template_a':2});self.ticket=self.f.flow.customer_ticket()
        self.f.service.ticket_saved();self.original=self.f.flow.snapshot();self.oid=self.original['order']['order_id']

    def expire(self):
        oid=self.f.flow.snapshot()['order']['order_id']
        self.f.provider.rows[oid].update(transaction_status='expire',status_code='407')
        self.f.store.db.execute('UPDATE checkouts SET check_after=0')
        self.f.flow._reconcile_at=0
        return self.f.service.check()

    def renew(self, automatic=False, ready=lambda _cart:None):
        old=self.f.flow.snapshot()
        self.f.flow.verify_qr_renewal(old['checkout_key'],automatic)
        self.f.flow.renew_expired_qr(old['checkout_key'],ready,automatic)
        return self.f.service.check()

    def reopen(self):
        provider=self.f.provider;self.f.close();self.f=Fixture(self.root,recovery_pin='12345678')
        self.f.provider=provider;self.f.backend.provider=provider;self.f.flow.qr_renewal_enabled=True

    def test_verified_expiry_archives_before_same_cart_new_key_and_new_ticket(self):
        view=self.expire();self.assertEqual(view['phase'],'CANCELLED')
        self.assertTrue(self.f.flow.expiry_auto_available);self.assertTrue(self.f.flow.expiry_proof_ready)
        archive=self.root/'visits'/(self.original['checkout_key']+'.json')
        saved=json.loads(archive.read_text());self.assertEqual(saved['order']['order_id'],self.oid)
        self.assertNotIn(self.ticket.split(':')[-1],archive.read_text())
        new=self.renew(automatic=True);ticket=self.f.flow.customer_ticket()
        self.assertNotEqual(new['checkout_key'],self.original['checkout_key'])
        self.assertNotEqual(new['order']['order_id'],self.oid);self.assertNotEqual(ticket,self.ticket)
        self.assertEqual(new['quantities'],self.original['quantities']);self.assertEqual(new['amount'],self.original['amount'])
        self.assertEqual(new['qr_replaces'],self.original['checkout_key']);self.assertEqual(new['qr_renewal_count'],1)
        self.assertTrue(new['ticket_required']);self.assertEqual(self.f.provider.charges,2)
        self.f.service.ticket_saved();self.f.paid();self.f.service.check();self.f.flow.lock_customer()
        with self.assertRaises(ValueError):self.f.flow.customer_claim(self.ticket)
        self.f.flow.customer_claim(ticket)
        self.assertEqual(self.f.flow.snapshot()['order']['state'],'PAID')
        self.assertIsNone(self.f.store.get(self.oid)['grant_id'])

    def test_second_expiry_requires_manual_action_and_never_loops_provider_posts(self):
        self.expire();self.renew(automatic=True);self.f.service.ticket_saved()
        self.expire();self.assertFalse(self.f.flow.expiry_auto_available)
        for _ in range(3):self.f.service.check()
        self.assertEqual(self.f.provider.charges,2)
        with self.assertRaises(RuntimeError):self.renew(automatic=True)
        self.renew();self.assertEqual(self.f.provider.charges,3)
        self.assertEqual(self.f.flow.snapshot()['qr_renewal_count'],2)

    def test_pause_or_restart_retires_automatic_authority_and_proof(self):
        self.expire();key=self.f.flow.snapshot()['checkout_key']
        self.f.flow.lock_customer()
        with self.assertRaises(RuntimeError):self.f.flow.renew_expired_qr(key,lambda _:None,True)
        self.assertEqual(self.f.provider.charges,1)
        self.reopen();self.assertFalse(self.f.flow.expiry_auto_available)
        self.assertFalse(self.f.flow.expiry_proof_ready)
        self.assertEqual(self.f.flow.snapshot()['checkout_key'],key)

    def test_cached_expired_raw_mismatch_and_entitlements_never_grant_replacement(self):
        self.f.flow.lock_customer()
        self.f.provider.rows[self.oid].update(transaction_status='expire',status_code='407')
        result=self.f.backend.reconcile(self.oid,'PB001','restart');base=self.f.flow.snapshot()
        cases=[{'verification_pending':True},{'reconciliation':dict(result['reconciliation'],checked=False)},
               {'reconciliation':dict(result['reconciliation'],provider_state='pending')},
               {'state':'PAID'},{'service_state':'STARTED'},{'grant_id':'a'*32},
               {'fulfillment':{'obligation_state':'OWED'}},{'local_transaction_id':'fixture-photo'},
               {'fulfillment_issue':{'reason':'PHOTO_STATE_UNAVAILABLE'}},{'service_fence':{'suspended':True}},
               {'release':{'state':'PREPARED'}}]
        for change in cases:
            with self.subTest(change=change):
                self.f.flow.data=copy.deepcopy(base);candidate=copy.deepcopy(result);candidate.update(change)
                self.f.flow._reconcile_at=0
                with patch.object(self.f.flow.client,'reconcile',return_value=candidate):self.f.service.check()
                self.assertFalse(self.f.flow.expiry_proof_ready);self.assertTrue(self.f.flow.active)
                self.assertEqual(self.f.provider.charges,1)
        for local in [{'transaction_id':'fixture-photo'},{'allocation_operation_id':'b'*32},
                      {'release_operation_id':'c'*32},{'isolation_id':'d'*32},
                      {'recovery':{'interrupted_phase':'STARTED'}},{'allocation_ready':True}]:
            with self.subTest(local=local):
                self.f.flow.data=copy.deepcopy(base);self.f.flow.data.update(local);self.f.flow._reconcile_at=0
                with patch.object(self.f.flow.client,'reconcile',return_value=result):self.f.service.check()
                self.assertTrue(self.f.flow.active);self.assertFalse(self.f.flow.expiry_proof_ready)
        self.assertFalse((self.root/'visits').exists())

    def test_archive_save_and_replacement_journal_faults_never_send_new_charge(self):
        self.f.provider.rows[self.oid].update(transaction_status='expire',status_code='407')
        self.f.flow.lock_customer()
        with patch.object(self.f.flow,'_archive_snapshot',side_effect=OSError('synthetic archive failure')):
            with self.assertRaises(OSError):self.f.service.operator_inspect('12345678')
        self.assertTrue(self.f.flow.active);self.assertEqual(self.f.provider.charges,1)
        save=self.f.flow._save
        def fail_closed():
            if self.f.flow.data['phase']=='CANCELLED':raise OSError('synthetic final expiry save failure')
            save()
        with patch.object(self.f.flow,'_save',side_effect=fail_closed):
            with self.assertRaises(OSError):self.f.flow.inspect_recovery('12345678')
        self.assertTrue(self.f.flow.active)
        self.f.flow.inspect_recovery('12345678');old=self.f.flow.snapshot()
        save=self.f.flow._save
        def fail_new():
            if self.f.flow.data['checkout_key']!=old['checkout_key']:raise OSError('synthetic new journal failure')
            save()
        with patch.object(self.f.flow,'_save',side_effect=fail_new):
            with self.assertRaises(OSError):self.f.flow.renew_expired_qr(old['checkout_key'],lambda _:None)
        self.assertEqual(self.f.flow.snapshot()['checkout_key'],old['checkout_key'])
        self.assertEqual(self.f.provider.charges,1)
        self.assertEqual(json.loads((self.root/'visit.json').read_text())['checkout_key'],old['checkout_key'])

    def test_readiness_failure_or_privacy_change_in_preflight_blocks_creation(self):
        self.expire();key=self.f.flow.snapshot()['checkout_key']
        with self.assertRaises(RuntimeError):
            self.f.flow.renew_expired_qr(key,lambda _:(_ for _ in ()).throw(RuntimeError('synthetic camera not ready')))
        def retire(_cart):self.f.flow.lock_customer()
        with self.assertRaises(RuntimeError):self.f.flow.renew_expired_qr(key,retire)
        self.assertEqual(self.f.provider.charges,1)

    def test_late_settlement_during_reverification_holds_original_paid_rights(self):
        self.expire();self.f.flow.invalidate_qr_renewal();self.f.paid()
        created=self.f.store.get(self.oid)['created_at'];self.f.store.now=lambda:created+120
        self.f.flow.data['phase']='VERIFYING_QR';self.f.flow._reconcile_at=0
        self.f.service.check()
        self.assertEqual(self.f.flow.snapshot()['phase'],'RECOVERY')
        self.assertTrue(self.f.flow.active);self.assertFalse(self.f.flow.expiry_proof_ready)
        self.assertEqual(self.f.store.get(self.oid)['state'],'REVIEW_REQUIRED')
        self.assertEqual(self.f.flow.snapshot()['order']['reconciliation']['provider_state'],'settlement')
        self.assertEqual(self.f.provider.charges,1)

    def test_lost_replacement_reply_reuses_durable_new_key_after_restart(self):
        self.expire();self.f.provider.lost_charge=True
        with self.assertRaises(RuntimeError):self.renew()
        replacement=self.f.flow.snapshot();self.assertEqual(self.f.provider.charges,2)
        self.f.provider.lost_charge=False;self.reopen();self.f.service.check()
        restored=self.f.flow.snapshot()
        self.assertEqual(restored['checkout_key'],replacement['checkout_key'])
        self.assertEqual(restored['qr_renewal_count'],1);self.assertEqual(self.f.provider.charges,2)

    def test_disabled_and_mock_profiles_cannot_issue_expiry_replacement_authority(self):
        self.f.flow.qr_renewal_enabled=False;self.f.flow.lock_customer()
        self.expire();self.assertTrue(self.f.flow.active)
        self.assertFalse(self.f.flow.expiry_proof_ready);self.assertFalse((self.root/'visits').exists())
        result=self.f.flow.snapshot()['order'];self.f.flow.qr_renewal_enabled=True
        self.f.flow.context['mode']='mock';self.f.flow.data['context']['mode']='mock'
        candidate=copy.deepcopy(result);candidate['mode']='mock';self.f.flow._reconcile_at=0
        with patch.object(self.f.flow.client,'reconcile',return_value=candidate):self.f.service.check()
        self.assertTrue(self.f.flow.active);self.assertFalse(self.f.flow.expiry_proof_ready)
        self.assertFalse((self.root/'visits').exists());self.assertEqual(self.f.provider.charges,1)

    def test_expired_runtime_proof_cannot_be_replaced_by_a_cached_journal_flag(self):
        self.expire();key=self.original['checkout_key'];deadline=self.f.flow._expiry_proof[2]
        with patch('photobooth.qris_session.time.monotonic',return_value=deadline+1):
            self.assertFalse(self.f.flow.expiry_proof_ready)
            with self.assertRaises(RuntimeError):self.f.flow.renew_expired_qr(key,lambda _:None)
        self.assertEqual(self.f.provider.charges,1)

    def test_operator_late_settlement_revokes_recent_expiry_proof_and_keeps_original_identity(self):
        self.expire();self.assertTrue(self.f.flow.expiry_proof_ready)
        self.f.paid();self.f.flow.inspect_recovery('12345678')
        self.assertFalse(self.f.flow.expiry_proof_ready)
        self.assertEqual(self.f.flow.snapshot()['phase'],'RECOVERY')
        self.assertEqual(self.f.flow.snapshot()['checkout_key'],self.original['checkout_key'])
        with self.assertRaises(RuntimeError):self.f.flow.renew_expired_qr(self.original['checkout_key'],lambda _:None)
        self.assertEqual(self.f.provider.charges,1)
