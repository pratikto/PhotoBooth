"""Per-booth storage v2; empty local reserves do not depend on Drive availability."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import threading
from uuid import uuid4

from photobooth.manifest_io import write_json_atomic
from photobooth.transaction_store import TransactionStore


def checked_path(path):
    """Reject archives and traversal through symlinks/junctions before any descent."""
    path = Path(path).absolute()
    if any(part.casefold() == 'old' or part == '..' for part in path.parts):
        raise ValueError('The old archive is excluded from active storage.')
    for parent in (*reversed(path.parents), path):
        if parent.is_symlink() or getattr(parent, 'is_junction', lambda: False)():
            raise ValueError('Linked storage paths are not allowed.')
    return path


class BoothWorkspace:
    """One writer per booth, monotonic IDs and durable claims; never scans old."""
    def __init__(self, data_root, booth_id='PB001V2', *, target_ready=25, seed_counter=None):
        if not re.fullmatch(r'PB[0-9]+(?:V2(?:S2)?)?', booth_id):
            raise ValueError('Use a PB001-style booth identity.')
        self.booth_id = booth_id
        self.physical_id = re.sub(r'V2(?:S2)?$', '', booth_id)
        self.root = checked_path(Path(data_root) / self.physical_id)
        self.state_root = self.root / '_state'
        self.state_path = self.state_root / ('pool-' + booth_id + '.json')
        self.counter_path = self.state_root / ('counter-' + booth_id + '.json')
        self.target_ready = max(25, int(target_ready))
        self.seed_counter = checked_path(seed_counter) if seed_counter else None
        self._lock = threading.RLock()

    @contextmanager
    def locked(self):
        with self._lock:
            checked_path(self.state_root).mkdir(parents=True, exist_ok=True)
            with checked_path(self.state_root / 'storage.lock').open('a+b') as stream:
                if os.name == 'nt':
                    import msvcrt
                    stream.seek(0); stream.write(b'0'); stream.flush(); stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    if os.name == 'nt':
                        stream.seek(0); msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def _load(self):
        if self.state_path.exists():
            state = json.loads(checked_path(self.state_path).read_text())
            if state.get('booth_id') != self.booth_id or state.get('schema_version') != 2:
                raise ValueError('Booth reserve ledger identity is invalid.')
            if not isinstance(state.get('ready'), list) or not isinstance(state.get('claimed'), dict):
                raise ValueError('Booth reserve ledger is invalid.')
            seen = set()
            for slot in [*state['ready'], *state['claimed'].values()]:
                txid = slot.get('transaction_id') if isinstance(slot, dict) else None
                if (not isinstance(txid, str) or not re.fullmatch(re.escape(self.booth_id) + r'_[0-9]{8}', txid)
                        or not re.fullmatch(r'[a-f0-9]{32}', str(slot.get('claim_token', '')))
                        or txid in seen):
                    raise ValueError('Invalid or duplicate reserved identity.')
                seen.add(txid)
                if slot.get('folder_id') and (not re.fullmatch(r'[A-Za-z0-9_-]+', str(slot['folder_id']))
                        or slot.get('folder_url') != 'https://drive.google.com/drive/folders/' + slot['folder_id']):
                    raise ValueError('Reserved remote folder link is invalid.')
            if state['ready'] or state['claimed']:
                if not checked_path(self.counter_path).is_file():
                    raise ValueError('Restore the missing counter before allocating new IDs.')
            return state
        return {'schema_version': 2, 'booth_id': self.booth_id, 'ready': [], 'claimed': {}}

    def _refill(self, state):
        checked_path(self.counter_path)
        store = TransactionStore(self.root, self.counter_path, self.booth_id, layout_version=2)
        while len(state['ready']) < self.target_ready:
            txid = store.reserve_transaction_id()
            folder = checked_path(self.root / txid)
            if folder.exists():
                continue  # Never recycle or inspect existing customer directories.
            folder.mkdir()
            state['ready'].append({'transaction_id': txid, 'claim_token': uuid4().hex})
            write_json_atomic(self.state_path, state)

    def prepare(self):
        with self.locked():
            for sub in ('Local/Advertisement', 'Local/Template',
                        'Cache/Global_Advertisement', 'Cache/Global_Template'):
                checked_path(self.root / sub).mkdir(parents=True, exist_ok=True)
            if not self.counter_path.exists() and self.seed_counter and self.seed_counter.is_file():
                seed = json.loads(self.seed_counter.read_text())
                if seed.get('booth_id') == self.booth_id:
                    number = seed.get('next_sequence')
                    if type(number) is not int or number < 1:
                        raise ValueError('Active counter checkpoint is invalid.')
                    write_json_atomic(self.counter_path, seed)
            state = self._load()
            self._refill(state)
            return len(state['ready'])

    def ready_slots(self):
        with self.locked():
            return [dict(slot) for slot in self._load()['ready']]

    def remember_remote(self, remote):
        """Cache actual reserved IDs/URLs, never manufacture a download address."""
        with self.locked():
            state = self._load()
            by_id = {slot['transaction_id']: slot for slot in remote}
            for slot in state['ready']:
                reply = by_id.get(slot['transaction_id'])
                if reply:
                    slot.update(folder_id=reply['folder_id'], folder_url=reply['folder_url'], photo_number_layout=reply.get('photo_number_layout'), link_verified=reply.get('link_verified', False))
            write_json_atomic(self.state_path, state)

    def claim(self):
        with self.locked():
            state = self._load()
            self._refill(state)
            slot = state['ready'][0]
            folder = checked_path(self.root / slot['transaction_id'])
            if not folder.is_dir() or any(folder.iterdir()):
                raise ValueError('Ready transaction directory is missing or not empty.')
            state['ready'].pop(0)
            state['claimed'][slot['transaction_id']] = dict(slot)
            write_json_atomic(self.state_path, state)  # Claim before the first manifest/photo.
            try:
                self._refill(state)
            except OSError:
                # The admitted claim survives; the next prepare retries replenishment.
                state['refill_error'] = 'storage_unavailable'
                write_json_atomic(self.state_path, state)
            return {**slot, 'staging_path': str(folder)}

    def manifests(self):
        """Direct, identity-checked transaction roots only; no recursive archive scan."""
        if not self.root.is_dir():
            return
        pattern = re.compile(re.escape(self.booth_id) + r'_[0-9]{8}')
        for folder in self.root.iterdir():
            if not pattern.fullmatch(folder.name):
                continue
            checked_path(folder)
            manifest = checked_path(folder / 'manifest.json')
            if manifest.is_file():
                yield manifest

