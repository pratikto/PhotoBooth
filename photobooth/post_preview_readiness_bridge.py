"""Private local worker observations for a separately owned merchant backend.

The launcher supplies connected socket-pair capabilities, never a public listener
or HTTP readiness flags. This bridge carries no payment/Drive authorization,
credentials, media or QR. A failed channel is retired, never reconnected/replayed.
It does not enable a provider profile or establish OS credential protection.
"""
import json
import ipaddress
import select
import socket
import struct
import threading
import time
import uuid
from contextlib import contextmanager

from photobooth.post_preview_authority import authenticated_payment_readiness
from photobooth.post_preview_readiness import (
    CheckObservation, LocalChargeReadiness, ReadinessScope, TrustedChargeReadiness,
    REQUIRED_CHECKS, finite_number,
)

LOCAL_CHECKS = LocalChargeReadiness.LOCAL_CHECKS | {'worker_ownership'}
DRIVE_CHECKS = frozenset({'drive_api', 'drive_sharing', 'unclaimed_ready_capacity'})
MAX_MESSAGE = 8192


def _private_channel(channel):
    if not isinstance(channel, socket.socket) or channel.type != socket.SOCK_STREAM:
        raise ValueError('Private connected stream required')
    try:
        local, peer = channel.getsockname(), channel.getpeername()
        if channel.family == getattr(socket, 'AF_UNIX', None):
            valid = local == peer == ''  # Anonymous socketpair, no filesystem listener.
        else:
            valid = (channel.family in {socket.AF_INET, socket.AF_INET6}
                     and ipaddress.ip_address(local[0]).is_loopback
                     and ipaddress.ip_address(peer[0]).is_loopback)
        if not valid:
            raise ValueError('Private local channel required')
    except (OSError, IndexError, TypeError):
        raise ValueError('Private connected channel required') from None


def _budget(channel, deadline):
    remaining = deadline-time.monotonic()
    if remaining <= 0:
        raise TimeoutError('Readiness deadline elapsed')
    channel.settimeout(remaining)


def _unknown():
    return {name: CheckObservation('UNKNOWN', None) for name in LOCAL_CHECKS}


def _scope_data(scope):
    if type(scope) is not ReadinessScope:
        raise ValueError('Exact original worker scope required')
    return dict(purchase_group_id=scope.purchase_group_id, booth_id=scope.booth_id,
                contract_sha256=scope.contract_sha256, generation=scope.generation)


def _scope(value):
    if type(value) is not dict or set(value) != {
            'purchase_group_id', 'booth_id', 'contract_sha256', 'generation'}:
        raise ValueError('Original readiness scope required')
    return ReadinessScope(**value)


def _exact_bytes(channel, length, deadline):
    data = bytearray()
    while len(data) < length:
        _budget(channel, deadline)
        chunk = channel.recv(length-len(data))
        if not chunk:
            raise OSError('Readiness channel retired')
        data.extend(chunk)
    return bytes(data)


def _receive(channel, deadline):
    size = struct.unpack('!I', _exact_bytes(channel, 4, deadline))[0]
    if not 1 <= size <= MAX_MESSAGE:
        raise ValueError('Bounded readiness message required')
    def unique_fields(pairs):
        result = {}
        for name, item in pairs:
            if name in result:
                raise ValueError('Duplicate readiness field')
            result[name] = item
        return result
    value = json.loads(_exact_bytes(channel, size, deadline), object_pairs_hook=unique_fields)
    if type(value) is not dict:
        raise ValueError('Typed readiness message required')
    return value


def _send(channel, value, deadline):
    payload = json.dumps(value, separators=(',', ':'), allow_nan=False).encode('utf-8')
    if not 1 <= len(payload) <= MAX_MESSAGE:
        raise ValueError('Bounded readiness message required')
    _budget(channel, deadline)
    channel.sendall(struct.pack('!I', len(payload))+payload)


def _retire(channel):
    try:
        channel.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    channel.close()


def _identity(message, kind, fields):
    request_id = message.get('request_id')
    if (set(message) != fields or message.get('version') != 1
            or type(message.get('version')) is not int or message.get('kind') != kind
            or type(request_id) is not str or len(request_id) != 32
            or any(c not in '0123456789abcdef' for c in request_id)):
        raise ValueError('Scoped readiness protocol required')
    return request_id, _scope(message['scope'])


class WorkerReadinessClient:
    """Backend-only client; one bounded, nonce-bound request at a time."""
    def __init__(self, channel, *, timeout=1):
        _private_channel(channel)
        if not finite_number(timeout) or not .05 <= timeout <= 2:
            raise ValueError('Bounded private readiness channel required')
        channel.settimeout(timeout)
        self._channel = channel
        self._timeout = timeout
        self._lock = threading.Lock()
        self._closed = False

    def close(self):
        self._closed = True
        _retire(self._channel)

    def observe(self, scope):
        if not self._lock.acquire(blocking=False):
            return _unknown()
        try:
            if self._closed:
                return _unknown()
            request_id = uuid.uuid4().hex
            deadline = time.monotonic()+self._timeout
            _send(self._channel, dict(version=1, kind='READINESS', request_id=request_id,
                                      scope=_scope_data(scope)), deadline)
            response = _receive(self._channel, deadline)
            received, actual = _identity(response, 'OBSERVATIONS', {
                'version', 'kind', 'request_id', 'scope', 'observations'})
            observations = response['observations']
            if (received != request_id or actual != scope or type(observations) is not dict
                    or set(observations) != LOCAL_CHECKS):
                raise ValueError('Original worker response mismatch')
            result = {}
            for name, value in observations.items():
                if (type(value) is not dict or set(value) != {'state', 'observed_at'}
                        or value['state'] not in {'READY', 'NOT_READY', 'UNKNOWN'}
                        or value['observed_at'] is not None and not finite_number(value['observed_at'])
                        or value['state'] == 'READY' and value['observed_at'] is None):
                    raise ValueError('Typed worker observation required')
                result[name] = CheckObservation(value['state'], value['observed_at'])
            # Freshness is checked by TrustedChargeReadiness at admission. Never
            # restamp an old value simply because its transport just completed.
            return result
        except (OSError, ValueError, TypeError, KeyError, RecursionError, struct.error):
            self.close()
            return _unknown()
        finally:
            self._lock.release()


