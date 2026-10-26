"""Read-only startup review over existing v2 journals; never authorize replay.

No Kivy/service imports: this must work before devices or native providers start.
Only direct known journal locations are inspected, never photos or archives.
"""
from collections import Counter
from contextlib import closing
import json
import os
from pathlib import Path
import re
import sqlite3

MAX_JSON = 4 * 1024 * 1024
MAX_ENTRIES = 10000
RECOVERY_EXIT = 3


def checked_path(path):
    """Same archive/link boundary as BoothWorkspace, without its Pillow import."""
    path = Path(path).absolute()
    if any(part.casefold() == 'old' or part == '..' for part in path.parts):
        raise ValueError('Excluded storage path')
    for component in (*reversed(path.parents), path):
        if component.is_symlink() or getattr(component, 'is_junction', lambda: False)():
            raise ValueError('Linked storage path')
    return path


class LaunchLease:
    """One v2 launcher per checkout, including ordinary and merchant trial.

    Native locking mirrors the payment KioskLease, whose module imports Pillow
    through quotation/catalogue code and cannot be used on this pre-GUI path.
    Never unlink the lock file: the kernel releases ownership on process exit.
    """
    def __init__(self, root):
        path = checked_path(Path(root) / 'data' / 'kiosk-v2-launch.lock')
        path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = path.open('a+b')
        try:
            self.stream.seek(0)
            if not self.stream.read(1):
                self.stream.write(b'0')
                self.stream.flush()
            self.stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            self.stream.close()
            raise

    def close(self):
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


class RecoveryReview:
    def __init__(self, *, limit=MAX_ENTRIES):
        self.findings = Counter()
        self.checked = Counter()
        self.remaining = limit

    def json(self, path):
        path = checked_path(path)
        with path.open('rb') as stream:
            raw = stream.read(MAX_JSON + 1)
        if len(raw) > MAX_JSON:
            raise ValueError('Oversized journal')
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError('Invalid journal')
        return data

    def entries(self, root):
        root = checked_path(root)
        if not root.exists():
            return
        with os.scandir(root) as items:
            for item in items:
                # Do not descend/resolve old, even when it is a symlink.
                if item.name.casefold() == 'old':
                    continue
                self.remaining -= 1
                if self.remaining < 0:
                    raise ValueError('Review limit exceeded')
                yield Path(item.path)

    def sandbox(self, path):
        data = self.json(path)
        self.checked['sandbox_journals'] += 1
        phase = data.get('phase')
        if data.get('version') != 1 or phase not in {
                'CREATING', 'WAITING', 'RESERVED', 'STARTING', 'STARTED', 'COMPLETING',
                'COMPLETED', 'CANCELLING', 'CANCELLED', 'RECOVERY'}:
            raise ValueError('Invalid payment journal')
        if phase not in {'COMPLETED', 'CANCELLED'}:
            self.findings['SANDBOX_UNRESOLVED'] += 1

    def manifest(self, path):
        data = self.json(path)
        self.checked['photo_manifests'] += 1
        # The original store durably creates IN_PROGRESS before adding purpose.
        # Missing purpose/status is therefore not proof that a visit is safe.
        if data.get('status') != 'COMPLETED' and data.get('test_ended_early') is not True:
            self.findings['PHOTO_INCOMPLETE'] += 1
        jobs = data.get('test_print_jobs', {})
        if not isinstance(jobs, dict):
            raise ValueError('Invalid print journal')
        for job in jobs.values():
            if not isinstance(job, dict) or job.get('state') not in {'SENDING', 'SUBMITTED', 'UNCERTAIN'}:
                raise ValueError('Unknown print state')
            if job['state'] == 'SENDING' or (job['state'] == 'UNCERTAIN' and job.get('operator_checked') is not True):
                self.findings['PRINT_UNCERTAIN'] += 1

    def photos(self, root):
        for folder in self.entries(root):
            # Legacy opt-in profiles permit non-PB booth names ending in V2;
            # TransactionStore also keeps growing the minimum-eight-digit suffix.
            if not re.fullmatch(r'[A-Za-z0-9_-]+_[0-9]{8,}', folder.name):
                continue
            folder = checked_path(folder)
            path = checked_path(folder / 'manifest.json')
            if path.exists():
                self.manifest(path)
            # Empty reserve folders are not interrupted sessions. A nonempty
            # transaction without its manifest needs review; never inspect media.
            elif any(True for _ in self.entries(folder)):
                self.findings['MISSING_PHOTO_MANIFEST'] += 1

    def mock(self, path):
        path = checked_path(path)
        if not path.exists():
            return
        for suffix in ('-wal', '-shm'):
            checked_path(str(path) + suffix)
        # mode=ro prevents creation or accidental ledger updates/expiry. Do not
        # use immutable=1: it could hide an uncheckpointed live WAL transaction.
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=.2)) as db:
            try:
                rows = db.execute('SELECT state, COUNT(*) FROM mock_orders GROUP BY state').fetchall()
            except sqlite3.OperationalError:
                # Game-only ledgers legitimately have attempts but no mock_orders.
                if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='mock_orders'").fetchone():
                    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='attempts'").fetchone():
                        self.checked['mock_ledgers'] += 1
                        return
                raise
        self.checked['mock_ledgers'] += 1
        for state, count in rows:
            if state not in {'CANCELLED', 'EXPIRED', 'ADMITTED'}:
                self.findings['MOCK_UNRESOLVED'] += count

    def result(self):
        return {'schema_version': 1,
                'status': 'OPERATOR_REVIEW' if self.findings else 'CLEAR_FOR_MANUAL_START',
                'findings': dict(sorted(self.findings.items())),
                'checked': dict(sorted(self.checked.items())),
                'automatic_restart': False, 'replay_allowed': False,
                'scope': 'local v2 journals only; no provider/device/cloud certification'}


def review_recovery(root, *, environ=None, limit=MAX_ENTRIES):
    """A clear local review is advisory, never a payment/print recovery grant."""
    env = os.environ if environ is None else environ
    review = RecoveryReview(limit=limit)
    try:
        root = checked_path(root)
        review.mock(root / 'data' / 'kiosk-v2-p4' / 'demo-attempts.sqlite3')
        review.photos(root / 'data' / 'kiosk-v2-p3' / 'photos')
        storage = checked_path(env.get('PHOTOBOOTH_V2_STORAGE_ROOT', root / 'data' / 'Photobooth'))
        for booth in review.entries(storage):
            if re.fullmatch(r'PB[0-9]+', booth.name):
                review.photos(booth)
        sandbox = root / 'data' / 'kiosk-v2-sandbox'
        explicit = env.get('MEONG_QRIS_JOURNAL')
        explicit_path = checked_path(explicit) if explicit else None
        if explicit_path is not None:
            if not explicit_path.is_relative_to(checked_path(sandbox)):
                raise ValueError('Unsupported journal scope')
            if explicit_path.exists():
                review.sandbox(explicit_path)
        for merchant in review.entries(sandbox):
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', merchant.name):
                continue
            for booth in review.entries(merchant):
                if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', booth.name):
                    continue
                journal = checked_path(booth / 'visit.json')
                if journal != explicit_path and journal.exists():
                    review.sandbox(journal)
                elif not journal.exists() and checked_path(booth / 'orders.sqlite').exists():
                    review.findings['SANDBOX_JOURNAL_MISSING'] += 1
                review.photos(booth / 'photo-tests' / 'photos')
    except (OSError, ValueError, TypeError, sqlite3.Error):
        review.findings['LOCAL_STATE_UNREADABLE'] += 1
    return review.result()
