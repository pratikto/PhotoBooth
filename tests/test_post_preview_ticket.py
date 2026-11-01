"""Original paid ticket escrow and independent presentation/receipt state."""
import hmac
import sqlite3
import unittest

from photobooth.credential_vault import SyntheticAeadProtector, VaultUnavailable
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_store import DraftHeld, PostPreviewStore
from tests import test_post_preview_payments as payment_fixtures


class OriginalPaidTicketTests(unittest.TestCase):
    def setUp(self):
        self.fixture = payment_fixtures.PostPreviewPaymentTests(); self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.ledger, self.lease = self.fixture.ledger, self.fixture.lease
        self.group = self.fixture.group
        self.ticket = self.make_ticket()

    def make_ticket(self, protector=None):
        return OriginalRecoveryTicketService(self.fixture.service,
            protector or self.fixture.fixture.protector, allow_synthetic=True)

    def paid(self):
        self.fixture.begin()
        self.fixture.provider.state(self.fixture.order(), 'settlement')
        return self.fixture.service.reconcile_all(self.group, 'PB001', force=True)

    def row(self):
        return self.ledger.db.execute('SELECT * FROM pp_ticket_presentations').fetchone()

    def test_unpaid_pending_or_unknown_never_issue_paid_ticket_or_service(self):
        for action in (lambda: None, self.fixture.begin):
            action()
            with self.assertRaises((DraftHeld,VaultUnavailable)): self.ticket.prepare(self.lease)
        self.assertEqual(0,self.ledger.db.execute('SELECT count(*) FROM pp_ticket_credentials').fetchone()[0])
        self.assertEqual(0,self.ledger.db.execute('SELECT count(*) FROM pp_paid_services').fetchone()[0])

    def test_verified_paid_binds_one_original_ticket_entitlement_and_ciphertext(self):
        paid = self.paid()
        first = self.ticket.prepare(self.lease)
        self.assertEqual(first,self.ticket.prepare(self.lease))
        offer = self.ticket.private_offer(self.lease)
        self.assertTrue(offer.qr_payload.startswith('MEONG:RECOVERY:1:PB001:'))
        self.assertFalse(offer.qr_payload in repr(offer)+str(offer))
        self.assertIsNone(self.row()['shown_at'])
        self.assertEqual('NOT_OFFERED',self.row()['screen_state'])
        self.assertEqual('PREPARED',self.row()['receipt_state'])
        service = self.ledger.db.execute('SELECT * FROM pp_paid_services').fetchone()
        self.assertEqual(paid['entitlement_id'],service['entitlement_id'])
        self.assertEqual('OWED',service['status'])
        for name in ('drafts.db','drafts.db-wal'):
            path=self.fixture.fixture.root/name
            if path.exists(): self.assertFalse(offer.qr_payload.encode() in path.read_bytes())

    def test_restart_recovers_same_protected_original_but_never_redisplays_offered_ticket(self):
        self.paid();self.ticket.prepare(self.lease)
        first=self.ticket.private_offer(self.lease)
        restarted=self.make_ticket();restarted.prepare(self.lease)
        second=restarted.private_offer(self.lease)
        self.assertTrue(hmac.compare_digest(first.qr_payload,second.qr_payload))
        restarted.mark_visible(self.lease,second)
        self.assertEqual('VISIBLE',self.row()['screen_state'])
        with self.assertRaises(VaultUnavailable): self.make_ticket().private_offer(self.lease)
        restarted.dismiss(self.lease,second)
        self.assertEqual('DISMISSED',self.row()['screen_state'])
        with self.assertRaises(VaultUnavailable): restarted.private_offer(self.lease)

    def test_credential_types_are_separate_and_verified_ticket_grants_no_media(self):
        self.paid();self.ticket.prepare(self.lease)
        ticket=self.ticket.private_offer(self.lease)
        ccp=self.fixture.fixture.service.private_offer(self.lease)
        with self.assertRaises(PermissionError): self.ticket.verify(self.group,'PB001',ccp.qr_payload)
        with self.assertRaises(PermissionError): self.fixture.fixture.service.verify(self.group,'PB001',ticket.qr_payload)
        scope=self.ticket.verify(self.group,'PB001',ticket.qr_payload)
        self.assertFalse(scope.media_authorized)
        self.assertFalse(scope.payment_authorized)

    def test_key_loss_and_missing_original_journal_hold_owed_without_reissue(self):
        self.paid();self.ticket.prepare(self.lease)
        wrong=SyntheticAeadProtector(b'z'*32,fixture=True)
        with self.assertRaises(VaultUnavailable): self.make_ticket(wrong).private_offer(self.lease)
        self.ledger.db.execute('DELETE FROM pp_ticket_presentations')
        with self.assertRaises(VaultUnavailable): self.ticket.prepare(self.lease)
        self.assertEqual(1,self.ledger.db.execute('SELECT count(*) FROM pp_ticket_credentials').fetchone()[0])
        self.assertEqual('OWED',self.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_hide_and_retired_owner_cannot_decrypt_or_offer_and_never_free_booth(self):
        self.paid();self.ticket.prepare(self.lease)
        offer=self.ticket.private_offer(self.lease)
        self.ticket.hide_private()
        with self.assertRaises(VaultUnavailable): self.ticket.mark_visible(self.lease,offer)
        self.fixture.service.signal_lifecycle(self.lease,'APP_SUSPENDED')
        with self.assertRaises((DraftHeld,VaultUnavailable)): self.make_ticket().private_offer(self.lease)
        self.assertEqual(0,self.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])

    def test_current_schema_missing_paid_journal_is_not_silently_recreated(self):
        self.ledger.db.execute('DROP TABLE pp_paid_strip_jobs')
        with self.assertRaises(DraftHeld): PostPreviewStore(self.fixture.fixture.root/'drafts.db')

    def test_additive_v5_upgrade_preserves_paid_entitlement_and_original_ccp(self):
        paid=self.paid()
        ccp=self.ledger.db.execute('SELECT ciphertext FROM pp_ccp_credentials').fetchone()[0]
        for table in ('pp_paid_strip_jobs','pp_paid_services','pp_ticket_presentations','pp_ticket_credentials'):
            self.ledger.db.execute('DROP TABLE '+table)
        self.ledger.db.execute('UPDATE pp_schema SET version=5')
        other=PostPreviewStore(self.fixture.fixture.root/'drafts.db');self.addCleanup(other.close)
        self.assertEqual(8,other.db.execute('SELECT version FROM pp_schema').fetchone()[0])
        self.assertEqual(paid['entitlement_id'],other.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0])
        self.assertEqual(ccp,other.db.execute('SELECT ciphertext FROM pp_ccp_credentials').fetchone()[0])
        self.assertEqual(0,other.db.execute('SELECT count(*) FROM pp_ticket_credentials').fetchone()[0])

    def test_sql_guards_preserve_original_ticket_service_and_no_screen_or_receipt_replay(self):
        self.paid();self.ticket.prepare(self.lease)
        for sql in ("UPDATE pp_ticket_credentials SET ciphertext=x'00'",
                    "UPDATE pp_paid_services SET entitlement_id='replacement'",
                    "UPDATE pp_ticket_presentations SET receipt_job_id='replacement'"):
            with self.assertRaises(sqlite3.IntegrityError): self.ledger.db.execute(sql)
        offer=self.ticket.private_offer(self.lease);self.ticket.mark_visible(self.lease,offer)
        self.assertTrue(self.ticket.dismiss(self.lease,offer))
        self.assertFalse(self.ticket.dismiss(self.lease,offer))
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute("UPDATE pp_ticket_presentations SET screen_state='NOT_OFFERED'")
        self.ledger.db.execute("UPDATE pp_ticket_presentations SET receipt_state='SENDING'")
        self.ledger.db.execute("UPDATE pp_ticket_presentations SET receipt_state='UNCERTAIN'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute("UPDATE pp_ticket_presentations SET receipt_state='PREPARED'")

    def test_duplicate_settled_attempts_preserve_one_original_service_and_ticket(self):
        first=self.fixture.begin();order1=self.fixture.order(first)
        self.fixture.provider.state(order1,'expire')
        second=self.fixture.service.continue_expired(self.lease,actively_continuing=True)
        self.fixture.provider.state(order1,'settlement')
        self.fixture.service.reconcile_all(self.group,'PB001',force=True)
        original=self.ticket.prepare(self.lease)
        self.fixture.provider.state(self.fixture.order(second),'settlement')
        self.fixture.service.reconcile_all(self.group,'PB001',force=True)
        self.assertEqual(original,self.ticket.prepare(self.lease))
        self.assertEqual(1,self.ledger.db.execute('SELECT count(*) FROM pp_paid_services').fetchone()[0])
        self.assertEqual(1,self.ledger.db.execute('SELECT count(*) FROM pp_ticket_credentials').fetchone()[0])


if __name__=='__main__': unittest.main()
