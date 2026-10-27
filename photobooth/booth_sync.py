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
from photobooth.delivery_retry import DeliveryRetries

from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError
from photobooth.drive_sync import DriveSyncWorker, sync_manifest
from photobooth.manifest_io import manifest_lock, write_json_atomic
from photobooth.retention import register_drive_retention
from photobooth.booth_storage import checked_path


class DriveBindingError(DriveApiError):
    """Fixed diagnostic codes; never include returned IDs, URLs or claim tokens."""
    def __init__(self, code):
        self.code = code
        super().__init__(code, 409)


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
        if result.get('storage_layout') != 2 or result.get('photo_number_layout') != 1:
            raise DriveBindingError('BIND_LAYOUT_UNSUPPORTED')
        if result.get('transaction_id') != manifest['transaction_id']:
            raise DriveBindingError('BIND_RESPONSE_ID_MISMATCH')
        if result.get('link_verified') is not True:
            raise DriveBindingError('BIND_LINK_UNVERIFIED')
        folder_id = result.get('folder_id')
        if (not isinstance(folder_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', folder_id)
                or result.get('folder_url') != 'https://drive.google.com/drive/folders/' + folder_id):
            raise DriveBindingError('BIND_RESPONSE_INVALID')
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
        self.retries = DeliveryRetries()

    def notify_transaction(self, transaction_id):
        with self._queue_lock:
            if transaction_id not in self._queued:
                self._queued[transaction_id] = time.monotonic()
                event('queued', transaction_id, queue_depth=len(self._queued))
        self.kick()

    def _interrupted(self):
        return self._stop.is_set() or self._wake.is_set()

    def _record_failure(self, path, tx, code, phase, error=None, *, customer=False):
        self.last_error = True
        retry = self.retries.failed(tx, code, phase, customer=customer)
        event('transaction_error', tx, error=type(error).__name__ if error else None,
              error_code=code, phase=phase, retry_seconds=retry['delay_seconds'],
              failure_count=retry['failures'], customer_priority=retry['customer_priority'], result='retry')
        try:
            with manifest_lock(path):
                latest = json.loads(checked_path(path).read_text(encoding='utf-8'))
                # A mismatched identity must never receive another transaction's metadata.
                if not isinstance(latest, dict) or latest.get('transaction_id') != tx:
                    return
                latest['drive_delivery_retry'] = retry
                if phase == 'bind':
                    latest['drive_binding_error'] = ('DRIVE_SETUP_REQUIRED' if isinstance(error, DriveApiError)
                                                     and error.status_code == 409 else 'DRIVE_RETRY')
                write_json_atomic(path, latest)
        except (OSError, ValueError, TypeError):
            # Unreadable state remains intact; memory backoff bounds log/retry churn.
            pass

    def _clear_failure(self, path, tx, *, background=False):
        if tx not in self.retries.states:
            return
        with manifest_lock(path):
            latest = json.loads(checked_path(path).read_text(encoding='utf-8'))
            if latest.get('transaction_id') != tx:
                raise DriveBindingError('BIND_TRANSACTION_CHANGED')
            background = background and self._needs_delivery(latest)
            latest['drive_delivery_retry'] = ({'failures': 0, 'delay_seconds': 0,
                'not_before_unix': time.time(), 'background_only': True} if background else None)
            if latest.get('drive_binding_verified'):
                latest['drive_binding_error'] = None
            write_json_atomic(path, latest)
        self.retries.recovered(tx, background=background)
        event('transaction_recovered', tx, result='ok')

    @staticmethod
    def _error_code(error, phase):
        if isinstance(error, DriveBindingError):
            return error.code
        if isinstance(error, DriveApiError):
            return 'DRIVE_NETWORK_RETRY' if error.transient else 'DRIVE_REMOTE_REJECTED'
        return {'manifest': 'MANIFEST_INVALID', 'bind': 'BIND_LOCAL_STATE_INVALID',
                'retention': 'RETENTION_LOCAL_STATE_INVALID', 'upload': 'UPLOAD_LOCAL_STATE_INVALID'}[phase]

    def _process_transaction(self, path, tx, *, lane):
        phase = 'manifest'
        customer = lane == 'customer'
        try:
            manifest = json.loads(checked_path(path).read_text(encoding='utf-8'))
            if manifest.get('transaction_id') != tx:
                raise DriveBindingError('BIND_TRANSACTION_CHANGED')
            if manifest.get('storage_layout') != 2 or not manifest.get('drive_intent'):
                return False
            with self._queue_lock:
                queued = self._queued.pop(tx, None)
            event('worker_start', tx, lane=lane,
                  queue_wait_ms=round((time.monotonic()-queued)*1000, 1) if queued is not None else None,
                  queue_origin='notified' if queued is not None else 'discovered')
            phase = 'bind'
            if not manifest.get('drive_binding_verified') or manifest.get('photo_number_layout') != 1:
                with span('bind', tx):
                    bound = self.client.bind_transaction(manifest)
                with manifest_lock(path):
                    latest = json.loads(path.read_text(encoding='utf-8'))
                    if latest.get('transaction_id') != tx:
                        raise DriveBindingError('BIND_TRANSACTION_CHANGED')
                    if latest.get('drive_folder_id') and latest['drive_folder_id'] != bound['folder_id']:
                        raise DriveBindingError('BIND_FOLDER_CONFLICT')
                    # Existing manifests also protect pre-update offline bindings
                    # whose folder has not yet been added to the claim ledger.
                    for other in self.workspace.manifests():
                        if other == path:
                            continue
                        try:
                            previous = json.loads(other.read_text(encoding='utf-8'))
                        except (OSError, ValueError, TypeError):
                            continue  # Its ledger/server claim remains protected.
                        if isinstance(previous, dict) and previous.get('drive_folder_id') == bound['folder_id']:
                            raise DriveBindingError('BIND_FOLDER_CONFLICT')
                    try:
                        self.workspace.remember_binding(tx, latest['drive_claim_token'], bound)
                    except ValueError as error:
                        raise DriveBindingError('BIND_FOLDER_CONFLICT') from error
                    latest.update(drive_folder_id=bound['folder_id'], drive_folder_url=bound['folder_url'],
                                  drive_binding_verified=True, drive_binding_error=None, photo_number_layout=1)
                    write_json_atomic(path, latest)
            # Let an admitted request finish, then yield old recovery before its
            # next network stage when a customer arrives during that request.
            if not customer and self._interrupted():
                return False
            phase = 'retention'
            with span('retention', tx):
                register_drive_retention(path, self.client)
            manifest = json.loads(path.read_text(encoding='utf-8'))
            if manifest.get('drive_retention_error'):
                self._record_failure(path, tx, 'RETENTION_HOLD', phase, customer=customer)
                return False
            if not customer and self._interrupted():
                return False
            phase = 'upload'
            if manifest.get('drive_retention_registered_at') and manifest.get('upload_status') not in {'UPLOAD_COMPLETE', 'LOCAL_EXPIRED'}:
                before = manifest.get('upload_files', {})
                result = sync_manifest(path, self.client, max_files=1,
                                       cancelled=self._stop.is_set if customer else self._interrupted)
                records = result.get('upload_files', {})
                failed = any(r.get('status') == 'UPLOAD_RETRY' and
                             r.get('attempts', 0) > before.get(key, {}).get('attempts', 0)
                             for key, r in records.items())
                if failed:
                    self._record_failure(path, tx, 'UPLOAD_RETRY', phase, customer=customer)
                    return False
                self._clear_failure(path, tx, background=not customer)
                return any(r.get('status') not in {'VERIFIED', 'ACTION_REQUIRED', 'LOCAL_EXPIRED'}
                           for r in records.values())
            self._clear_failure(path, tx, background=not customer)
        except (OSError, ValueError, TypeError, RuntimeError, KeyError) as error:
            self._record_failure(path, tx, self._error_code(error, phase), phase, error, customer=customer)
        return False

    @staticmethod
    def _needs_delivery(manifest):
        if manifest.get('upload_status') in {'UPLOAD_COMPLETE', 'LOCAL_EXPIRED', 'LOCAL_ONLY', 'ACTION_REQUIRED'}:
            return False
        return (not manifest.get('drive_binding_verified') or manifest.get('photo_number_layout') != 1
                or not manifest.get('drive_retention_registered_at')
                or any(r.get('status') not in {'VERIFIED', 'ACTION_REQUIRED', 'LOCAL_EXPIRED', 'LOCAL_ONLY'}
                       for r in manifest.get('upload_files', {}).values()))

    def _pending_deliveries(self):
        customers = []
        recovery = []
        for path in sorted(self.workspace.manifests()):
            if self._stop.is_set():
                break
            tx = path.parent.name
            try:
                manifest = json.loads(checked_path(path).read_text(encoding='utf-8'))
                if not isinstance(manifest, dict):
                    raise ValueError('Invalid transaction metadata.')
                if manifest.get('storage_layout') != 2 or not manifest.get('drive_intent'):
                    continue
                if not self._needs_delivery(manifest):
                    continue
                state = self.retries.state(tx, manifest)
                if state is not None and (state.get('background_only') or not state.get('customer_priority')):
                    recovery.append((tx, path))
                else:
                    customers.append((tx, path))
            except (OSError, ValueError, TypeError, KeyError) as error:
                state = self.retries.states.get(tx)
                if state is None or state['due'] <= time.monotonic():
                    self._record_failure(path, tx, 'MANIFEST_INVALID', 'manifest', error)
        return customers, recovery

    def run_once(self):
        customers, recovery = self._pending_deliveries()
        # Stable monotonic transaction IDs provide FIFO across customer sessions.
        # Keep the head through its files and two short retries; no old recovery,
        # reserves or content requests are admitted while customer work remains.
        if customers and not self._stop.is_set():
            tx, path = customers[0]
            state = self.retries.states.get(tx)
            if state is not None and state['due'] > time.monotonic():
                return False  # Wait for its persisted deadline, without busy-spinning.
            self._process_transaction(path, tx, lane='customer')
            customers, recovery = self._pending_deliveries()
            if customers:
                state = self.retries.states.get(customers[0][0])
                return state is None or state['due'] <= time.monotonic()
        # Background resumes after verified completion or bounded failure release.
        more = False
        if not self._interrupted():
            selected = self.retries.choose(recovery)
            if selected is not None:
                tx, path = selected
                recovering = not self.retries.states[tx].get('background_only')
                try:
                    more = self._process_transaction(path, tx, lane='recovery') or more
                finally:
                    if recovering:
                        self.retries.finish_turn()
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
