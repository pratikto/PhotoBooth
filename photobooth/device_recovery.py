"""FEAT-008 B.3: read-only, fail-closed device presence transitions.

The OS candidate inventory is not evidence of an operational camera or paper.
No camera/print handle is opened, changed, or recovered by this module.
"""
from dataclasses import dataclass
from photobooth.device_selection import DeviceSelection, DeviceSelectionError, _validate
from photobooth.hardware_adapters import platform_family


@dataclass(frozen=True)
class SelectionObservation:
    kind: str
    target: str
    state: str  # unselected, unsupported, unknown, missing, candidate, returned
    message: str


def selected_device_observation(selection: DeviceSelection, kind: str, *,
                                platform: str, detected=(), previous=None,
                                discovery_complete: bool = False) -> SelectionObservation:
    """Evaluate an explicit selection from read-only OS candidates.

    Discovery failure is UNKNOWN, not missing. Reappearance requires an
    explicit subsequent enumeration of the *same* identity, never a fallback.
    """
    _validate(selection)
    if kind not in ("camera", "printer"):
        raise DeviceSelectionError("Unknown device kind.")
    family = platform_family(platform, environ={})
    backend = getattr(selection, kind + "_kind")
    target = getattr(selection, kind + "_value")
    if not backend:
        return SelectionObservation(kind, "", "unselected", "Existing device configuration applies.")
    if backend == "windows-spooler" and family != "windows":
        return SelectionObservation(kind, target, "unsupported", "Saved printer requires Windows.")
    if backend == "linux-v4l-by-id" and family != "linux":
        return SelectionObservation(kind, target, "unsupported", "Saved camera requires Linux.")
    if backend == "opencv-index":
        # Camera indices have no stable enumeration identity in this project.
        # An index must be checked by the existing camera open/frame route.
        if family != "windows":
            return SelectionObservation(kind, target, "unsupported", "Saved index requires Windows.")
        return SelectionObservation(kind, target, "unknown", "Camera index requires a live frame test.")
    if not discovery_complete:
        return SelectionObservation(kind, target, "unknown", "OS device discovery not verified.")
    names = set()
    for device in detected:
        if getattr(device, "kind", None) != kind:
            continue
        if getattr(device, "presence", None) not in ("queue-detected", "node-detected"):
            continue
        names.add(str(getattr(device, "name", "")))
        names.add(str(getattr(device, "device_id", "")))
    found = target in names or (backend == "linux-v4l-by-id" and
                               any(name.endswith("/" + target) for name in names))
    if not found:
        return SelectionObservation(kind, target, "missing",
                                    "Selected device not detected; do not switch to another.")
    was_missing = (previous is not None and previous.kind == kind
                   and previous.target == target and previous.state == "missing")
    return SelectionObservation(kind, target, "returned" if was_missing else "candidate",
                                "Same selected identity detected; physical operation unverified.")
