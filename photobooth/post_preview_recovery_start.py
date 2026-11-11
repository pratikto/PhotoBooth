"""Actual NEW recovery-process provenance; never old retirement/ACK authority."""
import hashlib
import hmac
import json
import os
import re
import subprocess

from photobooth.capture_journal import sync_directory
from photobooth.kiosk_v2.recovery import checked_path
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_process_identity import OriginalProcessIdentity,observe_process,original_process_exited
from photobooth.post_preview_store import DraftHeld,ORDER_VERSION
from photobooth.post_preview_worker_escrow import _root,_regular_file,_unique,read_worker_escrow
from photobooth.post_preview_worker_custody import restore_worker_key
from photobooth.post_preview_worker_fence import WorkerFenceKey,canonical

_HELD='Original recovery process provenance is held'


def _require(value):
    if not value: raise DraftHeld(_HELD)


def _hex(value):
    _require(type(value) is str and re.fullmatch(r'[a-f0-9]{32}',value) is not None)
    return value


def _path(config,nonce,*,intent=False):
    suffix='.intent.json' if intent else '.json'
    return checked_path(config.private_root/'worker-recoveries'/(_hex(nonce)+suffix))


def _read_record(config,key,nonce,*,intent=False):
    try:
        _require(type(config) is SandboxHostConfig and type(key) is WorkerFenceKey)
        with _regular_file(_path(config,nonce,intent=intent),'rb') as stream: raw=stream.read(8193)
        _require(len(raw)<=8192)
        value=json.loads(raw,object_pairs_hook=_unique)
        _require(type(value) is dict and set(value)=={'frame','mac'})
        frame=value['frame']
        expected=dict(version=1,kind='ORIGINAL_RECOVERY_INTENT' if intent else 'ORIGINAL_RECOVERY_PROCESS_START',mode='sandbox',
            order_version=ORDER_VERSION,private_root=str(config.private_root),merchant_id=config.merchant_id,
            booth_id=config.booth_id,worker_epoch=key.key_id,nonce=nonce)
        extra={'operation_id','parent_pid','parent_birth','project_scope_sha256'}
        if not intent: extra|={'child_pid','child_birth'}
        _require(type(frame) is dict and set(frame)==set(expected)|extra)
        _require(type(frame['version']) is int and all(frame[k]==v for k,v in expected.items()))
        _hex(frame['operation_id'])
        OriginalProcessIdentity(frame['parent_pid'],frame['parent_birth'])
        if not intent:
            OriginalProcessIdentity(frame['child_pid'],frame['child_birth'])
            _require(frame['parent_pid']!=frame['child_pid'])
        _require(type(frame['project_scope_sha256']) is str
                 and re.fullmatch(r'[a-f0-9]{64}',frame['project_scope_sha256']) is not None
                 and type(value['mac']) is str and hmac.compare_digest(value['mac'],key.sign(frame))
                 and canonical(value).encode()==raw)
        return frame
    except Exception:
        raise DraftHeld(_HELD) from None


def read_recovery_intent(config,key,nonce):
    return _read_record(config,key,nonce,intent=True)


def read_recovery_start(config,key,nonce):
    try:
        intent=read_recovery_intent(config,key,nonce)
        frame=_read_record(config,key,nonce)
        _require(all(frame[name]==value for name,value in intent.items() if name!='kind'))
        return frame
    except Exception:
        raise DraftHeld(_HELD) from None


def record_recovery_intent(global_owner,config,key,operation,nonce):
    """Durable BEFORE Popen; an unmatched intent blocks later attempts."""
    try:
        project=_root(global_owner)
        _require(type(config) is SandboxHostConfig and type(key) is WorkerFenceKey)
        parent=observe_process(os.getpid())
        frame=dict(version=1,kind='ORIGINAL_RECOVERY_INTENT',mode='sandbox',order_version=ORDER_VERSION,
            private_root=str(config.private_root),merchant_id=config.merchant_id,booth_id=config.booth_id,
            worker_epoch=key.key_id,operation_id=_hex(operation),nonce=_hex(nonce),parent_pid=parent.pid,
            parent_birth=parent.birth,project_scope_sha256=hashlib.sha256(str(project).encode()).hexdigest())
        _persist_record(config,key,nonce,frame,intent=True)
        _require(_root(global_owner)==project and observe_process(os.getpid())==parent)
        return frame
    except Exception:
        raise DraftHeld(_HELD) from None


