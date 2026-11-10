"""Read-only OS process observations; NOT worker/descendant/ACK authority.

Persisting/authenticating the original identity and proving independent kernel
and device quiescence are separate obligations. A PID or absent process alone
must never admit a visitor, release an owner or sign an old worker receipt.
"""
from dataclasses import dataclass
import os
from pathlib import Path
import re
import sys


class ProcessObservationHeld(RuntimeError):
    """Static failure; never expose OS/private path details."""


_HELD = 'Original process observation is unavailable'


def _pid(value):
    if type(value) is not int or not 1 <= value <= 2**32-1:
        raise ProcessObservationHeld(_HELD)
    return value


@dataclass(frozen=True)
class OriginalProcessIdentity:
    pid: int
    birth: str

    def __post_init__(self):
        _pid(self.pid)
        if (type(self.birth) is not str or re.fullmatch(
                r'(windows-filetime-[a-f0-9]{16}|linux-[a-f0-9]{32}-[0-9]{1,20})',
                self.birth) is None):
            raise ProcessObservationHeld(_HELD)


def _windows_snapshot(pid):
    """One actual handle binds creation time and wait status without PID race."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)]*4
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    # PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, read/wait only; no kill.
    handle = kernel.OpenProcess(0x1000 | 0x100000, False, pid)
    if not handle:
        if ctypes.get_last_error() == 87:  # Valid PID, no original process exists.
            return None
        raise ProcessObservationHeld(_HELD)
    try:
        creation, exit_time, kernel_time, user_time = (wintypes.FILETIME() for _ in range(4))
        if not kernel.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time),
                                      ctypes.byref(kernel_time), ctypes.byref(user_time)):
            raise ProcessObservationHeld(_HELD)
        birth = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        if not birth:
            raise ProcessObservationHeld(_HELD)
        wait = kernel.WaitForSingleObject(handle, 0)
        if wait not in (0, 258):  # WAIT_OBJECT_0 or WAIT_TIMEOUT only.
            raise ProcessObservationHeld(_HELD)
        return 'windows-filetime-%016x' % birth, wait == 0
    finally:
        kernel.CloseHandle(handle)


def _linux_snapshot(pid):
    # Numeric /proc path only; do not inspect cwd/executable/customer files.
    boot = Path('/proc/sys/kernel/random/boot_id').read_text(encoding='ascii').strip()
    if re.fullmatch(r'[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}', boot) is None:
        raise ProcessObservationHeld(_HELD)
    try:
        with Path('/proc/%d/stat' % pid).open('rb') as stream:
            raw = stream.read(4097)
    except FileNotFoundError:
        return None
    if len(raw) > 4096 or not raw.startswith(('%d (' % pid).encode()):
        raise ProcessObservationHeld(_HELD)
    # comm can contain spaces and ')'; all following stat fields are scalar.
    end = raw.rfind(b') ')
    fields = raw[end+2:].split() if end >= 0 else []
    if (len(fields) < 20 or re.fullmatch(rb'[0-9]{1,20}', fields[19]) is None
            or int(fields[19]) <= 0 or fields[0] not in (b'R', b'S', b'D', b'Z', b'T', b't', b'X', b'I', b'P')):
        raise ProcessObservationHeld(_HELD)
    return 'linux-%s-%s' % (boot.replace('-', ''), fields[19].decode('ascii')), fields[0] in (b'Z', b'X')


def _snapshot(pid):
    _pid(pid)
    try:
        if os.name == 'nt':
            return _windows_snapshot(pid)
        if sys.platform.startswith('linux'):
            return _linux_snapshot(pid)
        raise ProcessObservationHeld(_HELD)
    except Exception:
        raise ProcessObservationHeld(_HELD) from None


def observe_process(pid):
    """Capture an actual live process birth; no caller-supplied birth accepted."""
    snapshot = _snapshot(pid)
    if snapshot is None or snapshot[1]:
        raise ProcessObservationHeld(_HELD)
    return OriginalProcessIdentity(pid, snapshot[0])


def original_process_exited(identity):
    """Only process exit, NOT descendants, devices, kernel locks or ownership.

    Identity must later come from authenticated original pre-work custody. This
    primitive intentionally has no ability to make that admission decision.
    PID reuse/foreign boot identities hold conservatively, even if old PID died.
    """
    if type(identity) is not OriginalProcessIdentity:
        raise ProcessObservationHeld(_HELD)
    native_prefix = 'windows-filetime-' if os.name == 'nt' else 'linux-'
    if not identity.birth.startswith(native_prefix):
        raise ProcessObservationHeld(_HELD)
    snapshot = _snapshot(identity.pid)
    if snapshot is None:
        return True
    if snapshot[0] != identity.birth:
        raise ProcessObservationHeld(_HELD)
    return snapshot[1]
