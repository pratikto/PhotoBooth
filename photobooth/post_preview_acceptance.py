"""Passive owned-Windows acceptance checks and redacted OWNER reports only.

No camera/backend/provider/printer/Drive call, key provisioning, enrollment,
customer journal mutation, money/media/ACK/recovery or commercial authority.
Runtime work stays in the original explicitly consented Sandbox launcher.
"""
from datetime import datetime, timezone
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys
import uuid

from photobooth.kiosk_v2.recovery import checked_path, LaunchLease

BRANCH = 'feature/post-preview-qris-checkout'
CASES = {
    'WN02': 'Original startup and actual camera',
    'WN03': 'Capture, per-design retake and all previews',
    'WN04': 'Original private CCP before QRIS',
    'WN05': 'Official Sandbox simulator and independent PAID',
    'WN06': 'Same Recovery Ticket screen opportunity and one receipt',
    'WN07': 'Verified original Drive link on owner phone',
    'WN08': 'Original designs/copies and actual paper',
    'WN09': 'Automatic result return and privacy wipe',
    'WN10': 'Next customer isolation and proof-gated return',
    'WN11': 'Normal shutdown and same-root restart without replay',
}
CHECKS = ('windows', 'python_3_12', 'source', 'dependencies', 'isolated_profile',
          'original_configuration_history', 'current_account_dpapi')
BLOCKED_SCOPES = ['INTERRUPTED_BOOT_RECOVERY', 'UNCERTAIN_OUTPUT_REMEDY',
                  'REFUND_QUALIFICATION', 'FULL_COMMERCIAL_ACCEPTANCE']
RESULTS = ('PASS', 'FAIL', 'BLOCKED')
_FAILURE = 'Acceptance check held; no original customer state was changed'


class AcceptanceHeld(RuntimeError):
    """Static allowlisted failure; never echo private data/arguments."""


def _require(value):
    if not value: raise AcceptanceHeld(_FAILURE)


def _hex(value, size):
    return type(value) is str and re.fullmatch(r'[a-f0-9]{%d}' % size, value) is not None


def _raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _utc(): return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _source(root):
    def git(*args):
        value = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                               text=True, timeout=8, check=False)
        _require(value.returncode == 0)
        return value.stdout.strip()
    try:
        revision = git('rev-parse', 'HEAD')
        changed = git('diff', '--name-only', 'HEAD', '--').splitlines()
        clean = not any(not (name.startswith('docs/') or name.lower().endswith('.md'))
                        for name in changed)
        _require(_hex(revision, 40) and git('branch', '--show-current') == BRANCH)
        return revision, clean
    except Exception:
        return 'UNAVAILABLE', False


def _windows_host(): return os.name == 'nt'


def _dependencies():
    # Reuse the original interpreter checklist without importing native modules.
    from tools.check_post_preview_pilot import IMPORTS
    try: return all(importlib.util.find_spec(name) is not None for name in (*IMPORTS, 'uvicorn', 'escpos'))
    except Exception: return False


def _isolated():
    from tools.check_post_preview_pilot import CONFLICTING_PROFILES
    return not any(os.environ.get(name) == '1' for name in CONFLICTING_PROFILES)


def _dpapi_self_test():
    try:
        from photobooth.credential_vault import WindowsDPAPIProtector
        protector = WindowsDPAPIProtector()
        nonce = secrets.token_bytes(32)  # NOT a worker/customer key; memory only.
        entropy = b'MEONG_OWNED_ACCEPTANCE_NONCREDENTIAL_SELFTEST_V1'
        protected = protector.protect(nonce, entropy)
        return hmac.compare_digest(nonce, protector.unprotect(protected, entropy))
    except Exception:
        return False


def _scope(settings):
    config = settings.config
    return hashlib.sha256(_raw(dict(storage=str(config.storage_root),
        merchant=config.merchant_id, booth=config.booth_id, mode='sandbox'))).hexdigest()


