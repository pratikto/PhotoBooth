"""Explicit fresh-booth enrollment, not replacement history or boot authority.

No camera/provider/custody I/O. All metadata is non-secret, exclusive and bound
to the original global owner/account/root. Partial unknown writes stay held.
"""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import uuid

from photobooth.kiosk_v2.recovery import checked_path,review_recovery
from photobooth.post_preview_launch import ProtectedSandboxLaunch,ProtectedLaunchHeld


def _active(owner):
    if (type(owner) is not ProtectedSandboxLaunch or owner._closed or owner._stopping
            or owner._started or owner._global.stream.closed):
        raise ProtectedLaunchHeld('Original active setup owner required')


def _raw(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode('utf-8')


def _read(path):
    def unique(pairs):
        value={}
        for key,item in pairs:
            if key in value:raise ValueError
            value[key]=item
        return value
    with checked_path(path).open('rb') as stream:raw=stream.read(8193)
    if len(raw)>8192:raise ValueError
    value=json.loads(raw,object_pairs_hook=unique)
    if type(value) is not dict:raise ValueError
    return value


def _sync(parent):
    from photobooth.capture_journal import sync_directory
    sync_directory(parent)


def _exclusive_json(path,value):
    path=checked_path(path)
    descriptor=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(descriptor,'wb') as stream:
        stream.write(_raw(value));stream.flush();os.fsync(stream.fileno())
    _sync(path.parent)


def _context(owner,settings):
    from photobooth.post_preview_store import ORDER_VERSION
    return dict(version=1,kind='NEW_BOOTH',mode='sandbox',order_version=ORDER_VERSION,
                project_root=str(owner.project_root),storage_root=str(settings.config.storage_root),
                merchant_id=settings.config.merchant_id,booth_id=settings.config.booth_id)


def _paths(owner):
    folder=checked_path(owner.project_root/'data'/'post-preview-enrollment')
    return folder,checked_path(folder/'intent.json'),checked_path(folder/'enrolled.json'),checked_path(folder/'legacy-baseline.sqlite3')


def _no_legacy(owner,settings):
    # Direct known roots ONLY. No archive traversal, photos, arbitrary filesystem
    # discovery, or convenient substitute ledger. Even partial roots hold.
    roots=('data/kiosk-v2-sandbox','data/qris-sandbox-trial','data/qris-sandbox.sqlite',
           'data/qris-mock.sqlite','data/kiosk-v2-p3','data/Photobooth')
    if any(checked_path(owner.project_root/relative).exists() for relative in roots):raise ValueError
    for relative in ('data/qris-sandbox.sqlite','data/qris-mock.sqlite'):
        if any(checked_path(str(owner.project_root/relative)+suffix).exists() for suffix in ('-wal','-shm')):raise ValueError
    for name in ('PHOTOBOOTH_V2_STORAGE_ROOT','MEONG_QRIS_DB_PATH','MEONG_QRIS_JOURNAL'):
        value=os.environ.get(name)
        if value:
            path=checked_path(owner.project_root/Path(value))
            if any(checked_path(str(path)+suffix).exists() for suffix in ('','-wal','-shm')):raise ValueError
    if checked_path(settings.config.storage_root/'Photobooth').exists():raise ValueError
    if review_recovery(owner.project_root)['status']!='CLEAR_FOR_MANUAL_START':raise ValueError


def _intent(owner,settings,path):
    value=_read(path);expected=_context(owner,settings)
    if (set(value)!=set(expected)|{'enrollment_id','state'} or value.get('state')!='PREPARED'
            or type(value.get('version')) is not int
            or any(value.get(k)!=v for k,v in expected.items())
            or type(value.get('enrollment_id')) is not str
            or re.fullmatch(r'[a-f0-9]{32}',value['enrollment_id']) is None):raise ValueError
    return value


def _baseline(path,intent):
    for suffix in ('-wal','-shm'):checked_path(str(path)+suffix)
    with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=.2)) as db:
        row=db.execute('SELECT context_json FROM pp_launch_enrollment WHERE singleton=1').fetchone()
        if (not row or row[0]!=_raw(intent).decode('utf-8')
                or db.execute('SELECT COUNT(*) FROM pp_launch_enrollment').fetchone()[0]!=1):raise ValueError
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError
        tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        # Baseline is never a customer ledger. Any old/new row is a hold, even
        # if a caller tries to mark its payment terminal or fulfilled.
        for table in tables:
            if table=='pp_launch_enrollment':continue
            quoted='"'+table.replace('"','""')+'"'
            if db.execute('SELECT 1 FROM '+quoted+' LIMIT 1').fetchone():raise ValueError
        db.execute('SELECT id,booth_id,checkout_key,state FROM checkouts LIMIT 0')


