"""Actual global launch/child/control/camera ownership; external effects fake."""
from contextlib import closing,contextmanager
from dataclasses import replace
from pathlib import Path
import tempfile
import sqlite3
import threading
import time
import unittest
from unittest.mock import patch

from PIL import Image

from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_launch import ProtectedSandboxLaunch,ProtectedLaunchHeld
from photobooth.printer import PrinterConfig


class ProtectedLaunchTests(unittest.TestCase):
    @contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            legacy=root/'legacy.sqlite3'
            CheckoutStore(legacy).close()
            config=SandboxHostConfig(root/'storage','MTEST','PB001','Mid-server-LAUNCH-FIXTURE',
                'b'*48,'https://script.google.com/macros/s/LAUNCH_FIXTURE/exec','synthetic-launch-drive')
            launch=ProtectedSandboxLaunch(root/'project')
            try:
                with patch('photobooth.post_preview_bootstrap.CHILD_MODULE',
                           'tests.post_preview_host_process_fixture'):
                    yield launch,config,legacy
            finally:
                deadline=time.monotonic()+12
                while not launch.stop(timeout=.2):
                    if time.monotonic()>=deadline:self.fail('Original launch did not finish')
                    time.sleep(.05)

    def start(self,launch,config,legacy,**kwargs):
        return launch.start(config,PrinterConfig(lan_host='fixture-printer',usb_device_path=None),
            legacy_path=legacy,qr_loader=lambda _:Image.new('RGB',(200,200),'white'),
            camera_enabled=False,**kwargs)

    def locked(self,launch):
        with self.assertRaises(OSError):LaunchLease(launch.project_root)

    def test_global_owner_precedes_camera_legacy_and_backend_construction(self):
        with self.fixture() as (launch,config,legacy):
            with patch('photobooth.kiosk_v2.devices.AsyncCamera',side_effect=AssertionError('No device')):
                with self.assertRaises(ProtectedLaunchHeld):ProtectedSandboxLaunch(launch.project_root)
            self.locked(launch)
            self.assertIsNone(launch._legacy);self.assertIsNone(launch._camera)
            self.assertIsNone(launch._visits)

    def test_actual_child_ready_exposes_only_original_public_control_and_same_camera(self):
        with self.fixture() as (launch,config,legacy):
            control=self.start(launch,config,legacy)
            self.assertIs(control,launch.control)
            self.assertEqual('READY',control.state)
            self.assertIs(control.binding.jobs,launch._visits._jobs)
            self.assertIs(launch.camera,launch._visits._camera)
            self.assertIsNone(launch.camera._thread)  # GUI has not started the device.
            self.assertIsNone(launch._visits._backend.process.poll())
            self.assertNotIn(config.server_key,repr(launch))
            self.assertNotIn(config.drive_token,repr(launch))
            with self.assertRaises(ProtectedLaunchHeld):self.start(launch,config,legacy)
            self.assertTrue(launch.stop(timeout=12))
            self.assertTrue(launch.stop(timeout=0))
            with LaunchLease(launch.project_root):pass
            with self.assertRaises(ProtectedLaunchHeld):_ = launch.control
            with self.assertRaises(ProtectedLaunchHeld):_ = launch.camera

    def test_missing_or_archive_history_never_creates_a_replacement(self):
        with self.fixture() as (launch,config,legacy):
            missing=legacy.parent/'absent.sqlite3'
            with self.assertRaises(ProtectedLaunchHeld):self.start(launch,config,missing)
            self.assertFalse(missing.exists());self.assertIsNone(launch._camera)
            self.locked(launch)
        with self.fixture() as (launch,config,legacy):
            # No contents of any old directory are inspected or materialized.
            with self.assertRaises(ProtectedLaunchHeld):self.start(launch,config,legacy.parent/'old'/'legacy.sqlite3')
            self.assertIsNone(launch._legacy);self.assertIsNone(launch._camera)

    def test_empty_or_foreign_database_is_not_upgraded_into_empty_legacy_history(self):
        for foreign in (False,True):
            with self.subTest(foreign=foreign),self.fixture() as (launch,config,legacy):
                history=legacy.parent/'wrong.sqlite3'
                with closing(sqlite3.connect(history)) as db:
                    if foreign:db.execute('CREATE TABLE foreign_table(value TEXT)')
                before=history.read_bytes()
                with self.assertRaises(ProtectedLaunchHeld):self.start(launch,config,history)
                self.assertEqual(before,history.read_bytes())
                self.assertIsNone(launch._legacy);self.assertIsNone(launch._camera)
                self.locked(launch)

    def test_actual_child_worker_stop_false_retains_both_original_global_and_backend_owners(self):
        with self.fixture() as (launch,config,legacy):
            config=replace(config,server_key='Mid-server-HOLD-FIXTURE')
            self.start(launch,config,legacy)
            backend=launch._visits._backend
            try:
                self.assertFalse(launch.stop(timeout=.1));self.locked(launch)
                self.assertIsNone(backend.process.poll())
                with self.assertRaises(OSError):LaunchLease(config.private_root/'backend-owner')
                launch._legacy.db.execute('SELECT COUNT(*) FROM checkouts').fetchone()
            finally:(config.private_root/'fixture-release').write_text('original fixture worker released')
            self.assertTrue(launch.stop(timeout=12))
            self.assertIsNotNone(backend.process.poll())
            with LaunchLease(launch.project_root):pass

    def test_actual_photo_thread_holds_global_owner_and_legacy_until_original_exit(self):
        with self.fixture() as (launch,config,legacy):
            control=self.start(launch,config,legacy)
            entered=threading.Event();release=threading.Event()
            def blocked():entered.set();release.wait(10);return {'phase':'confirm'}
            try:
                with patch.object(control.binding.service,'snapshot',side_effect=blocked):
                    control.binding.jobs.submit('snapshot');self.assertTrue(entered.wait(3))
                    self.assertFalse(launch.stop(timeout=.05));self.locked(launch)
                    self.assertEqual(0,launch._legacy.db.execute('SELECT COUNT(*) FROM checkouts').fetchone()[0])
                    self.assertFalse(launch._visits._closed)
                    release.set()
                    self.assertTrue(launch.stop(timeout=12))
                with LaunchLease(launch.project_root):pass
            finally:release.set()

    def test_actual_camera_thread_holds_global_owner_after_original_worker_stops(self):
        with self.fixture() as (launch,config,legacy):
            self.start(launch,config,legacy)
            entered=threading.Event();release=threading.Event()
            class Camera:
                def open(self):entered.set();release.wait(10);return False
                def close(self):pass
            camera=launch.camera;camera.enabled=True;camera._factory=lambda _:Camera()
            try:
                camera.start();self.assertTrue(entered.wait(3))
                self.assertFalse(launch.stop(timeout=.1));self.locked(launch)
                self.assertTrue(camera._thread.is_alive())
                launch._legacy.db.execute('SELECT COUNT(*) FROM checkouts').fetchone()
                release.set();self.assertTrue(launch.stop(timeout=12))
                self.assertFalse(camera._thread.is_alive())
                with LaunchLease(launch.project_root):pass
            finally:release.set()

    def test_unverified_original_startup_retains_global_owner_until_drained(self):
        with self.fixture() as (launch,config,legacy):
            from photobooth.post_preview_sandbox_visits import OriginalSandboxVisits
            from photobooth.post_preview_store import DraftHeld
            with patch.object(OriginalSandboxVisits,'start',side_effect=DraftHeld('private startup details')):
                with self.assertRaises(ProtectedLaunchHeld) as error:
                    self.start(launch,config,legacy,timeout=.05)
                self.assertNotIn('private startup details',str(error.exception))
                self.locked(launch)
                self.assertIsNotNone(launch._worker)
            self.assertTrue(launch.stop(timeout=12))
            with LaunchLease(launch.project_root):pass


if __name__=='__main__':unittest.main()
