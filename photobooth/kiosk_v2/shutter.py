"""Original v2 camera curtain cue; deterministic synthesis, no sampled audio.

Regenerate intentionally with ``python -m photobooth.kiosk_v2.shutter``.
Playback reads the shipped WAV, never generates audio in a capture callback.
"""

from array import array
import math
from pathlib import Path
import random
import sys
import wave

SAMPLE_RATE = 22050
DURATION = .30


def shutter_pcm():
    """Two rounded mechanical curtains with a warm body and a soft release."""
    rng = random.Random(20261023)
    samples = []
    low_noise = 0.0
    for index in range(round(SAMPLE_RATE * DURATION)):
        t = index / SAMPLE_RATE
        low_noise += .32 * (rng.uniform(-1, 1) - low_noise)
        value = 0.0
        for start, strength in ((.008, 1.0), (.081, .72)):
            age = t - start
            if age >= 0:
                attack = min(1.0, age / .0025)
                snap = low_noise * math.exp(-age / .012) * .95
                body = math.sin(2 * math.pi * (310 * age - 160 * age * age))
                body *= math.exp(-age / .023) * .26
                value += strength * attack * (snap + body)
        # Quiet spring return, rounded to avoid a sharp digital tail.
        if t >= .115:
            age = t - .115
            value += .055 * math.sin(2 * math.pi * 710 * age) * math.exp(-age / .025)
        value *= min(1.0, (DURATION - t) / .012)
        samples.append(value)
    mean = sum(samples) / len(samples)
    centered = [value - mean for value in samples]
    gain = .68 / max(abs(value) for value in centered)
    pcm = array('h', (round(value * gain * 32767) for value in centered))
    pcm[0] = pcm[-1] = 0
    if sys.byteorder != 'little':
        pcm.byteswap()
    return pcm.tobytes()


def write_shutter(path):
    with wave.open(str(path), 'wb') as output:
        output.setparams((1, 2, SAMPLE_RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(shutter_pcm())


if __name__ == '__main__':
    write_shutter(Path(__file__).resolve().parents[1] / 'assets' / 'audio' /
                  'meong-v2-shutter-soft.wav')
