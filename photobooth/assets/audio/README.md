# Original offline music and sound cues

> **CURRENT (2026-10-19, `feature/kivy-gui`):** Original bundled WAVs remain the Kivy music/SFX source. **Actual GUI route:** header gear → **Pengaturan Meong** → **PENGATURAN AUDIO**. An explicit **UJI MUSIK** press requests a fresh playback to diagnose silent devices; normal background music avoids unwanted restarting across pages. The Settings/music test code now covers this logic, but **audible Windows music remains an unresolved/deferred owner issue (BUG-001/007)**; synthetic CI does not prove loudspeaker output.

All WAVs in this folder are synthesized by `photobooth/audio.py`, using original
note sequences and deterministic instruments/noise. They contain no sampled
commercial recording or transcription of a game's melody.

**Meong's Little Photo Garden** is a 40-second, 16-bar loop at 96 BPM, with a
flute-like lead, harp arpeggios, triangle bass, bell accents and soft shakers.
Its cheerful farming/adventure atmosphere follows the user's Harvest Moon /
The Legend of Zelda: The Minish Cap direction.

| File | Duration | Use | Volume bus |
| --- | ---: | --- | --- |
| `meong-v2-music.wav` | 40.00 s | Persistent background loop | Music |
| `meong-v2-button.wav` | 0.16 s | Accepted button action | Buttons |
| `meong-v2-count.wav` | 0.20 s | Once per displayed countdown second | Effects |
| `meong-v2-shutter.wav` | 0.23 s | Successful photo save | Effects |
| `meong-v2-success.wav` | 0.90 s | Saved result first presented | Effects |

Every file is mono, signed 16-bit little-endian PCM at 22,050 Hz. Short fades
remove edge clicks; bounded peaks leave mixing headroom. Runtime playback reads
these shipped files. A missing/truncated sample is rebuilt into `data/audio`
without writing into this asset directory. `levels.json` remains under
`data/audio`, preserving the user's independent gains and 0% mute settings.
The new `v2` names bypass any older generated `v1` cache.

To regenerate the committed bank after intentionally editing the score, run
from the repository root:

```python
from photobooth.audio import BUNDLED_AUDIO_DIR, SOUND_NAMES, ASSET_VERSION, prepare_assets

# A valid file is normally reused. Remove the old version's outputs first when
# rebuilding an edited score; bump ASSET_VERSION before shipping changed bytes.
for name in SOUND_NAMES:
    (BUNDLED_AUDIO_DIR / f"meong-{ASSET_VERSION}-{name}.wav").unlink(missing_ok=True)
prepare_assets(BUNDLED_AUDIO_DIR, bundled_directory=None)
```

Use the header gear → **Pengaturan Meong** → **PENGATURAN AUDIO** to
adjust music, button, camera and advertisement gains, run Uji previews, inspect
output diagnostics or retry loading after an output problem. **Uji** respects
the selected volume; 0% stays muted. Explicit **UJI MUSIK** intentionally
restarts the music sound handle for an audible audition; ordinary background
music transitions do **not** restart an already playing loop. On desktop,
the app prefers SDL2 for these WAVs; an explicitly set `KIVY_AUDIO` retains
provider selection. Physical Windows speaker output still needs owner validation.
