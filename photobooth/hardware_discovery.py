"""FEAT-008 B.2: safe, read-only discovery of *potential* local hardware.

Discovery finds OS device nodes and named print queues. A discovered node/queue
does not prove permission, frame capture, motor readiness or paper status.
Windows camera enumeration is deliberately NOT attempted by opening index 0..N;
doing so would contend with the active customer camera.
"""

from __future__ import annotations

from pathlib import Path
import subprocess

from photobooth.hardware_adapters import DeviceDescriptor, platform_family


def _enumerate_windows_queues(spooler=None) -> tuple[str, ...]:
    """List local/connected spooler queues without opening or sending print jobs."""
    try:
        if spooler is None:
            import win32print as spooler
        flags = spooler.PRINTER_ENUM_LOCAL | spooler.PRINTER_ENUM_CONNECTIONS
        entries = spooler.EnumPrinters(flags, None, 2)
        names = [item.get("pPrinterName", "") for item in entries]
        return tuple(sorted({name.strip() for name in names if isinstance(name, str) and name.strip()}))
    except (ImportError, OSError, RuntimeError, AttributeError, TypeError):
        return ()


def _linux_video_devices(*, root: Path = Path("/dev")) -> tuple[DeviceDescriptor, ...]:
    """Prefer stable v4l/by-id aliases; then show unaliased volatile video nodes."""
    stable = {}
    by_id = root / "v4l" / "by-id"
    try:
        entries = sorted(by_id.iterdir(), key=lambda p: p.name)
    except OSError:
        entries = ()
    for alias in entries:
        try:
            if not alias.is_symlink() or not alias.exists():
                continue
            target = alias.resolve()
            if not target.name.startswith("video"):
                continue
            stable[str(target)] = DeviceDescriptor(
                "camera", f"v4l:by-id:{alias.name}", alias.name,
                "v4l2", "linux", "udev-by-id", "node-detected",
                ("node-presence",),
                "Udev alias identifies a candidate node; no frames were acquired.",
            )
        except OSError:
            continue
    found = list(stable.values())
    try:
        nodes = sorted(root.glob("video*"), key=lambda p: p.name)
    except OSError:
        nodes = ()
    for node in nodes:
        try:
            if not node.is_char_device() or str(node.resolve()) in stable:
                continue
            found.append(DeviceDescriptor(
                "camera", f"v4l:node:{node.name}", node.name,
                "v4l2", "linux", "ephemeral", "node-detected",
                ("node-presence",),
                "Device path is unstable and does not prove access or camera capture.",
            ))
        except OSError:
            continue
    return tuple(found)


def _linux_usb_printers(*, root: Path = Path("/dev")) -> tuple[DeviceDescriptor, ...]:
    found = []
    try:
        nodes = sorted((root / "usb").glob("lp*"), key=lambda p: p.name)
    except OSError:
        nodes = ()
    for node in nodes:
        try:
            if not node.is_char_device():
                continue
            found.append(DeviceDescriptor(
                "printer", f"linux-usb:{node.name}", f"USB printer node {node.name}",
                "linux-usb-node", "linux", "ephemeral", "node-detected",
                ("node-presence",),
                "Node presence does not prove a connected ESC/POS printer or paper.",
            ))
        except OSError:
            continue
    return tuple(found)


def _linux_cups_queues(*, runner=None) -> tuple[str, ...]:
    """lpstat -e lists names only; it does not submit a job or change queues."""
    if runner is None:
        runner = subprocess.run
    try:
        proc = runner(
            ["lpstat", "-e"],
            capture_output=True, text=True, timeout=1.5, check=False,
        )
        if proc.returncode:
            return ()
        return tuple(sorted({name.strip() for name in proc.stdout.splitlines()
                             if name.strip()}))
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        return ()


def discover_local_devices(
    *,
    platform: str | None = None,
    root: Path = Path("/dev"),
    spooler=None,
    cups_runner=None,
    environ=None,
) -> tuple[DeviceDescriptor, ...]:
    """Find possible hardware on operator request; never select or open it."""
    family = platform_family(platform, environ)
    if family == "windows":
        return tuple(DeviceDescriptor(
            "printer", "win-queue:" + name, f"Print queue: {name}",
            "windows-spooler", family, "queue-name", "queue-detected",
            ("spooler-presence",),
            "Spooler enumeration does not prove the physical printer is online.",
        ) for name in _enumerate_windows_queues(spooler))
    if family == "linux":
        cups = tuple(DeviceDescriptor(
            "printer", "cups-queue:" + name, f"CUPS queue: {name}",
            "cups", family, "queue-name", "queue-detected",
            ("spooler-presence",),
            "CUPS queue existence does not prove USB/network/paper readiness.",
        ) for name in _linux_cups_queues(runner=cups_runner))
        return (*_linux_video_devices(root=root),
                *_linux_usb_printers(root=root), *cups)
    # Android uses the native CameraManager/USBManager to enumerate supported
    # hardware, not desktop Python endpoints. Until a JNI adapter exists,
    # absence of results must not be interpreted as 'no devices'.
    return ()
