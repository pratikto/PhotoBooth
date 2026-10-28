"""Offline HTTP fixture using the real API/client; no external merchant request."""
from fastapi.testclient import TestClient
from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.qris_api import create_app
from photobooth.qris_kiosk_client import QrisKioskClient
from photobooth.qris_session import KioskCheckout
from photobooth.kiosk_v2.sandbox_checkout import SandboxCheckout, SandboxJobs
from photobooth.qr_code import create_qr_image
from photobooth.kiosk_v2.qr_branding import with_meong_logo
from tests.test_checkout_backend import FakeProvider, KEY, MERCHANT


class Response:
    def __init__(self, response):
        self.response=response;self.status_code=response.status_code
    def iter_content(self, size): yield self.response.content
    def close(self): self.response.close()


class InProcessSession:
    def __init__(self, app): self.http=TestClient(app)
    def request(self, method, url, **kwargs):
        kwargs.pop('stream');kwargs.pop('allow_redirects')
        return Response(self.http.request(method,url,**kwargs))
    def close(self): self.http.close()


class Fixture:
    def __init__(self, root):
        self.root=root
        self.provider=FakeProvider()
        self.store=CheckoutStore(root/'orders.sqlite')
        self.backend=CheckoutBackend(self.store,self.provider,KEY,MERCHANT)
        auth=BoothAuthenticator({'PB001':'a'*48})
        self.session=InProcessSession(create_app(self.backend,auth,rate_limit=1000))
        client=QrisKioskClient('http://127.0.0.1:8765','PB001','a'*48,allow_local_http=True,session=self.session)
        self.flow=KioskCheckout(root/'visit.json',client,mode='sandbox',booth_id='PB001',endpoint=client.base_url)
        def offline_qr(order):
            original = create_qr_image('MEONG OFFLINE HTTP FIXTURE - NOT PAYABLE',with_logo=False)
            return with_meong_logo(original)
        self.service=SandboxCheckout(self.flow,image_loader=offline_qr)
        self.jobs=SandboxJobs(lambda:self.service)
    def paid(self):
        oid=self.flow.snapshot()['order']['order_id']
        self.provider.rows[oid].update(transaction_status='settlement',status_code='200')
        self.store.db.execute('UPDATE checkouts SET check_after=0')
    def close(self):
        self.jobs.close();self.jobs.wait_closed();self.store.close()
