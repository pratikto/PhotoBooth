"""Private mock wire to original release-store protocol; never a mounted API.

Mock paid printing and Sandbox HTTP release are intentionally separate domains.
This fixture joins the original controller to the existing store protocol after
fresh mock reconciliation, without relaxing the real HTTP Sandbox-only guard.
"""
from photobooth import checkout_release


class MockReleaseWire:
    def __init__(self, client, backend):
        if backend.provider_mode != 'mock' or backend.delivery_policy != 'PRINT_REQUIRED_V1':
            raise ValueError('Only the explicit isolated paid-print fixture is supported')
        self.client,self.backend=client,backend

    def __getattr__(self,name):return getattr(self.client,name)

    def release(self,order_id,pin,operation_id,*,isolation_id=None):
        if pin!='12345678':raise PermissionError('Synthetic operator proof required')
        order,provider_state=self.backend._fresh_payment(order_id,'PB001')
        if order['state']!='PAID' or provider_state!='settlement':
            raise RuntimeError('Fresh original settlement required')
        if isolation_id is None:
            checkout_release.prepare(self.backend.store,order_id,'PB001',operation_id,'isolated-test-wire')
        else:
            checkout_release.acknowledge(self.backend.store,order_id,'PB001',operation_id,isolation_id)
        return self.backend.view(self.backend.store.get(order_id,'PB001'))
