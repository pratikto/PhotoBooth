"""One asynchronous camera owner and the existing local face-invitation policy."""

import logging
import threading
import time

LOG = logging.getLogger(__name__)


def open_camera_service(index):
    # Native imports and the first driver read stay off the GUI thread.
    from photobooth.camera import Camera
    return Camera(camera_index=index)


class AsyncCamera:
    """Open/reconnect/close on one manager thread; GUI reads a fresh mailbox.

    The underlying Camera retains its own acquisition-thread ownership. Never
    open another handle while a previous native read is still shutting down.
    This adapter never writes frames, recognises identity or records video.
    """

    def __init__(self, *, enabled=True, index=0, factory=open_camera_service,
                 retry_seconds=3, clock=time.monotonic):
        self.enabled, self.index = enabled, index
        self._factory, self._clock = factory, clock
        self._retry_seconds = retry_seconds
        self._lock = threading.Lock()
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread = None
        self._active = True
        self._frame = None
        self._stamp = 0
        self._state = 'idle' if enabled else 'disabled'

    @property
    def state(self):
        with self._lock:
            return self._state

    def start(self):
        with self._lock:
            if not self.enabled or self._thread is not None or self._stop.is_set():
                return
            self._thread = threading.Thread(target=self._run, daemon=True, name='portrait-v2-camera')
            self._thread.start()

    def set_active(self, active):
        with self._lock:
            active = bool(active)
            if active == self._active or self._stop.is_set():
                return
            self._active = active
            self._frame = None
            self._stamp = 0
            self._state = 'connecting' if active else 'paused'
        self._wake.set()

    def read(self):
        with self._lock:
            if (self._stop.is_set() or not self._active or
                    self._clock() - self._stamp > 1):
                return None
            return self._frame

    def _status(self, state):
        with self._lock:
            if self._stop.is_set():
                return
            changed = state != self._state
            self._state = state if self._active else 'paused'
        if changed:
            LOG.info('Camera state=%s', state)

    def _wait(self, seconds):
        self._wake.wait(seconds)
        self._wake.clear()

    def _run(self):
        camera = None
        opened = False
        try:
            while not self._stop.is_set():
                with self._lock:
                    active = self._active
                if not active:
                    if camera is not None and opened:
                        camera.close()
                    opened = False
                    self._wait(.1)
                    continue
                if not opened:
                    self._status('connecting')
                    try:
                        if camera is None:
                            camera = self._factory(self.index)
                        opened = bool(camera.open())
                    except Exception:
                        LOG.warning('Camera connection unavailable', exc_info=True)
                        opened = False
                    if not opened:
                        self._status('unavailable')
                        self._wait(self._retry_seconds)
                        continue
                frame = camera.read()
                if frame is None:
                    with self._lock:
                        self._frame = None
                    self._status('unavailable')
                    camera.close()
                    opened = False
                    self._wait(self._retry_seconds)
                    continue
                with self._lock:
                    if self._active and not self._stop.is_set():
                        if frame is not self._frame:
                            self._stamp = self._clock()
                        self._frame = frame
                self._status('ready')
                self._wait(.03)
        except Exception:
            LOG.warning('Camera manager stopped after a driver failure', exc_info=True)
            self._status('unavailable')
        finally:
            if camera is not None:
                try:
                    camera.close()
                except Exception:
                    LOG.warning('Camera close failed', exc_info=True)
            with self._lock:
                self._frame = None
                self._state = 'closed'

    def close(self):
        self._stop.set()
        with self._lock:
            self._frame = None
            self._state = 'closing' if self._thread is not None and self._thread.is_alive() else 'closed'
        self._wake.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=.05)

    def wait_closed(self, timeout=3):
        """Dedicated launcher waits after GUI shutdown, while diagnostics stay open."""
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=timeout)


class FaceInviter:
    """Use the existing nonrecording worker, hold, cooldown and revision tags."""

    def __init__(self, *, enabled=True, hold=5, cooldown=45, worker=None, trigger=None):
        self.enabled = enabled
        self.hold, self.cooldown = hold, cooldown
        self._worker, self._trigger = worker, trigger
        self._closed = False

    def update(self, frame, revision, *, allowed, now=None):
        if self._closed or not self.enabled:
            return False
        if not allowed or frame is None:
            self.pause()
            return False
        if self._worker is None:
            from photobooth.face_presence import FacePresenceTrigger, FacePresenceWorker
            self._worker = FacePresenceWorker()
            self._trigger = FacePresenceTrigger(self.hold, self.cooldown)
        self._worker.start()
        self._worker.submit(frame, revision)
        result = self._worker.poll()
        now = time.monotonic() if now is None else now
        if (result is None or result.context != revision or
                not 0 <= now - result.captured_at <= .5):
            return False
        return self._trigger.observe(result.score >= .5, result.captured_at)

    def pause(self):
        if self._worker is not None:
            self._worker.pause()
            self._trigger.pause()

    def close(self):
        self._closed = True
        self.pause()
        if self._worker is not None:
            self._worker.close()
