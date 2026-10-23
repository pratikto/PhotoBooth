"""New page-owned music and effects controller for the portrait GUI.

Independent of photobooth.audio.AudioManager: no global fade state and no
invisible legacy sound handle is shared with the existing Kivy GUI. Reuses only
the bundled original Meong WAV **media files**, not the v1 playback lifecycle.
Real speaker audibility still needs a fresh Windows operator test.
"""

from pathlib import Path
import logging
import math
import os

LOG = logging.getLogger(__name__)

BUNDLED_SOUNDS = Path(__file__).resolve().parents[1] / "assets" / "audio"
SOUND_FILES = {
    "music": "meong-v2-music.wav",
    "button": "meong-v2-button.wav",
    "count": "meong-v2-count.wav",
    "shutter": "meong-v2-shutter-soft.wav",
    "success": "meong-v2-success.wav",
}
# No soundtrack over an advertising video; still images may use GUI music. A future game
# integration must obtain/release its own isolated audio channel explicitly.
MUSIC_PAGES = frozenset({"tutorial", "templates"})
KNOWN_PAGES = frozenset({"advert", "tutorial", "templates", "game_preview"})


def bounded_gain(value: float) -> float:
    """Prevent invalid mute/volume input reaching native SDL audio handles."""
    try:
        gain = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    if gain != gain:
        return 0.0
    return max(0.0, min(1.0, gain))


def select_pcm_handle(candidates):
    """Use the first native WAV handle with a positive, finite duration.

    The earlier GUI sometimes selected an audio provider that could report
    playback while remaining silent on Windows. An unusable provider must not
    monopolize the only music channel or hide the working SDL2 fallback.
    Candidate factories are injected so provider selection can be tested without
    importing Kivy or touching a real speaker.
    """
    for name, factory in candidates:
        handle = None
        try:
            handle = factory()
            seconds = float(getattr(handle, "length", 0)) if handle is not None else 0
            if handle is not None and math.isfinite(seconds) and seconds > 0:
                LOG.info("Meong v2 WAV provider=%s duration=%.2fs", name, seconds)
                return handle
            LOG.warning("Meong v2 WAV provider=%s returned unusable duration", name)
        except Exception:
            LOG.warning("Meong v2 WAV provider=%s failed", name, exc_info=True)
        if handle is not None:
            try:
                handle.unload()
            except Exception:
                LOG.warning("Failed to release rejected WAV provider=%s", name, exc_info=True)
    return None


def kivy_sound_loader():
    """Prefer desktop SDL2 for bundled PCM WAV; preserve explicit KIVY_AUDIO.

    Import Kivy only when the window starts. SoundLoader alone may select
    ffpyplayer first on Windows; our previous GUI's music audibility remained
    unverified even when a handle said 'play'. SDL2 is attempted directly
    before the ordinary provider fallback, while an operator's KIVY_AUDIO
    override is honored. Default Windows WAV fallback stays on SDL2: ffpyplayer
    can fail natively when reopening a different channel layout after ad video.
    Neither provider success nor state='play' proves that
    real speakers produced audible sound.
    """
    from kivy.core.audio import SoundLoader
    from kivy.utils import platform

    def load(path):
        candidates = []
        if platform in {"win", "linux", "macosx"} and not os.environ.get("KIVY_AUDIO"):
            try:
                from .mixer import channel_safe_sound
                candidates.append(("SDL2 (idle channel recovery)", lambda: channel_safe_sound(path)))
            except Exception:
                LOG.warning("SDL2 WAV channel recovery helper unavailable", exc_info=True)
            if platform == "win":
                # A ctypes/helper failure must not start a second FFmpeg audio
                # decoder. That fallback crashed on the owner's ad -> tutorial
                # handoff with ffpyplayer 4.5.3 ('Channel layout change ...').
                # Plain SDL keeps the GUI usable if channel repair is unavailable;
                # if both SDL paths fail, return None and let the UI stay open.
                try:
                    from kivy.core.audio.audio_sdl2 import SoundSDL2
                    candidates.append(("SDL2 (plain fallback)",
                                       lambda: SoundSDL2(source=str(path))))
                except Exception:
                    LOG.warning("Windows SDL2 WAV fallback unavailable", exc_info=True)
                return select_pcm_handle(candidates)
        candidates.append(("Kivy SoundLoader", lambda: SoundLoader.load(str(path))))
        return select_pcm_handle(candidates)

    return load


