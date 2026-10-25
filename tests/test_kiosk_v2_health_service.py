"""Read-only v1 bridge and safe-report boundaries, without physical probes."""
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import threading
import time
import unittest
from unittest.mock import Mock, patch

from photobooth.device_health import HealthCheck, HealthSnapshot
from photobooth.kiosk_v2.health_service import V2HealthController, CachedCamera, DeferredPrinterConfig
from photobooth.kiosk_v2.health_report import safe_health_report, HealthReportStore


def snapshot():
    return HealthSnapshot('2026-10-25T05:00:00+00:00',tuple(
        HealthCheck(name,'ready','SECRET DRIVER MESSAGE 192.0.2.9 token=private')
        for name in ('camera','printer','disk','network','media','heartbeat')))


class Scheduler:
    def __init__(self):self.pending=[]
    def after(self,_delay,callback):self.pending.append(callback)
    def flush(self):
        for callback in self.pending[:]:self.pending.remove(callback);callback()


class HealthBridgeTests(unittest.TestCase):
    def make(self, root, frame=object()):
        owner=SimpleNamespace(_closed=False,camera_device=SimpleNamespace(read=Mock(return_value=frame),index=2),
            catalog=object(),_sandbox_jobs=None,_photo_jobs=None,_operator_last_tick=123.0)
        scheduler=Scheduler()
        return owner,scheduler,V2HealthController(owner,scheduler,root)
    def wait(self,controller):
        deadline=time.monotonic()+3
        while controller._health_probe_lock.locked() and time.monotonic()<deadline:time.sleep(.005)
        self.assertFalse(controller._health_probe_lock.locked())
        # The v1 worker schedules immediately after releasing its lock.
        deadline=time.monotonic()+1
        while not controller.root.pending and time.monotonic()<deadline:time.sleep(.005)
    def test_original_worker_receives_cached_frame_and_lazy_config_off_ui(self):
        with TemporaryDirectory() as root:
            owner,scheduler,controller=self.make(root);result=[];threads=[]
            def collect(**kwargs):
                threads.append(threading.current_thread().name)
                self.assertIsInstance(kwargs['camera'],CachedCamera)
                self.assertIsInstance(kwargs['printer_config'],DeferredPrinterConfig)
                self.assertEqual(kwargs['last_heartbeat'],123.0)
                return snapshot()
            with patch('photobooth.v1_health_controller.collect_health_snapshot',side_effect=collect):
                controller.refresh(result.append);self.wait(controller)
                self.assertEqual(result,[])
                scheduler.flush()
            self.assertEqual(threads,['meong-device-health'])
            self.assertIn('handle tidak dibuka ulang',result[0].by_name('camera').message)
            owner.camera_device.read.assert_called_once()
    def test_no_frame_does_not_claim_camera_handle_offline_or_ready(self):
        with TemporaryDirectory() as root:
            _,scheduler,controller=self.make(root,None);result=[]
            with patch('photobooth.v1_health_controller.collect_health_snapshot',return_value=snapshot()):
                controller.refresh(result.append);self.wait(controller);scheduler.flush()
            self.assertEqual(result[0].by_name('camera').status,'unknown')
    def test_old_worker_single_flight_and_closing_ignores_late_result(self):
        with TemporaryDirectory() as root:
            owner,scheduler,controller=self.make(root);entered=threading.Event();release=threading.Event();result=[]
            def collect(**_):entered.set();release.wait(3);return snapshot()
            with patch('photobooth.v1_health_controller.collect_health_snapshot',side_effect=collect) as probe:
                controller.refresh(result.append);self.assertTrue(entered.wait(1))
                controller.refresh(result.append);scheduler.flush()
                self.assertEqual(result,[None]);self.assertEqual(probe.call_count,1)
                owner._closed=True;release.set();self.wait(controller);scheduler.flush()
                self.assertEqual(result,[None])
    def test_printer_settings_are_read_only_and_deferred(self):
        with TemporaryDirectory() as root,patch('photobooth.printer_settings.load_printer_config') as load:
            view=DeferredPrinterConfig(Path(root)/'settings.json');load.assert_not_called()
            load.return_value=SimpleNamespace(lan_host='configured')
            self.assertEqual(view.lan_host,'configured');self.assertEqual(view.lan_host,'configured')
            load.assert_called_once()
    def test_report_excludes_driver_messages_environment_secrets_and_device_identity(self):
        with TemporaryDirectory() as root,patch.dict('os.environ',{'MIDTRANS_SERVER_KEY':'PRIVATE KEY','MEONG_QRIS_BOOTH_TOKEN':'PRIVATE TOKEN'}):
            value=safe_health_report(root,snapshot());raw=json.dumps(value)
            for secret in ('SECRET DRIVER','192.0.2.9','token=private','PRIVATE KEY','PRIVATE TOKEN'):
                self.assertNotIn(secret,raw)
            self.assertEqual(len(value['health']['checks']),6)
            self.assertEqual(set(value['acceptance'].values()),{'NOT_RUN'})
            self.assertEqual(value['report_kind'],'portrait-v2-operator-health')
    def test_atomic_report_is_local_unique_and_readiness_form_compatible(self):
        with TemporaryDirectory() as root:
            store=HealthReportStore(root)
            one=store.save(snapshot());two=store.save(snapshot())
            self.assertNotEqual(one['file'],two['file'])
            for item in (one,two):
                path=Path(root)/'data'/'diagnostics'/item['file'];self.assertTrue(path.is_file())
                value=json.loads(path.read_text());self.assertEqual(value['schema_version'],1)
                self.assertIn('source',value);self.assertIn('device',value)
            self.assertEqual(list(Path(root).rglob('*.jpg')),[])
    def test_missing_snapshot_cannot_export_as_pass(self):
        with self.assertRaises(ValueError):safe_health_report('/tmp',None)
