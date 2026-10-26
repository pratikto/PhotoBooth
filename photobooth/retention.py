"""Photo retention: 15 days on the booth and 30 days in its Drive destination.

Photo lifetimes start at transaction creation, never at empty-slot creation or
at a retry. Keep the small manifest/counter as a tombstone after removing image
bytes, so cleanup cannot reuse a transaction ID or restart an expired upload.
The Apps Script timer enforces Drive retention while the booth is switched off.
"""

from datetime import datetime, timedelta, timezone
import json
import logging
import os
from pathlib import Path
import re
import threading

from photobooth.manifest_io import manifest_lock, write_json_atomic


LOCAL_DAYS = 15
DRIVE_DAYS = 30
RETENTION_MARKER = 'meongs-photobooth-retention-v1'
TRANSACTION_ID = re.compile(r'^[A-Za-z0-9]+_[0-9]{8}$')
LEGACY_PHOTO = re.compile(r'^photo_[0-9]{8}_[0-9]{6}_[0-9]{6}\.jpg$')
LOGGER = logging.getLogger(__name__)


def _is_link(path):
    """Windows junctions are traversal boundaries just like symbolic links."""
    return path.is_symlink() or getattr(path, 'is_junction', lambda: False)()


def utc_datetime(value):
    """Reject ambiguous/malformed dates rather than guessing a deletion time."""
    stamp = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        raise ValueError('Retention timestamps must include their timezone.')
    return stamp.astimezone(timezone.utc)


def retention_metadata(transaction_id, started_at):
    """Use the same immutable marker/clock in Python and Apps Script."""
    if not TRANSACTION_ID.fullmatch(str(transaction_id)):
        raise ValueError('Invalid retention transaction ID.')
    started = utc_datetime(started_at)
    return {'managed_by': RETENTION_MARKER, 'transaction_id': transaction_id,
            'started_at': started.isoformat(),
            'expires_at': (started + timedelta(days=DRIVE_DAYS)).isoformat()}


def local_photos_expired(manifest, now=None):
    """A failed/offline upload never extends the requested local lifetime."""
    if manifest.get('local_photos_expired_at'):
        return True
    now = now if now is not None else datetime.now(timezone.utc)
    try:
        return now >= utc_datetime(manifest['created_at']) + timedelta(days=LOCAL_DAYS)
    except (ValueError, TypeError, KeyError):
        return False  # An unreadable clock needs inspection, not guessed deletion.


def read_drive_retention(description, transaction_id):
    """Only our exact marker and a 30-day deadline authorize Drive deletion."""
    try:
        policy = json.loads(description or '{}')
        if (policy.get('managed_by') != RETENTION_MARKER
                or policy.get('transaction_id') != transaction_id
                or not TRANSACTION_ID.fullmatch(str(transaction_id))):
            return None
        if utc_datetime(policy['expires_at']) != utc_datetime(policy['started_at']) + timedelta(days=DRIVE_DAYS):
            return None
        return policy
    except (ValueError, TypeError, KeyError, AttributeError):
        return None


def mark_local_expired(manifest, now=None):
    """Stop retries before unlinking photos, including delayed success callbacks."""
    now = now if now is not None else datetime.now(timezone.utc)
    manifest.setdefault('local_photos_expired_at', now.isoformat())
    for record in manifest.get('upload_files', {}).values():
        if record.get('status') != 'VERIFIED':
            record.update(status='LOCAL_EXPIRED', upload_session_url=None,
                          error='Local photo retention expired after 15 days.')
    if not all(record.get('status') == 'VERIFIED'
               for record in manifest.get('upload_files', {}).values()):
        manifest['upload_status'] = 'LOCAL_EXPIRED'


def register_drive_retention(manifest_path, client):
    """Register the original transaction date even for previously verified uploads.

    The server keeps the earlier timestamp on repeat requests, so a retry cannot
    renew the customer's folder. An old Web App can still accept photos while
    its missing retention API is recorded for the operator to deploy separately.
    Never hold the manifest lock during a network operation.
    """
    register = getattr(client, 'register_retention', None)
    if not callable(register):
        return
    path = Path(manifest_path)
    with manifest_lock(path):
        manifest = json.loads(path.read_text(encoding='utf-8'))
        if manifest.get('drive_retention_registered_at') or not manifest.get('drive_folder_id'):
            return
        metadata = retention_metadata(manifest['transaction_id'], manifest['created_at'])
    try:
        reply = register(manifest['drive_folder_id'], manifest['transaction_id'], metadata['started_at'])
        if not isinstance(reply, dict) or reply.get('managed_by') != RETENTION_MARKER:
            raise ValueError('Backend did not acknowledge the photo retention policy.')
        # A response cannot lengthen the clock originally requested by this client.
        if utc_datetime(reply['expires_at']) > utc_datetime(metadata['expires_at']):
            raise ValueError('Backend returned a later photo retention deadline.')
        changes = {'drive_retention_registered_at': datetime.now(timezone.utc).isoformat(),
                   'drive_photos_expire_at': reply['expires_at'], 'drive_retention_error': None}
    except Exception as error:
        changes = {'drive_retention_error': str(error)}
        LOGGER.warning('Drive retention registration failed for %s: %s', manifest['transaction_id'], error)
    with manifest_lock(path):
        latest = json.loads(path.read_text(encoding='utf-8'))
        latest.update(changes)
        write_json_atomic(path, latest)


