"""Compose original bought strips only after verified PAID and individual Drive URL.

Explicit mock or protected backend binding authorizes this shared core. No
printer bytes or upload is sent by preparation. Every original strip is
recorded with the source photo binding, output digest and one immutable job ID.
"""
import hashlib
import json
from pathlib import Path
import threading
import uuid

from photobooth.booth_storage import checked_path
from photobooth.capture_journal import publish_output,validate_image
from photobooth.catalog import compose_result
from photobooth.kiosk_v2.photo_recovery import _publish_staged
from photobooth.manifest_io import manifest_lock
from photobooth.post_preview_paid_media import OriginalPaidMediaImporter
from photobooth.post_preview_store import DraftHeld
from photobooth.transaction_store import LocalTransaction,TransactionStore
from photobooth.workflow import build_session_plans


class OriginalPaidStripPreparer:
    def __init__(self,importer,*,allow_incomplete_fixture=False):
        from photobooth.post_preview_sandbox_delivery import original_paid_core_allowed
        if (type(importer) is not OriginalPaidMediaImporter
                or not original_paid_core_allowed(importer.binder,allow_incomplete_fixture)):
            raise DraftHeld('Exact original paid strip preparation authority required')
        self.importer=importer
        self.binder=importer.binder
        self._lock=threading.RLock()

    @staticmethod
    def _original_final_paths(store,tx,plan):
        record=store._session_record(tx,plan.session_id)
        entries={r.get('path'):r for r in record.get('raw_photos',[])}
        root=checked_path(store.session_path(tx,plan,'raw'))
        originals=[checked_path(root/f'photo_{i:02d}.jpg') for i in (1,2,3)]
        required={p.relative_to(tx.folder_path).as_posix() for p in originals}
        if record['retake_used']:
            replacement=checked_path(root/'retake.jpg')
            required.add(replacement.relative_to(tx.folder_path).as_posix())
        if set(entries)!=required or len(entries)!=len(required):
            raise DraftHeld('Original paid photo/retake set is incomplete')
        for p in [*originals,*([replacement] if record['retake_used'] else [])]:
            item=entries[p.relative_to(tx.folder_path).as_posix()]
            validate_image(p,item.get('sha256'),image_format='JPEG')
        final=list(originals)
        if record['retake_used']:
            if record.get('selected_photo') not in {
                p.relative_to(tx.folder_path).as_posix() for p in originals}:
                raise DraftHeld('Original retake target changed')
            index=[p.relative_to(tx.folder_path).as_posix() for p in originals].index(
                record['selected_photo'])
            final[index]=replacement
        elif record.get('selected_photo') is not None:
            raise DraftHeld('Unapproved original retake target')
        return final

    @staticmethod
    def _binding(contract,service,plan,photos):
        return {
            'version':contract['version'],'service_id':service['service_id'],
            'contract_sha256':service['contract_sha256'],
            'folder_url':service['folder_url'],
            'template_id':plan.template.template_id,
            'copies':plan.print_copies,
            'final_photos':[p.name for p in photos],
        }

    def prepare(self,lease,group,templates):
        """Publish original purchased composition and prepare, never send, jobs."""
        with self._lock,self.importer._lock,self.binder._lock:
            staged=self.importer.prepare(lease,group,templates)
            with self.binder.ledger.write():
                service,contract=self.binder._record(lease,group)
                if (service['drive_state'] not in {'VERIFIED','UPLOADED'} or not service['folder_id']
                        or service['transaction_id']!=staged['transaction_id']
                        or not service['folder_url']):
                    raise DraftHeld('Verified original paid customer Drive URL required')
            plans=build_session_plans(templates,contract['quantities'])
            root=checked_path(self.binder.workspace.root)
            folder=checked_path(root/staged['transaction_id'])
            manifest_path=checked_path(folder/'manifest.json')
            store=TransactionStore(root,self.binder.workspace.counter_path,
                self.binder.workspace.booth_id,layout_version=2,capture_protocol=1)
            with manifest_lock(manifest_path):
                data=json.loads(manifest_path.read_text(encoding='utf-8'))
                if (data.get('purpose')!='POST_PREVIEW_PAID'
                        or data.get('transaction_id')!=service['transaction_id']
                        or data.get('payment_binding',{}).get('service_id')!=service['service_id']
                        or data.get('frozen_order')!=contract
                        or data.get('paid_media_import_ready') is not True
                        or data.get('drive_folder_id')!=service['folder_id']
                        or data.get('drive_folder_url')!=service['folder_url']):
                    raise DraftHeld('Original paid media or folder binding is unavailable')
            tx=LocalTransaction(service['transaction_id'],folder,manifest_path,data)
            journal=[]
            for plan in plans:
                with manifest_lock(manifest_path):
                    tx.manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
                    photos=self._original_final_paths(store,tx,plan)
                    binding=self._binding(contract,service,plan,photos)
                    stored_binding=tx.manifest.setdefault('paid_strip_bindings',{}).get(plan.session_id)
                    if stored_binding is not None and stored_binding!=binding:
                        raise DraftHeld('Original paid strip binding changed')
                    output=checked_path(store.output_path(tx,plan))
                    intent=tx.manifest.get('output_intents',{}).get(plan.session_id)
                    if intent:
                        if intent.get('state')=='STAGED':
                            _publish_staged(folder,intent,'PNG',repair=True)
                            store.record_output(tx,plan.session_id,photos,output)
                        elif intent.get('state')=='COMMITTED':
                            validate_image(output,intent.get('sha256'),
                                image_format='PNG',expected_size=(640,1920))
                            record=store._session_record(tx,plan.session_id)
                            expected=[p.relative_to(folder).as_posix() for p in photos]
                            if record.get('final_photos')!=expected:
                                raise DraftHeld('Saved paid strip photos changed')
                        else:
                            raise DraftHeld('Unverified original paid composition state')
                    else:
                        def render(destination,plan=plan,photos=photos):
                            compose_result(photos,plan.template,destination,
                                tx.transaction_id,plan.session_id,
                                folder_url=service['folder_url'],mirror_photos=True)
                        publish_output(store,tx,plan,photos,render)
                        store.record_output(tx,plan.session_id,photos,output)
                    # publish_output reloads the durable manifest; create the
                    # exact-bound field after that verified staged/committed step.
                    tx.manifest.setdefault('paid_strip_bindings',{})[plan.session_id]=binding
                    store._write_manifest(tx)
                    intent=tx.manifest['output_intents'][plan.session_id]
                    output_sha=intent['sha256']
                    relative=output.relative_to(folder).as_posix()
                    with self.binder.ledger.write():
                        latest,_=self.binder._record(lease,group)
                        if (latest['transaction_id']!=tx.transaction_id
                                or latest['folder_id']!=service['folder_id']):
                            raise DraftHeld('Original service/folder changed during composition')
                        existing=self.binder.ledger.db.execute('''SELECT * FROM pp_paid_strip_jobs
                            WHERE purchase_group_id=? AND template_id=?''',
                            (group,plan.template.template_id)).fetchone()
                        if existing:
                            if (existing['copies']!=plan.print_copies
                                    or existing['output_path']!=relative
                                    or existing['output_sha256']!=output_sha):
                                raise DraftHeld('Original purchased strip job differs')
                            job=existing['job_id']
                        else:
                            job=uuid.uuid4().hex
                            self.binder.ledger.db.execute('''INSERT INTO pp_paid_strip_jobs
                                (purchase_group_id,template_id,job_id,copies,
                                 output_path,output_sha256,updated_at)
                                VALUES(?,?,?,?,?,?,?)''',
                                (group,plan.template.template_id,job,
                                 plan.print_copies,relative,output_sha,
                                 self.binder.ledger.now()))
                            self.binder.ledger._event(lease.draft_id,'PAID_STRIP_PREPARED')
                    journal.append({'template_id':plan.template.template_id,
                                    'copies':plan.print_copies,'job_id':job,
                                    'output_path':str(output),'output_sha256':output_sha,
                                    'state':'PREPARED'})
            with self.binder.ledger.write():
                latest,_=self.binder._record(lease,group)
                count=self.binder.ledger.db.execute('SELECT COUNT(*) FROM pp_paid_strip_jobs WHERE purchase_group_id=?',
                                                    (group,)).fetchone()[0]
                if count!=len(plans) or latest['status']!='OWED':
                    raise DraftHeld('Exact original paid print obligations incomplete')
                with manifest_lock(manifest_path):
                    tx.manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
                    tx.manifest['drive_intent']=True
                    for item in tx.manifest['upload_files'].values():
                        if item['status']=='LOCAL_ONLY':
                            item['status']='PENDING_UPLOAD'
                    tx.manifest['upload_status']='PENDING_UPLOAD'
                    tx.manifest['status']='READY_FOR_PAID_DELIVERY'
                    store._write_manifest(tx)
            return {'transaction_id':tx.transaction_id,
                    'folder_url':service['folder_url'],'jobs':journal,
                    'status':'OWED_PREPARED','printing_started':False,
                    'public_upload_started':False}
