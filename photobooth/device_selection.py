"""FEAT-008 B.2.1: operator-staged camera/printer startup selection.

No bus scans, camera handles, print bytes or imports from Kivy in this module.
Only explicit choices are persisted. An incompatible/missing selected device
MUST NOT silently fall back to a different customer-facing device.

The settings file lives per kiosk under data/device_selection.json. Printer
selection is a Windows spooler queue; Linux/CUPS and Android are intentionally
not offered as printable backends until their runtime drivers are validated.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
import os
from pathlib import Path
import re
import tempfile

from photobooth.hardware_adapters import platform_family


class DeviceSelectionError(ValueError):
    """Invalid or incompatible operator-selected device."""


@dataclass(frozen=True)
class DeviceSelection:
    camera_kind: str = ""  # "" = existing PHOTOBOOTH_CAMERA_INDEX
    camera_value: str = ""
    printer_kind: str = ""  # "" = existing printer_settings.json configuration
    printer_value: str = ""


def _validate(selection: DeviceSelection) -> DeviceSelection:
    if not isinstance(selection, DeviceSelection):
        raise DeviceSelectionError("Invalid device selection type.")
    if any(type(value) is not str for value in (
            selection.camera_kind, selection.camera_value,
            selection.printer_kind, selection.printer_value)):
        raise DeviceSelectionError("Device selections must be strings.")
    if selection.camera_kind not in ("", "opencv-index", "linux-v4l-by-id"):
        raise DeviceSelectionError("Unsupported camera selection backend.")
    if selection.printer_kind not in ("", "windows-spooler"):
        raise DeviceSelectionError("Unsupported printer selection backend.")
    if selection.camera_kind == "":
        if selection.camera_value:
            raise DeviceSelectionError("Camera value supplied without a backend.")
    elif selection.camera_kind == "opencv-index":
        if not re.fullmatch(r"(?:[0-9]|1[0-5])", selection.camera_value):
            raise DeviceSelectionError("Camera index must be an integer from 0 to 15.")
    else:
        value = selection.camera_value
        if (not isinstance(value, str) or not 1 <= len(value) <= 180
                or value in (".", "..")
                or not re.fullmatch(r"[A-Za-z0-9_.-]+", value)
                or not value.startswith(("usb-", "pci-", "platform-"))):
            raise DeviceSelectionError("Invalid V4L stable camera alias.")
    if selection.printer_kind == "":
        if selection.printer_value:
            raise DeviceSelectionError("Printer value supplied without a backend.")
    else:
        name = selection.printer_value
        if (not isinstance(name, str) or not name.strip()
                or name != name.strip() or len(name) > 255
                or any(ord(char) < 32 for char in name)):
            raise DeviceSelectionError("Invalid Windows printer queue name.")
    return selection


def load_device_selection(path: str | Path) -> DeviceSelection:
    """Read a strict, versioned per-machine selection; errors are explicit."""
    path = Path(path)
    if not path.exists():
        return DeviceSelection()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or raw.get("version") != 1:
            raise DeviceSelectionError("Unsupported device selection file version.")
        if set(raw) != {"version", "camera_kind", "camera_value", "printer_kind", "printer_value"}:
            raise DeviceSelectionError("Unexpected fields in device selection.")
        if any(not isinstance(raw[key], str) for key in (
                "camera_kind", "camera_value", "printer_kind", "printer_value")):
            raise DeviceSelectionError("Device selection fields must be text.")
        return _validate(DeviceSelection(
            camera_kind=raw["camera_kind"],
            camera_value=raw["camera_value"],
            printer_kind=raw["printer_kind"],
            printer_value=raw["printer_value"],
        ))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DeviceSelectionError("Device selection file cannot be read.") from error


def save_device_selection(path: str | Path, selection: DeviceSelection) -> None:
    """Write config atomically; never mutate active Camera/ThermalPrinter."""
    selection = _validate(selection)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            tmp = Path(handle.name)
            json.dump({
                "version": 1, "camera_kind": selection.camera_kind,
                "camera_value": selection.camera_value,
                "printer_kind": selection.printer_kind,
                "printer_value": selection.printer_value,
            }, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def stage_selection(
    current: DeviceSelection, *, camera: tuple[str, str] | None = None,
    printer: tuple[str, str] | None = None,
) -> DeviceSelection:
    """Modify only explicitly supplied target(s), preserving other choices."""
    selection = _validate(current)
    if camera is not None:
        selection = replace(selection, camera_kind=camera[0], camera_value=camera[1])
    if printer is not None:
        selection = replace(selection, printer_kind=printer[0], printer_value=printer[1])
    return _validate(selection)


def camera_startup_source(
    selection: DeviceSelection, fallback_index: int, *,
    platform: str | None = None, aliases_root: Path = Path("/dev/v4l/by-id"),
):
    """Resolve chosen camera at process startup; no fallback when target selected.

    Does not open it. Camera.open() owns the first and only VideoCapture.
    """
    _validate(selection)
    family = platform_family(platform)
    if not selection.camera_kind:
        return fallback_index
    if selection.camera_kind == "opencv-index":
        if family not in ("windows", "linux"):
            raise DeviceSelectionError("Selected OpenCV index is unsupported on this OS.")
        return int(selection.camera_value)
    if family != "linux":
        raise DeviceSelectionError("Selected V4L camera needs Linux.")
    alias = aliases_root / selection.camera_value
    # Never follow operator input paths outside the fixed V4L alias directory.
    # The alias may disappear after reboot: fail closed, not camera index 0.
    try:
        if not alias.is_symlink() or not alias.exists() or not alias.resolve().name.startswith("video"):
            raise DeviceSelectionError("Selected V4L camera is missing; no fallback permitted.")
    except (OSError, RuntimeError) as error:
        raise DeviceSelectionError("Selected V4L camera cannot be resolved.") from error
    return str(alias)


def printer_startup_config(selection: DeviceSelection, existing_config, *,
                           platform: str | None = None):
    """Apply selected queue to an *in-memory* config only at startup.

    The legacy saved settings remain untouched and are still the fallback
    when no explicit queue selection exists. No print data is sent.
    """
    _validate(selection)
    if not selection.printer_kind:
        return existing_config
    if platform_family(platform) != "windows":
        raise DeviceSelectionError("Selected Windows queue needs Windows.")
    return replace(
        existing_config, lan_host="", wifi_host="",
        windows_printer_name=selection.printer_value,
        usb_vendor_id=None, usb_product_id=None,
    )
