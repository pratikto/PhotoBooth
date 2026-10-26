"""FEAT-009 observation-only supervisor; never terminate/restart the kiosk.

The UI writes a tiny, replace-only heartbeat from Kivy's main thread. A separate
process measures changes with its own monotonic clock, so a stuck event loop
cannot keep reporting healthy through a background thread. No customer data,
checkout identifiers, credentials or commands enter these reports.
"""

import json
import logging
import math
import os
from pathlib import Path
import time

from photobooth.manifest_io import write_json_atomic

LOG = logging.getLogger(__name__)
PHASES = frozenset({'starting', 'running', 'suspended', 'stopping'})


class HeartbeatWriter:
    def __init__(self, path, run_id, *, pid=None):
        self.path = Path(path)
        self.run_id = run_id
        self.pid = os.getpid() if pid is None else pid
        self.sequence = 0

    def pulse(self, phase):
        if phase not in PHASES:
            raise ValueError('Unknown heartbeat phase')
        self.sequence += 1
        payload = {'schema_version': 1, 'run_id': self.run_id, 'pid': self.pid,
                   'sequence': self.sequence, 'phase': phase}
        # Ephemeral liveness evidence needs atomic replacement, not a durable
        # transaction fsync on every UI tick. Durable reports use manifest_io.
        temporary = self.path.with_suffix('.tmp')
        try:
            temporary.write_text(json.dumps(payload), encoding='utf-8')
            temporary.replace(self.path)
        except OSError:
            # An unavailable diagnostics disk must not break a paid visit.
            if self.sequence == 1:
                LOG.warning('Watchdog heartbeat unavailable')


class AppHeartbeat:
    """Optional launcher hook; owns one scheduled event, no UI/service methods."""
    def __init__(self, app, clock, writer):
        self.app, self.writer = app, writer
        writer.pulse('starting')
        self.event = clock.schedule_interval(self.tick, 2)

    def tick(self, _dt):
        phase = ('stopping' if getattr(self.app, '_closed', False) else
                 'suspended' if getattr(self.app, '_suspended', False) else 'running')
        self.writer.pulse(phase)

    def close(self):
        self.event.cancel()
        self.writer.pulse('stopping')


def attach_heartbeat(app, clock, *, environ=None):
    env = os.environ if environ is None else environ
    path, run_id = env.get('MEONG_WATCHDOG_HEARTBEAT'), env.get('MEONG_WATCHDOG_RUN_ID')
    if not path or not run_id:
        return None
    return AppHeartbeat(app, clock, HeartbeatWriter(path, run_id))


class WatchdogMonitor:
    """Ignore foreign/stale/malformed pulses; never infer business recovery."""
    def __init__(self, run_id, pid, *, clock=time.monotonic, startup_timeout=90,
                 stale_timeout=30):
        if not all(math.isfinite(value) and value > 0 for value in (startup_timeout, stale_timeout)):
            raise ValueError('Timeouts must be positive')
        self.run_id, self.pid, self.clock = run_id, pid, clock
        self.startup_timeout, self.stale_timeout = startup_timeout, stale_timeout
        self.started = self.last_seen = clock()
        self.sequence = 0
        self.phase = 'starting'

    def observe(self, payload=None, *, exit_code=None):
        now = self.clock()
        if isinstance(payload, dict) and (
                payload.get('schema_version') == 1 and payload.get('run_id') == self.run_id
                and payload.get('pid') == self.pid
                and type(payload.get('sequence')) is int
                and payload['sequence'] > self.sequence
                and isinstance(payload.get('phase'), str) and payload['phase'] in PHASES):
            self.sequence = payload['sequence']
            self.phase = payload['phase']
            self.last_seen = now
        if exit_code is not None:
            status = {0: 'EXITED', 2: 'STARTUP_BLOCKED', 3: 'RECOVERY_HOLD'}.get(exit_code, 'CRASHED')
        elif not self.sequence or self.phase == 'starting':
            status = 'STARTUP_TIMEOUT' if now - self.started >= self.startup_timeout else 'STARTING'
        elif now - self.last_seen >= self.stale_timeout:
            status = 'UNRESPONSIVE'
        else:
            status = self.phase.upper()
        return {'schema_version': 1, 'run_id': self.run_id, 'pid': self.pid,
                'status': status, 'phase': self.phase, 'exit_code': exit_code,
                'operator_attention': status in {'CRASHED', 'STARTUP_TIMEOUT', 'UNRESPONSIVE',
                                                 'STARTUP_BLOCKED', 'RECOVERY_HOLD'},
                'automatic_restart': False}


