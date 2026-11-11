"""Trusted pre-device ownership for the original protected Sandbox profile.

No native/provider imports before the shared original global LaunchLease. This
is a launcher-owned core, not a customer entry point or production activation.
The GUI receives only accepted public control and the same original camera.
"""
from contextlib import closing
from pathlib import Path
import sqlite3
import time

from photobooth.kiosk_v2.recovery import LaunchLease,checked_path


class ProtectedLaunchHeld(RuntimeError):
    """Static redacted startup/shutdown status; no private configuration."""


class ProtectedSandboxLaunch:
    def __init__(self,project_root):
        self._legacy=self._camera=self._visits=self._worker=self._control=None
        self._recovery=None
        self._started=self._ready=self._stopping=self._closed=False
        try:
            root=Path(project_root)
            if not root.is_absolute():raise ValueError
            self.project_root=checked_path(root)
            # SAME lock as original ordinary v2, merchant trial and pilot.
            self._global=LaunchLease(self.project_root)
        except (OSError,ValueError,TypeError):
            raise ProtectedLaunchHeld('Original global kiosk ownership unavailable') from None

    def __repr__(self):
        return '<ProtectedSandboxLaunch: trusted original owner; not release authority>'

    def _public(self):
        if not self._ready or self._stopping or self._closed:
            raise ProtectedLaunchHeld('Original accepted native startup required')

    @property
    def control(self):
        self._public()
        return self._control

    @property
    def camera(self):
        self._public()
        return self._camera

    def start(self,config,printer_config,*,legacy_path,qr_loader,
              camera_index=0,camera_enabled=True,timeout=25,finish_on_stop=False,
              durable_worker_epochs=False):
        """One bounded trusted startup; preserve partial handles on any failure.

        Caller must retain this owner and retry stop() until True on startup
        HOLD as well as normal GUI exit. Never use an unconditional with/finally
        that releases global ownership beneath an original live worker.
        """
        if self._started or self._stopping or self._closed or self._global.stream.closed:
            raise ProtectedLaunchHeld('Original launch cannot be restarted')
        self._started=True
        try:
            if (type(timeout) not in (int,float) or not 0<timeout<=30
                    or type(camera_index) is not int or not 0<=camera_index<=32
                    or type(camera_enabled) is not bool or type(finish_on_stop) is not bool
                    or type(durable_worker_epochs) is not bool
                    or not callable(qr_loader)):
                raise ValueError
            deadline=time.monotonic()+timeout
            # These imports/constructions happen only AFTER global ownership.
            from photobooth.checkout_store import CheckoutStore
            from photobooth.kiosk_v2.devices import AsyncCamera
            from photobooth.post_preview_host import SandboxHostConfig
            from photobooth.post_preview_sandbox_visits import OriginalSandboxVisits
            from photobooth.post_preview_visit_control import create_visit_control
            from photobooth.printer import PrinterConfig
            if type(config) is not SandboxHostConfig or type(printer_config) is not PrinterConfig:
                raise ValueError
            history=Path(legacy_path)
            if not history.is_absolute():raise ValueError
            history=checked_path(history)
            if not history.is_file():raise ValueError
            for suffix in ('-wal','-shm'):checked_path(str(history)+suffix)
            # An arbitrary existing/empty file is not original legacy history.
            # Check read-only before CheckoutStore's additive migrations run.
            with closing(sqlite3.connect(history.as_uri()+'?mode=ro',uri=True,timeout=.2)) as db:
                db.execute('SELECT id,booth_id,checkout_key,state FROM checkouts LIMIT 0')
            self._legacy=CheckoutStore(history)
            if durable_worker_epochs:
                from photobooth.post_preview_interrupted_recovery import OriginalInterruptedRecovery
                self._recovery=OriginalInterruptedRecovery(self,config,printer_config)
                remaining=deadline-time.monotonic()
                if remaining<=0:raise ValueError
                self._recovery.finish(timeout=remaining)
                if time.monotonic()>=deadline:raise ValueError
            self._camera=AsyncCamera(enabled=camera_enabled,index=camera_index)
            self._visits=OriginalSandboxVisits(config,printer_config,self._legacy,
                camera=self._camera,qr_loader=qr_loader,durable_worker_epochs=durable_worker_epochs)
            self._control,self._worker=create_visit_control(self._visits,finish_on_stop=finish_on_stop)
            if not self._control.start():raise ValueError
            while time.monotonic()<deadline:
                outcome=self._control.poll()
                if outcome is not None:
                    if (outcome.state!='READY' or outcome.binding is None
                            or outcome.binding is not self._visits._binding
                            or outcome.binding is not self._control.binding):raise ValueError
                    self._ready=True
                    return self._control
                time.sleep(.01)
            raise ValueError
        except Exception:
            # The trusted owner remains reachable with all partial resources.
            # Stop request is nonblocking; original threads must actually exit.
            if self._control is not None:self._control.request_stop()
            raise ProtectedLaunchHeld('Original protected startup held; preserve owner and drain') from None

    def stop(self,*,timeout=0):
        """False retains global lock/history; True requires actual original exit."""
        if type(timeout) not in (int,float) or not 0<=timeout<=15:
            raise ValueError('Bounded original launch shutdown required')
        if self._closed:return True
        self._stopping=True;self._ready=False
        deadline=time.monotonic()+timeout
        try:
            if self._control is not None:self._control.request_stop()
            if self._camera is not None:self._camera.close()
            if self._recovery is not None and not self._recovery.stop(timeout=max(0,deadline-time.monotonic())):
                return False
            if self._worker is not None:
                if not self._worker.stop(timeout=max(0,deadline-time.monotonic())):return False
                if (self._worker._thread.is_alive() or not self._control.stopped
                        or not self._visits._closed):return False
            elif self._visits is not None and not self._visits.stop():return False
            if self._camera is not None:
                self._camera.wait_closed(timeout=max(0,deadline-time.monotonic()))
                thread=self._camera._thread
                # wait_closed returns None, never a quiescence assertion.
                if thread is not None and thread.is_alive():return False
            if self._legacy is not None:self._legacy.close();self._legacy=None
            self._global.close()
            self._closed=True
            return True
        except Exception:
            return False  # Never close the shared global lock on uncertainty.
