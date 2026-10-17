"""Exercise expiration against temporary image files and fake remote services.

No test opens the user's photo directory or deletes content from a real Drive.
The exact boundary, offline queues, traversal boundaries, and late upload
callbacks matter here: a retention policy must not merely change a date label.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock

from PIL import Image

from photobooth.catalog import get_templates
from photobooth.drive_storage import API_ROOT, FOLDER_MIME_TYPE, AppsScriptDriveClient, DriveApiError, GoogleDriveClient
from photobooth.drive_sync import sync_manifest
from photobooth.retention import (
    PhotoRetentionWorker, purge_local_photos, read_drive_retention,
    register_drive_retention, retention_metadata,
)
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import build_session_plans


class PhotoRetentionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.photos = self.root / 'photos'
        self.now = datetime.now(timezone.utc)
        self.store = TransactionStore(self.photos, self.root / 'booth_state.json')
        self.plan = build_session_plans(get_templates(), {'template_a': 1})[0]
        self.transaction = self.store.start_transaction([self.plan], drive_slot={
            'folder_id': 'fixture-folder', 'folder_url': 'https://example.org/photos', 'slot_key': 'fixture'})
        self.raw = self.store.save_raw_photo(self.transaction, self.plan, Image.new('RGB', (20, 20), 'red'),
                                             'capture_01.jpg', 'capture')
        self.output = self.transaction.folder_path / 'output' / 'session_001' / 'template_a.png'
        self.output.parent.mkdir(parents=True)
        Image.new('RGB', (20, 20), 'green').save(self.output)
        self.store.record_output(self.transaction, self.plan.session_id, [self.raw] * 3, self.output)

    def saved(self):
        return json.loads(self.transaction.manifest_path.read_text())

    def change(self, **changes):
        manifest = self.saved()
        manifest.update(changes)
        self.store._atomic_write_json(self.transaction.manifest_path, manifest)
        return manifest

    def test_local_boundary_keeps_metadata_counter_and_never_reuses_a_transaction_id(self):
        self.change(created_at=(self.now - timedelta(days=15)).isoformat())
        counter = self.store.state_path.read_bytes()
        before = self.transaction.manifest_path.read_bytes()
        purge_local_photos(self.photos, now=self.now - timedelta(microseconds=1))
        self.assertTrue(self.raw.exists())
        self.assertTrue(self.output.exists())
        self.assertEqual(self.transaction.manifest_path.read_bytes(), before)
        report = purge_local_photos(self.photos, now=self.now)
        self.assertEqual(report['transactions'], [self.transaction.transaction_id])
        self.assertFalse(self.raw.exists())
        self.assertFalse(self.output.exists())
        self.assertEqual(self.saved()['upload_status'], 'LOCAL_EXPIRED')
        self.assertTrue(self.saved()['local_photos_purged_at'])
        self.assertEqual(self.store.state_path.read_bytes(), counter)
        self.assertEqual(purge_local_photos(self.photos, now=self.now)['transactions'], [])
        self.assertEqual(self.store.reserve_transaction_id(), 'PB001_00000002')

    def test_offline_failed_and_verified_queues_all_lose_local_photo_bytes_at_fifteen_days(self):
        for state in ('LOCAL_ONLY', 'PENDING_UPLOAD', 'UPLOAD_RETRY', 'ACTION_REQUIRED', 'VERIFIED'):
            with self.subTest(state=state):
                self.raw.parent.mkdir(parents=True, exist_ok=True)
                self.raw.write_bytes(b'restored fixture')
                manifest = self.saved()
                manifest.pop('local_photos_expired_at', None)
                manifest.pop('local_photos_purged_at', None)
                manifest['created_at'] = (self.now - timedelta(days=16)).isoformat()
                for record in manifest['upload_files'].values():
                    record['status'] = state
                manifest['upload_status'] = 'UPLOAD_COMPLETE' if state == 'VERIFIED' else state
                self.store._atomic_write_json(self.transaction.manifest_path, manifest)
                purge_local_photos(self.photos, now=self.now)
                self.assertFalse(self.raw.exists())
                expected = 'UPLOAD_COMPLETE' if state == 'VERIFIED' else 'LOCAL_EXPIRED'
                self.assertEqual(self.saved()['upload_status'], expected)

    def test_local_only_worker_protects_current_photos_and_expires_abandoned_in_progress_sessions(self):
        worker = PhotoRetentionWorker(self.photos)
        worker.run_once(now=self.now)
        self.assertTrue(self.raw.exists())
        self.change(created_at=(self.now - timedelta(days=16)).isoformat(), status='IN_PROGRESS')
        worker.run_once(now=self.now)
        self.assertFalse(self.raw.exists())

    def test_expired_controller_capture_cannot_recreate_a_deleted_photo(self):
        self.change(created_at=(self.now - timedelta(days=16)).isoformat())
        purge_local_photos(self.photos, now=self.now)
        with self.assertRaisesRegex(RuntimeError, 'retention deadline'):
            self.store.save_raw_photo(self.transaction, self.plan, Image.new('RGB', (10, 10)), 'capture_02.jpg', 'capture')
        self.assertFalse((self.transaction.folder_path / 'raw').exists())

    def test_invalid_dates_unknown_folders_and_outside_symlink_targets_are_preserved(self):
        self.change(created_at='not a date')
        purge_local_photos(self.photos, now=self.now)
        self.assertTrue(self.raw.exists())
        self.change(created_at=(self.now - timedelta(days=16)).isoformat())
        outside = self.root / 'personal'
        outside.mkdir()
        private = outside / 'private.jpg'
        private.write_bytes(b'keep outside bytes')
        linked = self.raw.parent / 'linked'
        try:
            linked.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            # Standard Windows users can lack the SeCreateSymbolicLinkPrivilege
            # even though the retention implementation is otherwise valid.
            # Skip this specific filesystem-permission case, not the whole
            # retention suite or other unexpected symlink errors.
            if getattr(error, "winerror", None) == 1314:
                self.skipTest("Windows account cannot create symbolic links")
            raise
        unknown = self.photos / 'unrelated'
        unknown.mkdir()
        (unknown / 'picture.jpg').write_bytes(b'keep unrelated bytes')
        purge_local_photos(self.photos, now=self.now)
        self.assertEqual(private.read_bytes(), b'keep outside bytes')
        self.assertTrue((unknown / 'picture.jpg').exists())
        self.assertFalse(linked.exists())

    def test_legacy_generated_photos_expire_but_arbitrary_root_images_do_not(self):
        old = self.photos / 'photo_20260901_120000_000001.jpg'
        recent = self.photos / 'photo_20261016_120000_000001.jpg'
        unrelated = self.photos / 'reference.jpg'
        for path in (old, recent, unrelated):
            path.write_bytes(b'fixture')
        stamp = (self.now - timedelta(days=16)).timestamp()
        os.utime(old, (stamp, stamp))
        os.utime(unrelated, (stamp, stamp))
        result = purge_local_photos(self.photos, now=self.now)
        self.assertEqual(result['legacy_photos'], 1)
        self.assertFalse(old.exists())
        self.assertTrue(recent.exists())
        self.assertTrue(unrelated.exists())

    def test_expired_transaction_cannot_start_an_upload(self):
        self.change(created_at=(self.now - timedelta(days=16)).isoformat())
        backend = MagicMock()
        result = sync_manifest(self.transaction.manifest_path, backend)
        self.assertEqual(result['upload_status'], 'LOCAL_EXPIRED')
        backend.upload_file.assert_not_called()
        backend.register_retention.assert_not_called()

    def test_late_success_and_resume_callbacks_cannot_resurrect_purged_photos(self):
        owner = self
        class Backend:
            def upload_file(self, _folder, _transaction, _relative, path, **kwargs):
                data = path.read_bytes()
                purge_local_photos(owner.photos, now=owner.now + timedelta(days=16))
                kwargs['on_session_url']('https://example.org/old-resume')
                return {'id': 'old-success', 'size': len(data),
                        'md5Checksum': hashlib.md5(data).hexdigest()}
        returned = sync_manifest(self.transaction.manifest_path, Backend())
        for manifest in (returned, self.saved()):
            self.assertEqual(manifest['upload_status'], 'LOCAL_EXPIRED')
            self.assertTrue(manifest['local_photos_expired_at'])
            self.assertTrue(all(r['status'] == 'LOCAL_EXPIRED' for r in manifest['upload_files'].values()))
        self.assertFalse(self.raw.exists())

    def test_original_drive_deadline_registration_survives_controller_saves(self):
        metadata = retention_metadata(self.transaction.transaction_id, self.saved()['created_at'])
        backend = MagicMock()
        backend.register_retention.return_value = metadata
        register_drive_retention(self.transaction.manifest_path, backend)
        register_drive_retention(self.transaction.manifest_path, backend)
        backend.register_retention.assert_called_once()
        self.store.save_raw_photo(self.transaction, self.plan, Image.new('RGB', (10, 10)), 'capture_02.jpg', 'capture')
        self.assertTrue(self.saved()['drive_retention_registered_at'])
        self.assertEqual(self.saved()['drive_photos_expire_at'], metadata['expires_at'])

    def test_old_backend_retention_error_is_recorded_without_discarding_new_photos(self):
        backend = MagicMock()
        backend.register_retention.side_effect = RuntimeError('Unsupported action: register_retention')
        with self.assertLogs('photobooth.retention', level='WARNING'):
            register_drive_retention(self.transaction.manifest_path, backend)
        self.assertIn('Unsupported action', self.saved()['drive_retention_error'])
        self.assertNotIn('drive_retention_registered_at', self.saved())
        self.assertTrue(self.raw.exists())


class DriveRetentionClientTests(unittest.TestCase):
    def test_description_requires_our_exact_marker_identity_and_thirty_day_duration(self):
        good = retention_metadata('PB001_00000001', datetime.now(timezone.utc).isoformat())
        self.assertEqual(read_drive_retention(json.dumps(good), good['transaction_id']), good)
        for changes in ({'managed_by': 'other-app'}, {'transaction_id': 'PB001_00000002'}, {'expires_at': good['started_at']}):
            self.assertIsNone(read_drive_retention(json.dumps({**good, **changes}), good['transaction_id']))

    def test_direct_oauth_deletes_only_expired_marked_assigned_folders_in_its_parent(self):
        client = GoogleDriveClient('booth-parent', 'fixture-id', 'fixture-secret', 'fixture-refresh')
        now = datetime.now(timezone.utc)
        old = retention_metadata('PB001_00000001', (now - timedelta(days=31)).isoformat())
        base = {'id': 'expired', 'name': old['transaction_id'], 'parents': ['booth-parent'],
                'mimeType': FOLDER_MIME_TYPE, 'description': json.dumps(old), 'appProperties': {}}
        client._list_files = MagicMock(return_value=[base, {**base, 'id': 'elsewhere', 'parents': ['other-parent']},
            {**base, 'id': 'ready', 'appProperties': {'photoboothStatus': 'READY'}},
            {**base, 'id': 'unknown', 'description': ''},
            {**base, 'id': 'recent', 'description': json.dumps(retention_metadata(old['transaction_id'], now.isoformat()))}])
        client._request = MagicMock()
        self.assertEqual(client.cleanup_expired()['deleted'], ['expired'])
        client._request.assert_called_once_with('DELETE', f'{API_ROOT}/files/expired', params={'supportsAllDrives': 'true'})

    def test_direct_oauth_register_retry_never_extends_an_existing_deadline(self):
        client = GoogleDriveClient('booth-parent', 'fixture-id', 'fixture-secret', 'fixture-refresh')
        now = datetime.now(timezone.utc)
        old = retention_metadata('PB001_00000001', (now - timedelta(days=2)).isoformat())
        response = MagicMock()
        response.json.return_value = {'id': 'folder', 'name': old['transaction_id'], 'parents': ['booth-parent'],
            'mimeType': FOLDER_MIME_TYPE, 'description': json.dumps(old)}
        client._request = MagicMock(return_value=response)
        self.assertEqual(client.register_retention('folder', old['transaction_id'], now.isoformat()), old)
        self.assertEqual(client._request.call_count, 1)  # No later PATCH.

    def test_direct_oauth_registration_claims_a_ready_slot_without_extending_its_clock(self):
        client = GoogleDriveClient('booth-parent', 'fixture-id', 'fixture-secret', 'fixture-refresh')
        now = datetime.now(timezone.utc)
        old = retention_metadata('PB001_00000001', (now - timedelta(days=2)).isoformat())
        response = MagicMock()
        response.json.return_value = {'id': 'folder', 'name': old['transaction_id'], 'parents': ['booth-parent'],
            'mimeType': FOLDER_MIME_TYPE, 'description': json.dumps(old),
            'appProperties': {'photoboothStatus': 'READY', 'photoboothSlotKey': 'keep-slot-key'}}
        client._request = MagicMock(return_value=response)
        self.assertEqual(client.register_retention('folder', old['transaction_id'], now.isoformat()), old)
        self.assertEqual(client._request.call_args.kwargs['json_body'], {'appProperties': {
            'photoboothStatus': 'ASSIGNED', 'photoboothSlotKey': 'keep-slot-key'}})

    def test_apps_script_actions_include_original_time_and_never_send_delete_all(self):
        client = AppsScriptDriveClient('https://example.org/exec', 'fixture-token')
        policy = retention_metadata('PB001_00000001', datetime.now(timezone.utc).isoformat())
        client._post = MagicMock(return_value={'ok': True, 'retention': policy, 'retention_enabled': True, 'enabled': True})
        self.assertEqual(client.register_retention('fixture-folder', policy['transaction_id'], policy['started_at']), policy)
        self.assertEqual(client._post.call_args.args[0]['started_at'], policy['started_at'])
        client.cleanup_expired()
        client._post.assert_called_with({'action': 'cleanup_retention'})

    def test_unactivated_server_is_not_reported_as_an_active_retention_policy(self):
        client = AppsScriptDriveClient('https://example.org/exec', 'fixture-token')
        client._post = MagicMock(return_value={'ok': True, 'retention_enabled': False, 'enabled': False})
        with self.assertRaisesRegex(DriveApiError, 'setupPhotoRetention'):
            client.register_retention('folder', 'PB001_00000001', datetime.now(timezone.utc).isoformat())
        with self.assertRaisesRegex(DriveApiError, 'setupPhotoRetention'):
            client.cleanup_expired()