def read_heartbeat(path):
    try:
        # Bound input even if a damaged file is substituted for the heartbeat.
        with Path(path).open('rb') as stream:
            raw = stream.read(2049)
        return json.loads(raw) if len(raw) <= 2048 else None
    except (OSError, ValueError, UnicodeError):
        return None


def supervise(process, heartbeat_path, report_path, monitor, *, wait=time.sleep,
              announce=print):
    """Wait for actual process exit; a closing UI may still have active workers.

    Ctrl+C in the monitor must not kill an uncertain payment/print. The launcher
    isolates the child's process group; the operator closes the kiosk normally.
    """
    previous = None
    report_error = False
    while True:
        try:
            code = process.poll()
            report = monitor.observe(read_heartbeat(heartbeat_path), exit_code=code)
            if report['status'] != previous:
                try:
                    write_json_atomic(Path(report_path), report)
                except OSError:
                    if not report_error:
                        announce('Watchdog report unavailable; console observation continues.')
                        report_error = True
                announce('MEONG watchdog: ' + report['status'])
                previous = report['status']
            if code is not None:
                return code
            wait(1)
        except KeyboardInterrupt:
            announce('Close the kiosk window to exit safely; watchdog keeps observing.')


def windows_startup_script(root, executable, arguments=()):
    """Generate a reviewable cmd launcher; installation is an operator action.

    Values are literal cmd strings. Reject shell metacharacters rather than
    accepting arbitrary shell fragments or embedding environment credentials.
    """
    values = [str(Path(root).resolve()), str(Path(executable).resolve())]
    if any(any(c in value for c in '\r\n"%!?^&|<>') for value in values):
        raise ValueError('Startup paths contain unsupported cmd characters')
    allowed = {'--print', '--drive', '--manual-print'}
    if any(arg not in allowed for arg in arguments):
        raise ValueError('Only delivery flags are supported')
    if '--manual-print' in arguments and '--print' not in arguments:
        raise ValueError('--manual-print requires --print in the startup launcher')
    folder, python = values
    options = ''.join(' ' + arg for arg in arguments)
    return ('@echo off\nsetlocal\nchcp 65001 >nul\n'
            f'cd /d "{folder}"\nif errorlevel 1 exit /b 1\n'
            f'"{python}" "{folder}\\tools\\run_portrait_v2_watchdog.py"{options}\n'
            'set "MEONG_EXIT=%ERRORLEVEL%"\n'
            'if not "%MEONG_EXIT%"=="0" pause\nexit /b %MEONG_EXIT%\n')


def systemd_user_unit(root, executable, arguments=()):
    """Generate an Ubuntu graphical-session unit, including from Windows.

    Target paths are POSIX paths on the mini PC, never resolved on the developer
    machine. systemd receives an argv directly; no shell or embedded credentials.
    """
    from pathlib import PurePosixPath
    paths = [str(root), str(executable)]
    if any(not PurePosixPath(value).is_absolute() or value != value.strip() or '\\' in value
           or any(ord(c) < 32 or ord(c) == 127 or c in '%$' for c in value)
           or '..' in PurePosixPath(value).parts for value in paths):
        raise ValueError('Use absolute Ubuntu paths without control characters, variables or traversal')
    if any(arg not in {'--print', '--drive', '--manual-print'} for arg in arguments):
        raise ValueError('Only delivery flags are supported')
    if '--manual-print' in arguments and '--print' not in arguments:
        raise ValueError('--manual-print requires --print in the startup launcher')
    def quote(value):
        return '"' + value.replace('"', '\\"') + '"'
    folder, python = paths
    command = [quote(python), quote(str(PurePosixPath(folder) / 'tools/run_portrait_v2_watchdog.py')),
               *arguments]
    return ('[Unit]\nDescription=Meong portrait kiosk v2 watchdog\n'
            'PartOf=graphical-session.target\nAfter=graphical-session-pre.target\n\n'
            '[Service]\nType=simple\n'
            f'WorkingDirectory={folder}\nExecStart={" ".join(command)}\n'
            'Restart=no\nKillSignal=SIGINT\nTimeoutStopSec=90\nSendSIGKILL=no\n\n'
            '[Install]\nWantedBy=graphical-session.target\n')
