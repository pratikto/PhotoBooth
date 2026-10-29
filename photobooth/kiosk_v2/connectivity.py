"""Passive OS connectivity hints; never payment/provider reachability evidence."""
import os
from pathlib import PureWindowsPath
import platform
import re
import subprocess
import time


def read_connectivity_hint(*, system=None, run=None, environ=None):
    """Read cached OS state off the UI thread, with no external network probe."""
    system = platform.system() if system is None else system
    run = subprocess.run if run is None else run
    environ = os.environ if environ is None else environ
    if system == 'Linux':
        command = ['nmcli', '--terse', '--fields', 'CONNECTIVITY', 'general']
    elif system == 'Windows':
        root = PureWindowsPath(environ.get('SystemRoot', environ.get('SYSTEMROOT', '')))
        if not root.is_absolute() or re.fullmatch(r'[A-Za-z]:', root.drive) is None or '..' in root.parts:
            return None
        command = [str(root / 'System32/WindowsPowerShell/v1.0/powershell.exe'),
                   '-NoProfile', '-NonInteractive', '-Command',
                   "$nlm=[Activator]::CreateInstance([type]::GetTypeFromCLSID("
                   "[guid]'{DCB00C01-570F-4A9B-8D69-199FDBA5723B}')); [int]$nlm.GetConnectivity()"]
    else:
        return None
    # Local OS helpers need no booth bearer, merchant key, PIN, customer ticket,
    # user PowerShell profile or provider endpoint configuration.
    clean = {key: value for key, value in environ.items()
             if key.upper() in {'SYSTEMROOT', 'WINDIR', 'PATH', 'LANG', 'LC_ALL'}}
    try:
        result = run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                     shell=False, timeout=1.5, check=False, env=clean)
        if result.returncode != 0 or not isinstance(result.stdout, bytes) or len(result.stdout) > 64:
            return None
        state = result.stdout.decode('ascii').strip()
        if system == 'Linux':
            return {'full': True, 'none': False, 'limited': False, 'portal': False}.get(state)
        if re.fullmatch(r'[0-9]{1,5}', state) is None:
            return None
        flags = int(state)
        if flags & ~0x773:  # Only documented NLM_CONNECTIVITY flags.
            return None
        return bool(flags & 0x440)  # NLM IPv4/IPv6 Internet hint flags.
    except (OSError, subprocess.SubprocessError, ValueError, UnicodeError):
        return None


class ConnectivityRestoration:
    """Coalesce sampled offline→online edges on the existing checkout worker."""
    def __init__(self, *, read=read_connectivity_hint, clock=time.monotonic):
        self.read, self.clock = read, clock
        self._next_at = 0
        self._last = None

    def poll(self):
        current = self.clock()
        if current < self._next_at:
            return False
        self._next_at = current + 5
        try:
            state = self.read()
        except Exception:
            return False  # A hint failure never breaks the original paid visit.
        if state is False:
            self._last = False
        elif state is True:
            restored = self._last is False
            self._last = True
            return restored
        return False
