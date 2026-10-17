"""Standalone Windows audio-output diagnostic; does not launch the kiosk.

Run: python tools/check_audio_output.py
Listen for music during a 5-second interval. Successful Kivy state alone is
not proof that sound reached Windows' selected speaker.
"""
import os
import time
from pathlib import Path

from photobooth.audio import BUNDLED_AUDIO_DIR, load_native_sound

def main():
    path = BUNDLED_AUDIO_DIR / "meong-v2-music.wav"
    print("WAV:", path, "exists:", path.is_file())
    print("PHOTOBOOTH_AUDIO:", os.environ.get("PHOTOBOOTH_AUDIO", "<unset>"))
    print("KIVY_AUDIO:", os.environ.get("KIVY_AUDIO", "<unset>"))
    print("SDL_AUDIODRIVER:", os.environ.get("SDL_AUDIODRIVER", "<unset>"))
    sound = load_native_sound(path)
    if sound is None:
        print("ERROR: Kivy could not load the native music sound.")
        return 1
    print("Provider:", type(sound).__name__, "duration:", sound.length)
    try:
        sound.loop = True
        sound.volume = 1.0
        sound.play()
        print("Music state:", sound.state)
        print("LISTEN NOW for 5 seconds. Check Windows Volume Mixer for Python.")
        time.sleep(5)
        print("State after 5 seconds:", sound.state)
    finally:
        sound.stop()
        sound.unload()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
