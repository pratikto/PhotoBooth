"""v2 integration over original payment protocol; fixtures never call a provider."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photobooth.kiosk_v2.sandbox_checkout import SandboxCheckout, sandbox_enabled, configured_sandbox
from photobooth.qris_session import KioskCheckout
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.qris_mock import MockQrisProvider
from tools.run_portrait_v2_sandbox import v2_environments


from tests.test_qris_session import LocalClient

class SandboxAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.now=[1000.0]
        self.store=CheckoutStore(self.root/'orders.sqlite',now=lambda:self.now[0])
        self.provider=MockQrisProvider(self.root/'provider.sqlite',settle_after=5,now=lambda:self.now[0])
        self.backend=CheckoutBackend(self.store,self.provider,'mock-key','MOCK')
        self.flow=KioskCheckout(self.root/'visit.json',LocalClient(self.backend),mode='mock',booth_id='PB001',endpoint='http://127.0.0.1:8765')
        self.adapter=SandboxCheckout(self.flow)
    def tearDown(self):
        self.adapter.close();self.store.db.close();self.provider.close();self.temp.cleanup()
    def reserve(self):
        self.adapter.begin({'template_a':1,'template_b':0})
        self.now[0]+=6
        return self.adapter.check()
    def test_cart_server_quote_and_once_only_start_complete(self):
        view=self.reserve();self.assertEqual(view['amount'],10000)
        self.assertEqual(view['quantities'],{'template_a':1})
        self.assertEqual(view['phase'],'RESERVED')
        self.assertEqual(self.adapter.prepare()['phase'],'STARTING')
        with self.assertRaises(RuntimeError):self.adapter.prepare()
        self.assertEqual(self.adapter.started('PB001V2_00000001')['phase'],'STARTED')
        self.assertEqual(self.adapter.complete()['phase'],'COMPLETED')
        self.assertEqual(self.adapter.begin({'template_b':2})['amount'],15000)
    def test_restart_cannot_replay_partial_service(self):
        self.reserve();self.adapter.prepare();self.adapter.started('PB001V2_00000001');self.adapter.close()
        self.flow=KioskCheckout(self.root/'visit.json',LocalClient(self.backend),mode='mock',booth_id='PB001',endpoint='http://127.0.0.1:8765')
        self.adapter=SandboxCheckout(self.flow)
        self.assertEqual(self.adapter.boot()['phase'],'RECOVERY')
        with self.assertRaises(RuntimeError):self.adapter.begin({'template_b':1})
    def test_cancel_racing_settlement_preserves_reserved_permit(self):
        self.adapter.begin({'template_a':1});self.now[0]+=6
        self.assertEqual(self.adapter.cancel()['phase'],'RESERVED')
    def test_unpaid_cannot_start(self):
        self.adapter.begin({'template_a':1})
        with self.assertRaises(RuntimeError):self.adapter.prepare()
    def test_nine_copy_ui_limit_and_no_client_discount_input(self):
        with self.assertRaises(ValueError):self.adapter.begin({'template_a':10})
        with self.assertRaises(TypeError):self.adapter.begin({'template_a':1},discount=2500)
    def test_failed_qr_download_retains_same_order(self):
        with patch.object(self.adapter,'image_loader',side_effect=OSError('offline')):
            one=self.adapter.begin({'template_a':1});two=self.adapter.check()
        self.assertEqual(one['order']['order_id'],two['order']['order_id'])
        self.assertIsNone(two['qr_rgb'])
    def test_abort_recovery_blocks_replay(self):
        self.reserve();self.adapter.prepare();self.adapter.started('PB001V2_00000001')
        self.assertEqual(self.adapter.recover()['phase'],'RECOVERY')
        with self.assertRaises(RuntimeError):self.adapter.complete()
    def test_mode_and_credential_isolation(self):
        backend,gui=v2_environments({'PHOTOBOOTH_V2_CHECKOUT_MOCK':'1'},'merchant','SB-Mid-server-test','PB001',8765,self.root)
        self.assertTrue(sandbox_enabled(gui));self.assertNotIn('MIDTRANS_SERVER_KEY',gui)
        self.assertIn('MIDTRANS_SERVER_KEY',backend)
        self.assertIn('kiosk-v2-sandbox',gui['MEONG_QRIS_JOURNAL'])
        self.assertEqual(gui['PHOTOBOOTH_V2_PRINT'],'0')
        with self.assertRaises(ValueError):sandbox_enabled(dict(gui,MIDTRANS_SERVER_KEY='secret'))
        with self.assertRaises(ValueError):sandbox_enabled(dict(gui,PHOTOBOOTH_V2_CHECKOUT_MOCK='1'))
        with self.assertRaises(ValueError):sandbox_enabled(dict(gui,MEONG_QRIS_MODE='production'))
        self.assertFalse(sandbox_enabled({}))
    def test_cannot_reuse_legacy_profile(self):
        _,gui=v2_environments({},'merchant','SB-Mid-server-test','PB001',8765,self.root)
        gui['MEONG_QRIS_JOURNAL']=str(self.root/'data'/'qris-sandbox-trial'/'visit.json')
        with self.assertRaises(ValueError):configured_sandbox(self.root,gui)
