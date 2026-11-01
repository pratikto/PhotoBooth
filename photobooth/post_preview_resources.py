"""Bounded private staging checks; configurable nonproduction defaults.

Resource exhaustion holds the original draft. It never deletes customer media,
releases worker ownership, starts delivery, or cuts off an active visit by time.
"""
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import tempfile

from photobooth.booth_storage import checked_path
from photobooth.post_preview_store import DraftHeld


@dataclass(frozen=True)
class PrivateCapturePolicy:
    min_free_bytes: int = 256*1024*1024
    max_draft_bytes: int = 512*1024*1024
    max_photo_pixels: int = 40_000_000
    max_entries: int = 4096

    def __post_init__(self):
        for name in ('min_free_bytes', 'max_draft_bytes', 'max_photo_pixels', 'max_entries'):
            value = getattr(self, name)
            if type(value) is not int or value < (0 if name == 'min_free_bytes' else 1):
                raise ValueError('Private capture resource limits must be bounded integers')
        if self.max_photo_pixels > 40_000_000:
            raise ValueError('Image limit cannot exceed original decoder safety bound')

    def inspect(self, root, *, image=None, probe=False):
        root = checked_path(Path(root))
        anticipated = 0
        if image is not None:
            width, height = image.size
            if (type(width) is not int or type(height) is not int or width < 1 or height < 1
                    or width*height > self.max_photo_pixels):
                raise DraftHeld('Private camera frame exceeds safe image bounds')
            # Reserve decoded RGB + encoder workspace before starting file I/O.
            anticipated = width*height*4
        parent = root
        while not parent.exists():
            parent = parent.parent
        if not parent.is_dir():
            raise DraftHeld('Private staging requires a directory')
        if shutil.disk_usage(parent).free < self.min_free_bytes + anticipated:
            raise DraftHeld('Private staging free-space reserve unavailable')
        total = count = 0
        if root.exists():
            pending = [root]
            while pending:
                directory = pending.pop()
                with os.scandir(directory) as entries:
                    for entry in entries:
                        count += 1
                        if count > self.max_entries:
                            raise DraftHeld('Private staging entry limit reached')
                        path = checked_path(entry.path)
                        if path.is_dir():
                            pending.append(path)
                        elif path.is_file():
                            total += path.stat().st_size
                            if total + anticipated > self.max_draft_bytes:
                                raise DraftHeld('Private staging byte limit reached')
                        else:
                            raise DraftHeld('Unexpected private staging object')
        if total + anticipated > self.max_draft_bytes:
            raise DraftHeld('Private staging byte limit reached')
        if probe:
            root.mkdir(parents=True, exist_ok=True)
            descriptor, path = tempfile.mkstemp(prefix='.durability-probe-', dir=root)
            try:
                with os.fdopen(descriptor, 'wb') as stream:
                    stream.write(b'meong-private-staging-probe')
                    stream.flush()
                    os.fsync(stream.fileno())
            finally:
                # Only this freshly created probe; never remove a saved frame.
                Path(path).unlink(missing_ok=True)
        return {'private_bytes': total, 'entries': count, 'resource_ready': True}
