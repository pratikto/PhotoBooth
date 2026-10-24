"""Bundled original game soundtrack and existing synth reuse."""

import array
import math
import unittest
import wave

from photobooth.kiosk_v2.audio import BUNDLED_SOUNDS,SOUND_FILES
from photobooth.kiosk_v2.game_music import game_music_pcm,DURATION,SAMPLE_RATE,BPM


class GameMusicTests(unittest.TestCase):
    def test_asset_is_a_distinct_bounded_30_second_loop_with_matching_pcm_format(self):
        path=BUNDLED_SOUNDS/SOUND_FILES['game_music']
        with wave.open(str(path),'rb') as stream:
            self.assertEqual((stream.getnchannels(),stream.getsampwidth(),stream.getframerate()),(1,2,SAMPLE_RATE))
            self.assertEqual(stream.getnframes(),round(DURATION*SAMPLE_RATE))
            values=array.array('h',stream.readframes(stream.getnframes()))
        self.assertEqual((values[0],values[-1]),(0,0))
        self.assertGreater(max(abs(v) for v in values),10000)
        self.assertLessEqual(max(abs(v) for v in values),23000)
        self.assertGreater(math.sqrt(sum(v*v for v in values)/len(values)),1000)
        self.assertEqual(BPM,128)
        self.assertNotEqual(path.read_bytes(),(BUNDLED_SOUNDS/SOUND_FILES['music']).read_bytes())

    def test_existing_instrument_generator_is_deterministic(self):
        self.assertEqual(game_music_pcm(),game_music_pcm())


if __name__=='__main__':unittest.main()
