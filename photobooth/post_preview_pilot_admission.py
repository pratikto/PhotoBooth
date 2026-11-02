"""Explicit MOCK-only original customer handoff for supervised Windows pilot.

A public advertising page is NOT a financial admission. Old protected visits
must be durably PREPARED and ACKED before the next customer's draft; valid
proof may reacquire the old paid obligation only if the booth is truly free.
This module does not issue a charge, print, upload, refund or customer token.
"""
import re
import threading

from photobooth.kiosk_v2.photos import PhotoJobs
from photobooth.post_preview_claim import OriginalMockClaim
from photobooth.post_preview_isolation import OriginalMockIsolation
from photobooth.post_preview_store import DraftHeld


class OriginalPilotAdmission:
    """One gate shared by Photo, Meong Fly and original customer claim."""

    def __init__(self, isolation, claim, *, allow_synthetic_pilot=False):
        if (allow_synthetic_pilot is not True or
                not isinstance(isolation,OriginalMockIsolation) or
                not isinstance(claim,OriginalMockClaim) or
                isolation.payments is not claim.payments or
                isolation.ledger is not claim.ledger or
                not isinstance(isolation.jobs,PhotoJobs) or
                isolation.jobs.service is None or
                isolation.jobs.service.ledger is not claim.ledger):
            raise DraftHeld('Exact supervised MOCK-only admission coordinator required')
        self.isolation,self.claim=isolation,claim
        self.jobs=isolation.jobs
        self._lock=threading.RLock()

    def ensure_new_visitor_ready(self):
        """Fail closed on ambiguous provider, old print/Drive, live customer."""
        with self._lock:
            service=self.jobs.service
            if self.jobs.busy:
                raise DraftHeld('Original worker is still processing old customer')
            if service.lease is None:
                with self.claim.ledger.write():
                    active=self.claim.ledger.db.execute(
                        'SELECT 1 FROM pp_drafts WHERE booth_id=? AND closed=0',
                        (service.booth_id,)).fetchone()
                    if active:
                        raise DraftHeld('Original booth has an unresolved customer')
                return True
            if not service._hidden.is_set():
                raise DraftHeld('Live customer cannot be preempted')
            old=service.lease
            # Crash/reply-loss recovery is bound to the very same operation.
            with self.claim.ledger.write():
                rows=list(self.claim.ledger.db.execute('''SELECT * FROM pp_isolation_ops
                    WHERE draft_id=? AND original_generation=?''',
                    (old.draft_id,old.generation)))
            if len(rows)>1:
                raise DraftHeld('Conflicting original isolation operation')
            if rows:
                operation=rows[0]['operation_id']
                if rows[0]['state']=='PREPARED':
                    self.isolation.acknowledge(service.booth_id,operation)
                elif rows[0]['state']!='ACKED':
                    raise DraftHeld('Unclassified old session isolation')
            else:
                operation=self.isolation.prepare(service.booth_id)
                self.isolation.acknowledge(service.booth_id,operation)
            service.reset_after_acked_isolation(operation)
            return True

    def recover_paid(self, qr_payload):
        """Return original paid *snapshot* only with original proof and free booth.

        A proof valid for a still-active protected visit may first safely
        isolate THAT retired occupancy. A live other customer remains WAIT.
        QR payload is never stored, logged, sent to cloud or echoed to the UI.
        """
        if not isinstance(qr_payload,str) or len(qr_payload)>256:
            raise PermissionError('Original customer proof required')
        booth=self.jobs.service.booth_id
        match=re.fullmatch(
            r'MEONG:(?:CCP|RECOVERY):1:'+re.escape(booth)
            +r':([a-f0-9]{32}):[A-Za-z0-9_-]{43}',
            qr_payload)
        # Actual issued proof order is booth:GROUP:RANDOM43;
        # do not infer authorization from this syntactic match.
        if match is None:
            raise PermissionError('Original customer proof role or scope invalid')
        group=match.group(1)
        with self._lock:
            if self.jobs.busy:
                return {'state':'WAIT','reason':'BOOTH_BUSY'}
            result=self.claim.claim(group,booth,qr_payload)
            if result['state']=='WAIT':
                service=self.jobs.service
                if service.lease is None or not service._hidden.is_set():
                    return {'state':'WAIT','reason':'BOOTH_BUSY'}
                self.ensure_new_visitor_ready()
                result=self.claim.claim(group,booth,qr_payload)
            if result['state']!='REACQUIRED':
                return {'state':'WAIT','reason':'BOOTH_BUSY'}
            restored=self.jobs.service.recover_original_owed(result['lease'],group)
            return {'state':'RESTORED','snapshot':restored,'purchase_group_id':group}
