"""Layout-2 adapters over the existing Apps Script client and upload engine.

No network operation admits a local session or replays a print. Tokens remain in
private local state, and clocks always originate in the transaction manifest.
"""
import base64
import json
import logging
import re
import time
import threading

from photobooth.delivery_timing import event, span

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
        if payload.get('action') == 'upload_file':
            match = re.fullmatch(r'Photo/(\d{2})/(raw|color|bw)/([^/]+)', payload['relative_path'])
            if not match:
                raise DriveApiError('Invalid local session upload path.', 400)
            session, kind, filename = match.groups()
            filename = f'session_{int(session):03d}_{filename}'
            payload = {**payload, 'relative_path': f'{kind}/{filename}', 'filename': filename}
        return super()._post({**payload, 'storage_layout': 2, 'booth_id': self.booth_id})

    def reserve_transactions(self, slots):
        result = self._post({'action': 'reserve_transactions', 'slots': slots})
        if result.get('storage_layout') != 2 or not isinstance(result.get('slots'), list):
            raise DriveApiError('Update the existing Web App for booth storage layout 2.', 409)
        expected = {s['transaction_id'] for s in slots}
        received = {s.get('transaction_id') for s in result['slots'] if s.get('status') == 'READY' and s.get('folder_id')}
        if expected != received:
            raise DriveApiError('Remote reserves did not match the local ledger.', 409)
        folder_ids = set()
        for slot in result['slots']:
            folder_id = slot['folder_id']
            if (slot.get('link_verified') is not True or slot.get('photo_number_layout') != 1
                    or folder_id in folder_ids or not re.fullmatch(r'[A-Za-z0-9_-]+', folder_id)
                    or slot.get('folder_url') != 'https://drive.google.com/drive/folders/' + folder_id):
                raise DriveApiError('Remote reserve links could not be verified.', 409)
            folder_ids.add(folder_id)
        return result['slots']

    def bind_transaction(self, manifest):
        result = self._post({'action': 'bind_transaction',
            'transaction_id': manifest['transaction_id'], 'claim_token': manifest['drive_claim_token'],
            'started_at': manifest['created_at'], 'session_count': len(manifest['sessions'])})
        if (result.get('photo_number_layout') != 1 or result.get('link_verified') is not True
                or result.get('storage_layout') != 2 or result.get('transaction_id') != manifest['transaction_id']
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
    """One writer; round-robin customer files precede bounded maintenance requests."""
    RESERVE_BATCH = 5
    RECONCILE_SECONDS = 15 * 60

    def __init__(self, workspace, client, content=None):
        super().__init__(workspace.root, client, pool=None)
        self.workspace = workspace
        self.content = content
        self.last_error = False
        self._verified_reserves = {}
        self._reconcile_at = None
        self._content_checked = 0
        self._queue_lock = threading.Lock()
        self._queued = {}
        self._retry_after = {}

    def notify_transaction(self, transaction_id):
        with self._queue_lock:
            if transaction_id not in self._queued:
                self._queued[transaction_id] = time.monotonic()
                event('queued', transaction_id, queue_depth=len(self._queued))
        self.kick()

    def _interrupted(self):
        return self._stop.is_set() or self._wake.is_set()

    def run_once(self):
        more = False
        # Stable ordering plus one file per visit prevents either old or new sessions
        # from monopolizing a pass. Failed requests wait for the normal retry interval.
        for path in sorted(self.workspace.manifests()):
            if self._stop.is_set():
                return False
            try:
                manifest = json.loads(checked_path(path).read_text(encoding='utf-8'))
                if manifest.get('storage_layout') != 2 or not manifest.get('drive_intent'):
                    continue
                tx = manifest['transaction_id']
                if time.monotonic() < self._retry_after.get(tx, 0):
                    continue
                if (manifest.get('drive_binding_verified') and manifest.get('photo_number_layout') == 1
                        and manifest.get('drive_retention_registered_at')
                        and manifest.get('upload_status') in {'UPLOAD_COMPLETE', 'LOCAL_EXPIRED'}):
                    continue
                with self._queue_lock:
                    queued = self._queued.pop(tx, None)
                event('worker_start', tx, queue_wait_ms=round((time.monotonic()-queued)*1000, 1)
                      if queued is not None else None, queue_origin='notified' if queued is not None else 'discovered')
                if not manifest.get('drive_binding_verified') or manifest.get('photo_number_layout') != 1:
                    with span('bind', tx):
                        bound = self.client.bind_transaction(manifest)
                    with manifest_lock(path):
                        latest = json.loads(path.read_text(encoding='utf-8'))
                        if latest.get('transaction_id') != tx:
                            raise ValueError('Transaction identity changed.')
                        if latest.get('drive_folder_id') and latest['drive_folder_id'] != bound['folder_id']:
                            raise ValueError('A known reserved folder cannot be replaced.')
                        latest.update(drive_folder_id=bound['folder_id'], drive_folder_url=bound['folder_url'],
                                      drive_binding_verified=True, drive_binding_error=None, photo_number_layout=1)
                        write_json_atomic(path, latest)
                with span('retention', tx):
                    register_drive_retention(path, self.client)
                manifest = json.loads(path.read_text(encoding='utf-8'))
                if manifest.get('drive_retention_error'):
                    event('retention_hold', tx, result='retry')
                    self._retry_after[tx] = time.monotonic() + self.interval_seconds
                if manifest.get('drive_retention_registered_at') and manifest.get('upload_status') not in {'UPLOAD_COMPLETE', 'LOCAL_EXPIRED'}:
                    result = sync_manifest(path, self.client, max_files=1, cancelled=self._stop.is_set)
                    records = list(result.get('upload_files', {}).values())
                    if any(r.get('status') == 'UPLOAD_RETRY' for r in records):
                        self._retry_after[tx] = time.monotonic() + self.interval_seconds
                    elif any(r.get('status') not in {'VERIFIED', 'ACTION_REQUIRED', 'LOCAL_EXPIRED'} for r in records):
                        more = True
            except (OSError, ValueError, TypeError, RuntimeError) as error:
                self.last_error = True
                self._retry_after[path.parent.name] = time.monotonic() + self.interval_seconds
                event('transaction_error', path.parent.name, error=type(error).__name__, result='retry')
                with manifest_lock(path):
                    latest = json.loads(path.read_text(encoding='utf-8'))
                    latest['drive_binding_error'] = 'DRIVE_SETUP_REQUIRED' if isinstance(error, DriveApiError) and error.status_code == 409 else 'DRIVE_RETRY'
                    write_json_atomic(path, latest)
        if more or self._interrupted():
            return more
        self._maintain_reserves()
        if self._interrupted():
            return False
        if self.content and (self.content.pending or time.monotonic() - self._content_checked >= 60):
            with span('content_sync'):
                self.content.sync(self.client, cancelled=self._interrupted)
            if not self.content.pending:
                self._content_checked = time.monotonic()
            else:
                event('content_yield', result='customer_or_stop')
        return False

    @staticmethod
    def _reserve_identity(slot):
        return tuple(slot.get(k) for k in ('claim_token', 'folder_id', 'folder_url',
                                           'link_verified', 'photo_number_layout'))

    def _maintain_reserves(self):
        now = time.monotonic()
        if self._reconcile_at is not None and now >= self._reconcile_at:
            self._verified_reserves.clear()
            self._reconcile_at = None
        slots = self.workspace.ready_slots()
        ready = {s['transaction_id'] for s in slots}
        self._verified_reserves = {tx: value for tx, value in self._verified_reserves.items() if tx in ready}
        pending = [s for s in slots if self._verified_reserves.get(s['transaction_id']) != self._reserve_identity(s)]
        # Bound each lock-held server request; kick can interrupt before the next batch.
        for start in range(0, len(pending), self.RESERVE_BATCH):
            if self._interrupted():
                return
            batch = pending[start:start+self.RESERVE_BATCH]
            with span('reserve', slots=len(batch), remaining=len(pending)-start):
                remote = self.client.reserve_transactions([{k: s[k] for k in ('transaction_id', 'claim_token')} for s in batch])
            self.workspace.remember_remote(remote)
            # Only an acknowledged response validates a reserve. Cached URLs alone
            # cannot suppress startup or periodic ownership/link reconciliation.
            acknowledged = {s['transaction_id'] for s in remote}
            for slot in self.workspace.ready_slots():
                if slot['transaction_id'] in acknowledged:
                    self._verified_reserves[slot['transaction_id']] = self._reserve_identity(slot)
        if all(s['transaction_id'] in self._verified_reserves for s in self.workspace.ready_slots()):
            if self._reconcile_at is None:
                self._reconcile_at = time.monotonic() + self.RECONCILE_SECONDS

    def _run(self):
        while not self._stop.is_set():
            self._wake.clear()  # Kicks arriving during requests remain set until the next pass.
            self.last_error = False
            try:
                more = self.run_once()
            except (OSError, ValueError, TypeError, RuntimeError) as error:
                self.last_error = True
                event('maintenance_error', error=type(error).__name__, result='retry')
                more = False
            if more:
                continue
            self._wake.wait(self.interval_seconds)
