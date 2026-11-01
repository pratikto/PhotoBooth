"""Synthetic paid source-media import for a single original verified Drive folder.

Private draft media is never uploaded, photographed again, printed or deleted.
The immutable PAID folder transaction is created before copied bytes are used.
Every source JPEG keeps its approved frozen digest; an interruption can resume
the SAME file identity without overwriting any existing customer artifact.
No paid strip composition or Drive publication happens in this module.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import threading
import uuid

from photobooth.booth_storage import checked_path
from photobooth.capture_journal import sync_directory, validate_image
from photobooth.manifest_io import manifest_lock
from photobooth.post_preview_paid_drive import OriginalPaidDriveBinding
from photobooth.post_preview_store import DraftHeld
from photobooth.transaction_store import LocalTransaction, TransactionStore
from photobooth.workflow import build_session_plans


class OriginalPaidMediaImporter:
    def __init__(self, binder, *, allow_incomplete_fixture=False):
        if (type(binder) is not OriginalPaidDriveBinding or
                allow_incomplete_fixture is not True):
            raise DraftHeld('Original mock-only paid media authorization required')
        self.binder=binder
        self._lock=threading.RLock()

    def _paid_transaction(self,lease,group,templates):
        binder=self.binder
        with binder.ledger.write():
            service,contract=binder._record(lease,group)
            if (service['drive_state'] not in {'VERIFIED','UPLOADED'} or not service['transaction_id']
                    or not service['folder_id'] or not service['folder_url']):
                raise DraftHeld('Exact paid Drive folder and viewer URL required')
        slot=binder.workspace.original_slot(service['transaction_id'])
        if (slot.get('folder_id')!=service['folder_id']
                or slot.get('folder_url')!=service['folder_url']
                or slot.get('link_verified') is not True
                or slot.get('photo_number_layout')!=1):
            raise DraftHeld('Original paid folder local/remote evidence mismatch')
        claimed=binder.workspace.claim_exact(service['transaction_id'],slot['claim_token'])
        plans=build_session_plans(templates,contract['quantities'])
        if (len(plans)!=len(contract['designs']) or len(plans)>12 or
                {p.template.template_id for p in plans}!={d['template_id'] for d in contract['designs']}):
            raise DraftHeld('Original frozen paid design set changed')
        return service,contract,claimed,plans

    @staticmethod
    def _binding(group,service,contract):
        return {
            'order_version':contract['version'],
            'purchase_group_id':group,
            'service_id':service['service_id'],
            'entitlement_id':service['entitlement_id'],
            'contract_sha256':service['contract_sha256'],
        }

    @staticmethod
    def _manifest(store,claimed,service,contract,plans,group):
        folder=checked_path(Path(claimed['staging_path']))
        manifest_path=checked_path(folder/'manifest.json')
        binding=OriginalPaidMediaImporter._binding(group,service,contract)
        if manifest_path.exists():
            if not manifest_path.is_file() or manifest_path.stat().st_size>2*1024*1024:
                raise DraftHeld('Original paid media manifest unavailable')
            with manifest_lock(manifest_path):
                data=json.loads(manifest_path.read_text(encoding='utf-8'))
            if (data.get('transaction_id')!=service['transaction_id']
                    or data.get('booth_id')!=store.booth_id
                    or data.get('storage_layout')!=2
                    or data.get('capture_protocol')!=1
                    or data.get('purpose')!='POST_PREVIEW_PAID'
                    or data.get('payment_binding')!=binding
                    or data.get('frozen_order')!=contract
                    or data.get('drive_folder_id')!=service['folder_id']
                    or data.get('drive_folder_url')!=service['folder_url']
                    or len(data.get('sessions',[]))!=len(plans)
                    or any(row.get('template_id')!=plan.template.template_id or
                           row.get('session_id')!=plan.session_id or
                           row.get('print_copies')!=plan.print_copies
                           for row,plan in zip(data['sessions'],plans))):
                raise DraftHeld('Original paid media manifest has conflicting ownership')
            return LocalTransaction(service['transaction_id'],folder,manifest_path,data)
        transaction=store.start_transaction(
            plans,transaction_id=service['transaction_id'],folder_path=folder,
            drive_slot={'folder_id':service['folder_id'],'folder_url':service['folder_url']},
            initial_metadata={'purpose':'POST_PREVIEW_PAID','payment_enabled':True,
                              'financial_transaction':True,'payment_binding':binding,
                              'frozen_order':contract})
        transaction.manifest.update(
            drive_claim_token=claimed['claim_token'],
            drive_binding_verified=True,photo_number_layout=1,
            drive_intent=False,paid_media_import_ready=False,
            post_preview_retention_anchor=service['retention_anchor'])
        store._write_manifest(transaction)
        return transaction

    @staticmethod
    def _source_record(source_tx,source):
        relative=checked_path(source).relative_to(checked_path(source_tx.folder_path)).as_posix()
        matches=[item for item in source_tx.manifest['sessions'][0].get('raw_photos',[])
                 if item.get('path')==relative]
        if len(matches)!=1 or not isinstance(matches[0].get('sha256'),str):
            raise DraftHeld('Original private source capture hash is missing')
        digest=matches[0]['sha256']
        validate_image(source,digest,image_format='JPEG')
        return relative,digest

    @staticmethod
    def _transfer(store,transaction,plan,source,source_relative,expected_sha,filename,role,lineage):
        raw_dir=checked_path(store.session_path(transaction,plan,'raw'))
        raw_dir.mkdir(parents=True,exist_ok=True)
        destination=checked_path(raw_dir/filename)
        relative=destination.relative_to(transaction.folder_path).as_posix()
        with manifest_lock(transaction.manifest_path):
            transaction.manifest=json.loads(transaction.manifest_path.read_text(encoding='utf-8'))
            manifest=transaction.manifest
            intents=manifest.setdefault('paid_transfer_intents',{})
            expected={
                'source_lineage':lineage,'source_relative':source_relative,
                'destination':relative,'sha256':expected_sha,'role':role,
            }
            intent=intents.get(relative)
            if intent is None:
                intent={**expected,'operation_id':uuid.uuid4().hex,'state':'PREPARED'}
                intents[relative]=intent
                store._write_manifest(transaction)
            elif any(intent.get(k)!=v for k,v in expected.items()):
                raise DraftHeld('Original media import identity changed')
            temporary=checked_path(destination.with_name(
                '.'+destination.name+'.'+intent['operation_id']+'.tmp'))
            if destination.exists():
                validate_image(destination,expected_sha,image_format='JPEG')
            else:
                if temporary.exists():
                    validate_image(temporary,expected_sha,image_format='JPEG')
                else:
                    with checked_path(source).open('rb') as src,temporary.open('xb') as out:
                        shutil.copyfileobj(src,out,1024*1024)
                        out.flush()
                        os.fsync(out.fileno())
                    validate_image(temporary,expected_sha,image_format='JPEG')
                os.link(temporary,destination,follow_symlinks=False)
                sync_directory(destination.parent)
            if temporary.exists():
                temporary.unlink()
                sync_directory(temporary.parent)
            if intent['state'] not in {'PREPARED','COMMITTED'}:
                raise DraftHeld('Unknown original paid import state')
            intent['state']='COMMITTED'
            record=store._session_record(transaction,plan.session_id)
            existing=[r for r in record['raw_photos'] if r.get('path')==relative]
            if existing:
                if (len(existing)!=1 or existing[0].get('sha256')!=expected_sha
                        or existing[0].get('role')!=role):
                    raise DraftHeld('Original paid source record differs from saved file')
            else:
                record['raw_photos'].append({'path':relative,'role':role,
                                              'sha256':expected_sha})
            files=manifest.setdefault('upload_files',{})
            if relative not in files:
                files[relative]={
                    'path':relative,'content_version':uuid.uuid4().hex,
                    'status':'LOCAL_ONLY','size_bytes':destination.stat().st_size,
                    'drive_file_id':None,'md5_checksum':None,
                    'upload_session_url':None}
            store._write_manifest(transaction)
        return destination

    def prepare(self,lease,group,templates):
        """Stage exactly the original approved raw JPEGs; nothing is published."""
        with self._lock,self.binder._lock:
            self.binder.checkout.verify_frozen(group,templates)
            service,contract,claimed,plans=self._paid_transaction(lease,group,templates)
            store=TransactionStore(self.binder.workspace.root,self.binder.workspace.counter_path,
                                   self.binder.workspace.booth_id,layout_version=2,capture_protocol=1)
            tx=self._manifest(store,claimed,service,contract,plans,group)
            rows={d['template_id']:d for d in contract['designs']}
            staged={}
            for plan in plans:
                design=rows[plan.template.template_id]
                # Prepaid frozen contracts are intentionally NOT editable.
                # _selected() is a capture/edit-only helper, so read the exact
                # immutable selected lineage under a non-editing owner check.
                with self.binder.ledger.write():
                    self.binder.ledger._owned(lease)
                    row=self.binder.ledger.db.execute('''SELECT * FROM pp_templates
                        WHERE draft_id=? AND template_id=?''',
                        (lease.draft_id,plan.template.template_id)).fetchone()
                    if (row is None or not row['selected'] or not row['approved']
                            or row['lineage_id']!=design['lineage_id']
                            or row['copies']!=plan.print_copies):
                        raise DraftHeld('Original frozen selected-photo lineage changed')
                source_store,source_tx,source_plan=self.binder.checkout.photos._open(
                    lease,plan.template,row,repair=False)
                source_session=self.binder.checkout.photos._session(source_tx,source_plan)
                if len(source_session.initial_photo_paths)!=3:
                    raise DraftHeld('Three approved original photos required')
                sources=[(p,f'photo_{i:02d}.jpg','capture') for i,p in
                         enumerate(source_session.initial_photo_paths,1)]
                if source_session.retake_path is not None:
                    sources.append((source_session.retake_path,'retake.jpg','retake'))
                destinations=[]
                for original,name,role in sources:
                    rel,sha=self._source_record(source_tx,original)
                    path=self._transfer(store,tx,plan,original,rel,sha,name,role,
                                        design['lineage_id'])
                    destinations.append(path)
                with manifest_lock(tx.manifest_path):
                    tx.manifest=json.loads(tx.manifest_path.read_text(encoding='utf-8'))
                    session=store._session_record(tx,plan.session_id)
                    if session['retake_used'] and not design['retake_consumed']:
                        raise DraftHeld('Original paid retake lineage disagrees')
                    session['retake_used']=bool(design['retake_consumed'])
                    if design['retake_consumed']:
                        idx=design['retake_slot']
                        if type(idx) is not int or idx not in (0,1,2) or len(destinations)!=4:
                            raise DraftHeld('Original paid retake was not preserved')
                        session['selected_photo']=destinations[idx].relative_to(
                            tx.folder_path).as_posix()
                    elif len(destinations)!=3:
                        raise DraftHeld('Unregistered paid retake exists')
                    store._write_manifest(tx)
                staged[plan.template.template_id]={
                    'session_id':plan.session_id,'copies':plan.print_copies,
                    'raw_count':len(destinations)}
            with manifest_lock(tx.manifest_path):
                tx.manifest=json.loads(tx.manifest_path.read_text(encoding='utf-8'))
                tx.manifest['paid_media_import_ready']=True
                store._write_manifest(tx)
            return {'transaction_id':tx.transaction_id,
                    'raw_count':sum(x['raw_count'] for x in staged.values()),
                    'templates':staged,'status':'STAGED_PRIVATE',
                    'print_authorized':False,'upload_authorized':False}
