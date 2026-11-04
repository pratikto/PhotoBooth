"""Cross-feature customer journeys and fault injection against real local SQLite/API.

Every provider/Drive/printer here is a synthetic test fixture. These tests
deliberately exercise multiple components *per scenario*, not individual
pure functions, and must never use merchant credentials or external devices.
"""
import json
from dataclasses import replace
from pathlib import Path
import tempfile
import threading
import unittest
from types import SimpleNamespace

import numpy as np

from photobooth.catalog import get_templates
from photobooth.capture_journal import CaptureRecoveryRequired
from photobooth.post_preview_paid_print import OriginalPaidPrintDispatcher
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests.test_post_preview_pilot_admission import PilotAdmissionTests


class CustomerJourneyMatrixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = CheckoutFixture(Path(self.temp.name))
        self.addCleanup(self.fixture.close)
        self.service = self.fixture.service
        self.frame = np.zeros((32, 48, 3), dtype=np.uint8)

    def capture_all(self, quantities):
        """Actual per-template capture/compose/next, without camera hardware."""
        self.service.prepare()
        view = self.service.start(get_templates(), quantities)
        for _ in quantities:
            for _ in range(3):
                view = self.service.capture(
                    self.frame, view['capture_slot'], view['revision'],
                    view['retake'], view['generation'])
            self.service.compose()
            view = self.service.next()
        self.assertEqual('final_preview', view['phase'])
        return view

    def checkout(self, quantities=None):
        final = self.capture_all(quantities or {'template_a': 1})
        proof = self.service.freeze_checkout(final['revision'], final['amount'])
        self.assertEqual('claim_proof', proof['phase'])
        self.assertEqual(0, self.fixture.provider.charges)
        self.service.ccp_visible(proof['ccp_offer'])
        view = self.service.begin_payment()
        self.assertEqual('payment_pending', view['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        return view

    def paid(self, quantities=None):
        view = self.checkout(quantities)
        original = view['payment']['attempts'][0]['provider_order_id']
        self.fixture.provider.state(original, 'settlement')
        observed = self.service.check_payment('connectivity')
        self.assertEqual('paid_hold', observed['phase'])
        self.assertEqual('OWED', observed['payment']['obligation_state'])
        return observed

    def ticket(self, quantities=None):
        self.fixture.enable_paid_ticket()
        view = self.paid(quantities)
        ticket = self.service.prepare_ticket()
        self.service.ticket_visible(ticket['ticket_offer'])
        self.service.ticket_send_receipt()
        self.service.ticket_dismiss()
        self.assertEqual(1, len(self.fixture.receipt_sizes))
        return view

    def ready_to_print(self, quantities=None):
        self.fixture.enable_paid_ticket()
        self.fixture.enable_paid_delivery()
        self.paid(quantities)
        ticket = self.service.prepare_ticket()
        self.service.ticket_visible(ticket['ticket_offer'])
        self.service.ticket_send_receipt()
        self.service.ticket_dismiss()
        view = self.service.prepare_paid_delivery()
        self.assertEqual('paid_delivery', view['phase'])
        return view

    def jpeg_paths(self):
        return sorted(str(p) for p in self.service.root.rglob('*.jpg'))

    def test_j21_twelve_paid_visits_complete_without_folder_or_payment_contamination(self):
        """Bounded repeated complete visits, not a physical/time-based soak."""
        import hashlib
        from photobooth.post_preview_isolation import OriginalMockIsolation
        self.fixture.enable_paid_ticket()
        self.fixture.enable_paid_delivery()
        isolation=OriginalMockIsolation(
            self.service.ledger,self.fixture.backend,self.fixture.jobs,
            self.fixture.launch_lease,printer_lane=self.service._receipt_lane,
            delivery=self.fixture.paid_monitor,allow_incomplete_fixture=True)
        groups,folders,transactions,entitlements=set(),set(),set(),set()
        preserved={}
        for visit in range(12):
            self.frame.fill(visit*17)
            quantities={'template_a':visit%3+1,'template_b':1}
            final=self.capture_all(quantities)
            proof=self.service.freeze_checkout(final['revision'],final['amount'])
            self.service.ccp_visible(proof['ccp_offer'])
            pending=self.service.begin_payment()
            self.assertEqual('payment_pending',pending['phase'])
            order=pending['payment']['attempts'][0]['provider_order_id']
            self.fixture.provider.state(order,'settlement')
            paid=self.service.check_payment('connectivity')['payment']
            group=self.service.group
            self.assertNotIn(group,groups);groups.add(group)
            self.assertNotIn(paid['entitlement_id'],entitlements)
            entitlements.add(paid['entitlement_id'])
            offer=self.service.prepare_ticket()['ticket_offer']
            self.service.ticket_visible(offer)
            self.service.ticket_send_receipt()
            self.service.ticket_dismiss()
            delivery=self.service.prepare_paid_delivery()['delivery']
            self.assertNotIn(delivery['folder_url'],folders)
            folders.add(delivery['folder_url'])
            self.assertNotIn(delivery['transaction_id'],transactions)
            transactions.add(delivery['transaction_id'])
            for _ in range(2):self.service.paid_print_next()
            self.assertEqual([quantities['template_a'],1],
                             [x[1] for x in self.fixture.paid_print_sends[-2:]])
            self.assertEqual(2*(visit+1),len(self.fixture.paid_print_sends))
            self.assertEqual(visit+1,len(self.fixture.receipt_sizes))
            self.assertEqual(visit+1,self.fixture.provider.charges)
            for path,digest in preserved.items():
                self.assertEqual(digest,hashlib.sha256(path.read_bytes()).hexdigest())
            for path in self.service.photos.root.rglob('*.jpg'):
                preserved[path]=hashlib.sha256(path.read_bytes()).hexdigest()
            self.service.retire('APP_SUSPENDED')
            operation=isolation.prepare('PB001')
            self.assertTrue(isolation.acknowledge('PB001',operation))
            self.service.reset_after_acked_isolation(operation)
            self.assertEqual('confirm',self.service.phase)
        self.assertEqual(72,len(preserved))
        self.assertEqual(12,len(folders))
        self.assertEqual(12,self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_paid_services WHERE status='OWED'").fetchone()[0])
        self.assertEqual(12,self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_isolation_ops WHERE state='ACKED'").fetchone()[0])
        self.assertEqual(24,self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_paid_strip_jobs WHERE state='SUBMITTED'").fetchone()[0])
        self.assertEqual(0,self.service.ledger.db.execute(
            'SELECT count(*) FROM pp_drafts WHERE closed=0').fetchone()[0])

    def test_j01_all_twelve_designs_capture_36_originals_before_one_charge(self):
        quantities = {t.template_id: (i % 3) + 1 for i, t in enumerate(get_templates())}
        self.assertEqual(12, len(quantities))
        view = self.checkout(quantities)
        originals = self.jpeg_paths()
        self.assertEqual(36, len(originals))
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual('NONE', view['payment']['obligation_state'])
        contract = json.loads(self.service.ledger.db.execute(
            'SELECT contract_json FROM pp_checkout_intents').fetchone()[0])
        self.assertEqual(quantities, contract['quantities'])
        self.assertEqual(12, len(contract['designs']))
        for _ in range(3):
            observed = self.service.check_payment('connectivity')
            self.assertEqual('payment_pending', observed['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(originals, self.jpeg_paths())

    def test_j02_three_designs_copies_2_1_3_one_charge_three_exact_batches(self):
        view = self.ready_to_print({'template_a': 2, 'template_b': 1, 'template_c': 3})
        # Nine camera captures are intentionally imported into the separate
        # PAID delivery staging tree. Verify each category separately: this
        # is not 18 shutter activations and copies do not create sessions.
        staged = sorted(self.fixture.workspace.root.rglob('*.jpg'))
        camera_originals = sorted(
            p for p in self.service.root.rglob('*.jpg')
            if not p.is_relative_to(self.fixture.workspace.root))
        self.assertEqual(9, len(camera_originals))
        self.assertEqual(9, len(staged))
        self.assertEqual({'template_a': 'PREPARED', 'template_b': 'PREPARED',
                          'template_c': 'PREPARED'}, view['delivery']['print_states'])
        for _ in range(3):
            view = self.service.paid_print_next()
        self.assertEqual([2, 1, 3],
                         [copies for _path, copies in self.fixture.paid_print_sends])
        self.assertEqual(3, len(self.fixture.paid_print_sends))
        self.assertTrue(view['delivery']['print_all_submitted'])
        self.assertFalse(view['delivery']['physical_paper_verified'])
        self.service.paid_print_next()
        self.assertEqual(3, len(self.fixture.paid_print_sends))
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(1, len(self.fixture.receipt_sizes))
        self.assertEqual('OWED', view['delivery']['service_status'])

    def test_j03_paid_delivery_blocked_before_original_ticket_dismissal(self):
        self.fixture.enable_paid_ticket()
        self.fixture.enable_paid_delivery()
        self.paid({'template_a': 1, 'template_b': 2})
        with self.assertRaises(DraftHeld):
            self.service.prepare_paid_delivery()
        offer = self.service.prepare_ticket()['ticket_offer']
        with self.assertRaises(DraftHeld):
            self.service.prepare_paid_delivery()
        self.service.ticket_visible(offer)
        self.service.ticket_send_receipt()
        with self.assertRaises(DraftHeld):
            self.service.prepare_paid_delivery()
        self.service.ticket_dismiss()
        view = self.service.prepare_paid_delivery()
        self.assertEqual('paid_delivery', view['phase'])
        self.assertEqual(1, len(self.fixture.receipt_sizes))
        self.assertEqual(0, len(self.fixture.paid_print_sends))

    def test_j04_paid_drive_outage_then_same_transaction_recovers_without_new_charge(self):
        self.fixture.enable_paid_ticket()
        self.fixture.enable_paid_delivery()
        self.paid()
        ticket = self.service.prepare_ticket()['ticket_offer']
        self.service.ticket_visible(ticket)
        self.service.ticket_send_receipt()
        self.service.ticket_dismiss()
        original_binding = self.fixture.drive.bind_transaction
        def offline(_manifest):
            raise OSError('synthetic Drive offline')
        self.fixture.drive.bind_transaction = offline
        with self.assertRaises(DraftHeld):
            self.service.prepare_paid_delivery()
        original = self.service.ledger.db.execute(
            'SELECT transaction_id FROM pp_paid_services').fetchone()[0]
        self.assertIsNotNone(original)
        self.fixture.drive.bind_transaction = original_binding
        delivered = self.service.prepare_paid_delivery()
        self.assertEqual(original, delivered['delivery']['transaction_id'])
        self.assertEqual('paid_delivery', delivered['phase'])
        self.assertEqual('OWED', delivered['delivery']['service_status'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(1, len(self.fixture.receipt_sizes))

    def test_j05_malicious_drive_url_after_paid_never_releases_paid_print(self):
        self.fixture.enable_paid_ticket()
        self.fixture.enable_paid_delivery()
        self.paid()
        offer = self.service.prepare_ticket()['ticket_offer']
        self.service.ticket_visible(offer)
        self.service.ticket_send_receipt()
        self.service.ticket_dismiss()
        self.fixture.drive.bind_transaction = lambda manifest: {
            'transaction_id': manifest['transaction_id'],
            'folder_id': 'evilNotReal',
            'folder_url': 'https://untrusted.example/photos',
            'link_verified': True,
            'photo_number_layout': 1}
        with self.assertRaises(DraftHeld):
            self.service.prepare_paid_delivery()
        self.assertEqual([], self.fixture.paid_print_sends)
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual('OWED', self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_j06_corrupted_saved_source_after_paid_never_prints_different_image(self):
        self.fixture.enable_paid_ticket()
        self.fixture.enable_paid_delivery()
        self.paid()
        offer = self.service.prepare_ticket()['ticket_offer']
        self.service.ticket_visible(offer)
        self.service.ticket_send_receipt()
        self.service.ticket_dismiss()
        source = Path(self.jpeg_paths()[0])
        source.write_bytes(b'NOT A PHOTO: synthetic corruption')
        with self.assertRaises(CaptureRecoveryRequired):
            self.service.prepare_paid_delivery()
        self.assertEqual([], self.fixture.paid_print_sends)
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual('OWED', self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_j07_negative_printer_ack_quarantines_every_remaining_design(self):
        view = self.ready_to_print({'template_a': 2, 'template_b': 1})
        attempted = []
        def negative_ack(path, *, copies):
            attempted.append(copies)
            return SimpleNamespace(success=False)
        self.service._paid_printer.print_image = negative_ack
        view = self.service.paid_print_next()
        self.assertEqual([2], attempted)
        self.assertEqual({'template_a': 'UNCERTAIN', 'template_b': 'PREPARED'},
                         view['delivery']['print_states'])
        self.assertTrue(view['delivery']['needs_operator_review'])
        with self.assertRaises(DraftHeld):
            self.service.paid_print_next()
        self.assertEqual([2], attempted)
        self.assertEqual('OWED', view['delivery']['service_status'])

    def test_j08_second_batch_timeout_keeps_prior_submitted_job_immutable(self):
        self.ready_to_print({'template_a': 2, 'template_b': 3})
        first = self.service.paid_print_next()
        self.assertEqual('SUBMITTED', first['delivery']['print_states']['template_a'])
        attempts = []
        def lost_ack(_path, *, copies):
            attempts.append(copies)
            raise TimeoutError('synthetic printer stalled on second design')
        self.service._paid_printer.print_image = lost_ack
        state = self.service.paid_print_next()
        self.assertEqual([3], attempts)
        self.assertEqual({'template_a': 'SUBMITTED', 'template_b': 'UNCERTAIN'},
                         state['delivery']['print_states'])
        with self.assertRaises(DraftHeld):
            self.service.paid_print_next()
        self.assertEqual(1, len(self.fixture.paid_print_sends))
        self.assertEqual('OWED', state['delivery']['service_status'])

    def test_j09_new_dispatcher_cannot_bypass_uncertain_A_to_send_B(self):
        self.ready_to_print({'template_a': 2, 'template_b': 1})
        self.service._paid_printer.print_image = lambda _path, *, copies: (
            _ for _ in ()).throw(TimeoutError('synthetic first design unknown'))
        self.service.paid_print_next()
        # A second dispatcher has another in-process lock, but shares the
        # persisted original-purchase SQLite ledger.
        fresh = OriginalPaidPrintDispatcher(self.fixture.paid_dispatcher.preparer,
                                            allow_incomplete_fixture=True)
        other_printer = SimpleNamespace(print_image=lambda *_a, **_kw:
                                        (_ for _ in ()).throw(AssertionError('unsafe send')))
        with self.assertRaises(DraftHeld):
            fresh.send_once(self.service.lease, self.service.group, 'template_b',
                            other_printer, shared_lane=threading.Lock())
        states = self.fixture.paid_monitor.inspect(self.service.lease, self.service.group)
        self.assertEqual('UNCERTAIN', states['print_states']['template_a'])
        self.assertEqual('PREPARED', states['print_states']['template_b'])
        self.assertEqual('OWED', states['service_status'])

    def test_j10_direct_dispatcher_honors_durable_sending_other_design(self):
        self.ready_to_print({'template_a': 1, 'template_b': 1})
        with self.service.ledger.write():
            self.service.ledger.db.execute(
                "UPDATE pp_paid_strip_jobs SET state='SENDING' "
                "WHERE purchase_group_id=? AND template_id='template_a'",
                (self.service.group,))
        fresh = OriginalPaidPrintDispatcher(self.fixture.paid_dispatcher.preparer,
                                            allow_incomplete_fixture=True)
        attempts = []
        printer = SimpleNamespace(print_image=lambda *_a, **_kw: attempts.append(1))
        with self.assertRaises(DraftHeld):
            fresh.send_once(self.service.lease, self.service.group, 'template_b',
                            printer, shared_lane=threading.Lock())
        self.assertEqual([], attempts)
        status = self.fixture.paid_monitor.inspect(self.service.lease, self.service.group)
        self.assertEqual('SENDING', status['print_states']['template_a'])
        self.assertEqual('PREPARED', status['print_states']['template_b'])
        self.assertTrue(status['needs_operator_review'])

    def test_j11_uncertain_original_receipt_never_gets_resubmitted(self):
        self.fixture.enable_paid_ticket()
        self.paid()
        offer = self.service.prepare_ticket()['ticket_offer']
        self.service.ticket_visible(offer)
        calls = []
        def timeout(_bitmap, *, copies):
            calls.append(copies)
            raise TimeoutError('receipt may have physically printed')
        self.service._receipt_printer.print_bitmap = timeout
        sent = self.service.ticket_send_receipt()
        self.assertEqual('UNCERTAIN', sent['ticket_receipt']['receipt_state'])
        self.service.ticket_dismiss()
        with self.assertRaises(DraftHeld):
            self.service.prepare_ticket()
        self.assertEqual([1], calls)
        self.assertEqual('OWED', self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_j12_lost_http_response_and_repeated_poll_never_mint_new_charge(self):
        final = self.capture_all({'template_a': 1, 'template_b': 1})
        offered = self.service.freeze_checkout(final['revision'], final['amount'])
        self.service.ccp_visible(offered['ccp_offer'])
        self.fixture.session.lose_response = True
        held = self.service.begin_payment()
        self.assertEqual('payment_hold', held['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual('payment_pending', self.service.check_payment('restart')['phase'])
        original = self.service.snapshot()['payment']['attempts'][0]['provider_order_id']
        for _ in range(10):
            self.service.check_payment('connectivity')
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(original, self.service.snapshot()['payment']['attempts'][0]['provider_order_id'])
        self.assertEqual(6, len(self.jpeg_paths()))

    def test_j13_full_three_renewals_all_settle_late_only_one_entitlement(self):
        original = self.checkout()
        orders = []
        for ordinal in (1, 2, 3):
            order = self.service.snapshot()['payment']['attempts'][-1]['provider_order_id']
            orders.append(order)
            if ordinal < 3:
                self.fixture.provider.state(order, 'expire')
                status = self.service.check_payment('connectivity')
                self.assertEqual('EXPIRED_UNPAID', status['payment']['state'])
                self.service.continue_payment(True)
        self.assertEqual(3, self.fixture.provider.charges)
        self.fixture.provider.state(orders[0], 'settlement')
        observed = self.service.check_payment('connectivity')
        first_entitlement = observed['payment']['entitlement_id']
        self.assertIsNotNone(first_entitlement)
        for index in (1, 2):
            self.fixture.provider.state(orders[index], 'settlement')
            seen = self.service.check_payment('connectivity')
            self.assertEqual(first_entitlement, seen['payment']['entitlement_id'])
        self.assertEqual(2, len(seen['payment']['excess_paid_attempts']))
        self.assertEqual(1, self.service.ledger.db.execute(
            'SELECT count(*) FROM pp_purchase_finance WHERE entitlement_id IS NOT NULL'
        ).fetchone()[0])
        self.assertEqual(3, self.fixture.provider.charges)
        self.assertEqual(3, len(self.service.snapshot()['payment']['attempts']))

    def test_j14_paid_payment_poll_stress_cannot_change_entitlement_or_photos(self):
        original = self.paid({'template_a': 1, 'template_b': 2})
        token = original['payment']['entitlement_id']
        originals = self.jpeg_paths()
        for _ in range(25):
            seen = self.service.check_payment('connectivity')
            self.assertEqual(token, seen['payment']['entitlement_id'])
            self.assertEqual('OWED', seen['payment']['obligation_state'])
            self.assertNotIn('payment_qr', seen)
            self.assertFalse(seen['fulfillment_authorized'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(originals, self.jpeg_paths())

    def test_j15_storage_readiness_loss_after_capture_prevents_new_charge(self):
        from dataclasses import replace
        final = self.capture_all({'template_a': 2, 'template_b': 1})
        originals = self.jpeg_paths()
        self.fixture.ready = replace(self.fixture.ready, drive_sharing=False)
        with self.assertRaises(DraftHeld):
            self.service.freeze_checkout(final['revision'], final['amount'])
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertEqual(originals, self.jpeg_paths())
        self.fixture.ready = replace(self.fixture.ready, drive_sharing=True)
        proof = self.service.freeze_checkout(final['revision'], final['amount'])
        self.service.ccp_visible(proof['ccp_offer'])
        paid = self.service.begin_payment()
        self.assertEqual('payment_pending', paid['phase'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual(originals, self.jpeg_paths())

    def test_j16_invalid_capture_generation_does_not_advance_or_charge(self):
        self.service.prepare()
        view = self.service.start(get_templates(), {'template_a': 2})
        original_slot = view['capture_slot']
        with self.assertRaises(DraftHeld):
            self.service.capture(self.frame, original_slot, view['revision'],
                                 view['retake'], view['generation'] + 1)
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertEqual([], self.jpeg_paths())
        current = self.service.snapshot()
        self.assertEqual(original_slot, current['capture_slot'])
        for _ in range(3):
            view = self.service.capture(self.frame, view['capture_slot'],
                                        view['revision'], view['retake'], view['generation'])
        self.service.compose()
        self.service.next()
        self.assertEqual(3, len(self.jpeg_paths()))
        self.assertEqual(0, self.fixture.provider.charges)


class MultiVisitorJourneyMatrixTests(unittest.TestCase):
    # Reuse established source/fixture setup WITHOUT inheriting its test methods.
    setUp = PilotAdmissionTests.setUp
    final = PilotAdmissionTests.final
    freeze = PilotAdmissionTests.freeze
    ready = PilotAdmissionTests.ready
    paid_private_A = PilotAdmissionTests.paid_private_A

    def test_j17_A_paid_B_captures_A_waits_then_returns_without_new_payment(self):
        original, proof, group = self.paid_private_A()
        self.assertTrue(self.admission.ensure_new_visitor_ready())
        new = self.service.start(get_templates(), {'template_b': 1})
        other = self.service.lease
        self.assertNotEqual(original.draft_id, other.draft_id)
        view = self.service.snapshot()
        frame = self.frame
        self.service.capture(frame, view['capture_slot'], view['revision'],
                             view['retake'], view['generation'])
        waiting = self.admission.recover_paid(proof)
        self.assertEqual('WAIT', waiting['state'])
        self.assertEqual(other.draft_id, self.service.lease.draft_id)
        self.service.retire('APP_SUSPENDED')
        self.assertTrue(self.admission.ensure_new_visitor_ready())
        restored = self.admission.recover_paid(proof)
        self.assertEqual('RESTORED', restored['state'])
        self.assertEqual(original.draft_id, self.service.lease.draft_id)
        self.assertEqual('OWED', restored['snapshot']['payment']['obligation_state'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual('OWED', self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services WHERE purchase_group_id=?',
            (group,)).fetchone()[0])

    def test_j18_invalid_QR_roles_during_B_never_release_original_paid_A(self):
        original, proof, group = self.paid_private_A()
        self.admission.ensure_new_visitor_ready()
        self.service.start(get_templates(), {'template_b': 1})
        active_B = self.service.lease
        tokens = ['MEONG:PAYMENT:1:PB001:wrong',
                  'MEONG:DEMO:1:PB001:wrong',
                  'MEONG:OPERATOR:1:PB001:wrong',
                  'MEONG:RECOVERY:1:PB002:' + 'a'*32 + ':' + 'a'*43,
                  '', 'invalid', 'x'*300]
        for code in tokens:
            with self.subTest(kind=code[:18]):
                with self.assertRaises(PermissionError):
                    self.admission.recover_paid(code)
                self.assertEqual(active_B.draft_id, self.service.lease.draft_id)
        self.assertEqual('WAIT', self.admission.recover_paid(proof)['state'])
        self.assertEqual(1, self.fixture.provider.charges)
        self.assertEqual('OWED', self.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services WHERE purchase_group_id=?',
            (group,)).fetchone()[0])

    def test_j19_stalled_worker_blocks_B_and_A_without_consuming_original_proof(self):
        original, proof, group = self.paid_private_A()
        self.fixture.jobs.busy = True
        with self.assertRaises(DraftHeld):
            self.admission.ensure_new_visitor_ready()
        self.assertEqual('WAIT', self.admission.recover_paid(proof)['state'])
        self.assertEqual(original.draft_id, self.service.lease.draft_id)
        self.assertEqual(0, self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_isolation_ops WHERE state='ACKED'").fetchone()[0])
        self.fixture.jobs.busy = False
        result = self.admission.recover_paid(proof)
        self.assertEqual('RESTORED', result['state'])
        self.assertEqual(1, self.fixture.provider.charges)

    def test_j20_twelve_rapid_protected_visits_do_not_share_draft_or_charge(self):
        self.service.prepare()
        unique = set()
        for _ in range(12):
            view = self.service.start(get_templates(), {'template_a': 1})
            original = self.service.lease.draft_id
            self.assertNotIn(original, unique)
            unique.add(original)
            self.assertEqual(0, self.fixture.provider.charges)
            self.service.retire('APP_SUSPENDED')
            self.assertTrue(self.admission.ensure_new_visitor_ready())
            self.assertIsNone(self.service.lease)
        self.assertEqual(12, len(unique))
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertEqual(12, self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_drafts WHERE lifecycle='ISOLATED' AND closed=1"
        ).fetchone()[0])
        self.assertEqual(12, self.service.ledger.db.execute(
            "SELECT count(*) FROM pp_isolation_ops WHERE state='ACKED'"
        ).fetchone()[0])


if __name__ == '__main__':
    unittest.main()
