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

    def prepare(self, root, kind):
        with closing(AllocationHarness(root)) as initial, closing(PhotoTest(initial.photo_root)) as photo:
            ticket = initial.create_reserved()
            initial.flow.prepare_capture()
            binding = initial.binding()
            before, originals = None, {}
            if kind != 'initial':
                photo.start_bound(get_templates(), {'template_a': 2}, binding)
                initial.flow.bind_transaction(binding['transaction_id'])
                initial.flow.refresh()
                for color in ((17,) if kind == 'capture' else (17, 83, 201)):
                    photo.capture(np.full((24, 32, 3), color, dtype=np.uint8))
                before = json.loads(photo.transaction.manifest_path.read_text())
                originals = {p.relative_to(photo.transaction.folder_path).as_posix(): p.read_bytes()
                             for p in photo.session.initial_photo_paths}
        return root, ticket, binding, before, originals

    def crash(self, kind, stage, number):
        root = self.root / (kind + '-' + stage + '-' + str(number))
        original = self.prepare(root, kind)
        root, ticket, binding, before, originals = original
        child = subprocess.run([sys.executable, '-m', 'tests.storage_fault_fixture', str(root), kind, stage, str(number)],
                               input=ticket, text=True, capture_output=True, timeout=30,
                               cwd=Path(__file__).resolve().parents[1])
        diagnostic = child.stderr.replace(ticket, '[REDACTED]').replace(ticket.split(':')[-1], '[REDACTED]')
        self.assertEqual(child.returncode, 120, diagnostic)
        self.assertEqual(json.loads((root / 'fault.json').read_text()),
                         {'kind': kind, 'stage': stage, 'errno': number, 'acknowledged': False})
        self.assertNotIn(ticket.split(':')[-1], (root / 'visit.json').read_text())
        return original

    def files(self, folder):
        return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}

    def no_effects(self, harness):
        harness.forbid_new_charge()
        stack = ExitStack()
        for name in ('capture', 'compose', 'print_result'):
            stack.enter_context(patch.object(PhotoTest, name, side_effect=AssertionError('No automatic media/delivery retry')))
        stack.enter_context(patch.object(harness.client, 'allocate', side_effect=AssertionError('No replacement allocation')))
        def transport_off(photo):
            # First-manifest restoration legitimately invokes this existing
            # hook; no delivery worker or transport may be installed.
            self.assertIsNone(photo.drive_worker)
            self.assertIsNone(photo.drive_client)
            self.assertIsNone(photo.printer)
        stack.enter_context(patch.object(PhotoTest, '_notify_delivery', new=transport_off))
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
        self.exercise('capture', stages)

    def exercise(self, kind, stages):
        for number in (errno.ENOSPC, errno.EACCES):
            for stage in stages:
                with self.subTest(errno=number, stage=stage):
                    root, ticket, binding, before, originals = self.crash(kind, stage, number)
                    folder = root / 'photo-test' / 'photos' / binding['transaction_id']
                    interrupted = json.loads((folder / 'manifest.json').read_text()) if kind != 'initial' else None
                    if interrupted is not None:
                        self.assertEqual(len(interrupted['sessions'][0]['raw_photos']), len(originals))
                        self.assertFalse(interrupted['sessions'][0]['retake_used'])
                        self.assertEqual(bool(interrupted['sessions'][0]['output_path']), stage == 'complete_manifest')
                    else:
                        self.assertEqual(self.files(folder), {})
                    saved_files = self.files(folder)
                    held = stage in {'image_write', 'image_fsync', 'staged_manifest'} or kind == 'output' and stage == 'image_open'
                    intents = ((interrupted or {}).get('output_intents', {}) if kind == 'output'
                               else (interrupted or {}).get('capture_intents', {}))
                    intent = list(intents.values())[-1] if intents else None
                    saved_frame = None
                    if stage in {'publish', 'commit_manifest', 'complete_manifest'}:
                        candidate = folder / (intent['path'] if (folder / intent['path']).exists() else intent['temporary_path'])
                        saved_frame = candidate.read_bytes()
                    for reopen in range(2):
                        with closing(AllocationHarness(root)) as resumed, closing(PhotoTest(resumed.photo_root)) as photo, \
                                self.no_effects(resumed):
                            self.assertEqual(resumed.store.get(binding['order_id'])['service_state'],
                                             'RESERVED' if kind == 'initial' and reopen == 0 else 'STARTED')
                            self.assertTrue(resumed.flow.customer_claim_required)
                            with self.assertRaises(RuntimeError):
                                resumed.flow.resume_permit()
                            with self.assertRaises(CaptureRecoveryRequired):
                                photo.restore(get_templates(), binding, None)
                            self.assertIsNone(photo.transaction)
                            self.assertNotIn('thumbnails', photo.snapshot())
                            resumed.flow.customer_claim(ticket)
                            permit = resumed.flow.resume_permit()
                            if held:
                                with self.assertRaises(CaptureRecoveryRequired):
                                    photo.restore(get_templates(), binding, permit)
                                self.assertIsNone(photo.transaction)
                                self.assertNotIn('thumbnails', photo.snapshot())
                                self.assertEqual(self.files(folder), saved_files)
                            else:
                                view = (photo.restore_allocated(get_templates(), {'template_a': 2}, binding, permit,
                                        resumed.flow.snapshot()['order']['service_state'])
                                        if kind == 'initial' and reopen == 0 else photo.restore(get_templates(), binding, permit))
                                if kind == 'capture':
                                    expected = ('capture', 2 if saved_frame is not None else 1, False, False)
                                elif kind == 'initial':
                                    expected = ('capture', 0, False, False)
                                elif kind == 'retake':
                                    expected = (('review', 3, True, False) if saved_frame is not None else
                                                ('review', 3, False, False) if stage == 'selection_manifest'
                                                else ('capture', 3, False, True))
                                else:
                                    expected = ('result' if saved_frame is not None else 'review', 3, False, False)
                                self.assertEqual((view['phase'], view['captured'], view['retake_used'], view['retake']), expected)
                                self.assertEqual((view['copies'], view['print_state']), (2, 'NOT_SENT'))
                                self.assertEqual(view['transaction_id'], binding['transaction_id'])
                                resumed.flow.confirm_resume(binding['transaction_id'], view['phase'])
                                current = json.loads((folder / 'manifest.json').read_text())
                                self.assertEqual(current['payment_binding'], binding)
                                self.assertEqual(current['sessions'][0]['retake_used'], view['retake_used'])
                                if before is not None:
                                    for key in ('created_at', 'local_retention_days', 'drive_retention_days',
                                                'drive_photos_expire_at', 'frozen_order', 'payment_binding'):
                                        self.assertEqual(current[key], before[key])
                                if saved_frame is not None:
                                    self.assertEqual((folder / intent['path']).read_bytes(), saved_frame)
                                    if kind == 'output':
                                        self.assertEqual(current['output_intents']['session_001']['state'], 'COMMITTED')
                                        self.assertEqual(current['output_intents']['session_001']['operation_id'], intent['operation_id'])
                                    else:
                                        self.assertEqual(current['capture_intents'][intent['operation_id']]['state'], 'COMMITTED')
                                        self.assertEqual(current['sessions'][0]['raw_photos'][-1]['operation_id'], intent['operation_id'])
                                    if kind == 'retake':
                                        self.assertEqual(photo.session.retake_target_index, 1)
                                        self.assertEqual(photo.session.final_photo_paths[1], folder / intent['path'])
                                elif stage == 'image_open' and kind != 'output':
                                    self.assertEqual(current['capture_intents'][intent['operation_id']]['state'], 'VOID_BEFORE_FRAME')
                                else:
                                    self.assertEqual(len(current['capture_intents']), len(originals))
                                if reopen == 0:
                                    repaired_files = self.files(folder)
                                else:
                                    self.assertEqual(self.files(folder), repaired_files)
                            for path, content in originals.items():
                                self.assertEqual((folder / path).read_bytes(), content)
                            self.assertFalse(photo.store.state_path.exists())
                            self.assert_financial(resumed, binding)

    def test_cap20_retake_selection_and_write_failures_never_false_commit_or_renew_quota(self):
        self.exercise('retake', ('selection_manifest', 'intent_manifest', 'image_open', 'image_write',
                                 'image_fsync', 'staged_manifest', 'publish', 'commit_manifest'))

    def test_cap20_output_write_and_final_status_failures_preserve_original_composition_or_hold(self):
        self.exercise('output', ('intent_manifest', 'image_open', 'image_write', 'image_fsync',
                                 'staged_manifest', 'publish', 'commit_manifest', 'complete_manifest'))

    def test_cap20_initial_manifest_fault_can_initialize_only_the_same_reserved_allocation(self):
        self.exercise('initial', ('initial_manifest',))

    def test_cap20_failed_issue_intent_write_keeps_preexisting_owed_before_reporting_recovers(self):
        import os
        for number in (errno.ENOSPC, errno.EACCES):
            with self.subTest(errno=number):
                root, ticket, binding, before, originals = self.prepare(self.root / ('issue-' + str(number)), 'capture')
                folder = root / 'photo-test' / 'photos' / binding['transaction_id']
                saved_files = self.files(folder)
                with closing(AllocationHarness(root)) as failed, self.no_effects(failed):
                    financial = failed.store.get(binding['order_id'])
                    journal = failed.flow.path.read_bytes()
                    original_replace = os.replace
                    fired = []
                    def replace(source, destination, *args, **options):
                        if Path(destination) == failed.flow.path:
                            fired.append(True)
                            raise OSError(number, 'Synthetic issue-intent write fault')
                        return original_replace(source, destination, *args, **options)
                    with patch('os.replace', side_effect=replace), \
                            patch.object(failed.client, 'report_fulfillment_issue', side_effect=AssertionError('No API before saved intent')):
                        with self.assertRaises(OSError) as error:
                            failed.flow.report_fulfillment_issue('CAPTURE_FAILED')
                        self.assertEqual(error.exception.errno, number)
                    self.assertEqual(fired, [True])
                    self.assertEqual(failed.flow.path.read_bytes(), journal)
                    self.assertEqual(failed.store.get(binding['order_id']), financial)
                    self.assertEqual(failed.store.fulfillment(binding['order_id'], 'PB001')['obligation_state'], 'OWED')
                    self.assertEqual(failed.store.db.execute('SELECT count(*) FROM checkout_fulfillment_issue_events').fetchone()[0], 0)
                with closing(AllocationHarness(root)) as recovered, self.no_effects(recovered):
                    self.assertTrue(recovered.flow.customer_claim_required)
                    recovered.flow.report_fulfillment_issue('CAPTURE_FAILED')
                    recovered.flow.report_fulfillment_issue('CAPTURE_FAILED')
                    self.assert_financial(recovered, binding)
                    self.assertEqual(self.files(folder), saved_files)

    def test_cap20_both_atomic_json_writers_preserve_absence_or_prior_bytes_on_create_write_fsync_faults(self):
        from photobooth.manifest_io import write_json_atomic
        from photobooth.transaction_store import TransactionStore
        for label, writer in (('manifest', write_json_atomic), ('transaction', TransactionStore._atomic_write_json)):
            for stage in ('temporary_create', 'partial_json_write', 'json_fsync'):
                for number in (errno.ENOSPC, errno.EACCES):
                    for exists in (False, True):
                        with self.subTest(writer=label, stage=stage, errno=number, prior=exists):
                            folder = self.root / f'atomic-{label}-{stage}-{number}-{exists}'
                            folder.mkdir()
                            path = folder / 'manifest.json'
                            prior = b'{"state":"PRIOR"}\n'
                            if exists:
                                path.write_bytes(prior)
                            fired = []
                            def fail(*args, **options):
                                fired.append(True)
                                raise OSError(number, 'Synthetic atomic JSON fault')
                            def partial(payload, stream, **options):
                                stream.write('{"state":')
                                fail()
                            target = {'temporary_create': 'tempfile.mkstemp', 'partial_json_write': 'json.dump',
                                      'json_fsync': 'os.fsync'}[stage]
                            with patch(target, side_effect=partial if stage == 'partial_json_write' else fail):
                                with self.assertRaises(OSError) as error:
                                    writer(path, {'state': 'NEW'})
                                self.assertEqual(error.exception.errno, number)
                            self.assertEqual(fired, [True])
                            self.assertEqual(path.exists(), exists)
                            if exists:
                                self.assertEqual(path.read_bytes(), prior)
                            self.assertEqual(set(folder.iterdir()), {path} if exists else set())
                            writer(path, {'state': 'NEW'})
                            self.assertEqual(json.loads(path.read_text()), {'state': 'NEW'})
                            self.assertEqual(set(folder.iterdir()), {path})
