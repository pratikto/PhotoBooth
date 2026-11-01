"""Unpaid private capture adapter over the original immutable JPEG journal.

No printer, provider, Drive pool/worker or paid completion API is constructed.
One retained template lineage owns one private transaction even when deselected.
Only a trusted, current draft worker may use this adapter. It is not mounted by
the legacy GUI and does not implement returning-customer authentication.
"""
import json
from pathlib import Path
import re

from photobooth.booth_storage import checked_path
from photobooth.capture_journal import CaptureRecoveryRequired, commit_capture, validate_image
from photobooth.fulfillment_contract import frozen_contract
from photobooth.kiosk_v2.photo_recovery import _publish_staged
from photobooth.manifest_io import manifest_lock
from photobooth.post_preview_store import DraftHeld
from photobooth.retention import local_photos_expired, utc_datetime
from photobooth.transaction_store import LocalTransaction, TransactionStore
from photobooth.workflow import PhotoSession, build_session_plans


PURPOSE = 'POST_PREVIEW_PRIVATE'


class PrivateDraftPhotos:
    def __init__(self, ledger, root, *, policy=None):
        from photobooth.post_preview_resources import PrivateCapturePolicy
        self.ledger = ledger
        self.root = checked_path(Path(root))
        self.policy = policy or PrivateCapturePolicy()
        if not isinstance(self.policy, PrivateCapturePolicy):
            raise TypeError('Explicit private resource policy required')

    def prepare(self, lease):
        """Actual private disk/fsync probe off the GUI thread, no shutter/cloud."""
        with self.ledger.write():
            self.ledger._owned(lease, editable=True)
            return self.policy.inspect(self.root/lease.draft_id, probe=True)

    def _selected(self, lease, template, *, revision=None):
        self.ledger._owned(lease, editable=True, revision=revision)
        row = self.ledger.db.execute('SELECT * FROM pp_templates WHERE draft_id=? AND template_id=?',
                                    (lease.draft_id, template.template_id)).fetchone()
        if not row or not row['selected']:
            raise DraftHeld('Original selected template required')
        return row

    def _open(self, lease, template, row):
        root = checked_path(self.root / lease.draft_id)
        store = TransactionStore(root, root / 'unused-counter.json', lease.booth_id,
                                 layout_version=2, capture_protocol=1)
        plan = build_session_plans([template], {template.template_id: 1})[0]
        transaction_id = 'PP' + row['lineage_id'] + '_00000001'
        folder = checked_path(root / transaction_id)
        path = checked_path(folder / 'manifest.json')
        contract = frozen_contract({template.template_id: 1}, templates=[template])
        with manifest_lock(path):
            if not path.exists():
                if folder.exists():
                    raise CaptureRecoveryRequired('Private lineage allocation is incomplete')
                tx = store.start_transaction([plan], transaction_id=transaction_id,
                    initial_metadata={'purpose': PURPOSE, 'financial_transaction': False,
                                      'payment_enabled': False, 'frozen_order': contract})
            else:
                if path.stat().st_size > 2*1024*1024:
                    raise CaptureRecoveryRequired('Private manifest is oversized')
                data = json.loads(path.read_text(encoding='utf-8'))
                if (data.get('transaction_id') != transaction_id
                        or data.get('booth_id') != lease.booth_id
                        or data.get('purpose') != PURPOSE
                        or data.get('capture_protocol') != 1
                        or data.get('schema_version') != 2
                        or data.get('frozen_order') != contract
                        or data.get('status') != 'IN_PROGRESS'
                        or data.get('upload_status') != 'LOCAL_ONLY'
                        or data.get('drive_folder_id') or data.get('drive_folder_url')
                        or data.get('drive_intent') or data.get('payment_binding')
                        or data.get('financial_transaction') is not False
                        or data.get('payment_enabled') is not False):
                    raise CaptureRecoveryRequired('Private draft identity/artwork changed')
                tx = LocalTransaction(transaction_id, folder, path, data)
            utc_datetime(tx.manifest.get('created_at'))
            if local_photos_expired(tx.manifest):
                raise CaptureRecoveryRequired('Private draft media lifetime expired')
            self._restore(store, tx, plan, row)
            return store, tx, plan

    def _restore(self, store, tx, plan, row):
        data = tx.manifest
        records = data.get('sessions')
        if (not isinstance(records, list) or len(records) != 1
                or records[0].get('session_id') != plan.session_id
                or records[0].get('template_id') != plan.template.template_id):
            raise CaptureRecoveryRequired('Exact private template session required')
        record = records[0]
        intents = data.get('capture_intents', {})
        if not isinstance(intents, dict) or len(intents) > 16:
            raise CaptureRecoveryRequired('Private capture intent bound exceeded')
        allowed = set()
        active = set()
        for operation, intent in intents.items():
            if (re.fullmatch(r'[a-f0-9]{32}', operation) is None
                    or not isinstance(intent, dict) or intent.get('operation_id') != operation
                    or intent.get('session_id') != plan.session_id
                    or type(intent.get('slot')) is not int or not 0 <= intent['slot'] < 3
                    or intent.get('role') not in {'capture', 'retake'}):
                raise CaptureRecoveryRequired('Private capture intent is invalid')
            filename = (f"photo_{intent['slot']+1:02d}.jpg" if intent['role'] == 'capture' else 'retake.jpg')
            target = checked_path(store.session_path(tx, plan, 'raw') / filename)
            temporary = target.with_name('.'+target.stem+'.'+operation+'.tmp.jpg')
            if (intent.get('path') != target.relative_to(tx.folder_path).as_posix()
                    or intent.get('temporary_path') != temporary.relative_to(tx.folder_path).as_posix()):
                raise CaptureRecoveryRequired('Private media path redirected')
            allowed.update((target, checked_path(temporary)))
            if intent.get('state') == 'VOID_BEFORE_FRAME':
                continue
            if target in active:
                raise CaptureRecoveryRequired('Duplicate capture intent')
            active.add(target)
            if intent.get('state') == 'INTENT' and not target.exists() and not temporary.exists():
                intent['state'] = 'VOID_BEFORE_FRAME'
                store._write_manifest(tx)
                continue
            if intent.get('state') == 'STAGED':
                if any(p.get('path') == intent['path'] for p in record['raw_photos']):
                    raise CaptureRecoveryRequired('Staged media already acknowledged')
                originals = [p for p in record['raw_photos'] if p.get('role') == 'capture']
                if intent['role'] == 'retake':
                    if (len(originals) != 3 or row['retake_consumed'] != 1
                            or row['retake_slot'] != intent['slot']
                            or intent.get('selected_photo') != originals[intent['slot']]['path']):
                        raise CaptureRecoveryRequired('Staged retake has a different quota/target')
                elif intent['slot'] != len(originals):
                    raise CaptureRecoveryRequired('Staged original has a different slot')
                _publish_staged(tx.folder_path, intent, 'JPEG', repair=True)
                commit_capture(store, tx, intent)
            elif intent.get('state') != 'COMMITTED':
                raise CaptureRecoveryRequired('Unknown private saved bytes require review')
            validate_image(target, intent.get('sha256'), image_format='JPEG',
                           expected_size=(intent.get('width'), intent.get('height')))
        originals = []
        retakes = []
        for photo in record.get('raw_photos', []):
            intent = intents.get(photo.get('operation_id'), {})
            if (intent.get('state') != 'COMMITTED' or photo.get('path') != intent.get('path')
                    or photo.get('sha256') != intent.get('sha256')
                    or photo.get('role') != intent.get('role')):
                raise CaptureRecoveryRequired('Private manifest and media journal disagree')
            if photo['role'] == 'capture':
                if intent['slot'] != len(originals):
                    raise CaptureRecoveryRequired('Original capture sequence changed')
                originals.append(photo)
            else:
                retakes.append(photo)
        if len(originals) > 3 or len(retakes) > 1:
            raise CaptureRecoveryRequired('Private photo quota exceeded')
        committed = [i for i in intents.values() if i.get('state') == 'COMMITTED']
        if len(committed) != len(originals)+len(retakes):
            raise CaptureRecoveryRequired('Private capture acknowledgement missing')
        if retakes:
            intent = intents[retakes[0]['operation_id']]
            if (len(originals) != 3 or row['retake_consumed'] != 1
                    or row['retake_slot'] != intent['slot'] or record.get('retake_used') is not True
                    or record.get('selected_photo') != originals[intent['slot']]['path']
                    or intent.get('selected_photo') != record['selected_photo']):
                raise CaptureRecoveryRequired('Original retake quota/target changed')
        elif record.get('retake_used'):
            raise CaptureRecoveryRequired('Consumed private retake has no bytes')
        directory = checked_path(store.session_path(tx, plan, 'raw'))
        if directory.exists():
            for entry in directory.iterdir():
                if checked_path(entry) not in allowed:
                    raise CaptureRecoveryRequired('Unbound private file requires review')
        if row['retake_consumed'] and not retakes:
            if len(originals) != 3:
                raise CaptureRecoveryRequired('Retake quota has no original trio')
            if record.get('pending_retake_index') != row['retake_slot']:
                record['pending_retake_index'] = row['retake_slot']
                store._write_manifest(tx)

    def _session(self, tx, plan):
        record = tx.manifest['sessions'][0]
        session = PhotoSession(plan)
        for photo in record['raw_photos']:
            if photo['role'] == 'capture':
                session.add_initial_photo(tx.folder_path / photo['path'])
        for photo in record['raw_photos']:
            if photo['role'] == 'retake':
                originals = [p['path'] for p in record['raw_photos'] if p['role'] == 'capture']
                session.select_photo(originals.index(record['selected_photo']))
                session.apply_retake(tx.folder_path / photo['path'])
        return session

    def inspect(self, lease, template):
        with self.ledger.write():
            row = self._selected(lease, template)
            store, tx, plan = self._open(lease, template, row)
            session = self._session(tx, plan)
            return {'lineage_id': row['lineage_id'], 'original_count': len(session.initial_photo_paths),
                    'retake_consumed': bool(row['retake_consumed']),
                    'retake_saved': session.retake_used, 'final_paths': tuple(session.final_photo_paths),
                    'manifest_path': tx.manifest_path}

    def request_retake(self, lease, template, slot, *, revision):
        if type(slot) is not int or not 0 <= slot < 3:
            raise ValueError('Choose one of three original slots')
        with self.ledger.write():
            row = self._selected(lease, template, revision=revision)
            store, tx, plan = self._open(lease, template, row)
            if row['retake_consumed'] or not self._session(tx, plan).ready_for_review:
                raise DraftHeld('Exactly one retake after three original captures')
            # SQLite quota/slot commits BEFORE the next shutter/file operation.
            self.ledger.db.execute('''UPDATE pp_templates SET retake_consumed=1,
                retake_slot=?,approved=0 WHERE draft_id=? AND template_id=?''',
                (slot, lease.draft_id, template.template_id))
            self._changed(lease, 'RETAKE_SELECTED')

    def _changed(self, lease, event):
        self.ledger.db.execute('UPDATE pp_drafts SET revision=revision+1,updated_at=? WHERE draft_id=?',
                               (self.ledger.now(), lease.draft_id))
        self.ledger._event(lease.draft_id, event)

    def capture(self, lease, template, image, *, slot, revision, retake=False):
        """One explicit original slot/selected retake; duplicate callbacks never recapture."""
        if type(slot) is not int or not 0 <= slot < 3 or type(retake) is not bool:
            raise ValueError('Exact original slot and role required')
        with self.ledger.write():
            row = self._selected(lease, template, revision=revision)
            self.policy.inspect(self.root/lease.draft_id, image=image)
            store, tx, plan = self._open(lease, template, row)
            session = self._session(tx, plan)
            if retake:
                if not row['retake_consumed'] or row['retake_slot'] != slot:
                    raise DraftHeld('Original durable retake selection required')
                if session.retake_used:
                    return session.retake_path
                filename, role = 'retake.jpg', 'retake'
            else:
                if slot < len(session.initial_photo_paths):
                    return session.initial_photo_paths[slot]
                if slot != len(session.initial_photo_paths) or row['retake_consumed']:
                    raise DraftHeld('Original capture slot is unavailable')
                filename, role = f'photo_{slot+1:02d}.jpg', 'capture'
            with manifest_lock(tx.manifest_path):
                path = store.save_raw_photo(tx, plan, image, filename, role)
            self.ledger.db.execute('UPDATE pp_templates SET approved=0 WHERE draft_id=? AND template_id=?',
                                   (lease.draft_id, template.template_id))
            self._changed(lease, 'RETAKE_SAVED' if retake else 'PHOTO_SAVED')
            return path
