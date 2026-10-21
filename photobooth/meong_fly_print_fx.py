"""FEAT-021: a single, camera-anchored instant-print animation.

All coordinates are TOP-origin 360x720 logical UI pixels. The emitter is pure
Python (no Kivy or camera/print APIs). Paper is attached to the slot while it
feeds, detaches at the current slot, and then falls from that same spot.
Never spawn photo confetti at arbitrary screen coordinates.
"""

from dataclasses import dataclass
from math import sin, cos, radians


@dataclass(frozen=True)
class PrintedPhotoPose:
    serial: int
    x: float
    y: float
    width: float
    height: float
    reveal: float   # 0..1; progressive printing while attached
    opacity: float  # 0..1; fade before leaving the designated play zone
    attached: bool
    angle: float = 0.0


@dataclass
class _Sheet:
    serial: int
    born_at: float
    detach_x: float | None = None
    detach_y: float | None = None
    detached_at: float | None = None
    detach_angle: float = 0.0


class InstantPhotoEmitter:
    """At most two sheets: feed from camera, release, gravity, then disappear."""

    FEED_SECONDS = 0.60
    HOLD_SECONDS = 0.18
    INITIAL_DELAY = 0.62
    INTERVAL = 2.15
    MAX_SHEETS = 2
    GRAVITY = 115.0
    INITIAL_FALL_SPEED = 19.0

    def __init__(self, size=(20.0, 26.0)):
        self.width, self.height = map(float, size)
        self.reset()

    def reset(self):
        self.elapsed = 0.0
        self.next_print_at = self.INITIAL_DELAY
        self._serial = 0
        self._sheets: list[_Sheet] = []
        self._slot = None
        self._bottom = 720.0
        self._angle = 0.0

    def update(self, dt, slot, bottom, paused=False, angle=0.0):
        """Advance the visual clock only in an active (unpaused) scene.

        `slot`: x/y beneath the camera's actual print outlet, in logical pixels.
        The detached sheet position never depends on later camera movement.
        """
        if paused:
            return
        previous_slot, previous_angle = self._slot, self._angle
        self.elapsed += max(0.0, min(float(dt), 0.12))
        self._slot = tuple(map(float, slot))
        self._bottom = float(bottom)
        self._angle = float(angle)

        for sheet in self._sheets:
            if (sheet.detach_x is None and
                    self.elapsed - sheet.born_at >= self.FEED_SECONDS + self.HOLD_SECONDS):
                sheet.detach_x = previous_slot[0] - self.width / 2
                sheet.detach_y = previous_slot[1]
                sheet.detached_at = self.elapsed
                sheet.detach_angle = previous_angle

        # Prune spent sheets even when FPS is temporarily low.
        self._sheets = [s for s in self._sheets
                        if self._pose(s) is not None]

        if (self.elapsed >= self.next_print_at
                and len(self._sheets) < self.MAX_SHEETS
                and self._slot[1] + self.height + 6 < self._bottom):
            self._sheets.append(_Sheet(self._serial, self.elapsed))
            self._serial += 1
            self.next_print_at = self.elapsed + self.INTERVAL

    def _pose(self, sheet):
        age = self.elapsed - sheet.born_at
        if self._slot is None:
            return None
        if sheet.detach_x is None:
            # The camera is moving: paper is physically attached until release.
            reveal = max(0.02, min(1.0, age / self.FEED_SECONDS))
            x = self._slot[0] - self.width / 2
            y = self._slot[1]
            detached = False
            angle = self._angle
        else:
            fall = max(0.0, self.elapsed - sheet.detached_at)
            # Small pendulum-like sway, not random horizontal movement.
            x = sheet.detach_x + sin(fall * 2.1 + sheet.serial * 0.4) * min(4.0, fall * 3.0)
            y = sheet.detach_y + self.INITIAL_FALL_SPEED * fall + 0.5 * self.GRAVITY * fall * fall
            reveal = 1.0
            detached = True
            angle = sheet.detach_angle + sin(fall * 2.1) * min(3.0, fall * 2.0)

        corners = paper_corners(x, y, self.width, self.height, angle)
        lower = max(p[1] for p in corners)
        if lower >= self._bottom:
            return None
        if min(p[0] for p in corners) < 0 or max(p[0] for p in corners) > 360:
            return None
        # Fade only as it nears the lower boundary; the sheet stays tangible.
        remaining = self._bottom - lower
        opacity = min(1.0, max(0.0, remaining / 22.0))
        return PrintedPhotoPose(sheet.serial, x, y, self.width, self.height,
                                reveal, opacity, not detached, angle)

    def poses(self):
        """Return immutable snapshots suitable for a cached Kivy texture."""
        return tuple(pose for sheet in self._sheets
                     if (pose := self._pose(sheet)) is not None)


def paper_corners(x, y, width, height, angle=0):
    """Top-left, bottom-left, bottom-right, top-right around the outlet."""
    a = radians(angle)
    cx = x + width/2
    return tuple((cx + dx*cos(a) - dy*sin(a),
                  y + dx*sin(a) + dy*cos(a))
                 for dx, dy in ((-width/2,0), (-width/2,height),
                                (width/2,height), (width/2,0)))
