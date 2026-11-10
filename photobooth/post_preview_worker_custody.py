"""Unmounted OS envelope for the ORIGINAL worker key, never release authority.

Scope authenticates claimed metadata only. It observes neither process birth nor
death, owns no kernel lease and grants no ACK, finance or customer-media access.
No files, replacement keys, vault provisioning or launcher changes occur here.
"""
import base64
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re

from photobooth.credential_vault import (ProtectedCredential, VaultUnavailable,
    WindowsDPAPIProtector, platform_protector)
from photobooth.linux_credential_vault import LinuxSecretServiceProtector
from photobooth.kiosk_v2.recovery import checked_path
from photobooth.post_preview_store import ORDER_VERSION
from photobooth.post_preview_worker_fence import WorkerFenceKey, canonical


_ROLE = 'ORIGINAL_WORKER_KEY'
_PROTECTORS = (WindowsDPAPIProtector, LinuxSecretServiceProtector)
_FAILURE = 'Original worker custody is unavailable'


def _require(condition):
    if not condition:
        raise VaultUnavailable(_FAILURE)


def _match(value, expression):
    return type(value) is str and re.fullmatch(expression, value) is not None


@dataclass(frozen=True)
class WorkerCustodyScope:
    private_root: Path = field(repr=False)
    merchant_id: str = field(repr=False)
    booth_id: str
    worker_epoch: str
    owner_pid: int
    process_birth: str

    def __post_init__(self):
        try:
            _require(isinstance(self.private_root, Path) and self.private_root.is_absolute())
            root = checked_path(self.private_root)
            _require(_match(self.merchant_id, r'[A-Za-z0-9_-]{1,64}')
                     and self.merchant_id.lower() != 'old')
            _require(_match(self.booth_id, r'PB[0-9]{3,8}'))
            _require(_match(self.worker_epoch, r'[a-f0-9]{32}'))
            _require(type(self.owner_pid) is int and 1 <= self.owner_pid <= 2**32-1)
            _require(_match(self.process_birth, r'[A-Za-z0-9:_-]{1,128}'))
            object.__setattr__(self, 'private_root', root)
            _require(len(self.entropy()) <= 2048)
        except Exception:
            raise VaultUnavailable(_FAILURE) from None

    def to_record(self):
        return dict(version=1, kind=_ROLE, mode='sandbox', order_version=ORDER_VERSION,
                    private_root=str(self.private_root), merchant_id=self.merchant_id,
                    booth_id=self.booth_id, worker_epoch=self.worker_epoch,
                    owner_pid=self.owner_pid, process_birth=self.process_birth)

    @classmethod
    def from_record(cls, value):
        keys = {'version', 'kind', 'mode', 'order_version', 'private_root',
                'merchant_id', 'booth_id', 'worker_epoch', 'owner_pid', 'process_birth'}
        try:
            _require(type(value) is dict and set(value) == keys)
            _require(type(value['version']) is int and value['version'] == 1
                     and value['kind'] == _ROLE and value['mode'] == 'sandbox'
                     and value['order_version'] == ORDER_VERSION)
            _require(type(value['private_root']) is str and len(value['private_root']) <= 2048)
            result = cls(Path(value['private_root']), value['merchant_id'], value['booth_id'],
                         value['worker_epoch'], value['owner_pid'], value['process_birth'])
            _require(result.to_record() == value)
            return result
        except Exception:
            raise VaultUnavailable(_FAILURE) from None

    def entropy(self):
        return canonical(self.to_record()).encode('utf-8')


@dataclass(frozen=True)
class ProtectedWorkerKey:
    key_id: str
    scope_sha256: str
    credential: ProtectedCredential = field(repr=False)

    def __post_init__(self):
        _require(_match(self.key_id, r'[a-f0-9]{32}')
                 and _match(self.scope_sha256, r'[a-f0-9]{64}'))
        _require(type(self.credential) is ProtectedCredential)
        _require(self.credential.protector_id in tuple(p.protector_id for p in _PROTECTORS))
        _require(type(self.credential.ciphertext) is bytes
                 and 1 <= len(self.credential.ciphertext) <= 65536)

    def to_record(self):
        return dict(version=1, kind=_ROLE, key_id=self.key_id,
                    scope_sha256=self.scope_sha256, protector_id=self.credential.protector_id,
                    ciphertext=base64.b64encode(self.credential.ciphertext).decode('ascii'))

    @classmethod
    def from_record(cls, value):
        try:
            _require(type(value) is dict and set(value) ==
                     {'version', 'kind', 'key_id', 'scope_sha256', 'protector_id', 'ciphertext'})
            _require(type(value['version']) is int and value['version'] == 1 and value['kind'] == _ROLE)
            encoded = value['ciphertext']
            _require(type(encoded) is str and 1 <= len(encoded) <= 87384)
            raw = base64.b64decode(encoded, validate=True)
            _require(base64.b64encode(raw).decode('ascii') == encoded)
            return cls(value['key_id'], value['scope_sha256'],
                       ProtectedCredential(value['protector_id'], raw))
        except Exception:
            raise VaultUnavailable(_FAILURE) from None


def _protector(value):
    result = platform_protector() if value is None else value
    _require(type(result) in _PROTECTORS)
    return result


def protect_worker_key(key, scope, *, protector=None):
    """Protect an existing capability only; never create a replacement."""
    try:
        _require(type(key) is WorkerFenceKey and type(scope) is WorkerCustodyScope)
        entropy = scope.entropy()
        digest = hashlib.sha256(entropy).hexdigest()
        payload = canonical(dict(version=1, kind=_ROLE, key_id=key.key_id,
                                 scope_sha256=digest, secret_hex=key.secret.hex())).encode('ascii')
        selected = _protector(protector)
        credential = selected.protect(payload, entropy)
        _require(credential.protector_id == selected.protector_id)
        return ProtectedWorkerKey(key.key_id, digest, credential)
    except Exception:
        raise VaultUnavailable(_FAILURE) from None


def _unique(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def restore_worker_key(envelope, scope, *, protector=None):
    """Restore the same capability; caller still has NO ownership/ACK proof."""
    try:
        _require(type(envelope) is ProtectedWorkerKey and type(scope) is WorkerCustodyScope)
        entropy = scope.entropy()
        _require(hashlib.sha256(entropy).hexdigest() == envelope.scope_sha256)
        selected = _protector(protector)
        _require(envelope.credential.protector_id == selected.protector_id)
        raw = selected.unprotect(envelope.credential, entropy)
        _require(type(raw) is bytes and 1 <= len(raw) <= 8192)
        payload = json.loads(raw, object_pairs_hook=_unique)
        _require(type(payload) is dict and set(payload) ==
                 {'version', 'kind', 'key_id', 'scope_sha256', 'secret_hex'})
        _require(type(payload['version']) is int and payload['version'] == 1
                 and payload['kind'] == _ROLE and payload['key_id'] == envelope.key_id
                 and payload['scope_sha256'] == envelope.scope_sha256
                 and _match(payload['secret_hex'], r'[a-f0-9]{64}'))
        _require(canonical(payload).encode('ascii') == raw)
        return WorkerFenceKey(envelope.key_id, bytes.fromhex(payload['secret_hex']))
    except Exception:
        raise VaultUnavailable(_FAILURE) from None
