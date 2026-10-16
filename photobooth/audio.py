"""Original offline music and sound cues for the MEONG kiosk.

The melody below is an original small farm-game-style composition, not a
recording or transcription of a commercial game's soundtrack. NumPy creates
short PCM waveforms once in a background worker. Kivy loads/plays them only on
the UI thread. No audio download, account, or additional native mixer is needed.

The three buses are independent: music, buttons, and camera effects. Keeping
one manager for the application's lifetime prevents restarting the song when
the controller rebuilds a screen. Volume zero is a real mute.
"""

from dataclasses import asdict, dataclass
import json
import logging
import math
import os
from pathlib import Path
from queue import Empty, SimpleQueue
import tempfile
import threading
import wave

import numpy as np


LOG = logging.getLogger(__name__)
SAMPLE_RATE = 22050
ASSET_VERSION = "v1"
SOUND_NAMES = ("music", "button", "count", "shutter")
CHANNEL_FOR = {"music": "music", "button": "buttons", "count": "effects", "shutter": "effects"}


def clamp_volume(value, fallback=0.0):
    """Reject invalid persisted values and constrain gains to a finite 0..1."""
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return fallback
    return min(1.0, max(0.0, value)) if math.isfinite(value) else fallback


@dataclass
class AudioLevels:
    """Operator preferences; these gains are not baked into generated samples."""

    music: float = .28
    buttons: float = .55
    effects: float = .70

    @classmethod
    def load(cls, path):
        """A damaged preference file must never stop the camera application."""
        defaults = cls()
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return defaults
        except (OSError, ValueError):
            return defaults
        return cls(**{key: clamp_volume(payload.get(key), default)
                      for key, default in asdict(defaults).items()})

    def save(self, path):
        """Replace preferences atomically so a power loss leaves valid JSON."""
        path = Path(path)
        temporary = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                             dir=path.parent, delete=False) as output:
                temporary = Path(output.name)
                json.dump(asdict(self), output, indent=2, allow_nan=False)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, path)
            return True
        except OSError:
            LOG.warning("Audio preferences could not be saved", exc_info=True)
            return False
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def _note(buffer, start, beats, midi, gain, *, beat_seconds=.75, sample_rate=SAMPLE_RATE):
    """Mix a softly plucked note, with short attack and a natural decay.

    MIDI numbers express pitch only; all phrases and their rhythm are specified
    here. Envelopes avoid abrupt discontinuities and keep the loop comfortable.
    """
    begin = round(start * beat_seconds * sample_rate)
    length = min(round(beats * beat_seconds * sample_rate), len(buffer) - begin)
    if length <= 0:
        return
    t = np.arange(length, dtype=np.float64) / sample_rate
    frequency = 440.0 * 2 ** ((midi - 69) / 12)
    tone = (np.sin(2 * np.pi * frequency * t)
            + .22 * np.sin(4 * np.pi * frequency * t)
            + .06 * np.sin(6 * np.pi * frequency * t))
    envelope = (1 - np.exp(-t * 120)) * np.exp(-t * 4.8 / max(.15, beats))
    envelope *= np.minimum(1, (length / sample_rate - t) * 70)
    buffer[begin:begin + length] += tone * envelope * gain


