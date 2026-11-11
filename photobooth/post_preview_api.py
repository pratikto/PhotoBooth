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
from photobooth.post_preview_authority import authenticated_charge_request,authenticated_freeze_request
from photobooth.post_preview_readiness import ReadinessScope
from photobooth.post_preview_store import DraftHeld, DraftLease, ORDER_VERSION
from photobooth.qris_api import LocalRateLimit, bounded_json


class OwnerRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    visit_id: str = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')
    generation: int = Field(ge=1, le=2147483647)


class ContinueRequest(OwnerRequest):
    actively_continuing: bool


class FreezeRequest(OwnerRequest):
    revision:int=Field(ge=1,le=2147483647)
    expected_amount:int=Field(ge=1,le=2147483647)


class PresentationRequest(OwnerRequest):
    presentation_id: str = Field(pattern=r'^[a-f0-9]{32}$')


class LifecycleRequest(OwnerRequest):
    event: Literal['USER_CANCEL', 'APP_SUSPENDED', 'INACTIVITY_WARNING', 'INACTIVITY_EXPIRED', 'VISIT_ABANDONED', 'RESULT_TIMEOUT']


class ReconcileRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    trigger: Literal['poll', 'restart', 'connectivity'] = 'poll'


class ClaimRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    request_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    proof: str = Field(min_length=1,max_length=256)


