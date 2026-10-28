"""AR-09 release race, lost ACK and returning original customer ownership."""
import unittest
from contextlib import closing
import hashlib,secrets
from photobooth.checkout_store import CheckoutStore,CheckoutConflict
from photobooth import checkout_release
import tests.test_checkout_fulfillment as fixture

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        fixture.FulfillmentTests.setUp(self)
        self.capability=secrets.token_urlsafe(32)
        self.store.db.execute('INSERT INTO checkout_customer_capabilities (order_id,booth_id,capability_hash,created_at,expires_at) VALUES (?,?,?,?,?)',
            (self.oid,'PB001',hashlib.sha256(self.capability.encode()).hexdigest(),self.store.now(),self.store.now()+86400))
        fixture.FulfillmentTests.paid(self)
        self.grant=self.backend.claim(self.oid,'PB001',self.key)['grant_id']
        self.tx=self.backend.allocate(self.oid,'PB001',self.grant,'d'*32)['fulfillment']['transaction_id']

    def prepare(self):return checkout_release.prepare(self.store,self.oid,'PB001','e'*32,'operator-fixture')
    def ack(self):return checkout_release.acknowledge(self.store,self.oid,'PB001','e'*32,'f'*32)
    def claim(self):return self.backend.customer_claim(self.oid,'PB001',self.capability,'b'*32)

    def test_prepare_holds_booth_and_ack_releases_only_occupancy(self):
        before=self.store.get(self.oid);self.prepare()
        with self.assertRaises(CheckoutConflict):self.backend.create_order('PB001',{'template_a':1},'9'*32)
        self.ack();after=self.store.get(self.oid)
        for key in ('state','grant_id','service_state','local_transaction_id'):self.assertEqual(after[key],before[key])
        self.assertEqual(self.store.fulfillment(self.oid,'PB001')['obligation_state'],'OWED')
        self.backend.create_order('PB001',{'template_a':1},'9'*32)
        with self.assertRaises(CheckoutConflict):self.claim()

    def test_same_operations_survive_restart_and_mismatched_receipt_denied(self):
        first=self.prepare();self.assertEqual(self.prepare(),first)
        ack=self.ack()
        with closing(CheckoutStore(self.path)) as reopened:
            self.assertEqual(checkout_release.acknowledge(reopened,self.oid,'PB001','e'*32,'f'*32),ack)
            with self.assertRaises(CheckoutConflict):checkout_release.acknowledge(reopened,self.oid,'PB001','e'*32,'0'*32)

    def test_customer_reacquires_original_grant_and_allocation_with_new_fence(self):
        self.prepare();old=self.store.service_fence(self.oid,'PB001')['token'];self.ack()
        view=self.claim()
        self.assertFalse(view['closed']);self.assertEqual(view['grant_id'],self.grant)
        self.assertEqual(view['fulfillment']['transaction_id'],self.tx)
        self.assertNotEqual(view['service_fence']['token'],old)
        with self.assertRaises(CheckoutConflict):self.backend.service_transition(self.oid,'PB001',self.grant,'STARTED',self.tx,service_fence=old)
        self.backend.service_transition(self.oid,'PB001',self.grant,'STARTED',self.tx,service_fence=view['service_fence']['token'])

    def test_invalid_claim_and_legacy_operator_cannot_reactivate_suspended_rights(self):
        self.prepare();self.ack()
        with self.assertRaises(PermissionError):self.backend.customer_claim(self.oid,'PB001','x'*43,'b'*32)
        with self.assertRaises(CheckoutConflict):self.store.recovery_action(self.oid,'PB001','c'*32,'resume','fixture',self.tx,'operator-fixture')
        self.assertTrue(self.store.get(self.oid)['closed'])
