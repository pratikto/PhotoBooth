"""Original offline music and sound cues for the MEONG kiosk.

The melody below is an original small farm-game-style composition, not a
recording or transcription of a commercial game's soundtrack. Ready-to-play
WAVs ship with the application; the score below can rebuild a missing/corrupt
asset in a background worker. Kivy loads/plays them only on the UI thread.
No audio download, account, or additional native mixer is needed.

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
ASSET_VERSION = "v2"
BUNDLED_AUDIO_DIR = Path(__file__).resolve().parent / "assets" / "audio"
SOUND_DURATIONS = {"music": 40.0, "button": .16, "count": .20,
                   "shutter": .23, "success": .90}
SOUND_NAMES = tuple(SOUND_DURATIONS)
CHANNEL_FOR = {"music": "music", "button": "buttons", "count": "effects",
               "shutter": "effects", "success": "effects"}


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
    ads: float = .50

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


def _note(buffer, start, beats, midi, gain, *, voice="harp", beat_seconds=.625,
          sample_rate=SAMPLE_RATE):
    """Mix an original synthesized instrument with click-free note boundaries.

    MIDI numbers express pitch only; all phrases and their rhythm are specified
    here. Envelopes avoid abrupt discontinuities and keep the loop comfortable.
    """
    begin = round(start * beat_seconds * sample_rate)
    length = min(round(beats * beat_seconds * sample_rate), len(buffer) - begin)
    if length <= 0:
        return
    t = np.arange(length, dtype=np.float64) / sample_rate
    frequency = 440.0 * 2 ** ((midi - 69) / 12)
    seconds = length / sample_rate
    phase = 2 * np.pi * frequency * t
    if voice == "flute":
        # A mellow, slightly vibrating lead evokes a small handheld adventure.
        phase += .012 * np.sin(2 * np.pi * 5.2 * t)
        tone = np.sin(phase) + .12 * np.sin(2 * phase) + .035 * np.sin(3 * phase)
        envelope = (1 - np.exp(-t * 45)) * np.exp(-t * 1.2 / seconds)
    elif voice == "bass":
        tone = np.sin(phase) - np.sin(3 * phase) / 9 + np.sin(5 * phase) / 25
        envelope = (1 - np.exp(-t * 90)) * np.exp(-t * 2.2 / seconds)
    elif voice == "bell":
        tone = np.sin(phase) + .25 * np.sin(2 * phase) + .08 * np.sin(3 * phase)
        envelope = (1 - np.exp(-t * 180)) * np.exp(-t * 4.0 / seconds)
    else:
        tone = np.sin(phase) + .22 * np.sin(2 * phase) + .06 * np.sin(3 * phase)
        envelope = (1 - np.exp(-t * 120)) * np.exp(-t * 4.8 / seconds)
    envelope *= np.minimum(1, (seconds - t) * 90)
    buffer[begin:begin + length] += tone * envelope * gain


def synthesize(name, sample_rate=SAMPLE_RATE):
    """Return deterministic signed 16-bit mono PCM for one named sound.

    Music: "Meong's Little Photo Garden", sixteen bars at 96 BPM. A flute-like
    lead, harp arpeggios, triangle bass and soft shakers suggest a cheerful
    farming/adventure game. All pitches, rhythms and timbres are authored here.
    Button/count: short, rounded menu and countdown chimes.
    Shutter: a camera click with a tiny sparkling finish.
    Success: a short ascending reward flourish after the result is saved.
    """
    if name not in SOUND_NAMES:
        raise ValueError(f"Unknown sound: {name}")
    if name == "music":
        samples = np.zeros(round(SOUND_DURATIONS[name] * sample_rate), dtype=np.float64)
        chords = ((48, 52, 55), (43, 47, 50), (45, 48, 52), (40, 43, 47),
                  (41, 45, 48), (48, 52, 55), (50, 53, 57), (43, 47, 50))
        phrases = (
            ((0, 76, .65), (.75, 79, .40), (1.25, 81, .65), (2, 79, .90), (3, 74, .80)),
            ((0, 74, .40), (.5, 71, .65), (1.25, 74, .40), (2, 79, .65), (2.75, 76, .90)),
            ((0, 72, .65), (.75, 76, .65), (1.5, 81, .40), (2, 83, .65), (2.75, 81, .90)),
            ((0, 79, .90), (1, 76, .65), (1.75, 74, .40), (2.5, 71, 1.25)),
            ((0, 77, .65), (.75, 81, .40), (1.25, 79, .65), (2, 77, .65), (2.75, 76, .90)),
            ((0, 76, .40), (.5, 79, .65), (1.25, 84, .65), (2, 83, .40), (2.5, 79, 1.25)),
            ((0, 77, .65), (.75, 74, .65), (1.5, 76, .40), (2, 77, .65), (2.75, 81, .90)),
            ((0, 79, .65), (.75, 74, .40), (1.25, 71, .65), (2, 74, .65), (3, 72, .85)),
        )
        rng = np.random.default_rng(516)
        for bar in range(16):
            chord = chords[bar % 8]
            for offset, pitch in ((0, chord[0] - 12), (2, chord[2] - 12)):
                _note(samples, bar * 4 + offset, 1.8, pitch, .23,
                      voice="bass", sample_rate=sample_rate)
            for step in range(8):
                _note(samples, bar * 4 + step * .5, .72,
                      chord[(0, 1, 2, 1)[step % 4]] + 12, .13, sample_rate=sample_rate)
                # Bounded, seeded shaker noise keeps the score reproducible.
                begin = round((bar * 4 + step * .5 + .25) * .625 * sample_rate)
                count = min(round(.055 * sample_rate), len(samples) - begin)
                t = np.arange(count) / sample_rate
                samples[begin:begin + count] += rng.uniform(-1, 1, count) * np.exp(-t * 85) * .023
            for offset, pitch, duration in phrases[bar % 8]:
                _note(samples, bar * 4 + offset, duration, pitch, .30,
                      voice="flute", sample_rate=sample_rate)
                if bar >= 8 and offset in (0, 2):
                    _note(samples, bar * 4 + offset, duration, pitch + 12, .055,
                          voice="bell", sample_rate=sample_rate)
    elif name in {"button", "count"}:
        samples = np.zeros(round(SOUND_DURATIONS[name] * sample_rate))
        _note(samples, 0, .14, 79 if name == "button" else 84, .48,
              voice="bell", beat_seconds=1, sample_rate=sample_rate)
        if name == "button":
            _note(samples, .045, .10, 84, .20, voice="bell",
                  beat_seconds=1, sample_rate=sample_rate)
    elif name == "success":
        samples = np.zeros(round(SOUND_DURATIONS[name] * sample_rate))
        for offset, pitch in ((0, 72), (.12, 76), (.24, 79), (.40, 84)):
            _note(samples, offset, .48, pitch, .40, voice="bell",
                  beat_seconds=1, sample_rate=sample_rate)
    else:
        t = np.arange(round(SOUND_DURATIONS[name] * sample_rate)) / sample_rate
        noise = np.random.default_rng(248).uniform(-1, 1, len(t))
        first = np.exp(-t * 85)
        second = np.where(t >= .065, np.exp(-np.maximum(0, t - .065) * 65), 0)
        samples = .55 * noise * (first + .65 * second) + .12 * np.sin(2 * np.pi * 130 * t) * np.exp(-t * 35)
        _note(samples, .08, .14, 88, .13, voice="bell",
              beat_seconds=1, sample_rate=sample_rate)
    # Fade both loop boundaries to zero, and leave headroom for overlapping buses.
    fade = min(round(.012 * sample_rate), len(samples) // 2)
    if fade:
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
    # Normalize the quiet score without changing the user's selected volume.
    # Peak headroom leaves room for the native mixer to overlay a menu cue.
    rms = float(np.sqrt(np.mean(samples ** 2)))
    peak = float(np.max(np.abs(samples)))
    gain = min((.20 if name == "music" else .24) / max(rms, 1e-9),
               .76 / max(peak, 1e-9))
    return np.round(samples * gain * 32767).astype("<i2").tobytes()


def _valid_asset(path, name):
    """Reject truncated WAVs as well as files with an incompatible PCM header."""
    try:
        with wave.open(str(path), "rb") as source:
            frames = round(SOUND_DURATIONS[name] * SAMPLE_RATE)
            return (source.getnchannels() == 1 and source.getsampwidth() == 2
                    and source.getframerate() == SAMPLE_RATE
                    and source.getnframes() == frames
                    and len(source.readframes(frames)) == frames * 2)
    except (OSError, EOFError, wave.Error):
        return False


def prepare_assets(directory, *, bundled_directory=BUNDLED_AUDIO_DIR):
    """Prefer shipped WAVs; only regenerate missing assets into the local cache.

    A fresh checkout plays the same bytes as a tested build. A read-only code
    directory is fine: any repair goes under the caller's writable data path.
    Passing bundled_directory=None is useful for reproducible asset builds.
    """
    directory = Path(directory)
    paths = {}
    for name in SOUND_NAMES:
        if bundled_directory is not None:
            bundled = Path(bundled_directory) / f"meong-{ASSET_VERSION}-{name}.wav"
            if _valid_asset(bundled, name):
                paths[name] = bundled
                continue
        path = directory / f"meong-{ASSET_VERSION}-{name}.wav"
        if not _valid_asset(path, name):
            directory.mkdir(parents=True, exist_ok=True)
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


def load_native_sound(path):
    """Load desktop WAVs with SDL2, falling back to Kivy's platform provider.

    SoundLoader chooses the first registered provider even when that provider
    returns an unusable handle. In particular, an installed ffpyplayer can
    take priority over SDL2. PCM WAVs need no external codec, so prefer Kivy's
    bundled SDL2 mixer on desktops unless the operator explicitly set
    KIVY_AUDIO. Android/iOS retain their platform-selected audio provider.
    A zero-length handle is a load failure, not evidence that sound is ready.
    """
    from kivy.core.audio import SoundLoader
    from kivy.utils import platform

    loaders = []
    if platform in {"win", "linux", "macosx"} and not os.environ.get("KIVY_AUDIO"):
        try:
            from kivy.core.audio.audio_sdl2 import SoundSDL2
            loaders.append(lambda filename: SoundSDL2(source=filename))
        except ImportError:
            pass
    loaders.append(SoundLoader.load)
    for loader in loaders:
        sound = None
        try:
            sound = loader(str(path))
            if sound is not None and sound.length > 0:
                LOG.info("Loaded %s with %s (%.2fs)", Path(path).name,
                         type(sound).__name__, sound.length)
                return sound
        except Exception:
            LOG.warning("Audio provider could not open %s", Path(path).name, exc_info=True)
        if sound is not None:
            try:
                sound.unload()
            except Exception:
                pass
    return None


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
        self._advertising = False
        self._music_mix = 1.0
        self._fade_event = None
        self._enabled = os.environ.get("PHOTOBOOTH_AUDIO", "1").lower() not in {"0", "false", "no"}
        if not self._enabled:
            self.status = "Audio dinonaktifkan lewat konfigurasi"

    @property
    def summary(self):
        """Live operator feedback: distinguish muted buses from failed output."""
        if not self._enabled or not self._sounds:
            return self.status
        if self._paused:
            return "Audio dijeda"
        if self._advertising:
            return "Layar iklan · musik aplikasi dijeda"
        if all(getattr(self.levels, channel) == 0 for channel in ("music", "buttons", "effects")):
            return "Semua suara dibisukan · naikkan volume untuk mendengar"
        if self.levels.music == 0:
            return "Musik dibisukan · efek mengikuti volume masing-masing"
        music = self._sounds.get("music")
        if music is not None and music.state == "play":
            return ("Musik menyala · efek siap" if len(self._sounds) == len(SOUND_NAMES)
                    else "Musik menyala · beberapa efek belum tersedia")
        return self.status

    @property
    def diagnostic(self):
        """Show real playback gates, not merely the optimistic 'audio ready' flag.

        Operators need this when the WAV works in a standalone speaker check
        but is silent inside the kiosk. The snapshot contains no user data.
        """
        music = self._sounds.get("music")
        return (
            f"provider={type(music).__name__ if music else 'none'} "
            f"state={getattr(music, 'state', 'unloaded')} "
            f"gain={getattr(music, 'volume', 0):.2f} "
            f"level={self.levels.music:.2f} mix={self._music_mix:.2f} "
            f"advert={int(self._advertising)} paused={int(self._paused)} "
            f"started={int(self._started)} sounds={len(self._sounds)} "
            f"enabled={int(self._enabled)}"
        )

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
            self._loader = load_native_sound
        for name, path in paths.items():
            try:
                sound = self._loader(str(path))
                if sound is not None:
                    sound.loop = name == "music"
                    self._sounds[name] = sound
            except Exception:
                LOG.warning("Audio provider could not load %s", name, exc_info=True)
        self.status = ("Audio siap" if len(self._sounds) == len(SOUND_NAMES)
                       else "Sebagian audio belum tersedia" if self._sounds
                       else "Audio belum tersedia · periksa keluaran suara perangkat")
        missing = set(SOUND_NAMES) - self._sounds.keys()
        if missing:
            LOG.warning("Audio bank incomplete; unavailable: %s", ", ".join(sorted(missing)))
        self._apply_levels()
        self._ensure_music()
        return False

    def _apply_levels(self):
        """Only music is ducked during capture; other buses keep their own gain."""
        for name, sound in self._sounds.items():
            try:
                sound.volume = getattr(self.levels, CHANNEL_FOR[name]) * (self._music_mix if name == 'music' else 1) * (
                    .28 if name == "music" and self._capturing else 1)
                if sound.volume == 0:
                    sound.stop()
            except Exception:
                LOG.warning("Audio gain update failed", exc_info=True)

    def _ensure_music(self):
        """Resume the existing loop only when audible and the host is active."""
        sound = self._sounds.get("music")
        if (self._closed or self._paused or self._advertising or not self._enabled
                or sound is None or self.levels.music <= 0 or self._music_mix <= 0):
            return
        try:
            if sound.state != "play":
                sound.play()
                if sound.state != "play":
                    self.status = "Musik gagal diputar · periksa keluaran suara perangkat"
                    LOG.warning("Music provider did not enter the playing state")
        except Exception:
            self.status = "Audio belum tersedia"
            LOG.warning("Music playback failed", exc_info=True)

    def set_volume(self, channel, value):
        """Apply slider changes immediately; the UI persists them on dismissal."""
        if channel not in {"music", "buttons", "effects", "ads"}:
            raise ValueError(f"Unknown audio channel: {channel}")
        setattr(self.levels, channel, clamp_volume(value))
        self._apply_levels()
        self._ensure_music()

    def save_settings(self):
        """Persist the three gains without making a write failure fatal."""
        return self.levels.save(self.settings_path)

    def retry(self):
        """Let the operator retry loading after fixing an output/device problem.

        Keep one preparation worker at a time. A disabled configuration and a
        closed host remain disabled; this control never overrides their intent.
        """
        if self._closed or not self._enabled or self._poll_event is not None:
            return
        for sound in self._sounds.values():
            try:
                sound.stop()
                sound.unload()
            except Exception:
                pass
        self._sounds.clear()
        self._started = False
        self.start()

    def set_capture_active(self, active):
        """Duck/restore music without seeking or restarting the track."""
        self._capturing = bool(active)
        self._apply_levels()

    def set_advertising(self, active, fade_seconds=.25):
        """Give idle video sole audio ownership; fade music back into the app.

        This page state is separate from host pause, so resuming the app cannot
        accidentally restart its song over an advertisement. New/cold handles
        receive the target mix before asynchronous native loading completes.
        """
        active = bool(active)
        if active == self._advertising:
            return
        self._advertising = active
        if self._fade_event is not None:
            self._fade_event.cancel()
            self._fade_event = None
        if active:
            for name, sound in self._sounds.items():
                if name != 'music':
                    sound.stop()
        target = 0.0 if active else 1.0
        # Stop immediately before a newly mounted video can emit sound. Only
        # returning to the photo workflow fades the application song back in.
        if active or not self._sounds or fade_seconds <= 0:
            self._music_mix = target
            self._apply_levels()
            self._ensure_music()
            return
        # No stale effect is replayed. Normal navigation keeps one ongoing
        # song; only entering/leaving idle advertisements changes this mix.
        start, elapsed = self._music_mix, 0.0
        self._ensure_music()
        def step(dt):
            nonlocal elapsed
            elapsed += dt
            self._music_mix = start + (target - start) * min(1, elapsed / fade_seconds)
            self._apply_levels()
            # Leaving the advertisement begins with a silent (and therefore
            # stopped) music handle. A volume update does not start a stopped
            # Kivy/SDL2 sound. Once the fade becomes audible, explicitly
            # resume its loop without waiting for a Settings slider event.
            # _ensure_music also respects mute, pause and failed devices.
            if self._music_mix > 0:
                self._ensure_music()
            if elapsed >= fade_seconds or self._closed:
                self._fade_event = None
                return False
            return True
        from kivy.clock import Clock
        self._fade_event = Clock.schedule_interval(step, 1 / 30)

    def play(self, name):
        """Play one cue; no disabled, muted, or unprepared action queues sound."""
        if (self._closed or self._paused or self._advertising or not self._enabled
                or name not in CHANNEL_FOR):
            return
        # The music preview must not rewind the ongoing track. Normal button
        # and camera cues still restart their one bounded reusable handle.
        if name == "music":
            self._ensure_music()
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
        if self._fade_event is not None:
            self._fade_event.cancel()
            self._fade_event = None
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
