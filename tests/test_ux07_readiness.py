"""UX-07 offline readiness -> real controller/HTTP/SQLite before any charge."""
from contextlib import contextmanager
from dataclasses import replace
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time
from unittest import TestCase
from unittest.mock import patch

from photobooth.catalog import get_templates
from photobooth.device_health import HealthCheck, WARNING, UNKNOWN
from photobooth.kiosk_v2.recovery_readiness import prepayment_readiness
from tests.qris_v2_fixture import Fixture


class PrepaymentBoundaryTests(TestCase):
    @contextmanager
    def fixture(self):
        with TemporaryDirectory() as temp, patch.dict(os.environ, PHOTOBOOTH_V2_PRINT='0', PHOTOBOOTH_V2_DRIVE='0'):
            f = Fixture(Path(temp))
            try:
                yield f
            finally:
                f.flow.close()  # Direct calls never instantiate jobs.store.
                f.close()

    def no_order(self, f):
        self.assertIsNone(f.flow.snapshot())
        self.assertFalse(f.flow.path.exists())
        self.assertEqual(f.provider.charges, 0)
        self.assertEqual(f.provider.reads, 0)
        self.assertEqual(f.store.db.execute('SELECT COUNT(*) FROM checkouts').fetchone()[0], 0)
        self.assertEqual(f.store.db.execute('SELECT COUNT(*) FROM checkout_create_attempts').fetchone()[0], 0)

    def test_ux07_camera_failures_deny_before_order_or_provider(self):
        for valid, age in [(False,0),(True,4),(True,-4),(True,float('nan')),(True,float('inf'))]:
            with self.subTest(valid=valid,age=age), self.fixture() as f:
                with self.assertRaises(RuntimeError):
                    f.service.begin_ready({'template_a':1},valid,time.monotonic()-age)
                self.no_order(f)

    def test_ux07_storage_and_template_failures_preserve_bytes_then_retry_once(self):
        for kind in ('low_disk','unknown_disk','probe_open','probe_fsync','missing_template','artwork','mask'):
            with self.subTest(kind=kind), self.fixture() as f:
                root=f.root/'photo-tests'/'photos';root.mkdir(parents=True)
                kept=root/'existing-synthetic.bin';kept.write_bytes(b'PRESERVE SYNTHETIC BYTES')
                if kind.endswith('disk'):
                    fault=patch('photobooth.kiosk_v2.recovery_readiness.check_disk',return_value=
                                HealthCheck('disk',WARNING if kind=='low_disk' else UNKNOWN,'synthetic'))
                elif kind=='probe_open':
                    fault=patch('photobooth.kiosk_v2.recovery_readiness.tempfile.NamedTemporaryFile',side_effect=PermissionError('private-fixture-path'))
                elif kind=='probe_fsync':
                    fault=patch('photobooth.kiosk_v2.recovery_readiness.os.fsync',side_effect=OSError('private-fixture-path'))
                else:
                    templates=get_templates()
                    if kind=='missing_template':
                        changed=[]
                    else:
                        bad=f.root/'synthetic-corrupt-asset.png';bad.write_bytes(b'NOT AN IMAGE')
                        t=next(t for t in templates if t.template_id=='template_a')
                        t=(replace(t,artwork_path=bad) if kind=='artwork' else
                           replace(t,apertures=(replace(t.apertures[0],mask_path=bad),*t.apertures[1:])))
                        changed=[t]
                    fault=patch('photobooth.catalog.get_templates',return_value=changed)
                with fault:
                    with self.assertRaises(RuntimeError):
                        f.service.begin_ready({'template_a':1},True,time.monotonic())
                self.no_order(f)
                self.assertEqual(kept.read_bytes(),b'PRESERVE SYNTHETIC BYTES')
                self.assertEqual(list(root.glob('.meong-readiness-*')),[])
                view=f.service.begin_ready({'template_a':1},True,time.monotonic())
                self.assertEqual(view['phase'],'WAITING')
                self.assertEqual(f.provider.charges,1)
                self.assertEqual(f.store.db.execute('SELECT COUNT(*) FROM checkouts').fetchone()[0],1)
                self.assertEqual(kept.read_bytes(),b'PRESERVE SYNTHETIC BYTES')

    def test_ux07_delivery_optins_fail_before_any_printer_probe_or_order(self):
        for key in ('PRINT','DRIVE'):
            with self.subTest(key=key), self.fixture() as f:
                with patch.dict(os.environ,{'PHOTOBOOTH_V2_'+key:'1'}), \
                        patch('photobooth.device_health.check_printer',side_effect=AssertionError('No physical probe')):
                    with self.assertRaises(RuntimeError):
                        f.service.begin_ready({'template_a':1},True,time.monotonic())
                self.no_order(f)
                self.assertFalse((f.root/'photo-tests').exists())

    def test_ux07_expiration_during_worker_validation_denies_before_order(self):
        with self.fixture() as f:
            ticks=iter((100,103))
            def delayed(*args,**kwargs):
                return prepayment_readiness(*args,now=lambda:next(ticks),**kwargs)
            with patch('photobooth.kiosk_v2.recovery_readiness.prepayment_readiness',side_effect=delayed):
                with self.assertRaisesRegex(RuntimeError,'expired'):
                    f.service.begin_ready({'template_a':1},True,100)
            self.no_order(f)
            self.assertEqual(list((f.root/'photo-tests'/'photos').glob('.meong-readiness-*')),[])

    def test_ux07_failed_current_readiness_cannot_replace_or_recharge_active_order(self):
        with self.fixture() as f:
            initial=f.service.begin_ready({'template_a':1},True,time.monotonic())
            with patch('photobooth.kiosk_v2.recovery_readiness.prepayment_readiness',side_effect=AssertionError('Existing order must reconcile')):
                current=f.service.begin_ready({'template_a':1},False,0)
                self.assertEqual(current['checkout_key'],initial['checkout_key'])
                self.assertEqual(current['order']['order_id'],initial['order']['order_id'])
                with self.assertRaises(RuntimeError):
                    f.service.begin_ready({'template_b':1},False,0)
            self.assertEqual(f.provider.charges,1)
            self.assertEqual(f.store.db.execute('SELECT COUNT(*) FROM checkouts').fetchone()[0],1)
