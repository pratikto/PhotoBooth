"""CAP-01–05 exact child exits: same paid identities, no second allocation."""
from contextlib import closing
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from photobooth.catalog import get_templates
from photobooth.capture_journal import CaptureRecoveryRequired
from photobooth.kiosk_v2.photos import PhotoTest
from tests.fulfillment_crash_fixture import AllocationHarness


class AllocationCrashTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def crash(self, boundary, code):
        root = self.root / boundary
        with closing(AllocationHarness(root)) as original:
            ticket = original.create_reserved()
            before = original.flow.snapshot()
            attempt = original.store.creation_attempt(before['order']['order_id'])
        child = subprocess.run([sys.executable, '-m', 'tests.fulfillment_crash_fixture',
                                str(root), boundary], input=ticket, text=True,
                               capture_output=True, timeout=30,
                               cwd=Path(__file__).resolve().parents[1])
        self.assertEqual(child.returncode, code, child.stderr)
        saved = json.loads((root / 'visit.json').read_text())
        self.assertNotIn(ticket.split(':')[-1], (root / 'visit.json').read_text())
        return root, ticket, before, attempt, saved

    def assert_private_before_proof(self, harness):
        self.assertTrue(harness.flow.customer_claim_required)
        with self.assertRaises(RuntimeError):
            harness.flow.prepare_capture()
        with self.assertRaises(RuntimeError):
            harness.flow.resume_permit()

    def assert_one_mapping(self, harness, before, attempt, transaction, operation):
        oid = before['order']['order_id']
        row = harness.store.get(oid)
        self.assertEqual(row['state'], 'PAID')
        self.assertEqual(row['grant_id'], before['order']['grant_id'])
        self.assertEqual(row['checkout_key'], before['checkout_key'])
        self.assertEqual(row['local_transaction_id'], transaction)
        self.assertEqual(harness.store.creation_attempt(oid), attempt)
        self.assertEqual(harness.store.fulfillment(oid, 'PB001')['obligation_state'], 'OWED')
        replay = harness.client.allocate(oid, row['grant_id'], operation)
        self.assertEqual(replay['fulfillment']['transaction_id'], transaction)
        self.assertEqual(harness.store.db.execute('SELECT count(*) FROM checkouts').fetchone()[0], 1)
        self.assertEqual(harness.store.db.execute('SELECT count(*) FROM checkout_fulfillments').fetchone()[0], 1)
        self.assertEqual(harness.provider.db.execute('SELECT count(*) FROM mock_orders').fetchone()[0], 1)
        self.assertEqual(harness.store.db.execute('SELECT next_sequence FROM checkout_allocation_counters').fetchone()[0], 2)
        self.assertEqual(harness.store.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(harness.provider.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(harness.store.db.execute('PRAGMA journal_mode').fetchone()[0], 'wal')
        self.assertEqual(harness.store.db.execute('PRAGMA synchronous').fetchone()[0], 2)

    def test_cap01_exit_before_local_or_backend_intent_creates_only_first_original_allocation(self):
        for boundary, code in (('before_local_intent', 81), ('before_backend_intent', 82)):
            with self.subTest(boundary=boundary):
                root, ticket, before, attempt, saved = self.crash(boundary, code)
                self.assertFalse((root / 'photo-test').exists())
                with closing(AllocationHarness(root)) as resumed:
                    resumed.forbid_new_charge()
                    self.assert_private_before_proof(resumed)
                    self.assertIsNone(resumed.store.get(before['order']['order_id'])['local_transaction_id'])
                    resumed.flow.customer_claim(ticket)
                    self.assertEqual(resumed.flow.snapshot()['phase'], 'RESERVED')
                    resumed.flow.prepare_capture()
                    current = resumed.flow.snapshot()
                    transaction = current['transaction_id']
                    self.assertEqual(transaction, 'PB001V2AR_00000001')
                    if saved.get('allocation_operation_id'):
                        self.assertEqual(current['allocation_operation_id'], saved['allocation_operation_id'])
                    self.assert_one_mapping(resumed, before, attempt, transaction, current['allocation_operation_id'])
                    self.assertFalse(resumed.photo_root.exists())

    def test_cap02_exit_after_backend_commit_recovers_same_allocation_before_first_folder(self):
        root, ticket, before, attempt, saved = self.crash('allocated_reply_lost', 83)
        self.assertIsNone(saved['transaction_id'])
        operation = saved['allocation_operation_id']
        with closing(AllocationHarness(root)) as resumed:
            resumed.forbid_new_charge()
            self.assert_private_before_proof(resumed)
            transaction = resumed.store.get(before['order']['order_id'])['local_transaction_id']
            self.assertEqual(transaction, 'PB001V2AR_00000001')
            self.assertFalse(resumed.photo_root.exists())
            resumed.flow.customer_claim(ticket)
            self.assertEqual(resumed.flow.snapshot()['transaction_id'], transaction)
            with closing(PhotoTest(resumed.photo_root)) as photo, \
                    patch.object(PhotoTest, 'capture', side_effect=AssertionError('No shutter replay')), \
                    patch.object(PhotoTest, 'compose', side_effect=AssertionError('No render replay')):
                view = photo.restore_allocated(get_templates(), {'template_a': 2}, resumed.flow.resume_binding(),
                                              resumed.flow.resume_permit(), 'RESERVED')
                self.assertEqual((view['transaction_id'], view['captured']), (transaction, 0))
                self.assertFalse(photo.store.state_path.exists())
                manifest = photo.transaction.manifest_path.read_bytes()
                self.assertEqual(resumed.flow.confirm_resume(transaction, view['phase'])['phase'], 'STARTED')
                self.assertEqual(photo.transaction.manifest_path.read_bytes(), manifest)
            self.assert_one_mapping(resumed, before, attempt, transaction, operation)

    def restore_original(self, boundary, code):
        root, ticket, before, attempt, saved = self.crash(boundary, code)
        transaction = saved['transaction_id']
        folder = root / 'photo-test' / 'photos' / transaction
        manifest_path = folder / 'manifest.json'
        original_manifest = manifest_path.read_bytes() if manifest_path.exists() else None
        expected_service = 'STARTED' if boundary == 'started_reply_lost' else 'RESERVED'
        with closing(AllocationHarness(root)) as resumed:
            resumed.forbid_new_charge()
            self.assert_private_before_proof(resumed)
            self.assertEqual(resumed.store.get(before['order']['order_id'])['service_state'], expected_service)
            self.assertEqual(saved['order']['service_state'], 'RESERVED')
            resumed.flow.customer_claim(ticket)
            binding = resumed.flow.resume_binding()
            self.assertEqual(binding['transaction_id'], transaction)
            with closing(PhotoTest(resumed.photo_root)) as photo, \
                    patch.object(PhotoTest, 'capture', side_effect=AssertionError('No shutter replay')), \
                    patch.object(PhotoTest, 'compose', side_effect=AssertionError('No composition replay')), \
                    patch.object(PhotoTest, 'print_result', side_effect=AssertionError('No print replay')):
                view = photo.restore_allocated(get_templates(), {'template_a': 2}, binding,
                                              resumed.flow.resume_permit(), expected_service)
                self.assertEqual((view['transaction_id'], view['captured'], view['phase']),
                                 (transaction, 0, 'capture'))
                self.assertEqual(photo.transaction.manifest['payment_binding'], binding)
                if original_manifest is not None:
                    self.assertEqual(manifest_path.read_bytes(), original_manifest)
                self.assertFalse(photo.store.state_path.exists())
                self.assertIsNone(photo.printer)
                self.assertIsNone(photo.drive_client)
                self.assertEqual(list(folder.glob('**/*.jpg')), [])
                self.assertEqual(list(folder.glob('**/*.png')), [])
                ready = resumed.flow.confirm_resume(transaction, view['phase'])
                self.assertEqual(ready['phase'], 'STARTED')
                self.assertEqual(ready['order']['service_state'], 'STARTED')
                acknowledged_manifest = manifest_path.read_bytes()
            self.assert_one_mapping(resumed, before, attempt, transaction, saved['allocation_operation_id'])
            self.assertEqual(manifest_path.read_bytes(), acknowledged_manifest)
        # A second freshly opened controller/DB retains the same ACK after the
        # first successful recovery; capture count and allocation cannot advance.
        with closing(AllocationHarness(root)) as reopened:
            reopened.forbid_new_charge()
            reopened.flow.customer_claim(ticket)
            self.assertEqual(reopened.flow.resume_binding()['transaction_id'], transaction)
            self.assert_one_mapping(reopened, before, attempt, transaction, saved['allocation_operation_id'])
            self.assertEqual(manifest_path.read_bytes(), acknowledged_manifest)

    def test_cap03_exit_after_empty_folder_before_manifest_initializes_only_original_id(self):
        self.restore_original('folder_before_manifest', 84)

    def test_cap04_exit_after_first_manifest_before_started_preserves_manifest_and_same_ack(self):
        self.restore_original('manifest_before_started', 85)

    def test_cap05_exit_after_started_acceptance_replays_original_ack_without_capture(self):
        self.restore_original('started_reply_lost', 86)

    def test_cap03_orphan_bytes_after_folder_crash_are_held_without_recency_lookup(self):
        root, ticket, before, attempt, saved = self.crash('folder_before_manifest', 84)
        transaction = saved['transaction_id']
        folder = root / 'photo-test' / 'photos' / transaction
        orphan = folder / 'unknown.bin'
        orphan.write_bytes(b'SYNTHETIC ORPHAN - DO NOT ADOPT')
        neighbor = folder.parent / 'PB001V2AR_99999999'
        neighbor.mkdir()
        (neighbor / 'unknown.bin').write_bytes(b'SYNTHETIC OTHER SESSION')
        with closing(AllocationHarness(root)) as resumed:
            resumed.forbid_new_charge()
            resumed.flow.customer_claim(ticket)
            with closing(PhotoTest(resumed.photo_root)) as photo:
                original_iterdir = Path.iterdir
                def exact_folder_only(path):
                    if path == folder.parent:
                        raise AssertionError('Recovery must not search other transactions by recency')
                    return original_iterdir(path)
                with patch.object(Path, 'iterdir', autospec=True, side_effect=exact_folder_only), \
                        self.assertRaises(CaptureRecoveryRequired):
                    photo.restore_allocated(get_templates(), {'template_a': 2}, resumed.flow.resume_binding(),
                                            resumed.flow.resume_permit(), 'RESERVED')
                self.assertTrue(photo.transaction is None)
                self.assertFalse(photo.store.state_path.exists())
            self.assertEqual(orphan.read_bytes(), b'SYNTHETIC ORPHAN - DO NOT ADOPT')
            self.assertEqual((neighbor / 'unknown.bin').read_bytes(), b'SYNTHETIC OTHER SESSION')
            self.assertFalse((folder / 'manifest.json').exists())
            self.assert_one_mapping(resumed, before, attempt, transaction, saved['allocation_operation_id'])
