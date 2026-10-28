"""Thin v2 adapter over the unchanged QRIS branch protocol; no payment authority here."""
from pathlib import Path
import os
import threading
import hashlib

from photobooth.qris_kiosk_client import QrisKioskClient
from photobooth.qris_session import KioskCheckout
from photobooth.qris_evidence import sandbox_qr_url
from .qr_branding import branded_sandbox_qr_image
from .demo_game import GameJobs

ACTIONS = {'boot', 'begin', 'begin_ready', 'check', 'cancel', 'prepare', 'started', 'complete', 'recover',
           'ticket_saved', 'customer_claim', 'scan_claim', 'resume', 'resumed','fulfillment_issue',
           'operator_inspect','prepare_release','acknowledge_release'}


def simulator_qr_url(view):
    """Return only the active Sandbox image action, never a derived URL/payload."""
    view = view or {}
    order = view.get('order') or {}
    if (view.get('phase') != 'WAITING' or order.get('mode') != 'sandbox'
            or order.get('state') != 'PENDING' or order.get('verification_pending')
            or view.get('ticket_required') or view.get('customer_claim_required')):
        return None
    try:
        return sandbox_qr_url(order.get('qr_url'))
    except (ValueError, TypeError):
        return None


def sandbox_enabled(env=None):
    env = os.environ if env is None else env
    enabled = env.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX') == '1'
    if enabled and env.get('PHOTOBOOTH_V2_CHECKOUT_MOCK') == '1':
        raise ValueError('Select one checkout test mode')
    if enabled and (env.get('MEONG_QRIS_MODE') != 'sandbox' or
                    env.get('MIDTRANS_SERVER_KEY') or env.get('MIDTRANS_MERCHANT_ID')):
        raise ValueError('Sandbox GUI requires isolated booth credentials, never merchant credentials')
    return enabled


def configured_sandbox(root, env=None):
    env = os.environ if env is None else env
    if not sandbox_enabled(env):
        raise ValueError('Sandbox was not selected')
    path = Path(env.get('MEONG_QRIS_JOURNAL', ''))
    base = (Path(root)/'data'/'kiosk-v2-sandbox').resolve()
    if not path.is_absolute() or not path.resolve().is_relative_to(base):
        raise ValueError('Use an isolated v2 Sandbox profile')
    client = QrisKioskClient(env.get('MEONG_QRIS_API_URL', ''),
                            env.get('MEONG_QRIS_BOOTH_ID', ''),
                            env.get('MEONG_QRIS_BOOTH_TOKEN', ''),
                            allow_local_http=env.get('MEONG_QRIS_LOCAL_PREVIEW') == '1',
                            expected_mode='sandbox')
    try:
        flow = KioskCheckout(path, client, mode='sandbox', booth_id=client.booth_id,
                             endpoint=client.base_url)
    except BaseException:
        client.close()
        raise
    return SandboxCheckout(flow)


