"""Hardware-free checks for real audio samples, mixer buses and preferences."""

from dataclasses import asdict
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import wave

import numpy as np

from photobooth.audio import (AudioLevels, AudioManager, BUNDLED_AUDIO_DIR,
                             SAMPLE_RATE, SOUND_DURATIONS, SOUND_NAMES,
                             prepare_assets, synthesize)


class FakeSound:
    """An instrumented provider handle; tests never open a system audio device."""

    def __init__(self):
        self.volume = 1
        self.loop = False
        self.state = "stop"
        self.plays = 0
        self.unloaded = False

    def play(self):
        self.plays += 1
        self.state = "play"

    def stop(self):
        self.state = "stop"

    def unload(self):
        self.unloaded = True


class AudioTests(unittest.TestCase):
    def test_original_samples_are_audible_bounded_deterministic_and_distinct(self):
        """Check PCM itself, not merely whether a generated filename exists."""
        content = {name: synthesize(name, sample_rate=8000) for name in SOUND_NAMES}
        self.assertEqual(len(content["music"]), round(SOUND_DURATIONS["music"] * 8000) * 2)
        self.assertEqual(len(set(content.values())), len(SOUND_NAMES))
        for name, pcm in content.items():
            with self.subTest(name=name):
                samples = np.frombuffer(pcm, dtype="<i2")
                self.assertGreater(np.sqrt(np.mean(samples.astype(float) ** 2)), 200)
                self.assertLessEqual(np.max(np.abs(samples.astype(int))), 30000)
                self.assertEqual(int(samples[0]), 0)
                self.assertEqual(int(samples[-1]), 0)
                self.assertEqual(pcm, synthesize(name, sample_rate=8000))
        with self.assertRaises(ValueError):
            synthesize("unknown")

    def test_wav_cache_reuses_bytes_and_repairs_an_unreadable_file(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = prepare_assets(directory, bundled_directory=None)
            initial = {name: (path.read_bytes(), path.stat().st_mtime_ns) for name, path in paths.items()}
            prepare_assets(directory, bundled_directory=None)
            for name, path in paths.items():
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), initial[name])
                with wave.open(str(path)) as source:
                    self.assertEqual(source.getframerate(), SAMPLE_RATE)
                    self.assertEqual(source.getsampwidth(), 2)
                    self.assertEqual(source.getnchannels(), 1)
            paths["count"].write_bytes(b"interrupted write")
            prepare_assets(directory, bundled_directory=None)
            self.assertEqual(paths["count"].read_bytes(), initial["count"][0])
            # A WAV can retain a correct header after a partially copied payload.
            paths["shutter"].write_bytes(initial["shutter"][0][:-100])
            prepare_assets(directory, bundled_directory=None)
            self.assertEqual(paths["shutter"].read_bytes(), initial["shutter"][0])

    def test_fresh_install_uses_complete_shipped_samples_without_writing_a_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "uncreated-cache"
            paths = prepare_assets(cache)
            self.assertFalse(cache.exists())
            self.assertEqual(set(paths), set(SOUND_NAMES))
            for name, path in paths.items():
                with self.subTest(sound=name), wave.open(str(path)) as source:
                    self.assertEqual(path.parent, BUNDLED_AUDIO_DIR)
                    self.assertEqual(source.readframes(source.getnframes()), synthesize(name))

    def test_missing_bundled_sample_repairs_only_that_sample_in_the_local_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            cache = root / "cache"
            prepare_assets(bundle, bundled_directory=None)
            missing = bundle / "meong-v2-count.wav"
            missing.unlink()
            paths = prepare_assets(cache, bundled_directory=bundle)
            self.assertEqual(paths["count"].parent, cache)
            self.assertFalse(missing.exists())
            self.assertTrue(all(path.parent == bundle for key, path in paths.items() if key != "count"))

    def test_corrupt_preferences_are_recoverable_and_gains_are_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "levels.json"
            path.write_text('{"music":-2,"buttons":8,"effects":"nan"}')
            levels = AudioLevels.load(path)
            self.assertEqual((levels.music, levels.buttons, levels.effects), (0, 1, .70))
            levels.music = .37
            self.assertTrue(levels.save(path))
            self.assertEqual(asdict(AudioLevels.load(path)), asdict(levels))
            path.write_text("damaged")
            self.assertEqual(AudioLevels.load(path), AudioLevels())
            path.write_text("[]")
            self.assertEqual(AudioLevels.load(path), AudioLevels())

    def make_manager(self, directory):
        with patch.dict("os.environ", {"PHOTOBOOTH_AUDIO": "1"}):
            manager = AudioManager(directory)
        manager._sounds = {name: FakeSound() for name in SOUND_NAMES}
        manager._apply_levels()
        manager._ensure_music()
        self.addCleanup(manager.close)
        return manager

    def test_three_buses_mute_live_and_ducking_does_not_restart_music(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = self.make_manager(directory)
            song = manager._sounds["music"]
            self.assertEqual(song.plays, 1)
            manager.set_capture_active(True)
            self.assertAlmostEqual(song.volume, .28 * .28)
            manager.set_capture_active(False)
            self.assertAlmostEqual(song.volume, .28)
            self.assertEqual(song.plays, 1)
            manager.set_volume("buttons", 0)
            manager.play("button")
            manager.play("count")
            self.assertEqual(manager._sounds["button"].plays, 0)
            self.assertEqual(manager._sounds["count"].plays, 1)
            manager.set_volume("effects", 0)
            manager.play("shutter")
            manager.play("count")
            self.assertEqual(manager._sounds["shutter"].plays, 0)
            self.assertEqual(manager._sounds["count"].plays, 1)
            self.assertAlmostEqual(song.volume, .28)
            manager.set_volume("music", 0)
            self.assertEqual(song.state, "stop")
            manager.set_volume("music", .42)
            self.assertEqual(song.state, "play")
            self.assertAlmostEqual(song.volume, .42)
            self.assertTrue(manager.save_settings())
            self.assertEqual(AudioLevels.load(manager.settings_path), manager.levels)

    def test_missing_provider_and_late_worker_completion_do_not_block_the_booth(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = AudioManager(directory, loader=lambda path: None)
            manager._results.put(({"count": Path(directory) / "unused.wav"}, None))
            self.assertFalse(manager._poll())
            manager.play("count")
            self.assertFalse(manager._sounds)
            manager.close()
            calls = []
            manager._loader = calls.append
            manager._results.put(({"music": Path(directory) / "late.wav"}, None))
            self.assertFalse(manager._poll())
            self.assertFalse(calls)

    def test_pause_and_close_stop_all_handles_and_never_replay_expired_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = self.make_manager(directory)
            sounds = dict(manager._sounds)
            manager.play("shutter")
            manager.pause()
            self.assertTrue(all(sound.state == "stop" for sound in sounds.values()))
            manager.play("count")
            self.assertEqual(sounds["count"].plays, 0)
            manager.resume()
            self.assertEqual(sounds["music"].state, "play")
            self.assertEqual(sounds["shutter"].plays, 1)
            manager.close()
            manager.play("count")
            self.assertTrue(all(sound.unloaded for sound in sounds.values()))
            self.assertFalse(manager._sounds)

    def test_status_distinguishes_disabled_muted_and_playing_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = self.make_manager(directory)
            self.assertIn("Musik menyala", manager.summary)
            before = manager._sounds["music"].plays
            manager.play("music")
            self.assertEqual(manager._sounds["music"].plays, before)
            for channel in ("music", "buttons", "effects"):
                manager.set_volume(channel, 0)
            self.assertIn("Semua suara dibisukan", manager.summary)
            with patch.dict(os.environ, {"PHOTOBOOTH_AUDIO": "0"}):
                disabled = AudioManager(directory)
            disabled.start()
            disabled.retry()
            self.assertIn("dinonaktifkan", disabled.summary)
            self.assertFalse(disabled._started)
            disabled.close()

    @unittest.skipUnless(os.environ.get("PHOTOBOOTH_TEST_AUDIO") == "1", "native audio checks are opt-in")
    def test_real_provider_starts_music_and_loads_every_cue_from_a_fresh_install(self):
        """Use Kivy's actual mixer/Clock, not FakeSound, with a CI dummy device.

        This catches missing WAVs/providers and startup wiring that fixture-only
        tests miss. A dummy output validates playback state, not speaker volume.
        """
        from kivy.clock import Clock
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"PHOTOBOOTH_AUDIO": "1"}):
                manager = AudioManager(directory)
            self.addCleanup(manager.close)
            manager.start()
            manager.start()
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and not manager._sounds:
                Clock.tick()
            self.assertEqual(set(manager._sounds), set(SOUND_NAMES), manager.summary)
            song = manager._sounds["music"]
            self.assertEqual(song.state, "play", manager.summary)
            self.assertAlmostEqual(song.length, SOUND_DURATIONS["music"], places=2)
            self.assertAlmostEqual(song.volume, manager.levels.music)
            for name in SOUND_NAMES[1:]:
                manager.play(name)
                self.assertEqual(manager._sounds[name].state, "play", name)
            manager.pause()
            self.assertTrue(all(sound.state == "stop" for sound in manager._sounds.values()))
            manager.resume()
            self.assertEqual(song.state, "play")


if __name__ == "__main__":
    unittest.main()
