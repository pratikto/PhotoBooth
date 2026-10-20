"""Sandbox-only ASGI entrypoint: uvicorn photobooth.qris_server:app

Environment variables:
 MIDTRANS_SERVER_KEY, MEONG_QRIS_BOOTH_ID, MEONG_QRIS_BOOTH_TOKEN,
 MEONG_QRIS_DB_PATH (optional).
Never expose the sandbox server directly to the public internet.
"""
import os
from photobooth.booth_auth import BoothAuthenticator
from photobooth.checkout_service import SandboxCheckoutService
from photobooth.midtrans_sandbox import MidtransSandboxClient
from photobooth.payment_orders import OrderStore
from photobooth.qris_api import create_app


def build_sandbox_app(environ=None):
    env = os.environ if environ is None else environ
    server_key = env.get("MIDTRANS_SERVER_KEY", "")
    booth_id = env.get("MEONG_QRIS_BOOTH_ID", "")
    token = env.get("MEONG_QRIS_BOOTH_TOKEN", "")
    if not server_key or not booth_id or not token:
        raise RuntimeError("Missing sandbox backend configuration")
    auth = BoothAuthenticator({booth_id: token})
    store = OrderStore(env.get("MEONG_QRIS_DB_PATH", "data/qris-sandbox.sqlite"))
    service = SandboxCheckoutService(store, MidtransSandboxClient(server_key), server_key)
    return create_app(service, auth)


# Uvicorn resolves this on import; missing credentials fail closed.
app = build_sandbox_app()
