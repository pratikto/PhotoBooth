"""Sandbox HTTP boundary: strict input, bounded streaming and threaded I/O."""
import asyncio
from collections import OrderedDict
from contextlib import asynccontextmanager
import json
import hmac
import re
import time
import uuid
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from starlette.concurrency import run_in_threadpool

from photobooth.checkout_backend import ProviderUnavailable
from photobooth.checkout_store import CheckoutConflict, CheckoutMissing, identifier
from photobooth.payment_quote import quote_checkout


class NewOrder(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    quantities: dict[str, Annotated[int, Field(strict=True, ge=1, le=10)]] = Field(min_length=1, max_length=12)
    customer_capability_hash: str | None = Field(default=None, pattern=r'^[a-f0-9]{64}$')

    @field_validator('quantities')
    @classmethod
    def valid_catalog(cls, value):
        quote_checkout(value)
        return value


class ServiceUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    grant_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    state: str = Field(pattern=r'^(STARTED|COMPLETED)$')
    transaction_id: str = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')
    service_fence: str | None = Field(default=None,pattern=r'^[a-f0-9]{32}$')


class ReleaseUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    operation_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    isolation_id: str | None = Field(default=None,pattern=r'^[a-f0-9]{32}$')
    legacy_without_ticket: bool = False


class AllocationUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    grant_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    operation_id: str = Field(pattern=r'^[A-Za-z0-9_-]{16,64}$')


class CustomerClaim(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    capability: str = Field(pattern=r'^[A-Za-z0-9_-]{43}$')
    operation_id: str = Field(pattern=r'^[A-Za-z0-9_-]{16,64}$')


class FulfillmentIssue(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    operation_id: str = Field(pattern=r'^[A-Za-z0-9_-]{16,64}$')
    reason: str = Field(pattern=r'^(PHOTO_STATE_UNAVAILABLE|CAPTURE_FAILED|COMPOSITION_FAILED|DEVICE_UNAVAILABLE)$')


class RecoveryUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    action_id: str = Field(pattern=r'^[A-Za-z0-9_-]{16,64}$')
    action: str = Field(pattern=r'^(reconcile|resume|abandon|complete)$')
    reason: str = Field(min_length=1, max_length=160)
    transaction_id: str | None = Field(default=None, pattern=r'^[A-Za-z0-9_-]{1,64}$')

    @field_validator('reason')
    @classmethod
    def valid_reason(cls, value):
        if not value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in value):
            raise ValueError('A plain recovery reason is required')
        return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON member')
        result[key] = value
    return result


async def bounded_json(request, limit=16384):
    """Stop on the first excessive chunk, even without Content-Length."""
    try:
        length = int(request.headers.get('content-length', '0'))
    except ValueError as error:
        raise HTTPException(400, 'Invalid content length') from error
    if length < 0:
        raise HTTPException(400, 'Invalid content length')
    if length > limit:
        raise HTTPException(413, 'Payload too large')
    payload = bytearray()
    try:
        async with asyncio.timeout(5):
            async for chunk in request.stream():
                if len(payload) + len(chunk) > limit:
                    raise HTTPException(413, 'Payload too large')
                payload.extend(chunk)
        data = json.loads(payload, object_pairs_hook=unique_object)
        if not isinstance(data, dict):
            raise ValueError('JSON object required')
        return data
    except TimeoutError as error:
        raise HTTPException(408, 'Request body timed out') from error
    except (ValueError, UnicodeError) as error:
        raise HTTPException(400, 'Invalid JSON') from error


class LocalRateLimit:
    """Bounded one-worker Sandbox guard; production needs an ingress limiter."""
    def __init__(self, limit=120, window=60):
        self.limit, self.window = limit, window
        self.entries = OrderedDict()

    def check(self, key):
        now = time.monotonic()
        start, count = self.entries.pop(key, (now, 0))
        if now - start >= self.window:
            start, count = now, 0
        self.entries[key] = (start, count + 1)
        while len(self.entries) > 2048:
            self.entries.popitem(last=False)
        if count >= self.limit:
            raise HTTPException(429, 'Too many requests', headers={'Retry-After': '60'})


def create_app(service, authenticator, *, on_shutdown=None, rate_limit=120, recovery_pin=None):
    if recovery_pin is not None and (not isinstance(recovery_pin, str) or re.fullmatch(r'[0-9]{8}', recovery_pin) is None):
        raise ValueError('Recovery requires an eight-digit operator PIN')
    @asynccontextmanager
    async def lifespan(_app):
        yield
        if on_shutdown is not None:
            await run_in_threadpool(on_shutdown)

    app = FastAPI(title='MEONG QRIS Sandbox', version='0.2.0', lifespan=lifespan)
    limiter = LocalRateLimit(rate_limit)
    operator_limiter = LocalRateLimit(8, 60)
    operator_actor = 'sandbox-operator-' + uuid.uuid4().hex

    async def audit_operator_denial(route, reason):
        try:
            await run_in_threadpool(service.store.record_operator_denial, route, reason)
        except Exception:
            raise HTTPException(503, 'Operator authentication temporarily unavailable') from None

    async def operator_identity(request, booth_id, authorization, pin, route):
        booth = booth_identity(request, booth_id, authorization)
        if not recovery_pin or not getattr(service, 'sandbox_recovery_supported', False):
            raise HTTPException(404, 'Sandbox recovery is not enabled')
        peer = request.client.host if request.client else 'unknown'
        try:
            operator_limiter.check('operator:' + peer)
        except HTTPException as error:
            if error.status_code == 429:
                await audit_operator_denial(route, 'RATE_LIMITED')
            raise
        if not isinstance(pin, str) or re.fullmatch(r'[0-9]{8}', pin) is None or not hmac.compare_digest(pin, recovery_pin):
            await audit_operator_denial(route, 'INVALID_PIN')
            raise HTTPException(401, 'Operator authentication required')
        return booth

    def booth_identity(request, booth_id, authorization):
        peer = request.client.host if request.client else 'unknown'
        limiter.check('peer:' + peer)
        if len(booth_id) > 64 or len(authorization) > 520:
            raise HTTPException(401, 'Unauthorized')
        identity = authenticator.authenticate(booth_id, authorization)
        if identity is None:
            raise HTTPException(401, 'Unauthorized')
        return identity

    async def invoke(function, *args, operator_route=None, **kwargs):
        try:
            return await run_in_threadpool(function, *args, **kwargs)
        except CheckoutMissing as error:
            if operator_route is not None:
                await audit_operator_denial(operator_route, 'NOT_OWNED')
            raise HTTPException(404, 'Order not found') from error
        except CheckoutConflict as error:
            if operator_route is not None:
                await audit_operator_denial(operator_route, 'ACTION_CONFLICT')
            raise HTTPException(409, 'Checkout requires recovery or completion') from error
        except PermissionError as error:
            raise HTTPException(403, 'Original customer proof required') from error
        except ProviderUnavailable as error:
            raise HTTPException(503, 'Provider verification temporarily unavailable') from error
        except ValueError as error:
            raise HTTPException(422, 'Invalid checkout') from error
        except Exception as error:
            raise HTTPException(503, 'Checkout temporarily unavailable') from error

    def key(value):
        try:
            return identifier(value, minimum=16)
        except ValueError as error:
            raise HTTPException(422, 'Valid Idempotency-Key required') from error

    @app.get('/api/health')
    async def health():
        return {'status': 'ok', 'mode': getattr(service, 'mode', 'sandbox'), 'api_version': 2}

    @app.post('/api/orders', status_code=201)
    async def create_order(request: Request, x_booth_id: str = Header(default=''),
                           authorization: str = Header(default=''),
                           idempotency_key: str = Header(default='')):
        booth = booth_identity(request, x_booth_id, authorization)
        visit = key(idempotency_key)
        data = await bounded_json(request, 8192)
        try:
            body = NewOrder.model_validate(data)
        except (ValidationError, ValueError) as error:
            raise HTTPException(422, 'Invalid template quantities') from error
        if body.customer_capability_hash is None:
            return await invoke(service.create_order, booth, body.quantities, visit)
        return await invoke(lambda: service.create_order(booth, body.quantities, visit,
            customer_capability_hash=body.customer_capability_hash))

    @app.get('/api/orders/{order_id}')
    async def order_status(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                           authorization: str = Header(default='')):
        booth = booth_identity(request, x_booth_id, authorization)
        result = await invoke(service.status, order_id, booth)
        if result is None:
            raise HTTPException(404, 'Order not found')
        return result

    @app.post('/api/orders/{order_id}/claim')
    async def claim_order(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                          authorization: str = Header(default=''),
                          idempotency_key: str = Header(default='')):
        booth = booth_identity(request, x_booth_id, authorization)
        return await invoke(service.claim, order_id, booth, key(idempotency_key))

    @app.post('/api/orders/{order_id}/reconcile')
    async def reconcile_order(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                              authorization: str = Header(default=''),
                              x_reconciliation_trigger: str = Header(default='poll')):
        booth = booth_identity(request, x_booth_id, authorization)
        return await invoke(service.reconcile, order_id, booth, x_reconciliation_trigger)

    @app.post('/api/orders/{order_id}/service')
    async def service_update(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                             authorization: str = Header(default='')):
        booth = booth_identity(request, x_booth_id, authorization)
        data = await bounded_json(request, 2048)
        try:
            body = ServiceUpdate.model_validate(data)
        except ValidationError as error:
            raise HTTPException(422, 'Invalid service acknowledgement') from error
        options={'service_fence':body.service_fence} if body.service_fence is not None else {}
        return await invoke(service.service_transition, order_id, booth, body.grant_id,
                            body.state, body.transaction_id,**options)

    @app.post('/api/orders/{order_id}/allocate')
    async def allocate_order(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                             authorization: str = Header(default='')):
        booth = booth_identity(request, x_booth_id, authorization)
        try:
            body = AllocationUpdate.model_validate(await bounded_json(request, 2048))
        except ValidationError as error:
            raise HTTPException(422, 'Invalid allocation request') from error
        return await invoke(service.allocate, order_id, booth, body.grant_id, body.operation_id)

    @app.post('/api/orders/{order_id}/fulfillment-issue')
    async def fulfillment_issue(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                                authorization: str = Header(default='')):
        booth = booth_identity(request,x_booth_id,authorization)
        try:
            body=FulfillmentIssue.model_validate(await bounded_json(request,2048))
        except ValidationError as error:
            raise HTTPException(422,'Invalid fulfillment issue request') from error
        return await invoke(service.report_fulfillment_issue,order_id,booth,body.operation_id,body.reason)

    @app.post('/api/orders/{order_id}/customer-claim')
    async def customer_claim(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                             authorization: str = Header(default='')):
        booth = booth_identity(request, x_booth_id, authorization)
        try:
            body = CustomerClaim.model_validate(await bounded_json(request, 2048))
        except ValidationError as error:
            raise HTTPException(422, 'Invalid customer proof request') from error
        return await invoke(service.customer_claim, order_id, booth, body.capability, body.operation_id)

    @app.post('/api/orders/{order_id}/cancel')
    async def cancel_order(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                           authorization: str = Header(default='')):
        booth = booth_identity(request, x_booth_id, authorization)
        return await invoke(service.cancel, order_id, booth)

    @app.post('/api/orders/{order_id}/recovery/release')
    async def release_order(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                            authorization: str = Header(default=''), x_recovery_pin: str = Header(default='')):
        booth=await operator_identity(request,x_booth_id,authorization,x_recovery_pin,'release')
        try:
            body=ReleaseUpdate.model_validate(await bounded_json(request,2048))
        except ValidationError as error:
            raise HTTPException(422,'Invalid release request') from error
        if body.isolation_id is None:
            return await invoke(service.prepare_release,order_id,booth,body.operation_id,operator_actor,
                                legacy_without_ticket=body.legacy_without_ticket,
                                operator_route='release')
        if body.legacy_without_ticket:
            raise HTTPException(422,'Legacy intent belongs to release preparation only')
        return await invoke(service.acknowledge_release,order_id,booth,body.operation_id,body.isolation_id,
                            operator_route='release')

    @app.post('/api/orders/{order_id}/recovery/inspect')
    async def recovery_inspect(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                               authorization: str = Header(default=''), x_recovery_pin: str = Header(default='')):
        booth = await operator_identity(request, x_booth_id, authorization, x_recovery_pin, 'inspect')
        return await invoke(service.recovery_inspect, order_id, booth, operator_route='inspect')

    @app.post('/api/orders/{order_id}/recovery/resolve')
    async def recovery_resolve(order_id: str, request: Request, x_booth_id: str = Header(default=''),
                               authorization: str = Header(default=''), x_recovery_pin: str = Header(default='')):
        booth = await operator_identity(request, x_booth_id, authorization, x_recovery_pin, 'resolve')
        data = await bounded_json(request, 2048)
        try:
            body = RecoveryUpdate.model_validate(data)
        except ValidationError as error:
            raise HTTPException(422, 'Invalid recovery decision') from error
        return await invoke(service.recovery_resolve, order_id, booth, body.action_id,
                            body.action, body.reason, body.transaction_id, operator_actor,
                            operator_route='resolve')

    @app.post('/api/webhooks/midtrans')
    async def midtrans_webhook(request: Request):
        limiter.check('webhook:' + (request.client.host if request.client else 'unknown'))
        notification = await bounded_json(request)
        try:
            accepted = await run_in_threadpool(service.process_notification, notification)
        except (ValueError, TypeError, KeyError) as error:
            raise HTTPException(400, 'Invalid notification') from error
        except Exception as error:
            raise HTTPException(503, 'Provider verification unavailable') from error
        if not accepted:
            raise HTTPException(503, 'Notification not applied; retry required')
        return {'received': True}

    return app