def preflight(root, storage_root, booth):
    """LOCAL prerequisites only; never certify hardware/account/boot recovery."""
    revision, clean = _source(root)
    checks = dict.fromkeys(CHECKS, 'NOT_CHECKED')
    values = (_windows_host(), sys.version_info[:2] == (3,12),
              revision != 'UNAVAILABLE' and clean, _dependencies(), _isolated())
    for name, passed in zip(CHECKS, values): checks[name] = 'PASS' if passed else 'BLOCKED'
    report = dict(version=1, kind='OWNED_WINDOWS_SANDBOX_ACCEPTANCE',
        session_id=uuid.uuid4().hex, created_utc=_utc(), source_sha=revision,
        source_clean=clean, checks=checks, local_scope=None, status='BLOCKED',
        owner_cases=dict.fromkeys(CASES, 'NOT_RUN'), blocked_scopes=list(BLOCKED_SCOPES),
        commercial_ready=False)
    if not all(value == 'PASS' for value in checks.values() if value != 'NOT_CHECKED'):
        return report
    owner = None
    try:
        from photobooth.post_preview_launch import ProtectedSandboxLaunch
        from photobooth.post_preview_launch_settings import load_settings
        owner = ProtectedSandboxLaunch(root)
        settings = load_settings(owner, storage_root=storage_root, booth_id=booth)
        checks['original_configuration_history'] = 'PASS'
        report['local_scope'] = _scope(settings)
        checks['current_account_dpapi'] = 'PASS' if _dpapi_self_test() else 'BLOCKED'
    except Exception:
        checks['original_configuration_history'] = 'BLOCKED'
    finally:
        if owner is not None:
            if not owner.stop(timeout=0): checks['original_configuration_history'] = 'BLOCKED'
    if all(value == 'PASS' for value in checks.values()):
        report['status'] = 'LOCAL_PREREQUISITES_PASS'
    return report


def _unique(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result); result[key] = value
    return result


def _read(path):
    # Stdlib-only: blocked dependency checks must still produce safe reports.
    path = checked_path(path); before = path.lstat()
    _require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 < before.st_size <= 16384)
    descriptor = os.open(path, os.O_RDONLY | getattr(os,'O_NOFOLLOW',0)
                         | getattr(os,'O_NONBLOCK',0) | getattr(os,'O_BINARY',0))
    try:
        actual = os.fstat(descriptor)
        _require(stat.S_ISREG(actual.st_mode) and actual.st_nlink == 1
                 and (before.st_dev,before.st_ino) == (actual.st_dev,actual.st_ino))
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None; raw = stream.read(16385)
    finally:
        if descriptor is not None: os.close(descriptor)
    _require(len(raw) <= 16384)
    value = json.loads(raw, object_pairs_hook=_unique)
    _require(type(value) is dict and _raw(value) == raw)
    return value


