"""Isolated PP backend HTTP boundary; never mounts legacy or media routes.

The injected trusted server owns provider credentials/readiness. This application
factory does not start listeners, configure merchants, or enable customer payments.
"""
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.concurrency import run_in_threadpool

from photobooth.post_preview_inbox import PostPreviewNotificationInbox
from photobooth.post_preview_lifecycle import PostPreviewLifecycleWorker
from photobooth.post_preview_authority import authenticated_charge_request
from photobooth.post_preview_readiness import ReadinessScope
from photobooth.post_preview_store import DraftHeld, DraftLease, ORDER_VERSION
from photobooth.qris_api import LocalRateLimit, bounded_json


class OwnerRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    visit_id: str = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')
    generation: int = Field(ge=1, le=2147483647)


class ContinueRequest(OwnerRequest):
    actively_continuing: bool


class LifecycleRequest(OwnerRequest):
    event: Literal['USER_CANCEL', 'APP_SUSPENDED', 'INACTIVITY_WARNING', 'INACTIVITY_EXPIRED', 'VISIT_ABANDONED', 'RESULT_TIMEOUT']


class ReconcileRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    trigger: Literal['poll', 'restart', 'connectivity'] = 'poll'


def create_app(payments, authenticator, *, inbox=None, on_shutdown=None, rate_limit=120,
               background_worker=True):
    if type(background_worker) is not bool:
        raise ValueError('Explicit lifecycle worker selection required')
    inbox = inbox or PostPreviewNotificationInbox(payments)
    worker = PostPreviewLifecycleWorker(payments, inbox) if background_worker else None
    limiter = LocalRateLimit(rate_limit)

    @asynccontextmanager
    async def lifespan(_app):
        if worker:
            worker.start()
        try:
            yield
        finally:
            if worker and not await run_in_threadpool(worker.stop):
                # Never close a ledger underneath an unfinished provider call.
                raise RuntimeError('Original lifecycle worker remains active')
            if on_shutdown:
                await run_in_threadpool(on_shutdown)

    app = FastAPI(title='MEONG post-preview isolated backend', lifespan=lifespan)
    app.state.notification_inbox = inbox
    app.state.lifecycle_worker = worker

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request, _error):
        return JSONResponse(status_code=422, content={'detail': 'Invalid request'})

    def identity(request, booth, authorization):
        limiter.check('peer:' + (request.client.host if request.client else 'unknown'))
        if len(booth) > 64 or len(authorization) > 520:
            raise HTTPException(401, 'Unauthorized')
        value = authenticator.authenticate(booth, authorization)
        if value is None:
            raise HTTPException(401, 'Unauthorized')
        return value

    async def body(request, model):
        data = await bounded_json(request)
        try:
            return model.model_validate(data)
        except ValidationError:
            raise HTTPException(422, 'Invalid request') from None

    async def invoke(fn, *args, **kwargs):
        try:
            return await run_in_threadpool(fn, *args, **kwargs)
        except DraftHeld:
            raise HTTPException(409, 'Original checkout is held') from None
        except ValueError:
            raise HTTPException(422, 'Invalid request') from None
        except Exception:
            raise HTTPException(503, 'Checkout temporarily unavailable') from None

    def lease(group, booth, owner):
        with payments.ledger.write():
            intent, _ = payments._group(group, booth)
            if intent['visit_id'] != owner.visit_id:
                raise DraftHeld('Original visit required')
            return DraftLease(intent['draft_id'], booth, owner.visit_id, owner.generation)

    def envelope(view):
        return dict(view, mode=payments.mode, order_version=ORDER_VERSION)

    def charge_call(function, group, token, **kwargs):
        # This runs only after authenticated booth/visit parsing above. No ready
        # flag, bearer secret or caller observation enters the readiness report.
        with payments.ledger.write():
            payments.ledger._owned(token)
            intent, _ = payments._group(group, token.booth_id)
            scope = ReadinessScope(group, token.booth_id, intent['contract_sha256'], token.generation)
            stamp = payments._now()
        with authenticated_charge_request(scope, stamp):
            return function(token, **kwargs)

    @app.get('/api/postpay/health')
    async def health():
        return {'api_version': 1, 'order_version': ORDER_VERSION, 'mode': payments.mode,
                'fulfillment_enabled': False}

    @app.get('/api/postpay/groups/{group}')
    async def inspect(group: str, request: Request, x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
        booth = identity(request, x_booth_id, authorization)
        return envelope(await invoke(payments.inspect, group, booth))

    @app.post('/api/postpay/groups/{group}/begin')
    async def begin(group: str, request: Request, x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
        booth = identity(request, x_booth_id, authorization)
        owner = await body(request, OwnerRequest)
        token = await invoke(lease, group, booth, owner)
        return envelope(await invoke(charge_call, payments.begin, group, token))

    @app.post('/api/postpay/groups/{group}/continue')
    async def renew(group: str, request: Request, x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
        booth = identity(request, x_booth_id, authorization)
        owner = await body(request, ContinueRequest)
        token = await invoke(lease, group, booth, owner)
        return envelope(await invoke(charge_call, payments.continue_expired, group, token,
                                     actively_continuing=owner.actively_continuing))

    @app.post('/api/postpay/groups/{group}/reconcile')
    async def reconcile(group: str, request: Request, x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
        booth = identity(request, x_booth_id, authorization)
        action = await body(request, ReconcileRequest)
        return envelope(await invoke(payments.reconcile_all, group, booth, force=action.trigger != 'poll'))

    @app.post('/api/postpay/groups/{group}/lifecycle')
    async def lifecycle(group: str, request: Request, x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
        booth = identity(request, x_booth_id, authorization)
        owner = await body(request, LifecycleRequest)
        token = await invoke(lease, group, booth, owner)
        await invoke(payments.signal_lifecycle, token, owner.event)
        return envelope(await invoke(payments.inspect, group, booth))

    @app.post('/api/postpay/webhooks/midtrans')
    async def webhook(request: Request):
        limiter.check('webhook:' + (request.client.host if request.client else 'unknown'))
        data = await bounded_json(request)
        # Durable ACK contains no provider GET; explicit leased worker does that.
        try:
            return await run_in_threadpool(inbox.accept, data)
        except ValueError:
            raise HTTPException(400, 'Invalid notification') from None
        except Exception:
            raise HTTPException(503, 'Notification temporarily unavailable') from None

    return app
