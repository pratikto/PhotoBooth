"""FEAT-008 B.1: capability-aware inventory for heterogeneous booth hardware.

Device descriptions are informational: configured != detected != operational.
No camera opening, print submission, cloud request or device enumeration on import.
Backend selection must never silently switch a customer-facing camera or printer.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Mapping


@dataclass(frozen=True)
class DeviceDescriptor:
    kind: str
    device_id: str
    name: str
    transport: str
    platform: str
    identity_quality: str
    presence: str
    capabilities: tuple[str, ...]
    note: str


def platform_family(platform: str | None = None, environ: Mapping[str, str] | None = None) -> str:
    """Detect runtime family; Android's Python often reports 'linux'."""
    raw = (sys.platform if platform is None else platform).lower()
    env = os.environ if environ is None else environ
    if raw.startswith("android") or (
        raw.startswith("linux")
        and any(env.get(key) for key in ("ANDROID_ARGUMENT", "ANDROID_APP_PATH"))
    ):
        return "android"
    if raw.startswith("win"):
        return "windows"
    if raw.startswith("linux"):
        return "linux"
    return "other"


class PlatformHardwareAdapter:
    """Safe read-only device descriptions for the currently selected backend."""

    family = "other"

    def describe_camera(self, camera) -> DeviceDescriptor:
        index = getattr(camera, "camera_index", None)
        capture = getattr(camera, "capture", None)
        name = f"Configured camera index {index}" if index is not None else "Camera index unknown"
        return DeviceDescriptor(
            "camera", "camera:active", name, "active-capture", self.family,
            "ephemeral", "active-handle" if capture is not None else "not-open",
            ("cached-frame",) if capture is not None else (),
            "Index/active handle is not a permanent physical camera identity.",
        )

    def describe_printer(self, config) -> tuple[DeviceDescriptor, ...]:
        if config is None:
            return ()
        found = []
        for route, key in (("lan", "lan_host"), ("wifi", "wifi_host")):
            if getattr(config, key, "").strip():
                found.append(DeviceDescriptor(
                    "printer", f"printer:{route}", f"Configured {route.upper()} printer",
                    route, self.family, "configuration-only", "configured",
                    ("tcp-reachability",),
                    "Network address is not proof of the physical printer or paper state.",
                ))
        name = getattr(config, "windows_printer_name", "").strip()
        if name:
            found.append(DeviceDescriptor(
                "printer", "printer:windows-queue", f"Windows queue: {name}",
                "windows-spooler", self.family, "queue-name", "configured",
                ("spooler-presence",) if self.family == "windows" else (),
                "A Windows queue is not a verified physical printer identity.",
            ))
        if self.family == "linux":
            path = getattr(config, "usb_device_path", None)
            if path:
                found.append(DeviceDescriptor(
                    "printer", "printer:usb-path", "Configured Linux USB printer path",
                    "linux-usb-node", self.family, "ephemeral", "configured",
                    ("device-node-presence",),
                    "USB device node may change after reconnect; not paper status.",
                ))
        if getattr(config, "usb_vendor_id", None) is not None and getattr(config, "usb_product_id", None) is not None:
            found.append(DeviceDescriptor(
                "printer", "printer:usb-vidpid", "Configured ESC/POS USB IDs",
                "usb-id", self.family, "model-only", "configured", (),
                "Vendor/product ID can identify a model, not an individual device.",
            ))
        return tuple(found)

    def inventory(self, camera=None, printer_config=None) -> tuple[DeviceDescriptor, ...]:
        return (self.describe_camera(camera), *self.describe_printer(printer_config))


class WindowsHardwareAdapter(PlatformHardwareAdapter):
    family = "windows"


class LinuxHardwareAdapter(PlatformHardwareAdapter):
    family = "linux"


class AndroidHardwareAdapter(PlatformHardwareAdapter):
    family = "android"

    def describe_camera(self, camera) -> DeviceDescriptor:
        return DeviceDescriptor(
            "camera", "camera:android-pending", "Android camera bridge not installed",
            "camera2-pending", self.family, "unknown", "unsupported", (),
            "Kivy/OpenCV desktop capture is not an Android Camera2 implementation.",
        )

    def describe_printer(self, config) -> tuple[DeviceDescriptor, ...]:
        return (DeviceDescriptor(
            "printer", "printer:android-pending", "Android printer bridge not installed",
            "android-usb-or-network-pending", self.family, "unknown", "unsupported", (),
            "Android USB permissions and vendor/transport drivers require a native bridge.",
        ),)


class UnsupportedHardwareAdapter(PlatformHardwareAdapter):
    family = "other"


def adapter_for(platform: str | None = None, environ: Mapping[str, str] | None = None) -> PlatformHardwareAdapter:
    family = platform_family(platform, environ)
    return {
        "windows": WindowsHardwareAdapter,
        "linux": LinuxHardwareAdapter,
        "android": AndroidHardwareAdapter,
        "other": UnsupportedHardwareAdapter,
    }[family]()


def configured_inventory(camera=None, printer_config=None, *, platform: str | None = None,
                         environ: Mapping[str, str] | None = None) -> tuple[DeviceDescriptor, ...]:
    """List configured routes without performing an invasive bus scan."""
    return adapter_for(platform, environ).inventory(camera, printer_config)
