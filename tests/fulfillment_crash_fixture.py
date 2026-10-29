"""Disposable real HTTP/controller/SQLite allocation process-exit fixtures."""
from contextlib import ExitStack
import json
import os
from pathlib import Path
import sys

from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.qris_api import create_app
from photobooth.qris_kiosk_client import QrisKioskClient
from photobooth.qris_mock import MockQrisProvider
from photobooth.qris_session import KioskCheckout
from tests.qris_v2_fixture import InProcessSession


class AllocationHarness:
    def __init__(self, root):
        self.root = Path(root)
        self.photo_root = self.root / 'photo-test'
        self.cleanup = ExitStack()
        try:
            self.provider = MockQrisProvider(self.root / 'provider.sqlite',
                scenario='pending', settle_after=0, now=lambda: 1000.0)
            self.cleanup.callback(self.provider.close)
            self.store = CheckoutStore(self.root / 'orders.sqlite', now=lambda: 1000.0)
            self.cleanup.callback(self.store.close)
            self.backend = CheckoutBackend(self.store, self.provider, 'offline-fixture', 'MOCK')
            auth = BoothAuthenticator({'PB001': 'x' * 48})
            session = InProcessSession(create_app(self.backend, auth))
            self.client = QrisKioskClient('http://127.0.0.1:8765', 'PB001', 'x' * 48,
                allow_local_http=True, expected_mode='mock', session=session)
            self.cleanup.callback(self.client.close)
            self.flow = KioskCheckout(self.root / 'visit.json', self.client,
                mode='mock', booth_id='PB001', endpoint=self.client.base_url)
            self.cleanup.callback(self.flow.close)
        except BaseException:
            self.cleanup.close()
            raise

    def create_reserved(self):
        self.flow.begin({'template_a': 2})
        self.flow.refresh()
        ticket = self.flow.customer_ticket()
        oid = self.flow.snapshot()['order']['order_id']
        self.provider.db.execute("UPDATE mock_orders SET state='settlement' WHERE id=?", (oid,))
        self.flow.refresh()
        assert self.flow.snapshot()['phase'] == 'RESERVED' and ticket
        return ticket

    def forbid_new_charge(self):
        def forbidden(*_args):
            raise AssertionError('Recovery must not create another provider charge')
        self.provider.create_qris = forbidden
        self.client.create_order = forbidden

    def binding(self):
        order = self.flow.snapshot()['order']
        allocation = order['fulfillment']
        binding = {key: allocation[key] for key in ('fulfillment_id', 'transaction_id',
            'allocation_operation_id', 'contract_hash', 'booth_id', 'merchant_id')}
        return dict(binding, order_id=order['order_id'], grant_id=order['grant_id'])

    def close(self):
        self.cleanup.close()


def crash_allocation(root, boundary):
    harness = AllocationHarness(root)
    harness.forbid_new_charge()
    ticket = sys.stdin.read(201)  # Synthetic secret only in memory, never argv/file.
    harness.flow.customer_claim(ticket)
    oid = harness.flow.snapshot()['order']['order_id']
    if boundary == 'before_local_intent':
        original = harness.flow._save
        def before_save():
            if harness.flow.data['phase'] == 'STARTING':
                saved = json.loads(harness.flow.path.read_text())
                assert saved['phase'] == 'RESERVED' and not saved.get('allocation_operation_id')
                assert harness.store.fulfillment(oid, 'PB001')['transaction_id'] is None
                os._exit(81)
            return original()
        harness.flow._save = before_save
    elif boundary in {'before_backend_intent', 'allocated_reply_lost'}:
        original = harness.client.allocate
        def allocate(order_id, grant, operation):
            saved = json.loads(harness.flow.path.read_text())
            assert saved['phase'] == 'STARTING' and saved['allocation_operation_id'] == operation
            if boundary == 'before_backend_intent':
                assert harness.store.fulfillment(oid, 'PB001')['transaction_id'] is None
                os._exit(82)
            value = original(order_id, grant, operation)
            assert value['fulfillment']['transaction_id'] == harness.store.get(oid)['local_transaction_id']
            assert not harness.photo_root.exists()
            os._exit(83)
        harness.client.allocate = allocate
    elif boundary in {'folder_before_manifest', 'manifest_before_started', 'started_reply_lost'}:
        from photobooth.catalog import get_templates
        from photobooth.kiosk_v2.photos import PhotoTest
        harness.flow.prepare_capture()
        binding = harness.binding()
        photo = PhotoTest(harness.photo_root)
        if boundary == 'folder_before_manifest':
            def before_manifest(transaction):
                assert transaction.folder_path.is_dir() and not any(transaction.folder_path.iterdir())
                assert not transaction.manifest_path.exists()
                assert harness.store.get(oid)['service_state'] == 'RESERVED'
                os._exit(84)
            photo.store._write_manifest = before_manifest
        photo.start_bound(get_templates(), {'template_a': 2}, binding)
        assert photo.transaction.manifest_path.is_file()
        assert photo.transaction.manifest['payment_binding'] == binding
        if boundary == 'manifest_before_started':
            assert harness.store.get(oid)['service_state'] == 'RESERVED'
            assert harness.flow.snapshot()['allocation_ready'] is False
            os._exit(85)
        harness.flow.bind_transaction(binding['transaction_id'])
        original = harness.client.service_transition
        def after_started(order_id, grant, state, transaction_id, **options):
            value = original(order_id, grant, state, transaction_id, **options)
            assert state == 'STARTED' and value['service_state'] == 'STARTED'
            assert harness.store.get(oid)['service_state'] == 'STARTED'
            saved = json.loads(harness.flow.path.read_text())
            assert saved['phase'] == 'STARTING' and saved['order']['service_state'] == 'RESERVED'
            os._exit(86)
        harness.client.service_transition = after_started
        harness.flow.refresh()
        raise AssertionError('STARTED crash boundary was not reached')
    else:
        raise ValueError('Unknown allocation crash boundary')
    harness.flow.prepare_capture()
    raise AssertionError('Allocation crash boundary was not reached')


if __name__ == '__main__':
    crash_allocation(*sys.argv[1:])
