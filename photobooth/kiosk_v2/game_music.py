"""Asteroid Chase: original minor-key 128 BPM loop, using the existing synth.

Offline generation only. Runtime reads the bundled PCM WAV; no synthesis on tap.
Regenerate with ``python -m photobooth.kiosk_v2.game_music``.
"""

from pathlib import Path
import wave

SAMPLE_RATE = 22050
BPM = 128
BARS = 16
DURATION = BARS*4*60/BPM


def game_music_pcm():
    import numpy as np
    from photobooth.audio import _note

    beat = 60/BPM
    samples = np.zeros(round(DURATION*SAMPLE_RATE), dtype=np.float64)
    rng = np.random.default_rng(20261024)
    chords = ((50,53,57),(46,50,53),(43,46,50),(45,49,52))
    for bar in range(BARS):
        chord = chords[bar%4]
        for step in range(16):
            _note(samples,bar*4+step*.25,.23,chord[(0,2,1,2)[step%4]]+12,.105,
                  beat_seconds=beat,sample_rate=SAMPLE_RATE)
        for step in range(8):
            _note(samples,bar*4+step*.5,.42,chord[0]-12,.20,voice='bass',
                  beat_seconds=beat,sample_rate=SAMPLE_RATE)
        for offset in (0,2):
            begin=round((bar*4+offset)*beat*SAMPLE_RATE)
            t=np.arange(round(.13*SAMPLE_RATE))/SAMPLE_RATE
            samples[begin:begin+len(t)] += .14*np.sin(2*np.pi*(95*t-170*t*t))*np.exp(-t*32)
        for offset in (1,3):
            begin=round((bar*4+offset)*beat*SAMPLE_RATE)
            t=np.arange(round(.09*SAMPLE_RATE))/SAMPLE_RATE
            samples[begin:begin+len(t)] += rng.uniform(-1,1,len(t))*np.exp(-t*60)*.035
        if bar>=4:
            for offset,pitch in ((.5,chord[2]+24),(1.75,chord[1]+24),(2.5,chord[0]+24)):
                _note(samples,bar*4+offset,.4,pitch,.065,voice='bell',
                      beat_seconds=beat,sample_rate=SAMPLE_RATE)
    samples -= samples.mean()
    gain=min(.17/max(float(np.sqrt(np.mean(samples*samples))),1e-9),
             .70/max(float(np.max(np.abs(samples))),1e-9))
    samples *= gain
    fade=round(SAMPLE_RATE*.008)
    samples[:fade] *= np.linspace(0,1,fade)
    samples[-fade:] *= np.linspace(1,0,fade)
    pcm=np.rint(samples*32767).astype('<i2')
    pcm[0]=pcm[-1]=0
    return pcm.tobytes()


def write_game_music(path):
    with wave.open(str(path),'wb') as stream:
        stream.setparams((1,2,SAMPLE_RATE,0,'NONE','not compressed'))
        stream.writeframes(game_music_pcm())


if __name__=='__main__':
    write_game_music(Path(__file__).resolve().parents[1]/'assets'/'audio'/'meong-v2-game-chase.wav')
