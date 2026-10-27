"""Reject stale preview APKs and foreign native payloads before distribution."""
import io
from pathlib import Path
import struct
import tarfile
import tempfile
import unittest
import zipfile

from tools.verify_android_apk import main, verify_badging, verify_native

ROOT = Path(__file__).resolve().parents[1]
SPEC = (ROOT / 'android/buildozer.spec').read_text()
BADGING = """package: name='id.meong.meongpreview' versionCode='1024200' versionName='0.2.0'
sdkVersion:'24'
targetSdkVersion:'35'
uses-permission: name='android.permission.CAMERA'
uses-permission: name='android.permission.INTERNET'
native-code: 'arm64-v8a'
"""


def elf(machine=183):
    blob = bytearray(64)
    blob[:6] = b'\x7fELF\x02\x01'
    struct.pack_into('<H', blob, 18, machine)
    return bytes(blob)


def apk(path, extension=None, *, bundle=True, abi='arm64-v8a'):
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('lib/' + abi + '/libmain.so', elf())
        if bundle:
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode='w:gz') as payload:
                content = elf() if extension is None else extension
                member = tarfile.TarInfo('_python_bundle/site-packages/native.so')
                member.size = len(content)
                payload.addfile(member, io.BytesIO(content))
            archive.writestr('lib/' + abi + '/libpybundle.so', stream.getvalue())


class AndroidApkTests(unittest.TestCase):
    def test_runtime_identity_and_exact_permissions(self):
        result = verify_badging(BADGING, SPEC)
        self.assertEqual(result['version_name'], '0.2.0')
        self.assertEqual(result['permissions'], ['android.permission.CAMERA', 'android.permission.INTERNET'])

    def test_rejects_old_preview_wrong_api_permission_and_abi(self):
        changes = [('0.2.0', '0.1.0'), ('id.meong.meongpreview', 'id.other.app'),
                   ("sdkVersion:'24'", "sdkVersion:'23'"),
                   ("targetSdkVersion:'35'", "targetSdkVersion:'34'"),
                   ("uses-permission: name='android.permission.CAMERA'\n", ''),
                   ("'arm64-v8a'", "'arm64-v8a' 'x86_64'")]
        for before, after in changes:
            with self.subTest(before=before), self.assertRaises(ValueError):
                verify_badging(BADGING.replace(before, after), SPEC)
        with self.assertRaises(ValueError):
            verify_badging(BADGING + "uses-permission-sdk-23: name='android.permission.READ_EXTERNAL_STORAGE'\n", SPEC)

    def test_checks_python_bundle_as_well_as_outer_libraries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'runtime.apk'
            apk(path)
            self.assertEqual(verify_native(path), 2)
            for content in [elf(62), b'not ELF', elf()[:19]]:
                apk(path, content)
                with self.subTest(content=content[:6]), self.assertRaises(ValueError):
                    verify_native(path)
            apk(path, bundle=False)
            with self.assertRaises(ValueError):
                verify_native(path)
            apk(path, abi='x86_64')
            with self.assertRaises(ValueError):
                verify_native(path)

    def test_report_identifies_bytes_and_removes_stale_success_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, badging, spec, output = [root / n for n in ['runtime.apk', 'badging', 'spec', 'report.json']]
            apk(path)
            badging.write_text(BADGING)
            spec.write_text(SPEC)
            args = [str(path), '--badging', str(badging), '--spec', str(spec), '--output', str(output)]
            self.assertEqual(main(args), 0)
            self.assertIn('"android_device_acceptance": "NOT_RUN"', output.read_text())
            badging.write_text(BADGING.replace('0.2.0', '0.1.0'))
            with self.assertRaises(ValueError):
                main(args)
            self.assertFalse(output.exists())

    def test_report_cannot_overwrite_apk_or_other_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = [root / name for name in ('app.apk', 'badging', 'spec')]
            for path in inputs:
                path.write_bytes(b'preserve')
            for output in inputs:
                with self.subTest(output=output.name), self.assertRaises(SystemExit):
                    main([str(inputs[0]), '--badging', str(inputs[1]), '--spec', str(inputs[2]),
                          '--output', str(output)])
                self.assertEqual(output.read_bytes(), b'preserve')


if __name__ == '__main__':
    unittest.main()
