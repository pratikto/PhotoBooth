"""Optional offline portrait background replacement for FEAT-021.

Only the three accepted still photos are segmented, never live camera frames.
The model must be installed into rembg's local cache by an operator beforehand:
a customer-facing kiosk MUST NOT download a large model or upload photographs
to a third-party service at runtime. Imports are lazy so ordinary boot/capture,
printer comparison tools, and CI work without rembg installed.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import threading
from typing import Callable, Mapping, Sequence

from PIL import Image, ImageOps


MODEL_NAME = "birefnet-portrait"
MODEL_FILE = "birefnet-portrait.onnx"
ORIGINAL = "original"
CLEAN_STUDIO = "clean-studio"
BACKGROUND_STYLES = (ORIGINAL, CLEAN_STUDIO)
# Near-white avoids grey halo artifacts in prints while retaining bright studio
# backgrounds in downloadable color originals. Floyd is still applied only by
# the pre-existing thermal printer processing pipeline.
STUDIO_COLOR = (248, 248, 246)


class BackgroundProcessingError(RuntimeError):
    """A recoverable AI failure: use all three unchanged original photographs."""


def cached_model_path(
    environ: Mapping[str, str] | None = None, user_home: Path | None = None,
) -> Path | None:
    """Find a pre-seeded BiRefNet portrait model without touching the network.

    rembg 2.0.84 uses <home>/models/<model>/<model>.onnx. Older versions keep
    downloaded ONNX files at ~/.u2net/<model>.onnx, which rembg still reads.
    Respect the explicitly configured U2NET_HOME/REMBG_HOME/XDG_DATA_HOME.
    """
    values = os.environ if environ is None else environ
    home = Path.home() if user_home is None else Path(user_home)
    legacy = Path(values["U2NET_HOME"]).expanduser() if values.get("U2NET_HOME") else (
        Path(values["XDG_DATA_HOME"]).expanduser() / ".u2net"
        if values.get("XDG_DATA_HOME") else home / ".u2net"
    )
    if values.get("U2NET_HOME"):
        root = legacy
    elif values.get("REMBG_HOME"):
        root = Path(values["REMBG_HOME"]).expanduser()
    elif values.get("XDG_DATA_HOME"):
        root = Path(values["XDG_DATA_HOME"]).expanduser() / "rembg"
    else:
        root = home / ".rembg"
    for candidate in (root / "models" / MODEL_NAME / MODEL_FILE,
                      legacy / MODEL_FILE):
        try:
            if candidate.is_file() and candidate.stat().st_size > 0:
                return candidate
        except OSError:
            continue
    return None


def composite_clean_studio(source: Image.Image, cutout: Image.Image) -> Image.Image:
    """Flatten a foreground RGBA mask over studio off-white at capture size.

    Reject invalid or empty mattes so a bad segmentation never silently
    produces blank, artificially unaltered, or misaligned customer photos.
    The foreground must never overwrite the passed original source.
    """
    if not isinstance(cutout, Image.Image) or cutout.mode != "RGBA":
        raise BackgroundProcessingError("Model returned no RGBA foreground mask.")
    if cutout.size != source.size:
        raise BackgroundProcessingError("Foreground dimensions do not match the capture.")
    lo, hi = cutout.getchannel("A").getextrema()
    if lo == hi:  # All foreground or all background is an unusable cutout.
        raise BackgroundProcessingError("Portrait mask is empty or fully opaque.")
    canvas = Image.new("RGBA", source.size, STUDIO_COLOR + (255,))
    return Image.alpha_composite(canvas, cutout).convert("RGB")


class BackgroundStudio:
    """Reusable, serialized AI session and all-or-nothing three-photo processing.

    The injectable functions make mask, disk, and fallback tests deterministic
    without shipping ONNX weights to CI. The real backend is rembg+BiRefNet
    Portrait, loaded lazily, only when the operator pre-seeded its local model.
    """

    def __init__(
        self,
        *,
        session_factory: Callable | None = None,
        remove_function: Callable | None = None,
        model_locator: Callable[[], Path | None] = cached_model_path,
    ) -> None:
        self._session_factory = session_factory
        self._remove_function = remove_function
        self._model_locator = model_locator
        self._lock = threading.Lock()
        self._session = None

    def available_offline(self) -> bool:
        """Cheap readiness test: no weights imported or downloaded in UI thread."""
        return (self._model_locator() is not None
                and (self._session_factory is not None and self._remove_function is not None
                     or importlib.util.find_spec("rembg") is not None))

    def process_three(self, paths: Sequence[Path]) -> tuple[Image.Image, ...]:
        """Prepare three RGB copies for preview and the normal receipt composer.

        Any failure aborts the entire batch. Caller shows Original and retains
        the raw JPEGs, avoiding a strip with inconsistent backgrounds.
        """
        if len(paths) != 3:
            raise ValueError("Background Studio requires exactly three captured photos.")
        if self._model_locator() is None:
            raise BackgroundProcessingError(
                "Model BiRefNet belum dipasang offline. Gunakan mode Original."
            )
        with self._lock:
            factory = self._session_factory
            remove = self._remove_function
            if factory is None or remove is None:
                try:
                    from rembg import new_session, remove as rembg_remove
                except (ImportError, OSError) as error:
                    raise BackgroundProcessingError(
                        "Paket rembg belum siap. Gunakan mode Original."
                    ) from error
                factory = factory or new_session
                remove = remove or rembg_remove
            if self._session is None:
                try:
                    self._session = factory(MODEL_NAME)
                except Exception as error:
                    raise BackgroundProcessingError(
                        "Model BiRefNet gagal dimuat. Gunakan mode Original."
                    ) from error
            results = []
            for path in paths:
                try:
                    with Image.open(path) as original:
                        source = ImageOps.exif_transpose(original).convert("RGB")
                    foreground = remove(source, session=self._session)
                    results.append(composite_clean_studio(source, foreground))
                except BackgroundProcessingError:
                    raise
                except Exception as error:
                    raise BackgroundProcessingError(
                        "AI gagal memproses salah satu foto. Gunakan mode Original."
                    ) from error
        return tuple(results)
