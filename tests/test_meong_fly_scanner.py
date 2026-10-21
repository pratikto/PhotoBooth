"""Real QR decoding with synthetic frames; no physical camera required."""
import importlib.util
import threading
import time
import unittest
import tempfile
from pathlib import Path

from photobooth.meong_fly_scanner import ReceiptScanner, is_demo_token, MIRRORED_UV


class TokenTests(unittest.TestCase):
    def test_only_demo_tokens(self):
        for value in ('DEMO-', '', 'https://example.org', 'PAID-123', 'DEMO-'+'x'*100):
            self.assertFalse(is_demo_token(value))
        self.assertTrue(is_demo_token('DEMO-SCAN-001'))


@unittest.skipUnless(importlib.util.find_spec('cv2'), 'OpenCV unavailable')
class ScannerWorkerTests(unittest.TestCase):
    def wait_for(self, predicate):
        deadline=time.monotonic()+4
        while time.monotonic()<deadline:
            if predicate(): return
            time.sleep(.01)
        self.fail('scanner worker did not reach expected state')

    def test_actual_qr_decode_and_camera_release_without_mutating_source(self):
        import numpy as np
        import qrcode
        raw=np.array(qrcode.make('DEMO-SCAN-001').convert('RGB'))
        before=raw.copy()
        closed=threading.Event()
        class Camera:
            def __init__(self,index): pass
            def open(self): return True
            def read(self): return raw
            def close(self): closed.set()
        scanner=ReceiptScanner(camera_factory=Camera)
        self.addCleanup(scanner.dispose)
        scanner.set_active(True)
        self.wait_for(lambda: scanner.snapshot()[2]=='DEMO-SCAN-001')
        self.assertIsNotNone(scanner.snapshot()[1])
        np.testing.assert_array_equal(raw,before)
        scanner.set_active(False)
        self.assertIsNone(scanner.snapshot()[1])
        self.assertTrue(closed.wait(2))

    def test_stop_during_open_and_reentry_do_not_open_second_handle(self):
        opened=threading.Event(); proceed=threading.Event(); closed=threading.Event()
        calls=[]
        class Camera:
            def __init__(self,index): calls.append(index)
            def open(self): opened.set(); proceed.wait(2); return True
            def read(self): return None
            def close(self): closed.set()
        scanner=ReceiptScanner(camera_factory=Camera)
        self.addCleanup(scanner.dispose)
        scanner.set_active(True)
        self.assertTrue(opened.wait(2))
        scanner.set_active(False);scanner.set_active(True)
        self.assertEqual(len(calls),1)
        proceed.set()
        self.assertTrue(closed.wait(2))
        self.assertIsNone(scanner.snapshot()[1])

    def test_unavailable_camera_retains_manual_fallback_without_retry_loop(self):
        calls=[]
        class Camera:
            def __init__(self,index): calls.append(index)
            def open(self): return False
            def close(self): pass
        scanner=ReceiptScanner(camera_factory=Camera)
        self.addCleanup(scanner.dispose)
        scanner.set_active(True)
        self.wait_for(lambda: 'tidak tersedia' in scanner.snapshot()[3])
        for _ in range(10): scanner.set_active(True)
        self.assertEqual(len(calls),1)


@unittest.skipUnless(importlib.util.find_spec('kivy'), 'Kivy unavailable')
class ScannerGuiTests(unittest.TestCase):
    def setUp(self):
        from photobooth.meong_fly_gui import MeongFlyStage
        from photobooth.meong_fly_receipts import DemoReceiptLedger
        from photobooth.meong_fly_flow import MeongFlyFlow
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.flow=MeongFlyFlow(DemoReceiptLedger(Path(self.tmp.name)/'receipt.db'))
        class Scanner:
            active=False; disposed=False
            def set_active(self,active): self.active=active
            def snapshot(self):
                return (1,(2,1,bytes([255,0,0,0,0,255])), 'DEMO-SCAN-001','QR terbaca')
            def dispose(self): self.disposed=True;self.active=False
        self.scanner=Scanner()
        self.stage=MeongFlyStage(self.flow,scanner=self.scanner,size=(450,900),size_hint=(None,None))
        self.addCleanup(self.stage.dispose)

    def test_mirror_uv_reuse_and_explicit_claim(self):
        from kivy.graphics import Rectangle
        self.flow.open_scan();self.stage._refresh();self.stage.update(.03)
        self.assertTrue(self.scanner.active)
        self.assertEqual(self.stage.receipt.text,'DEMO-SCAN-001')
        self.assertIsNone(self.flow.active_receipt)
        self.assertEqual(self.flow.screen,'scan')
        texture=self.stage._scan_texture
        self.stage.update(.03)
        self.assertIs(self.stage._scan_texture,texture)
        rect=next(c for c in self.stage.canvas.before.children
                  if isinstance(c,Rectangle) and c.texture is texture)
        self.assertEqual(tuple(rect.tex_coords),MIRRORED_UV)
        self.stage.validate_receipt()
        self.assertEqual(self.flow.screen,'game')
        self.assertFalse(self.scanner.active)
        self.assertIsNone(self.stage._scan_texture)

    def test_rendered_preview_is_horizontally_mirrored(self):
        from PIL import Image
        self.flow.open_scan();self.stage._refresh();self.stage.update(.03)
        path=Path(self.tmp.name)/'mirror.png'
        self.stage.export_to_png(str(path))
        with Image.open(path) as image:
            left=image.getpixel((150,400));right=image.getpixel((300,400))
        self.assertGreater(left[2],left[0])  # Source right blue appears on left.
        self.assertGreater(right[0],right[2])

    def test_back_closes_preview_without_claim(self):
        self.flow.open_scan();self.stage._refresh();self.stage.update(.03)
        self.stage._handle_action('back')
        self.assertEqual(self.flow.screen,'start')
        self.assertFalse(self.scanner.active)
        self.assertIsNone(self.flow.active_receipt)
        self.stage.dispose();self.assertTrue(self.scanner.disposed)
