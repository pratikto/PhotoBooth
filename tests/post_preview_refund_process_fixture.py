"""Hard-exit mock refund probe; no restored customer key or device transport."""
import json
import os
from pathlib import Path
import sys
import threading

import numpy as np

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.post_preview_photos import PrivatePhotoService
from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_isolation import OriginalMockIsolation
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_refund_assessment import OriginalRefundEvidence, VerifiedPaidAttempt
from photobooth.post_preview_refund_simulation import MockRefundCoordinator, SimulatedRefundProvider
from photobooth.post_preview_store import PostPreviewStore
from tests.post_preview_checkout_fixture import CheckoutFixture
from tests.test_post_preview_payments import SyntheticProvider


def run(root, action, checkpoint):
    if action == 'produce':
        f = CheckoutFixture(root/'booth')
        f.enable_paid_ticket()
        s = f.service
        s.prepare()
        view = s.start(get_templates(), {'template_a': 1})
        for _ in range(3):
            view = s.capture(np.zeros((32, 48, 3), dtype=np.uint8), view['capture_slot'],
                             view['revision'], view['retake'], view['generation'])
        s.compose()
        view = s.next()
        view = s.freeze_checkout(view['revision'], view['amount'])
        s.ccp_visible(view['ccp_offer'])
        view = s.begin_payment()
        f.provider.state(view['payment']['attempts'][0]['provider_order_id'], 'settlement')
        s.check_payment('connectivity')
        s.prepare_ticket()
        group = s.group
        # Independent synthetic payment-server snapshot, never derived from
        # local PAID rows in the consumer. No proof/key/secret is written.
        with (root/'synthetic-payment-server.json').open('x') as stream:
            json.dump(f.provider.rows, stream)
        s.retire('APP_SUSPENDED')
        iso = OriginalMockIsolation(s.ledger, f.backend, f.jobs, f.launch_lease,
            printer_lane=s._receipt_lane, allow_incomplete_fixture=True)
        op = iso.prepare('PB001')
        iso.acknowledge('PB001', op)
        provider = SimulatedRefundProvider(root/'synthetic-refund-server.sqlite3', simulation=True)
        c = MockRefundCoordinator(f.backend, provider, isolation=iso, simulation=True)
        finance = s.ledger.db.execute('SELECT * FROM pp_purchase_finance').fetchone()
        paid = s.ledger.db.execute('SELECT * FROM pp_payment_attempts').fetchone()
        evidence = OriginalRefundEvidence(group, 'MTEST', finance['amount'],
            VerifiedPaidAttempt(paid['attempt_id'], paid['provider_ref'], 'MTEST', finance['amount'], True),
            reason='IRRECOVERABLE_MERCHANT_SERVICE', service_irrecoverable=True,
            financial_integrity_verified=True, all_external_workers_fenced=True,
            merchant_refund_feature_verified=True, approved_commercial_policy=True, approved_abuse_limit=True)
        intent = c.prepare(evidence, 'PB001')
        print(json.dumps({'intent': intent, 'group': group}), flush=True)
        if checkpoint == 'PREPARED':
            os._exit(73)
        def crash(boundary):
            if boundary == checkpoint:
                os._exit(73)
        c.submit(intent, group, 'PB001', checkpoint=crash)
        raise AssertionError('Hard-exit boundary was not reached')

    context = json.loads(sys.stdin.read())
    ledger = PostPreviewStore(root/'booth'/'drafts.sqlite3')
    service = PrivatePhotoService(root/'booth', trusted_ledger=ledger)
    jobs = PhotoJobs(service)
    launch = LaunchLease(root/'booth')
    payment_provider = SyntheticProvider()
    payment_provider.rows = json.loads((root/'synthetic-payment-server.json').read_text())
    payments = PostPreviewPayments(ledger, payment_provider, 'MTEST', readiness=lambda _: None, poll_seconds=0)
    provider = SimulatedRefundProvider(root/'synthetic-refund-server.sqlite3', simulation=True)
    iso = OriginalMockIsolation(ledger, payments, jobs, launch, printer_lane=threading.Lock(),
                                allow_incomplete_fixture=True)
    c = MockRefundCoordinator(payments, provider, isolation=iso, simulation=True)
    try:
        for _ in range(3):
            status = c.submit(context['intent'], context['group'], 'PB001')
        rows = list(provider.db.execute('SELECT * FROM simulated_refunds'))
        print(json.dumps(dict(status, provider_requests=sum(row['requests'] for row in rows),
            provider_rows=len(rows), new_charges=payment_provider.charges,
            owed=ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0],
            payment=ledger.db.execute('SELECT payment_state FROM pp_payment_attempts').fetchone()[0],
            intents=ledger.db.execute('SELECT count(*) FROM pp_mock_refund_intents').fetchone()[0],
            active=ledger.db.execute('SELECT count(*) FROM pp_drafts WHERE closed=0').fetchone()[0])))
    finally:
        provider.close()
        jobs.close()
        service.close()
        service.wait_closed(10)
        launch.close()


if __name__ == '__main__':
    run(Path(sys.argv[1]), sys.argv[2], sys.argv[3])
