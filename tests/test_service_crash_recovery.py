"""PAY-18 lost service replies retain original rights and immutable result."""
from contextlib import closing, ExitStack
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoTest
from tests.fulfillment_crash_fixture import AllocationHarness


class ServiceCrashTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def crash(self, boundary, code, ticket):
        child = subprocess.run([sys.executable, '-m', 'tests.service_crash_fixture',
                                str(self.root), boundary], input=ticket, text=True,
                               capture_output=True, timeout=30,
                               cwd=Path(__file__).resolve().parents[1])
        # Failure diagnostics contain no credential, even if a transport regresses.
        self.assertEqual(child.returncode, code, child.stderr.replace(ticket, '[REDACTED]')
                         .replace(ticket.split(':')[-1], '[REDACTED]'))
        journal = (self.root / 'visit.json').read_text()
        self.assertNotIn(ticket.split(':')[-1], journal)
        return json.loads(journal)

    def chain(self):
        with closing(AllocationHarness(self.root)) as initial:
            initial.flow.begin({'template_a': 2})
            initial.flow.refresh()
            ticket = initial.flow.customer_ticket()
            before = initial.flow.snapshot()
            oid = before['order']['order_id']
            self.assertIsNone(before['order']['grant_id'])
            initial.provider.db.execute("UPDATE mock_orders SET state='settlement' WHERE id=?", (oid,))
        grant_lost = self.crash('grant_reply_lost', 90, ticket)
        self.assertIsNone(grant_lost['order']['grant_id'])
        with closing(AllocationHarness(self.root)) as observed:
            grant = observed.store.get(oid)['grant_id']
            self.assertTrue(grant)
        claim = self.crash('claim_reply_lost', 91, ticket)
        operation = claim['customer_claim_operation_id']
        with closing(AllocationHarness(self.root)) as observed:
            self.assertEqual(observed.store.get(oid)['grant_id'], grant)
            attempt = observed.store.creation_attempt(oid)
            self.assertTrue(grant)
            self.assertIsNone(claim['order']['grant_id'])
            row = observed.store.db.execute('SELECT claim_operation_id FROM checkout_customer_capabilities '
                                           'WHERE order_id=?', (oid,)).fetchone()
            self.assertEqual(row[0], operation)
            self.assertTrue(observed.flow.customer_claim_required)
        started = self.crash('started_reply_lost', 92, ticket)
        self.assertEqual(started['customer_claim_operation_id'], operation)
        self.assertEqual(started['order']['grant_id'], grant)
        transaction = started['transaction_id']
        self.assertEqual(transaction, 'PB001V2AR_00000001')
        completed = self.crash('completed_reply_lost', 93, ticket)
        self.assertEqual(completed['phase'], 'COMPLETING')
        self.assertEqual(completed['order']['service_state'], 'STARTED')
        self.assertEqual(completed['transaction_id'], transaction)
        self.assertEqual(completed['customer_claim_operation_id'], operation)
        self.assertEqual(completed['allocation_operation_id'], started['allocation_operation_id'])
        return ticket, before, grant, attempt, completed

    def media(self, transaction):
        folder = self.root / 'photo-test' / 'photos' / transaction
        return {str(path.relative_to(folder)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in folder.rglob('*') if path.is_file()}

    def forbid_effects(self, harness):
        stack = ExitStack()
        harness.forbid_new_charge()
        for method in ('capture', 'compose', 'print_result', '_notify_delivery'):
            stack.enter_context(patch.object(PhotoTest, method,
                side_effect=AssertionError('Recovery cannot repeat a media/delivery effect')))
        return stack

    def assert_private(self, harness):
        self.assertTrue(harness.flow.active)
        self.assertTrue(harness.flow.customer_claim_required)
        with self.assertRaises(RuntimeError):
            harness.flow.prepare_capture()
        with self.assertRaises(RuntimeError):
            harness.flow.resume_permit()
        with closing(PhotoTest(harness.photo_root)) as photo:
            with self.assertRaises(RuntimeError):
                photo.restore(get_templates(), harness.binding(), None)
            self.assertIsNone(photo.transaction)

    def assert_identity(self, harness, before, grant, attempt, saved):
        oid = before['order']['order_id']
        row = harness.store.get(oid)
        self.assertEqual((row['checkout_key'], row['grant_id'], row['local_transaction_id']),
                         (before['checkout_key'], grant, saved['transaction_id']))
        self.assertEqual(row['service_state'], 'COMPLETED')
        self.assertEqual(harness.store.creation_attempt(oid), attempt)
        fulfillment = harness.store.fulfillment(oid, 'PB001')
        self.assertEqual((fulfillment['state'], fulfillment['obligation_state']), ('COMPOSED', 'OWED'))
        self.assertEqual(fulfillment['allocation_operation_id'], saved['allocation_operation_id'])
        for table in ('checkouts', 'checkout_fulfillments', 'checkout_customer_capabilities'):
            self.assertEqual(harness.store.db.execute('SELECT count(*) FROM ' + table).fetchone()[0], 1)
        self.assertEqual(harness.provider.db.execute('SELECT count(*) FROM mock_orders').fetchone()[0], 1)
        self.assertEqual(harness.store.db.execute('SELECT next_sequence FROM checkout_allocation_counters').fetchone()[0], 2)
        self.assertEqual(harness.store.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(harness.provider.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(harness.store.db.execute('PRAGMA journal_mode').fetchone()[0], 'wal')
        self.assertEqual(harness.store.db.execute('PRAGMA synchronous').fetchone()[0], 2)

    def complete_original(self, ticket, before, grant, attempt, saved):
        media = self.media(saved['transaction_id'])
        self.assertEqual(sum(name.endswith('.jpg') for name in media), 3)
        self.assertEqual(sum(name.endswith('.png') for name in media), 1)
        archives = self.root / 'visits'
        archived_bytes = {str(p.relative_to(archives)): p.read_bytes() for p in archives.rglob('*.json')}
        with closing(AllocationHarness(self.root)) as resumed, self.forbid_effects(resumed):
            self.assert_private(resumed)
            resumed.flow.refresh()  # Private observation cannot release this visit.
            self.assertEqual(resumed.flow.snapshot()['phase'], 'COMPLETING')
            self.assertEqual({str(p.relative_to(archives)): p.read_bytes()
                              for p in archives.rglob('*.json')}, archived_bytes)
            with patch.object(resumed.provider, 'get_status', wraps=resumed.provider.get_status) as status:
                resumed.flow.customer_claim(ticket)
                self.assertGreaterEqual(status.call_count, 1)
                with closing(PhotoTest(resumed.photo_root)) as photo:
                    binding = resumed.flow.resume_binding()
                    view = photo.restore(get_templates(), binding, resumed.flow.resume_permit())
                    self.assertEqual((view['phase'], view['captured']), ('result', 3))
                    self.assertEqual((view['copies'], view['session_count'], view['print_state']),
                                     (2, 1, 'NOT_SENT'))
                    self.assertIsNone(photo.printer)
                    self.assertIsNone(photo.drive_client)
                    self.assertFalse(photo.auto_print)
                    with self.assertRaises(RuntimeError):
                        resumed.flow.confirm_resume(saved['transaction_id'], 'capture')
                    with patch.object(resumed.client, 'service_transition',
                                      wraps=resumed.client.service_transition) as transitions:
                        resumed.flow.confirm_resume(saved['transaction_id'], view['phase'])
                        resumed.flow.request_complete()
                        result = resumed.flow.refresh()
                        self.assertEqual(transitions.call_count, 1)
                        self.assertEqual(transitions.call_args.args[:4],
                            (before['order']['order_id'], grant, 'COMPLETED', saved['transaction_id']))
                self.assertGreaterEqual(status.call_count, 4)
            self.assertEqual(result['phase'], 'COMPLETED')
            self.assertFalse(resumed.flow.active)
            self.assert_identity(resumed, before, grant, attempt, saved)
            self.assertEqual(result['customer_claim_operation_id'], saved['customer_claim_operation_id'])
            for archive in (self.root / 'visits' / (before['checkout_key'] + '.json'),
                            self.root / 'visits' / before['checkout_key'] / 'completed.json'):
                self.assertEqual(json.loads(archive.read_text()), result)
                self.assertNotIn(ticket.split(':')[-1], archive.read_text())
            self.assertEqual(self.media(saved['transaction_id']), media)
        with closing(AllocationHarness(self.root)) as reopened, self.forbid_effects(reopened):
            self.assertFalse(reopened.flow.active)
            self.assert_identity(reopened, before, grant, attempt, saved)
            self.assertEqual(self.media(saved['transaction_id']), media)

    def test_pay18_combined_lost_claim_started_completed_replies_restore_original_result_and_ack(self):
        original = self.chain()
        self.assertFalse((self.root / 'visits').exists())
        self.complete_original(*original)

    def test_pay18_completion_archive_exits_hold_until_history_index_and_final_journal_are_durable(self):
        base = self.root
        boundaries = (('completed_ack_before_archive', 94, False, False),
                      ('archive_operation_before_index', 95, True, False),
                      ('archive_index_before_final_journal', 96, True, True))
        for boundary, code, history_exists, index_exists in boundaries:
            with self.subTest(boundary=boundary):
                self.root = base / boundary
                original = self.chain()
                ticket, before, grant, attempt, completed = original
                media = self.media(completed['transaction_id'])
                saved = self.crash(boundary, code, ticket)
                self.assertEqual(saved['phase'], 'COMPLETING')
                self.assertEqual(saved['order']['service_state'], 'COMPLETED')
                self.assertEqual(saved['customer_claim_operation_id'], completed['customer_claim_operation_id'])
                directory = self.root / 'visits'
                history = directory / before['checkout_key'] / 'completed.json'
                index = directory / (before['checkout_key'] + '.json')
                self.assertEqual(history.exists(), history_exists)
                self.assertEqual(index.exists(), index_exists)
                for path in (history, index):
                    if path.exists():
                        archive = json.loads(path.read_text())
                        self.assertEqual(archive['phase'], 'COMPLETED')
                        self.assertEqual(archive['transaction_id'], completed['transaction_id'])
                        self.assertEqual(archive['order']['grant_id'], grant)
                with closing(AllocationHarness(self.root)) as held, self.forbid_effects(held):
                    self.assert_private(held)
                    with self.assertRaises(RuntimeError):
                        held.flow.begin({'template_b': 1})
                    with self.assertRaises(RuntimeError):
                        held.flow.open_archived(ticket)
                    self.assertEqual(held.flow.snapshot()['phase'], 'COMPLETING')
                    self.assert_identity(held, before, grant, attempt, saved)
                self.assertEqual(self.media(completed['transaction_id']), media)
                self.complete_original(*original)
                self.assertEqual(self.media(completed['transaction_id']), media)
        self.root = base

    def test_pay18_completed_reply_loss_cannot_use_cached_paid_during_outage_or_refund(self):
        ticket, before, grant, attempt, saved = self.chain()
        media = self.media(saved['transaction_id'])
        with closing(AllocationHarness(self.root)) as resumed, self.forbid_effects(resumed):
            self.assert_private(resumed)
            with patch.object(resumed.provider, 'get_status', side_effect=ConnectionError('Synthetic outage')):
                with self.assertRaisesRegex(RuntimeError, 'HTTP 503'):
                    resumed.flow.customer_claim(ticket)
            self.assert_private(resumed)
            self.assertFalse((self.root / 'visits').exists())
            oid = before['order']['order_id']
            resumed.provider.db.execute("UPDATE mock_orders SET state='refund' WHERE id=?", (oid,))
            with self.assertRaisesRegex(RuntimeError, 'HTTP 409'):
                resumed.flow.customer_claim(ticket)
            self.assert_private(resumed)
            self.assertEqual(resumed.store.get(oid)['state'], 'REVIEW_REQUIRED')
            self.assertEqual(resumed.store.get(oid)['grant_id'], grant)
            self.assertEqual(resumed.store.fulfillment(oid, 'PB001')['obligation_state'], 'OWED')
            self.assertEqual(resumed.flow.snapshot()['phase'], 'COMPLETING')
            self.assertFalse((self.root / 'visits').exists())
            self.assertEqual(self.media(saved['transaction_id']), media)

    def composition_crash(self, boundary, code):
        with closing(AllocationHarness(self.root)) as initial, closing(PhotoTest(initial.photo_root)) as photo:
            ticket = initial.create_reserved()
            initial.flow.prepare_capture()
            binding = initial.binding()
            photo.start_bound(get_templates(), {'template_a': 2}, binding)
            initial.flow.bind_transaction(binding['transaction_id'])
            initial.flow.refresh()
            before = initial.flow.snapshot()
            manifest = json.loads(photo.transaction.manifest_path.read_text())
            attempt = initial.store.creation_attempt(binding['order_id'])
        saved = self.crash(boundary, code, ticket)
        self.assertEqual(saved['order']['service_state'], 'STARTED')
        self.assertEqual(saved['transaction_id'], binding['transaction_id'])
        self.assertFalse((self.root / 'visits').exists())
        return ticket, before, binding, manifest, attempt, saved

    def test_cap16_composed_and_completion_intent_exits_restore_original_result_before_same_ack(self):
        base = self.root
        for boundary, code, phase in (('composed_before_completion_intent', 106, 'STARTED'),
                                      ('completion_intent_before_request', 107, 'COMPLETING')):
            with self.subTest(boundary=boundary):
                self.root = base / boundary
                ticket, before, binding, original_manifest, attempt, saved = self.composition_crash(boundary, code)
                self.assertEqual(saved['phase'], phase)
                media = self.media(saved['transaction_id'])
                self.assertEqual(sum(p.endswith('.jpg') for p in media), 3)
                self.assertEqual(sum(p.endswith('.png') for p in media), 1)
                with closing(AllocationHarness(self.root)) as resumed, self.forbid_effects(resumed), \
                        patch.object(resumed.client, 'allocate', side_effect=AssertionError('No reallocation')):
                    self.assert_private(resumed)
                    observed_phase = resumed.flow.snapshot()['phase']
                    resumed.flow.refresh()
                    self.assertEqual(resumed.flow.snapshot()['phase'], observed_phase)
                    row = resumed.store.get(binding['order_id'])
                    self.assertEqual((row['state'], row['service_state']), ('PAID', 'STARTED'))
                    self.assertEqual(resumed.store.fulfillment(binding['order_id'], 'PB001')['obligation_state'], 'OWED')
                    self.assertFalse((self.root / 'visits').exists())
                    with patch.object(resumed.provider, 'get_status', wraps=resumed.provider.get_status) as status, \
                            closing(PhotoTest(resumed.photo_root)) as photo:
                        resumed.flow.customer_claim(ticket)
                        view = photo.restore(get_templates(), binding, resumed.flow.resume_permit())
                        self.assertEqual((view['phase'], view['captured'], view['copies'], view['print_state']),
                                         ('result', 3, 2, 'NOT_SENT'))
                        current = json.loads(photo.transaction.manifest_path.read_text())
                        self.assertEqual(current['status'], 'COMPLETED')
                        self.assertEqual(current['output_intents']['session_001']['state'], 'COMMITTED')
                        for key in ('created_at', 'local_retention_days', 'drive_retention_days',
                                    'drive_photos_expire_at', 'frozen_order', 'payment_binding'):
                            self.assertEqual(current[key], original_manifest[key])
                        self.assertEqual(resumed.store.get(binding['order_id'])['service_state'], 'STARTED')
                        self.assertEqual(self.media(saved['transaction_id']), media)
                        with patch.object(resumed.client, 'service_transition',
                                          wraps=resumed.client.service_transition) as transitions:
                            resumed.flow.confirm_resume(binding['transaction_id'], view['phase'])
                            resumed.flow.request_complete()
                            result = resumed.flow.refresh()
                            self.assertEqual([call.args[:4] for call in transitions.call_args_list],
                                [(binding['order_id'], binding['grant_id'], state, binding['transaction_id'])
                                 for state in ('STARTED', 'COMPLETED')])
                        self.assertGreaterEqual(status.call_count, 3)
                        self.assertFalse(photo.auto_print)
                        self.assertIsNone(photo.printer)
                        self.assertIsNone(photo.drive_client)
                    self.assertEqual(result['phase'], 'COMPLETED')
                    self.assertFalse(resumed.flow.active)
                    self.assert_identity(resumed, before, binding['grant_id'], attempt, saved)
                    for path in (self.root / 'visits' / (before['checkout_key'] + '.json'),
                                 self.root / 'visits' / before['checkout_key'] / 'completed.json'):
                        self.assertEqual(json.loads(path.read_text()), result)
                        self.assertNotIn(ticket.split(':')[-1], path.read_text())
                    self.assertEqual(self.media(saved['transaction_id']), media)
                with closing(AllocationHarness(self.root)) as again, self.forbid_effects(again):
                    self.assertFalse(again.flow.active)
                    self.assert_identity(again, before, binding['grant_id'], attempt, saved)
                    self.assertEqual(self.media(saved['transaction_id']), media)
        self.root = base
