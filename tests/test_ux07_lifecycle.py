"""UX-07.l2a paid-print controller proof with original transport-off worker."""
from pathlib import Path
import hashlib
import unittest
from unittest.mock import patch
import numpy as np
from photobooth.qris_session import KioskCheckout
from photobooth.kiosk_v2.photos import PhotoTest
from photobooth.catalog import get_templates
from tests import test_purchased_print_http as http


class PurchasedLifecycleTests(unittest.TestCase):
    def test_original_paid_requirement_proof_expiry_and_deliberate_restore(self):
        h=http.PaidPrintHttpTests();h.setUp();self.addCleanup(h.doCleanups)
        flow=KioskCheckout(h.root/'visit.json',h.client,mode='mock',booth_id='PB001',endpoint=h.client.base_url)
        self.addCleanup(flow.close)
        flow.begin({'template_a':2});flow.refresh();ticket=flow.customer_ticket();flow.acknowledge_ticket()
        oid=flow.snapshot()['order']['order_id']
        h.provider.rows[oid].update(transaction_status='settlement',status_code='200')
        h.store.db.execute('UPDATE checkouts SET check_after=0');flow.refresh();flow.prepare_capture()
        data=flow.snapshot();a=data['order']['fulfillment']
        binding={k:a[k] for k in ('fulfillment_id','transaction_id','allocation_operation_id','contract_hash','booth_id','merchant_id')}
        binding.update(order_id=oid,grant_id=data['order']['grant_id'])
        photo=PhotoTest(h.root/'photo');self.addCleanup(photo.close)
        photo.start_bound(get_templates(),{'template_a':2},binding)
        flow.bind_transaction(binding['transaction_id']);flow.refresh()
        photo.capture(np.zeros((48,64,3),dtype=np.uint8))
        files={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in photo.transaction.folder_path.rglob('*') if p.is_file()}
        requirement=flow.snapshot()['order']['delivery_requirement']
        flow.lock_customer();photo.hide_private()
        self.assertEqual(photo.snapshot(),{'phase':'claim_required'})
        with self.assertRaises(RuntimeError):flow.resume_permit()
        for wrong in (ticket.replace(':PB001:',':PB002:'),ticket.rsplit(':',1)[0]+':'+'B'*43):
            with self.assertRaises((ValueError,RuntimeError)):flow.customer_claim(wrong)
            self.assertTrue(flow.customer_claim_required)
        flow.customer_claim(ticket)
        permit=flow.resume_permit();flow.lock_customer()
        with self.assertRaises(RuntimeError):photo.restore(get_templates(),binding,permit)
        flow.customer_claim(ticket)
        with patch('photobooth.qris_session.time.monotonic',return_value=flow._ownership_expires+1):
            with self.assertRaises(RuntimeError):flow.resume_permit()
        self.assertEqual({p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},files)
        flow.customer_claim(ticket)
        restored=photo.restore(get_templates(),flow.resume_binding(),flow.resume_permit())
        flow.confirm_resume(binding['transaction_id'],restored['phase'])
        self.assertEqual(restored['captured'],1)
        self.assertIsNone(photo.printer);self.assertIsNone(photo.drive_client)
        self.assertEqual(h.provider.charges,1)
        self.assertEqual(flow.snapshot()['order']['delivery_requirement'],requirement)
        self.assertEqual(h.store.fulfillment(oid,'PB001')['obligation_state'],'OWED')
        self.assertEqual({p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},files)