def create_app(payments, authenticator, *, inbox=None, on_shutdown=None, rate_limit=120,
               background_worker=True, ccp_presentation=None, ticket_presentation=None,
               paid_delivery=None, protected_isolation=None, protected_claim=None, protected_freeze=None,
               worker_generations=None,recovery_authority=None):
    if type(background_worker) is not bool:
        raise ValueError('Explicit lifecycle worker selection required')
    if recovery_authority is not None:
        from photobooth.post_preview_interrupted_worker import OriginalRecoveryAuthority
        if (type(recovery_authority) is not OriginalRecoveryAuthority or recovery_authority.ledger is not payments.ledger
                or recovery_authority.review.scope.merchant_id!=payments.merchant_id or background_worker
                or worker_generations is not None or protected_isolation is None
                or protected_isolation.receipts.key is not recovery_authority.key):
            raise ValueError('Exact private original recovery-only authority required')
    if worker_generations is not None:
        from photobooth.post_preview_worker_binding import BackendWorkerEpoch
        if (type(worker_generations) is not BackendWorkerEpoch or worker_generations.ledger is not payments.ledger
                or worker_generations.scope.merchant_id != payments.merchant_id
                or protected_isolation is None or protected_claim is None or protected_freeze is None
                or protected_claim._worker_generations is not worker_generations):
            raise ValueError('Exact original private backend epoch required')
    if ccp_presentation is not None:
        from photobooth.post_preview_presentation import OriginalCCPPresentation
        if (type(ccp_presentation) is not OriginalCCPPresentation
                or ccp_presentation.ledger is not payments.ledger
                or ccp_presentation.credentials.merchant_id != payments.merchant_id):
            raise ValueError('Exact original backend proof authority required')
    if ticket_presentation is not None:
        from photobooth.post_preview_ticket_presentation import OriginalRecoveryPresentation
        if (type(ticket_presentation) is not OriginalRecoveryPresentation
                or ticket_presentation.ledger is not payments.ledger
                or ticket_presentation.credentials.payments is not payments):
            raise ValueError('Exact original backend paid ticket authority required')
    inbox = inbox or PostPreviewNotificationInbox(payments)
    if paid_delivery is not None:
        from photobooth.post_preview_sandbox_delivery import OriginalSandboxPaidDelivery
        if (type(paid_delivery) is not OriginalSandboxPaidDelivery
                or paid_delivery.binder.payments is not payments
                or paid_delivery.binder.presentation is not ticket_presentation):
            raise ValueError('Exact same original protected ticket/delivery backend required')
    if protected_isolation is not None or protected_claim is not None:
        from photobooth.post_preview_sandbox_handoff import OriginalSandboxIsolation,OriginalSandboxClaim
        if (type(protected_isolation) is not OriginalSandboxIsolation
                or type(protected_claim) is not OriginalSandboxClaim
                or protected_isolation.payments is not payments or protected_claim.payments is not payments
                or protected_isolation.delivery is not paid_delivery
                or ccp_presentation is None or ticket_presentation is None
                or protected_claim.ccp is not ccp_presentation.credentials
                or protected_claim.ticket is not ticket_presentation.credentials):
            raise ValueError('Exact original protected handoff authority required')
    worker = PostPreviewLifecycleWorker(payments, inbox) if background_worker else None
    if protected_freeze is not None:
        from photobooth.post_preview_freeze import OriginalSandboxFreeze
        if (type(protected_freeze) is not OriginalSandboxFreeze
                or protected_freeze.checkout.ledger is not payments.ledger
                or protected_isolation is None):
            raise ValueError('Exact original protected freeze backend required')
    limiter = LocalRateLimit(rate_limit)

    @asynccontextmanager
    async def lifespan(_app):
        if worker:
            worker.start()
        try:
            yield
        finally:
            if paid_delivery is not None and not await run_in_threadpool(paid_delivery.stop,timeout=1):
                raise RuntimeError('Original paid delivery worker remains active')
            if worker and not await run_in_threadpool(worker.stop):
                # Never close a ledger underneath an unfinished provider call.
                raise RuntimeError('Original lifecycle worker remains active')
            if ccp_presentation is not None:
                await run_in_threadpool(ccp_presentation.close)
            if ticket_presentation is not None:
                await run_in_threadpool(ticket_presentation.close)
            if on_shutdown:
                await run_in_threadpool(on_shutdown)

    app = FastAPI(title='MEONG post-preview isolated backend', lifespan=lifespan)
    app.state.notification_inbox = inbox
    app.state.lifecycle_worker = worker
    app.state.paid_delivery = paid_delivery

    @app.middleware('http')
    async def private_responses(request, call_next):
        allowed = recovery_authority is None or (
            request.method=='GET' and request.url.path=='/api/postpay/health' or
            request.method=='POST' and request.url.path==
                '/api/postpay/isolation/'+recovery_authority.review.operation_id+'/ack')
        response = await call_next(request) if allowed else JSONResponse(status_code=404,content={'detail':'Not found'})
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

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
            token=DraftLease(intent['draft_id'], booth, owner.visit_id, owner.generation)
            if worker_generations is not None: worker_generations.require_locked(token)
            return token

    def envelope(view):
        return dict(view, mode=payments.mode, order_version=ORDER_VERSION)

    def charge_call(function, group, token, **kwargs):
        # This runs only after authenticated booth/visit parsing above. No ready
        # flag, bearer secret or caller observation enters the readiness report.
        with payments.ledger.write():
            payments.ledger._owned(token)
            if worker_generations is not None: worker_generations.require_locked(token)
            intent, _ = payments._group(group, token.booth_id)
            scope = ReadinessScope(group, token.booth_id, intent['contract_sha256'], token.generation)
            stamp = payments._now()
        with authenticated_charge_request(scope, stamp):
            return function(token, **kwargs)

    @app.get('/api/postpay/health')
    async def health():
        return {'api_version': 1, 'order_version': ORDER_VERSION, 'mode': payments.mode,
                'fulfillment_enabled': False}

    if worker_generations is not None:
        @app.post('/api/postpay/drafts/{draft_id}/worker-binding')
        async def original_worker_binding(draft_id:str,request:Request,
                x_booth_id:str=Header(default=''),authorization:str=Header(default='')):
            booth=identity(request,x_booth_id,authorization)
            command=await body(request,OwnerRequest)
            token=DraftLease(draft_id,booth,command.visit_id,command.generation)
            await invoke(worker_generations.bind,token)
            return dict(kind='ORIGINAL_WORKER_BOUND',draft_id=draft_id,booth_id=booth,
                visit_id=token.visit_id,generation=token.generation,mode=payments.mode,
                order_version=ORDER_VERSION,fulfillment_authorized=False)

    if protected_freeze is not None:
        def freeze_call(token,command):
            if worker_generations is not None: worker_generations.require(token)
            scope=protected_freeze.scope(token,revision=command.revision,expected_amount=command.expected_amount)
            with authenticated_freeze_request(scope,payments._now()):
                intent=protected_freeze.freeze(token,revision=command.revision,
                    expected_amount=command.expected_amount,expected_scope=scope)
            return dict(kind='FROZEN_CHECKOUT',purchase_group_id=intent['purchase_group_id'],
                draft_id=token.draft_id,booth_id=token.booth_id,visit_id=token.visit_id,
                generation=token.generation,revision=command.revision,amount=scope.amount,
                contract_sha256=intent['contract_sha256'],phase='CREATE_PREPARED',
                mode=payments.mode,order_version=ORDER_VERSION,fulfillment_authorized=False)

        @app.post('/api/postpay/drafts/{draft_id}/freeze')
        async def original_freeze(draft_id:str,request:Request,
                x_booth_id:str=Header(default=''),authorization:str=Header(default='')):
            booth=identity(request,x_booth_id,authorization)
            command=await body(request,FreezeRequest)
            return await invoke(freeze_call,DraftLease(draft_id,booth,command.visit_id,command.generation),command)

    if protected_isolation is not None:
        def original_operation(operation,booth,owner=None):
            with payments.ledger.write():
                row=payments.ledger.db.execute('''SELECT o.*,d.visit_id FROM pp_isolation_ops o
                    JOIN pp_drafts d USING(draft_id) WHERE o.operation_id=? AND o.booth_id=?''',
                    (operation,booth)).fetchone()
                if (not row or owner is not None and
                        (row['visit_id']!=owner.visit_id or row['original_generation']!=owner.generation)):
                    raise DraftHeld('Exact original release operation required')
                return dict(kind='ORIGINAL_ISOLATION',operation_id=operation,booth_id=booth,
                    draft_id=row['draft_id'],visit_id=row['visit_id'],generation=row['original_generation'],
                    state=row['state'],mode=payments.mode,order_version=ORDER_VERSION)

        @app.post('/api/postpay/drafts/{draft_id}/isolation/prepare')
        async def isolation_prepare(draft_id: str,request:Request,
                x_booth_id: str=Header(default=''),authorization: str=Header(default='')):
            booth=identity(request,x_booth_id,authorization)
            owner=await body(request,OwnerRequest)
            if worker_generations is not None:
                await invoke(worker_generations.require_retired,
                             DraftLease(draft_id,booth,owner.visit_id,owner.generation))
            operation=await invoke(protected_isolation.prepare,booth,
                expected_owner=DraftLease(draft_id,booth,owner.visit_id,owner.generation))
            return await invoke(original_operation,operation,booth,owner)

        @app.post('/api/postpay/isolation/{operation}/ack')
        async def isolation_ack(operation: str,request:Request,
                x_booth_id: str=Header(default=''),authorization: str=Header(default='')):
            booth=identity(request,x_booth_id,authorization)
            owner=await body(request,OwnerRequest)
            original=await invoke(original_operation,operation,booth,owner)
            if recovery_authority is not None:
                await invoke(recovery_authority.require,operation,
                    DraftLease(original['draft_id'],booth,owner.visit_id,owner.generation))
            if worker_generations is not None:
                await invoke(worker_generations.require_retired,DraftLease(
                    original['draft_id'],booth,owner.visit_id,owner.generation))
            await invoke(protected_isolation.acknowledge,booth,operation)
            return await invoke(original_operation,operation,booth,owner)

        @app.post('/api/postpay/groups/{group}/claim')
        async def original_claim(group: str,request:Request,
                x_booth_id: str=Header(default=''),authorization: str=Header(default='')):
            booth=identity(request,x_booth_id,authorization)
            command=await body(request,ClaimRequest)
            try:
                result=await run_in_threadpool(protected_claim.claim_once,command.request_id,group,booth,command.proof)
            except PermissionError:
                raise HTTPException(403,'Original private customer proof required') from None
            except DraftHeld:
                raise HTTPException(409,'Original claim is held') from None
            except ValueError:
                raise HTTPException(422,'Invalid request') from None
            except Exception:
                raise HTTPException(503,'Original claim temporarily unavailable') from None
            base=dict(kind='ORIGINAL_CLAIM',request_id=command.request_id,purchase_group_id=group,
                      booth_id=booth,mode=payments.mode,order_version=ORDER_VERSION,state=result['state'])
            if result['state']=='WAIT':
                return dict(base,reason='BOOTH_BUSY')
            lease=result['lease']
            return dict(base,lease=dict(draft_id=lease.draft_id,booth_id=lease.booth_id,
                visit_id=lease.visit_id,generation=lease.generation),entitlement_id=result['entitlement_id'],
                service_still_owed=True)

    if paid_delivery is not None:
        @app.post('/api/postpay/groups/{group}/delivery/{action}')
        async def delivery(group: str, action: Literal['prepare','status','print-next'], request: Request,
                           x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
            booth=identity(request,x_booth_id,authorization)
            owner=await body(request,OwnerRequest)
            token=await invoke(lease,group,booth,owner)
            function={'prepare':paid_delivery.prepare,'status':paid_delivery.inspect,
                      'print-next':paid_delivery.print_next}[action]
            status=await invoke(function,group,token)
            return dict(kind='PAID_DELIVERY',purchase_group_id=group,booth_id=booth,
                generation=owner.generation,action=action,mode=payments.mode,
                order_version=ORDER_VERSION,delivery=status)

    if ccp_presentation is not None:
        @app.post('/api/postpay/groups/{group}/ccp/offer')
        async def ccp_offer(group: str, request: Request, x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
            booth = identity(request, x_booth_id, authorization)
            owner = await body(request, OwnerRequest)
            token = await invoke(lease, group, booth, owner)
            offer = await invoke(ccp_presentation.offer, group, token)
            return dict(kind='CCP', purchase_group_id=group, booth_id=booth,
                generation=offer.generation, presentation_id=offer.presentation_id,
                qr_payload=offer.qr_payload, mode=payments.mode, order_version=ORDER_VERSION)

        @app.post('/api/postpay/groups/{group}/ccp/{action}')
        async def ccp_ack(group: str, action: Literal['visible', 'retire'], request: Request,
                          x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
            booth = identity(request, x_booth_id, authorization)
            owner = await body(request, PresentationRequest)
            token = await invoke(lease, group, booth, owner)
            function = ccp_presentation.visible if action == 'visible' else ccp_presentation.retire
            await invoke(function, group, token, owner.presentation_id)
            return dict(kind='CCP', purchase_group_id=group, booth_id=booth,
                generation=owner.generation, presentation_id=owner.presentation_id,
                action=action, mode=payments.mode, order_version=ORDER_VERSION)

    if ticket_presentation is not None:
        @app.post('/api/postpay/groups/{group}/ticket/offer')
        async def ticket_offer(group: str, request: Request, x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
            booth = identity(request, x_booth_id, authorization)
            owner = await body(request, OwnerRequest)
            token = await invoke(lease, group, booth, owner)
            offer = await invoke(ticket_presentation.offer, group, token)
            return dict(kind='RECOVERY', purchase_group_id=group, booth_id=booth,
                generation=offer.generation, presentation_id=offer.presentation_id,
                qr_payload=offer.qr_payload, mode=payments.mode, order_version=ORDER_VERSION)

        @app.post('/api/postpay/groups/{group}/ticket/{action}')
        async def ticket_ack(group: str, action: Literal['visible', 'dismiss', 'retire', 'receipt'], request: Request,
                             x_booth_id: str = Header(default=''), authorization: str = Header(default='')):
            booth = identity(request, x_booth_id, authorization)
            owner = await body(request, PresentationRequest)
            token = await invoke(lease, group, booth, owner)
            if action == 'receipt':
                result = await invoke(ticket_presentation.receipt, group, token, owner.presentation_id)
                return dict(result, kind='RECOVERY', purchase_group_id=group, booth_id=booth,
                    generation=owner.generation, presentation_id=owner.presentation_id,
                    action=action, mode=payments.mode, order_version=ORDER_VERSION)
            function = {'visible': ticket_presentation.visible,
                        'dismiss': ticket_presentation.dismiss,
                        'retire': ticket_presentation.retire}[action]
            await invoke(function, group, token, owner.presentation_id)
            return dict(kind='RECOVERY', purchase_group_id=group, booth_id=booth,
                generation=owner.generation, presentation_id=owner.presentation_id,
                action=action, mode=payments.mode, order_version=ORDER_VERSION)

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
