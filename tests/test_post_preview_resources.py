"""Private disk controls without public uploads, deletion or wall-clock cutoff."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from photobooth.catalog import get_templates
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_resources import PrivateCapturePolicy
from photobooth.post_preview_store import DraftHeld, PostPreviewStore


class PrivateResourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = PostPreviewStore(self.root/'drafts.db')
        self.addCleanup(self.ledger.close)
        self.lease = self.ledger.create('PB001', 'visitA', {'template_a': 1})
        self.policy = PrivateCapturePolicy()
        self.photos = PrivateDraftPhotos(self.ledger, self.root/'private', policy=self.policy)
        self.template = get_templates()[0]
        self.image = Image.new('RGB', (48, 32), 'red')

    def capture(self, photos=None):
        return (photos or self.photos).capture(self.lease, self.template, self.image,
                                               slot=0, revision=self.ledger.inspect(self.lease)['revision'])

    def test_actual_probe_is_private_and_leaves_no_files(self):
        result = self.photos.prepare(self.lease)
        self.assertTrue(result['resource_ready'])
        self.assertFalse(list((self.root/'private').rglob('*.jpg')))
        self.assertFalse(list((self.root/'private').rglob('.durability-probe-*')))
        self.assertEqual('OPEN', self.ledger.inspect(self.lease)['state'])

    def test_low_disk_blocks_before_new_image_and_preserves_originals(self):
        path = self.capture()
        original = path.read_bytes()
        revision = self.ledger.inspect(self.lease)['revision']
        with patch('photobooth.post_preview_resources.shutil.disk_usage',
                   return_value=SimpleNamespace(free=0)):
            with self.assertRaises(DraftHeld):
                self.photos.capture(self.lease, self.template, self.image, slot=1, revision=revision)
        self.assertEqual(original, path.read_bytes())
        self.assertEqual(1, len(list(path.parent.glob('*.jpg'))))
        self.assertEqual(revision, self.ledger.inspect(self.lease)['revision'])

    def test_byte_quota_blocks_without_cleanup_or_shutter(self):
        policy = replace(self.policy, max_draft_bytes=1024)
        photos = PrivateDraftPhotos(self.ledger, self.root/'private', policy=policy)
        with self.assertRaises(DraftHeld): self.capture(photos)
        self.assertFalse((self.root/'private').exists())

    def test_image_limit_blocks_before_save(self):
        photos = PrivateDraftPhotos(self.ledger, self.root/'private',
                                    policy=replace(self.policy, max_photo_pixels=100))
        with self.assertRaises(DraftHeld): self.capture(photos)
        self.assertFalse((self.root/'private').exists())

    def test_entry_quota_is_bounded_and_preserves_every_file(self):
        folder = self.root/'private'/self.lease.draft_id
        folder.mkdir(parents=True)
        for n in range(3): (folder/str(n)).write_bytes(b'private')
        photos = PrivateDraftPhotos(self.ledger, self.root/'private', policy=replace(self.policy, max_entries=2))
        with self.assertRaises(DraftHeld): photos.prepare(self.lease)
        self.assertEqual(3, len(list(folder.iterdir())))

    def test_probe_fsync_failure_holds_and_cleans_only_its_own_probe(self):
        folder = self.root/'private'/self.lease.draft_id
        folder.mkdir(parents=True)
        sentinel = folder/'existing-private-media'
        sentinel.write_bytes(b'keep exact')
        with patch('photobooth.post_preview_resources.os.fsync', side_effect=OSError('disk write failed')):
            with self.assertRaises(OSError): self.photos.prepare(self.lease)
        self.assertEqual(b'keep exact', sentinel.read_bytes())
        self.assertEqual([sentinel], list(folder.iterdir()))

    def test_retired_worker_cannot_probe_or_create_storage(self):
        self.ledger.lifecycle_event(self.lease, 'VISIT_ABANDONED')
        with self.assertRaises(DraftHeld): self.photos.prepare(self.lease)
        self.assertFalse((self.root/'private').exists())

    def test_no_configured_policy_can_exceed_original_image_decoder_bound(self):
        with self.assertRaises(ValueError): replace(self.policy, max_photo_pixels=40_000_001)
        with self.assertRaises(ValueError): replace(self.policy, max_entries=True)
        with self.assertRaises(ValueError): replace(self.policy, max_draft_bytes=-1)


if __name__ == '__main__': unittest.main()
