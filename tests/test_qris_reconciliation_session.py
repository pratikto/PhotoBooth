"""AR-02 restart observation preserves private capture holds and identity."""
from contextlib import closing
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.qris_mock import MockQrisProvider
from photobooth.qris_session import KioskCheckout
from tests.test_qris_session import LocalClient


class ReconciliationClient(LocalClient):
    def __init__(self,backend):
        super().__init__(backend)
        self.observations=0
    def reconcile(self,oid, *, trigger='poll'):
        self.observations+=1
        return self.backend.reconcile(oid,'PB001', trigger=trigger)


class RestartReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.now=[1000.0]
        self.provider=MockQrisProvider(self.root/'provider.db',settle_after=5,now=lambda:self.now[0])
        self.addCleanup(self.provider.close)
        self.store=CheckoutStore(self.root/'orders.db',now=lambda:self.now[0])
        self.addCleanup(self.store.close)
        self.client=ReconciliationClient(CheckoutBackend(self.store,self.provider,'offline','MOCK'))

    def flow(self):
        return KioskCheckout(self.root/'visit.json',self.client,mode='mock',booth_id='PB001',endpoint='http://127.0.0.1:8765')

    def interrupted(self):
        with closing(self.flow()) as flow:
            flow.begin({'template_a':2});flow.refresh();self.now[0]+=6
            flow.refresh();flow.prepare_capture();flow.bind_transaction('PB001_00000001');flow.refresh()
            return flow.snapshot()

    def test_restart_checks_payment_once_but_never_resumes_camera_or_new_grant(self):
        old=self.interrupted()
        with closing(self.flow()) as flow:
            result=flow.refresh()
            self.assertEqual(self.client.observations,1)
            self.assertEqual(result['phase'],'RECOVERY')
            self.assertEqual(result['transaction_id'],old['transaction_id'])
            self.assertEqual(result['order']['grant_id'],old['order']['grant_id'])
            self.assertEqual(result['recovery']['interrupted_phase'],'STARTED')
            self.assertEqual(result['order']['reconciliation']['outcome'],'paid')
            for _ in range(5):flow.refresh()
            self.assertEqual(self.client.observations,1)
            with self.assertRaises(RuntimeError):flow.prepare_capture()

    def test_refund_and_unknown_provider_leave_private_hold_unchanged(self):
        self.interrupted()
        with closing(self.flow()) as flow:
            with patch.object(self.provider,'get_status',return_value={'status_code':'404'}):
                result=flow.refresh()
            self.assertEqual(result['phase'],'RECOVERY')
            self.assertTrue(result['order']['verification_pending'])
            self.assertEqual(result['order']['reconciliation']['outcome'],'provider_not_found_unproven')
            self.assertEqual(result['transaction_id'],'PB001_00000001')

    def test_legacy_recovery_without_original_phase_remains_unknown_and_held(self):
        self.interrupted()
        path=self.root/'visit.json';data=json.loads(path.read_text())
        data['phase']='RECOVERY';data.pop('recovery',None);path.write_text(json.dumps(data))
        with closing(self.flow()) as flow:
            result=flow.refresh()
            self.assertEqual(result['phase'],'RECOVERY')
            self.assertEqual(result.get('recovery',{}).get('interrupted_phase','UNKNOWN'),'UNKNOWN')

    def test_wrong_observed_order_cannot_replace_existing_journal(self):
        self.interrupted()
        with closing(self.flow()) as flow:
            before=flow.snapshot()
            result=dict(before['order'],order_id='another')
            with patch.object(self.client,'reconcile',return_value=result),self.assertRaises(ValueError):
                flow.refresh()
            self.assertEqual(flow.snapshot(),before)
