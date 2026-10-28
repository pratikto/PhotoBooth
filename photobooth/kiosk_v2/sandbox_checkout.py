"""Thin v2 adapter over the unchanged QRIS branch protocol; no payment authority here."""
from pathlib import Path
import os
import threading

from photobooth.qris_kiosk_client import QrisKioskClient
from photobooth.qris_session import KioskCheckout
from photobooth.qris_evidence import sandbox_qr_url
from .qr_branding import branded_sandbox_qr_image
from .demo_game import GameJobs

ACTIONS = {'boot', 'begin', 'check', 'cancel', 'prepare', 'started', 'complete', 'recover'}


def simulator_qr_url(view):
    """Return only the active Sandbox image action, never a derived URL/payload."""
    view = view or {}
    order = view.get('order') or {}
    if (view.get('phase') != 'WAITING' or order.get('mode') != 'sandbox'
            or order.get('state') != 'PENDING' or order.get('verification_pending')):
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

    def view(self):
        data = self.flow.snapshot()
        if data is None:
            return {'phase':'IDLE'}
        order = data.get('order') or {}
        data['qr_rgb'] = None
        if data['phase'] == 'WAITING' and order.get('state') == 'PENDING' and not order.get('verification_pending'):
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

    def check(self):
        self.flow.refresh()
        return self.view()

    def cancel(self):
        self.flow.request_cancel()
        return self.check()

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
