"""Safety/command-boundary tests; never open devices or perform cloud writes."""
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from tools import start_post_preview_device_test as entry


class PhysicalDeviceEntryTests(unittest.TestCase):
    @contextmanager
    def booth(self, *, ready=True, code=0, extra_env=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)/'repo'; root.mkdir()
            capture = io.StringIO()
            env = {name:'0' for name in entry.CONFLICTING_PROFILES}
            env.update(extra_env or {})
            with patch.object(entry, 'ROOT', root), patch.object(entry, 'source_head', return_value='a'*40), \
                 patch.object(entry, 'inspect', return_value={'status':'READY_FOR_SUPERVISED_SYNTHETIC_PILOT' if ready else 'BLOCKED','checks':[]}) as preflight, \
                 patch.object(entry.subprocess, 'run', return_value=SimpleNamespace(returncode=code)) as child, \
                 patch.dict(os.environ, env), redirect_stdout(capture), redirect_stderr(capture):
                yield root, child, preflight, capture

    def test_check_only_is_read_only_and_opens_no_child_or_device(self):
        with self.booth() as (root, child, _, _):
            self.assertEqual(0, entry.main(['--check-only']))
            child.assert_not_called()
            self.assertEqual([], list(root.iterdir()))

    def test_blocked_preflight_cannot_create_trial_or_launch(self):
        with self.booth(ready=False) as (root, child, _, _):
            self.assertEqual(2, entry.main([]))
            child.assert_not_called()
            self.assertEqual([], list(root.iterdir()))

    def test_generated_roots_are_unique_and_child_starts_before_root_is_occupied(self):
        with self.booth() as (root, child, _, _):
            roots=[]
            def launched(command, **kwargs):
                selected=Path(command[command.index('--private-root')+1])
                self.assertFalse(selected.exists())
                self.assertIn('--synthetic-payment-only', command)
                self.assertEqual('452x900', command[command.index('--size')+1])
                roots.append(selected)
                return SimpleNamespace(returncode=0)
            child.side_effect=launched
            self.assertEqual(0, entry.main([]))
            self.assertEqual(0, entry.main([]))
            self.assertEqual(2, len(set(roots)))
            reports=list((root/'work'/'postpay-device-reports').glob('*/session.json'))
            self.assertEqual(2, len(reports))
            for report in reports:
                record=json.loads(report.read_text())
                self.assertEqual('CLOSED_NOT_ACCEPTED', record['state'])
                self.assertEqual('NOT_RUN', record['hardware_acceptance'])
                self.assertEqual('SYNTHETIC_ONLY', record['payment'])

    def test_child_gets_physical_camera_and_isolated_flags_without_changing_parent(self):
        with self.booth(extra_env={'PHOTOBOOTH_CAMERA':'0','PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'1'}) as (_, child, preflight, _):
            self.assertEqual(0, entry.main(['--camera-index','2','--size','800x1280']))
            environment=child.call_args.kwargs['env']
            self.assertEqual('1', environment['PHOTOBOOTH_CAMERA'])
            self.assertEqual('2', environment['PHOTOBOOTH_CAMERA_INDEX'])
            self.assertEqual('0', environment['PHOTOBOOTH_V2_CHECKOUT_SANDBOX'])
            self.assertEqual(environment, preflight.call_args.kwargs['environment'])
            self.assertEqual('0', os.environ['PHOTOBOOTH_CAMERA'])
            self.assertEqual('1', os.environ['PHOTOBOOTH_V2_CHECKOUT_SANDBOX'])

    def test_headless_drivers_are_removed_only_from_physical_child(self):
        original={'SDL_VIDEODRIVER':'offscreen','SDL_AUDIODRIVER':'dummy'}
        child=entry.child_environment(original,0)
        self.assertNotIn('SDL_VIDEODRIVER',child)
        self.assertNotIn('SDL_AUDIODRIVER',child)
        self.assertEqual('offscreen',original['SDL_VIDEODRIVER'])
        real=entry.child_environment({'SDL_VIDEODRIVER':'windows','SDL_AUDIODRIVER':'wasapi'},0)
        self.assertEqual('windows',real['SDL_VIDEODRIVER'])
        self.assertEqual('wasapi',real['SDL_AUDIODRIVER'])

    def test_paper_and_public_upload_require_both_original_consents(self):
        for arg in ('--enable-real-printer','--accept-real-paper','--enable-real-drive','--accept-public-test-upload'):
            with self.subTest(arg=arg), self.booth() as (root, child, _, _):
                self.assertEqual(2, entry.main([arg]))
                child.assert_not_called()
                self.assertEqual([], list(root.iterdir()))

    def test_explicit_paper_cloud_modes_forward_only_original_flags_and_redact_metadata(self):
        secret='PRIVATE-UPLOAD-TOKEN-NEVER-LOG'
        env={'PHOTOBOOTH_PRINTER_WINDOWS_NAME':'OWNED-POS80',
             'PHOTOBOOTH_WEB_APP_URL':'https://script.google.com/macros/s/TEST/exec',
             'PHOTOBOOTH_UPLOAD_TOKEN':secret}
        flags=['--enable-real-printer','--accept-real-paper','--enable-real-drive','--accept-public-test-upload']
        with self.booth(extra_env=env) as (root, child, _, capture):
            self.assertEqual(0, entry.main(flags))
            command=child.call_args.args[0]
            for flag in flags: self.assertIn(flag,command)
            self.assertNotIn(secret,' '.join(command))
            report=next((root/'work'/'postpay-device-reports').glob('*/session.json'))
            self.assertNotIn(secret,report.read_text()+capture.getvalue())
            self.assertEqual('REAL_TEST_OPT_IN', json.loads(report.read_text())['drive'])

    def test_occupied_root_is_preserved_without_launch_or_report_creation(self):
        with self.booth() as (root, child, _, _):
            occupied=root/'work'/'original'; occupied.mkdir(parents=True)
            original=occupied/'drafts.sqlite3'; original.write_bytes(b'original owed fixture')
            self.assertEqual(2,entry.main(['--private-root',str(occupied)]))
            child.assert_not_called()
            self.assertEqual(b'original owed fixture',original.read_bytes())
            self.assertFalse((root/'work'/'postpay-device-reports').exists())

    def test_child_failure_is_recorded_and_returned_without_claiming_acceptance(self):
        with self.booth(code=7) as (root, _, _, _):
            self.assertEqual(7,entry.main([]))
            record=json.loads(next((root/'work'/'postpay-device-reports').glob('*/session.json')).read_text())
            self.assertEqual(7,record['exit_code'])
            self.assertEqual('EXIT_ERROR',record['state'])
            self.assertEqual('NOT_RUN',record['hardware_acceptance'])

    def test_os_launch_failure_is_recorded_without_silent_retry(self):
        with self.booth() as (root, child, _, _):
            child.side_effect=OSError('fixture launch failed')
            self.assertEqual(2,entry.main([]))
            self.assertEqual(1,child.call_count)
            record=json.loads(next((root/'work'/'postpay-device-reports').glob('*/session.json')).read_text())
            self.assertEqual('LAUNCH_ERROR',record['state'])

    def test_invalid_camera_index_is_blocked_before_preflight_or_launch(self):
        with self.booth() as (root, child, preflight, _):
            self.assertEqual(2,entry.main(['--camera-index','-1']))
            preflight.assert_not_called();child.assert_not_called()
            self.assertEqual([],list(root.iterdir()))


if __name__=='__main__': unittest.main()
