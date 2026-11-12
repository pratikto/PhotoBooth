"""Trusted launcher-only original visit manager, never a GUI/provider adapter.

Blocking methods belong on a serialized launcher worker. GUI code may receive
only NativeVisitBinding, which contains the existing native service/PhotoJobs.
This core does not mount customer controls, freeze checkout or adopt boot media.
"""
from dataclasses import dataclass
import hashlib
import re
import socket
import threading
import uuid

from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.kiosk_v2.post_preview_protected_checkout import ProtectedCheckoutService
from photobooth.kiosk_v2.recovery import LaunchLease,checked_path
from photobooth.post_preview_authority import OriginalWorkerReadiness
from photobooth.post_preview_bootstrap import SandboxBackendProcess
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_handoff_client import PostPreviewHandoffClient
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment,validate_original_printer_config
from photobooth.post_preview_isolation import OriginalMockIsolation
from photobooth.post_preview_readiness import LocalChargeReadiness
from photobooth.post_preview_readiness_bridge import WorkerReadinessServer
from photobooth.post_preview_sandbox_handoff import require_acked_worker_receipt
from photobooth.post_preview_store import DraftHeld,DraftLease
from photobooth.post_preview_worker_fence import WorkerFenceKey,NativeWorkerRetirement
from photobooth.post_preview_visit_history import require_free_visit_history,review_before_original_worker
from photobooth.printer import PrinterConfig

_RETIRE_EVENTS=frozenset({'USER_CANCEL','APP_SUSPENDED','INACTIVITY_EXPIRED',
                          'VISIT_ABANDONED','RESULT_TIMEOUT'})


@dataclass(frozen=True)
class NativeVisitBinding:
    service: ProtectedCheckoutService
    jobs: PhotoJobs
    epoch: int


