"""FEAT-008 Stage A: read-only diagnostics for an operator-initiated health panel.

Checks are deliberately *not* scheduled here and never open a second camera,
print paper, upload data, delete photos, or restart the kiosk. A READY result
means that only the named observation passed; it is not a guarantee that an
ESC/POS print will complete or that a video codec will decode.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import os
import shutil
import socket
import sys
import time


READY = "ready"
WARNING = "warning"
UNAVAILABLE = "unavailable"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class HealthCheck:
    """One safe-to-display, non-secret check result."""

    name: str
    status: str
    message: str


@dataclass(frozen=True)
class HealthSnapshot:
    """Immutable set of observations, suitable for a future operator UI."""

    checked_at: str
    checks: tuple[HealthCheck, ...]

    def by_name(self, name: str) -> HealthCheck:
        return next(check for check in self.checks if check.name == name)


def check_camera(camera) -> HealthCheck:
    """Inspect the existing latest-frame mailbox; never acquire/open the USB camera.

    Camera.read() is nonblocking in photobooth.camera.Camera and returns None
    when its most recent frame has become stale. This is a point-in-time check.
    """
    if camera is None:
        return HealthCheck("camera", UNKNOWN, "Camera controller was not supplied.")
    capture = getattr(camera, "capture", None)
    if capture is None:
        return HealthCheck("camera", UNAVAILABLE, "Camera is not opened.")
    try:
        # isOpened does not grab any frames or reopen a busy Windows device.
        if not capture.isOpened():
            return HealthCheck("camera", UNAVAILABLE, "Camera handle is closed.")
        if camera.read() is None:
            return HealthCheck("camera", WARNING, "No fresh camera frame is available.")
    except Exception:
        return HealthCheck("camera", UNAVAILABLE, "Camera status could not be read.")
    return HealthCheck("camera", READY, "Camera handle and recent frame are available.")


def _windows_queue_probe(name: str) -> bool | None:
    """Open only a Windows spooler *handle*, never a document or print job."""
    try:
        import win32print
    except ImportError:
        return None
    handle = win32print.OpenPrinter(name)
    try:
        return True
    finally:
        win32print.ClosePrinter(handle)


def _network_dial(host: str, port: int, timeout: float):
    """Open a bounded TCP connection and return a socket for the caller to close."""
    return socket.create_connection((host, port), timeout=timeout)


def check_printer(
    config,
    *,
    dial=None,
    windows_queue_probe=None,
    platform: str | None = None,
    device_exists=None,
) -> HealthCheck:
    """Probe the saved printer routes without sending any ESC/POS payload.

    LAN and Wi-Fi are tested in the actual fallback order. Windows queue probes
    confirm spooler visibility only, not a physical connection or paper supply.
    USB device-path presence is similarly limited to a filesystem observation.
    """
    if config is None:
        return HealthCheck("printer", UNKNOWN, "Printer configuration was not supplied.")
    dial = dial or _network_dial
    windows_queue_probe = windows_queue_probe or _windows_queue_probe
    device_exists = device_exists or os.path.exists
    platform = sys.platform if platform is None else platform
    attempted = False

    for label, host_attr, port_attr in (
        ("LAN", "lan_host", "lan_port"),
        ("Wi-Fi", "wifi_host", "wifi_port"),
    ):
        host = getattr(config, host_attr, "").strip()
        if not host:
            continue
        attempted = True
        try:
            # No print bytes are sent. Limit time spent probing any one route.
            conn = dial(host, getattr(config, port_attr, 9100), 0.75)
            try:
                pass
            finally:
                conn.close()
            return HealthCheck("printer", READY, f"{label} TCP port accepted a connection; paper status is unknown.")
        except (OSError, TimeoutError, ValueError):
            continue

    queue_name = getattr(config, "windows_printer_name", "").strip()
    if platform.startswith("win") and queue_name:
        attempted = True
        try:
            result = windows_queue_probe(queue_name)
            if result is True:
                return HealthCheck("printer", READY, "Windows print queue is accessible; printer and paper status are unknown.")
        except (OSError, RuntimeError):
            pass

    # The default Unix path is irrelevant on Windows. Do not probe the USB
    # device directly; doing so could contend with the print transport.
    path = getattr(config, "usb_device_path", None)
    if not platform.startswith("win") and path:
        attempted = True
        try:
            if device_exists(path):
                return HealthCheck("printer", READY, "USB device path exists; printer and paper status are unknown.")
        except OSError:
            pass

    usb_ids = (getattr(config, "usb_vendor_id", None), getattr(config, "usb_product_id", None))
    if all(value is not None for value in usb_ids):
        return HealthCheck("printer", UNKNOWN, "USB IDs are configured, but USB presence was not safely verified.")

    if queue_name and not platform.startswith("win") and not attempted:
        return HealthCheck("printer", UNKNOWN, "Windows print queue cannot be probed on this platform.")
    if attempted:
        return HealthCheck("printer", WARNING, "Configured printer routes were not confirmed reachable.")
    return HealthCheck("printer", UNKNOWN, "No usable printer route could be inspected.")


def check_disk(
    photo_directory: str | Path | None,
    *,
    usage=None,
    minimum_free_bytes: int = 1024**3,
    minimum_free_fraction: float = 0.10,
) -> HealthCheck:
    """Check the volume containing photos, without creating/deleting files."""
    if photo_directory is None:
        return HealthCheck("disk", UNKNOWN, "Photo storage location was not supplied.")
    usage = usage or shutil.disk_usage
    try:
        # A fresh installation may not have created photos/ yet. Check its
        # closest existing ancestor on the same intended storage volume.
        path = Path(photo_directory)
        while not path.exists() and path != path.parent:
            path = path.parent
        volume = usage(path)
        free_bytes = volume.free
        total_bytes = volume.total
        if total_bytes <= 0:
            return HealthCheck("disk", UNKNOWN, "Disk capacity could not be determined.")
        percent = 100 * free_bytes / total_bytes
        if free_bytes < minimum_free_bytes or percent < 100 * minimum_free_fraction:
            return HealthCheck("disk", WARNING, f"Photo storage is low: {percent:.1f}% available.")
        return HealthCheck("disk", READY, f"Photo storage has {percent:.1f}% available.")
    except (OSError, ValueError, TypeError):
        return HealthCheck("disk", UNKNOWN, "Photo storage capacity could not be checked.")


def check_network(*, dial=None, host: str = "1.1.1.1", port: int = 443) -> HealthCheck:
    """Test a short TCP route; one endpoint cannot prove global internet status."""
    dial = dial or _network_dial
    try:
        conn = dial(host, port, 0.75)
        try:
            pass
        finally:
            conn.close()
    except (OSError, TimeoutError, ValueError):
        return HealthCheck("network", WARNING, "Connectivity probe failed; other network routes may still work.")
    return HealthCheck("network", READY, "Connectivity probe succeeded; cloud services were not checked.")


def check_media(catalog) -> HealthCheck:
    """Inspect the loaded offline-ad catalog and file bytes, never decode media.

    The existing AdCatalog remains the source of truth for playlists/schedules.
    Disabled/scheduled-out items are not made available by this check.
    """
    if catalog is None:
        return HealthCheck("media", UNKNOWN, "Advertising catalog was not supplied.")
    try:
        playlist = Path(catalog.path)
        if not playlist.is_file():
            return HealthCheck("media", WARNING, "Advertising playlist file is missing.")
        items = catalog.items
        if not items:
            return HealthCheck("media", WARNING, "No enabled advertising files were loaded.")
        missing = 0
        for item in items:
            paths = [item.path]
            if getattr(item, "poster", None) is not None:
                paths.append(item.poster)
            for path in paths:
                media = Path(path)
                if not media.is_file() or media.stat().st_size <= 0:
                    missing += 1
        if missing:
            return HealthCheck("media", WARNING, f"{missing} advertising asset(s) are missing or empty.")
        return HealthCheck("media", READY, f"{len(items)} advertising item(s) have local files; decoder not tested.")
    except (OSError, ValueError, TypeError, AttributeError):
        return HealthCheck("media", UNKNOWN, "Advertising assets could not be inspected.")


def check_heartbeat(
    last_tick: float | None,
    *,
    now: float | None = None,
    maximum_age: float = 5.0,
) -> HealthCheck:
    """Evaluate a future UI-owned monotonic heartbeat without scheduling one."""
    if last_tick is None:
        return HealthCheck("heartbeat", UNKNOWN, "Application heartbeat was not supplied.")
    now = time.monotonic() if now is None else now
    age = now - last_tick
    if age < 0:
        return HealthCheck("heartbeat", UNKNOWN, "Application heartbeat clock was reset.")
    if age > maximum_age:
        return HealthCheck("heartbeat", WARNING, "Application heartbeat is stale.")
    return HealthCheck("heartbeat", READY, "Application heartbeat was recently updated.")


def collect_health_snapshot(
    *,
    camera=None,
    printer_config=None,
    photo_directory=None,
    ad_catalog=None,
    last_heartbeat=None,
) -> HealthSnapshot:
    """Run one opt-in observation pass (never scheduled during kiosk startup).

    Network and LAN reachability checks initiate short TCP handshakes only.
    A future GUI must run this function outside the Kivy rendering thread.
    """
    checks = (
        check_camera(camera),
        check_printer(printer_config),
        check_disk(photo_directory),
        check_network(),
        check_media(ad_catalog),
        check_heartbeat(last_heartbeat),
    )
    return HealthSnapshot(
        checked_at=datetime.now(timezone.utc).isoformat(),
        checks=checks,
    )
