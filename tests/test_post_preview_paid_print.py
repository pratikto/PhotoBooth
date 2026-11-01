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
