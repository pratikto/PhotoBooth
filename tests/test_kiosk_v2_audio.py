"""Audio page ownership and fake-provider regression (not speaker verification)."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from photobooth.kiosk_v2.audio import (
    BUNDLED_SOUNDS, SOUND_FILES, PortraitAudio, bounded_gain, select_pcm_handle,
)


class FakeClip:
    def __init__(self):
        self.volume = 0
        self.loop = False
        self.state = "stop"
        self.plays = 0
        self.stops = 0
        self.unloads = 0

    def play(self):
        self.state = "play"
        self.plays += 1

    def stop(self):
        self.state = "stop"
        self.stops += 1

    def unload(self):
        self.unloads += 1


class PortraitAudioTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        for filename in SOUND_FILES.values():
            (Path(self.directory.name) / filename).write_bytes(b"fake")
        self.loaded = {}

        def loader(path):
            clip = FakeClip()
            self.loaded[Path(path).name] = clip
            return clip

        self.audio = PortraitAudio(loader, root=self.directory.name)

    def test_advert_is_silent_and_tutorial_starts_once(self):
        self.assertFalse(self.audio.enter_page("advert"))
        self.assertNotIn("meong-v2-music.wav", self.loaded)
        self.assertTrue(self.audio.enter_page("tutorial"))
        clip = self.loaded["meong-v2-music.wav"]
        self.assertTrue(clip.loop)
        self.assertEqual(clip.plays, 1)
        self.audio.enter_page("templates")
        self.assertEqual(clip.plays, 1)
        self.assertTrue(self.audio.enter_page("templates"))
        self.assertEqual(clip.plays, 1)
        self.audio.enter_page("advert")
        self.assertEqual(clip.state, "stop")
        self.assertEqual(clip.volume, 0)

    def test_in_game_preview_has_no_legacy_music_overlap(self):
        self.audio.enter_page("tutorial")
        clip = self.loaded["meong-v2-music.wav"]
        self.assertFalse(self.audio.enter_page("game_preview"))
        self.assertEqual(clip.state, "stop")

    def test_volume_zero_mutes_and_does_not_restart(self):
        self.audio.enter_page("tutorial")
        clip = self.loaded["meong-v2-music.wav"]
        self.assertFalse(self.audio.set_music_gain(0))
        self.assertEqual(clip.state, "stop")
        self.assertTrue(self.audio.set_music_gain(.3))
        self.assertEqual(clip.plays, 2)
        self.assertAlmostEqual(clip.volume, .3)

    def test_effects_do_not_play_over_advertisements(self):
        self.assertFalse(self.audio.cue("button"))
        self.assertNotIn("meong-v2-button.wav", self.loaded)
        self.audio.enter_page("tutorial")
        self.assertTrue(self.audio.cue("button"))
        clip = self.loaded["meong-v2-button.wav"]
        self.assertEqual(clip.plays, 1)
        self.audio.enter_page("advert")
        self.assertFalse(self.audio.cue("button"))
        self.assertEqual(clip.plays, 1)

    def test_suspend_resume_and_cleanup(self):
        self.audio.enter_page("tutorial")
        music = self.loaded["meong-v2-music.wav"]
        self.audio.suspend()
        self.assertEqual(music.state, "stop")
        self.assertFalse(self.audio.cue())
        self.audio.resume()
        self.assertEqual(music.plays, 2)
        self.assertTrue(self.audio.test_music())
        self.assertEqual(music.plays, 3)
        self.audio.close()
        self.assertEqual(music.unloads, 1)

    def test_missing_assets_fail_softly(self):
        missing = PortraitAudio(lambda path: FakeClip(), root=Path(self.directory.name) / "missing")
        self.assertFalse(missing.enter_page("tutorial"))
        self.assertIn("unavailable", missing.status()["last_error"])

    def test_disabled_audio_never_attempts_loading(self):
        offline = PortraitAudio(lambda path: self.fail("should not load"), root=self.directory.name, enabled=False)
        self.assertFalse(offline.enter_page("tutorial"))
        self.assertFalse(offline.cue("button"))
        self.assertFalse(offline.test_music())

    def test_bundled_original_wav_paths_exist(self):
        for filename in SOUND_FILES.values():
            self.assertTrue((BUNDLED_SOUNDS / filename).is_file(), filename)

    def test_unknown_pages_and_gain_bounds(self):
        with self.assertRaises(ValueError):
            self.audio.enter_page("payment_paid")
        with self.assertRaises(ValueError):
            self.audio.cue("unknown")
        self.assertEqual(bounded_gain(-5), 0)
        self.assertEqual(bounded_gain(3), 1)
        self.assertEqual(bounded_gain(float("nan")), 0)



class WavProviderSelectionTests(unittest.TestCase):
    """Provider fallback tests use fake handles; no speaker is asserted."""

    def test_valid_primary_does_not_load_secondary(self):
        primary = FakeClip()
        primary.length = 4.0
        calls = []

        def first():
            calls.append("SDL2")
            return primary

        def second():
            calls.append("fallback")
            return FakeClip()

        self.assertIs(select_pcm_handle([("SDL2", first), ("other", second)]), primary)
        self.assertEqual(calls, ["SDL2"])
        self.assertEqual(primary.unloads, 0)

    def test_invalid_zero_length_primary_is_unloaded_then_falls_back(self):
        primary, fallback = FakeClip(), FakeClip()
        primary.length = 0
        fallback.length = 1.25
        resolved = select_pcm_handle([
            ("SDL2", lambda: primary),
            ("fallback", lambda: fallback),
        ])
        self.assertIs(resolved, fallback)
        self.assertEqual(primary.unloads, 1)
        self.assertEqual(fallback.unloads, 0)

    def test_broken_primary_loader_does_not_block_valid_fallback(self):
        fallback = FakeClip()
        fallback.length = 1.5

        def broken():
            raise RuntimeError("bad backend")

        self.assertIs(select_pcm_handle([
            ("SDL2", broken), ("fallback", lambda: fallback),
        ]), fallback)

    def test_nan_and_missing_durations_are_not_accepted(self):
        invalid = FakeClip()
        invalid.length = float("nan")
        missing = FakeClip()
        self.assertIsNone(select_pcm_handle([
            ("nan", lambda: invalid), ("missing", lambda: missing),
        ]))
        self.assertEqual(invalid.unloads, 1)
        self.assertEqual(missing.unloads, 1)

    def test_music_play_request_is_not_success_if_provider_remains_stopped(self):
        with TemporaryDirectory() as directory:
            (Path(directory) / SOUND_FILES["music"]).write_bytes(b"fake")

            class UnresponsiveClip(FakeClip):
                def play(self):
                    self.plays += 1  # Sound driver ignores the request.
                    self.state = "stop"

            audio = PortraitAudio(lambda _path: UnresponsiveClip(), root=directory)
            self.assertFalse(audio.enter_page("tutorial"))
            self.assertEqual(audio.status()["music_state"], "stop")
            self.assertIn("did not acknowledge", audio.status()["last_error"])
            audio.close()


if __name__ == "__main__":
    unittest.main()
