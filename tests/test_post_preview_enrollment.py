"""Explicit original new-booth enrollment; never erase/adopt legacy history."""
from contextlib import contextmanager,closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from photobooth.post_preview_enrollment import enroll_new_booth
from photobooth.post_preview_launch import ProtectedSandboxLaunch,ProtectedLaunchHeld
from photobooth.post_preview_launch_settings import load_settings


class ProtectedEnrollmentTests(unittest.TestCase):
    @contextmanager
    def fixture(self):
        system={k:v for k,v in os.environ.items() if k in
                {'PATH','SYSTEMROOT','WINDIR','TEMP','TMP','TMPDIR','HOME','USERPROFILE','LOCALAPPDATA','APPDATA'}}
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,system,clear=True):
            root=Path(directory);(root/'photobooth').mkdir()
            (root/'photobooth'/'local_settings.py').write_text("MIDTRANS_SANDBOX_MERCHANT_ID='MTEST'\nMIDTRANS_SANDBOX_SERVER_KEY='Mid-server-ENROLLMENT-FIXTURE'\nWEB_APP_URL='https://script.google.com/macros/s/ENROLL_FIXTURE/exec'\nUPLOAD_TOKEN='synthetic-enroll-token'\n")
            (root/'data').mkdir()
            (root/'data'/'printer_settings.json').write_text(json.dumps({'windows_printer_name':'Fixture POS80'}))
            owner=ProtectedSandboxLaunch(root)
            try:yield owner,root
            finally:self.assertTrue(owner.stop(timeout=1))

    def enroll(self,owner,root):return enroll_new_booth(owner,storage_root=root/'storage',booth_id='PB001')
    def load(self,owner,root):return load_settings(owner,storage_root=root/'storage',booth_id='PB001')

    def test_explicit_fresh_enrollment_uses_original_dedicated_baseline_without_fake_journal(self):
        with self.fixture() as (owner,root):
            with self.assertRaises(ProtectedLaunchHeld):self.load(owner,root)
            settings=self.enroll(owner,root);again=self.enroll(owner,root)
            self.assertEqual(settings.legacy_path,again.legacy_path)
            self.assertEqual(settings.legacy_path,self.load(owner,root).legacy_path)
            self.assertFalse((root/'data'/'kiosk-v2-sandbox').exists())
            self.assertFalse((root/'storage').exists())
            with closing(sqlite3.connect(settings.legacy_path)) as db:
                self.assertEqual(0,db.execute('SELECT COUNT(*) FROM checkouts').fetchone()[0])
            metadata=''.join(p.read_text() for p in settings.legacy_path.parent.glob('*.json'))
            self.assertNotIn(settings.config.server_key,metadata)
            self.assertNotIn(settings.config.drive_token,metadata)
            self.assertIsNone(owner._camera);self.assertIsNone(owner._visits)

    def test_known_legacy_or_protected_namespace_is_never_relabelled_fresh(self):
        for relative in ('data/kiosk-v2-sandbox','data/qris-sandbox-trial','data/Photobooth',
                         'data/kiosk-v2-p3','storage/post-preview-sandbox','storage/Photobooth'):
            with self.subTest(path=relative),self.fixture() as (owner,root):
                path=root/relative;path.mkdir(parents=True);sentinel=path/'keep.bin';sentinel.write_bytes(b'original')
                with self.assertRaises(ProtectedLaunchHeld):self.enroll(owner,root)
                self.assertEqual(b'original',sentinel.read_bytes())
                self.assertFalse((root/'data'/'post-preview-enrollment').exists())

    def test_selected_storage_identity_cannot_be_replaced_after_enrollment(self):
        with self.fixture() as (owner,root):
            settings=self.enroll(owner,root);before=hashlib.sha256(settings.legacy_path.read_bytes()).hexdigest()
            with self.assertRaises(ProtectedLaunchHeld):
                enroll_new_booth(owner,storage_root=root/'different',booth_id='PB001')
            with self.assertRaises(ProtectedLaunchHeld):
                load_settings(owner,storage_root=root/'different',booth_id='PB001')
            self.assertEqual(before,hashlib.sha256(settings.legacy_path.read_bytes()).hexdigest())

    def test_new_legacy_appearance_after_enrollment_holds_routine_load(self):
        with self.fixture() as (owner,root):
            settings=self.enroll(owner,root)
            (root/'data'/'kiosk-v2-sandbox').mkdir()
            with self.assertRaises(ProtectedLaunchHeld):self.load(owner,root)
            self.assertTrue(settings.legacy_path.is_file())

    def test_explicit_external_legacy_paths_or_orphan_wal_are_not_ignored(self):
        for name in ('PHOTOBOOTH_V2_STORAGE_ROOT','MEONG_QRIS_DB_PATH','MEONG_QRIS_JOURNAL','ORPHAN_WAL'):
            with self.subTest(setting=name),self.fixture() as (owner,root):
                path=root/'external-history'
                if name=='ORPHAN_WAL':path=root/'data'/'qris-sandbox.sqlite-wal'
                else:os.environ[name]=str(path)
                path.write_bytes(b'original unresolved evidence')
                with self.assertRaises(ProtectedLaunchHeld):self.enroll(owner,root)
                self.assertEqual(b'original unresolved evidence',path.read_bytes())

    def test_nonempty_baseline_or_damaged_completion_is_never_reset(self):
        for kind in ('row','completion'):
            with self.subTest(kind=kind),self.fixture() as (owner,root):
                settings=self.enroll(owner,root)
                if kind=='row':
                    from photobooth.checkout_store import CheckoutStore
                    with closing(CheckoutStore(settings.legacy_path)) as store:
                        store.begin('PB001',{'template_a':1},10000,'new-enrollment-row-0001')
                else:(settings.legacy_path.parent/'enrolled.json').write_text('{}')
                before=hashlib.sha256(settings.legacy_path.read_bytes()).hexdigest()
                with self.assertRaises(ProtectedLaunchHeld):self.load(owner,root)
                with self.assertRaises(ProtectedLaunchHeld):self.enroll(owner,root)
                self.assertEqual(before,hashlib.sha256(settings.legacy_path.read_bytes()).hexdigest())

    def test_interrupted_completion_resumes_same_original_intent_and_baseline(self):
        with self.fixture() as (owner,root):
            import photobooth.post_preview_enrollment as module
            original=module._exclusive_json
            def interrupted(path,value):
                if path.name=='enrolled.json':raise OSError('Synthetic interrupted completion')
                return original(path,value)
            with patch.object(module,'_exclusive_json',side_effect=interrupted):
                with self.assertRaises(ProtectedLaunchHeld):self.enroll(owner,root)
            folder=root/'data'/'post-preview-enrollment'
            intent=(folder/'intent.json').read_bytes();baseline=(folder/'legacy-baseline.sqlite3').read_bytes()
            settings=self.enroll(owner,root)
            self.assertEqual(intent,(folder/'intent.json').read_bytes())
            self.assertEqual(baseline,settings.legacy_path.read_bytes())

    def test_unknown_partial_intent_holds_and_no_closed_owner_can_enroll(self):
        with self.fixture() as (owner,root):
            folder=root/'data'/'post-preview-enrollment';folder.mkdir()
            (folder/'intent.json').write_bytes(b'{')
            with self.assertRaises(ProtectedLaunchHeld):self.enroll(owner,root)
            self.assertEqual(b'{',(folder/'intent.json').read_bytes())
        with self.fixture() as (owner,root):
            owner.stop(timeout=0)
            with self.assertRaises(ProtectedLaunchHeld):self.enroll(owner,root)
            self.assertFalse((root/'data'/'post-preview-enrollment').exists())

    def test_setup_creates_no_native_backend_network_or_protected_media(self):
        with self.fixture() as (owner,root):
            with patch('socket.socket',side_effect=AssertionError('No network')):
                with patch.object(owner,'start',side_effect=AssertionError('No backend')):
                    settings=self.enroll(owner,root)
            self.assertFalse(settings.config.private_root.exists())
            with self.assertRaises(ProtectedLaunchHeld):
                enroll_new_booth(owner,storage_root=root/'old'/'data',booth_id='PB001')

    def test_python_entry_requires_explicit_local_setup_and_does_not_launch_backend(self):
        from tools import run_post_preview_sandbox as entry
        with self.fixture() as (owner,root):
            owner.stop(timeout=0)
            import io
            with patch.object(entry,'ROOT',root),patch('sys.stdout',new_callable=io.StringIO) as out,patch('sys.stderr',new_callable=io.StringIO):
                args=['--storage-root',str(root/'storage')]
                self.assertEqual(2,entry.main(args+['--check-only']))
                self.assertFalse((root/'data'/'post-preview-enrollment').exists())
                self.assertEqual(2,entry.main(args+['--enroll-new-booth','--sandbox-only']))
                with patch('photobooth.post_preview_launch.ProtectedSandboxLaunch.start',side_effect=AssertionError('No child')):
                    self.assertEqual(0,entry.main(args+['--setup-only','--enroll-new-booth','--sandbox-only']))
                    self.assertEqual(0,entry.main(args+['--check-only']))
                self.assertIn('NOT_CHECKED',out.getvalue())

    def test_later_protected_state_uses_same_enrollment_and_original_boot_guards(self):
        with self.fixture() as (owner,root):
            settings=self.enroll(owner,root)
            settings.config.private_root.mkdir(parents=True)
            sentinel=settings.config.private_root/'original-evidence';sentinel.write_bytes(b'keep')
            self.assertEqual(settings.legacy_path,self.load(owner,root).legacy_path)
            self.assertEqual(b'keep',sentinel.read_bytes())
            # Loading enrollment is NOT a grant to open/adopt those protected
            # rows/media. Original backend context/worker startup remains separate.
            self.assertIsNone(owner._visits);self.assertIsNone(owner._camera)

    def test_enrolled_original_baseline_supports_actual_child_start_stop_and_same_root_restart(self):
        from PIL import Image
        with self.fixture() as (owner,root):
            settings=self.enroll(owner,root)
            with patch('photobooth.post_preview_bootstrap.CHILD_MODULE','tests.post_preview_host_process_fixture'):
                control=owner.start(settings.config,settings.printer_config,legacy_path=settings.legacy_path,
                                    qr_loader=lambda _:Image.new('RGB',(100,100)),camera_enabled=False)
                self.assertEqual('READY',control.state);self.assertIsNone(owner.camera._thread)
                self.assertTrue(owner.stop(timeout=12))
                again=ProtectedSandboxLaunch(root)
                try:
                    same=load_settings(again,storage_root=root/'storage',booth_id='PB001')
                    self.assertEqual(settings.legacy_path,same.legacy_path)
                    second=again.start(same.config,same.printer_config,legacy_path=same.legacy_path,
                                       qr_loader=lambda _:Image.new('RGB',(100,100)),camera_enabled=False)
                    self.assertEqual('READY',second.state)
                finally:self.assertTrue(again.stop(timeout=12))


if __name__=='__main__':unittest.main()
