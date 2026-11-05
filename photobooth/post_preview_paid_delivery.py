"""Verified post-preview cloud delivery status, never physical-print proof.

Called only inside the isolated post-preview synthetic worker until the exact
original recovery/booth-release protocol is implemented. Uploads are performed
by the established BoothDriveWorker, not from UI or printer callbacks.
"""
import hashlib
import json
from pathlib import Path
import re
import threading

from photobooth.booth_storage import checked_path
from photobooth.booth_sync import BoothDriveWorker
from photobooth.capture_journal import validate_image
from photobooth.manifest_io import manifest_lock
from photobooth.post_preview_paid_strips import OriginalPaidStripPreparer
from photobooth.post_preview_store import DraftHeld


class OriginalPaidDeliveryMonitor:
    def __init__(self, preparer, *, worker=None, allow_incomplete_fixture=False):
        if (type(preparer) is not OriginalPaidStripPreparer or
                allow_incomplete_fixture is not True or
                (worker is not None and
                 (not isinstance(worker,BoothDriveWorker) or
                  worker.workspace is not preparer.binder.workspace or
                  worker.client is not preparer.binder.client))):
            raise DraftHeld('Exact original post-preview Drive delivery owner required')
        self.preparer=preparer
        self.binder=preparer.binder
        self.worker=worker
        self._lock=threading.RLock()
        self._started=False

    def _owned_manifest(self, lease, group):
        binder=self.binder
        with binder.ledger.write():
            service,contract=binder._record(lease,group)
            if (service['drive_state'] not in {'VERIFIED','UPLOADED'}
                    or not service['transaction_id'] or not service['folder_id']
                    or service['folder_url']!='https://drive.google.com/drive/folders/'+service['folder_id']):
                raise DraftHeld('Original paid Drive viewer binding is not verified')
        manifest_path=checked_path(binder.workspace.root/service['transaction_id']/'manifest.json')
        if not manifest_path.is_file() or manifest_path.stat().st_size>2*1024*1024:
            raise DraftHeld('Original paid delivery manifest is unavailable')
        with manifest_lock(manifest_path):
            manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if (manifest.get('purpose')!='POST_PREVIEW_PAID'
                or manifest.get('transaction_id')!=service['transaction_id']
                or manifest.get('booth_id')!=binder.workspace.booth_id
                or manifest.get('payment_binding',{}).get('service_id')!=service['service_id']
                or manifest.get('payment_binding',{}).get('contract_sha256')!=service['contract_sha256']
                or manifest.get('frozen_order')!=contract
                or manifest.get('drive_folder_id')!=service['folder_id']
                or manifest.get('drive_folder_url')!=service['folder_url']
                or manifest.get('drive_binding_verified') is not True
                or manifest.get('photo_number_layout')!=1
                or manifest.get('paid_media_import_ready') is not True
                or manifest.get('drive_intent') is not True
                or manifest.get('status')!='READY_FOR_PAID_DELIVERY'):
            raise DraftHeld('Original paid delivery media ownership has changed')
        return service,contract,manifest_path,manifest

    @staticmethod
    def _files(manifest_path,manifest):
        files=manifest.get('upload_files')
        if not isinstance(files,dict) or not files or len(files)>100:
            raise DraftHeld('Original paid upload file set is missing or too large')
        verified=0
        for relative, entry in files.items():
            if (not isinstance(relative,str) or not isinstance(entry,dict)
                    or entry.get('path')!=relative
                    or re.fullmatch(r'Photo/\d{2}/(?:raw|color|bw)/[A-Za-z0-9_.-]+',relative) is None
                    or not isinstance(entry.get('content_version'),str)):
                raise DraftHeld('Original paid upload path/revision changed')
            local=checked_path(manifest_path.parent/relative)
            if not local.is_file():
                raise DraftHeld('Original paid file is missing; preserve owed state')
            if entry.get('status')=='VERIFIED':
                remote=entry.get('drive_file_id')
                checksum=entry.get('md5_checksum')
                if (not isinstance(remote,str) or re.fullmatch(r'[A-Za-z0-9_-]+',remote) is None
                        or not isinstance(checksum,str) or re.fullmatch(r'[a-f0-9]{32}',checksum) is None
                        or hashlib.md5(local.read_bytes()).hexdigest()!=checksum):
                    raise DraftHeld('Original uploaded bytes or server acknowledgement changed')
                verified+=1
        return len(files),verified

    def inspect(self,lease,group):
        with self._lock:
            service,contract,path,manifest=self._owned_manifest(lease,group)
            total,verified=self._files(path,manifest)
            with self.binder.ledger.write():
                service,_=self.binder._record(lease,group)
                jobs=[dict(x) for x in self.binder.ledger.db.execute(
                    'SELECT * FROM pp_paid_strip_jobs WHERE purchase_group_id=? ORDER BY template_id',(group,))]
                if ({x['template_id'] for x in jobs}!={x['template_id'] for x in contract['designs']}
                        or len(jobs)!=len(contract['designs'])):
                    raise DraftHeld('Original purchased strip obligations are incomplete')
                for job in jobs:
                    saved=manifest.get('output_intents',{})
                    session=next((r for r in manifest['sessions']
                                  if r['template_id']==job['template_id']),None)
                    if (session is None or
                            (saved.get(session['session_id']) or {}).get('sha256')!=job['output_sha256']
                            or job['output_path']!=session.get('output_path')):
                        raise DraftHeld('Original paid print bytes are no longer authoritative')
                    validate_image(checked_path(path.parent/job['output_path']),
                                   job['output_sha256'],image_format='PNG',expected_size=(640,1920))
                complete=(manifest.get('upload_status')=='UPLOAD_COMPLETE'
                          and verified==total and not manifest.get('drive_retention_error')
                          and bool(manifest.get('drive_retention_registered_at')))
                if complete and service['drive_state']=='VERIFIED':
                    self.binder.ledger.db.execute("UPDATE pp_paid_services SET drive_state='UPLOADED' WHERE purchase_group_id=?",
                                                  (group,))
                    self.binder.ledger._event(lease.draft_id,'PAID_DRIVE_FILES_VERIFIED')
                elif service['drive_state']=='UPLOADED' and not complete:
                    raise DraftHeld('Previously verified paid Drive outcome is inconsistent')
                states={j['template_id']:j['state'] for j in jobs}
                receipt=self.binder.ledger.db.execute(
                    'SELECT receipt_state FROM pp_ticket_presentations WHERE purchase_group_id=?',(group,)).fetchone()
                return {
                    'transaction_id':service['transaction_id'],
                    'folder_url':service['folder_url'],
                    'upload_status':'UPLOAD_COMPLETE' if complete else manifest.get('upload_status'),
                    'upload_total':total,'upload_verified':verified,
                    'drive_verified':complete,'print_states':states,
                    'print_all_submitted':all(v=='SUBMITTED' for v in states.values()),
                    'physical_paper_verified':False,
                    'service_status':'OWED',
                    'safe_to_release_without_original_claim':False,
                    'needs_operator_review':any(v in {'SENDING','UNCERTAIN'} for v in states.values())
                        or bool(receipt and receipt['receipt_state']=='UNCERTAIN')
                }

    def enqueue(self,lease,group,templates):
        """Prepare original paid files, then notify the real serialized uploader.

        An absent uploader means a local synthetic dry run, not successful upload.
        """
        with self._lock:
            prepared=self.preparer.prepare(lease,group,templates)
            status=self.inspect(lease,group)
            if prepared['transaction_id']!=status['transaction_id']:
                raise DraftHeld('Original purchase changed between preparation and upload')
            if not self.worker:
                return dict(status,worker='NOT_CONFIGURED')
            if not self._started:
                self.worker.start()
                self._started=True
            self.worker.notify_transaction(prepared['transaction_id'])
            return dict(status,worker='QUEUED')
