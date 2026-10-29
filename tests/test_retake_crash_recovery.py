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
        self.assertEqual(harness.store.fulfillment(binding['order_id'], 'PB001')['obligation_state'], 'OWED')
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
