"""Mock-only fixture host reusing actual paid/photo/print code; no entrypoint."""
import hashlib
import json
import threading
from types import SimpleNamespace

from photobooth.checkout_store import CheckoutConflict
from photobooth.kiosk_v2.photo_recovery import reconstruct
from photobooth.kiosk_v2.photos import PhotoTest
from photobooth.qris_session import KioskLease
from photobooth.resume_authority import trusted_resume_permit


class OfflinePaidPrint:
    def __init__(self, backend, binding, photo_root, templates, printer, capability,
                 claim_operation, session_id, *, active=lambda:True):
        if backend.provider_mode != 'mock' or backend.delivery_policy != 'PRINT_REQUIRED_V1':
            raise ValueError('Explicit mock print fixture required')
        self.backend,self.binding,self.templates=backend,dict(binding),templates
        self.capability,self.claim_operation=capability,claim_operation
        self.active=active;self._closed=threading.Event();self._gate=threading.Lock();self._printing=False
        self.photo=PhotoTest(photo_root);self.lease=None
        try:
            view=self._authenticate()
            self.requirement=view['delivery_requirement']
            self.fence=view['service_fence']
            self.lease=KioskLease(str(self.photo.root/'paid-print.lock'))
            self.photo.restore(templates,binding,trusted_resume_permit(binding,validator=self._active))
            self.store=self.photo.store
            self.transaction,self.sessions,*_=reconstruct(self.store,templates,binding)
            self.index=next(i for i,s in enumerate(self.sessions) if s.plan.session_id==session_id)
            self.session=self.sessions[self.index]
            if self.session.output_path is None:
                raise CheckoutConflict('Original committed output required')
            self.digest=hashlib.sha256(self.session.output_path.read_bytes()).hexdigest()
            if self.requirement['copies'].get(self.session.plan.template.template_id)!=self.session.plan.print_copies:
                raise CheckoutConflict('Original required copies mismatch')
            self.photo.index=self.index;self.photo.phase='result'
            self.phase='result';self.workspace=None
            # Sanitize driver failures without retrying or forwarding driver text.
            def send(path,*,copies):
                try:return printer.print_image(path,copies=copies)
                except Exception:return SimpleNamespace(success=False)
            self.printer=SimpleNamespace(print_image=send)
        except BaseException:
            self.photo.close()
            if self.lease:self.lease.close()
            raise

    def _active(self):return not self._closed.is_set() and self.active()

    def _authenticate(self):
        if not self._active():raise RuntimeError('Original customer visit required')
        b=self.binding
        view=self.backend.customer_claim(b['order_id'],b['booth_id'],self.capability,self.claim_operation)
        if (view['customer_claim']['payment_verified'] is not True or view['grant_id']!=b['grant_id']
                or b['merchant_id']!=self.backend.merchant_id
                or any(view['fulfillment'].get(k)!=b[k] for k in ('fulfillment_id','transaction_id','allocation_operation_id','contract_hash','booth_id','merchant_id'))):
            raise CheckoutConflict('Original paid allocation required')
        if hasattr(self,'requirement') and (view['delivery_requirement']!=self.requirement or view['service_fence']!=self.fence):
            raise CheckoutConflict('Original delivery authority retired')
        return view

    def _edit(self,callback):
        def checked(manifest):
            if manifest.get('payment_binding')!=self.binding:
                raise CheckoutConflict('Original payment binding required')
            tx,sessions,*_=reconstruct(self.store,self.templates,self.binding)
            session=sessions[self.index]
            if session.output_path!=self.session.output_path or hashlib.sha256(session.output_path.read_bytes()).hexdigest()!=self.digest:
                raise CheckoutConflict('Original output bytes required')
            key=self.session.plan.session_id
            expected={'requirement_id':self.requirement['requirement_id'],
                      'payment_binding':self.binding,'output_sha256':self.digest}
            old=manifest['test_print_jobs'].get(key)
            if old is not None and any(old.get(k)!=v for k,v in expected.items()):
                raise CheckoutConflict('Unproven prior print intent requires inspection')
            if old is None and not self._active():
                raise RuntimeError('Original customer visit required')
            callback(manifest)
            manifest['test_print_jobs'][key].update(expected)
        PhotoTest._edit(self,checked)

    def print_result(self):
        with self._gate:
            if self._printing or not self._active():raise RuntimeError('Print owner unavailable')
            self._printing=True
        try:
            self._authenticate()
            return PhotoTest.print_result(self)
        finally:
            with self._gate:
                self._printing=False
                if self._closed.is_set():self._release()

    def snapshot(self):
        if not self._active():return {'phase':'claim_required'}
        view=self.photo.snapshot()
        view.update(print_available=True,auto_print=False)
        return view

    def _release(self):
        self.photo.close()
        if self.lease:self.lease.close()

    def close(self):
        self._closed.set()
        with self._gate:
            if not self._printing:self._release()
