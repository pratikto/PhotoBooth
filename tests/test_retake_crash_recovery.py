"""Bound retake abrupt exits preserve private original photos, quota and OWED."""
from contextlib import closing, ExitStack
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from photobooth.catalog import get_templates
from photobooth.capture_journal import CaptureRecoveryRequired
from photobooth.kiosk_v2.photos import PhotoTest
from tests.fulfillment_crash_fixture import AllocationHarness


class RetakeCrashTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def crash(self, stage, code):
        root = self.root / stage
        with closing(AllocationHarness(root)) as initial, closing(PhotoTest(initial.photo_root)) as photo:
            ticket = initial.create_reserved()
            initial.flow.prepare_capture()
            binding = initial.binding()
            photo.start_bound(get_templates(), {'template_a': 2}, binding)
            initial.flow.bind_transaction(binding['transaction_id'])
            initial.flow.refresh()
            for color in (17, 83, 201):
                photo.capture(np.full((24, 32, 3), color, dtype=np.uint8))
            before = json.loads(photo.transaction.manifest_path.read_text())
            originals = {p.relative_to(photo.transaction.folder_path).as_posix(): p.read_bytes()
                         for p in photo.session.initial_photo_paths}
            attempt = initial.store.creation_attempt(binding['order_id'])
        child = subprocess.run([sys.executable, '-m', 'tests.retake_crash_fixture', str(root), stage],
                               input=ticket, text=True, capture_output=True, timeout=30,
                               cwd=Path(__file__).resolve().parents[1])
        diagnostic = child.stderr.replace(ticket, '[REDACTED]').replace(ticket.split(':')[-1], '[REDACTED]')
        self.assertEqual(child.returncode, code, diagnostic)
        self.assertNotIn(ticket.split(':')[-1], (root / 'visit.json').read_text())
        return root, ticket, binding, before, originals, attempt

    def forbidden_effects(self, harness):
        harness.forbid_new_charge()
        stack = ExitStack()
        for method in ('capture', 'compose', 'print_result', '_notify_delivery'):
            stack.enter_context(patch.object(PhotoTest, method,
                side_effect=AssertionError('Restoration must not replay media or delivery')))
        return stack

    def private_before_proof(self, harness, photo, binding):
        self.assertTrue(harness.flow.customer_claim_required)
        with self.assertRaises(RuntimeError):
            harness.flow.resume_permit()
        with self.assertRaises(CaptureRecoveryRequired):
            photo.restore(get_templates(), binding, None)
        self.assertIsNone(photo.transaction)
        self.assertNotIn('thumbnails', photo.snapshot())

    def original_identity(self, harness, binding, before, originals, attempt, photo):
        self.assertEqual(photo.transaction.manifest['payment_binding'], binding)
        current = json.loads(photo.transaction.manifest_path.read_text())
        for key in ('transaction_id', 'booth_id', 'created_at', 'local_retention_days',
                    'drive_retention_days', 'drive_photos_expire_at', 'frozen_order'):
            self.assertEqual(current[key], before[key], key)
        self.assertEqual(current['sessions'][0]['print_copies'], 2)
        for path, contents in originals.items():
            self.assertEqual((photo.transaction.folder_path / path).read_bytes(), contents)
        self.assertFalse(photo.store.state_path.exists())
        self.assertIsNone(photo.printer)
        self.assertIsNone(photo.drive_client)
        self.assertFalse(photo.auto_print)
        row = harness.store.get(binding['order_id'])
        self.assertEqual((row['state'], row['service_state'], row['grant_id'], row['local_transaction_id']),
                         ('PAID', 'STARTED', binding['grant_id'], binding['transaction_id']))
        fulfillment = harness.store.fulfillment(binding['order_id'], 'PB001')
        self.assertEqual(fulfillment['obligation_state'], 'OWED')
        for key in ('fulfillment_id', 'transaction_id', 'allocation_operation_id', 'contract_hash'):
            self.assertEqual(fulfillment[key], binding[key])
        capability = harness.store.db.execute('SELECT claim_operation_id FROM checkout_customer_capabilities '
                                             'WHERE order_id=?', (binding['order_id'],)).fetchone()
        self.assertEqual(capability[0], harness.flow.snapshot()['customer_claim_operation_id'])
        self.assertEqual(harness.store.creation_attempt(binding['order_id']), attempt)
        for table in ('checkouts', 'checkout_fulfillments', 'checkout_customer_capabilities'):
            self.assertEqual(harness.store.db.execute('SELECT count(*) FROM ' + table).fetchone()[0], 1)
        self.assertEqual(harness.provider.db.execute('SELECT count(*) FROM mock_orders').fetchone()[0], 1)
        self.assertEqual(harness.store.db.execute('SELECT next_sequence FROM checkout_allocation_counters').fetchone()[0], 2)
        self.assertEqual(harness.store.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(harness.provider.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(harness.store.db.execute('PRAGMA journal_mode').fetchone()[0], 'wal')
        self.assertEqual(harness.store.db.execute('PRAGMA synchronous').fetchone()[0], 2)

    def restore(self, harness, photo, ticket, binding):
        with patch.object(harness.provider, 'get_status', wraps=harness.provider.get_status) as status:
            harness.flow.customer_claim(ticket)
            self.assertEqual(harness.flow.resume_binding(), binding)
            view = photo.restore(get_templates(), binding, harness.flow.resume_permit())
            harness.flow.confirm_resume(binding['transaction_id'], view['phase'])
            self.assertGreaterEqual(status.call_count, 3)
        return view

    def test_cap11_selection_and_empty_intent_exits_keep_selected_original_and_one_deliberate_retake(self):
        for stage, code in (('selection', 100), ('intent', 101)):
            with self.subTest(stage=stage):
                root, ticket, binding, before, originals, attempt = self.crash(stage, code)
                with closing(AllocationHarness(root)) as resumed, closing(PhotoTest(resumed.photo_root)) as photo:
                    with self.forbidden_effects(resumed):
                        self.private_before_proof(resumed, photo, binding)
                        view = self.restore(resumed, photo, ticket, binding)
                    self.assertEqual((view['phase'], view['captured'], view['retake'], view['retake_used']),
                                     ('capture', 3, True, False))
                    self.assertEqual(photo.session.selected_index, 1)
                    self.assertEqual(photo.session.final_photo_paths, photo.session.initial_photo_paths)
                    current = json.loads(photo.transaction.manifest_path.read_text())
                    if stage == 'intent':
                        intent = next(i for i in current['capture_intents'].values() if i['role'] == 'retake')
                        self.assertEqual(intent['state'], 'VOID_BEFORE_FRAME')
                        self.assertEqual(intent['reason'], 'no_saved_bytes')
                    self.original_identity(resumed, binding, before, originals, attempt, photo)
                    # Explicit synthetic customer action, never part of restoration.
                    photo.capture(np.full((24, 32, 3), 247, dtype=np.uint8))
                    self.assertTrue(photo.session.retake_used)
                    self.assertEqual(photo.session.retake_target_index, 1)
                    manifest = photo.transaction.manifest_path.read_bytes()
                    with self.assertRaises(ValueError):
                        photo.retake(0)
                    with self.assertRaises(ValueError):
                        photo.capture(np.full((24, 32, 3), 119, dtype=np.uint8))
                    self.assertEqual(photo.transaction.manifest_path.read_bytes(), manifest)
                with closing(AllocationHarness(root)) as again, closing(PhotoTest(again.photo_root)) as photo, \
                        self.forbidden_effects(again):
                    self.private_before_proof(again, photo, binding)
                    view = self.restore(again, photo, ticket, binding)
                    self.assertEqual((view['phase'], view['captured'], view['retake_used']), ('review', 3, True))
                    self.assertEqual(photo.session.retake_target_index, 1)
                    self.assertEqual(photo.transaction.manifest_path.read_bytes(), manifest)
                    self.original_identity(again, binding, before, originals, attempt, photo)

    def folder(self, root, binding):
        return root / 'photo-test' / 'photos' / binding['transaction_id']

    def file_bytes(self, folder):
        return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}

    def retake_record(self, folder):
        manifest = json.loads((folder / 'manifest.json').read_text())
        return manifest, next(i for i in manifest['capture_intents'].values() if i['role'] == 'retake')

    def assert_consumed(self, photo, view, intent, saved_bytes):
        self.assertEqual((view['phase'], view['captured'], view['retake_used'], view['retake']),
                         ('review', 3, True, False))
        self.assertEqual((view['copies'], view['session_count'], view['print_state']), (2, 1, 'NOT_SENT'))
        self.assertEqual(photo.session.retake_target_index, 1)
        target = photo.transaction.folder_path / intent['path']
        self.assertEqual(target.read_bytes(), saved_bytes)
        self.assertEqual(hashlib.sha256(saved_bytes).hexdigest(), intent['sha256'])
        self.assertEqual(photo.session.final_photo_paths,
                         [photo.session.initial_photo_paths[0], target, photo.session.initial_photo_paths[2]])
        current = json.loads(photo.transaction.manifest_path.read_text())
        record = current['sessions'][0]
        self.assertTrue(record['retake_used'])
        self.assertEqual(record['selected_photo'], record['raw_photos'][1]['path'])
        self.assertNotIn('pending_retake_index', record)
        self.assertEqual(len(record['raw_photos']), 4)
        self.assertEqual(sum(p['role'] == 'retake' for p in record['raw_photos']), 1)
        self.assertEqual(current['capture_intents'][intent['operation_id']]['state'], 'COMMITTED')
        self.assertEqual(current['upload_files'][intent['path']]['content_version'], intent['operation_id'])
        self.assertFalse((photo.transaction.folder_path / intent['temporary_path']).exists())
        self.assertEqual(list(photo.transaction.folder_path.rglob('*.png')), [])
        manifest = photo.transaction.manifest_path.read_bytes()
        with self.assertRaises(ValueError):
            photo.retake(0)
        # A fourth original/second retake is never initiated by this retry.
        with self.assertRaises(ValueError):
            photo.capture(np.full((24, 32, 3), 119, dtype=np.uint8))
        self.assertEqual(photo.transaction.manifest_path.read_bytes(), manifest)
        self.assertEqual(target.read_bytes(), saved_bytes)

    def restore_saved_retake(self, stage, code):
        root, ticket, binding, before, originals, attempt = self.crash(stage, code)
        folder = self.folder(root, binding)
        interrupted_manifest = (folder / 'manifest.json').read_bytes()
        manifest, intent = self.retake_record(folder)
        candidate = folder / (intent['path'] if (folder / intent['path']).exists() else intent['temporary_path'])
        saved_bytes = candidate.read_bytes()
        self.assertNotIn(saved_bytes, originals.values())
        for reopen in range(2):
            with closing(AllocationHarness(root)) as resumed, closing(PhotoTest(resumed.photo_root)) as photo:
                with self.forbidden_effects(resumed):
                    self.private_before_proof(resumed, photo, binding)
                    view = self.restore(resumed, photo, ticket, binding)
                self.assert_consumed(photo, view, intent, saved_bytes)
                self.original_identity(resumed, binding, before, originals, attempt, photo)
                current = photo.transaction.manifest_path.read_bytes()
                if stage == 'committed':
                    self.assertEqual(current, interrupted_manifest)
                if reopen == 0:
                    acknowledged = current
                else:
                    self.assertEqual(current, acknowledged)

    def test_cap12_staged_and_published_retake_exits_adopt_only_same_bytes_and_consume_quota_once(self):
        for stage, code in (('staged', 103), ('published', 104)):
            with self.subTest(stage=stage):
                self.restore_saved_retake(stage, code)

    def assert_held(self, root, ticket, binding, originals):
        folder = self.folder(root, binding)
        saved_files = self.file_bytes(folder)
        for _ in range(2):
            with closing(AllocationHarness(root)) as held, closing(PhotoTest(held.photo_root)) as photo, \
                    self.forbidden_effects(held):
                self.private_before_proof(held, photo, binding)
                held.flow.customer_claim(ticket)
                with self.assertRaises(CaptureRecoveryRequired):
                    photo.restore(get_templates(), binding, held.flow.resume_permit())
                self.assertIsNone(photo.transaction)
                self.assertNotIn('thumbnails', photo.snapshot())
                self.assertTrue(held.flow.active)
                self.assertEqual(held.store.get(binding['order_id'])['service_state'], 'STARTED')
                self.assertEqual(held.store.fulfillment(binding['order_id'], 'PB001')['obligation_state'], 'OWED')
                self.assertFalse(photo.store.state_path.exists())
                self.assertEqual(held.store.db.execute('SELECT next_sequence FROM checkout_allocation_counters').fetchone()[0], 2)
                self.assertEqual(self.file_bytes(folder), saved_files)
                for path, contents in originals.items():
                    self.assertEqual((folder / path).read_bytes(), contents)
                manifest, intent = self.retake_record(folder)
                self.assertFalse(manifest['sessions'][0]['retake_used'])
                self.assertEqual(len(manifest['sessions'][0]['raw_photos']), 3)
                self.assertEqual(manifest['sessions'][0]['pending_retake_index'], 1)

    def test_cap12_unhashed_temporary_retake_exit_holds_original_bytes_and_unconsumed_quota(self):
        root, ticket, binding, before, originals, attempt = self.crash('temporary', 102)
        self.assert_held(root, ticket, binding, originals)

    def test_cap12_tampered_staged_retake_is_held_without_overwrite_or_quota_commit(self):
        root, ticket, binding, before, originals, attempt = self.crash('staged', 103)
        folder = self.folder(root, binding)
        manifest, intent = self.retake_record(folder)
        temporary = folder / intent['temporary_path']
        temporary.write_bytes(temporary.read_bytes() + b'SYNTHETIC TAMPER')
        self.assert_held(root, ticket, binding, originals)

    def test_cap13_committed_retake_exit_preserves_original_selection_bytes_and_consumed_quota(self):
        self.restore_saved_retake('committed', 105)
