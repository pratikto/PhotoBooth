"""Offline integration host; never imported by an application entrypoint."""
import time
from photobooth.checkout_store import CheckoutConflict, identifier
from photobooth.device_health import READY
from photobooth.kiosk_v2.recovery_readiness import prepayment_readiness


class OfflinePrintPurchase:
    def __init__(self, backend, root, templates, booth_id, printer_config, *, printer_probe, now=time.monotonic):
        if backend.provider_mode != 'mock' or backend.delivery_policy != 'PRINT_REQUIRED_V1':
            raise ValueError('Explicit mock print fixture required')
        identifier(booth_id)
        self.backend,self.root,self.templates=backend,root,templates
        self.booth_id,self.config=booth_id,printer_config
        self.probe,self.now=printer_probe,now

    def begin(self, quantities, key, camera_valid, observed_at, *, capability_hash=None):
        store=self.backend.store
        with store.lock:
            old=store.db.execute('SELECT id FROM checkouts WHERE booth_id=? AND checkout_key=?',(self.booth_id,key)).fetchone()
            active=store.db.execute("SELECT id FROM checkouts WHERE booth_id=? AND closed=0 AND state NOT IN ('EXPIRED','CANCELLED','FAILED') AND service_state!='COMPLETED'",(self.booth_id,)).fetchone()
        if old is None:
            if active is not None:
                raise CheckoutConflict('Original checkout key required')
            try:
                prepayment_readiness(self.root,self.templates,quantities,camera_valid,observed_at,now=self.now)
                if self.probe(self.config).status != READY or not 0 <= self.now()-observed_at <= 2:
                    raise RuntimeError('Printer observation not ready')
            except Exception:
                raise RuntimeError('Purchase readiness requires attention') from None
        return self.backend.create_order(self.booth_id,quantities,key,customer_capability_hash=capability_hash)
