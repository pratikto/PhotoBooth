"""Original paid print dispatch uses a single immutable copy-batched transport."""
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock

from photobooth.booth_storage import BoothWorkspace
from photobooth.post_preview_paid_print import OriginalPaidPrintDispatcher
from tests.test_post_preview_paid_strips import OriginalPaidStripTests


class OriginalPaidPrintTests(unittest.TestCase):
    prepared=OriginalPaidStripTests.prepared
    paid_fixture=OriginalPaidStripTests.paid_fixture
    binder=OriginalPaidStripTests.binder

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.workspace=BoothWorkspace(self.root,'PB001V2S2')
        self.workspace.prepare()

    def paid_ticket(self,fixture):
        view=fixture.service.prepare_ticket()
        offer=view['ticket_offer']
        fixture.service.ticket_visible(offer)
        receipt=fixture.service.ticket_send_receipt()
        self.assertEqual('SUBMITTED',receipt['ticket_receipt']['receipt_state'])
        fixture.service.ticket_dismiss()

    def prepped(self):
        fixture,preparer=self.prepared()
        prepared=preparer.prepare(fixture.service.lease,fixture.service.group,fixture.service.templates)
        dispatcher=OriginalPaidPrintDispatcher(preparer,allow_incomplete_fixture=True)
        return fixture,dispatcher,prepared

    def test_no_ticket_dismissal_means_no_paid_photo_bytes_sent(self):
        fixture,dispatcher,prepared=self.prepped()
        printer=Mock()
        with self.assertRaises(Exception):
            dispatcher.send_once(fixture.service.lease,fixture.service.group,
                                 'template_a',printer,shared_lane=threading.Lock())
        printer.print_image.assert_not_called()
        self.assertEqual('PREPARED',fixture.service.ledger.db.execute(
            'SELECT state FROM pp_paid_strip_jobs').fetchone()[0])

    def test_one_original_batch_only_and_paid_owed_stays(self):
        fixture,dispatcher,prepared=self.prepped()
        self.paid_ticket(fixture)
        printer=Mock()
        printer.print_image.return_value=Mock(success=True)
        response=dispatcher.send_once(fixture.service.lease,fixture.service.group,
                                       'template_a',printer,shared_lane=threading.Lock())
        self.assertEqual('SUBMITTED',response['state'])
        self.assertFalse(response['physical_paper_verified'])
        printer.print_image.assert_called_once()
        _,kw=printer.print_image.call_args
        self.assertEqual({'copies':1},kw)
        self.assertEqual('OWED',fixture.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])
        with self.assertRaises(Exception):
            dispatcher.send_once(fixture.service.lease,fixture.service.group,
                                 'template_a',printer,shared_lane=threading.Lock())
        printer.print_image.assert_called_once()

    def test_uncertain_original_receipt_blocks_even_direct_paid_strip_dispatch(self):
        from photobooth.post_preview_store import DraftHeld
        fixture,dispatcher,_=self.prepped()
        offer=fixture.service.prepare_ticket()['ticket_offer']
        fixture.service.ticket_visible(offer)
        fixture.service._receipt_printer.print_bitmap=lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError('Synthetic receipt response loss'))
        view=fixture.service.ticket_send_receipt()
        self.assertEqual('UNCERTAIN',view['ticket_receipt']['receipt_state'])
        fixture.service.ticket_dismiss()
        from photobooth.post_preview_paid_delivery import OriginalPaidDeliveryMonitor
        monitor=OriginalPaidDeliveryMonitor(dispatcher.preparer,allow_incomplete_fixture=True)
        self.assertTrue(monitor.inspect(fixture.service.lease,fixture.service.group)['needs_operator_review'])
        printer=Mock()
        with self.assertRaises(DraftHeld):
            dispatcher.send_once(fixture.service.lease,fixture.service.group,
                                 'template_a',printer,shared_lane=threading.Lock())
        printer.print_image.assert_not_called()
        self.assertEqual('PREPARED',fixture.service.ledger.db.execute(
            'SELECT state FROM pp_paid_strip_jobs').fetchone()[0])
        self.assertEqual('OWED',fixture.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_unknown_print_outcome_is_never_replayed(self):
        fixture,dispatcher,_=self.prepped()
        self.paid_ticket(fixture)
        printer=Mock()
        printer.print_image.side_effect=TimeoutError('synthetic uncertain send')
        result=dispatcher.send_once(fixture.service.lease,fixture.service.group,
                                    'template_a',printer,shared_lane=threading.Lock())
        self.assertEqual('UNCERTAIN',result['state'])
        with self.assertRaises(Exception):
            dispatcher.send_once(fixture.service.lease,fixture.service.group,
                                 'template_a',printer,shared_lane=threading.Lock())
        self.assertEqual(1,printer.print_image.call_count)

    def test_persisted_sending_after_worker_crash_blocks_new_dispatcher_replay(self):
        """Crash seam: SENDING was durable before external printer side effects."""
        from photobooth.post_preview_store import DraftHeld
        fixture, dispatcher, _ = self.prepped()
        self.paid_ticket(fixture)
        # Represent a process dying after the irreversible SENDING journal
        # transaction commits but before any trusted transport ACK arrives.
        with fixture.service.ledger.write():
            fixture.service.ledger.db.execute(
                "UPDATE pp_paid_strip_jobs SET state='SENDING' "
                "WHERE purchase_group_id=? AND template_id='template_a'",
                (fixture.service.group,))
        restarted = OriginalPaidPrintDispatcher(
            dispatcher.preparer, allow_incomplete_fixture=True)
        printer = Mock()
        with self.assertRaises(DraftHeld):
            restarted.send_once(
                fixture.service.lease, fixture.service.group, 'template_a',
                printer, shared_lane=threading.Lock())
        printer.print_image.assert_not_called()
        state = fixture.service.ledger.db.execute(
            "SELECT state FROM pp_paid_strip_jobs WHERE template_id='template_a'"
        ).fetchone()[0]
        self.assertEqual('SENDING', state)
        self.assertEqual('OWED', fixture.service.ledger.db.execute(
            'SELECT status FROM pp_paid_services').fetchone()[0])

    def test_missing_printer_is_not_sent_and_never_fabricates_paper(self):
        fixture,dispatcher,_=self.prepped()
        self.paid_ticket(fixture)
        result=dispatcher.send_once(fixture.service.lease,fixture.service.group,
                                    'template_a',None,shared_lane=threading.Lock())
        self.assertEqual('NOT_SENT',result['state'])
        self.assertFalse(result['physical_paper_verified'])

    def test_corrupt_saved_original_strip_cannot_be_printed(self):
        fixture,dispatcher,prepared=self.prepped()
        self.paid_ticket(fixture)
        Path(prepared['jobs'][0]['output_path']).write_bytes(b'CORRUPT')
        printer=Mock()
        with self.assertRaises(Exception):
            dispatcher.send_once(fixture.service.lease,fixture.service.group,
                                 'template_a',printer,shared_lane=threading.Lock())
        printer.print_image.assert_not_called()
        self.assertEqual('PREPARED',fixture.service.ledger.db.execute(
            'SELECT state FROM pp_paid_strip_jobs').fetchone()[0])


if __name__=='__main__':unittest.main()
