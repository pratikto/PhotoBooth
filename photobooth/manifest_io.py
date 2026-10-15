# PhotoBooth source file
# Shared locking and atomic JSON-writing helpers for transaction manifests.

"""Atomic local manifest writes shared by the UI thread and Drive worker."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import threading


_LOCKS_GUARD = threading.Lock()
_PATH_LOCKS: dict[str, threading.RLock] = {}


def manifest_lock(path: Path) -> threading.RLock:
    # Return a per-manifest reentrant lock so the GUI and background sync thread cannot write the same
    # JSON record at the same time.
    key = str(Path(path).resolve())
    with _LOCKS_GUARD:
        lock = _PATH_LOCKS.get(key)
        if lock is None:
            lock = threading.RLock()
            _PATH_LOCKS[key] = lock
        return lock


def write_json_atomic(path: Path, payload: dict) -> None:
    # Serialize a manifest to a temporary file and replace the destination only after the complete
    # JSON has been written.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
