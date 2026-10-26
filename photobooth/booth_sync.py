"""Layout-2 adapters over the existing Apps Script client and upload engine.

No network operation admits a local session or replays a print. Tokens remain in
private local state, and clocks always originate in the transaction manifest.
"""
import base64
import json
import re
import time

from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError
from photobooth.drive_sync import DriveSyncWorker, sync_manifest
from photobooth.manifest_io import manifest_lock, write_json_atomic
from photobooth.retention import register_drive_retention
from photobooth.booth_storage import checked_path


class BoothDriveClient(AppsScriptDriveClient):
    def __init__(self, existing, booth_id):
        super().__init__(existing.web_app_url, existing.upload_token, session=existing.session)
        self.booth_id = booth_id

    def _post(self, payload):
        return super()._post({**payload, 'storage_layout': 2, 'booth_id': self.booth_id})

    def reserve_transactions(self, slots):
        result = self._post({'action': 'reserve_transactions', 'slots': slots})
        if result.get('storage_layout') != 2 or not isinstance(result.get('slots'), list):
            raise DriveApiError('Update the existing Web App for booth storage layout 2.', 409)
        expected = {s['transaction_id'] for s in slots}
        received = {s.get('transaction_id') for s in result['slots'] if s.get('status') == 'READY' and s.get('folder_id')}
        if expected != received:
            raise DriveApiError('Remote reserves did not match the local ledger.', 409)
        return result['slots']

    def bind_transaction(self, manifest):
        result = self._post({'action': 'bind_transaction',
            'transaction_id': manifest['transaction_id'], 'claim_token': manifest['drive_claim_token'],
            'started_at': manifest['created_at'], 'session_count': len(manifest['sessions'])})
        if (result.get('storage_layout') != 2 or result.get('transaction_id') != manifest['transaction_id']
                or not result.get('folder_id') or not re.fullmatch(
                    r'https://drive\.google\.com/drive/folders/[A-Za-z0-9_-]+', str(result.get('folder_url', '')))):
            raise DriveApiError('Remote transaction binding could not be verified.', 409)
        return result

    def asset_manifest(self):
        result = self._post({'action': 'asset_manifest'})
        if result.get('storage_layout') != 2 or not isinstance(result.get('files'), list):
            raise DriveApiError('Content manifest protocol mismatch.', 409)
        return result

    def asset_chunk(self, descriptor, offset, length):
        namespace = descriptor['path'].split('/')[0]
        if namespace == 'Local':
            namespace = '/'.join(descriptor['path'].split('/')[:2])
        result = self._post({'action': 'asset_chunk', 'namespace': namespace,
            'file_id': descriptor['id'], 'md5': descriptor['md5'], 'offset': offset, 'length': length})
        try:
            data = base64.b64decode(result['data'], validate=True)
            if (result['offset'] != offset or result['size'] != descriptor['size']
                    or result['md5'] != descriptor['md5'] or len(data) != length):
                raise ValueError()
            return data
        except (ValueError, KeyError, TypeError) as error:
            raise DriveApiError('Content chunk verification failed.', 502) from error


class BoothDriveWorker(DriveSyncWorker):
    """Reuse durable upload revisions/retention and worker lifecycle, without a remote admission gate."""
    def __init__(self, workspace, client, content=None):
        super().__init__(workspace.root, client, pool=None)
        self.workspace = workspace
        self.content = content
        self.last_error = False
        self._reserved = None
        self._content_checked = 0

    def run_once(self):
        for path in self.workspace.manifests():
            if self._stop.is_set():
                return
            try:
                manifest = json.loads(checked_path(path).read_text(encoding='utf-8'))
                if manifest.get('storage_layout') != 2 or not manifest.get('drive_intent'):
                    continue
                if not manifest.get('drive_folder_id'):
                    bound = self.client.bind_transaction(manifest)
                    with manifest_lock(path):
                        latest = json.loads(path.read_text(encoding='utf-8'))
                        if latest.get('transaction_id') != manifest['transaction_id']:
                            raise ValueError('Transaction identity changed.')
                        latest.update(drive_folder_id=bound['folder_id'], drive_folder_url=bound['folder_url'], drive_binding_error=None)
                        write_json_atomic(path, latest)
                # Expiry tombstones also register their original deadline; no
                # image can be resurrected by a late reconnect.
                register_drive_retention(path, self.client)
                manifest = json.loads(path.read_text(encoding='utf-8'))
                if manifest.get('drive_retention_registered_at') and manifest.get('upload_status') not in {'UPLOAD_COMPLETE', 'LOCAL_EXPIRED'}:
                    sync_manifest(path, self.client)
            except (OSError, ValueError, TypeError, RuntimeError):
                self.last_error = True
                continue
        slots = self.workspace.ready_slots()
        fingerprint = tuple(s['transaction_id'] for s in slots)
        if fingerprint != self._reserved:
            self.client.reserve_transactions(slots)
            self._reserved = fingerprint
        if self.content and time.monotonic() - self._content_checked >= 60:
            self._content_checked = time.monotonic()
            self.content.sync(self.client, cancelled=self._stop.is_set)

    def _run(self):
        while not self._stop.is_set():
            self.last_error = False
            try:
                self.run_once()
            except (OSError, ValueError, TypeError, RuntimeError):
                self.last_error = True
            self._wake.wait(self.interval_seconds)
            self._wake.clear()
