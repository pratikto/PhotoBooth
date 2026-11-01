"""Real HTTP boundary with isolated synthetic provider/camera/vault adapters."""
import os
from PIL import Image
from fastapi.testclient import TestClient
from photobooth.booth_auth import BoothAuthenticator
from photobooth.credential_vault import SyntheticAeadProtector
from photobooth.post_preview_api import create_app
from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.kiosk_v2.post_preview_checkout import PrivateCheckoutService
from tests import test_post_preview_payments as payment_fixtures


class ResponseAdapter:
    def __init__(self, response):
        self.response, self.status_code = response, response.status_code

    def iter_content(self, size):
        return self.response.iter_bytes(size)

    def close(self):
        self.response.close()


class SessionAdapter:
    def __init__(self, client):
        self.client = client
        self.lose_response = False

    def request(self, method, url, **kwargs):
        assert kwargs.pop('allow_redirects') is False
        assert kwargs.pop('stream') is True
        response = self.client.request(method, url, follow_redirects=False, **kwargs)
        if self.lose_response:
            self.lose_response = False
            response.close()
            raise OSError('Synthetic HTTP response loss')
        return ResponseAdapter(response)

    def close(self):
        self.client.close()


class CheckoutFixture:
    def __init__(self, root):
        self.ready = ChargeReadiness(True, True, True, True, True, True, True, 25)
        self.client = PostPreviewClient('https://fixture.invalid', 'PB001', 'SYNTHETIC-BOOTH-'+'a'*48,
                                        expected_mode='mock')
        self.protector = SyntheticAeadProtector(os.urandom(32), fixture=True)
        self.service = PrivateCheckoutService(root, payment_client=self.client, protector=self.protector,
            merchant_id='MTEST', readiness=lambda: self.ready,
            qr_loader=lambda _: Image.new('RGB', (180,180), 'white'), allow_incomplete_fixture=True)
        self.provider = payment_fixtures.SyntheticProvider()
        self.backend = PostPreviewPayments(self.service.ledger, self.provider, 'MTEST',
            readiness=lambda _: self.ready, poll_seconds=0)
        auth = BoothAuthenticator({'PB001':'SYNTHETIC-BOOTH-'+'a'*48})
        self.http = TestClient(create_app(self.backend, auth))
        self.session = SessionAdapter(self.http)
        self.client._transport.session.close()
        self.client._transport.session = self.session

    def close(self):
        self.service.close()
        self.service.wait_closed(10)
        self.client.close()
