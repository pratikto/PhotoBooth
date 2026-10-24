"""Sandbox server factory; import has no credential or database side effects.

Run: python -m uvicorn photobooth.qris_server:build_sandbox_app --factory
Use one worker behind HTTPS/rate-limited ingress; never deploy this as live QRIS.
"""
import os
from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.midtrans_sandbox import MidtransSandboxClient
from photobooth.qris_api import create_app


def build_sandbox_app(environ=None):
    env = os.environ if environ is None else environ
    mode = env.get('MEONG_QRIS_MODE', 'sandbox')
    if mode not in {'sandbox', 'mock'}:
        raise RuntimeError('Only Sandbox or explicit offline mock is supported')
    if mode == 'mock':
        return build_mock_app(env)
    names = ('MIDTRANS_SERVER_KEY', 'MIDTRANS_MERCHANT_ID',
             'MEONG_QRIS_BOOTH_ID', 'MEONG_QRIS_BOOTH_TOKEN')
    values = [env.get(name, '') for name in names]
    if not all(values):
        raise RuntimeError('Missing Sandbox backend configuration')
    server_key, merchant_id, booth_id, token = values
    auth = BoothAuthenticator({booth_id: token})
    provider = MidtransSandboxClient(server_key, timeout=6)
    store = CheckoutStore(env.get('MEONG_QRIS_DB_PATH', 'data/qris-sandbox.sqlite'))
    try:
        service = CheckoutBackend(store, provider, server_key, merchant_id)
        return create_app(service, auth, on_shutdown=store.close)
    except BaseException:
        store.close()
        raise


def build_mock_app(env):
    from photobooth.qris_mock import MockQrisProvider
    auth = BoothAuthenticator({env.get('MEONG_QRIS_BOOTH_ID', ''): env.get('MEONG_QRIS_BOOTH_TOKEN', '')})
    path = env.get('MEONG_QRIS_DB_PATH', 'data/qris-mock.sqlite')
    store = CheckoutStore(path)
    provider = MockQrisProvider(path + '.provider',
        settle_after=float(env.get('MEONG_QRIS_MOCK_DELAY', '8')),
        scenario=env.get('MEONG_QRIS_MOCK_SCENARIO', 'settlement'))
    service = CheckoutBackend(store, provider, 'offline-mock-not-a-merchant-key', 'MOCK')
    service.mode = 'mock'
    def close():
        provider.close(); store.close()
    return create_app(service, auth, on_shutdown=close)