class OriginalSandboxVisits:
    def __init__(self,config,printer_config,legacy,*,camera,qr_loader,printer_dial=None,
                 durable_worker_epochs=False):
        if (type(config) is not SandboxHostConfig or type(printer_config) is not PrinterConfig
                or type(legacy) is not CheckoutStore or not callable(qr_loader)
                or printer_dial is not None and not callable(printer_dial)
                or type(durable_worker_epochs) is not bool):
            raise DraftHeld('Exact trusted original launcher dependencies required')
        validate_original_printer_config(printer_config)  # No key minted for validation.
        self._config,self._printer,self._legacy=config,printer_config,legacy
        self._camera,self._qr_loader,self._dial=camera,qr_loader,printer_dial
        self._durable_worker_epochs=durable_worker_epochs
        self._lock=threading.RLock()
        self._launcher=LaunchLease(config.private_root)
        self._backend=self._client=self._service=self._jobs=self._server=None
        self._native=self._handoff=self._key=self._release=None
        self._acked=False
        self._epoch=0
        self._binding=None
        self._admitted=self._closed=self._stopping=False
        self._closing=self._opening=False
        self._empty_rotating=False
        self._pending_claim=None  # request/group/proof hash/epoch only, never raw proof.

    def __repr__(self):
        return '<OriginalSandboxVisits: trusted private launcher; not a GUI service>'

    @property
    def ledger(self):
        if self._service is None:
            raise DraftHeld('Original native ledger unavailable')
        return self._service.ledger

    # The original method only classifies existing ledger finance/output. No
    # mock constructor, payment object, fixture flag or provider is constructed.
    _financial=OriginalMockIsolation._financial

    def _active(self):
        if self._closed or self._stopping or self._launcher.stream.closed:
            raise DraftHeld('Original trusted visit manager is stopping')

    def _free_history(self):
        with self.ledger.write():
            require_free_visit_history(self.ledger.db,self._config.booth_id)

    def _open(self):
        if self._backend is not None or self._service is not None:
            raise DraftHeld('Original child/native handles must finish first')
        if not self._durable_worker_epochs:
            try:
                durable=any(checked_path(self._config.private_root/name).exists()
                    for name in ('worker-custody','worker-recoveries'))
            except (OSError,ValueError):
                raise DraftHeld('Original durable worker history cannot downgrade to ephemeral startup') from None
            if durable: raise DraftHeld('Original durable worker history cannot downgrade to ephemeral startup')
        if self._durable_worker_epochs:
            from photobooth.post_preview_worker_epochs import review_eligible_worker_history
            review_eligible_worker_history(self._launcher,self._config)
        else:
            review_before_original_worker(self._launcher,self._config)
        self._key=WorkerFenceKey.create()
        if self._durable_worker_epochs:
            from photobooth.post_preview_worker_epochs import write_eligible_worker_escrow
            write_eligible_worker_escrow(self._launcher,self._config,self._key)
        fulfillment=SandboxHostFulfillment(self._printer,self._key,self._durable_worker_epochs)
        worker,child=socket.socketpair()
        self._backend=SandboxBackendProcess(self._config,fulfillment=fulfillment,
                                           worker_launcher=self._launcher)
        try:
            endpoint=self._backend.start(child)
            self._client=PostPreviewClient(endpoint,self._config.booth_id,self._config.booth_token,
                expected_mode='sandbox',allow_local_http=True)
            self._client._transport.session.trust_env=False  # Original authenticated loopback only.
            self._service=ProtectedCheckoutService(self._config.private_root,
                payment_client=self._client,qr_loader=self._qr_loader,
                require_worker_binding=self._durable_worker_epochs)
            self._jobs=PhotoJobs(self._service)
            ownership=OriginalWorkerReadiness(self._service,self._jobs,self._launcher,self._legacy)
            from photobooth.catalog import get_templates
            collector=LocalChargeReadiness(self._service.checkout,get_templates(),
                probes={'worker_ownership':ownership},camera=self._camera,
                printer_config=self._printer,printer_dial=self._dial)
            self._server=WorkerReadinessServer.from_original_worker(worker,collector)
            self._server.start()
            self._native=NativeWorkerRetirement(self._jobs,self._server,self._launcher,self._key)
            self._handoff=PostPreviewHandoffClient(self._client)
            self._release=None;self._acked=False
            self._epoch+=1
            self._binding=NativeVisitBinding(self._service,self._jobs,self._epoch)
        except Exception:
            if self._server is None:worker.close()
            # Retain all possibly live original handles for stop(), never kill.
            raise DraftHeld('Original protected visit startup held') from None
        finally:child.close()

    def start(self):
        with self._lock:
            self._active()
            if self._backend is not None:
                raise DraftHeld('Original trusted manager already started')
            self._open()
            # A boot owner has no tokenless restore path in this first scope.
            self._free_history()
            self._admitted=True
            return self._binding

    def _accepted_release(self):
        with self.ledger.write():
            operation=self.ledger.db.execute('SELECT * FROM pp_isolation_ops WHERE operation_id=?',
                                           (self._release.operation_id,)).fetchone()
            lease=self._service.lease
            draft=self.ledger.db.execute('SELECT * FROM pp_drafts WHERE draft_id=?',
                                         (lease.draft_id,)).fetchone()
            if (not operation or not draft or operation['booth_id']!=lease.booth_id
                    or operation['draft_id']!=lease.draft_id
                    or operation['original_generation']!=lease.generation+1
                    or not draft['closed'] or draft['lifecycle']!='ISOLATED'
                    or draft['generation']!=lease.generation+2):
                raise DraftHeld('Original accepted release generation changed')
            require_acked_worker_receipt(self.ledger,operation)

    def _release_ack_is_durable(self):
        if self._release is None:return False
        with self.ledger.write():
            operation=self.ledger.db.execute('SELECT state FROM pp_isolation_ops WHERE operation_id=?',
                                             (self._release.operation_id,)).fetchone()
            accepted=bool(operation and operation['state']=='ACKED')
        if accepted:self._accepted_release()
        return accepted

    def _close_handles(self):
        """Actual collector/file/child exit before any original ledger close."""
        if self._server is not None and not self._server.stop(timeout=0):return False
        if self._jobs is not None and not self._jobs.retire(timeout=0):return False
        if self._backend is not None:
            if not self._backend.stop(timeout=.2):return False
            if self._backend.process is not None and self._backend.process.poll() is None:return False
        if self._service is not None:
            self._service.close();self._service.wait_closed(1)
            if self._service._cleanup_thread.is_alive():return False
        if self._client is not None:self._client.close()
        if self._handoff is not None:self._handoff.hide_private()
        self._backend=self._client=self._service=self._jobs=self._server=None
        self._native=self._handoff=self._key=self._release=None
        self._binding=None;self._acked=False
        return True

    def _ack_retired(self):
        """Reuse exact original handoff; no new visitor or child is created."""
        service=self._service;lease=service.lease if service is not None else None
        if lease is None or not service._hidden.is_set() or service.phase!='hold':
            raise DraftHeld('Original retired owner required')
        if not self._closing and not self._acked:
            if not self._server.stop(timeout=0) or not self._jobs.retire(timeout=0):
                raise DraftHeld('Original collector/photo worker is still active')
            if self._release is None:
                retired=DraftLease(lease.draft_id,lease.booth_id,lease.visit_id,lease.generation+1)
                self._release=self._handoff.prepare(retired)
            with self.ledger.write():
                operation=self.ledger.db.execute('SELECT state FROM pp_isolation_ops WHERE operation_id=?',
                    (self._release.operation_id,)).fetchone()
            if operation and operation['state']=='ACKED':
                self._accepted_release()  # Lost reply, never republish a PREPARED receipt.
            else:
                self._native.publish(self._release.operation_id,timeout=0)
            self._release=self._handoff.acknowledge(self._release)
            self._acked=True
        if not self._closing:
            self._accepted_release()
            self._closing=True

    def finish_for_shutdown(self):
        """Trusted serialized normal exit only; uncertain original state holds."""
        with self._lock:
            self._active()
            if not self._admitted:
                raise DraftHeld('Original admitted same-process owner required')
            if self._closing or self._opening or self._empty_rotating:
                # These private flags witness an already accepted same-process
                # transition. Its old SQL handle can be closed; do not reopen a
                # child or query that dead context merely to finish shutdown.
                return True
            if self._service is None:raise DraftHeld('Original shutdown context unavailable')
            service=self._service
            if not service._hidden.is_set() or service.phase!='hold':
                raise DraftHeld('Original immediate privacy retirement required')
            if not self._server.stop(timeout=0) or not self._jobs.retire(timeout=0):
                raise DraftHeld('Original native workers must actually finish')
            if service.lease is None:
                self._free_history()  # Empty owner cannot invent a release.
            else:
                self._ack_retired()
            return True

    def retire_for_shutdown(self,event):
        """Opt-in trusted stop: finish exact accepted ACK, never rotate/repaint."""
        if event not in _RETIRE_EVENTS:raise ValueError('Original privacy retirement event required')
        with self._lock:
            self._active()
            if not self._admitted:raise DraftHeld('Original admitted shutdown required')
            if self._closing or self._opening or self._empty_rotating:
                if self._service is not None:self._service.hide_private()
                return {'phase':'hold'}
            if self._acked:
                self._accepted_release()
                return {'phase':'hold'}
            if self._release_ack_is_durable():return {'phase':'hold'}
            return self.retire_current(event)

    def ensure_new_visitor_ready(self):
        with self._lock:
            self._active()
            if self._empty_rotating:
                if not self._close_handles():
                    raise DraftHeld('Original empty private worker is still stopping')
                self._opening=True
                self._open();self._opening=False;self._empty_rotating=False
                self._free_history()
                return self._binding
            if self._opening and self._admitted:
                if not self._close_handles():
                    raise DraftHeld('Original attempted child startup is still stopping')
                self._open();self._opening=False
            if not self._admitted or self._service is None:
                raise DraftHeld('Original supported start required')
            if self._service.lease is None and not self._service._hidden.is_set():
                thread=self._jobs._thread
                if (self._jobs._closed or self._jobs.busy
                        or thread is not None and thread.is_alive()):
                    raise DraftHeld('Original native command is still active')
                self._free_history()
                return self._binding
            service=self._service;lease=service.lease
            if lease is None and service._hidden.is_set():
                thread=self._jobs._thread
                if self._jobs.busy or thread is not None and thread.is_alive():
                    raise DraftHeld('Original empty private command is still active')
                # No current owner means no customer release may be invented.
                # Old released history is still independently verified.
                self._free_history()
                self._empty_rotating=True
                return self.ensure_new_visitor_ready()
            if lease is None or not service._hidden.is_set() or service.phase!='hold':
                raise DraftHeld('Original live visitor cannot be preempted')
            # Durable retirement must already have run on the original worker.
            self._ack_retired()
            if not self._close_handles():
                raise DraftHeld('Original child/native handles are still stopping')
            self._closing=False;self._opening=True
            self._open();self._opening=False
            self._free_history()
            return self._binding

    def _claim_request(self,group,payload,*,allow_reacquired=True):
        proof_hash=hashlib.sha256(payload.encode()).hexdigest()
        with self.ledger.write():
            owner=self.ledger.db.execute('SELECT * FROM pp_drafts WHERE booth_id=? AND closed=0',
                                         (self._config.booth_id,)).fetchone()
            requests=list(self.ledger.db.execute('''SELECT * FROM pp_protected_claim_ops
                WHERE booth_id=? AND purchase_group_id=? AND proof_sha256=? ORDER BY created_at DESC''',
                (self._config.booth_id,group,proof_hash)))
            for request in requests:
                if (allow_reacquired and request['state']=='REACQUIRED' and owner and owner['lifecycle']=='ACTIVE'
                        and (owner['draft_id'],owner['visit_id'],owner['generation'])==
                        (request['draft_id'],request['visit_id'],request['generation'])):
                    self._pending_claim=(request['request_id'],group,proof_hash,self._epoch)
                    return request['request_id']
            prepared=next((r for r in requests if r['state']=='PREPARED'),None)
            identity=prepared['request_id'] if prepared else uuid.uuid4().hex
            self._pending_claim=(identity,group,proof_hash,self._epoch)
            return identity

    def recover_paid(self,payload):
        """Trusted worker only; returned binding/snapshot contains no raw proof."""
        with self._lock:
            self._active()
            if not self._admitted:
                raise DraftHeld('Supported original start required before proof claim')
            if type(payload) is not str or len(payload)>256:
                raise PermissionError('Original private customer proof required')
            match=re.fullmatch(r'MEONG:(?:CCP|RECOVERY):1:'+re.escape(self._config.booth_id)
                               +r':([a-f0-9]{32}):[A-Za-z0-9_-]{43}',payload)
            if match is None:raise PermissionError('Original customer proof role required')
            if self._opening:self.ensure_new_visitor_ready()
            if self._service is None:raise DraftHeld('Original native claim context unavailable')
            service=self._service;group=match.group(1)
            if service._hidden.is_set() and (self._acked or self._closing or self._release_ack_is_durable()):
                # Finish ONLY the already accepted close/open. Its old HTTP or
                # SQLite handle may have closed. New backend proof verification
                # below remains mandatory before any original media restore.
                self.ensure_new_visitor_ready()
                service=self._service
            thread=self._jobs._thread
            if (self._jobs.busy or thread is not None and thread.is_alive()
                    or self._jobs._closed and not service._hidden.is_set()):
                return dict(state='WAIT',reason='BOOTH_BUSY')
            if service.lease is not None and not service._hidden.is_set():
                request=self._claim_request(group,payload,allow_reacquired=False)
                if self._handoff.claim(group,payload,request) is not None:
                    service.hide_private()
                    raise DraftHeld('Original live claim owner changed')
                return dict(state='WAIT',reason='BOOTH_BUSY')
            request=self._claim_request(group,payload)
            if service._hidden.is_set():
                # Backend proof verification MUST precede release of a retired
                # owner. This separate observation can never restore pixels.
                if self._handoff.claim(group,payload,request) is not None:
                    raise DraftHeld('Original retired claim context changed')
                self.ensure_new_visitor_ready()
                service=self._service
            # Rotation may have replaced the original facade/epoch after proof
            # preflight. Remember only this actual request on the CURRENT one.
            self._pending_claim=(request,group,hashlib.sha256(payload.encode()).hexdigest(),self._epoch)
            view=service.claim_original(group,payload,request)
            if view.get('state')=='WAIT':return view
            return dict(state='RESTORED',snapshot=view,binding=self._binding,purchase_group_id=group)

    def review_remedy(self,payload,reason,request_id):
        """Nonbinding CASE only; no visit claim/rotation/retirement or media."""
        with self._lock:
            self._active()
            if not self._admitted or self._client is None:
                raise DraftHeld('Original review backend is unavailable')
            match=re.fullmatch(r'MEONG:(?:CCP|RECOVERY):1:'+re.escape(self._config.booth_id)
                +r':([a-f0-9]{32}):[A-Za-z0-9_-]{43}',payload) if type(payload) is str else None
            if match is None:raise PermissionError('Original private customer proof required')
            from photobooth.post_preview_remedy_client import PostPreviewRemedyClient
            return PostPreviewRemedyClient(self._client).review(request_id,match.group(1),payload,reason)

    def retire_current(self,event):
        """Trusted worker: retire current metadata after immediate GUI hide.

        A late claim can commit occupancy before its hidden/lost HTTP response.
        Only our exact pending durable REACQUIRED operation may supply its lease
        for retirement; no media/credential is read or grant reconstructed.
        Unknown boot/foreign owners remain held. This method never ACKs/FREEs.
        """
        if event not in _RETIRE_EVENTS:
            raise ValueError('Original privacy retirement event required')
        with self._lock:
            self._active()
            # Privacy can interrupt an already accepted release while its old
            # SQL handle is closing. Finish only that original transition
            # before inspecting the current owner; never query the dead handle.
            if self._closing or self._acked or self._opening or self._empty_rotating:
                self.ensure_new_visitor_ready()
            service=self._service
            if service is None:
                raise DraftHeld('Original native context unavailable')
            service.hide_private()
            collector_done=self._server.stop(timeout=0)
            jobs_done=self._jobs.retire(timeout=0)
            if not collector_done or not jobs_done:
                raise DraftHeld('Original collector/native command must drain before retirement')
            with self.ledger.write():
                owner=self.ledger.db.execute('SELECT * FROM pp_drafts WHERE booth_id=? AND closed=0',
                                             (self._config.booth_id,)).fetchone()
                if service.lease is None and owner is not None:
                    pending=self._pending_claim
                    request=(self.ledger.db.execute('SELECT * FROM pp_protected_claim_ops WHERE request_id=?',
                        (pending[0],)).fetchone() if pending and pending[3]==self._epoch else None)
                    if (not request or request['state']!='REACQUIRED'
                            or (request['purchase_group_id'],request['proof_sha256'])!=(pending[1],pending[2])
                            or (request['draft_id'],request['booth_id'],request['visit_id'],request['generation'])
                               !=(owner['draft_id'],owner['booth_id'],owner['visit_id'],owner['generation'])
                            or owner['lifecycle']!='ACTIVE'):
                        raise DraftHeld('Original exact pending claim owner required')
                    release=self.ledger.db.execute('SELECT * FROM pp_isolation_ops WHERE operation_id=?',
                                                   (request['release_operation'],)).fetchone()
                    if (not release or release['draft_id']!=owner['draft_id']
                            or release['booth_id']!=owner['booth_id']
                            or release['original_generation']+2!=owner['generation']):
                        raise DraftHeld('Original pending claim worker evidence changed')
                    require_acked_worker_receipt(self.ledger,release)
                    finance=self.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance '
                        'WHERE purchase_group_id=?',(pending[1],)).fetchone()
                    if not finance or finance['entitlement_id']!=request['entitlement_id']:
                        raise DraftHeld('Original pending claim identity changed')
                    service.lease=DraftLease(owner['draft_id'],owner['booth_id'],owner['visit_id'],owner['generation'])
                    service.group=pending[1]
                lease=service.lease
                if lease is None:
                    service.phase='hold'
                    return {'phase':'hold'}
                if (not owner or (owner['draft_id'],owner['visit_id'])!=(lease.draft_id,lease.visit_id)):
                    raise DraftHeld('Original current native owner changed')
                if owner['lifecycle']!='ACTIVE':
                    if owner['generation']!=lease.generation+1:
                        raise DraftHeld('Original retirement generation changed')
                    service.phase='hold'
                    return {'phase':'hold'}  # Preserve the FIRST durable retirement reason.
                if owner['generation']!=lease.generation:
                    raise DraftHeld('Original current native generation changed')
            return service.retire(event)

    def stop(self):
        with self._lock:
            if self._closed:return True
            self._stopping=True
            if self._service is not None:self._service.hide_private()
            if self._server is not None and not self._server.stop(timeout=0):return False
            if self._jobs is not None and not self._jobs.retire(timeout=0):return False
            service=self._service
            if service is not None and service.lease is not None and not service._closed.is_set():
                with self.ledger.write():
                    row=self.ledger.db.execute('SELECT * FROM pp_drafts WHERE draft_id=?',
                                               (service.lease.draft_id,)).fetchone()
                    live=(row and not row['closed'] and row['lifecycle']=='ACTIVE'
                          and row['generation']==service.lease.generation)
                if live:service.retire('APP_SUSPENDED')
            if not self._close_handles():return False
            self._launcher.close();self._closed=True;self._admitted=False
            return True
