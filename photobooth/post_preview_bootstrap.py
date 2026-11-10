"""Credential-isolated original Sandbox child host, never a customer launcher.

Secrets cross only a private anonymous socket after spawn, not argv/environment.
No mock/native admission guard is relaxed. The existing backend owns financial
workers and its kernel lease; a timed-out shutdown never force-kills or frees it.
"""
import argparse
import base64
from dataclasses import fields
import json
import logging
import math
import os
from pathlib import Path
import select
import socket
import subprocess
import sys
import threading
import time
import uuid

from photobooth.post_preview_host import SandboxHostConfig, SandboxHostRuntime
from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment
from photobooth.post_preview_readiness_bridge import (
    MAX_MESSAGE, WorkerReadinessClient, _private_channel, _receive, _send,
)
from photobooth.post_preview_store import ORDER_VERSION

CHILD_MODULE = 'photobooth.post_preview_bootstrap'
REPOSITORY = Path(__file__).resolve().parents[1]


class BackendStartupHeld(RuntimeError):
    """Allowlisted status only; never include account/OS exception text."""


def backend_environment(parent):
    allowed = {'PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'TMPDIR', 'HOME',
               'USERPROFILE', 'LOCALAPPDATA', 'APPDATA', 'LANG', 'LC_ALL', 'TZ',
               'XDG_RUNTIME_DIR', 'XDG_DATA_HOME', 'XDG_CONFIG_HOME', 'DBUS_SESSION_BUS_ADDRESS',
               'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY', 'SSL_CERT_FILE',
               'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE',
               'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'}
    return {key: value for key, value in parent.items() if key in allowed}


def _timeout(value, maximum=60):
    if type(value) not in (float, int) or not math.isfinite(value) or not 0 < value <= maximum:
        raise ValueError('Bounded backend process deadline required')
    return value


def _config_data(config):
    return {item.name: str(config.storage_root) if item.name == 'storage_root'
            else getattr(config, item.name) for item in fields(SandboxHostConfig)}


def _config(value):
    if type(value) is not dict or set(value) != {f.name for f in fields(SandboxHostConfig)}:
        raise ValueError('Exact private backend configuration required')
    if any(type(item) is not str for item in value.values()):
        raise ValueError('Typed private backend configuration required')
    return SandboxHostConfig(**value)


