"""Private preview/freeze fixtures, not payment or physical acceptance."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from photobooth.capture_journal import CaptureRecoveryRequired
from photobooth.catalog import get_templates
from photobooth.post_preview_checkout import ChargeReadiness, PrivateDraftCheckout, digest
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_store import DraftHeld, PostPreviewStore


class PreviewFreezeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = PostPreviewStore(self.root/'private.db')
        self.addCleanup(self.ledger.close)
        self.photos = PrivateDraftPhotos(self.ledger, self.root/'private')
        self.checkout = PrivateDraftCheckout(self.photos)
        self.templates = get_templates()
        self.a, self.b = self.templates[:2]
        self.lease = self.ledger.create('PB001', 'visitA', {'template_a': 2, 'template_b': 1})
        self.image = Image.new('RGB', (48, 32), (12, 45, 80))
        self.ready = ChargeReadiness(True, True, True, True, True, True, True, 25)

    def revision(self): return self.ledger.inspect(self.lease)['revision']

    def trio(self, template):
        for slot in range(3):
            self.photos.capture(self.lease, template, self.image, slot=slot, revision=self.revision())

    def approve_all(self):
        for template in (self.a, self.b):
            self.trio(template)
            self.checkout.approve(self.lease, template, revision=self.revision())

    def freeze(self, **kwargs):
        args = dict(revision=self.revision(), readiness=self.ready, expected_amount=25000)
        args.update(kwargs)
        return self.checkout.freeze(self.lease, self.templates, **args)

    def test_private_preview_reuses_renderer_without_delivery_or_completion(self):
        self.trio(self.a)
        with patch('photobooth.qr_code.create_qr_image', side_effect=AssertionError('unpaid QR')):
            result = self.checkout.preview(self.lease, self.a, revision=self.revision())
        with Image.open(result['preview_path']) as image:
            self.assertEqual((640, 1920), image.size)
        self.assertEqual(hashlib.sha256(result['preview_path'].read_bytes()).hexdigest(), result['preview_sha256'])
        media = self.photos.inspect(self.lease, self.a)
        data = json.loads(media['manifest_path'].read_text())
        self.assertEqual('IN_PROGRESS', data['status'])
        self.assertIsNone(data['sessions'][0]['output_path'])
        self.assertEqual('LOCAL_ONLY', data['upload_status'])
        self.assertFalse(list((self.root/'private').rglob('counter.json')))

    def test_every_selected_template_needs_three_photos_and_approval(self):
        self.trio(self.a)
        self.checkout.approve(self.lease, self.a, revision=self.revision())
        with self.assertRaises(DraftHeld): self.freeze()
        self.trio(self.b)
        with self.assertRaises(DraftHeld): self.freeze()
        self.checkout.approve(self.lease, self.b, revision=self.revision())
        self.assertEqual('CREATE_PREPARED', self.freeze()['phase'])

    def test_freeze_binds_exact_photos_artwork_copies_quote_and_revision(self):
        self.approve_all()
        revision = self.revision()
        result = self.freeze()
        contract = json.loads(result['contract_json'])
        self.assertEqual(result['contract_sha256'], digest(contract))
        self.assertEqual(revision, contract['revision'])
        self.assertEqual(25000, contract['amount'])
        self.assertEqual({'template_a': 2, 'template_b': 1}, contract['quantities'])
        self.assertEqual([2, 1], [d['copies'] for d in contract['designs']])
        self.assertEqual([3, 3], [len(d['binding']['photos']) for d in contract['designs']])
        self.assertEqual(['template_a', 'template_b'], [d['binding']['artwork']['template_id'] for d in contract['designs']])
        self.assertEqual('CREATE_PREPARED', self.ledger.inspect(self.lease)['state'])

    def test_freeze_survives_restart_and_never_recreates_group(self):
        self.approve_all()
        first = self.freeze()
        other = PostPreviewStore(self.root/'private.db')
        self.addCleanup(other.close)
        checkout = PrivateDraftCheckout(PrivateDraftPhotos(other, self.root/'private'))
        self.assertEqual(first, checkout.freeze(self.lease, self.templates,
            revision=self.revision(), readiness=self.ready, expected_amount=25000))
        self.assertEqual(1, other.db.execute('SELECT count(*) FROM pp_checkout_intents').fetchone()[0])

    def test_edits_and_capture_rejected_after_first_durable_create_prepared(self):
        self.approve_all()
        self.freeze()
        with self.assertRaises(DraftHeld):
            self.ledger.edit(self.lease, {'template_a': 9}, revision=self.revision())
        with self.assertRaises(DraftHeld):
            self.photos.request_retake(self.lease, self.a, 0, revision=self.revision())
        with self.assertRaises(DraftHeld):
            self.photos.capture(self.lease, self.a, self.image, slot=0, revision=self.revision())

    def test_readiness_is_nonconsuming_and_fail_closed_for_each_dependency(self):
        self.approve_all()
        for field in ('camera', 'disk', 'artwork', 'printer_route', 'payment_transport',
                      'drive_authenticated', 'drive_sharing'):
            with self.subTest(field=field), self.assertRaises(DraftHeld):
                self.freeze(readiness=replace(self.ready, **{field: False}))
        for capacity in (0, -1, True, 1.0):
            with self.subTest(capacity=capacity), self.assertRaises(DraftHeld):
                self.freeze(readiness=replace(self.ready, unclaimed_ready_capacity=capacity))
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_checkout_intents').fetchone()[0])
        self.assertEqual(25, self.ready.unclaimed_ready_capacity)
        self.assertEqual('CREATE_PREPARED', self.freeze()['phase'])
        self.assertEqual(25, self.ready.unclaimed_ready_capacity)

    def test_client_amount_mismatch_or_stale_revision_never_prepares_create(self):
        self.approve_all()
        for amount in (1, 25000.0, True, 0):
            with self.subTest(amount=amount), self.assertRaises(DraftHeld): self.freeze(expected_amount=amount)
        with self.assertRaises(DraftHeld): self.freeze(revision=self.revision()-1)
        self.assertEqual('OPEN', self.ledger.inspect(self.lease)['state'])

    def test_copy_edit_requotes_without_recapture_or_new_preview(self):
        self.approve_all()
        before = {p: p.read_bytes() for p in (self.root/'private').rglob('*.jpg')}
        outputs = list((self.root/'private').rglob('*.png'))
        self.ledger.edit(self.lease, {'template_a': 3, 'template_b': 1}, revision=self.revision())
        result = self.freeze(expected_amount=30000)
        self.assertEqual(30000, json.loads(result['contract_json'])['amount'])
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertEqual(outputs, list((self.root/'private').rglob('*.png')))

    def test_retake_after_preview_keeps_old_preview_and_requires_new_approval(self):
        self.approve_all()
        old = self.checkout.preview(self.lease, self.a, revision=self.revision())
        before = old['preview_path'].read_bytes()
        self.photos.request_retake(self.lease, self.a, 1, revision=self.revision())
        with self.assertRaises(DraftHeld): self.freeze()
        with self.assertRaises(DraftHeld): self.checkout.preview(self.lease, self.a, revision=self.revision())
        self.photos.capture(self.lease, self.a, Image.new('RGB', (48, 32), 'yellow'),
                            slot=1, revision=self.revision(), retake=True)
        with self.assertRaises(DraftHeld): self.freeze()
        new = self.checkout.approve(self.lease, self.a, revision=self.revision())
        self.assertNotEqual(old['preview_key'], new['preview_key'])
        self.assertEqual(before, old['preview_path'].read_bytes())
        self.freeze()

    def test_corrupt_raw_or_preview_blocks_checkout(self):
        self.approve_all()
        result = self.checkout.preview(self.lease, self.a, revision=self.revision())
        result['preview_path'].write_bytes(b'corrupt')
        with self.assertRaises(CaptureRecoveryRequired): self.freeze()
        self.assertEqual('OPEN', self.ledger.inspect(self.lease)['state'])

    def test_lost_preview_response_reuses_exact_saved_output(self):
        self.trio(self.a)
        def fault(stage):
            if stage == 'output_published': raise RuntimeError('lost renderer reply')
        with patch('photobooth.capture_journal.boundary', side_effect=fault):
            with self.assertRaises(RuntimeError):
                self.checkout.preview(self.lease, self.a, revision=self.revision())
        outputs = list((self.root/'private').rglob('*.png'))
        self.assertEqual(1, len(outputs))
        original = outputs[0].read_bytes()
        with patch('photobooth.post_preview_checkout.compose_result', side_effect=AssertionError('replayed render')):
            result = self.checkout.preview(self.lease, self.a, revision=self.revision())
        self.assertEqual(original, result['preview_path'].read_bytes())

    def test_additive_v1_schema_upgrade_preserves_private_owner_and_lineage(self):
        before = self.ledger.inspect(self.lease)
        for table in ('pp_paid_strip_jobs','pp_paid_services','pp_ticket_presentations','pp_ticket_credentials',
                      'pp_notification_inbox', 'pp_payment_audit', 'pp_payment_attempts',
                      'pp_purchase_finance', 'pp_ccp_credentials', 'pp_checkout_intents'):
            self.ledger.db.execute('DROP TABLE '+table)
        self.ledger.db.execute('DROP TRIGGER pp_draft_identity_immutable')
        self.ledger.db.execute('UPDATE pp_schema SET version=1')
        other = PostPreviewStore(self.root/'private.db')
        self.addCleanup(other.close)
        self.assertEqual(before, other.inspect(self.lease))
        self.assertEqual(8, other.db.execute('SELECT version FROM pp_schema').fetchone()[0])


if __name__ == '__main__': unittest.main()