def _persist_record(config,key,nonce,frame,*,intent=False):
    raw=canonical(dict(frame=frame,mac=key.sign(frame))).encode(); _require(len(raw)<=8192)
    path=_path(config,nonce,intent=intent)
    if not path.exists():
        checked_path(path.parent).mkdir(mode=0o700,exist_ok=True)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
        with os.fdopen(fd,'wb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
    loaded=read_recovery_intent(config,key,nonce) if intent else read_recovery_start(config,key,nonce)
    _require(loaded==frame)
    with _regular_file(path,'r+b') as stream: os.fsync(stream.fileno())
    sync_directory(path.parent);sync_directory(config.private_root)


def record_recovery_start(global_owner,config,key,operation,nonce,child):
    """Observe live ORIGINAL Popen under retained global owner, BEFORE START."""
    try:
        project=_root(global_owner)
        _require(type(config) is SandboxHostConfig and type(key) is WorkerFenceKey
                 and type(child) is subprocess.Popen and child.poll() is None)
        parent=observe_process(os.getpid()); identity=observe_process(child.pid)
        frame=dict(version=1,kind='ORIGINAL_RECOVERY_PROCESS_START',mode='sandbox',order_version=ORDER_VERSION,
            private_root=str(config.private_root),merchant_id=config.merchant_id,booth_id=config.booth_id,
            worker_epoch=key.key_id,operation_id=_hex(operation),nonce=_hex(nonce),parent_pid=parent.pid,
            parent_birth=parent.birth,child_pid=identity.pid,child_birth=identity.birth,
            project_scope_sha256=hashlib.sha256(str(project).encode()).hexdigest())
        recorded=read_recovery_intent(config,key,nonce)
        _require(all(frame[name]==value for name,value in recorded.items() if name!='kind'))
        _persist_record(config,key,nonce,frame)
        _require(_root(global_owner)==project and child.poll() is None and observe_process(child.pid)==identity)
        return frame
    except Exception:
        raise DraftHeld(_HELD) from None


def review_recovery_processes(native_owner,config,*,current_nonce=None):
    """Prior role journals must authenticate and show actual child exit.

    Only the actual current child may exempt its exact private bootstrap nonce;
    its actual parent must match getppid and remain live. No flags from HTTP.
    """
    try:
        _require(_root(native_owner)==config.private_root)
        folder=checked_path(config.private_root/'worker-recoveries')
        if not folder.exists():
            _require(current_nonce is None); return
        intents=set();starts=set();found=False
        for path in folder.iterdir():
            match=re.fullmatch(r'([a-f0-9]{32})(\.intent)?\.json',path.name)
            _require(match is not None and len(intents)+len(starts)<20000)
            (intents if match[2] else starts).add(match[1])
        _require(intents==starts)
        for nonce in intents:
            with _regular_file(_path(config,nonce,intent=True),'rb') as stream: raw=stream.read(8193)
            _require(len(raw)<=8192)
            value=json.loads(raw,object_pairs_hook=_unique)
            epoch=_hex(value['frame']['worker_epoch'])
            stored=read_worker_escrow(native_owner,epoch)
            _require(stored.scope.merchant_id==config.merchant_id and stored.scope.booth_id==config.booth_id
                     and stored.envelope.key_id==epoch==stored.scope.worker_epoch)
            key=restore_worker_key(stored.envelope,stored.scope)
            frame=read_recovery_start(config,key,nonce)
            parent=OriginalProcessIdentity(frame['parent_pid'],frame['parent_birth'])
            child=OriginalProcessIdentity(frame['child_pid'],frame['child_birth'])
            if nonce==current_nonce:
                _require(child.pid==os.getpid() and parent.pid==os.getppid()
                         and observe_process(child.pid)==child and observe_process(parent.pid)==parent)
                found=True
            else:
                _require(original_process_exited(child))
                if parent.pid==os.getpid(): _require(observe_process(os.getpid())==parent)
                else: _require(original_process_exited(parent))
        _require(current_nonce is None or found)
    except Exception:
        raise DraftHeld(_HELD) from None
