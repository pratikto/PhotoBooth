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
    elif boundary in {'completed_reply_lost', 'composed_before_completion_intent',
                      'completion_intent_before_request'}:
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
        if boundary in {'composed_before_completion_intent', 'completion_intent_before_request'}:
            def no_complete_request(*_args, **_options):
                raise AssertionError('CAP-16 must exit before any COMPLETE request')
            harness.client.service_transition = no_complete_request
            assert harness.store.get(oid)['service_state'] == 'STARTED'
            assert harness.store.fulfillment(oid, 'PB001')['obligation_state'] == 'OWED'
            assert not (Path(root) / 'visits').exists()
            if boundary == 'composed_before_completion_intent':
                assert json.loads(flow.path.read_text())['phase'] == 'STARTED'
                os._exit(106)
            flow.request_complete()
            assert json.loads(flow.path.read_text())['phase'] == 'COMPLETING'
            assert harness.store.get(oid)['service_state'] == 'STARTED'
            os._exit(107)
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
    elif boundary in {'completed_ack_before_archive', 'archive_operation_before_index',
                      'archive_index_before_final_journal'}:
        from unittest.mock import patch
        import photobooth.qris_session as session_module
        def forbidden(*_args, **_options):
            raise AssertionError('Archive recovery cannot repeat media or delivery effects')
        for method in ('capture', 'compose', 'print_result', '_notify_delivery'):
            setattr(PhotoTest, method, forbidden)
        flow.customer_claim(ticket)
        photo = PhotoTest(harness.photo_root)
        view = photo.restore(get_templates(), flow.resume_binding(), flow.resume_permit())
        assert view['phase'] == 'result' and view['captured'] == 3
        flow.confirm_resume(view['transaction_id'], view['phase'])
        flow.request_complete()
        key = flow.snapshot()['checkout_key']
        directory = Path(root) / 'visits'
        operation_path = directory / key / 'completed.json'
        index_path = directory / (key + '.json')
        def assert_ack():
            saved = json.loads(flow.path.read_text())
            assert saved['phase'] == 'COMPLETING'
            assert saved['order']['service_state'] == 'COMPLETED'
            assert harness.store.get(oid)['service_state'] == 'COMPLETED'
        if boundary == 'completed_ack_before_archive':
            def before_archive(snapshot, operation):
                assert_ack()
                assert snapshot['phase'] == 'COMPLETED' and operation == 'completed'
                assert not operation_path.exists() and not index_path.exists()
                os._exit(94)
            flow._archive_snapshot = before_archive
            flow.refresh()
        elif boundary == 'archive_operation_before_index':
            original = session_module.write_json_atomic
            def before_index(path, payload):
                if Path(path) == index_path:
                    assert_ack()
                    assert json.loads(operation_path.read_text()) == payload
                    assert not index_path.exists()
                    os._exit(95)
                return original(path, payload)
            with patch.object(session_module, 'write_json_atomic', side_effect=before_index):
                flow.refresh()
        else:
            original = flow._save
            def before_final_save():
                if flow.data['phase'] == 'COMPLETED':
                    assert_ack()
                    assert json.loads(operation_path.read_text()) == flow.snapshot()
                    assert json.loads(index_path.read_text()) == flow.snapshot()
                    os._exit(96)
                return original()
            flow._save = before_final_save
            flow.refresh()
    else:
        raise ValueError('Unknown service crash boundary')
    raise AssertionError('Service crash boundary was not reached')


if __name__ == '__main__':
    crash_service(*sys.argv[1:])
