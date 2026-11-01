"""Original encrypted CCP fixtures; no paid claim/photo admission implied."""
from dataclasses import replace
import json
import hmac
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from PIL import Image
from photobooth.catalog import get_templates
from photobooth.credential_vault import SyntheticAeadProtector, VaultUnavailable
from photobooth.post_preview_ccp import ClaimProofPolicy, OriginalCCPService, PendingCCPOffer
from photobooth.post_preview_checkout import ChargeReadiness, PrivateDraftCheckout
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_store import DraftHeld, PostPreviewStore


class OriginalCCPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.clock = [1000.0]
        self.monotonic = [10.0]
        self.ledger = PostPreviewStore(self.root/'drafts.db', now=lambda: self.clock[0])
        self.addCleanup(self.ledger.close)
        self.lease = self.ledger.create('PB001', 'visitA', {'template_a': 1})
        photos = PrivateDraftPhotos(self.ledger, self.root/'private')
        template = get_templates()[0]
        for slot in range(3):
            photos.capture(self.lease, template, Image.new('RGB', (32, 24), 'blue'),
                           slot=slot, revision=self.ledger.inspect(self.lease)['revision'])
        checkout = PrivateDraftCheckout(photos)
        checkout.approve(self.lease, template, revision=self.ledger.inspect(self.lease)['revision'])
        self.intent = checkout.freeze(self.lease, [template],
            revision=self.ledger.inspect(self.lease)['revision'],
            readiness=ChargeReadiness(True, True, True, True, True, True, True, 25), expected_amount=10000)
        self.key = os.urandom(32)
        self.protector = SyntheticAeadProtector(self.key, fixture=True)
        self.service = self.new_service()

    def new_service(self, protector=None, merchant='MTEST'):
        return OriginalCCPService(self.ledger, protector or self.protector, merchant,
                                  allow_synthetic=True, monotonic=lambda: self.monotonic[0])

    def issue(self):
        return self.service.issue_once(self.lease)

    def row(self):
        return self.ledger.db.execute('SELECT * FROM pp_ccp_credentials').fetchone()

    def offer(self):
        self.issue()
        return self.service.private_offer(self.lease)

    def verify(self, payload):
        return self.service.verify(self.intent['purchase_group_id'], 'PB001', payload)

    def test_issue_stores_ciphertext_hash_scope_without_raw_proof_or_offer_claim(self):
        info = self.issue()
        self.assertEqual({'purchase_group_id', 'kind', 'expires_at'}, set(info))
        self.assertIsNone(self.row()['offered_at'])
        offer = self.service.private_offer(self.lease)
        self.assertTrue(offer.qr_payload.startswith('MEONG:CCP:1:PB001:'))
        self.assertIsNone(self.row()['offered_at'])
        self.assertFalse(offer.qr_payload in repr(offer)+str(offer))
        self.assertFalse(offer.qr_payload.encode() in self.row()['ciphertext'])
        self.assertFalse(offer.qr_payload.encode() in self.ledger.db.execute('SELECT scope_json FROM pp_ccp_credentials').fetchone()[0].encode())
        for name in ('drafts.db', 'drafts.db-wal'):
            path = self.root/name
            if path.exists(): self.assertFalse(offer.qr_payload.encode() in path.read_bytes())

    def test_idempotent_issue_and_restart_keep_exact_original_and_expiry(self):
        first = self.offer()
        cipher = self.row()['ciphertext']
        expiry = self.row()['expires_at']
        self.clock[0] += 10
        restarted = self.new_service(SyntheticAeadProtector(self.key, fixture=True))
        restarted.issue_once(self.lease)
        second = restarted.private_offer(self.lease)
        self.assertTrue(hmac.compare_digest(first.qr_payload, second.qr_payload))
        self.assertEqual(cipher, self.row()['ciphertext'])
        self.assertEqual(expiry, self.row()['expires_at'])
        self.assertEqual(1, self.ledger.db.execute("SELECT count(*) FROM pp_events WHERE event='CCP_CREATED'").fetchone()[0])

    def test_genuine_offer_requires_original_live_render_permit_and_never_resets_timestamp(self):
        offer = self.offer()
        self.clock[0] += 5
        self.assertEqual(1005, self.service.mark_visible(self.lease, offer))
        self.clock[0] += 5
        self.assertEqual(1005, self.service.mark_visible(self.lease, offer))
        self.assertEqual(1, self.ledger.db.execute("SELECT count(*) FROM pp_events WHERE event='CCP_OFFERED'").fetchone()[0])

    def test_copied_permit_reboot_or_retired_ui_cannot_record_offer(self):
        offer = self.offer()
        forged = PendingCCPOffer(offer.presentation_id, offer.purchase_group_id, offer.generation, offer.qr_payload)
        with self.assertRaises(VaultUnavailable): self.service.mark_visible(self.lease, forged)
        with self.assertRaises(VaultUnavailable): self.new_service().mark_visible(self.lease, offer)
        self.service.hide_private()
        with self.assertRaises(VaultUnavailable): self.service.mark_visible(self.lease, offer)
        with self.assertRaises(VaultUnavailable): self.service.private_offer(self.lease)
        self.assertIsNone(self.row()['offered_at'])

    def test_expired_in_memory_render_permit_never_implies_genuine_offer(self):
        offer = self.offer()
        self.monotonic[0] += 61
        with self.assertRaises(VaultUnavailable): self.service.mark_visible(self.lease, offer)
        self.assertIsNone(self.row()['offered_at'])

    def test_prepaid_claim_proof_verification_grants_no_media_payment_or_machine_lease(self):
        offer = self.offer()
        scope = self.verify(offer.qr_payload)
        self.assertFalse(scope.media_authorized)
        self.assertFalse(scope.payment_authorized)
        self.assertEqual(self.lease.draft_id, scope.draft_id)
        self.assertEqual('CREATE_PREPARED', self.ledger.inspect(self.lease)['state'])

    def test_wrong_type_booth_merchant_group_and_guessed_proof_are_rejected(self):
        offer = self.offer()
        for payload in ('operator-login', 'https://drive.google.com/drive/folders/fixture',
                        offer.qr_payload.replace(':CCP:', ':RECOVERY:'),
                        offer.qr_payload.replace('PB001', 'PB002'), 'qris-provider-fixture',
                        offer.qr_payload[:-1]+('x' if offer.qr_payload[-1] != 'x' else 'y')):
            with self.subTest(kind=payload[:12]), self.assertRaises(PermissionError): self.verify(payload)
        with self.assertRaises(PermissionError):
            self.service.verify(self.intent['purchase_group_id'], 'PB002', offer.qr_payload)
        with self.assertRaises(PermissionError):
            self.service.verify('0'*32, 'PB001', offer.qr_payload)
        with self.assertRaises(PermissionError):
            self.new_service(merchant='OTHER').verify(self.intent['purchase_group_id'], 'PB001', offer.qr_payload)

    def test_rate_limit_is_durable_across_service_restart_and_window_is_bounded(self):
        offer = self.offer()
        for _ in range(8):
            with self.assertRaises(PermissionError): self.verify('forged')
        with self.assertRaises(PermissionError):
            self.new_service().verify(self.intent['purchase_group_id'], 'PB001', offer.qr_payload)
        self.clock[0] += 61
        self.assertFalse(self.verify(offer.qr_payload).media_authorized)

    def test_clock_rollback_expiry_and_revocation_never_reissue_or_extend(self):
        offer = self.offer()
        original = bytes(self.row()['ciphertext'])
        self.clock[0] = 999
        with self.assertRaises(PermissionError): self.verify(offer.qr_payload)
        self.clock[0] = 1000+86400
        with self.assertRaises(PermissionError): self.verify(offer.qr_payload)
        with self.assertRaises(VaultUnavailable): self.issue()
        self.assertEqual(original, bytes(self.row()['ciphertext']))
        self.clock[0] = 1001
        self.service.revoke(self.lease)
        with self.assertRaises(PermissionError): self.verify(offer.qr_payload)
        self.assertEqual(1, self.ledger.db.execute('SELECT count(*) FROM pp_checkout_intents').fetchone()[0])

    def test_key_loss_or_corrupt_ciphertext_fails_closed_with_original_record_retained(self):
        self.issue()
        old = bytes(self.row()['ciphertext'])
        other = self.new_service(SyntheticAeadProtector(os.urandom(32), fixture=True))
        with self.assertRaises(VaultUnavailable): other.private_offer(self.lease)
        self.assertEqual(old, bytes(self.row()['ciphertext']))
        self.ledger.db.execute('UPDATE pp_ccp_credentials SET ciphertext=?', (b'corrupt',))
        with self.assertRaises(VaultUnavailable): self.service.private_offer(self.lease)
        self.assertEqual(1, self.ledger.db.execute('SELECT count(*) FROM pp_checkout_intents').fetchone()[0])

    def test_missing_original_escrow_row_is_not_replaced_with_second_token(self):
        self.issue()
        self.ledger.db.execute('DELETE FROM pp_ccp_credentials')
        with self.assertRaises(VaultUnavailable): self.issue()
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_ccp_credentials').fetchone()[0])

    def test_synthetic_protector_not_implicitly_accepted_by_real_service(self):
        with self.assertRaises(VaultUnavailable): OriginalCCPService(self.ledger, self.protector, 'MTEST')

    def test_missing_v3_credential_table_is_not_silently_recreated(self):
        self.issue()
        self.ledger.db.execute('DROP TABLE pp_ccp_credentials')
        with self.assertRaises(DraftHeld): PostPreviewStore(self.root/'drafts.db')
        self.assertIsNone(self.ledger.db.execute(
            "SELECT name FROM sqlite_master WHERE name='pp_ccp_credentials'").fetchone())

    def test_protector_failure_never_records_a_created_or_offered_proof(self):
        with patch.object(self.protector, 'protect', side_effect=VaultUnavailable('unavailable')):
            with self.assertRaises(VaultUnavailable): self.issue()
        self.assertIsNone(self.row())
        self.assertEqual(0, self.ledger.db.execute("SELECT count(*) FROM pp_events WHERE event='CCP_CREATED'").fetchone()[0])

    def test_retirement_during_slow_decrypt_cannot_resurrect_pending_offer(self):
        self.issue()
        entered, release = threading.Event(), threading.Event()
        original = self.protector.unprotect
        outcomes = []
        def blocked(*args):
            entered.set(); release.wait(3)
            return original(*args)
        def offer():
            try: self.service.private_offer(self.lease)
            except VaultUnavailable: outcomes.append('held')
        with patch.object(self.protector, 'unprotect', side_effect=blocked):
            worker = threading.Thread(target=offer)
            worker.start()
            self.assertTrue(entered.wait(3))
            self.service.hide_private()
            release.set(); worker.join(5)
        self.assertEqual(['held'], outcomes)
        self.assertIsNone(self.row()['offered_at'])


if __name__ == '__main__': unittest.main()
