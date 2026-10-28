"""AR-03 exact backend-to-local binding, no duplicate folder or counter reuse."""
from contextlib import closing
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photobooth.catalog import get_templates
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.photos import PhotoTest
from tests.test_checkout_backend import FakeProvider,KEY,MERCHANT


class BoundPhotoTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.store=CheckoutStore(self.root/'orders.db');self.addCleanup(self.store.close)
        p=FakeProvider();b=CheckoutBackend(self.store,p,KEY,MERCHANT)
        self.quantities={'template_a':2}
        oid=b.create_order('PB001',self.quantities,'a'*32)['order_id']
        p.rows[oid].update(transaction_status='settlement',status_code='200')
        b._apply(self.store.get(oid),p.get_status(oid));grant=b.claim(oid,'PB001','a'*32)['grant_id']
        result=b.allocate(oid,'PB001',grant,'b'*32)
        allocation=result['fulfillment']
        self.binding={k:allocation[k] for k in ('fulfillment_id','transaction_id','allocation_operation_id','contract_hash','booth_id','merchant_id')}
        self.binding.update(order_id=oid,grant_id=grant)

    def test_first_manifest_binds_original_order_and_never_uses_photo_counter(self):
        with closing(PhotoTest(self.root/'photos')) as photo:
            first=[]
            original=photo.store._atomic_write_json
            def observe(path,data):
                if path.name=='manifest.json':first.append(json.loads(json.dumps(data)))
                return original(path,data)
            with patch.object(photo.store,'_atomic_write_json',side_effect=observe):
                view=photo.start_bound(get_templates(),self.quantities,self.binding)
            self.assertEqual(view['transaction_id'],self.binding['transaction_id'])
            self.assertEqual(first[0]['payment_binding'],self.binding)
            self.assertFalse(photo.store.state_path.exists())
            self.assertEqual(photo.start_bound(get_templates(),self.quantities,self.binding)['transaction_id'],view['transaction_id'])

    def test_restart_with_existing_manifest_is_held_without_overwriting(self):
        with closing(PhotoTest(self.root/'photos')) as photo:
            photo.start_bound(get_templates(),self.quantities,self.binding)
            path=photo.transaction.manifest_path;before=path.read_bytes()
        with closing(PhotoTest(self.root/'photos')) as restarted,self.assertRaises(FileExistsError):
            restarted.start_bound(get_templates(),self.quantities,self.binding)
        self.assertEqual(path.read_bytes(),before)

    def test_mismatched_frozen_contract_does_not_create_media_or_new_id(self):
        with closing(PhotoTest(self.root/'photos')) as photo,self.assertRaises(ValueError):
            photo.start_bound(get_templates(),self.quantities,dict(self.binding,contract_hash='0'*64))
        self.assertFalse((self.root/'photos'/'photos').exists())