class PortraitAudio:
    """Single long-lived sound owner; page rebuilds must not restart the song."""

    def __init__(self, loader, *, root=None, enabled=True, music_gain=.60, effects_gain=.65):
        self._load = loader
        self.root = Path(root or BUNDLED_SOUNDS)
        self.enabled = bool(enabled)
        self.music_gain = bounded_gain(music_gain)
        self.effects_gain = bounded_gain(effects_gain)
        self.page = "advert"
        self.ad_media = "video"
        self.suspended = False
        self._handles = {}
        self.last_error = None

    def _sound(self, name):
        if name not in SOUND_FILES:
            raise ValueError("Unknown sound name")
        if name not in self._handles:
            path = self.root / SOUND_FILES[name]
            try:
                handle = self._load(str(path)) if path.is_file() else None
                if handle is not None:
                    handle.volume = 0.0
                    if name == "music":
                        handle.loop = True
                self._handles[name] = handle
                if handle is None:
                    self.last_error = "Audio asset/provider unavailable: " + name
            except Exception as exc:
                LOG.warning("Meong v2 audio load failure: %s", name, exc_info=True)
                self._handles[name] = None
                self.last_error = f"{name}: {type(exc).__name__}"
        return self._handles[name]

    def prepare(self):
        """Load silent handles during idle; first tap must not open a WAV file."""
        if not self.enabled or self.suspended:
            return False
        handles = [self._sound(name) for name in ('button', 'music')]
        return all(handle is not None for handle in handles)

    @staticmethod
    def _stop(handle):
        if handle is not None:
            try:
                handle.volume = 0
                if getattr(handle, "state", None) == "play":
                    handle.stop()
            except Exception:
                LOG.warning("Meong v2 audio stop failure", exc_info=True)

    def _sync_music(self, *, restart=False):
        handle = self._handles.get("music")
        should_play = (self.enabled and not self.suspended and
                       (self.page in MUSIC_PAGES or
                        (self.page == "advert" and self.ad_media in {"image", "fallback"}))
                       and self.music_gain > 0)
        if not should_play:
            self._stop(handle)
            return False
        if handle is None:
            handle = self._sound("music")
        if handle is None:
            return False
        try:
            if restart and getattr(handle, "state", None) == "play":
                handle.stop()
            handle.volume = self.music_gain
            if restart or getattr(handle, "state", None) != "play":
                handle.play()
            if getattr(handle, "state", None) != "play":
                self.last_error = "music: native provider did not acknowledge playback"
                LOG.warning("Meong v2 music requested but native provider remains stopped")
                return False
            self.last_error = None
            return True
        except Exception as exc:
            self.last_error = f"music: {type(exc).__name__}"
            LOG.warning("Meong v2 soundtrack could not play", exc_info=True)
            return False

    def enter_page(self, page):
        """Be explicit about which view owns background music."""
        if page not in KNOWN_PAGES:
            raise ValueError("Unsupported prototype page: " + str(page))
        self.page = page
        if page == "advert":
            # Stay silent until the player declares its current creative.
            self.ad_media = "video"
        if page not in MUSIC_PAGES:
            for name, handle in self._handles.items():
                if name not in {"music", "button"}:
                    self._stop(handle)
        return self._sync_music()

    def set_ad_media(self, media):
        """The player calls before video load, or after a still/fallback is ready."""
        if media not in {"video", "image", "fallback"}:
            raise ValueError("Unsupported advertising media")
        self.ad_media = media
        return self._sync_music()

    def set_music_gain(self, value):
        self.music_gain = bounded_gain(value)
        return self._sync_music()

    def set_effects_gain(self, value):
        self.effects_gain = bounded_gain(value)

    def cue(self, name="button"):
        """Clicks are permitted on every page; camera effects stay page-owned."""
        if name not in ("button", "count", "shutter", "success"):
            raise ValueError("Unsupported sound cue")
        if (not self.enabled or self.suspended or self.effects_gain <= 0 or
                (name != "button" and self.page not in MUSIC_PAGES)):
            return False
        handle = self._sound(name)
        if handle is None:
            return False
        try:
            if getattr(handle, "state", None) == "play":
                handle.stop()
            handle.volume = self.effects_gain
            handle.play()
            return True
        except Exception as exc:
            self.last_error = f"{name}: {type(exc).__name__}"
            LOG.warning("Meong v2 sound cue could not play", exc_info=True)
            return False

    def test_music(self):
        """Force an audible test request, reloading if initial native load failed.

        Native state=play is only a provider response, NOT proof of speaker audio.
        """
        if self._handles.get("music") is None:
            self._handles.pop("music", None)
        return self._sync_music(restart=True)

    def suspend(self):
        self.suspended = True
        for handle in self._handles.values():
            self._stop(handle)

    def resume(self):
        self.suspended = False
        self._sync_music()

    def status(self):
        handle = self._handles.get("music")
        return {
            "page": self.page,
            "enabled": self.enabled,
            "music_gain": self.music_gain,
            "music_state": getattr(handle, "state", "unloaded") if handle else "unavailable",
            "provider": type(handle).__name__ if handle is not None else "none",
            "last_error": self.last_error,
        }

    def close(self):
        self.suspended = True
        for handle in self._handles.values():
            self._stop(handle)
            if handle is not None and callable(getattr(handle, "unload", None)):
                try:
                    handle.unload()
                except Exception:
                    LOG.warning("Meong v2 audio unload failed", exc_info=True)
        self._handles.clear()


def make_kivy_audio():
    return PortraitAudio(
        kivy_sound_loader(),
        enabled=os.environ.get("PHOTOBOOTH_AUDIO", "1").lower() not in {"0", "off", "false"},
    )
