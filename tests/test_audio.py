"""Hardware-free checks for real audio samples, mixer buses and preferences."""

from dataclasses import asdict
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

import numpy as np

from photobooth.audio import AudioLevels, AudioManager, SAMPLE_RATE, SOUND_NAMES, prepare_assets, synthesize


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
        self.assertEqual(len(content["music"]), 48 * 8000 * 2)
        self.assertEqual(len(set(content.values())), 4)
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
            paths = prepare_assets(directory)
            initial = {name: (path.read_bytes(), path.stat().st_mtime_ns) for name, path in paths.items()}
            prepare_assets(directory)
            for name, path in paths.items():
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), initial[name])
                with wave.open(str(path)) as source:
                    self.assertEqual(source.getframerate(), SAMPLE_RATE)
                    self.assertEqual(source.getsampwidth(), 2)
                    self.assertEqual(source.getnchannels(), 1)
            paths["count"].write_bytes(b"interrupted write")
            prepare_assets(directory)
            self.assertEqual(paths["count"].read_bytes(), initial["count"][0])

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


if __name__ == "__main__":
    unittest.main()
