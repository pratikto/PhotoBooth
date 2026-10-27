"""Verify built APK metadata and nested native libraries, without extracting files.

Run after apksigner and aapt in the existing Android build workflow. The JSON
describes binary checks only, never installation or physical-device acceptance.
"""
import argparse
import configparser
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import tarfile
import zipfile


def verify_badging(text, spec):
    config = configparser.ConfigParser()
    config.read_string(spec)
    app = config['app']
    package = re.search(r"^package: name='([^']+)'[^\n]*versionName='([^']+)'", text, re.M)
    expected = app['package.domain'] + '.' + app['package.name']
    if not package or package.groups() != (expected, app['version']):
        raise ValueError('APK package/version does not match staged buildozer.spec')
    for field, option in [('sdkVersion', 'android.minapi'), ('targetSdkVersion', 'android.api')]:
        match = re.search(r"^" + field + r":'([0-9]+)'$", text, re.M)
        if not match or match[1] != app[option]:
            raise ValueError('APK API mismatch: ' + field)
    permissions = set(re.findall(r"^uses-permission(?:-sdk-\d+)?: name='([^']+)'", text, re.M))
    expected_permissions = {'android.permission.' + p.strip()
                            for p in app.get('android.permissions', '').split(',') if p.strip()}
    if permissions != expected_permissions:
        raise ValueError('APK permissions differ from staged buildozer.spec')
    native = re.search(r'^native-code:(.*)$', text, re.M)
    abis = set(re.findall(r"'([^']+)'", native[1])) if native else set()
    if abis != {'arm64-v8a'} or app['android.archs'].strip() != 'arm64-v8a':
        raise ValueError('APK must contain only arm64-v8a')
    return {'package': package[1], 'version_name': package[2],
            'permissions': sorted(permissions), 'abi': 'arm64-v8a',
            'minimum_api': int(app['android.minapi']), 'target_api': int(app['android.api'])}


def verify_native(apk):
    """Reuse the workflow's ELF check, including p4a's gzip Python payload."""
    count = 0

    def check(name, blob):
        nonlocal count
        if (len(blob) < 20 or blob[:4] != b'\x7fELF' or blob[4:6] != b'\x02\x01'
                or struct.unpack_from('<H', blob, 18)[0] != 183):
            raise ValueError('Not a little-endian AArch64 ELF64 library: ' + name)
        count += 1

    with zipfile.ZipFile(apk) as archive:
        bundles = 0
        for name in archive.namelist():
            if name.startswith('lib/') and name.endswith('.so'):
                if not name.startswith('lib/arm64-v8a/'):
                    raise ValueError('Foreign ABI directory: ' + name)
                blob = archive.read(name)
                if name.endswith('/libpybundle.so'):
                    bundles += 1
                    extensions = 0
                    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:*') as bundle:
                        for entry in bundle:
                            if entry.name.endswith('.so'):
                                if not entry.isfile():
                                    raise ValueError('Python native extension is not a regular file')
                                check(entry.name, bundle.extractfile(entry).read())
                                extensions += 1
                    if not extensions:
                        raise ValueError('Python bundle contains no native extensions')
                else:
                    check(name, blob)
        if not count or bundles != 1:
            raise ValueError('APK must contain native libraries and one Python bundle')
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('apk', type=Path)
    parser.add_argument('--badging', required=True, type=Path)
    parser.add_argument('--spec', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    if args.output.resolve() in {p.resolve() for p in (args.apk, args.badging, args.spec)}:
        parser.error('Report output must not replace a verification input')
    # A failed rerun must not leave an older PASS report at the requested path.
    args.output.unlink(missing_ok=True)
    result = verify_badging(args.badging.read_text(), args.spec.read_text())
    result.update(arm64_native_libraries=verify_native(args.apk),
                  sha256=hashlib.sha256(args.apk.read_bytes()).hexdigest(),
                  bytes=args.apk.stat().st_size, android_device_acceptance='NOT_RUN')
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
