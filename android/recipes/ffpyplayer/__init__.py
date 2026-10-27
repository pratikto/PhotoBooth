"""Use current desktop v2's ffpyplayer release with the pinned p4a recipe."""
from pathlib import Path
from pythonforandroid.recipes import ffpyplayer as upstream


class CurrentFFPyPlayer(upstream.FFPyPlayerRecipe):
    version = 'v4.5.3'
    url = 'https://github.com/matham/ffpyplayer/archive/refs/tags/{version}.tar.gz'
    sha256sum = '413866ca00fad53f36de07362ca884dea54e55da2372293d2042888c68bd3eae'
    patches = [str(Path(upstream.__file__).parent/path) for path in upstream.FFPyPlayerRecipe.patches]


recipe = CurrentFFPyPlayer()
