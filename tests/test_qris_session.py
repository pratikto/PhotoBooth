"""Kiosk restart/timeout and automatic transition tests without Kivy."""
from pathlib import Path
import tempfile
import threading
import unittest
from photobooth.checkout_store import CheckoutStore
from photobooth.checkout_backend import CheckoutBackend
from photobooth.qris_mock import MockQrisProvider
from photobooth.qris_session import KioskCheckout


class LocalClient:
    def __init__(self, backend): self.backend = backend; self.drop = False
    def create_order(self, quantities, key):
        value = self.backend.create_order('PB001', quantities, key)
        if self.drop: self.drop = False; raise TimeoutError('lost creation response')
        return value
    def status(self, oid): return self.backend.status(oid, 'PB001')
    def claim(self, oid, key): return self.backend.claim(oid, 'PB001', key)
    def service_transition(self, oid, grant, state, tx):
        return self.backend.service_transition(oid, 'PB001', grant, state, tx)
    def cancel(self, oid): return self.backend.cancel(oid, 'PB001')
    def close(self): pass


class KioskSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.now = [1000.0]
        self.provider = MockQrisProvider(self.root/'provider.db', settle_after=5, now=lambda:self.now[0])
        self.store = CheckoutStore(self.root/'store.db', now=lambda:self.now[0])
        self.backend = CheckoutBackend(self.store, self.provider, 'mock-key', 'MOCK')
        self.client = LocalClient(self.backend)
        self.flow = self.make_flow()

    def make_flow(self):
        return KioskCheckout(self.root/'journal.json', self.client, mode='mock', booth_id='PB001', endpoint='http://127.0.0.1:8765')

    def tearDown(self):
        self.flow.close(); self.store.close(); self.provider.close(); self.tmp.cleanup()

    def reserved(self):
        self.flow.begin({'template_a':2}); self.flow.refresh()
        self.now[0] += 6; self.flow.refresh()
        self.assertEqual(self.flow.snapshot()['phase'], 'RESERVED')

    def test_auto_paid_grant_without_manual_confirmation(self):
        self.reserved()
        self.assertTrue(self.flow.snapshot()['order']['grant_id'])

    def test_journal_is_written_before_charge_and_survives_lost_reply(self):
        self.client.drop = True
        before = self.flow.begin({'template_a':2})
        self.assertTrue((self.root/'journal.json').exists())
        with self.assertRaises(TimeoutError): self.flow.refresh()
        self.flow.close(); self.flow = self.make_flow(); self.flow.refresh()
        self.assertEqual(self.flow.snapshot()['checkout_key'], before['checkout_key'])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkouts').fetchone()[0], 1)

    def test_second_gui_cannot_consume_same_journal(self):
        with self.assertRaises(RuntimeError): self.make_flow()

    def test_environment_mismatch_is_not_silently_reset(self):
        self.flow.begin({'template_a':2}); self.flow.close()
        with self.assertRaises(ValueError):
            KioskCheckout(self.root/'journal.json', self.client, mode='sandbox', booth_id='PB001', endpoint='http://127.0.0.1:8765')
        self.flow = self.make_flow()

    def test_partial_capture_restart_is_held_not_restarted(self):
        self.reserved(); self.flow.prepare_capture(); self.flow.bind_transaction('PB001_00000001')
        self.flow.refresh(); self.flow.close(); self.flow = self.make_flow()
        self.assertEqual(self.flow.refresh()['phase'], 'RECOVERY')
        with self.assertRaises(RuntimeError): self.flow.prepare_capture()

    def test_successful_service_completes_and_allows_next_visit(self):
        self.reserved(); self.flow.prepare_capture(); self.flow.bind_transaction('PB001_00000001')
        self.flow.refresh(); self.flow.request_complete(); self.flow.refresh()
        self.assertFalse(self.flow.active)
        self.assertEqual(self.flow.begin({'template_a':1})['phase'], 'CREATING')

    def test_cancel_cannot_discard_settlement(self):
        self.flow.begin({'template_a':2}); self.flow.refresh()
        self.now[0] += 6; self.flow.request_cancel(); self.flow.refresh()
        self.assertEqual(self.flow.snapshot()['phase'], 'RESERVED')

    def test_cancel_before_settlement_is_safe(self):
        self.flow.begin({'template_a':2}); self.flow.refresh()
        self.flow.request_cancel(); self.flow.refresh()
        self.assertEqual(self.flow.snapshot()['phase'], 'CANCELLED')

    def test_snapshot_does_not_wait_for_network(self):
        self.flow.begin({'template_a':2})
        started, release, done = threading.Event(), threading.Event(), threading.Event()
        original = self.client.create_order
        def slow(*args):
            started.set(); release.wait(2); return original(*args)
        self.client.create_order = slow
        thread = threading.Thread(target=self.flow.refresh)
        thread.start()
        try:
            self.assertTrue(started.wait(1))
            snapshot_thread = threading.Thread(target=lambda:(self.flow.snapshot(),done.set()))
            snapshot_thread.start()
            self.assertTrue(done.wait(.5))
            snapshot_thread.join()
        finally: release.set(); thread.join()

    def test_frozen_cart_cannot_change(self):
        self.flow.begin({'template_a':2})
        with self.assertRaises(RuntimeError): self.flow.begin({'template_a':1})

    def test_unpayable_mock_qr_label(self):
        self.flow.begin({'template_a':2}); data = self.flow.refresh()
        self.assertIn('NOT QRIS', data['order']['qr_payload'])
        self.assertIsNone(data['order']['qr_url'])
