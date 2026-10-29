"""Nonpayable causal purchase integration using original backend and SQLite."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock,patch
from photobooth.catalog import get_templates
from photobooth.checkout_store import CheckoutStore,CheckoutConflict
from photobooth.checkout_backend import CheckoutBackend,ProviderUnavailable
from photobooth.delivery_requirements import DeliveryRequirements
from photobooth.device_health import HealthCheck,READY,WARNING,UNKNOWN,UNAVAILABLE
from photobooth.printer import PrinterConfig
from tests.test_checkout_backend import FakeProvider,KEY,MERCHANT
from tests.purchased_print_fixture import OfflinePrintPurchase


class PrintPurchaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'photos'
        self.store=CheckoutStore(Path(self.temp.name)/'orders.sqlite');self.addCleanup(self.store.close)
        self.provider=FakeProvider();self.provider.mode='mock'
        self.backend=CheckoutBackend(self.store,self.provider,KEY,MERCHANT,delivery_policy='PRINT_REQUIRED_V1')
        self.clock=[101.0];self.probe=Mock(return_value=HealthCheck('printer',READY,'route only'))
        self.host=OfflinePrintPurchase(self.backend,self.root,get_templates(),'PB001',PrinterConfig(),printer_probe=self.probe,now=lambda:self.clock[0])
        self.key='k'*32

    def begin(self,**overrides):
        args=dict(quantities={'template_a':2},key=self.key,camera_valid=True,observed_at=100)
        args.update(overrides);return self.host.begin(**args)

    def assert_empty(self):
        self.assertEqual(self.provider.charges,0)
        for t in ('checkouts','checkout_frozen_orders','checkout_create_attempts','checkout_customer_capabilities'):
            self.assertEqual(self.store.db.execute('SELECT count(*) FROM '+t).fetchone()[0],0,t)

    def test_policy_rejects_sandbox_and_fixture_rejects_default_backend(self):
        with self.assertRaises(ValueError):CheckoutBackend(self.store,FakeProvider(),KEY,MERCHANT,delivery_policy='PRINT_REQUIRED_V1')
        default=CheckoutBackend(self.store,self.provider,KEY,MERCHANT)
        with self.assertRaises(ValueError):OfflinePrintPurchase(default,self.root,get_templates(),'PB001',None,printer_probe=self.probe)
        self.assert_empty()

    def test_camera_storage_template_and_printer_failures_create_no_order(self):
        for args in ({'camera_valid':False},{'observed_at':97},{'observed_at':102}):
            with self.subTest(args=args),self.assertRaises(RuntimeError):self.begin(**args)
            self.assert_empty()
        self.probe.assert_not_called()
        with patch('photobooth.kiosk_v2.recovery_readiness.check_disk',return_value=HealthCheck('disk',WARNING,'private')):
            with self.assertRaises(RuntimeError):self.begin()
        templates=self.host.templates;self.host.templates=[]
        with self.assertRaises(RuntimeError):self.begin()
        self.host.templates=templates
        for status in (WARNING,UNKNOWN,UNAVAILABLE):
            self.probe.return_value=HealthCheck('printer',status,'PRIVATE queue/host')
            with self.subTest(status=status),self.assertRaisesRegex(RuntimeError,'^Purchase readiness requires attention$'):self.begin(capability_hash='c'*64)
            self.assert_empty()
        self.probe.side_effect=OSError('PRIVATE queue/host')
        with self.assertRaisesRegex(RuntimeError,'^Purchase readiness requires attention$'):self.begin()
        self.assert_empty();self.assertEqual(list(self.root.iterdir()),[])

    def test_retry_freezes_requirement_before_one_nonpayable_provider_effect(self):
        original=self.provider.create_qris
        def create(oid,amount):
            self.assertEqual(DeliveryRequirements(self.store).get(oid,'PB001',MERCHANT)['copies'],{'template_a':2})
            return original(oid,amount)
        self.provider.create_qris=create
        self.probe.return_value=HealthCheck('printer',UNKNOWN,'fixture')
        with self.assertRaises(RuntimeError):self.begin()
        self.probe.return_value=HealthCheck('printer',READY,'route only')
        view=self.begin();self.assertEqual(view['mode'],'mock');self.assertIsNone(view['qr_url'])
        self.assertTrue(view['qr_payload'].startswith('MEONG MOCK ONLY - NOT QRIS - '))
        self.assertEqual(view['delivery_requirement']['copies'],{'template_a':2})
        self.assertEqual(self.provider.charges,1);self.assertIsNone(view['grant_id'])

    def test_slow_probe_expires_before_creation_and_preserves_existing_files(self):
        self.root.mkdir();marker=self.root/'synthetic-existing.txt';marker.write_bytes(b'unchanged')
        def slow(_config):
            self.clock[0]=103
            return HealthCheck('printer',READY,'late route')
        self.probe.side_effect=slow
        with self.assertRaises(RuntimeError):self.begin()
        self.assert_empty();self.assertEqual(marker.read_bytes(),b'unchanged');self.assertEqual(list(self.root.iterdir()),[marker])

    def test_active_identity_recovers_without_probe_and_cannot_be_replaced(self):
        first=self.begin();self.probe.side_effect=AssertionError('Must not probe recovery')
        again=self.begin(camera_valid=False,observed_at=0);self.assertEqual(again['order_id'],first['order_id'])
        with self.assertRaises(CheckoutConflict):self.begin(quantities={'template_a':3})
        with self.assertRaises(CheckoutConflict):self.begin(key='n'*32,camera_valid=False)
        self.assertEqual(self.provider.charges,1);self.assertEqual(self.probe.call_count,1)

    def test_lost_reply_retains_requirement_and_recovery_only_reads_status(self):
        self.provider.lost_charge=True
        with self.assertRaises(ProviderUnavailable):self.begin()
        oid=self.store.db.execute('SELECT id FROM checkouts').fetchone()[0]
        requirement=DeliveryRequirements(self.store).get(oid,'PB001',MERCHANT)
        self.provider.lost_charge=False;self.probe.side_effect=AssertionError('Must not probe recovery')
        view=self.begin(camera_valid=False,observed_at=0)
        self.assertEqual(view['order_id'],oid);self.assertEqual(view['delivery_requirement'],requirement)
        self.assertEqual(self.provider.charges,1)