class WorkerReadinessServer:
    """Native-process side; collector observes the actual original worker.

    Use the original LocalChargeReadiness collector with OriginalWorkerReadiness
    bound to the native camera/PhotoJobs/launch lease. It may inspect durable
    private media but cannot send that media through this protocol.
    """
    def __init__(self, channel, collector):
        _private_channel(channel)
        if not callable(collector):
            raise ValueError('Private channel and trusted worker collector required')
        channel.settimeout(.5)
        self._channel, self._collector = channel, collector
        self._stop = threading.Event()
        self._thread = None
        self._lifecycle_lock = threading.Lock()
        self._original_collector = None

    @classmethod
    def from_original_worker(cls, channel, collector):
        if type(collector) is not LocalChargeReadiness:
            raise ValueError('Original local media/device readiness collector required')
        server = cls(channel, lambda scope: collector(scope.purchase_group_id))
        server._original_collector = collector
        return server

    def start(self):
        with self._lifecycle_lock:
            if self._thread is not None or self._stop.is_set():
                raise RuntimeError('Readiness worker cannot be restarted')
            self._thread = threading.Thread(target=self._run, name='postpay-readiness', daemon=True)
            self._thread.start()

    def stop(self, *, timeout=2):
        if not finite_number(timeout) or not 0 <= timeout <= 5:
            raise ValueError('Bounded readiness shutdown required')
        with self._lifecycle_lock:
            self._stop.set()
            _retire(self._channel)
            thread = self._thread
        if thread is not None:
            thread.join(timeout)
        return thread is None or not thread.is_alive()

    @contextmanager
    def quiescent(self):
        """Permanently retire this original capability before occupancy ACK.

        Closing a socket alone does not stop its collector callback. A later
        visitor needs a new private channel/collector; this one never restarts.
        No shutdown deadline is relabelled as successful worker completion.
        """
        if not self.stop(timeout=0):
            raise RuntimeError('Original readiness collector remains active')
        yield

    def _run(self):
        try:
            while not self._stop.is_set():
                if not select.select([self._channel], [], [], .1)[0]:
                    continue
                request = _receive(self._channel, time.monotonic()+.5)
                request_id, scope = _identity(request, 'READINESS', {
                    'version', 'kind', 'request_id', 'scope'})
                values = _unknown()
                try:
                    report = self._collector(scope)
                    if (type(report) is TrustedChargeReadiness and report.scope == scope
                            and type(report.observations) is tuple
                            and len(report.observations) == len(REQUIRED_CHECKS)):
                        original = {}
                        for item in report.observations:
                            if (type(item) is not tuple or len(item) != 2
                                    or type(item[0]) is not str or item[0] not in REQUIRED_CHECKS
                                    or item[0] in original or type(item[1]) is not CheckObservation):
                                raise ValueError('Complete typed worker report required')
                            original[item[0]] = item[1]
                        values = {name: original.get(name, CheckObservation('UNKNOWN', None))
                                  for name in LOCAL_CHECKS}
                except Exception:
                    pass  # No private driver exception text crosses the channel.
                if self._stop.is_set():
                    break
                _send(self._channel, dict(version=1, kind='OBSERVATIONS', request_id=request_id,
                    scope=_scope_data(scope), observations={name: {
                        'state': value.state, 'observed_at': value.observed_at}
                        for name, value in values.items()}), time.monotonic()+.5)
        except (OSError, ValueError, TypeError, AttributeError, KeyError, RecursionError, struct.error):
            pass
        finally:
            self._stop.set()
            _retire(self._channel)


class BackendChargeReadiness:
    """Combine original-worker facts with independent backend authorities.

    This object is installed by the backend host. HTTP callers cannot supply its
    bridge or observations. The backend independently verifies the frozen bytes;
    original timestamps are rechecked by the payment coordinator before SEND.
    """
    def __init__(self, checkout, templates, bridge, *, drive_probe=None):
        if type(bridge) is not WorkerReadinessClient:
            raise ValueError('Exact original worker readiness channel required')
        self.checkout, self.templates = checkout, tuple(templates)
        self.bridge, self.drive_probe = bridge, drive_probe

    def __call__(self, group):
        scope = self.checkout.verify_frozen(group, self.templates)
        observations = self.bridge.observe(scope)
        if self.drive_probe is not None:
            try:
                drive = self.drive_probe.observe(scope)
                if type(drive) is dict and set(drive).issubset(DRIVE_CHECKS):
                    observations.update(drive)
            except Exception:
                pass
        observations['payment_authorization'] = authenticated_payment_readiness(scope)
        probes = {name: lambda _scope, value=value: value for name, value in observations.items()}
        return TrustedChargeReadiness.observe(scope, probes)
