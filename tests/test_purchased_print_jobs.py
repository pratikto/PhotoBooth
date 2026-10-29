"""Actual paid binding/media/manifest send protocol; only synthetic printer."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from tests.paid_print_scenario import PaidPrintScenario
from photobooth.checkout_store import CheckoutConflict


class PaidPrintJobTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.scenario=PaidPrintScenario(self.temp.name);self.addCleanup(self.scenario.close)
        self.printer=Mock();self.printer.print_image.return_value=SimpleNamespace(success=True)

    def test_original_copies_and_hash_persist_before_send_without_satisfying_owed(self):
        s=self.scenario;before=s.manifest.read_bytes()
        def send(path,*,copies):
            m=json.loads(s.manifest.read_text());job=next(iter(m['test_print_jobs'].values()))
            self.assertEqual(job['state'],'SENDING');self.assertEqual(copies,2)
            self.assertEqual(job['payment_binding'],s.binding)
            self.assertEqual(job['output_sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
            return SimpleNamespace(success=True)
        self.printer.print_image.side_effect=send
        with closing(s.adapter(self.printer)) as adapter:
            self.assertEqual(adapter.print_result()['print_state'],'SUBMITTED')
            with self.assertRaises(ValueError):adapter.print_result()
        self.assertEqual(self.printer.print_image.call_count,1)
        self.assertEqual(s.store.fulfillment(s.binding['order_id'],'PB001')['obligation_state'],'OWED')
        a=json.loads(before);b=json.loads(s.manifest.read_text());a.pop('test_print_jobs');b.pop('test_print_jobs');self.assertEqual(a,b)
        self.assertIsNone(s.photo.printer)  # Dedicated bound photo guards were never relaxed.

    def test_failed_send_and_restart_never_resend_original_job(self):
        s=self.scenario;self.printer.print_image.side_effect=OSError('PRIVATE driver')
        with closing(s.adapter(self.printer)) as adapter:self.assertEqual(adapter.print_result()['print_state'],'UNCERTAIN')
        before=s.manifest.read_bytes()
        with closing(s.adapter(self.printer)) as recovered:
            with self.assertRaises(ValueError):recovered.print_result()
        self.assertEqual(s.manifest.read_bytes(),before);self.assertEqual(self.printer.print_image.call_count,1)

    def test_wrong_customer_refund_corrupt_media_and_retired_fence_deny_send(self):
        s=self.scenario;token=s.token;s.token='B'*43
        with self.assertRaises(PermissionError):s.adapter(self.printer)
        s.token=token
        with closing(s.adapter(self.printer)) as adapter:
            s.provider.rows[s.binding['order_id']]['transaction_status']='refund'
            with self.assertRaises(CheckoutConflict):adapter.print_result()
        self.printer.print_image.assert_not_called()
        self.assertEqual(json.loads(s.manifest.read_text())['test_print_jobs'],{})
        for kind in ('media','fence'):
            with self.subTest(kind=kind),TemporaryDirectory() as temp,closing(PaidPrintScenario(temp)) as fresh:
                with closing(fresh.adapter(self.printer)) as adapter:
                    if kind=='media':adapter.session.output_path.write_bytes(b'synthetic corrupt PNG')
                    else:fresh.store.rotate_service_fence(fresh.binding['order_id'],'PB001',0,suspended=True)
                    with self.assertRaises((ValueError,RuntimeError)):adapter.print_result()
                self.assertEqual(json.loads(fresh.manifest.read_text())['test_print_jobs'],{})
        self.printer.print_image.assert_not_called()

    def test_original_native_lease_prevents_a_second_print_owner(self):
        with closing(self.scenario.adapter(self.printer)):
            with self.assertRaises((RuntimeError,OSError)):self.scenario.adapter(self.printer)
        self.printer.print_image.assert_not_called()

    def test_two_designs_keep_each_frozen_copy_count_without_extra_capture(self):
        with TemporaryDirectory() as temp,closing(PaidPrintScenario(temp,quantities={'template_a':2,'template_b':1})) as s:
            before={p:p.read_bytes() for p in s.manifest.parent.rglob('*.jpg')}
            for session in ('session_001','session_002'):
                with closing(s.adapter(self.printer,session_id=session)) as adapter:adapter.print_result()
            self.assertEqual([c.kwargs['copies'] for c in self.printer.print_image.call_args_list],[2,1])
            self.assertEqual({p:p.read_bytes() for p in before},before)

    def test_close_during_send_keeps_native_lease_and_hides_late_result(self):
        entered,release=threading.Event(),threading.Event();s=self.scenario
        def send(*args,**kwargs):
            entered.set()
            if not release.wait(5):raise TimeoutError('fixture barrier timeout')
            return SimpleNamespace(success=True)
        self.printer.print_image.side_effect=send
        adapter=s.adapter(self.printer)
        with ThreadPoolExecutor(max_workers=1) as executor:
            result=executor.submit(adapter.print_result)
            try:
                self.assertTrue(entered.wait(2));adapter.close()
                self.assertEqual(adapter.snapshot(),{'phase':'claim_required'})
                with self.assertRaises((RuntimeError,OSError)):s.adapter(self.printer)
            finally:release.set()
            self.assertEqual(result.result(timeout=5),{'phase':'claim_required'})
        with closing(s.adapter(self.printer)) as recovered:
            with self.assertRaises(ValueError):recovered.print_result()
        self.assertEqual(self.printer.print_image.call_count,1)

    def test_real_child_exits_after_intent_or_effect_hold_without_replay(self):
        script='''import os,sys
from pathlib import Path
from types import SimpleNamespace
from tests.paid_print_scenario import PaidPrintScenario
from tests.paid_print_fixture import OfflinePaidPrint
s=PaidPrintScenario(sys.argv[1],reopen=True)
class Printer:
 def print_image(self,path,*,copies):
  with (Path(sys.argv[1])/'effects.txt').open('a') as f:f.write('one\\n');f.flush();os.fsync(f.fileno())
  os._exit(92)
if sys.argv[2]=='intent':
 original=OfflinePaidPrint._edit
 def stop(self,callback):
  original(self,callback);os._exit(91)
 OfflinePaidPrint._edit=stop
a=s.adapter(Printer());a.print_result()
'''
        for stage,code,effects in [('intent',91,0),('effect',92,1)]:
            with self.subTest(stage=stage),TemporaryDirectory() as temp,closing(PaidPrintScenario(temp)) as s:
                r=subprocess.run([sys.executable,'-c',script,temp,stage],capture_output=True,timeout=30)
                self.assertEqual(r.returncode,code,r.stderr.decode(errors='replace'))
                m=json.loads(s.manifest.read_text());self.assertEqual(next(iter(m['test_print_jobs'].values()))['state'],'SENDING')
                path=Path(temp)/'effects.txt';self.assertEqual(len(path.read_text().splitlines()) if path.exists() else 0,effects)
                with closing(s.adapter(self.printer)) as recovered:
                    with self.assertRaises(ValueError):recovered.print_result()
                self.printer.print_image.assert_not_called()
                self.assertEqual(s.store.fulfillment(s.binding['order_id'],'PB001')['obligation_state'],'OWED')
