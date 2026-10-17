"""Offline advertising playlists and honest, local playback measurements.

Configuration contains local media paths, not executable Python or remote URLs.
The idle and payment placements are independent. Dates and daily hours use the
configured venue timezone; an invalid item is skipped without stopping a kiosk.
Events measure displayed playback time, never people or verified ad attention.
No camera pixels or biometric identifiers are written by this module.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time, timezone
import json
import logging
import math
import os
from pathlib import Path
from zoneinfo import ZoneInfo


LOG = logging.getLogger(__name__)
BUNDLED_CONFIG = Path(__file__).resolve().parent / "assets" / "ads" / "playlist.json"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".mkv", ".mov", ".webm"}


def bounded_seconds(value, default, low=1, high=86400):
    """Keep operator input finite and bounded, including JSON NaN/Infinity."""
    try:
        number = float(value)
        return min(high, max(low, number)) if math.isfinite(number) else default
    except (ValueError, TypeError, OverflowError):
        return default


@dataclass(frozen=True)
class KioskTiming:
    """Customer-facing timers; tests can advance a monotonic clock directly."""

    face_hold: float = 5
    offer_timeout: float = 15
    face_cooldown: float = 45
    landing_idle: float = 180
    idle_warning: float = 10
    payment_offer_after: float = 60
    payment_validity: float = 900

    @classmethod
    def from_config(cls, payload):
        defaults = cls()
        values = payload if isinstance(payload, dict) else {}
        return cls(**{key: bounded_seconds(values.get(key), getattr(defaults, key))
                      for key in defaults.__dataclass_fields__})


@dataclass(frozen=True)
class Advertisement:
    """One scheduled local creative; aspect ratio is always preserved by UI."""

    ad_id: str
    title: str
    path: Path
    placements: tuple
    seconds: float = 8
    poster: Path | None = None
    start: datetime | None = None
    end: datetime | None = None
    hours: tuple | None = None

    @property
    def video(self):
        return self.path.suffix.lower() in VIDEO_SUFFIXES

    def eligible(self, placement, now):
        """End timestamps are exclusive; overnight daily schedules are valid."""
        if placement not in self.placements or not self.path.is_file():
            return False
        if self.start is not None and now < self.start:
            return False
        if self.end is not None and now >= self.end:
            return False
        if self.hours is not None:
            start, end = self.hours
            current = now.time().replace(tzinfo=None)
            if start < end and not start <= current < end:
                return False
            if start > end and not (current >= start or current < end):
                return False
        return True


class AdCatalog:
    """Load a small playlist once per page, safely skipping broken entries.

    PHOTOBOOTH_AD_CONFIG can point at an operator-owned JSON file. Relative
    asset paths resolve beside that file, so it can live outside the checkout.
    The shipped playlist works without accounts, downloads, or a network.
    """

    def __init__(self, path=None):
        self.path = Path(path or os.environ.get("PHOTOBOOTH_AD_CONFIG", BUNDLED_CONFIG))
        self.items = []
        self.timing = KioskTiming()
        self.zone = ZoneInfo("Asia/Jakarta")
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get('ads', []), list):
                raise ValueError('A playlist must be an object containing an ads array.')
            self.zone = ZoneInfo(payload.get("timezone", "Asia/Jakarta"))
            self.timing = KioskTiming.from_config(payload.get("timing"))
            identifiers = set()
            for raw in payload.get("ads", []):
                try:
                    if not isinstance(raw, dict):
                        raise ValueError('Each advertising item must be an object.')
                    if not raw.get("enabled", True):
                        continue
                    identifier = str(raw["id"])
                    if not identifier or identifier in identifiers:
                        raise ValueError('Advertising IDs must be nonempty and unique.')
                    media = (self.path.parent / raw["file"]).resolve()
                    if media.suffix.lower() not in IMAGE_SUFFIXES | VIDEO_SUFFIXES:
                        continue
                    def stamp(key):
                        value = raw.get(key)
                        parsed = datetime.fromisoformat(value) if value else None
                        return parsed.replace(tzinfo=self.zone) if parsed and not parsed.tzinfo else parsed
                    hours = raw.get("hours")
                    if hours is not None:
                        if not isinstance(hours, list) or len(hours) != 2:
                            raise ValueError('Daily hours require a start and end.')
                        hours = tuple(time.fromisoformat(x) for x in hours)
                        if any(value.tzinfo is not None for value in hours):
                            raise ValueError('Daily hours use the venue timezone.')
                    self.items.append(Advertisement(
                        ad_id=identifier, title=str(raw.get("title", identifier)), path=media,
                        placements=tuple(x for x in raw.get("placements", ["idle"])
                                         if x in {"idle", "payment"}),
                        seconds=bounded_seconds(raw.get("seconds"), 8),
                        poster=(self.path.parent / raw["poster"]).resolve() if raw.get("poster") else None,
                        start=stamp("start"), end=stamp("end"),
                        hours=hours,
                    ))
                    identifiers.add(identifier)
                except (KeyError, TypeError, ValueError, OSError):
                    LOG.warning("Skipping invalid advertising item in %s", self.path)
        except (OSError, ValueError, TypeError, AttributeError, KeyError):
            LOG.warning("Advertising configuration unavailable; showing Meong poster", exc_info=True)

    def available(self, placement, now=None):
        now = now or datetime.now(self.zone)
        return [item for item in self.items if item.eligible(placement, now)]


class AdEventLog:
    """Append small anonymous events; a full/read-only disk cannot break checkout."""

    def __init__(self, path):
        self.path = Path(path)

    def write(self, event, **details):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as output:
                output.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                                         "event": event, **details}, allow_nan=False) + "\n")
        except (OSError, ValueError):
            LOG.warning("Advertising event could not be saved")


def summarize_events(path):
    """Aggregate actual displayed runs, partial runs, and entry-button actions."""
    rows = defaultdict(lambda: {"plays": 0, "completed": 0, "displayed_seconds": 0.0, "photo_entries": 0})
    try:
        with Path(path).open(encoding="utf-8") as source:
            for line in source:
                try:
                    event = json.loads(line)
                    if event["event"] == "playback":
                        seconds = float(event.get("seconds", 0))
                        if not math.isfinite(seconds) or seconds <= 0:
                            continue
                        row = rows[(event["ad_id"], event.get("placement", "idle"))]
                        row["plays"] += 1
                        row["completed"] += bool(event.get("completed"))
                        row["displayed_seconds"] += seconds
                    elif event["event"] == "photo_entry":
                        row = rows[(event["ad_id"], event.get("placement", "idle"))]
                        row["photo_entries"] += 1
                except (ValueError, KeyError, TypeError):
                    continue
    except FileNotFoundError:
        pass
    return [{"ad_id": key[0], "placement": key[1], **value} for key, value in sorted(rows.items())]
