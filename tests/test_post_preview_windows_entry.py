"""Protected Windows entry orchestration; no real account/device effects."""
from contextlib import contextmanager
import io
import os
from pathlib import Path
from types import SimpleNamespace
import threading
import time
import unittest
from unittest.mock import patch

from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.kiosk_v2.demo_game import GameJobs
from photobooth.kiosk_v2.previews import PreviewPreloader
from photobooth.post_preview_native_exit import drain_native_app
from tests import test_post_preview_launch_settings as fixtures
from tools import run_post_preview_sandbox as entry


class ProtectedWindowsEntryTests(unittest.TestCase):
    def test_optional_clipboard_cleanup_error_cannot_interrupt_original_owner_drain(self):
        from photobooth.post_preview_launch import ProtectedSandboxLaunch
        original=ProtectedSandboxLaunch.__init__;owners=[]
        def capture(owner,root):original(owner,root);owners.append(owner)
        def broken():raise RuntimeError('PRIVATE CLIPBOARD DIAGNOSTIC')
        bridge=SimpleNamespace(install=lambda:None,close=broken)
        with self.fixture() as (root,local,history,output,error):
            flags=['--sandbox-only','--enable-real-printer','--accept-real-paper',
                   '--enable-real-drive','--accept-public-test-upload','--owned-acceptance-session','a'*32]
            try:
                with patch.object(ProtectedSandboxLaunch,'__init__',capture), \
                     patch('photobooth.post_preview_acceptance.validate_runtime_session'), \
                     patch('photobooth.post_preview_bootstrap.CHILD_MODULE','tests.post_preview_host_process_fixture'), \
                     patch('photobooth.kiosk_v2.owned_sandbox_simulator.OwnedSandboxSimulatorClipboard',return_value=bridge), \
                     patch.object(entry,'native_app',return_value=SimpleNamespace(_closed=True,run=lambda:None)):
                    self.assertEqual(0,entry.main(self.args(root)+flags))
                self.assertTrue(owners[0]._closed)
                self.assertTrue(owners[0]._control.stopped)
                self.assertNotIn('PRIVATE CLIPBOARD',output.getvalue()+error.getvalue())
                with LaunchLease(root):pass
            finally:
                for owner in owners:
                    deadline=time.monotonic()+12
                    while not owner.stop(timeout=.2):
                        if time.monotonic()>deadline:self.fail('Original fixture owner did not drain')
    def test_acceptance_clipboard_session_is_not_a_check_only_or_consent_bypass(self):
        with patch('sys.stderr',new_callable=io.StringIO), patch(
                'photobooth.post_preview_launch.ProtectedSandboxLaunch',side_effect=AssertionError('No private owner')):
            args=['--storage-root',str(Path.cwd()),'--owned-acceptance-session','a'*32]
            self.assertEqual(2,entry.main(args+['--check-only']))
            self.assertEqual(2,entry.main(args+['--sandbox-only']))
    @contextmanager
    def fixture(self):
        helper=fixtures.ProtectedLaunchSettingsTests(methodName='runTest')
        with helper.fixture() as (owner,root,local,history):
            owner.stop(timeout=0)
            with patch.object(entry,'ROOT',root),patch('sys.stdout',new_callable=io.StringIO) as output,patch('sys.stderr',new_callable=io.StringIO) as error:
                yield root,local,history,output,error

    def args(self,root):return ['--storage-root',str(root/'protected')]

    def test_check_only_reads_local_original_history_without_backend_devices_or_storage_creation(self):
        with self.fixture() as (root,local,history,output,error):
            with patch('photobooth.post_preview_launch.ProtectedSandboxLaunch.start',side_effect=AssertionError('No child')):
                self.assertEqual(0,entry.main(self.args(root)+['--check-only']))
            self.assertIn('NOT_CHECKED',output.getvalue());self.assertFalse((root/'protected').exists())
            with LaunchLease(root):pass

    def test_runtime_requires_all_original_external_consents_before_global_or_private_reads(self):
        with patch.object(entry,'native_app',side_effect=AssertionError('No GUI')):
            with patch('sys.stderr',new_callable=io.StringIO):
                self.assertEqual(2,entry.main(['--storage-root',str(Path.cwd()/'unused'),'--sandbox-only']))

    def test_occupied_original_global_owner_blocks_entry_and_redacts_private_settings(self):
        with self.fixture() as (root,local,history,output,error):
            with LaunchLease(root):
                self.assertEqual(2,entry.main(self.args(root)+['--check-only']))
            self.assertNotIn('SETTINGS-FIXTURE',error.getvalue())

    def test_actual_original_child_control_and_same_camera_reach_native_constructor_then_drain(self):
        with self.fixture() as (root,local,history,output,error):
            seen=[]
            def native(control,camera,private_root,size):
                self.assertEqual('READY',control.state);self.assertIsNone(camera._thread)
                self.assertIsNotNone(control.binding);self.assertEqual('452x900',size)
                self.assertTrue(private_root.is_relative_to(root/'protected'))
                self.assertNotIn(os.environ.get('SDL_VIDEODRIVER'),('offscreen','dummy'))
                self.assertNotEqual('dummy',os.environ.get('SDL_AUDIODRIVER'))
                self.assertEqual('0',os.environ.get('PHOTOBOOTH_FACE_TRIGGER'))
                self.assertEqual('0',os.environ.get('PHOTOBOOTH_PALM_TRIGGER'))
                seen.append(control)
                return SimpleNamespace(_closed=True,run=lambda:None)
            flags=['--sandbox-only','--enable-real-printer','--accept-real-paper','--enable-real-drive','--accept-public-test-upload']
            os.environ.update(SDL_VIDEODRIVER='offscreen',SDL_AUDIODRIVER='dummy')
            with patch('photobooth.post_preview_bootstrap.CHILD_MODULE','tests.post_preview_host_process_fixture'),patch.object(entry,'native_app',side_effect=native):
                self.assertEqual(0,entry.main(self.args(root)+flags))
            self.assertEqual(1,len(seen));self.assertTrue(seen[0].stopped)
            with LaunchLease(root):pass

    def test_original_game_file_thread_prevents_global_shutdown_until_actual_exit(self):
        entered=threading.Event();release=threading.Event()
        def work():entered.set();release.wait(5)
        jobs=GameJobs(lambda:SimpleNamespace(save=work),actions={'save'})
        app=SimpleNamespace(_closed=True,_game_jobs=jobs)
        try:
            jobs.submit('save',1);self.assertTrue(entered.wait(2))
            self.assertFalse(drain_native_app(app,timeout=.01))
            self.assertTrue(jobs._thread.is_alive());release.set()
            self.assertTrue(drain_native_app(app,timeout=2));self.assertFalse(jobs._thread.is_alive())
        finally:release.set();jobs.wait_closed(2)

    def test_original_preview_pool_remains_held_after_nonblocking_close(self):
        entered=threading.Event();release=threading.Event()
        def render(_):entered.set();release.wait(5)
        pool=PreviewPreloader([SimpleNamespace(template_id='one')],renderer=render)
        app=SimpleNamespace(_closed=True,_preview_preloader=pool)
        try:
            pool.start();self.assertTrue(entered.wait(2))
            self.assertFalse(drain_native_app(app,timeout=.01));release.set()
            self.assertTrue(drain_native_app(app,timeout=2))
        finally:release.set();pool.close()


if __name__=='__main__':unittest.main()
