"""Strict original handoff observations and once-consumed private claim grants.

Only booth credentials enter this adapter. No worker capability, merchant key,
custody protector, printer or FREE/new-admission authority is provided here.
"""
from dataclasses import dataclass,field
import hashlib
import re
import threading
import time

from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_store import DraftHeld,DraftLease,ORDER_VERSION


def _hex(value):
    return type(value) is str and re.fullmatch(r'[a-f0-9]{32}',value) is not None


def _lease(value,booth):
    return (type(value) is DraftLease and value.booth_id==booth and _hex(value.draft_id)
        and type(value.visit_id) is str and re.fullmatch(r'[A-Za-z0-9_-]{1,64}',value.visit_id) is not None
        and type(value.generation) is int and 1<=value.generation<=2147483647)


@dataclass(frozen=True)
class OriginalReleaseObservation:
    operation_id: str
    lease: DraftLease
    state: str


@dataclass(frozen=True,repr=False)
class ProtectedClaimGrant:
    request_id: str
    purchase_group_id: str
    lease: DraftLease
    entitlement_id: str
    proof_sha256: str=field(repr=False)
    observed_at: float=field(repr=False)

    def __repr__(self):
        return '<ProtectedClaimGrant: original scoped result; not new-admission authority>'


class PostPreviewHandoffClient:
    def __init__(self,payments):
        if type(payments) is not PostPreviewClient or payments.mode!='sandbox':
            raise ValueError('Exact original authenticated Sandbox client required')
        self._payments=payments
        self._lock=threading.RLock()
        self._hidden=threading.Event()
        self._operation=self._grant=None

    def _active(self):
        if self._hidden.is_set():
            raise DraftHeld('Original private handoff retired')

    def _call(self,path,payload):
        self._active()
        try:result=self._payments._transport._call('POST',path,payload=payload)
        except Exception:raise DraftHeld('Original protected handoff request held') from None
        self._active()
        return result

    def _release(self,result,lease,operation=None):
        base=dict(kind='ORIGINAL_ISOLATION',booth_id=lease.booth_id,draft_id=lease.draft_id,
            visit_id=lease.visit_id,generation=lease.generation,mode='sandbox',order_version=ORDER_VERSION)
        if (type(result) is not dict or set(result)!=set(base)|{'operation_id','state'}
                or any(type(result[k]) is not type(v) or result[k]!=v for k,v in base.items())
                or not _hex(result['operation_id']) or type(result['state']) is not str
                or result['state'] not in {'PREPARED','ACKED'}
                or operation is not None and result['operation_id']!=operation):
            raise DraftHeld('Original protected release observation changed')
        return OriginalReleaseObservation(result['operation_id'],lease,result['state'])

    def prepare(self,retired_lease):
        with self._lock:
            self._active()
            if not _lease(retired_lease,self._payments.booth_id):
                raise DraftHeld('Exact original retired owner required')
            result=self._call('/api/postpay/drafts/'+retired_lease.draft_id+'/isolation/prepare',
                              self._payments._owner(retired_lease))
            operation=self._release(result,retired_lease)
            if operation.state!='PREPARED':
                raise DraftHeld('Original release preparation required')
            self._active();self._operation=operation
            return operation

    def acknowledge(self,operation):
        with self._lock:
            self._active()
            if type(operation) is not OriginalReleaseObservation or operation is not self._operation:
                raise DraftHeld('Exact original live release observation required')
            result=self._call('/api/postpay/isolation/'+operation.operation_id+'/ack',
                              self._payments._owner(operation.lease))
            accepted=self._release(result,operation.lease,operation.operation_id)
            if accepted.state!='ACKED':
                raise DraftHeld('Original backend worker ACK required')
            self._active();self._operation=accepted
            return accepted  # Observation only; native rotation/admission remains separate.

    def claim(self,group,proof,request_id):
        """Retry the SAME original ID after lost replies; None means busy WAIT."""
        with self._lock:
            self._active();self._grant=None
            booth=self._payments.booth_id
            if (not _hex(group) or not _hex(request_id) or type(proof) is not str
                    or re.fullmatch(r'MEONG:(?:CCP|RECOVERY):1:'+re.escape(booth)+':'+group+
                        r':[A-Za-z0-9_-]{43}',proof) is None):
                raise DraftHeld('Exact original customer claim scope required')
            response=self._call('/api/postpay/groups/'+group+'/claim',
                                dict(request_id=request_id,proof=proof))
            base=dict(kind='ORIGINAL_CLAIM',request_id=request_id,purchase_group_id=group,
                      booth_id=booth,mode='sandbox',order_version=ORDER_VERSION)
            if (type(response) is not dict or not set(base)<=set(response)
                    or any(type(response[k]) is not type(v) or response[k]!=v for k,v in base.items())
                    or type(response.get('state')) is not str):
                raise DraftHeld('Original claim response scope changed')
            if response['state']=='WAIT':
                if response!=dict(base,state='WAIT',reason='BOOTH_BUSY'):
                    raise DraftHeld('Original busy claim response changed')
                return None
            if (response['state']!='REACQUIRED'
                    or set(response)!=set(base)|{'state','lease','entitlement_id','service_still_owed'}
                    or response['service_still_owed'] is not True
                    or not _hex(response['entitlement_id'])
                    or type(response['lease']) is not dict
                    or set(response['lease'])!={'draft_id','booth_id','visit_id','generation'}):
                raise DraftHeld('Original exact owed claim result required')
            lease=DraftLease(**response['lease'])
            if not _lease(lease,booth):
                raise DraftHeld('Original claim lease changed')
            grant=ProtectedClaimGrant(request_id,group,lease,response['entitlement_id'],
                hashlib.sha256(proof.encode()).hexdigest(),time.monotonic())
            self._active();self._grant=grant
            return grant

    def consume(self,grant,restore):
        """Only our exact live response, once, during a bounded local interval."""
        with self._lock:
            self._active()
            if (type(grant) is not ProtectedClaimGrant or grant is not self._grant
                    or not 0<=time.monotonic()-grant.observed_at<=30 or not callable(restore)):
                raise DraftHeld('Exact live original claim grant required')
            self._grant=None
            result=restore(grant)
            self._active()
            if not 0<=time.monotonic()-grant.observed_at<=30:
                raise DraftHeld('Original private claim response expired')
            return result

    def hide_private(self):
        self._hidden.set()  # Immediate even when an original request is blocked.
        self._grant=self._operation=None
