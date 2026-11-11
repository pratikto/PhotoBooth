"""Original native worker retirement receipts; never finance or FREE authority.

Only a trusted launcher shares an ephemeral capability with the original native
coordinator and backend. HTTP callers cannot provide this key or worker flags.
Original journals retain the authenticated receipt; the key is never persisted.
"""
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import uuid

from photobooth.post_preview_readiness import finite_number
from photobooth.post_preview_store import DraftHeld, PostPreviewStore


def _hex(value, size):
    return type(value) is str and re.fullmatch('[a-f0-9]{%d}' % size, value) is not None


def canonical(frame):
    return json.dumps(frame, sort_keys=True, separators=(',', ':'), allow_nan=False)


@dataclass(frozen=True)
class WorkerFenceKey:
    key_id: str
    secret: bytes = field(repr=False)

    def __post_init__(self):
        if not _hex(self.key_id, 32) or type(self.secret) is not bytes or len(self.secret) != 32:
            raise ValueError('Private original worker capability required')

    @classmethod
    def create(cls):
        return cls(uuid.uuid4().hex, os.urandom(32))

    def sign(self, frame):
        return hmac.new(self.secret, canonical(frame).encode(), hashlib.sha256).hexdigest()


def install_worker_receipts(ledger):
    """Explicit trusted backend setup; no replacement of original operations."""
    if type(ledger) is not PostPreviewStore:
        raise DraftHeld('Original worker receipt ledger required')
    with ledger.write():
        ledger.db.execute('''CREATE TABLE IF NOT EXISTS pp_worker_retirements (
            operation_id TEXT NOT NULL REFERENCES pp_isolation_ops(operation_id),
            key_id TEXT NOT NULL CHECK(length(key_id)=32),
            frame_json TEXT NOT NULL CHECK(length(frame_json) BETWEEN 1 AND 2048),
            mac TEXT NOT NULL CHECK(length(mac)=64),
            backend_verified_at REAL,
            PRIMARY KEY(operation_id,key_id))''')
        columns=[(r['name'],r['type'],r['notnull'],r['pk'])
                 for r in ledger.db.execute('PRAGMA table_info(pp_worker_retirements)')]
        expected=[('operation_id','TEXT',1,1),('key_id','TEXT',1,2),
                  ('frame_json','TEXT',1,0),('mac','TEXT',1,0),('backend_verified_at','REAL',0,0)]
        links=[(r['table'],r['from'],r['to'])
               for r in ledger.db.execute('PRAGMA foreign_key_list(pp_worker_retirements)')]
        if columns != expected or links != [('pp_isolation_ops','operation_id','operation_id')]:
            raise DraftHeld('Original worker receipt schema requires review')
        ledger.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_worker_receipt_immutable
            BEFORE UPDATE OF operation_id,key_id,frame_json,mac ON pp_worker_retirements
            BEGIN SELECT RAISE(ABORT,'Original worker receipt is immutable'); END''')
        ledger.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_worker_receipt_no_delete
            BEFORE DELETE ON pp_worker_retirements
            BEGIN SELECT RAISE(ABORT,'Original worker receipt must be preserved'); END''')
        ledger.db.execute('''CREATE TRIGGER IF NOT EXISTS pp_worker_receipt_verify_once
            BEFORE UPDATE OF backend_verified_at ON pp_worker_retirements
            WHEN OLD.backend_verified_at IS NOT NULL OR NEW.backend_verified_at IS NULL
                 OR NEW.backend_verified_at<=0
            BEGIN SELECT RAISE(ABORT,'Original worker acknowledgement cannot be replaced'); END''')


def _original(ledger, operation_id):
    return _original_from_db(ledger.db, operation_id)


def _original_from_db(db, operation_id):
    if not _hex(operation_id, 32):
        raise DraftHeld('Exact original isolation operation required')
    row=db.execute('''SELECT o.*,d.visit_id,d.generation,d.lifecycle,d.closed,
        i.purchase_group_id,i.contract_sha256 FROM pp_isolation_ops o
        JOIN pp_drafts d USING(draft_id) LEFT JOIN pp_checkout_intents i USING(draft_id)
        WHERE o.operation_id=?''',(operation_id,)).fetchone()
    if not row:
        raise DraftHeld('Original PREPARED operation required')
    return row


def _frame(row, key_id, stamp):
    return dict(version=1, kind='ORIGINAL_WORKER_RETIRED',key_id=key_id,
        operation_id=row['operation_id'],draft_id=row['draft_id'],booth_id=row['booth_id'],
        visit_id=row['visit_id'],generation=row['original_generation'],
        purchase_group_id=row['purchase_group_id'],contract_sha256=row['contract_sha256'],
        observed_at=stamp)


class WorkerReceiptVerifier:
    def __init__(self, ledger, key):
        if type(ledger) is not PostPreviewStore or type(key) is not WorkerFenceKey:
            raise DraftHeld('Exact backend worker receipt authority required')
        self.ledger, self.key = ledger, key

    def verify(self, operation_id):
        """Call inside backend ACK transaction; never creates/ACKs an operation."""
        return verify_worker_receipt_from_db(self.ledger.db,self.key,operation_id,now=self.ledger.now())


