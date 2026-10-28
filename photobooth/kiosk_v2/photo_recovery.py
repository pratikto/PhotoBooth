"""Exact-binding photo reconstruction; no folder search, camera or delivery I/O."""
import hashlib
import json
import os
from pathlib import Path
import re

from photobooth.booth_storage import checked_path
from photobooth.capture_journal import (CaptureRecoveryRequired, commit_capture,
                                       sync_directory, validate_image)
from photobooth.fulfillment_contract import frozen_contract
from photobooth.manifest_io import manifest_lock
from photobooth.retention import local_photos_expired, utc_datetime
from photobooth.transaction_store import LocalTransaction
from photobooth.workflow import PhotoSession, build_session_plans


def _held(message):
    raise CaptureRecoveryRequired(message)


def _publish_staged(folder, intent, image_format, *, repair):
    target = checked_path(folder/intent['path'])
    temporary = checked_path(folder/intent['temporary_path'])
    if not target.exists() and not temporary.exists():
        _held('Intent has no recoverable saved media')
    candidate = target if target.exists() else temporary
    validate_image(candidate, intent.get('sha256'), image_format=image_format,
                   expected_size=(640,1920) if image_format == 'PNG' else
                   (intent.get('width'),intent.get('height')))
    if temporary.exists() and candidate != temporary:
        validate_image(temporary, intent.get('sha256'), image_format=image_format)
    if repair:
        if not target.exists():
            os.link(temporary, target, follow_symlinks=False)
            sync_directory(target.parent)
        if temporary.exists():
            temporary.unlink()
            sync_directory(target.parent)
    return target


