"""Build the curated Android project on Linux/WSL2 with workspace-local caches."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess

if __package__:
    from .prepare_android import prepare, ROOT
else:
    from prepare_android import prepare, ROOT


def verify_project(project):
    manifest = json.loads((project / 'android-source-manifest.json').read_text())
    for name, digest in manifest.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Invalid package manifest path')
        source = ROOT / ('android/' + name if name in {'main.py', 'buildozer.spec'} else name)
        target = project / name
        if (not target.is_file() or target.is_symlink() or
                hashlib.sha256(target.read_bytes()).hexdigest() != digest or
                not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != digest):
            raise ValueError('Staged source changed; prepare a fresh project: ' + name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-dir', type=Path, default=ROOT/'work/android-project')
    parser.add_argument('--cache-dir', type=Path, default=ROOT/'work/android-build-cache')
    parser.add_argument('--sdk-dir', type=Path)
    parser.add_argument('--ndk-dir', type=Path)
    parser.add_argument('--p4a-dir', type=Path, help='Optional checkout of the pinned p4a commit')
    parser.add_argument('--accept-sdk-license', action='store_true')
    parser.add_argument('--resume', action='store_true', help='Reuse a verified, unchanged staged project')
    args = parser.parse_args(argv)
    if sys.platform != 'linux':
        parser.error('Use Ubuntu or WSL2; native Windows cannot compile this APK')
    project, cache = args.project_dir.absolute(), args.cache_dir.absolute()
    for path in (project, cache):
        if any(part.casefold() == 'old' for part in path.parts):
            parser.error('Archive paths are excluded')
        if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)()
               for p in (path, *path.parents)):
            parser.error('Linked build/cache paths are excluded')
    if project == ROOT or project in ROOT.parents:
        parser.error('Build from a curated staging directory')
    if project.exists():
        if not args.resume:
            parser.error('Project exists; use --resume or choose a fresh --project-dir')
        verify_project(project)
    else:
        prepare(project)
    cache.mkdir(parents=True, exist_ok=True)
    # Keep HOME and runtime proxy/CA configuration intact. Build tools must not
    # place mutable SDK/Gradle/Android state into the developer home directory.
    for key, directory in {'GRADLE_USER_HOME':'gradle', 'ANDROID_USER_HOME':'android',
                           'XDG_CACHE_HOME':'cache', 'XDG_DATA_HOME':'share',
                           'XDG_CONFIG_HOME':'config', 'PIP_CACHE_DIR':'pip'}.items():
        os.environ.setdefault(key, str(cache/directory))
    os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', '')
    if sys.prefix != sys.base_prefix:
        os.environ['VIRTUAL_ENV'] = sys.prefix
    from buildozer import Buildozer
    from buildozer.logger import Logger
    # Buildozer's command-failure logger otherwise dumps the full environment.
    Logger.log_env = lambda self, level, env: self.log(level, 'Build environment omitted (may contain credentials)')

    class LocalBuildozer(Buildozer):
        @property
        def global_buildozer_dir(self):
            return str(cache/'buildozer')

    build = LocalBuildozer(str(project/'buildozer.spec'))
    if args.p4a_dir:
        revision = subprocess.run(['git', '-C', str(args.p4a_dir), 'rev-parse', 'HEAD'],
                                  check=True, capture_output=True, text=True).stdout.strip()
        if revision != build.config.get('app', 'p4a.commit'):
            parser.error('Local p4a checkout must match the pinned commit')
    for option, path in (('android.sdk_path', args.sdk_dir), ('android.ndk_path', args.ndk_dir),
                         ('p4a.source_dir', args.p4a_dir)):
        if path:
            build.config.set('app', option, str(path.absolute()))
    if args.sdk_dir:
        build.config.set('app', 'android.skip_update', 'True')
    if args.accept_sdk_license:
        build.config.set('app', 'android.accept_sdk_license', 'True')
    build.set_target('android')
    # Support the current official command-line-tools layout as well as the
    # legacy tools/bin location expected by Buildozer 1.6.
    original_target = type(build.target)

    class CommandLineToolsTarget(original_target):
        @property
        def sdkmanager_path(self):
            for path in ('cmdline-tools/latest/bin/sdkmanager', 'cmdline-tools/bin/sdkmanager',
                         'tools/bin/sdkmanager'):
                candidate = Path(self.android_sdk_dir)/path
                if candidate.is_file():
                    return str(candidate)
            return super().sdkmanager_path

    build.target.__class__ = CommandLineToolsTarget
    previous = Path.cwd()
    try:
        os.chdir(project)
        build.check_root()
        build.target.run_commands(['debug'])
    finally:
        os.chdir(previous)
    return 0


if __name__ == '__main__':
    sys.exit(main())