def verify_worker_receipt_from_db(db, key, operation_id, *, now):
    """SAME original read verifier for an already-owned read-only snapshot."""
    if type(key) is not WorkerFenceKey or not finite_number(now):
        raise DraftHeld('Exact backend worker receipt authority required')
    row=_original_from_db(db,operation_id)
    receipt=db.execute('SELECT * FROM pp_worker_retirements '
        'WHERE operation_id=? AND key_id=?',(operation_id,key.key_id)).fetchone()
    if receipt is None:
        raise DraftHeld('Original native worker has not retired')
    try:
        frame=json.loads(receipt['frame_json'])
        stamp=frame['observed_at']
        if (type(frame) is not dict or type(frame.get('version')) is not int
                or type(frame.get('generation')) is not int
                or type(row['original_generation']) is not int or row['original_generation']<2
                or not finite_number(row['prepared_at'])
                or not finite_number(stamp) or not row['prepared_at']<=stamp<=now
                or canonical(frame)!=receipt['frame_json']
                or frame!=_frame(row,key.key_id,stamp)
                or not _hex(receipt['mac'],64)
                or not hmac.compare_digest(receipt['mac'],key.sign(frame))):
            raise ValueError('Original worker receipt changed')
    except (ValueError, TypeError, KeyError, RecursionError):
        raise DraftHeld('Original worker receipt cannot be verified') from None
    return dict(receipt)


class NativeWorkerRetirement:
    """Exact original local workers, outside the PhotoJobs worker/UI callbacks."""
    def __init__(self, jobs, readiness, launcher, key):
        from photobooth.kiosk_v2.photos import PhotoJobs
        from photobooth.kiosk_v2.post_preview_protected_checkout import ProtectedCheckoutService
        from photobooth.kiosk_v2.recovery import LaunchLease
        from photobooth.post_preview_readiness_bridge import WorkerReadinessServer
        from photobooth.post_preview_readiness import LocalChargeReadiness
        from photobooth.post_preview_authority import OriginalWorkerReadiness
        if (type(jobs) is not PhotoJobs or type(jobs.service) is not ProtectedCheckoutService
                or type(readiness) is not WorkerReadinessServer or type(launcher) is not LaunchLease
                or type(key) is not WorkerFenceKey):
            raise DraftHeld('Original protected native worker bindings required')
        service=jobs.service
        collector=readiness._original_collector
        authority=collector.probes.get('worker_ownership') if type(collector) is LocalChargeReadiness else None
        if (type(authority) is not OriginalWorkerReadiness or authority.service is not service
                or authority.jobs is not jobs or authority.launch_lease is not launcher
                or collector.checkout is not service.checkout):
            raise DraftHeld('Exact original bound readiness collector required')
        self.jobs,self.service,self.readiness,self.launcher,self.key=jobs,service,readiness,launcher,key
        self.ledger=service.ledger

    def _scope(self, row):
        lease=self.service.lease
        stream=self.launcher.stream
        if (self.jobs.service is not self.service or self.service.ledger is not self.ledger
                or stream.closed
                or Path(stream.name).resolve() != (self.service.root/'data'/'kiosk-v2-launch.lock').resolve()
                or lease is None or lease.booth_id!=row['booth_id'] or lease.visit_id!=row['visit_id']
                or lease.draft_id!=row['draft_id'] or lease.generation+1!=row['original_generation']
                or row['lifecycle']=='ACTIVE' or not self.service._hidden.is_set()
                or self.service._closed.is_set()):
            raise DraftHeld('Original private worker retirement scope changed')

    def publish(self, operation_id, *, timeout=0):
        """No receipt until actual collector and file worker threads are gone."""
        if not finite_number(timeout) or not 0<=timeout<=5:
            raise ValueError('Bounded original worker retirement required')
        with self.ledger.write():
            row=_original(self.ledger,operation_id)
            self._scope(row)
            if row['state']!='PREPARED' or row['closed'] or row['generation']!=row['original_generation']:
                raise DraftHeld('Original worker PREPARED generation required')
        # Never hold SQLite while joining a collector/file callback that may
        # itself be finishing original journal I/O.
        if not self.readiness.stop(timeout=timeout):
            raise DraftHeld('Original readiness collector is still active')
        if not self.jobs.retire(timeout=timeout):
            raise DraftHeld('Original photo/file worker is still active')
        with self.ledger.write():
            current=_original(self.ledger,operation_id)
            self._scope(current)
            if (current['state']!='PREPARED' or current['closed']
                    or current['generation']!=row['original_generation']):
                raise DraftHeld('Original worker retirement operation changed')
            existing=self.ledger.db.execute('SELECT 1 FROM pp_worker_retirements '
                'WHERE operation_id=? AND key_id=?',(operation_id,self.key.key_id)).fetchone()
            if existing:
                WorkerReceiptVerifier(self.ledger,self.key).verify(operation_id)
                return operation_id
            stamp=self.ledger.now()
            if not finite_number(stamp) or stamp<current['prepared_at']:
                raise DraftHeld('Original worker retirement clock is invalid')
            frame=_frame(current,self.key.key_id,stamp)
            self.ledger.db.execute('INSERT INTO pp_worker_retirements '
                '(operation_id,key_id,frame_json,mac) VALUES(?,?,?,?)',
                (operation_id,self.key.key_id,canonical(frame),self.key.sign(frame)))
            return operation_id
