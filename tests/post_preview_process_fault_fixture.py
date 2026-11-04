"""Offline child process for hard exits at original print/isolation journals."""
import json
import os
from pathlib import Path
import sqlite3
import sys

import numpy as np

from photobooth.catalog import get_templates
from tests.post_preview_checkout_fixture import CheckoutFixture


def inspect(root, stage):
    db = sqlite3.connect(root / 'drafts.sqlite3')
    try:
        owed = db.execute('SELECT status FROM pp_paid_services').fetchone()[0]
        receipt = db.execute('SELECT receipt_state FROM pp_ticket_presentations').fetchone()[0]
        paid_attempts = db.execute(
            "SELECT count(*) FROM pp_payment_attempts WHERE payment_state='PAID'"
        ).fetchone()[0]
        jobs = db.execute('SELECT state, copies FROM pp_paid_strip_jobs').fetchall()
        if stage.startswith('isolation-'):
            operation = db.execute('''SELECT operation_id,original_generation,state,financial_class
                FROM pp_isolation_ops''').fetchone()
            original = db.execute('SELECT draft_id,generation,closed FROM pp_drafts').fetchone()
            # A new independent ledger, with no vault key/provider or original
            # worker, can inspect durability and test only local admission.
            from photobooth.post_preview_store import PostPreviewStore, DraftHeld
            ledger = PostPreviewStore(root/'drafts.sqlite3')
            try:
                try:
                    ledger.create('PB001', 'independent-visitorB', {'template_a': 1})
                    admitted = True
                except DraftHeld:
                    admitted = False
                print(json.dumps({'owed': owed, 'paid_attempts': paid_attempts,
                    'receipt': receipt, 'jobs': jobs, 'operation_id': operation[0],
                    'operation_generation': operation[1], 'operation_state': operation[2],
                    'financial_class': operation[3], 'original_generation': original[1],
                    'original_closed': original[2], 'new_local_admission': admitted,
                    'ack_events': db.execute("SELECT count(*) FROM pp_events WHERE event='ISOLATION_ACKED'").fetchone()[0]}))
            finally:
                ledger.close()
            return
        print(json.dumps({'owed': owed, 'receipt': receipt, 'paid_attempts': paid_attempts,
                          'jobs': jobs}))
    finally:
        db.close()


def crash_at(root, stage):
    fixture = CheckoutFixture(root)
    fixture.enable_paid_ticket()
    if stage == 'strip':
        fixture.enable_paid_delivery()
    service = fixture.service
    service.prepare()
    view = service.start(get_templates(), {'template_a': 2})
    frame = np.zeros((32, 48, 3), dtype=np.uint8)
    for _ in range(3):
        view = service.capture(frame, view['capture_slot'], view['revision'],
                               view['retake'], view['generation'])
    service.compose()
    view = service.next()
    view = service.freeze_checkout(view['revision'], view['amount'])
    service.ccp_visible(view['ccp_offer'])
    pay = service.begin_payment()
    order = pay['payment']['attempts'][0]['provider_order_id']
    fixture.provider.state(order, 'settlement')
    service.check_payment('connectivity')
    ticket = service.prepare_ticket()['ticket_offer']
    service.ticket_visible(ticket)

    def hard_exit(*_args, **_kwargs):
        # No Python cleanup, exception handler, fixture.close or ACK runs.
        # This is an abrupt OS process exit after durable SENDING is written.
        os._exit(73)

    if stage == 'receipt':
        service._receipt_printer.print_bitmap = hard_exit
        service.ticket_send_receipt()
    elif stage == 'strip':
        service.ticket_send_receipt()
        service.ticket_dismiss()
        service.prepare_paid_delivery()
        service._paid_printer.print_image = hard_exit
        service.paid_print_next()
    elif stage.startswith('isolation-'):
        from photobooth.post_preview_isolation import OriginalMockIsolation
        from photobooth.post_preview_store import DraftHeld
        service.ticket_send_receipt()
        service.ticket_dismiss()
        service.retire('APP_SUSPENDED')
        isolation = OriginalMockIsolation(service.ledger, fixture.backend, fixture.jobs,
            fixture.launch_lease, printer_lane=service._receipt_lane,
            allow_incomplete_fixture=True)
        operation = isolation.prepare('PB001')
        if stage == 'isolation-acked':
            isolation.acknowledge('PB001', operation)
        elif stage == 'isolation-worker-failed':
            service._receipt_lane.acquire()
            try:
                isolation.acknowledge('PB001', operation)
            except DraftHeld:
                pass
            else:
                raise AssertionError('Active worker must prevent ACK')
        elif stage == 'isolation-rollback':
            event = service.ledger._event
            def fail_archive(draft, name):
                if name == 'ISOLATION_ACKED':
                    raise OSError('Synthetic failure before ACK transaction commit')
                return event(draft, name)
            service.ledger._event = fail_archive
            try:
                isolation.acknowledge('PB001', operation)
            except OSError:
                pass
            else:
                raise AssertionError('Expected ACK transaction rollback')
        hard_exit()
    raise AssertionError('Expected the print callback to terminate this process')


if __name__ == '__main__':
    selected_root = Path(sys.argv[1])
    requested_stage = sys.argv[2]
    if requested_stage.startswith('inspect-'):
        inspect(selected_root, requested_stage[8:])
    elif requested_stage in {'receipt', 'strip', 'isolation-prepared',
                             'isolation-acked', 'isolation-worker-failed', 'isolation-rollback'}:
        crash_at(selected_root, requested_stage)
    else:
        raise SystemExit('Unsupported synthetic crash stage')
