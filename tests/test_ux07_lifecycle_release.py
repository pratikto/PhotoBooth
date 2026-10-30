"""UX-07.l2b: original paid requirement, drained worker and two-phase release."""
import hashlib
import json
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
import numpy as np

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoTest,PhotoJobs
from photobooth.qris_session import KioskCheckout,KioskLease
from tests import test_purchased_print_http as http
from tests.paid_print_fixture import OfflinePaidPrint
from tests.paid_lifecycle_fixture import MockReleaseWire

PIN='12345678'


class PurchasedReleaseTests(unittest.TestCase):
    def setUp(self):
        self.h=http.PaidPrintHttpTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.flow=self.make_flow(self.h.client)
        self.flow.begin({'template_a':2});self.flow.refresh();self.ticket=self.flow.customer_ticket()
        self.flow.acknowledge_ticket();self.oid=self.flow.snapshot()['order']['order_id']
        self.h.provider.rows[self.oid].update(transaction_status='settlement',status_code='200')
        self.h.store.db.execute('UPDATE checkouts SET check_after=0');self.flow.refresh();self.flow.prepare_capture()
        data=self.flow.snapshot();a=data['order']['fulfillment']
        self.binding={k:a[k] for k in ('fulfillment_id','transaction_id','allocation_operation_id','contract_hash','booth_id','merchant_id')}
        self.binding.update(order_id=self.oid,grant_id=data['order']['grant_id'])
        self.photo=PhotoTest(self.h.root/'photo');self.jobs=PhotoJobs(self.photo);self.addCleanup(self.close_jobs,self.jobs)
        self.photo.start_bound(get_templates(),{'template_a':2},self.binding)
        self.flow.bind_transaction(self.binding['transaction_id']);self.flow.refresh()
        for _ in range(3):self.photo.capture(np.zeros((48,64,3),dtype=np.uint8))
        self.photo.compose();self.flow.lock_customer();self.flow.customer_claim(self.ticket)
        self.requirement=self.flow.snapshot()['order']['delivery_requirement']
        self.output=self.photo.session.output_path;self.digest=hashlib.sha256(self.output.read_bytes()).hexdigest()
        self.original_manifest=json.loads(self.photo.transaction.manifest_path.read_text())
        self.flow.client=MockReleaseWire(self.h.client,self.h.backend)

    def make_flow(self,client):
        flow=KioskCheckout(self.h.root/'visit.json',client,mode='mock',booth_id='PB001',endpoint=client.base_url)
        self.addCleanup(flow.close);return flow

    def close_jobs(self,jobs):
        jobs.close();jobs.wait_closed(5)
        self.assertFalse(jobs._thread and jobs._thread.is_alive())

    def run_photo(self,action,*args):
        self.assertTrue(self.jobs.submit(action,*args))
        self.jobs.wait_closed(5)
        result=self.jobs.poll();self.assertIsNotNone(result)
        return result

    def isolate(self):
        data=self.flow.snapshot()
        return self.run_photo('isolate',self.oid,self.binding['transaction_id'],data['order']['release']['generation'])

    def assert_rights(self):
        order=self.h.store.get(self.oid,'PB001')
        self.assertEqual(order['state'],'PAID')
        self.assertEqual(order['grant_id'],self.binding['grant_id'])
        self.assertEqual(order['local_transaction_id'],self.binding['transaction_id'])
        self.assertEqual(self.h.backend.view(order)['delivery_requirement'],self.requirement)
        self.assertEqual(self.h.store.fulfillment(self.oid,'PB001')['obligation_state'],'OWED')
        self.assertEqual(hashlib.sha256(self.output.read_bytes()).hexdigest(),self.digest)
        manifest=json.loads(self.output.parents[1].joinpath('manifest.json').read_text())
        self.assertEqual({k:v for k,v in manifest.items() if k!='test_print_jobs'},
                         {k:v for k,v in self.original_manifest.items() if k!='test_print_jobs'})
        self.assertIsNone(self.photo.printer);self.assertIsNone(self.photo.drive_client)

    def print_worker(self,success=True):
        entered,release=threading.Event(),threading.Event();printer=Mock()
        def send(path,*,copies):
            self.assertEqual(copies,2);self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),self.digest)
            entered.set()
            if not release.wait(8):raise TimeoutError('Synthetic sender did not drain')
            return SimpleNamespace(success=success)
        printer.print_image.side_effect=send
        adapter=OfflinePaidPrint(self.h.backend,self.binding,self.photo.root,get_templates(),printer,
            self.ticket.split(':')[-1],self.flow.snapshot()['customer_claim_operation_id'],'session_001',
            active=lambda:not self.flow.customer_claim_required,controller=self.flow)
        worker=PhotoJobs(adapter);self.addCleanup(self.close_jobs,worker)
        self.assertTrue(worker.submit('print_result'));self.assertTrue(entered.wait(2))
        self.addCleanup(release.set)
        return worker,adapter,printer,release

    def test_mock_http_release_guard_remains_and_sending_sender_keeps_lease(self):
        with self.assertRaises(RuntimeError):self.h.client.release(self.oid,PIN,'e'*32)
        worker,adapter,printer,release=self.print_worker()
        self.flow.prepare_release(PIN);self.photo.hide_private()
        result=self.isolate();self.assertEqual(result.error,'RuntimeError')
        self.assertNotIn('isolation',result.value or {})
        with self.assertRaises(RuntimeError):self.flow.acknowledge_release(PIN,True)
        with self.assertRaises(RuntimeError):self.flow.begin({'template_b':1})
        worker.close()
        with self.assertRaises((RuntimeError,PermissionError)):
            KioskLease(str(self.photo.root/'paid-print.lock'))
        self.assertFalse(self.h.store.get(self.oid)['closed']);self.assert_rights()
        release.set();worker.wait_closed(5);self.assertFalse(worker._thread.is_alive())
        available=KioskLease(str(self.photo.root/'paid-print.lock'));available.close()
        with self.assertRaises(RuntimeError):adapter.print_result()
        self.assertEqual(printer.print_image.call_count,1)
        result=self.isolate();self.assertIsNone(result.error)
        self.flow.acknowledge_release(PIN,result.value['isolation']);self.assert_rights()

    def test_uncertain_sender_remains_held_after_drain_without_replay(self):
        worker,adapter,printer,release=self.print_worker(success=False)
        release.set();worker.wait_closed(5);outcome=worker.poll();self.assertIsNone(outcome.error)
        self.assertEqual(outcome.value['print_state'],'UNCERTAIN')
        self.flow.prepare_release(PIN);self.photo.hide_private()
        self.assertEqual(self.isolate().error,'RuntimeError')
        self.assertFalse(self.h.store.get(self.oid)['closed']);self.assertTrue(self.flow.active)
        with self.assertRaises(RuntimeError):self.flow.begin({'template_b':1})
        with self.assertRaises((RuntimeError,ValueError)):adapter.print_result()
        self.assertEqual(printer.print_image.call_count,1);self.assert_rights()

    def test_drained_job_lost_ack_restart_archive_and_return_preserve_original_rights(self):
        worker,adapter,printer,release=self.print_worker();release.set();worker.wait_closed(5)
        self.assertIsNone(worker.poll().error);worker.close()
        self.flow.prepare_release(PIN);self.photo.hide_private();result=self.isolate();self.assertIsNone(result.error)
        original=self.flow.client.release
        def lost(*args,**kwargs):original(*args,**kwargs);raise RuntimeError('Synthetic lost ACK')
        with patch.object(self.flow.client,'release',side_effect=lost):
            with self.assertRaises(RuntimeError):self.flow.acknowledge_release(PIN,result.value['isolation'])
        pending=self.flow.snapshot()
        with self.assertRaises(RuntimeError):self.flow.begin({'template_b':1})
        self.flow.close();client=self.h.make_client();self.flow=self.make_flow(MockReleaseWire(client,self.h.backend))
        self.flow.prepare_release(PIN);receipt=self.isolate().value['isolation']
        view=self.flow.acknowledge_release(PIN,receipt)
        self.assertEqual(view['release_operation_id'],pending['release_operation_id'])
        self.assertEqual(view['isolation_id'],pending['isolation_id'])
        archive=self.h.root/'visits'/(view['checkout_key']+'.json')
        self.assertEqual(json.loads(archive.read_text())['phase'],'SUSPENDED')
        self.assertNotIn(self.ticket.split(':')[-1],archive.read_text())
        self.assertEqual(self.h.store.db.execute('SELECT count(*) FROM checkout_releases').fetchone()[0],1)
        self.flow.begin({'template_b':1});self.flow.refresh()
        with self.assertRaises(RuntimeError):self.flow.open_archived(self.ticket)
        self.assertEqual(self.photo.snapshot()['phase'],'confirm')
        self.flow.request_cancel();self.flow.refresh();self.flow.open_archived(self.ticket)
        restored=self.run_photo('restore',get_templates(),self.flow.resume_binding(),self.flow.resume_permit())
        self.assertIsNone(restored.error);self.assertEqual(restored.value['phase'],'result')
        self.flow.confirm_resume(self.binding['transaction_id'],'result')
        self.assertEqual(printer.print_image.call_count,1);self.assertEqual(self.h.provider.charges,2)
        self.assert_rights()

    def test_archive_write_failure_never_admits_new_customer_before_retry(self):
        self.flow.prepare_release(PIN);self.photo.hide_private();receipt=self.isolate().value['isolation']
        with patch.object(self.flow,'_archive_snapshot',side_effect=OSError('Synthetic archive failure')):
            with self.assertRaises(OSError):self.flow.acknowledge_release(PIN,receipt)
        self.assertEqual(self.flow.snapshot()['phase'],'RELEASING');self.assertTrue(self.flow.active)
        with self.assertRaises(RuntimeError):self.flow.begin({'template_b':1})
        pending=self.flow.snapshot();self.flow.prepare_release(PIN)
        view=self.flow.acknowledge_release(PIN,self.isolate().value['isolation'])
        self.assertEqual(view['release_operation_id'],pending['release_operation_id'])
        self.assertEqual(view['isolation_id'],pending['isolation_id']);self.assertFalse(self.flow.active)
        self.assert_rights()

    def test_retired_print_callback_never_reactivates_after_fresh_customer_claim(self):
        worker,adapter,printer,release=self.print_worker()
        self.flow.lock_customer();self.photo.hide_private()
        release.set();worker.wait_closed(5);outcome=worker.poll()
        self.assertIsNone(outcome.error)
        self.assertEqual(outcome.value,{'phase':'claim_required'})
        self.flow.customer_claim(self.ticket)
        self.assertFalse(self.flow.customer_claim_required)
        self.assertEqual(adapter.snapshot(),{'phase':'claim_required'})
        with self.assertRaises(RuntimeError):adapter.print_result()
        self.assertEqual(printer.print_image.call_count,1)
        self.assert_rights()