def synthesize(name, sample_rate=SAMPLE_RATE):
    """Return deterministic signed 16-bit mono PCM for one named sound.

    Music: sixteen bars at 80 BPM, warm bass, arpeggios, and a light melody.
    Button: a brief two-note wooden/plucked acknowledgement.
    Count: a clear, short single chime, emitted once per controller tick.
    Shutter: two bounded noise clicks plus a quiet mechanical low transient.
    """
    if name not in SOUND_NAMES:
        raise ValueError(f"Unknown sound: {name}")
    if name == "music":
        samples = np.zeros(round(48 * sample_rate), dtype=np.float64)
        chords = ((48, 52, 55), (53, 57, 60), (57, 60, 64), (55, 59, 62))
        melody = ((72, 76, 79, 76, 74, 72), (69, 72, 77, 76, 72, 69),
                  (72, 76, 81, 79, 76, 72), (71, 74, 79, 77, 74, 71))
        for bar in range(16):
            chord = chords[bar % 4]
            _note(samples, bar * 4, 2, chord[0] - 12, .12, sample_rate=sample_rate)
            _note(samples, bar * 4 + 2, 1.8, chord[2] - 12, .08, sample_rate=sample_rate)
            for step in range(8):
                _note(samples, bar * 4 + step * .5, .60,
                      chord[(step % 4) % 3] + 12, .055, sample_rate=sample_rate)
            for offset, pitch in zip((0, .75, 1.5, 2, 2.75, 3.25), melody[bar % 4]):
                _note(samples, bar * 4 + offset, .55, pitch, .11, sample_rate=sample_rate)
    elif name in {"button", "count"}:
        samples = np.zeros(round((.16 if name == "button" else .20) * sample_rate))
        _note(samples, 0, .14, 84 if name == "button" else 81, .48,
              beat_seconds=1, sample_rate=sample_rate)
        if name == "button":
            _note(samples, .045, .10, 91, .20, beat_seconds=1, sample_rate=sample_rate)
    else:
        t = np.arange(round(.23 * sample_rate)) / sample_rate
        noise = np.random.default_rng(248).uniform(-1, 1, len(t))
        first = np.exp(-t * 85)
        second = np.where(t >= .065, np.exp(-np.maximum(0, t - .065) * 65), 0)
        samples = .55 * noise * (first + .65 * second) + .12 * np.sin(2 * np.pi * 130 * t) * np.exp(-t * 35)
    # Fade both loop boundaries to zero, and leave headroom for overlapping buses.
    fade = min(round(.012 * sample_rate), len(samples) // 2)
    if fade:
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
    return np.clip(samples * 24000, -30000, 30000).astype("<i2").tobytes()


def prepare_assets(directory):
    """Cache reproducible WAV files using atomic, same-directory replacements."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name in SOUND_NAMES:
        path = directory / f"meong-{ASSET_VERSION}-{name}.wav"
        try:
            with wave.open(str(path), "rb") as source:
                valid = (source.getnchannels() == 1 and source.getsampwidth() == 2
                         and source.getframerate() == SAMPLE_RATE and source.getnframes() > 0)
        except (OSError, EOFError, wave.Error):
            valid = False
        if not valid:
            handle, temporary = tempfile.mkstemp(suffix=".wav", dir=directory)
            os.close(handle)
            try:
                with wave.open(temporary, "wb") as output:
                    output.setnchannels(1)
                    output.setsampwidth(2)
                    output.setframerate(SAMPLE_RATE)
                    output.writeframes(synthesize(name))
                os.replace(temporary, path)
            finally:
                Path(temporary).unlink(missing_ok=True)
        paths[name] = path
    return paths


class AudioManager:
    """One optional mixer, with main-thread playback and bounded sound handles.

    Missing audio hardware/providers are a recoverable condition: startup,
    capture, payment and saving continue normally. A late worker completion
    cannot restart playback after shutdown. Tests may inject a loader and
    schedule function without opening a real speaker.
    """

    def __init__(self, directory, *, loader=None, schedule_interval=None):
        self.directory = Path(directory)
        self.settings_path = self.directory / "levels.json"
        self.levels = AudioLevels.load(self.settings_path)
        self.status = "Audio belum dimulai"
        self._loader = loader
        self._schedule_interval = schedule_interval
        self._results = SimpleQueue()
        self._sounds = {}
        self._poll_event = None
        self._started = self._closed = self._paused = self._capturing = False
        self._enabled = os.environ.get("PHOTOBOOTH_AUDIO", "1").lower() not in {"0", "false", "no"}

    def start(self):
        """Prepare files once off-thread; defer native audio loading to Clock."""
        if self._started or self._closed or not self._enabled:
            return
        self._started = True
        self.status = "Menyiapkan audio..."
        if self._schedule_interval is None:
            from kivy.clock import Clock
            self._schedule_interval = Clock.schedule_interval
        self._poll_event = self._schedule_interval(self._poll, .1)
        threading.Thread(target=self._prepare, name="meong-audio", daemon=True).start()

    def _prepare(self):
        """The worker only handles sample/file bytes, never Kivy audio objects."""
        try:
            self._results.put((prepare_assets(self.directory), None))
        except Exception as error:
            self._results.put(({}, error))

    def _poll(self, _dt=0):
        """Load the bounded bank on the UI thread, without waiting for the worker."""
        if self._closed:
            return False
        try:
            paths, error = self._results.get_nowait()
        except Empty:
            return True
        self._poll_event = None
        if error is not None:
            self.status = "Audio belum tersedia"
            LOG.warning("Audio asset preparation failed: %s", error)
            return False
        if self._loader is None:
            try:
                from kivy.core.audio import SoundLoader
                self._loader = SoundLoader.load
            except Exception:
                self.status = "Audio belum tersedia"
                LOG.warning("No audio provider is available", exc_info=True)
                return False
        for name, path in paths.items():
            try:
                sound = self._loader(str(path))
                if sound is not None:
                    sound.loop = name == "music"
                    self._sounds[name] = sound
            except Exception:
                LOG.warning("Audio provider could not load %s", name, exc_info=True)
        self.status = "Audio siap" if len(self._sounds) == len(SOUND_NAMES) else "Sebagian audio belum tersedia"
        self._apply_levels()
        self._ensure_music()
        return False

    def _apply_levels(self):
        """Only music is ducked during capture; other buses keep their own gain."""
        for name, sound in self._sounds.items():
            try:
                sound.volume = getattr(self.levels, CHANNEL_FOR[name]) * (
                    .28 if name == "music" and self._capturing else 1)
                if sound.volume == 0:
                    sound.stop()
            except Exception:
                LOG.warning("Audio gain update failed", exc_info=True)

    def _ensure_music(self):
        """Resume the existing loop only when audible and the host is active."""
        sound = self._sounds.get("music")
        if self._closed or self._paused or not self._enabled or sound is None or self.levels.music <= 0:
            return
        try:
            if sound.state != "play":
                sound.play()
        except Exception:
            self.status = "Audio belum tersedia"
            LOG.warning("Music playback failed", exc_info=True)

    def set_volume(self, channel, value):
        """Apply slider changes immediately; the UI persists them on dismissal."""
        if channel not in {"music", "buttons", "effects"}:
            raise ValueError(f"Unknown audio channel: {channel}")
        setattr(self.levels, channel, clamp_volume(value))
        self._apply_levels()
        self._ensure_music()

    def save_settings(self):
        """Persist the three gains without making a write failure fatal."""
        return self.levels.save(self.settings_path)

    def set_capture_active(self, active):
        """Duck/restore music without seeking or restarting the track."""
        self._capturing = bool(active)
        self._apply_levels()

    def play(self, name):
        """Play one cue; no disabled, muted, or unprepared action queues sound."""
        if self._closed or self._paused or not self._enabled or name not in CHANNEL_FOR:
            return
        sound = self._sounds.get(name)
        if sound is None or getattr(self.levels, CHANNEL_FOR[name]) <= 0:
            return
        try:
            sound.stop()
            sound.play()
        except Exception:
            LOG.warning("Audio cue %s failed", name, exc_info=True)

    def pause(self):
        """Silence the booth while the native application is in the background."""
        self._paused = True
        for sound in self._sounds.values():
            try:
                sound.stop()
            except Exception:
                pass

    def resume(self):
        """Restore only music; expired button/count cues must never replay."""
        self._paused = False
        self._ensure_music()

    def close(self):
        """Cancel polling, stop native handles, and ignore late worker output."""
        if self._closed:
            return
        self._closed = True
        if self._poll_event is not None:
            self._poll_event.cancel()
            self._poll_event = None
        self.pause()
        for sound in self._sounds.values():
            try:
                sound.unload()
            except Exception:
                pass
        self._sounds.clear()