class SandboxBackendProcess:
    """Trusted launcher-side handle; never hand this object/config to a GUI.

    endpoint/booth_id/booth_token are the only client connection values. stop()
    reports backend exit only; original native readiness collector/worker stop
    and PREPARE/ACK remain separate obligations before admitting another visitor.
    """
    def __init__(self, config, *, fulfillment=None):
        if (type(config) is not SandboxHostConfig
                or fulfillment is not None and type(fulfillment) is not SandboxHostFulfillment):
            raise ValueError('Exact private backend configuration required')
        self._config = config
        self._fulfillment = fulfillment
        self.process = self._control = None
        self.endpoint = None
        self._nonce = uuid.uuid4().hex

    def __repr__(self):
        return '<SandboxBackendProcess: isolated backend, not booth-release authority>'

    @property
    def booth_id(self):
        return self._config.booth_id

    @property
    def booth_token(self):
        return self._config.booth_token

    def start(self, readiness_channel, *, timeout=20):
        _timeout(timeout)
        _private_channel(readiness_channel)
        if self.process is not None:
            raise BackendStartupHeld('Original backend process already started')
        request = dict(version=1, kind='START', nonce=self._nonce,
                       config=_config_data(self._config))
        if self._fulfillment is not None:
            request['fulfillment']=self._fulfillment.to_private_startup()
        if len(json.dumps(request).encode('utf-8')) > MAX_MESSAGE:
            raise ValueError('Private backend configuration exceeds transport bound')
        parent, child = socket.socketpair()
        self._control = parent
        command = [sys.executable, '-m', CHILD_MODULE]
        kwargs = dict(cwd=str(REPOSITORY), env=backend_environment(os.environ),
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            if os.name == 'nt':
                kwargs.update(stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                self.process = subprocess.Popen(command+['--socket-bootstrap'], **kwargs)
                # Only opaque OS socket handles use stdin, never credentials.
                metadata = {name: base64.b64encode(sock.share(self.process.pid)).decode('ascii')
                            for name, sock in (('control', child), ('readiness', readiness_channel))}
                raw = json.dumps(metadata).encode('ascii')+b'\n'
                if len(raw) > 4096:
                    raise ValueError('Bounded original socket handles required')
                self.process.stdin.write(raw); self.process.stdin.flush(); self.process.stdin.close()
            else:
                kwargs.update(stdin=subprocess.DEVNULL, start_new_session=True,
                              pass_fds=(child.fileno(), readiness_channel.fileno()))
                self.process = subprocess.Popen(command+['--control-fd',str(child.fileno()),
                    '--readiness-fd',str(readiness_channel.fileno())], **kwargs)
            child.close(); readiness_channel.close()
            deadline = time.monotonic()+timeout
            _send(parent, request, deadline)
            result = _receive(parent, deadline)
            if (set(result) != {'version','kind','nonce','pid','port','mode','order_version'}
                    or type(result['version']) is not int or result['version'] != 1
                    or result['kind'] != 'READY' or result['nonce'] != self._nonce
                    or type(result['pid']) is not int or result['pid'] != self.process.pid
                    or type(result['port']) is not int or not 1024 <= result['port'] <= 65535
                    or result['mode'] != 'sandbox' or result['order_version'] != ORDER_VERSION
                    or self.process.poll() is not None):
                raise ValueError('Original backend startup is not verified')
            self.endpoint = 'http://127.0.0.1:'+str(result['port'])
            return self.endpoint
        except Exception:
            # No terminate/kill or replacement process: a late original worker
            # may still be stopping. Caller retains this handle and checks stop.
            if self.process is not None and self.process.stdin is not None:
                self.process.stdin.close()
            self.stop(timeout=1)
            raise BackendStartupHeld('Original Sandbox backend startup held') from None
        finally:
            child.close()
            readiness_channel.close()

    def stop(self, *, timeout=5):
        _timeout(timeout)
        if self.process is None:
            if self._control is not None:
                self._control.close()
            return True
        self.endpoint = None
        if self.process.poll() is None:
            try:
                _send(self._control, dict(version=1,kind='STOP',nonce=self._nonce),
                      time.monotonic()+min(timeout,.5))
            except (OSError,ValueError):
                pass
            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                return False  # Preserve process/lock; no false safe-release ACK.
        if self._control is not None:
            self._control.close()
        return True


def run_child(control, readiness):
    """Run only on original inherited capabilities; exceptions are sanitized."""
    runtime = listener = None
    server = None
    finished = threading.Event()
    nonce = None
    logging.disable(logging.CRITICAL)
    try:
        _private_channel(control); _private_channel(readiness)
        request = _receive(control,time.monotonic()+20)
        if (set(request) not in ({'version','kind','nonce','config'},
                                {'version','kind','nonce','config','fulfillment'})
                or type(request['version']) is not int or request['version'] != 1
                or request['kind'] != 'START' or type(request['nonce']) is not str
                or len(request['nonce']) != 32
                or any(c not in '0123456789abcdef' for c in request['nonce'])):
            raise ValueError('Original startup capability required')
        nonce = request['nonce']
        config = _config(request['config'])
        fulfillment=(SandboxHostFulfillment.from_private_startup(request['fulfillment'])
                     if 'fulfillment' in request else None)
        if os.name != 'nt':
            os.umask(0o077)
        runtime = SandboxHostRuntime(config,WorkerReadinessClient(readiness,timeout=2),
                                     fulfillment=fulfillment)
        import uvicorn
        listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listener.bind(('127.0.0.1',0)); listener.listen(32); listener.setblocking(False)
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(runtime.app,host='127.0.0.1',port=port,
            # HTTP thread-pool provider/Drive calls must finish as well as the
            # lifecycle worker. Cancelling their await after a timeout could
            # close SQLite while the underlying original I/O thread still runs.
            access_log=False,log_config=None,log_level='critical',timeout_graceful_shutdown=None))

        def announce():
            deadline=time.monotonic()+20
            while not server.started and not finished.wait(.01):
                if time.monotonic() >= deadline:
                    server.should_exit=True
                    return
            if not finished.is_set():
                try:
                    _send(control,dict(version=1,kind='READY',nonce=nonce,pid=os.getpid(),
                        port=port,mode='sandbox',order_version=ORDER_VERSION),time.monotonic()+1)
                except (OSError,ValueError):
                    server.should_exit=True

        def commands():
            try:
                while not finished.is_set():
                    if not select.select([control],[],[],.1)[0]:
                        continue
                    command=_receive(control,time.monotonic()+.5)
                    if (type(command.get('version')) is not int
                            or command != dict(version=1,kind='STOP',nonce=nonce)):
                        raise ValueError('Original shutdown capability required')
                    break
            except (OSError,ValueError):
                pass
            finally:
                server.should_exit=True

        threading.Thread(target=announce,name='postpay-startup',daemon=True).start()
        threading.Thread(target=commands,name='postpay-control',daemon=True).start()
        server.run(sockets=[listener])
        return 0
    except BaseException:
        if nonce is not None:
            try:
                _send(control,dict(version=1,kind='HELD',nonce=nonce),time.monotonic()+.5)
            except (OSError,ValueError):
                pass
        return 2
    finally:
        finished.set()
        if listener is not None:
            listener.close()
        # A stopped HTTP listener is not proof that an in-flight provider I/O
        # has ended. Keep the process/DB/kernel lease until original worker ends.
        while runtime is not None and not runtime.close(timeout=.2):
            time.sleep(.1)
        readiness.close(); control.close()


def main(argv=None):
    parser=argparse.ArgumentParser(description='Private post-preview Sandbox child; not a kiosk launcher')
    parser.add_argument('--control-fd',type=int)
    parser.add_argument('--readiness-fd',type=int)
    parser.add_argument('--socket-bootstrap',action='store_true')
    args=parser.parse_args(argv)
    try:
        if os.name == 'nt' and args.socket_bootstrap and args.control_fd is None and args.readiness_fd is None:
            raw=sys.stdin.buffer.readline(4097)
            if len(raw)>4096: return 2
            metadata=json.loads(raw)
            if type(metadata) is not dict or set(metadata)!={'control','readiness'}: return 2
            sockets=[socket.fromshare(base64.b64decode(metadata[name],validate=True))
                     for name in ('control','readiness')]
        elif (os.name != 'nt' and not args.socket_bootstrap
                and type(args.control_fd) is int and type(args.readiness_fd) is int
                and args.control_fd>=3 and args.readiness_fd>=3 and args.control_fd!=args.readiness_fd):
            sockets=[socket.socket(fileno=args.control_fd),socket.socket(fileno=args.readiness_fd)]
        else:
            return 2
        return run_child(*sockets)
    except BaseException:
        return 2  # Never print configuration/OS/HTTP error details.


if __name__ == '__main__':
    raise SystemExit(main())
