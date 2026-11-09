"""Ubuntu Secret Service vault candidate; no plaintext key-file fallback.

Routine construction/operations only read the existing unlocked app key. Explicit
operator provision() creates it once under a private runtime kernel lock. No
unlock/prompt, default-collection creation, overwrite or deletion is performed.
The platform selector and Sandbox backend accept this protector. Native merchant
admission and complete worker recovery remain separate guarded integration.
"""
from contextlib import contextmanager
import hmac
import itertools
import os
from pathlib import Path
import re
import stat
import sys
import time

from photobooth.booth_storage import checked_path
from photobooth.credential_vault import ProtectedCredential, VaultUnavailable, _bounded

APPLICATION = 'meong-photobooth'
DEFAULT_KEY_ID = 'postpay-v1'
_PREFIX = b'MSV1'


def _attributes(key_id):
    if type(key_id) is not str or re.fullmatch(r'[A-Za-z0-9_-]{1,64}', key_id) is None:
        raise VaultUnavailable('Original Ubuntu vault key identity is invalid')
    return {'application':APPLICATION, 'purpose':'credential-vault', 'version':'1', 'key_id':key_id}


def _runtime():
    if not sys.platform.startswith('linux'):
        raise VaultUnavailable('Ubuntu credential protection is unavailable')
    root = checked_path(os.environ.get('XDG_RUNTIME_DIR', '/run/user/'+str(os.getuid())))
    info = root.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise VaultUnavailable('Private Ubuntu runtime is unavailable')
    return root


class _BoundedBus:
    def __init__(self, connection):
        self.connection = connection
        self.deadline = time.monotonic()+2

    def send_and_get_reply(self, message):
        remaining = self.deadline-time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Ubuntu vault deadline elapsed')
        return self.connection.send_and_get_reply(message, timeout=remaining)


@contextmanager
def _collection():
    connection = None
    try:
        runtime = _runtime()
        address = os.environ.get('DBUS_SESSION_BUS_ADDRESS', '')
        expected = 'unix:path='+str(runtime/'bus')
        if address != expected and re.fullmatch(re.escape(expected)+r',guid=[a-fA-F0-9]{32}', address) is None:
            raise VaultUnavailable('Private Ubuntu session bus is unavailable')
        from jeepney.io.blocking import open_dbus_connection
        from secretstorage.collection import Collection
        from secretstorage.util import open_session
        connection = open_dbus_connection(address, auth_timeout=.5)
        bus = _BoundedBus(connection)
        session = open_session(bus)
        if session.encrypted is not True:
            raise VaultUnavailable('Encrypted Ubuntu vault session is unavailable')
        # Construct only the existing default collection; get_default_collection
        # can create/prompt, so it is deliberately not used here.
        collection = Collection(bus, session=session)
        if collection.is_locked():
            raise VaultUnavailable('Ubuntu vault is locked')
        yield collection
    except VaultUnavailable:
        raise
    except Exception:
        raise VaultUnavailable('Ubuntu credential protection is unavailable') from None
    finally:
        if connection is not None:
            connection.close()


def _items(collection, key_id):
    items = list(itertools.islice(collection.search_items(_attributes(key_id)), 2))
    if len(items) > 1:
        raise VaultUnavailable('Original Ubuntu vault key identity is ambiguous')
    return items


def _item_key(item, key_id):
    if item.is_locked() or item.get_attributes() != _attributes(key_id):
        raise VaultUnavailable('Original Ubuntu vault key is unavailable')
    key = item.get_secret()
    if type(key) is not bytes or len(key) != 32:
        raise VaultUnavailable('Original Ubuntu vault key is invalid')
    return key


def _read_key(key_id):
    with _collection() as collection:
        items = _items(collection, key_id)
        if not items:
            raise VaultUnavailable('Original Ubuntu vault key is missing')
        return _item_key(items[0], key_id)


