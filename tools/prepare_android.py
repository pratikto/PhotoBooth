"""Create a curated Buildozer project; never build from the repository root."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ASSET_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.json', '.wav', '.gz', '.ttf', '.kv', '.atlas'}


def eligible(relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != 'photobooth':
        return False
    if any(p.casefold() in {'old', 'data', '__pycache__', '.git', '.venv', 'ad_video'} for p in path.parts):
        return False
    if path.name.startswith('local_settings'):
        return False
    return path.suffix == '.py' or ('assets' in path.parts and path.suffix.lower() in ASSET_EXTENSIONS)


def prepare(destination, *, root=ROOT):
    root = Path(root).absolute()
    if any(p.casefold() == 'old' for p in root.parts):
        raise ValueError('Archive paths are excluded')
    if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in (root, *root.parents)):
        raise ValueError('Linked source roots are excluded')
    destination = Path(destination).absolute()
    if destination.exists():
        raise ValueError('Destination exists; choose a fresh staging directory')
    if 'old' in [part.casefold() for part in destination.parts]:
        raise ValueError('Archive paths are excluded')
    if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in destination.parents):
        raise ValueError('Linked staging parents are excluded')
    paths = subprocess.run(['git', '-C', str(root), 'ls-files', '-z', '--', 'photobooth'],
                           check=True, capture_output=True).stdout.decode().split('\0')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='android-stage-', dir=destination.parent) as temporary:
        stage = Path(temporary) / 'project'
        stage.mkdir()
        hashes = {}
        selected = [(p, p) for p in paths if p and eligible(p)]
        # These explicit inputs also work before their first commit.
        selected.extend([('android/main.py', 'main.py'), ('android/buildozer.spec', 'buildozer.spec'),
                         ('photobooth/kiosk_v2/android_preview.py', 'photobooth/kiosk_v2/android_preview.py')])
        for source, target in selected:
            original = root / source
            if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)()
                   for p in (original, *original.parents)):
                raise ValueError('Linked source paths are excluded')
            if not original.is_file():
                raise ValueError('Required package input is missing')
            output = stage / target
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, output)
            hashes[target] = hashlib.sha256(output.read_bytes()).hexdigest()
        (stage / 'android-source-manifest.json').write_text(json.dumps(hashes, indent=2)+'\n')
        stage.rename(destination)
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    manifest = prepare(args.output_dir)
    print(f'Prepared {len(manifest)} source/assets. APK build and device acceptance have not run.')


if __name__ == '__main__':
    main()
