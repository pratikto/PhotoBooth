"""Small v2 observation adapters for the verbatim v1 diagnostic worker."""
from dataclasses import replace
import os
from pathlib import Path
import threading
from types import SimpleNamespace

from photobooth.device_health import HealthCheck, READY, UNKNOWN
from photobooth.v1_health_controller import V1HealthController


class CachedCamera:
    """Expose only the already sampled mailbox, never a native camera handle."""
    def __init__(self, frame, index):
        self._frame = frame
        self.camera_index = index if type(index) is int else None
        self.capture = SimpleNamespace(isOpened=lambda: True) if frame is not None else None

    def read(self):
        return self._frame


class DeferredPrinterConfig:
    """Read existing settings only when the original probe worker needs them."""
    def __init__(self, path):
        self.path, self.value = Path(path), None

    def __getattr__(self, name):
        if self.value is None:
            from photobooth.printer_settings import load_printer_config
            self.value = load_printer_config(self.path)
        return getattr(self.value, name)


class V2HealthController(V1HealthController):
    """The original lock/thread/delivery algorithm is inherited without edits."""
    def __init__(self, owner, scheduler, root):
        self.owner, self.root, self.project_root = owner, scheduler, Path(root)
        self._health_probe_lock = threading.Lock()
        self._latest_health_snapshot = None
        self.ui = SimpleNamespace(ad_catalog=None, _health_last_tick=None)
        self._print_lock = threading.Lock()
        self._print_jobs_in_flight = set()

    @property
    def is_closing(self):
        return self.owner._closed

    def refresh(self, callback):
        app = self.owner
        frame = app.camera_device.read()  # Nonblocking fresh-frame mailbox, on UI thread.
        self.camera = CachedCamera(frame, getattr(app.camera_device, 'index', None))
        self.printer = SimpleNamespace(config=DeferredPrinterConfig(
            self.project_root/'data'/'printer_settings.json'))
        self.photos_root = self.project_root/'data'/'kiosk-v2-p3'/'photos'
        if not getattr(app, '_sandbox_enabled', False) and os.environ.get('PHOTOBOOTH_V2_STORAGE') == '2':
            from .photos import configured_workspace
            self.photos_root = configured_workspace(self.project_root).root
        if app._sandbox_jobs and app._sandbox_jobs.store:
            self.photos_root = app._sandbox_jobs.store.flow.path.parent/'photo-tests'/'photos'
        self.ui.ad_catalog = app.catalog
        self.ui._health_last_tick = app._operator_last_tick
        # Access is allowed only at idle or protected recovery, never during a send.
        self._print_jobs_in_flight = {'busy'} if app._photo_jobs and app._photo_jobs.busy else set()
        def observed(snapshot):
            if snapshot is not None:
                # A mailbox frame is the proven observation; don't claim a second
                # native handle inspection just to fit the v1 Camera interface.
                camera = HealthCheck('camera', READY if frame is not None else UNKNOWN,
                    'Frame terbaru kamera aktif tersedia; handle tidak dibuka ulang.' if frame is not None else
                    'Belum ada frame terbaru; koneksi atau output fisik belum dipastikan.')
                snapshot = replace(snapshot, checks=tuple(
                    camera if check.name == 'camera' else check for check in snapshot.checks))
            callback(snapshot)
        self._refresh_device_health(observed)