def reconstruct(store, templates, binding, *, repair=False):
    txid = binding.get('transaction_id')
    if (not isinstance(txid,str) or re.fullmatch(re.escape(binding.get('booth_id','')+'V2AR_')+r'[0-9]{8}',txid) is None
            or store.booth_id != binding.get('booth_id','')+'V2'):
        _held('Original booth allocation required')
    folder = checked_path(store.photos_root/txid)
    path = checked_path(folder/'manifest.json')
    if not path.is_file() or path.stat().st_size > 2*1024*1024:
        _held('Original bounded manifest required')
    with manifest_lock(path):
        data = json.loads(path.read_text(encoding='utf-8'))
        if (data.get('transaction_id') != txid or data.get('booth_id') != store.booth_id
                or data.get('capture_protocol') != 1 or data.get('schema_version') != store.layout_version
                or data.get('payment_binding') != binding or data.get('purpose') != 'PORTRAIT_V2_PHOTO_TEST'):
            _held('Exact payment and photo binding required')
        utc_datetime(data.get('created_at'))
        if local_photos_expired(data):
            _held('Original photo retention deadline passed')
        contract = data.get('frozen_order')
        if not isinstance(contract,dict):
            _held('Frozen paid template contract required')
        digest = hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if digest != binding.get('contract_hash') or frozen_contract(contract['quantities'],templates=templates) != contract:
            _held('Original template identity no longer available')
        plans = build_session_plans(templates,contract['quantities'])
        records = data.get('sessions')
        if not isinstance(records,list) or len(records) != len(plans):
            _held('Session count mismatch')
        transaction = LocalTransaction(txid,folder,path,data)
        known = {}
        for plan,record in zip(plans,records):
            if any(record.get(key) != value for key,value in {
                'session_id':plan.session_id,'template_id':plan.template.template_id,
                'order_number':plan.order_number,'total_sessions':plan.total_sessions,
                'print_copies':plan.print_copies}.items()):
                _held('Original session plan mismatch')
            known[plan.session_id]=plan
        intents = data.get('capture_intents',{})
        if not isinstance(intents,dict) or len(intents)>128:
            _held('Capture intent count invalid')
        active_paths=set();repair_required=False
        for operation,intent in intents.items():
            if (re.fullmatch(r'[a-f0-9]{32}',operation) is None or not isinstance(intent,dict)
                    or intent.get('operation_id') != operation or intent.get('session_id') not in known):
                _held('Capture operation identity invalid')
            if intent.get('state') == 'VOID_BEFORE_FRAME':
                continue
            plan=known[intent['session_id']];slot=intent.get('slot');role=intent.get('role')
            if type(slot) is not int or not 0<=slot<3 or role not in {'capture','retake'}:
                _held('Capture slot or role invalid')
            filename=f'photo_{slot+1:02d}.jpg' if role=='capture' else 'retake.jpg'
            expected=store.session_path(transaction,plan,'raw')/filename
            if intent.get('path') != expected.relative_to(folder).as_posix() or intent['path'] in active_paths:
                _held('Duplicate or redirected capture intent')
            active_paths.add(intent['path'])
            temporary=expected.with_name('.'+expected.stem+'.'+operation+'.tmp.jpg')
            if intent.get('temporary_path') != temporary.relative_to(folder).as_posix():
                _held('Capture temporary identity invalid')
            checked_path(expected);checked_path(temporary)
            if intent.get('state') == 'INTENT' and not expected.exists() and not temporary.exists():
                repair_required=True
                if repair:
                    intent.update(state='VOID_BEFORE_FRAME',reason='no_saved_bytes')
                    store._write_manifest(transaction)
                continue
            if intent.get('state') == 'STAGED':
                existing=store._session_record(transaction,plan.session_id)['raw_photos']
                if any(p.get('path')==intent['path'] for p in existing):
                    _held('Staged capture already appears in the manifest')
                _publish_staged(folder,intent,'JPEG',repair=repair);repair_required=True
                if repair:commit_capture(store,transaction,intent)
            elif intent.get('state') == 'COMMITTED':
                validate_image(expected,intent.get('sha256'),image_format='JPEG',
                               expected_size=(intent.get('width'),intent.get('height')))
            else:
                _held('Unproven capture bytes require review')
        sessions=[]
        for plan,record in zip(plans,records):
            session=PhotoSession(plan)
            raws=record.get('raw_photos')
            if not isinstance(raws,list) or len(raws)>4:
                _held('Capture count invalid')
            originals=[p for p in raws if p.get('role')=='capture']
            retakes=[p for p in raws if p.get('role')=='retake']
            if len(originals)>3 or len(retakes)>1 or len(originals)+len(retakes)!=len(raws):
                _held('Original or retake quota invalid')
            for index,photo in enumerate(originals):
                expected=store.session_path(transaction,plan,'raw')/f'photo_{index+1:02d}.jpg'
                intent=intents.get(photo.get('operation_id')) or {}
                if (photo.get('path') != expected.relative_to(folder).as_posix()
                        or intent.get('state')!='COMMITTED' or intent.get('path')!=photo['path']
                        or intent.get('role')!='capture' or intent.get('slot')!=index
                        or photo.get('sha256')!=intent.get('sha256')):
                    _held('Original manifest and intent disagree')
                validate_image(expected,intent['sha256'],image_format='JPEG')
                session.add_initial_photo(expected)
            if retakes:
                photo=retakes[0];intent=intents.get(photo.get('operation_id')) or {}
                if (len(originals)!=3 or record.get('retake_used') is not True
                        or record.get('selected_photo') not in [p['path'] for p in originals]
                        or intent.get('state')!='COMMITTED' or intent.get('path')!=photo.get('path')
                        or photo.get('path')!=(store.session_path(transaction,plan,'raw')/'retake.jpg').relative_to(folder).as_posix()
                        or intent.get('role')!='retake' or photo.get('sha256')!=intent.get('sha256')
                        or intent.get('selected_photo')!=record['selected_photo']):
                    _held('Retake selection/quota mismatch')
                index=[p['path'] for p in originals].index(record['selected_photo'])
                if intent.get('slot')!=index:_held('Retake target identity mismatch')
                session.select_photo(index);session.apply_retake(folder/photo['path'])
            elif record.get('retake_used'):
                _held('Consumed retake has no original saved bytes')
            if 'pending_retake_index' in record:
                if retakes or len(originals)!=3:
                    _held('Pending retake state invalid')
                session.select_photo(record['pending_retake_index'])
            raw_directory=checked_path(store.session_path(transaction,plan,'raw'))
            allowed={folder/i['path'] for i in intents.values() if i.get('session_id')==plan.session_id}
            allowed.update(folder/i['temporary_path'] for i in intents.values() if i.get('session_id')==plan.session_id)
            if raw_directory.exists():
                for entry in raw_directory.iterdir():
                    checked_path(entry)
                    if entry not in allowed:_held('Unbound capture file requires review')
            output_intent=data.get('output_intents',{}).get(plan.session_id)
            output=checked_path(store.output_path(transaction,plan))
            if output_intent:
                operation=output_intent.get('operation_id')
                if not isinstance(operation,str) or re.fullmatch(r'[a-f0-9]{32}',operation) is None:
                    _held('Output operation identity invalid')
                temporary=output.with_name('.'+output.stem+'.'+operation+'.tmp.png')
                if (output_intent.get('path')!=output.relative_to(folder).as_posix()
                        or output_intent.get('temporary_path')!=temporary.relative_to(folder).as_posix()
                        or output_intent.get('final_photos') != [store._relative_path(transaction,p) for p in session.final_photo_paths]
                        or len(originals)!=3):
                    _held('Output input identity mismatch')
                if output_intent.get('state')=='STAGED':
                    _publish_staged(folder,output_intent,'PNG',repair=repair);repair_required=True
                    if repair:store.record_output(transaction,plan.session_id,session.final_photo_paths,output)
                elif output_intent.get('state')!='COMMITTED':
                    _held('Unproven output requires review')
                if output.exists():
                    validate_image(output,output_intent.get('sha256'),image_format='PNG',expected_size=(640,1920))
                if record.get('output_path') != output.relative_to(folder).as_posix():
                    if repair:_held('Output acknowledgment mismatch')
                else:
                    if (record.get('output_sha256')!=output_intent.get('sha256')
                            or record.get('final_photos')!=output_intent['final_photos']):
                        _held('Committed output identity mismatch')
                    session.output_path=output
            elif output.exists() or record.get('output_path'):
                _held('Unbound composition requires review')
            sessions.append(session)
        index=next((i for i,s in enumerate(sessions) if s.output_path is None),len(sessions)-1)
        current=sessions[index];record=records[index]
        pending='pending_retake_index' in record
        phase='result' if current.output_path else 'capture' if pending or not current.ready_for_review else 'review'
        return transaction,sessions,index,phase,pending,repair_required
