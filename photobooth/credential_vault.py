"""OS-protected original credential ciphertext; no plaintext sidecar fallback.

Windows DPAPI is scoped to the current OS user with additional order entropy.
Unverified platforms fail closed. The explicitly synthetic AES-GCM adapter uses
an injected ephemeral test key and never claims OS/device protection.
"""
from dataclasses import dataclass, field
import os


class VaultUnavailable(RuntimeError):
    """Allowlisted failure; never include secret, ciphertext or OS error text."""


@dataclass(frozen=True)
class ProtectedCredential:
    protector_id: str
    ciphertext: bytes = field(repr=False)


def _bounded(value, scope, *, maximum=65536):
    if (not isinstance(value, bytes) or not 1 <= len(value) <= maximum
            or not isinstance(scope, bytes) or not 1 <= len(scope) <= 2048):
        raise VaultUnavailable('Invalid bounded credential envelope')


class WindowsDPAPIProtector:
    protector_id = 'windows-dpapi-current-user-v1'
    synthetic = False

    def __init__(self):
        if os.name != 'nt':
            raise VaultUnavailable('Windows credential protection is unavailable')

    def protect(self, plaintext, scope):
        return ProtectedCredential(self.protector_id, self._crypt(plaintext, scope, decrypt=False))

    def unprotect(self, envelope, scope):
        if not isinstance(envelope, ProtectedCredential) or envelope.protector_id != self.protector_id:
            raise VaultUnavailable('Original credential protector is unavailable')
        return self._crypt(envelope.ciphertext, scope, decrypt=True)

    @staticmethod
    def _crypt(data, scope, *, decrypt):
        _bounded(data, scope, maximum=65536 if decrypt else 8192)
        import ctypes
        from ctypes import wintypes

        class Blob(ctypes.Structure):
            _fields_ = [('cbData', wintypes.DWORD),
                        ('pbData', ctypes.POINTER(ctypes.c_ubyte))]

        data_buffer = ctypes.create_string_buffer(data)
        scope_buffer = ctypes.create_string_buffer(scope)
        source = Blob(len(data), ctypes.cast(data_buffer, ctypes.POINTER(ctypes.c_ubyte)))
        entropy = Blob(len(scope), ctypes.cast(scope_buffer, ctypes.POINTER(ctypes.c_ubyte)))
        output = Blob()
        crypt32 = ctypes.WinDLL('crypt32', use_last_error=True)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        function = crypt32.CryptUnprotectData if decrypt else crypt32.CryptProtectData
        function.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.POINTER(Blob),
                             ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
        function.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        description = None if decrypt else ctypes.cast(ctypes.c_wchar_p('Meong credential v1'), ctypes.c_void_p)
        try:
            # UI_FORBIDDEN; never LOCAL_MACHINE or an interactive credential prompt.
            if not function(ctypes.byref(source), description, ctypes.byref(entropy),
                            None, None, 1, ctypes.byref(output)):
                raise VaultUnavailable('Original credential protection failed')
            if not output.pbData or not 0 < output.cbData <= 65536:
                raise VaultUnavailable('Invalid protected credential result')
            return ctypes.string_at(output.pbData, output.cbData)
        finally:
            ctypes.memset(data_buffer, 0, len(data_buffer))
            ctypes.memset(scope_buffer, 0, len(scope_buffer))
            if output.pbData:
                ctypes.memset(output.pbData, 0, output.cbData)
                kernel32.LocalFree(output.pbData)


class SyntheticAeadProtector:
    """Encrypted fixture only; the key is supplied in memory, never written here."""
    protector_id = 'synthetic-aesgcm-fixture-v1'
    synthetic = True

    def __init__(self, key, *, fixture=False):
        if fixture is not True or not isinstance(key, bytes) or len(key) != 32:
            raise VaultUnavailable('Synthetic protection requires explicit fixture configuration')
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        self._cipher = AESGCM(key)

    def __repr__(self):
        return '<SyntheticAeadProtector: nonproduction fixture>'

    def protect(self, plaintext, scope):
        _bounded(plaintext, scope, maximum=8192)
        nonce = os.urandom(12)
        return ProtectedCredential(self.protector_id, nonce+self._cipher.encrypt(nonce, plaintext, scope))

    def unprotect(self, envelope, scope):
        if (not isinstance(envelope, ProtectedCredential) or envelope.protector_id != self.protector_id):
            raise VaultUnavailable('Original credential protector is unavailable')
        _bounded(envelope.ciphertext, scope)
        try:
            value = envelope.ciphertext
            return self._cipher.decrypt(value[:12], value[12:], scope)
        except Exception:
            raise VaultUnavailable('Original credential authentication failed') from None


def platform_protector():
    # No plaintext/key-file fallback on headless Linux, reinstall or missing keyring.
    # Ubuntu Secret Service/TPM support needs a verified adapter and real OS tests.
    return WindowsDPAPIProtector()


def mock_protector_allowed(protector, *, windows_protected=False):
    """Explicit mock-only integration gate; never a merchant launch approval.

    Do not trust a caller's protector ID or synthetic=False assertion as OS
    protection. The protected integration uses the exact implemented DPAPI
    adapter on Windows; other platforms and fixture keys fail closed.
    """
    if windows_protected is True:
        return os.name == 'nt' and type(protector) is WindowsDPAPIProtector
    if windows_protected is not False:
        return False
    return getattr(protector, 'synthetic', None) is True


def protection_status():
    return {'os_protection': 'WINDOWS_DPAPI_USER' if os.name == 'nt' else 'UNSUPPORTED',
            'device_acceptance': 'NOT_VERIFIED'}
