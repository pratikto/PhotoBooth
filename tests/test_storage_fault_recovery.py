"""CAP-20 errno failures preserve durable photo ACKs and paid claims."""
from contextlib import closing, ExitStack
import errno
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


class StorageFaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def crash(self, kind, stage, number):
        root = self.root / (kind + '-' + stage + '-' + str(number))
        with closing(AllocationHarness(root)) as initial, closing(PhotoTest(initial.photo_root)) as photo:
            ticket = initial.create_reserved()
            initial.flow.prepare_capture()
            binding = initial.binding()
            photo.start_bound(get_templates(), {'template_a': 2}, binding)
            initial.flow.bind_transaction(binding['transaction_id'])
            initial.flow.refresh()
            photo.capture(np.full((24, 32, 3), 17, dtype=np.uint8))
            before = json.loads(photo.transaction.manifest_path.read_text())
            originals = {p.relative_to(photo.transaction.folder_path).as_posix(): p.read_bytes()
                         for p in photo.session.initial_photo_paths}
        child = subprocess.run([sys.executable, '-m', 'tests.storage_fault_fixture', str(root), kind, stage, str(number)],
                               input=ticket, text=True, capture_output=True, timeout=30,
                               cwd=Path(__file__).resolve().parents[1])
        diagnostic = child.stderr.replace(ticket, '[REDACTED]').replace(ticket.split(':')[-1], '[REDACTED]')
        self.assertEqual(child.returncode, 120, diagnostic)
        self.assertEqual(json.loads((root / 'fault.json').read_text()),
                         {'kind': kind, 'stage': stage, 'errno': number, 'acknowledged': False})
        self.assertNotIn(ticket.split(':')[-1], (root / 'visit.json').read_text())
        return root, ticket, binding, before, originals

    def files(self, folder):
        return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}

    def no_effects(self, harness):
        harness.forbid_new_charge()
        stack = ExitStack()
        for name in ('capture', 'compose', 'print_result', '_notify_delivery'):
            stack.enter_context(patch.object(PhotoTest, name, side_effect=AssertionError('No automatic media/delivery retry')))
        stack.enter_context(patch.object(harness.client, 'allocate', side_effect=AssertionError('No replacement allocation')))
        return stack

    def assert_financial(self, harness, binding):
        row = harness.store.get(binding['order_id'])
        self.assertEqual((row['state'], row['service_state'], row['grant_id'], row['local_transaction_id']),
                         ('PAID', 'STARTED', binding['grant_id'], binding['transaction_id']))
        fulfillment = harness.store.fulfillment(binding['order_id'], 'PB001')
        self.assertEqual((fulfillment['state'], fulfillment['obligation_state']), ('STARTED', 'OWED'))
        self.assertEqual(fulfillment['allocation_operation_id'], binding['allocation_operation_id'])
        self.assertEqual(harness.store.fulfillment_issue(binding['order_id'], 'PB001')['status'], 'PAID_UNFULFILLED')
        self.assertEqual(harness.store.db.execute('SELECT count(*) FROM checkout_fulfillment_issue_events').fetchone()[0], 1)
        self.assertEqual(harness.store.db.execute('SELECT count(*) FROM checkouts').fetchone()[0], 1)
        self.assertEqual(harness.provider.db.execute('SELECT count(*) FROM mock_orders').fetchone()[0], 1)
        self.assertEqual(harness.store.db.execute('SELECT next_sequence FROM checkout_allocation_counters').fetchone()[0], 2)
        self.assertEqual(harness.store.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(harness.provider.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(harness.store.db.execute('PRAGMA journal_mode').fetchone()[0], 'wal')
        self.assertEqual(harness.store.db.execute('PRAGMA synchronous').fetchone()[0], 2)
        self.assertFalse((harness.root / 'visits').exists())

    def test_cap20_capture_write_faults_preserve_saved_ack_and_owed_or_hold_unproven_bytes(self):
        stages = ('intent_manifest', 'image_open', 'image_write', 'image_fsync',
                  'staged_manifest', 'publish', 'commit_manifest')
        for number in (errno.ENOSPC, errno.EACCES):
            for stage in stages:
                with self.subTest(errno=number, stage=stage):
                    root, ticket, binding, before, originals = self.crash('capture', stage, number)
                    folder = root / 'photo-test' / 'photos' / binding['transaction_id']
                    interrupted = json.loads((folder / 'manifest.json').read_text())
                    self.assertEqual(len(interrupted['sessions'][0]['raw_photos']), 1)
                    self.assertFalse(interrupted['sessions'][0]['retake_used'])
                    saved_files = self.files(folder)
                    held = stage in {'image_write', 'image_fsync', 'staged_manifest'}
                    intent = list(interrupted['capture_intents'].values())[-1]
                    saved_frame = None
                    if stage in {'publish', 'commit_manifest'}:
                        candidate = folder / (intent['path'] if (folder / intent['path']).exists() else intent['temporary_path'])
                        saved_frame = candidate.read_bytes()
                    for reopen in range(2):
                        with closing(AllocationHarness(root)) as resumed, closing(PhotoTest(resumed.photo_root)) as photo, \
                                self.no_effects(resumed):
                            self.assertTrue(resumed.flow.customer_claim_required)
                            with self.assertRaises(RuntimeError):
                                resumed.flow.resume_permit()
                            with self.assertRaises(CaptureRecoveryRequired):
                                photo.restore(get_templates(), binding, None)
                            self.assertIsNone(photo.transaction)
                            resumed.flow.customer_claim(ticket)
                            permit = resumed.flow.resume_permit()
                            if held:
                                with self.assertRaises(CaptureRecoveryRequired):
                                    photo.restore(get_templates(), binding, permit)
                                self.assertIsNone(photo.transaction)
                                self.assertNotIn('thumbnails', photo.snapshot())
                                self.assertEqual(self.files(folder), saved_files)
                            else:
                                view = photo.restore(get_templates(), binding, permit)
                                expected = 2 if stage in {'publish', 'commit_manifest'} else 1
                                self.assertEqual((view['phase'], view['captured'], view['copies']), ('capture', expected, 2))
                                resumed.flow.confirm_resume(binding['transaction_id'], view['phase'])
                                current = json.loads((folder / 'manifest.json').read_text())
                                for key in ('created_at', 'local_retention_days', 'drive_retention_days',
                                            'drive_photos_expire_at', 'frozen_order', 'payment_binding'):
                                    self.assertEqual(current[key], before[key])
                                if saved_frame is not None:
                                    self.assertEqual((folder / intent['path']).read_bytes(), saved_frame)
                                    self.assertEqual(current['capture_intents'][intent['operation_id']]['state'], 'COMMITTED')
                                    self.assertEqual(current['sessions'][0]['raw_photos'][-1]['operation_id'], intent['operation_id'])
                                elif stage == 'image_open':
                                    self.assertEqual(current['capture_intents'][intent['operation_id']]['state'], 'VOID_BEFORE_FRAME')
                                else:
                                    self.assertEqual(len(current['capture_intents']), 1)
                                if reopen == 0:
                                    repaired_files = self.files(folder)
                                else:
                                    self.assertEqual(self.files(folder), repaired_files)
                            for path, content in originals.items():
                                self.assertEqual((folder / path).read_bytes(), content)
                            self.assertFalse(photo.store.state_path.exists())
                            self.assert_financial(resumed, binding)
