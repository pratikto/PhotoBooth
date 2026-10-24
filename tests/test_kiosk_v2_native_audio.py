"""Native SDL mixer regression: opt in with PHOTOBOOTH_TEST_AUDIO=1.

Verifies PCM at the dummy mixer output, not physical Windows speakers.
"""

import ctypes
import os
import time
import unittest


@unittest.skipUnless(os.environ.get("PHOTOBOOTH_TEST_AUDIO") == "1",
                     "native SDL mixer test requires PHOTOBOOTH_TEST_AUDIO=1")
class NativeChannelReuseTests(unittest.TestCase):
    def test_default_wav_loader_uses_native_channel_recovery_without_ffpyplayer(self):
        from unittest.mock import patch
        from kivy.core.audio import audio_sdl2
        from photobooth.kiosk_v2.audio import kivy_sound_loader, BUNDLED_SOUNDS, SOUND_FILES
        from photobooth.kiosk_v2.mixer import loaded_mixer

        with patch.dict(os.environ, {'KIVY_AUDIO': ''}), \
                patch('kivy.core.audio.SoundLoader.load') as fallback:
            sound = kivy_sound_loader()(BUNDLED_SOUNDS / SOUND_FILES['button'])
            self.assertIsNotNone(sound)
            fallback.assert_not_called()
            try:
                self.assertIsInstance(sound, audio_sdl2.SoundSDL2)
                mixer = loaded_mixer(audio_sdl2.__file__)
                # A real load/play on Windows exercises ctypes' platform-specific
                # name validation, which Linux-only native tests did not cover.
                sound.volume = .6
                sound.play()
                self.assertEqual(sound.state, 'play')
                active = [i for i in range(mixer.Mix_AllocateChannels(-1))
                          if mixer.Mix_Playing(i)]
                self.assertTrue(active)
                self.assertTrue(all(mixer.Mix_Volume(i, -1) > 0 for i in active))
            finally:
                sound.stop()
                sound.unload()

    def test_repeated_muted_video_channel_reuse_has_real_pcm_and_keeps_active_ad_gain(self):
        from kivy.core.audio import audio_sdl2
        from photobooth.kiosk_v2.audio import PortraitAudio, BUNDLED_SOUNDS, SOUND_FILES
        from photobooth.kiosk_v2.mixer import channel_safe_sound, loaded_mixer

        mixer = loaded_mixer(audio_sdl2.__file__)
        active = lambda: [i for i in range(mixer.Mix_AllocateChannels(-1))
                          if mixer.Mix_Playing(i)]
        # Reproduce the old silent state despite a valid native play response.
        old = audio_sdl2.SoundSDL2(source=str(BUNDLED_SOUNDS / SOUND_FILES['music']))
        old.volume = .6
        old.play()
        channel = active()[0]
        mixer.Mix_Volume(channel, 0)
        old.stop()
        old.play()
        try:
            self.assertEqual(old.state, 'play')
            self.assertEqual(mixer.Mix_Volume(active()[0], -1), 0)
        finally:
            old.stop()
            old.unload()

        # Observe actual signed PCM after mixing, avoiding state-only assertions.
        peaks = []
        callback_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p,
                                       ctypes.POINTER(ctypes.c_int16), ctypes.c_int)

        @callback_type
        def observe(_data, samples, length):
            peaks.append(max(abs(v) for v in samples[:length // 2]))

        mixer.Mix_SetPostMix.argtypes = [callback_type, ctypes.c_void_p]
        mixer.Mix_SetPostMix.restype = None
        def sample_output(seconds=.12):
            # Never hold a Python post-mix callback while a Cython SoundSDL2
            # method may wait for the mixer lock with the GIL held. Install the
            # probe only during sleep, and remove it (ctypes releases the GIL)
            # before any play/stop/unload. The GUI never installs this test probe.
            peaks.clear()
            mixer.Mix_SetPostMix(observe, None)
            try:
                time.sleep(seconds)
            finally:
                mixer.Mix_SetPostMix(callback_type(), None)
            return list(peaks)
        audio = PortraitAudio(channel_safe_sound)
        ad = audio_sdl2.SoundSDL2(source=str(BUNDLED_SOUNDS / SOUND_FILES['music']))
        ad.volume = .5
        try:
            for cycle in range(20):
                with self.subTest(cycle=cycle):
                    audio.enter_page('advert')
                    audio.set_ad_media('video')
                    # Emulate a decoder's muted channel just before retirement.
                    ad.play()
                    ad_channel = active()[0]
                    mixer.Mix_Volume(ad_channel, 0)
                    audio.cue('button')
                    # A concurrent GUI click must not unmute the playing ad.
                    self.assertEqual(mixer.Mix_Volume(ad_channel, -1), 0)
                    ad.stop()
                    for page in ('tutorial', 'templates', 'game_preview'):
                        audio.enter_page(page)
                        if page == 'game_preview':
                            # Only the click supplies PCM on this silent page.
                            for clip in audio._handles.values():
                                if clip is not None:
                                    clip.stop()
                        self.assertTrue(audio.cue('button'))
                        output = sample_output()
                        self.assertTrue(output and max(output) > 50, 'native output was silent')
                    audio.enter_page('advert')
                    # A real distinct game loop must emit PCM by itself, not
                    # merely report state=play or borrow the click's samples.
                    audio.enter_page('game_play')
                    audio._handles['button'].stop()
                    self.assertEqual(audio._handles['music'].state,'stop')
                    self.assertEqual(audio._handles['game_music'].state,'play')
                    self.assertEqual(len(active()),1,'more than one music channel')
                    output=sample_output()
                    self.assertTrue(output and max(output)>50,'game soundtrack PCM was silent')
                    audio.enter_page('advert')
                    self.assertTrue(audio.set_ad_media('image'))
                    audio.suspend()
                    audio.resume()
                    output = sample_output()
                    self.assertTrue(output and max(output) > 50, 'music output was silent')
            audio.enter_page('templates')
            audio.set_music_gain(0)
            self.assertTrue(audio.cue('shutter'))
            output = sample_output(.12)
            self.assertTrue(output and max(output) > 50, 'new shutter PCM was silent')
            self.assertEqual(audio._handles['shutter'].source,
                             str(BUNDLED_SOUNDS / SOUND_FILES['shutter']))
            audio.close()
            output = sample_output(.22)
            self.assertTrue(output and output[-1] == 0, 'sound remained after close')
        finally:
            audio.close()
            ad.stop()
            ad.unload()
            mixer.Mix_SetPostMix(callback_type(), None)


if __name__ == '__main__':
    unittest.main()
