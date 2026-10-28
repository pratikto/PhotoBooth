"""AR-08 offline prepayment health: no camera open or customer media."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from photobooth.catalog import get_templates
from photobooth.device_health import HealthCheck, WARNING
from photobooth.kiosk_v2.recovery_readiness import prepayment_readiness

class ReadinessTests(TestCase):
    def test_valid_readiness_leaves_no_probe_or_customer_files(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)/'photos'
            prepayment_readiness(root,get_templates(),{'template_a':1},True,100,now=lambda:101)
            self.assertEqual(list(root.iterdir()),[])

    def test_missing_stale_future_camera_or_enabled_delivery_fails_closed(self):
        for valid,observed,delivery in [(False,100,False),(True,97,False),(True,102,False),(True,100,True)]:
            with self.subTest(valid=valid,observed=observed,delivery=delivery),TemporaryDirectory() as temp:
                root=Path(temp)/'photos'
                with self.assertRaises(RuntimeError):
                    prepayment_readiness(root,get_templates(),{'template_a':1},valid,observed,
                                         now=lambda:101,delivery_enabled=delivery)
                self.assertFalse(root.exists())

    def test_low_disk_or_unwritable_probe_prevents_admission(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)/'photos'
            with patch('photobooth.kiosk_v2.recovery_readiness.check_disk',return_value=HealthCheck('disk',WARNING,'fixture')):
                with self.assertRaises(RuntimeError):
                    prepayment_readiness(root,get_templates(),{'template_a':1},True,100,now=lambda:101)
            with patch('photobooth.kiosk_v2.recovery_readiness.tempfile.NamedTemporaryFile',side_effect=PermissionError):
                with self.assertRaises(RuntimeError):
                    prepayment_readiness(root,get_templates(),{'template_a':1},True,100,now=lambda:101)

    def test_absent_template_or_wrong_frozen_assets_blocks(self):
        with TemporaryDirectory() as temp:
            with self.assertRaises(RuntimeError):
                prepayment_readiness(Path(temp),[],{'template_a':1},True,100,now=lambda:101)