def _write(path, value):
    path = checked_path(path); checked_path(path.parent).mkdir(parents=True, exist_ok=True)
    raw = _raw(value); _require(len(raw) <= 16384)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os,'O_NOFOLLOW',0), 0o600)
    with os.fdopen(descriptor,'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def _folder(root, session):
    _require(_hex(session,32))
    return checked_path(Path(root)/'data'/'post-preview-acceptance'/session)


def _manifest(value):
    _require(set(value) == {'version','kind','session_id','created_utc','source_sha','source_clean',
        'checks','local_scope','status','owner_cases','blocked_scopes','commercial_ready'})
    _require(type(value['version']) is int and value['version']==1
        and value['kind']=='OWNED_WINDOWS_SANDBOX_ACCEPTANCE' and _hex(value['session_id'],32)
        and (value['source_sha']=='UNAVAILABLE' or _hex(value['source_sha'],40))
        and type(value['source_clean']) is bool and value['commercial_ready'] is False)
    _require(type(value['created_utc']) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',value['created_utc']))
    _require(type(value['checks']) is dict and set(value['checks'])==set(CHECKS)
        and all(type(s) is str and s in ('PASS','BLOCKED','NOT_CHECKED') for s in value['checks'].values()))
    _require(value['local_scope'] is None or _hex(value['local_scope'],64))
    _require(value['owner_cases']==dict.fromkeys(CASES,'NOT_RUN') and value['blocked_scopes']==BLOCKED_SCOPES)
    ready = (all(s=='PASS' for s in value['checks'].values()) and value['source_clean']
             and _hex(value['source_sha'],40) and _hex(value['local_scope'],64))
    _require(value['status']==('LOCAL_PREREQUISITES_PASS' if ready else 'BLOCKED'))
    return value


def save_session(root, report):
    try:
        _manifest(report)
        _write(_folder(root, report['session_id'])/'session.json', report)
        return report['session_id']
    except Exception: raise AcceptanceHeld(_FAILURE) from None


def load_session(root, session):
    try:
        value = _manifest(_read(_folder(root,session)/'session.json'))
        _require(value['session_id']==session)
        return value
    except Exception: raise AcceptanceHeld(_FAILURE) from None


def validate_for_run(root, storage_root, booth, session):
    try:
        original = load_session(root,session)
        current = preflight(root,storage_root,booth)
        _require(original['status']==current['status']=='LOCAL_PREREQUISITES_PASS'
                 and original['source_sha']==current['source_sha']
                 and original['local_scope']==current['local_scope'])
        return True
    except Exception: raise AcceptanceHeld(_FAILURE) from None


def validate_runtime_session(owner, settings, session):
    """Recheck under SAME original pre-start owner, without nesting its lock."""
    try:
        from photobooth.post_preview_launch import ProtectedSandboxLaunch
        from photobooth.post_preview_launch_settings import ProtectedLaunchSettings
        _require(type(owner) is ProtectedSandboxLaunch and not owner._started
                 and not owner._closed and not owner._stopping and not owner._global.stream.closed
                 and type(settings) is ProtectedLaunchSettings)
        report = load_session(owner.project_root,session)
        revision,clean = _source(owner.project_root)
        _require(_windows_host() and _isolated() and clean and _dpapi_self_test()
                 and report['status']=='LOCAL_PREREQUISITES_PASS'
                 and report['source_sha']==revision and report['local_scope']==_scope(settings))
    except Exception: raise AcceptanceHeld(_FAILURE) from None


def _observations(root, session):
    folder = checked_path(_folder(root,session)/'events')
    rows = []
    if folder.exists():
        for path in folder.iterdir():
            _require(len(rows)<512 and re.fullmatch(r'[0-9]{4}-[a-f0-9]{32}\.json',path.name))
            value = _read(path)
            _require(set(value)=={'version','kind','session_id','sequence','case_id','result','created_utc','source_sha'})
            _require(type(value['version']) is int and value['version']==1
                and value['kind']=='OWNER_REPORTED' and value['session_id']==session
                and type(value['sequence']) is int and 1<=value['sequence']<=512
                and value['case_id'] in CASES and value['result'] in RESULTS
                and _hex(value['source_sha'],40) and type(value['created_utc']) is str
                and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',value['created_utc']))
            _require(path.name.startswith('%04d-'%value['sequence']))
            rows.append(value)
    rows.sort(key=lambda value:value['sequence'])
    _require([v['sequence'] for v in rows]==list(range(1,len(rows)+1)))
    return rows


def record_result(root, session, case, result):
    try:
        _require(case in CASES and result in RESULTS)
        load_session(root,session)  # Unknown IDs cannot create report directories.
        with LaunchLease(_folder(root,session)):
            report = load_session(root,session); source,clean = _source(root)
            _require(report['status']=='LOCAL_PREREQUISITES_PASS' and clean and source==report['source_sha'])
            rows = _observations(root,session); _require(len(rows)<512)
            _require(all(row['source_sha']==source for row in rows))
            value = dict(version=1,kind='OWNER_REPORTED',session_id=session,sequence=len(rows)+1,
                         case_id=case,result=result,created_utc=_utc(),source_sha=source)
            _write(_folder(root,session)/'events'/('%04d-%s.json'%(value['sequence'],uuid.uuid4().hex)),value)
    except Exception: raise AcceptanceHeld(_FAILURE) from None


def summary(root, session):
    try:
        report = load_session(root,session); rows = _observations(root,session)
        cases = dict(report['owner_cases'])
        for row in rows:
            _require(row['source_sha']==report['source_sha']); cases[row['case_id']] = row['result']
        current,clean = _source(root)
        matches = clean and current==report['source_sha']
        return dict(report, owner_cases=cases, observation_count=len(rows),
                    evidence_origin='OWNER_REPORTED_NOT_INDEPENDENTLY_VERIFIED',
                    source_matches_current=matches,
                    normal_flow=('SOURCE_CHANGED_RETEST_NEEDED' if not matches else
                                 ('PASS_OWNER_REPORTED' if all(s=='PASS' for s in cases.values())
                                  else 'INCOMPLETE_OR_FAILED')),commercial_ready=False)
    except Exception: raise AcceptanceHeld(_FAILURE) from None
