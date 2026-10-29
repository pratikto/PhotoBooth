"""Synthetic payment/capture fixture shared by ledger and native tests."""
import hashlib
import json
from pathlib import Path
import numpy as np
from photobooth.catalog import get_templates
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.photos import PhotoTest
from tests.test_checkout_backend import FakeProvider,KEY,MERCHANT


class PaidPrintScenario:
    def __init__(self,root,*,quantities=None,reopen=False):
        self.root=Path(root);self.token='A'*43;self.operation='original-customer-claim'
        self.templates=get_templates();self.quantities=quantities or {'template_a':2}
        self.store=CheckoutStore(self.root/'orders.sqlite',now=lambda:1000)
        self.provider=FakeProvider();self.provider.mode='mock'
        self.backend=CheckoutBackend(self.store,self.provider,KEY,MERCHANT,delivery_policy='PRINT_REQUIRED_V1')
        self.photo_root=self.root/'photo'
        if reopen:
            data=json.loads((self.root/'fixture-state.json').read_text())
            self.provider.rows=data['provider_rows'];self.binding=data['binding'];return
        view=self.backend.create_order('PB001',self.quantities,'k'*32,
                                       customer_capability_hash=hashlib.sha256(self.token.encode()).hexdigest())
        oid=view['order_id'];self.provider.rows[oid].update(transaction_status='settlement',status_code='200')
        view=self.backend.customer_claim(oid,'PB001',self.token,self.operation)
        allocation=self.backend.allocate(oid,'PB001',view['grant_id'],'original-allocation')
        self.binding={k:allocation['fulfillment'][k] for k in ('fulfillment_id','transaction_id','allocation_operation_id','contract_hash','booth_id','merchant_id')}
        self.binding.update(order_id=oid,grant_id=allocation['grant_id'])
        self.photo=PhotoTest(self.photo_root)
        self.photo.start_bound(self.templates,self.quantities,self.binding)
        self.backend.service_transition(oid,'PB001',view['grant_id'],'STARTED',self.binding['transaction_id'])
        frame=np.zeros((80,120,3),dtype=np.uint8);frame[:,:60]=(0,0,255)
        for i in range(len(self.quantities)):
            for _ in range(3):self.photo.capture(frame)
            self.photo.compose()
            if i+1<len(self.quantities):self.photo.next()
        (self.root/'fixture-state.json').write_text(json.dumps({'provider_rows':self.provider.rows,'binding':self.binding}))

    def adapter(self,printer,**kwargs):
        from tests.paid_print_fixture import OfflinePaidPrint
        return OfflinePaidPrint(self.backend,self.binding,self.photo_root,self.templates,printer,
            self.token,self.operation,kwargs.pop('session_id','session_001'),**kwargs)

    @property
    def manifest(self):return self.photo_root/'photos'/self.binding['transaction_id']/'manifest.json'

    def close(self):
        if hasattr(self,'photo'):self.photo.close()
        self.store.close()