def purge_local_photos(photos_root, *, now=None):
    """Remove expired booth image bytes without traversing links or unknown folders.

    Transaction age protects current customers naturally. Neither a stale active
    screen nor an abandoned IN_PROGRESS record extends the 15-day deadline.
    Keep transaction manifests, Drive-slot ledgers, credentials, and booth counters.
    The old photo_TIMESTAMP.jpg workflow is included using the file's saved time.
    """
    root = Path(photos_root)
    now = now if now is not None else datetime.now(timezone.utc)
    report = {'transactions': [], 'legacy_photos': 0, 'errors': []}
    if not root.is_dir() or _is_link(root):
        return report
    for folder in root.iterdir():
        if folder.name.casefold() == 'old':
            continue
        if _is_link(folder) or not folder.is_dir() or not TRANSACTION_ID.fullmatch(folder.name):
            continue
        path = folder / 'manifest.json'
        if _is_link(path) or not path.is_file():
            continue
        try:
            with manifest_lock(path):
                manifest = json.loads(path.read_text(encoding='utf-8'))
                if manifest.get('transaction_id') != folder.name or not local_photos_expired(manifest, now):
                    continue
                managed_names = ('Photo',) if manifest.get('storage_layout') == 2 else ('raw', 'output')
                if manifest.get('local_photos_purged_at') and not any((folder / name).exists() for name in managed_names):
                    continue
                mark_local_expired(manifest, now)
                write_json_atomic(path, manifest)  # Tombstone precedes any image deletion.
                for name in managed_names:
                    managed = folder / name
                    if _is_link(managed):
                        raise ValueError('Refusing to traverse a linked photo directory.')
                    if not managed.is_dir():
                        continue
                    visited = []
                    for directory, folders, files in os.walk(managed, topdown=True, followlinks=False):
                        visited.append(Path(directory))
                        for dirname in list(folders):
                            if dirname.casefold() == 'old':
                                raise ValueError('Archive directory excluded from retention.')
                            child = Path(directory) / dirname
                            if _is_link(child):
                                folders.remove(dirname)  # Prune before os.walk can descend into a junction.
                                if child.is_symlink():
                                    child.unlink()
                                else:
                                    child.rmdir()
                        for filename in files:
                            if filename.casefold() == 'old':
                                raise ValueError('Archive path excluded from retention.')
                            item = Path(directory) / filename
                            # These dedicated subtrees contain customer photo
                            # bytes and temporary image writes, not booth settings.
                            item.unlink()
                    for directory in reversed(visited):
                        directory.rmdir()
                manifest['local_photos_purged_at'] = now.isoformat()
                write_json_atomic(path, manifest)
                report['transactions'].append(folder.name)
        except (OSError, ValueError, TypeError) as error:
            report['errors'].append({'transaction_id': folder.name, 'error': str(error)})
    for item in root.iterdir():
        if item.name.casefold() == 'old':
            continue
        if _is_link(item) or not item.is_file() or not LEGACY_PHOTO.fullmatch(item.name):
            continue
        try:
            saved_at = datetime.fromtimestamp(item.stat().st_mtime, timezone.utc)
            if now >= saved_at + timedelta(days=LOCAL_DAYS):
                item.unlink()
                report['legacy_photos'] += 1
        except OSError as error:
            report['errors'].append({'file': item.name, 'error': str(error)})
    return report


class PhotoRetentionWorker:
    """Run local cleanup at startup and hourly, even in local-only mode.

    Register Drive clocks before local bytes expire. The cloud has its own
    installable timer; the optional client cleanup is an extra online sweep.
    No deletion or network operation runs on Kivy's event thread.
    """

    def __init__(self, photos_root, client=None, interval_seconds=3600):
        self.photos_root, self.client = Path(photos_root), client
        self.interval_seconds = interval_seconds
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name='photobooth-retention', daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()

    def run_once(self, now=None):
        # Purge first, so a long/offline registration request cannot postpone
        # local cleanup. Surviving tombstones still hold the original Drive clock.
        report = purge_local_photos(self.photos_root, now=now)
        for error in report['errors']:
            LOGGER.warning('Local photo retention cleanup requires attention: %s', error)
        if self.client is not None:
            for path in self.photos_root.glob('*/manifest.json'):
                if self._stop.is_set() or _is_link(path) or _is_link(path.parent):
                    continue
                try:
                    register_drive_retention(path, self.client)
                except (OSError, ValueError, TypeError, KeyError):
                    LOGGER.exception('Could not register retention for %s', path.parent.name)
            cleanup = getattr(self.client, 'cleanup_expired', None)
            if callable(cleanup) and not self._stop.is_set():
                try:
                    result = cleanup()
                    if isinstance(result, dict) and result.get('errors'):
                        LOGGER.warning('Drive retention cleanup requires attention: %s', result['errors'])
                except Exception:
                    LOGGER.exception('Drive retention cleanup requires attention.')
        return report

    def _run(self):
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception:
                LOGGER.exception('Photo retention cleanup requires attention.')
            self._stop.wait(self.interval_seconds)
