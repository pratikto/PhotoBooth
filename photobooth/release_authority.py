"""Ephemeral local worker isolation receipt, never deserialized from a GUI flag."""
import time,uuid
_ISSUER=object()

class IsolationReceipt:
    def __init__(self,issuer,order_id,transaction_id,generation):
        if issuer is not _ISSUER:raise RuntimeError('Local photo worker receipt required')
        self.binding=(order_id,transaction_id,generation)
        self.isolation_id=uuid.uuid4().hex
        self.deadline=time.monotonic()+60
        self.used=False
    def consume(self,order_id,transaction_id,generation):
        if self.used or time.monotonic()>=self.deadline or self.binding!=(order_id,transaction_id,generation):
            raise RuntimeError('Current exact isolation receipt required')
        self.used=True

def trusted_isolation_receipt(order_id,transaction_id,generation):
    return IsolationReceipt(_ISSUER,order_id,transaction_id,generation)