class SandboxCheckout:
    """All calls run on the existing single-flight worker, including QR download."""
    def __init__(self, flow, *, image_loader=branded_sandbox_qr_image):
        self.flow, self.image_loader = flow, image_loader
        self.qr = self.qr_identity = None
        self.ticket_qr = self.ticket_identity = None

    def view(self):
        data = self.flow.snapshot()
        if data is None:
            return {'phase':'IDLE'}
        order = data.get('order') or {}
        data['customer_claim_required'] = self.flow.customer_claim_required
        data['resume_ready'] = False
        if data['phase']=='RECOVERY' and not data['customer_claim_required']:
            try:
                self.flow.resume_binding()
                data['resume_ready'] = True
            except RuntimeError:
                data['customer_claim_required'] = True
        data['ticket_required'] = bool(order.get('customer_capability_bound')
            and not self.flow.ticket_acknowledged and not self.flow.customer_claim_required
            and data['phase'] in {'CREATING','WAITING','RESERVED'})
        data['ticket_qr_rgb'] = None
        ticket = self.flow.customer_ticket() if data['ticket_required'] else None
        if ticket:
            identity=hashlib.sha256(ticket.encode()).hexdigest()
            if identity!=self.ticket_identity:
                from photobooth.qr_code import create_qr_image
                image=create_qr_image(ticket,with_logo=False).convert('RGB')
                self.ticket_qr=(image.size,image.tobytes());self.ticket_identity=identity
            data['ticket_qr_rgb']=self.ticket_qr
        else:
            self.ticket_qr=self.ticket_identity=None
        data['qr_rgb'] = None
        if (data['phase'] == 'WAITING' and order.get('state') == 'PENDING' and not order.get('verification_pending')
                and not data['customer_claim_required'] and not data['ticket_required']):
            identity = (order['order_id'], order.get('qr_url'))
            if identity != self.qr_identity:
                try:
                    image = self.image_loader(order).convert('RGB')
                    self.qr = (image.size, image.tobytes())
                    self.qr_identity = identity
                except Exception:
                    # Keep the persisted order; an image failure cannot create another charge.
                    self.qr = None
            data['qr_rgb'] = self.qr
        return data

    def boot(self):
        self.flow.refresh()
        return self.view()

    def begin(self, quantities):
        cart = {key:value for key,value in quantities.items() if value}
        # v2 touch controls retain their stricter 0..9 range.
        if any(type(n) is not int or not 1 <= n <= 9 for n in cart.values()):
            raise ValueError('Choose 1..9 copies')
        self.flow.begin(cart)
        return self.check()

    def begin_ready(self, quantities, camera_valid, observed_at):
        from .recovery_readiness import prepayment_readiness
        from photobooth.catalog import get_templates
        if not self.flow.active:
            prepayment_readiness(self.flow.path.parent/'photo-tests'/'photos',get_templates(),
                {k:v for k,v in quantities.items() if v},camera_valid,observed_at,
                delivery_enabled=any(os.environ.get('PHOTOBOOTH_V2_'+key)=='1' for key in ('PRINT','DRIVE')))
        return self.begin(quantities)

    def check(self):
        self.flow.refresh()
        return self.view()

    def cancel(self):
        self.flow.request_cancel()
        return self.check()

    def ticket_saved(self):
        self.flow.acknowledge_ticket()
        return self.view()

    def customer_claim(self, ticket):
        if self.flow.active:
            self.flow.customer_claim(ticket)
        else:
            self.flow.open_archived(ticket)
        return self.view()

    def prepare_release(self, pin):
        self.flow.prepare_release(pin)
        return self.view()

    def acknowledge_release(self, pin, receipt):
        self.flow.acknowledge_release(pin,receipt)
        return self.view()

    def scan_claim(self, frame):
        # Decode the existing camera owner's copied frame, never open a camera
        # or enable the DEMO/POS scanner. Never log the decoded capability.
        import cv2
        if frame is None or frame.size > 40_000_000*3:
            raise ValueError('Customer ticket frame required')
        ticket, _points, _straight=cv2.QRCodeDetector().detectAndDecode(frame)
        if not ticket:
            # Some valid recovery matrices are missed by the primary detector.
            # One bounded alternate attempt uses the same copied pixels and
            # installed OpenCV; decoded text still needs original customer proof.
            alternate=getattr(cv2,'QRCodeDetectorAruco',None)
            if callable(alternate):
                ticket, _points, _straight=alternate().detectAndDecode(frame)
        if not ticket.startswith('MEONG-RECOVERY-V1:'):
            raise ValueError('Original recovery QR required')
        return self.customer_claim(ticket)

    def resume(self):
        permit=self.flow.resume_permit()
        view=self.view()
        return {'view':view,'binding':self.flow.resume_binding(),'permit':permit,
                'service_state':view['order']['service_state'],'quantities':view['quantities']}

    def resumed(self, transaction_id, photo_phase):
        self.flow.confirm_resume(transaction_id,photo_phase)
        return self.view()

    def fulfillment_issue(self, reason):
        self.flow.report_fulfillment_issue(reason)
        return self.view()

    def operator_inspect(self, pin):
        order=(self.flow.snapshot() or {}).get('order') or {}
        result=self.flow.client.recovery_inspect(order['order_id'],pin)
        self.flow._accept(result)
        view=self.view()
        view['operator_report']={'payment':result['state'],'service':result['service_state'],
            'issue':(result.get('fulfillment_issue') or {}).get('reason'),
            'obligation':(result.get('fulfillment') or {}).get('obligation_state')}
        return view

    def prepare(self):
        self.flow.prepare_capture()
        return self.view()

    def started(self, transaction_id):
        self.flow.bind_transaction(transaction_id)
        return self.check()

    def complete(self):
        self.flow.request_complete()
        return self.check()

    def recover(self):
        self.flow.require_recovery()
        return self.view()

    def close(self):
        self.flow.close()


class SandboxJobs(GameJobs):
    """Reuse GameJobs; release its process lease only after its I/O has stopped."""
    def __init__(self, factory):
        super().__init__(factory, actions=ACTIONS)
        self._cleanup = None

    def close(self):
        if self._closed:
            return
        super().close()
        def cleanup():
            if self._thread:
                self._thread.join()
            if self.store:
                self.store.close()
        self._cleanup = threading.Thread(target=cleanup, name='v2-sandbox-close', daemon=True)
        self._cleanup.start()

    def wait_closed(self, timeout=30):
        if self._cleanup:
            self._cleanup.join(timeout)
        else:
            super().wait_closed(timeout)
