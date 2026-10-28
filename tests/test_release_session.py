"""Real HTTP controller/photo isolation/archive/return path, synthetic media only."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import numpy as np
from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoTest
from tests.qris_v2_fixture import Fixture

class ReleaseSessionTests(TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.f=Fixture(self.root,recovery_pin='12345678');self.addCleanup(self.f.close)
        self.f.service.begin({'template_a':1});self.ticket=self.f.flow.customer_ticket()
        self.f.paid();self.f.service.check();self.f.service.prepare()
        data=self.f.flow.snapshot();self.tx=data['transaction_id'];order=data['order'];a=order['fulfillment']
        self.binding={k:a[k] for k in ('fulfillment_id','transaction_id','allocation_operation_id','contract_hash','booth_id','merchant_id')}
        self.binding.update(order_id=order['order_id'],grant_id=order['grant_id'])
        self.photo=PhotoTest(self.root/'photo-tests');self.addCleanup(self.photo.close)
        self.photo.start_bound(get_templates(),{'template_a':1},self.binding)
        self.photo.capture(np.zeros((24,32,3),dtype=np.uint8))
        self.f.service.started(self.tx)

    def retire(self):
        view=self.f.flow.prepare_release('12345678');self.photo.hide_private()
        return self.photo.isolate(view['order']['order_id'],self.tx,view['order']['release']['generation'])['isolation']

    def test_release_archive_new_customer_then_exact_return_preserves_original_photo(self):
        path=self.photo.session.initial_photo_paths[0];before=path.read_bytes()
        receipt=self.retire();view=self.f.flow.acknowledge_release('12345678',receipt)
        self.assertEqual(view['phase'],'SUSPENDED');self.assertFalse(self.f.flow.active)
        raw=(self.root/'visits'/(view['checkout_key']+'.json')).read_text()
        self.assertNotIn(self.ticket.split(':')[-1],raw);self.assertNotIn('12345678',raw)
        self.f.service.begin({'template_a':1})
        with self.assertRaises(RuntimeError):self.f.flow.open_archived(self.ticket)
        self.f.service.cancel()
        self.f.flow.open_archived(self.ticket)
        permit=self.f.flow.resume_permit();binding=self.f.flow.resume_binding()
        restored=self.photo.restore(get_templates(),binding,permit)
        self.assertEqual(restored['captured'],1);self.assertEqual(path.read_bytes(),before)
        self.f.flow.confirm_resume(self.tx,restored['phase'])
        self.assertEqual(self.f.flow.snapshot()['phase'],'STARTED')
        self.assertEqual(self.f.provider.charges,2)

    def test_lost_release_ack_reuses_persisted_isolation_and_operation(self):
        receipt=self.retire();original=self.f.flow.client.release
        def lose(*args,**kwargs):original(*args,**kwargs);raise RuntimeError('Synthetic lost ACK')
        with patch.object(self.f.flow.client,'release',side_effect=lose):
            with self.assertRaises(RuntimeError):self.f.flow.acknowledge_release('12345678',receipt)
        pending=self.f.flow.snapshot();self.assertEqual(pending['phase'],'RELEASING')
        self.f.flow.prepare_release('12345678')
        receipt=self.photo.isolate(self.binding['order_id'],self.tx,pending['order']['release']['generation'])['isolation']
        view=self.f.flow.acknowledge_release('12345678',receipt)
        self.assertEqual(view['isolation_id'],pending['isolation_id'])
        self.assertEqual(view['release_operation_id'],pending['release_operation_id'])
        self.assertEqual(self.f.store.db.execute('SELECT count(*) FROM checkout_releases').fetchone()[0],1)

    def test_gui_boolean_cannot_substitute_worker_receipt(self):
        self.f.flow.prepare_release('12345678')
        with self.assertRaises(RuntimeError):self.f.flow.acknowledge_release('12345678',True)
        self.assertFalse(self.f.store.get(self.binding['order_id'])['closed'])
