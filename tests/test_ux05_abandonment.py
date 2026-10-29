"""UX-05 leave/cancel under uncertainty: real HTTP and journals, offline provider."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import uuid

from tests.qris_v2_fixture import Fixture

PIN = '12345678'


class AmbiguousAbandonmentTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.f = Fixture(self.root, recovery_pin=PIN)
        self.addCleanup(self.close_fixture)

    def close_fixture(self):
        # Direct service calls never instantiate jobs.store; retire its lease
        # explicitly before reopening, including on Windows.
        self.f.flow.close()
        self.f.close()

    def reopen(self):
        provider = self.f.provider
        self.close_fixture()
        self.f = Fixture(self.root, recovery_pin=PIN)
        self.f.provider = provider
        self.f.backend.provider = provider

    def deny_replacement(self, oid, key):
        with self.assertRaisesRegex(RuntimeError, 'HTTP 409'):
            self.f.flow.client.create_order({'template_b':1}, uuid.uuid4().hex)
        with self.assertRaises(RuntimeError):
            self.f.service.begin({'template_b':1})
        self.assertEqual(self.f.store.db.execute('SELECT COUNT(*) FROM checkouts').fetchone()[0], 1)
        self.assertEqual(self.f.flow.snapshot()['checkout_key'], key)
        self.assertFalse(self.f.store.get(oid)['closed'])
        self.assertTrue(self.f.flow.active)

    def test_ux05_lost_creation_reply_404_and_operator_leave_cannot_release_unknown_order(self):
        self.f.provider.lost_charge = True
        with self.assertRaisesRegex(RuntimeError, 'HTTP 503'):
            self.f.service.begin({'template_a':1})
        initial = self.f.flow.snapshot()
        oid = self.f.store.db.execute('SELECT id FROM checkouts').fetchone()[0]
        attempt = self.f.store.creation_attempt(oid)
        self.assertEqual(attempt['phase'], 'UNCERTAIN')
        with patch.object(self.f.provider, 'get_status', return_value={'status_code':'404'}):
            self.f.service.cancel()
            ticket = self.f.flow.customer_ticket()
            self.assertIsNotNone(ticket)
            for _ in range(2):
                self.f.store.db.execute('UPDATE checkouts SET check_after=0')
                with self.assertRaisesRegex(RuntimeError, 'HTTP 503'):
                    self.f.flow.client.recovery_resolve(oid,PIN,uuid.uuid4().hex,'abandon','Synthetic leave')
                with self.assertRaisesRegex(RuntimeError, 'HTTP 503'):
                    self.f.flow.prepare_release(PIN)
                self.deny_replacement(oid, initial['checkout_key'])
        self.reopen()
        self.f.provider.outage = True
        self.f.service.check()
        self.deny_replacement(oid, initial['checkout_key'])
        self.assertIsNone(self.f.service.view()['qr_rgb'])
        self.assertIsNone(self.f.service.view()['ticket_qr_rgb'])
        self.assertIsNone(self.f.flow.customer_ticket())
        self.assertIsNone(self.f.store.get(oid)['grant_id'])
        self.assertEqual(self.f.store.creation_attempt(oid)['request_hash'], attempt['request_hash'])
        self.assertEqual(self.f.provider.charges, 1)
        self.assertNotIn(ticket.split(':')[-1], (self.root/'visit.json').read_text())
        self.assertEqual(self.f.store.db.execute('SELECT COUNT(*) FROM checkout_releases').fetchone()[0], 0)
        self.assertEqual(self.f.store.db.execute('SELECT COUNT(*) FROM checkout_recovery_actions').fetchone()[0], 0)

    def test_ux05_cancel_outage_restart_late_paid_preserves_private_original_owed(self):
        self.f.service.begin({'template_a':1})
        ticket = self.f.flow.customer_ticket()
        before = self.f.flow.snapshot()
        oid = before['order']['order_id']
        claim = dict(self.f.store.db.execute('SELECT * FROM checkout_customer_capabilities').fetchone())
        self.f.provider.outage = True
        with patch.object(self.f.provider, 'cancel', side_effect=TimeoutError('synthetic unknown cancellation')):
            self.f.service.cancel()
        self.assertEqual(self.f.flow.snapshot()['phase'], 'CANCELLING')
        self.reopen()
        self.f.service.check()
        self.deny_replacement(oid,before['checkout_key'])
        self.f.provider.outage = False
        self.f.paid()
        self.f.store.now = lambda: claim['created_at'] + 120
        self.f.flow._reconcile_at = 0
        self.f.service.check()
        self.assertEqual(self.f.flow.snapshot()['order']['state'], 'PAID')
        self.assertIsNone(self.f.store.get(oid)['grant_id'])
        self.assertEqual(self.f.store.fulfillment(oid,'PB001')['obligation_state'], 'OWED')
        self.assertEqual(self.f.store.db.execute('SELECT capability_hash FROM checkout_customer_capabilities').fetchone()[0],claim['capability_hash'])
        self.assertIsNone(self.f.service.view()['qr_rgb'])
        self.assertIsNone(self.f.service.view()['ticket_qr_rgb'])
        self.assertTrue(self.f.flow.customer_claim_required)
        self.deny_replacement(oid,before['checkout_key'])
        self.f.flow.customer_claim(ticket)
        grant = self.f.flow.snapshot()['order']['grant_id']
        self.assertIsNotNone(grant)
        self.assertEqual(self.f.flow.snapshot()['phase'], 'RESERVED')
        self.assertEqual(self.f.provider.charges, 1)
        self.assertNotIn(ticket.split(':')[-1], (self.root/'visit.json').read_text())
