"""Repair idle SDL_mixer channel gains before allocating a GUI WAV channel.

ffpyplayer's Windows mixer backend sets channel volume independently of the WAV
chunk volume. A retired, muted video can leave its channel at zero. Kivy's
SoundSDL2 sets only chunk volume when reusing that channel, so state='play' can
remain completely silent. Never change the gain of a playing channel (e.g. ads).
"""

import ctypes
import sys
from functools import lru_cache


def restore_idle_channels(mixer):
    """Reset only unused channels; -1 is used solely for the count query."""
    for channel in range(mixer.Mix_AllocateChannels(-1)):
        if not mixer.Mix_Playing(channel):
            mixer.Mix_Volume(channel, 128)


@lru_cache(maxsize=1)
def loaded_mixer(provider_path):
    """Resolve the mixer already loaded by Kivy, without opening another device."""
    if sys.platform == "win32":
        # GetModuleHandle does not load/search DLLs. Using its handle also avoids
        # accidentally opening a different mixer than the one used by Kivy.
        get_module = ctypes.windll.kernel32.GetModuleHandleW
        get_module.argtypes = [ctypes.c_wchar_p]
        get_module.restype = ctypes.c_void_p
        module = get_module("SDL2_mixer.dll")
        if not module:
            raise RuntimeError("Kivy's loaded SDL2_mixer.dll was not found")
        mixer = ctypes.CDLL(None, handle=module)
    else:
        # POSIX dlsym includes dependencies of the already imported provider.
        mixer = ctypes.CDLL(provider_path)
    for name in ("Mix_AllocateChannels", "Mix_Playing"):
        function = getattr(mixer, name)
        function.argtypes = [ctypes.c_int]
        function.restype = ctypes.c_int
    mixer.Mix_Volume.argtypes = [ctypes.c_int, ctypes.c_int]
    mixer.Mix_Volume.restype = ctypes.c_int
    return mixer


def channel_safe_sound(path):
    from kivy.core.audio import audio_sdl2

    mixer = loaded_mixer(audio_sdl2.__file__)

    class ChannelSafeSoundSDL2(audio_sdl2.SoundSDL2):
        def play(self):
            # Release our own old channel first, including on automatic loops.
            self.stop()
            restore_idle_channels(mixer)
            super().play()

    return ChannelSafeSoundSDL2(source=str(path))
