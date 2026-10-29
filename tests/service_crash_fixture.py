"""PAY-18 real process exits over the existing authenticated offline harness."""
import json
import os
from pathlib import Path
import sys

from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoTest
from tests.fulfillment_crash_fixture import AllocationHarness


def crash_service(root, boundary):
    harness = AllocationHarness(root)
    harness.forbid_new_charge()
    ticket = sys.stdin.read(201)  # Parent memory -> child memory, never argv/file.
    flow = harness.flow
    oid = flow.snapshot()['order']['order_id']
    if boundary == 'grant_reply_lost':
        # Exercise the original booth claim HTTP boundary independently of
        # restarted GUI ownership. It returns no private media/restore permit.
        observed = harness.client.reconcile(oid, trigger='restart')
        assert observed['state'] == 'PAID' and observed['grant_id'] is None
        value = harness.client.claim(oid, flow.snapshot()['checkout_key'])
        saved = json.loads(flow.path.read_text())
        assert saved['order']['grant_id'] is None
        assert value['grant_id'] == harness.store.get(oid)['grant_id']
        assert harness.store.get(oid)['service_state'] == 'RESERVED'
        os._exit(90)
    elif boundary == 'claim_reply_lost':
        original = harness.client.customer_claim
        def after_claim(order_id, capability, operation):
            value = original(order_id, capability, operation)
            saved = json.loads(flow.path.read_text())
            assert saved['customer_claim_operation_id'] == operation
            assert saved['order']['grant_id'] is None
            assert value['grant_id'] == harness.store.get(oid)['grant_id']
            assert value['customer_claim']['operation_id'] == operation
            assert harness.store.get(oid)['service_state'] == 'RESERVED'
            os._exit(91)
        harness.client.customer_claim = after_claim
        flow.customer_claim(ticket)
    elif boundary == 'started_reply_lost':
        flow.customer_claim(ticket)
        flow.prepare_capture()
        photo = PhotoTest(harness.photo_root)
        photo.start_bound(get_templates(), {'template_a': 2}, harness.binding())
        flow.bind_transaction(harness.binding()['transaction_id'])
        original = harness.client.service_transition
        def after_started(order_id, grant, state, transaction_id, **options):
            value = original(order_id, grant, state, transaction_id, **options)
            assert state == 'STARTED' and value['service_state'] == 'STARTED'
            assert harness.store.get(oid)['service_state'] == 'STARTED'
            saved = json.loads(flow.path.read_text())
            assert saved['phase'] == 'STARTING' and saved['order']['service_state'] == 'RESERVED'
            os._exit(92)
        harness.client.service_transition = after_started
        flow.refresh()
    elif boundary == 'completed_reply_lost':
        import numpy as np
        flow.customer_claim(ticket)
        photo = PhotoTest(harness.photo_root)
        restored = photo.restore(get_templates(), flow.resume_binding(), flow.resume_permit())
        assert restored['captured'] == 0 and restored['phase'] == 'capture'
        flow.confirm_resume(restored['transaction_id'], restored['phase'])
        for color in (17, 83, 201):
            photo.capture(np.full((24, 32, 3), color, dtype=np.uint8))
        result = photo.compose()
        assert result['phase'] == 'result'
        assert photo.transaction.manifest['output_intents']['session_001']['state'] == 'COMMITTED'
        flow.request_complete()
        original = harness.client.service_transition
        def after_completed(order_id, grant, state, transaction_id, **options):
            value = original(order_id, grant, state, transaction_id, **options)
            assert state == 'COMPLETED' and value['service_state'] == 'COMPLETED'
            assert harness.store.get(oid)['service_state'] == 'COMPLETED'
            assert harness.store.fulfillment(oid, 'PB001')['obligation_state'] == 'OWED'
            saved = json.loads(flow.path.read_text())
            assert saved['phase'] == 'COMPLETING' and saved['order']['service_state'] == 'STARTED'
            assert not (Path(root) / 'visits').exists()
            os._exit(93)
        harness.client.service_transition = after_completed
        flow.refresh()
    else:
        raise ValueError('Unknown service crash boundary')
    raise AssertionError('Service crash boundary was not reached')


if __name__ == '__main__':
    crash_service(*sys.argv[1:])
