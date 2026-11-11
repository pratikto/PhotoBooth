"""Trusted private opt-in coordinator; SAME original child ACK-only role.

No customer/API caller supplies keys or worker facts. Global owner is retained
until the actual recovery process exits. Missing/uncertain evidence holds; no
new retirement receipt, payment, photo, print, upload or refund is created.
"""
from contextlib import closing
import socket
import sqlite3
import time

from photobooth.kiosk_v2.recovery import LaunchLease,checked_path
from photobooth.post_preview_bootstrap import SandboxBackendProcess
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment
from photobooth.post_preview_interrupted_worker import read_interrupted_worker
from photobooth.post_preview_store import DraftHeld,ORDER_VERSION
from photobooth.post_preview_visit_history import _regular
from photobooth.post_preview_worker_escrow import read_worker_escrow
from photobooth.post_preview_worker_custody import restore_worker_key
from photobooth.printer import PrinterConfig

_HELD='Original interrupted recovery is held'


class OriginalInterruptedRecovery:
    def __init__(self,owner,config,printer):
        from photobooth.post_preview_launch import ProtectedSandboxLaunch
        if (type(owner) is not ProtectedSandboxLaunch or owner._global.stream.closed
                or owner._closed or type(config) is not SandboxHostConfig or type(printer) is not PrinterConfig):
            raise DraftHeld(_HELD)
        self._owner,self._config,self._printer=owner,config,printer
        self._backend=self._client=self._readiness=None
        self._done=False

    def __repr__(self):
        return '<OriginalInterruptedRecovery: private same-operation coordinator>'

    def _candidate(self):
        path=checked_path(self._config.private_root/'drafts.sqlite3')
        if not path.exists(): return None,None
        _regular(path)
        with LaunchLease(self._config.private_root) as native,LaunchLease(
                self._config.private_root/'backend-owner') as backend:
            with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=.2)) as db:
                db.execute('PRAGMA query_only=ON')
                if not db.execute('SELECT 1 FROM pp_drafts WHERE closed=0 LIMIT 1').fetchone():
                    return None,None
            review=read_interrupted_worker(native,backend,self._config)
            stored=read_worker_escrow(native,review.scope.worker_epoch)
            key=restore_worker_key(stored.envelope,review.scope)
            return review,key

    def finish(self,*,timeout):
        try:
            if self._done:return True
            if type(timeout) not in (int,float) or not 0<timeout<=30 or self._owner._global.stream.closed:
                raise ValueError
            deadline=time.monotonic()+timeout
            review,key=self._candidate()
            if review is None:
                self._done=True;return True
            bundle=SandboxHostFulfillment(self._printer,key,recovery_operation=review.operation_id)
            self._backend=SandboxBackendProcess(self._config,fulfillment=bundle,recovery_launcher=self._owner._global)
            self._readiness,child=socket.socketpair()
            try:
                endpoint=self._backend.start(child,timeout=min(15,max(.1,deadline-time.monotonic())))
            finally:child.close()
            self._client=PostPreviewClient(endpoint,self._config.booth_id,self._config.booth_token,
                expected_mode='sandbox',allow_local_http=True,timeout=min(2,max(.2,deadline-time.monotonic())))
            self._client._transport.session.trust_env=False
            lease=review.retired_lease
            expected=dict(kind='ORIGINAL_ISOLATION',operation_id=review.operation_id,
                booth_id=lease.booth_id,draft_id=lease.draft_id,visit_id=lease.visit_id,
                generation=lease.generation,state='ACKED',mode='sandbox',order_version=ORDER_VERSION)
            acknowledged=False
            while time.monotonic()<deadline:
                try:
                    result=self._client._transport._call('POST','/api/postpay/isolation/'+review.operation_id+'/ack',
                        payload=dict(visit_id=lease.visit_id,generation=lease.generation))
                    if (type(result) is not dict or set(result)!=set(expected)
                            or any(type(result[k]) is not type(v) or result[k]!=v for k,v in expected.items())):
                        raise ValueError
                    acknowledged=True;break
                except Exception:
                    if self._backend.process.poll() is not None:break
                    time.sleep(min(.25,max(0,deadline-time.monotonic())))  # SAME bounded idempotent operation only.
            if not acknowledged:
                raise DraftHeld(_HELD)
            while time.monotonic()<deadline:
                if self.stop(timeout=min(.5,deadline-time.monotonic())):
                    self._done=True;return True
            raise DraftHeld(_HELD)
        except Exception:
            # Caller retains this coordinator and actual Popen for original drain.
            raise DraftHeld(_HELD) from None

    def stop(self,*,timeout=.2):
        if self._backend is not None and not self._backend.stop(timeout=max(.05,min(timeout,.5))):
            return False
        if self._client is not None:self._client.close()
        if self._readiness is not None:self._readiness.close()
        self._backend=self._client=self._readiness=None
        return True
