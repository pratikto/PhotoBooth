"""Reproduce same-path retries without a real Drive account or customer files.

A retake JPEG can be saved and uploaded before a later manifest operation fails.
Retrying then replaces that path with a new capture. Upload progress belongs to
the saved revision, not merely its filename; an old response must not verify the
replacement. Nested callbacks model this overlap deterministically, not with
timing-sensitive sleeps or live network requests.
"""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from photobooth.catalog import get_templates
from photobooth.drive_sync import sync_manifest
from photobooth.drive_storage import DriveApiError
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import build_session_plans


class UploadRevisionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        self.store = TransactionStore(root / 'photos', root / 'state.json', 'PB001')
        self.plan = build_session_plans(get_templates(), {'template_a': 1})[0]
        self.transaction = self.store.start_transaction([self.plan], drive_slot={
            'folder_id': 'fixture-folder',
            'folder_url': 'https://drive.google.com/drive/folders/fixture-folder',
            'slot_key': 'fixture-slot',
        })
        self.key = 'raw/session_001/retake_01.jpg'
        self.calls = []

    def save_retake(self, color):
        return self.store.save_raw_photo(self.transaction, self.plan,
                                         Image.new('RGB', (80, 60), color),
                                         'retake_01.jpg', 'retake')

    def read_manifest(self):
        return json.loads(self.transaction.manifest_path.read_text(encoding='utf-8'))

    def upload_file(self, folder_id, transaction_id, relative_path, local_path, **kwargs):
        """Return verified fixture bytes and record exactly what was uploaded."""
        data = local_path.read_bytes()
        self.calls.append((relative_path, data))
        return {'id': f'fixture-file-{len(self.calls)}', 'size': str(len(data)),
                'md5Checksum': hashlib.md5(data).hexdigest()}

    def test_saved_replacement_does_not_inherit_an_old_verified_upload(self):
        photo = self.save_retake('red')
        old_bytes = photo.read_bytes()
        sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(self.read_manifest()['upload_files'][self.key]['status'], 'VERIFIED')
        self.save_retake('blue')
        current_bytes = photo.read_bytes()
        self.assertNotEqual(old_bytes, current_bytes)
        replacement = self.read_manifest()['upload_files'][self.key]
        self.assertEqual(replacement['status'], 'PENDING_UPLOAD')
        self.assertIsNone(replacement['md5_checksum'])
        self.assertIsNone(replacement['drive_file_id'])
        result = sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(result['upload_files'][self.key]['md5_checksum'],
                         hashlib.md5(current_bytes).hexdigest())
        self.assertEqual(self.calls, [(self.key, old_bytes), (self.key, current_bytes)])
        sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(len(self.calls), 2)

    def test_late_upload_response_and_resume_url_cannot_verify_a_new_capture(self):
        photo = self.save_retake('red')
        old_bytes = photo.read_bytes()
        owner = self

        class DelayedDrive:
            def upload_file(self, _folder, _transaction, relative_path, local_path, **kwargs):
                # The worker already started the old revision. A UI save then
                # commits a replacement before its resumable callback/response.
                owner.save_retake('blue')
                kwargs['on_session_url']('https://upload.example/old-revision')
                return {'id': 'old-file', 'size': str(len(old_bytes)),
                        'md5Checksum': hashlib.md5(old_bytes).hexdigest()}

        returned = sync_manifest(self.transaction.manifest_path, DelayedDrive())
        saved = self.read_manifest()
        for manifest in (returned, saved):
            record = manifest['upload_files'][self.key]
            self.assertEqual(record['status'], 'PENDING_UPLOAD')
            self.assertIsNone(record['upload_session_url'])
            self.assertIsNone(record['drive_file_id'])
            self.assertIsNone(record['md5_checksum'])
        new_bytes = photo.read_bytes()
        self.assertNotEqual(new_bytes, old_bytes)
        final = sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(final['upload_files'][self.key]['status'], 'VERIFIED')
        self.assertEqual(self.calls, [(self.key, new_bytes)])
        self.assertEqual(final['drive_folder_url'], saved['drive_folder_url'])

    def test_legacy_records_without_a_revision_still_sync_and_requeue_on_replacement(self):
        photo = self.save_retake('red')
        legacy = self.read_manifest()
        legacy['upload_files'][self.key].pop('content_version', None)
        self.store._atomic_write_json(self.transaction.manifest_path, legacy)
        self.transaction.manifest = legacy
        sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(self.read_manifest()['upload_files'][self.key]['status'], 'VERIFIED')
        self.save_retake('blue')
        self.assertEqual(self.read_manifest()['upload_files'][self.key]['status'], 'PENDING_UPLOAD')
        result = sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(result['upload_files'][self.key]['md5_checksum'],
                         hashlib.md5(photo.read_bytes()).hexdigest())
        self.assertEqual(len(self.calls), 2)

    def test_old_failed_upload_cannot_block_the_new_revision(self):
        """A delayed permission/network failure also belongs to its old bytes."""
        owner = self
        for status_code in (503, 403):
            with self.subTest(status_code=status_code):
                self.save_retake('red')

                class FailedDrive:
                    def upload_file(self, *_args, **kwargs):
                        owner.save_retake('blue')
                        kwargs['on_session_url']('https://upload.example/failed-old-revision')
                        raise DriveApiError('Fixture old upload failed', status_code)

                returned = sync_manifest(self.transaction.manifest_path, FailedDrive())
                for manifest in (returned, self.read_manifest()):
                    record = manifest['upload_files'][self.key]
                    self.assertEqual(record['status'], 'PENDING_UPLOAD')
                    self.assertNotIn('error', record)
                    self.assertIsNone(record['upload_session_url'])
                self.assertEqual(sync_manifest(self.transaction.manifest_path, self)
                                 ['upload_files'][self.key]['status'], 'VERIFIED')

    def test_rewritten_output_requeues_without_resetting_verified_raw_photos(self):
        raw = self.save_retake('red')
        output = self.transaction.folder_path / 'output' / 'session_001' / 'result.png'
        output.parent.mkdir(parents=True)
        Image.new('RGB', (100, 70), 'white').save(output)
        self.store.record_output(self.transaction, self.plan.session_id, [raw] * 3, output)
        sync_manifest(self.transaction.manifest_path, self)
        Image.new('RGB', (100, 70), 'blue').save(output)
        self.store.record_output(self.transaction, self.plan.session_id, [raw] * 3, output)
        key = 'output/session_001/result.png'
        current = self.read_manifest()
        self.assertEqual(current['upload_files'][self.key]['status'], 'VERIFIED')
        self.assertEqual(current['upload_files'][key]['status'], 'PENDING_UPLOAD')
        final = sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(final['upload_files'][key]['md5_checksum'],
                         hashlib.md5(output.read_bytes()).hexdigest())
        self.assertEqual([path for path, _data in self.calls].count(self.key), 1)
        self.assertEqual([path for path, _data in self.calls].count(key), 2)

    def test_revision_changed_before_upload_starts_is_left_for_the_next_pass(self):
        """Do not call the backend after the initial progress merge retires a file."""
        from photobooth.drive_sync import _persist_upload_progress
        photo = self.save_retake('red')

        def replace_before_merge(path, working):
            self.save_retake('blue')
            _persist_upload_progress(path, working)

        with patch('photobooth.drive_sync._persist_upload_progress', side_effect=replace_before_merge):
            result = sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(self.calls, [])
        self.assertEqual(result['upload_files'][self.key]['status'], 'PENDING_UPLOAD')
        sync_manifest(self.transaction.manifest_path, self)
        self.assertEqual(self.calls, [(self.key, photo.read_bytes())])

    def test_backend_content_conflict_is_not_reported_as_uploaded(self):
        """Apps Script intentionally rejects changed bytes at an existing path.

        Its existing 409 protection is not bypassed by this local queue fix.
        Unlike the direct API's update behavior, this case needs staff action;
        the important guarantee is truthful status and retained local photos.
        """
        owner = self
        uploaded = {}

        class ConflictDrive:
            def upload_file(self, folder, transaction, relative_path, local_path, **kwargs):
                data = local_path.read_bytes()
                if relative_path in uploaded and uploaded[relative_path] != data:
                    raise DriveApiError('Different content already exists at this path.', 409)
                uploaded[relative_path] = data
                return owner.upload_file(folder, transaction, relative_path, local_path, **kwargs)

        backend = ConflictDrive()
        photo = self.save_retake('red')
        sync_manifest(self.transaction.manifest_path, backend)
        self.save_retake('blue')
        local_bytes = photo.read_bytes()
        result = sync_manifest(self.transaction.manifest_path, backend)
        self.assertEqual(result['upload_status'], 'ACTION_REQUIRED')
        self.assertEqual(result['upload_files'][self.key]['status'], 'ACTION_REQUIRED')
        self.assertIsNone(result['upload_files'][self.key]['md5_checksum'])
        self.assertEqual(photo.read_bytes(), local_bytes)
        self.assertNotEqual(uploaded[self.key], local_bytes)