def _completion(intent):
    return dict(version=1,kind='ENROLLED_NEW_BOOTH',enrollment_id=intent['enrollment_id'],
                intent_sha256=hashlib.sha256(_raw(intent)).hexdigest())


def enrolled_history(owner,settings):
    """Read-only new-install baseline selection; never grant booth/media access."""
    _active(owner)
    try:
        _no_legacy(owner,settings)
        folder,intent_path,complete_path,baseline=_paths(owner)
        intent=_intent(owner,settings,intent_path)
        complete=_read(complete_path)
        if type(complete.get('version')) is not int or complete!=_completion(intent):raise ValueError
        _baseline(baseline,intent)
        return baseline
    except Exception:
        raise ProtectedLaunchHeld('Original enrollment/history held; preserve the original setup') from None


def enroll_new_booth(owner,*,storage_root,booth_id):
    """Explicit local operation only; normal launch/check-only never call this."""
    _active(owner)
    try:
        from photobooth.post_preview_launch_settings import _configuration,ProtectedLaunchSettings
        from photobooth.checkout_store import CheckoutStore
        settings=_configuration(owner,storage_root=storage_root,booth_id=booth_id)
        _no_legacy(owner,settings)
        folder,intent_path,complete_path,baseline=_paths(owner)
        if complete_path.exists():
            return ProtectedLaunchSettings(settings.config,settings.printer_config,enrolled_history(owner,settings))
        # Before first completion, any protected namespace belongs to an older
        # or unknown installation. Never relabel it as a new empty booth.
        if checked_path(settings.config.storage_root/'post-preview-sandbox').exists():raise ValueError
        if folder.exists():
            intent=_intent(owner,settings,intent_path)
        else:
            intent=dict(_context(owner,settings),enrollment_id=uuid.uuid4().hex,state='PREPARED')
            folder.mkdir(mode=0o700)
            _exclusive_json(intent_path,intent)
        if not baseline.exists():
            # Reserve the exact new baseline, then persist identity BEFORE the
            # original additive schema. An interrupted unbound file stays held.
            descriptor=os.open(baseline,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(descriptor)
            with closing(sqlite3.connect(baseline)) as db:
                db.execute('PRAGMA synchronous=FULL')
                with db:
                    db.execute('CREATE TABLE pp_launch_enrollment(singleton INTEGER PRIMARY KEY CHECK(singleton=1),context_json TEXT NOT NULL)')
                    db.execute('INSERT INTO pp_launch_enrollment VALUES (1,?)',(_raw(intent).decode('utf-8'),))
            _sync(folder)
            with closing(CheckoutStore(baseline)):pass  # Original engine/schema, no invented legacy order/journal.
        _baseline(baseline,intent)
        _no_legacy(owner,settings)  # Recheck absence AFTER local DB I/O.
        _exclusive_json(complete_path,_completion(intent))
        return ProtectedLaunchSettings(settings.config,settings.printer_config,baseline)
    except Exception:
        raise ProtectedLaunchHeld('New-booth enrollment held; preserve original history and setup') from None