@contextmanager
def _provision_lock():
    descriptor = None
    try:
        root = _runtime()/'meong-photobooth'
        root.mkdir(mode=0o700, exist_ok=True)
        checked_path(root)
        info = root.stat()
        if info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise VaultUnavailable('Private Ubuntu vault lock is unavailable')
        descriptor = os.open(root/'vault-provision.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        info = os.fstat(descriptor)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_mode & 0o077 or info.st_nlink != 1):
            raise VaultUnavailable('Private Ubuntu vault lock is unavailable')
        import fcntl
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    except VaultUnavailable:
        raise
    except Exception:
        raise VaultUnavailable('Ubuntu vault provisioning is unavailable') from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _create_without_prompt(collection, key_id, key):
    from secretstorage.util import format_secret
    if collection.is_locked() or collection.session.encrypted is not True:
        raise VaultUnavailable('Unlocked encrypted Ubuntu vault is required')
    attributes = _attributes(key_id)
    properties = {'org.freedesktop.Secret.Item.Label':('s', 'Meong PhotoBooth recovery vault'),
                  'org.freedesktop.Secret.Item.Attributes':('a{ss}', attributes)}
    # SecretStorage.create_item executes returned prompts automatically. Call the
    # same protocol/encryption primitives but refuse any prompt, never execute it.
    item_path, prompt = collection._collection.call('CreateItem', 'a{sv}(oayays)b',
        properties, format_secret(collection.session, key, 'application/octet-stream'), False)
    if not isinstance(item_path, str) or len(item_path) <= 1 or prompt != '/':
        raise VaultUnavailable('Noninteractive Ubuntu vault provisioning is unavailable')


class LinuxSecretServiceProtector:
    protector_id = 'linux-secret-service-aesgcm-v1'
    synthetic = False

    def __init__(self, key_id=DEFAULT_KEY_ID):
        _attributes(key_id)
        self.key_id = key_id
        self._key()  # No create, unlock, cache or synthetic fallback.

    def __repr__(self):
        return '<LinuxSecretServiceProtector: protected OS custody>'

    def _key(self):
        try:
            key = _read_key(self.key_id)
            if type(key) is not bytes or len(key) != 32:
                raise VaultUnavailable('Original Ubuntu vault key is invalid')
            return key
        except VaultUnavailable:
            raise
        except Exception:
            raise VaultUnavailable('Original Ubuntu vault key is unavailable') from None

    @classmethod
    def provision(cls, key_id=DEFAULT_KEY_ID, *, ledger=None):
        """First setup requires an original ledger with no customer credentials.

        Missing custody with any existing CCP/ticket must be repaired from its
        original OS key backup, never replaced by first-time provisioning.
        """
        _attributes(key_id)
        try:
            with _provision_lock(), _collection() as collection:
                items = _items(collection, key_id)
                if items:
                    _item_key(items[0], key_id)
                else:
                    from photobooth.post_preview_store import PostPreviewStore
                    if type(ledger) is not PostPreviewStore:
                        raise VaultUnavailable('Original empty credential ledger required for first setup')
                    with ledger.write():
                        if (ledger.db.execute('SELECT 1 FROM pp_ccp_credentials LIMIT 1').fetchone()
                                or ledger.db.execute('SELECT 1 FROM pp_ticket_credentials LIMIT 1').fetchone()):
                            raise VaultUnavailable('Restore original Ubuntu custody before provisioning')
                        key = os.urandom(32)
                        _create_without_prompt(collection, key_id, key)
                        items = _items(collection, key_id)
                        if len(items) != 1 or not hmac.compare_digest(key, _item_key(items[0], key_id)):
                            raise VaultUnavailable('Original Ubuntu vault key could not be verified')
            return cls(key_id)
        except VaultUnavailable:
            raise
        except Exception:
            raise VaultUnavailable('Ubuntu vault provisioning is unavailable') from None

    def _header(self):
        return _PREFIX+self.key_id.encode('ascii').ljust(64, b'\0')

    def protect(self, plaintext, scope):
        _bounded(plaintext, scope, maximum=8192)
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        header, nonce = self._header(), os.urandom(12)
        ciphertext = AESGCM(self._key()).encrypt(nonce, plaintext, b'Meong/LinuxVault/v1\0'+header+scope)
        return ProtectedCredential(self.protector_id, header+nonce+ciphertext)

    def unprotect(self, envelope, scope):
        if type(envelope) is not ProtectedCredential or envelope.protector_id != self.protector_id:
            raise VaultUnavailable('Original Ubuntu credential protector is unavailable')
        _bounded(envelope.ciphertext, scope)
        header = self._header()
        if len(envelope.ciphertext) < 97 or envelope.ciphertext[:68] != header:
            raise VaultUnavailable('Original Ubuntu credential envelope is invalid')
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        try:
            return AESGCM(self._key()).decrypt(envelope.ciphertext[68:80], envelope.ciphertext[80:],
                                             b'Meong/LinuxVault/v1\0'+header+scope)
        except VaultUnavailable:
            raise
        except Exception:
            raise VaultUnavailable('Original credential authentication failed') from None
