"""AR-09 stale service authority after private suspension/reacquisition."""
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase
from unittest.mock import patch
from photobooth.checkout_store import CheckoutStore,CheckoutConflict
import tests.test_checkout_fulfillment as fixture

class ServiceFenceTests(TestCase):
    def setUp(self):
        fixture.FulfillmentTests.setUp(self);fixture.FulfillmentTests.paid(self)
        self.grant=self.backend.claim(self.oid,'PB001',self.key)['grant_id']
        self.tx=self.backend.allocate(self.oid,'PB001',self.grant,'a'*32)['fulfillment']['transaction_id']

    def test_suspension_preserves_rights_but_blocks_grant_allocate_and_service(self):
        before=self.store.get(self.oid);rights=self.store.fulfillment(self.oid,'PB001')
        fence=self.store.rotate_service_fence(self.oid,'PB001',0,suspended=True)
        self.assertEqual(fence['generation'],1)
        with self.assertRaises(CheckoutConflict):self.store.grant(self.oid,'PB001',self.key)
        with self.assertRaises(CheckoutConflict):self.store.allocate_fulfillment(self.oid,'PB001',self.grant,'a'*32)
        with self.assertRaises(CheckoutConflict):self.backend.service_transition(self.oid,'PB001',self.grant,'STARTED',self.tx)
        self.assertEqual(self.store.get(self.oid),before)
        self.assertEqual(self.store.fulfillment(self.oid,'PB001'),rights)

    def test_reacquired_generation_accepts_only_new_token_and_rejects_stale_cas(self):
        one=self.store.rotate_service_fence(self.oid,'PB001',0,suspended=True)
        two=self.store.rotate_service_fence(self.oid,'PB001',1,suspended=False)
        self.assertNotEqual(one['token'],two['token'])
        with self.assertRaises(CheckoutConflict):self.store.rotate_service_fence(self.oid,'PB001',1,suspended=False)
        for token in (None,one['token']):
            with self.assertRaises(CheckoutConflict):
                self.backend.service_transition(self.oid,'PB001',self.grant,'STARTED',self.tx,service_fence=token)
        view=self.backend.service_transition(self.oid,'PB001',self.grant,'STARTED',self.tx,service_fence=two['token'])
        self.assertEqual(view['service_state'],'STARTED')

    def test_delayed_provider_reply_cannot_cross_suspension_boundary(self):
        import threading
        entered,release=threading.Event(),threading.Event();original=self.provider.get_status
        def slow(*args):entered.set();release.wait(3);return original(*args)
        with patch.object(self.provider,'get_status',side_effect=slow),ThreadPoolExecutor(max_workers=1) as pool:
            result=pool.submit(self.backend.service_transition,self.oid,'PB001',self.grant,'STARTED',self.tx)
            try:
                self.assertTrue(entered.wait(1))
                self.store.rotate_service_fence(self.oid,'PB001',0,suspended=True)
            finally:release.set()
            with self.assertRaises(CheckoutConflict):result.result(3)
        self.assertEqual(self.store.get(self.oid)['service_state'],'RESERVED')

    def test_fence_survives_restart_and_does_not_unblock_new_customer_by_itself(self):
        fence=self.store.rotate_service_fence(self.oid,'PB001',0,suspended=True)
        with closing(CheckoutStore(self.path)) as reopened:
            self.assertEqual(reopened.service_fence(self.oid,'PB001'),fence)
            with self.assertRaises(CheckoutConflict):
                reopened.begin('PB001',{'template_a':2},15000,'b'*32)

    def test_schema_upgrade_does_not_fabricate_a_fence_for_legacy_order(self):
        before=self.store.get(self.oid)
        self.store.db.execute('DROP TABLE checkout_service_fences')
        with closing(CheckoutStore(self.path)) as reopened:
            self.assertIsNone(reopened.service_fence(self.oid,'PB001'))
            self.assertEqual(reopened.get(self.oid),before)
