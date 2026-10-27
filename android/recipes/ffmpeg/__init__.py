"""Pinned FFmpeg 6.1 LTS source; retain p4a's cross compiler/build procedure.

ffmpeg.org returned repeated HTTP 503 in the managed build. The official
FFmpeg 8 removes avfft/channel APIs still required by ffpyplayer. Use the latest
observed 6.1 LTS tag n6.1.6 (f1e3a2b), with a fixed official archive hash.
Software decoding avoids the old MediaCodec Android 15 binder issue.
"""
from pathlib import Path
from pythonforandroid.recipes import ffmpeg as upstream


class MirroredFFmpeg(upstream.FFMpegRecipe):
    version = '6.1.6'
    url = 'https://github.com/FFmpeg/FFmpeg/archive/f1e3a2bf7a2f2cde936d1ed97f09a26853d20125.tar.gz'
    sha256sum = 'a6812d1f3d955450b8b8a4897551b93e4f7d26b173b5d39949893f578f318859'
    patches = ['software-preview.patch']


recipe = MirroredFFmpeg()
