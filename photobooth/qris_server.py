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
    if env.get('MEONG_QRIS_MODE', 'sandbox') != 'sandbox':
        raise RuntimeError('Only Sandbox payment is supported by this server')
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
