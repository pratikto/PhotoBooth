"""Audio page ownership and fake-provider regression (not speaker verification)."""

from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch
import unittest

from photobooth.kiosk_v2.audio import (
    BUNDLED_SOUNDS, SOUND_FILES, PortraitAudio, bounded_gain, select_pcm_handle,
    kivy_sound_loader,
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
    def test_mock_checkout_preserves_one_music_stream_and_button_feedback(self):
        self.audio.enter_page('tutorial');music=self.loaded['meong-v2-music.wav']
        self.audio.enter_page('templates');self.audio.enter_page('mock_checkout')
        self.assertEqual(music.plays,1)
        self.assertTrue(self.audio.cue('button'))
        self.audio.suspend();self.assertEqual(music.state,'stop')
        self.audio.resume();self.assertEqual(music.plays,2)
        self.audio.enter_page('photo_confirm');self.assertEqual(music.plays,2)

    def test_new_shutter_is_original_bounded_pcm_and_does_not_replace_v1(self):
        import array
        import wave
        from photobooth.kiosk_v2.shutter import shutter_pcm, SAMPLE_RATE

        path = BUNDLED_SOUNDS / SOUND_FILES['shutter']
        self.assertNotEqual(path.name, 'meong-v2-shutter.wav')
        with wave.open(str(path), 'rb') as clip:
            self.assertEqual((clip.getnchannels(), clip.getsampwidth(), clip.getframerate()),
                             (1, 2, SAMPLE_RATE))
            pcm = clip.readframes(clip.getnframes())
            self.assertEqual(pcm, shutter_pcm())
            self.assertAlmostEqual(clip.getnframes() / SAMPLE_RATE, .30, places=3)
        values = array.array('h', pcm)
        self.assertGreater(max(values), 10000)
        self.assertLess(max(abs(value) for value in values), 23000)
        self.assertEqual((values[0], values[-1]), (0, 0))
        self.assertNotEqual(path.read_bytes(),
                            (BUNDLED_SOUNDS / 'meong-v2-shutter.wav').read_bytes())

    def test_channel_recovery_never_changes_a_playing_advertising_channel(self):
        from photobooth.kiosk_v2.mixer import restore_idle_channels

        class Mixer:
            gains = [0, 23, 0, 0]

            def Mix_AllocateChannels(self, count):
                self_query.assertEqual(count, -1)
                return 4

            def Mix_Playing(self, channel):
                return channel in (1, 2)

            def Mix_Volume(self, channel, gain):
                self_query.assertGreaterEqual(channel, 0)
                self.gains[channel] = gain

        self_query = self
        mixer = Mixer()
        restore_idle_channels(mixer)
        self.assertEqual(mixer.gains, [128, 23, 0, 128])

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
        for page in ('photo_confirm', 'capture', 'review', 'result'):
            self.assertTrue(self.audio.enter_page(page))
            self.assertEqual(clip.plays, 1, 'photo page restarted the music')
        self.audio.enter_page("advert")
        self.assertEqual(clip.state, "stop")
        self.assertEqual(clip.volume, 0)

    def test_idle_effect_prepare_is_silent_and_first_cue_reuses_its_handle(self):
        for name in ('count', 'shutter', 'success'):
            self.assertTrue(self.audio.prepare(names=(name,)))
        self.assertEqual(set(self.loaded), {SOUND_FILES[name] for name in ('count', 'shutter', 'success')})
        for clip in self.loaded.values():
            self.assertEqual((clip.volume, clip.plays), (0, 0))
        self.audio.enter_page('capture')
        for name in ('count', 'shutter', 'success'):
            clip = self.loaded[SOUND_FILES[name]]
            self.assertTrue(self.audio.cue(name))
            self.assertIs(self.loaded[SOUND_FILES[name]], clip)
            self.assertEqual(clip.plays, 1)

    def test_in_game_preview_has_no_legacy_music_overlap(self):
        self.audio.enter_page("tutorial")
        clip = self.loaded["meong-v2-music.wav"]
        self.assertFalse(self.audio.enter_page("game_preview"))
        self.assertEqual(clip.state, "stop")

    def test_demo_game_pages_keep_gui_music_off_and_single_click_owner_available(self):
        self.audio.enter_page('tutorial')
        music = self.loaded[SOUND_FILES['music']]
        for page in ('game_receipt', 'game_play', 'game_result'):
            self.assertFalse(self.audio.enter_page(page))
            self.assertEqual(music.state, 'stop')
            self.assertTrue(self.audio.cue('button'))
            self.assertFalse(self.audio.cue('shutter'))
        self.audio.enter_page('tutorial')
        self.assertEqual(music.plays, 2)

    def test_volume_zero_mutes_and_does_not_restart(self):
        self.audio.enter_page("tutorial")
        clip = self.loaded["meong-v2-music.wav"]
        self.assertFalse(self.audio.set_music_gain(0))
        self.assertEqual(clip.state, "stop")
        self.assertTrue(self.audio.set_music_gain(.3))
        self.assertEqual(clip.plays, 2)
        self.assertAlmostEqual(clip.volume, .3)

    def test_only_button_feedback_can_play_over_advert_and_game_preview(self):
        for page in ("advert", "game_preview"):
            self.audio.enter_page(page)
            self.assertTrue(self.audio.cue("button"))
            self.assertFalse(self.audio.cue("shutter"))
            self.assertFalse(self.audio.cue("count"))
        self.assertEqual(self.loaded[SOUND_FILES["button"]].plays, 2)
        self.assertNotIn(SOUND_FILES["music"], self.loaded)

    def test_image_music_yields_before_video_and_returns_for_next_image(self):
        self.audio.enter_page("advert")
        self.assertNotIn(SOUND_FILES["music"], self.loaded)
        self.assertTrue(self.audio.set_ad_media("image"))
        music = self.loaded[SOUND_FILES["music"]]
        self.audio.set_ad_media("image")
        self.assertEqual(music.plays, 1)
        self.audio.set_ad_media("video")
        self.assertEqual(music.state, "stop")
        self.audio.set_ad_media("image")
        self.assertEqual(music.plays, 2)
        self.audio.enter_page("tutorial")
        self.audio.enter_page("templates")
        self.assertEqual(music.plays, 2)
        self.audio.enter_page("advert")
        self.assertEqual(music.state, "stop")
        self.audio.set_ad_media("fallback")
        self.assertEqual(music.plays, 3)
        self.audio.suspend()
        self.audio.set_ad_media("video")
        self.audio.resume()
        self.assertEqual(music.state, "stop")
        with self.assertRaises(ValueError):
            self.audio.set_ad_media("unknown")

    def test_effects_stop_on_suspend_and_do_not_resume_as_stale_cues(self):
        self.audio.enter_page("tutorial")
        self.audio.cue("button")
        effect = self.loaded[SOUND_FILES["button"]]
        self.audio.suspend()
        self.assertEqual(effect.state, "stop")
        self.audio.resume()
        self.assertEqual(effect.state, "stop")
        self.assertEqual(effect.plays, 1)

    def test_page_handoff_preserves_immediate_click_but_stops_camera_effects(self):
        for page in ("advert", "game_preview"):
            self.audio.enter_page("tutorial")
            self.audio.cue("button")
            effect = self.loaded[SOUND_FILES["button"]]
            self.audio.cue('count')
            camera = self.loaded[SOUND_FILES['count']]
            self.audio.enter_page(page)
            self.assertEqual(effect.state, "play")
            self.assertEqual(camera.state, 'stop')
            self.assertFalse(self.audio.cue("shutter"))
            self.assertTrue(self.audio.cue("button"))

    def test_prepare_loads_once_silently_and_never_restarts_a_playing_song(self):
        self.assertTrue(self.audio.prepare())
        self.assertEqual(set(self.loaded), {SOUND_FILES['music'], SOUND_FILES['button']})
        for clip in self.loaded.values():
            self.assertEqual(clip.plays, 0)
            self.assertEqual(clip.volume, 0)
        self.audio.enter_page('tutorial')
        music = self.loaded[SOUND_FILES['music']]
        self.assertTrue(self.audio.prepare())
        self.assertEqual(music.plays, 1)
        self.assertEqual(music.volume, self.audio.music_gain)

    def test_prepare_during_suspend_or_disabled_audio_never_loads(self):
        self.audio.enabled = False
        self.assertFalse(self.audio.prepare())
        self.audio.enabled = True
        self.audio.suspend()
        self.assertFalse(self.audio.prepare())
        self.assertFalse(self.loaded)

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

    def test_return_from_game_preview_restores_music_only_on_allowed_page(self):
        self.audio.enter_page("tutorial")
        clip = self.loaded["meong-v2-music.wav"]
        self.audio.enter_page("game_preview")
        self.assertEqual(clip.state, "stop")
        self.assertEqual(self.audio.page, "game_preview")
        self.audio.enter_page("templates")
        self.assertEqual(clip.state, "play")
        self.assertEqual(clip.plays, 2)
        self.audio.enter_page("advert")
        self.assertEqual(clip.state, "stop")

    def test_close_then_reenter_does_not_reuse_unloaded_handle(self):
        self.audio.enter_page("tutorial")
        old = self.loaded["meong-v2-music.wav"]
        self.audio.close()
        self.assertEqual(old.unloads, 1)
        self.audio.resume()
        self.assertTrue(self.audio.enter_page("tutorial"))
        fresh = self.loaded["meong-v2-music.wav"]
        self.assertIsNot(old, fresh)
        self.assertEqual(fresh.plays, 1)

    def test_suspended_navigation_does_not_start_music(self):
        self.audio.suspend()
        self.assertFalse(self.audio.enter_page("tutorial"))
        self.assertNotIn("meong-v2-music.wav", self.loaded)
        self.audio.enter_page("templates")
        self.audio.resume()
        music = self.loaded["meong-v2-music.wav"]
        self.assertEqual(music.plays, 1)
        self.audio.enter_page("advert")
        self.assertEqual(music.state, "stop")

    def test_close_is_idempotent_for_loaded_effects(self):
        self.audio.enter_page("tutorial")
        self.assertTrue(self.audio.cue("button"))
        music = self.loaded["meong-v2-music.wav"]
        effect = self.loaded["meong-v2-button.wav"]
        self.audio.close()
        self.audio.close()
        self.assertEqual(music.unloads, 1)
        self.assertEqual(effect.unloads, 1)
        self.assertEqual(music.state, "stop")
        self.assertEqual(effect.state, "stop")

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


class WindowsAudioLoadingTests(unittest.TestCase):
    """Exercise Windows-only branches even on the Kivy-free Linux job."""

    def test_existing_windows_dll_handle_has_a_name_for_python312_ctypes(self):
        from photobooth.kiosk_v2 import mixer

        handle = 0x123456789ABC  # Do not truncate a 64-bit HMODULE.
        get_module = Mock(return_value=handle)
        functions = SimpleNamespace(Mix_AllocateChannels=Mock(), Mix_Playing=Mock(),
                                    Mix_Volume=Mock())

        def windows_cdll(name, *, handle):
            # CPython 3.12 on Windows performs this check even with a handle.
            if '/' in name or '\\' in name:
                raise AssertionError('The loaded module should not be searched by path')
            return functions

        with patch.object(mixer.sys, 'platform', 'win32'), \
                patch.object(mixer.ctypes, 'windll',
                             SimpleNamespace(kernel32=SimpleNamespace(GetModuleHandleW=get_module)),
                             create=True), \
                patch.object(mixer.ctypes, 'CDLL', side_effect=windows_cdll) as dll:
            self.assertIs(mixer.loaded_mixer.__wrapped__('audio_sdl2.pyd'), functions)
            dll.assert_called_once_with('SDL2_mixer.dll', handle=handle)
            get_module.assert_called_once_with('SDL2_mixer.dll')
            self.assertIs(get_module.restype, mixer.ctypes.c_void_p)

    def test_missing_windows_mixer_is_not_loaded_from_another_location(self):
        from photobooth.kiosk_v2 import mixer

        with patch.object(mixer.sys, 'platform', 'win32'), \
                patch.object(mixer.ctypes, 'windll',
                             SimpleNamespace(kernel32=SimpleNamespace(GetModuleHandleW=Mock(return_value=0))),
                             create=True), patch.object(mixer.ctypes, 'CDLL') as dll:
            with self.assertRaisesRegex(RuntimeError, 'loaded SDL2_mixer'):
                mixer.loaded_mixer.__wrapped__('audio_sdl2.pyd')
            dll.assert_not_called()

    @contextmanager
    def windows_providers(self, wrapped, native, *, override=''):
        # No Kivy/device import: the pure job must cover Windows fallback policy.
        modules = {name: ModuleType(name) for name in
                   ('kivy', 'kivy.core', 'kivy.core.audio', 'kivy.utils',
                    'kivy.core.audio.audio_sdl2')}
        fallback = Mock(name='SoundLoader.load')
        modules['kivy.core.audio'].SoundLoader = SimpleNamespace(load=fallback)
        modules['kivy.core.audio.audio_sdl2'].SoundSDL2 = native
        modules['kivy.utils'].platform = 'win'
        with patch.dict('sys.modules', modules), patch.dict('os.environ', {'KIVY_AUDIO': override}), \
                patch('photobooth.kiosk_v2.mixer.channel_safe_sound', wrapped):
            yield kivy_sound_loader(), fallback

    def test_windows_wrapper_failure_uses_plain_sdl_without_starting_ffpyplayer(self):
        native = FakeClip()
        native.length = 40
        factory = Mock(return_value=native)
        with self.windows_providers(Mock(side_effect=TypeError('Windows ctypes failure')), factory) as (load, ff):
            self.assertIs(load('music.wav'), native)
            factory.assert_called_once_with(source='music.wav')
            ff.assert_not_called()

    def test_windows_sdl_failure_keeps_gui_audio_unavailable_instead_of_native_ffmpeg_fallback(self):
        with self.windows_providers(Mock(side_effect=OSError('wrapper unavailable')),
                                    Mock(side_effect=OSError('SDL unavailable'))) as (load, ff):
            self.assertIsNone(load('music.wav'))
            ff.assert_not_called()

    def test_explicit_windows_audio_override_still_uses_requested_provider(self):
        wrapped, native = Mock(), Mock()
        with self.windows_providers(wrapped, native, override='ffpyplayer') as (load, ff):
            requested = FakeClip()
            requested.length = 1
            ff.return_value = requested
            self.assertIs(load('music.wav'), requested)
            wrapped.assert_not_called()
            native.assert_not_called()
            ff.assert_called_once_with('music.wav')


if __name__ == "__main__":
    unittest.main()
