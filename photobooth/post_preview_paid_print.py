"""Backend-owned original paid strip dispatch over the existing ThermalPrinter API.

One paid design yields one immutable ESC/POS submission for ALL purchased copies.
Physical paper is not proven by a successful transport ACK. Persist SENDING
before irreversible I/O; timeouts or restart never replay a possible print.
The same external lock must serialize the original Recovery Ticket and strips.
"""
import json
from pathlib import Path
import threading

from photobooth.booth_storage import checked_path
from photobooth.capture_journal import validate_image
from photobooth.manifest_io import manifest_lock
from photobooth.post_preview_paid_strips import OriginalPaidStripPreparer
from photobooth.post_preview_store import DraftHeld


class OriginalPaidPrintDispatcher:
    def __init__(self,preparer,*,allow_incomplete_fixture=False):
        from photobooth.post_preview_sandbox_delivery import original_paid_core_allowed
        if (type(preparer) is not OriginalPaidStripPreparer
                or not original_paid_core_allowed(preparer.binder,allow_incomplete_fixture)):
            raise DraftHeld('Exact original paid print authority required')
        self.preparer=preparer
        self.binder=preparer.binder
        self._lock=threading.RLock()

    def send_once(self,lease,group,template_id,printer,*,shared_lane):
        """Send at most ONE original purchased strip job, no automatic retries.

        The source customer must have truly seen and dismissed the original
        ticket, and the original ticket receipt lane must no longer be sending.
        Only the owned worker may call this shared core; callers cannot select
        another backend receipt printer or thermal lane.
        """
        from photobooth.post_preview_sandbox_delivery import OriginalSandboxPaidDriveBinding
        if type(self.binder) is OriginalSandboxPaidDriveBinding:
            self.binder.require_printer_lane(printer,shared_lane)
        with self._lock,self.preparer._lock,self.binder._lock:
            with self.binder.ledger.write():
                service,_=self.binder._record(lease,group)
                if (service['drive_state'] not in {'VERIFIED','UPLOADED'} or service['status']!='OWED'
                        or not service['transaction_id'] or not service['folder_id']):
                    raise DraftHeld('Original paid Drive/fulfillment evidence required')
                presentation=self.binder.ledger.db.execute(
                    'SELECT * FROM pp_ticket_presentations WHERE purchase_group_id=?',
                    (group,)).fetchone()
                if (presentation is None or presentation['screen_state']!='DISMISSED'
                        or presentation['receipt_state'] in {'PREPARED','SENDING','UNCERTAIN'}):
                    raise DraftHeld('Original Recovery Ticket presentation is incomplete')
                # Defense in depth: direct dispatchers, retired workers or a
                # second dispatcher instance must not bypass the kiosk-level
                # quarantine. This is a durable per-purchase gate, not a UI flag.
                uncertain=self.binder.ledger.db.execute(
                    "SELECT template_id FROM pp_paid_strip_jobs "
                    "WHERE purchase_group_id=? AND state IN ('SENDING','UNCERTAIN') "
                    "LIMIT 1",(group,)).fetchone()
                if uncertain is not None:
                    raise DraftHeld('Original paid print pipeline has unclassified paper; hold all batches')
                job=self.binder.ledger.db.execute('''SELECT * FROM pp_paid_strip_jobs
                    WHERE purchase_group_id=? AND template_id=?''',(group,template_id)).fetchone()
                if job is None or job['state']!='PREPARED':
                    raise DraftHeld('Original paid strip is not eligible for repeat dispatch')
                relative=Path(job['output_path'])
                if (relative.is_absolute() or '..' in relative.parts
                        or relative.as_posix()!=f'Photo/{self._ordinal(group,template_id):02d}/color/strip.png'):
                    raise DraftHeld('Original paid strip path is not authorized')
                file=checked_path(self.binder.workspace.root/service['transaction_id']/relative)
                validate_image(file,job['output_sha256'],image_format='PNG',
                               expected_size=(640,1920))
                manifest_path=checked_path(
                    self.binder.workspace.root/service['transaction_id']/'manifest.json')
                with manifest_lock(manifest_path):
                    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
                    if (manifest.get('purpose')!='POST_PREVIEW_PAID'
                            or manifest.get('status')!='READY_FOR_PAID_DELIVERY'
                            or manifest.get('transaction_id')!=service['transaction_id']
                            or manifest.get('drive_folder_id')!=service['folder_id']
                            or manifest.get('drive_folder_url')!=service['folder_url']
                            or manifest.get('payment_binding',{}).get('service_id')!=service['service_id']):
                        raise DraftHeld('Original purchased output manifest is not ready')
                status='NOT_SENT' if printer is None or shared_lane is None else 'SENDING'
                self.binder.ledger.db.execute('''UPDATE pp_paid_strip_jobs
                    SET state=?,updated_at=? WHERE purchase_group_id=? AND template_id=?''',
                    (status,self.binder.ledger.now(),group,template_id))
                self.binder.ledger._event(lease.draft_id,'PAID_STRIP_'+status)
                key=job['job_id']
                copies=job['copies']
            if status=='NOT_SENT':
                return {'job_id':key,'state':'NOT_SENT','physical_paper_verified':False}
            # External side effects only after durable SENDING with shared lane.
            outcome='UNCERTAIN'
            try:
                with shared_lane:
                    result=printer.print_image(file,copies=copies)
                if getattr(result,'success',None) is True:
                    outcome='SUBMITTED'
            except Exception:
                outcome='UNCERTAIN'
            with self.binder.ledger.write():
                original=self.binder.ledger.db.execute('''SELECT * FROM pp_paid_strip_jobs
                    WHERE purchase_group_id=? AND template_id=?''',(group,template_id)).fetchone()
                if (original is None or original['job_id']!=key
                        or original['state']!='SENDING'):
                    raise DraftHeld('Original purchased print journal changed while sending')
                self.binder.ledger.db.execute('''UPDATE pp_paid_strip_jobs
                    SET state=?,updated_at=? WHERE purchase_group_id=? AND template_id=?''',
                    (outcome,self.binder.ledger.now(),group,template_id))
                self.binder.ledger._event(lease.draft_id,'PAID_STRIP_'+outcome)
            return {'job_id':key,'state':outcome,'physical_paper_verified':False}

    def _ordinal(self,group,template_id):
        row=self.binder.ledger.db.execute(
            'SELECT transaction_id FROM pp_paid_services WHERE purchase_group_id=?',
            (group,)).fetchone()
        if row is None or not row['transaction_id']:
            raise DraftHeld('Original paid transaction not available')
        path=checked_path(self.binder.workspace.root/row['transaction_id']/'manifest.json')
        with manifest_lock(path):
            manifest=json.loads(path.read_text(encoding='utf-8'))
        matches=[i for i,entry in enumerate(manifest.get('sessions',[]),1)
                 if entry.get('template_id')==template_id]
        if len(matches)!=1:
            raise DraftHeld('Original paid template/print order is not unique')
        return matches[0]
