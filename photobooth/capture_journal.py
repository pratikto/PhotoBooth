"""AR-04 write-ahead JPEG publication over the existing manifest/retention lock.

Only v2 opts into this protocol. Existing targets are immutable; unexpected
intent/file combinations require reconstruction, never an overwrite retry.
"""
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

from PIL import Image


class CaptureRecoveryRequired(RuntimeError):
    """Keep original intent/media for exact recovery, without replaying shutter."""


def boundary(_name):
    """Deterministic offline fault seam; production has no injected action."""


def sync_directory(path):
    if os.name == 'nt':
        return False
    descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        try:
            os.fsync(descriptor)
        except OSError as error:
            if error.errno in {errno.EINVAL, errno.ENOTSUP}:
                return False
            raise
    finally:
        os.close(descriptor)
    return True


def save_capture(store, transaction, session, image, filename, role):
    from photobooth.booth_storage import checked_path
    if role not in {'capture', 'retake'} or not isinstance(filename, str):
        raise ValueError('Invalid capture role or filename')
    if role == 'capture' and re.fullmatch(r'photo_0[1-3]\.jpg', filename) is None:
        raise ValueError('Exactly three original capture slots are supported')
    if role == 'retake' and filename != 'retake.jpg':
        raise ValueError('One immutable retake target is supported')
    checked_path(transaction.manifest_path)
    latest = json.loads(transaction.manifest_path.read_text(encoding='utf-8'))
    if latest.get('transaction_id') != transaction.transaction_id or latest.get('capture_protocol') != 1:
        raise CaptureRecoveryRequired('Capture protocol identity requires review')
    transaction.manifest = latest
    record = store._session_record(transaction, session.session_id)
    originals = [p for p in record['raw_photos'] if p['role'] == 'capture']
    selected = None
    if role == 'capture':
        slot = int(filename[6:8])-1
        if slot != len(originals) or len(originals) >= 3:
            raise CaptureRecoveryRequired('Original slot already captured or ambiguous')
    else:
        slot = record.get('pending_retake_index')
        if (len(originals) != 3 or type(slot) is not int or not 0 <= slot < 3
                or record['retake_used'] or any(p['role'] == 'retake' for p in record['raw_photos'])):
            raise CaptureRecoveryRequired('Retake selection or quota requires review')
        selected = originals[slot]['path']
    relative = ((Path('Photo') / f'{session.order_number:02d}' / 'raw' / filename)
                if store.layout_version == 2 else Path('raw') / session.session_id / filename)
    target = checked_path(transaction.folder_path / relative)
    if target.exists() or any(i.get('path') == relative.as_posix()
                               for i in latest.get('capture_intents', {}).values()):
        raise CaptureRecoveryRequired('Existing capture evidence must not be replaced')
    target.parent.mkdir(parents=True, exist_ok=True)
    operation = uuid.uuid4().hex
    temporary = checked_path(target.with_name('.'+target.stem+'.'+operation+'.tmp.jpg'))
    intent = {'operation_id': operation, 'session_id': session.session_id,
              'slot': slot, 'role': role, 'attempt': 1, 'path': relative.as_posix(),
              'temporary_path': temporary.relative_to(transaction.folder_path).as_posix(),
              'state': 'INTENT', 'selected_photo': selected}
    latest.setdefault('capture_intents', {})[operation] = intent
    store._write_manifest(transaction)
    boundary('intent')
    with temporary.open('xb') as stream:
        image.convert('RGB').save(stream, format='JPEG', quality=95)
        stream.flush()
        os.fsync(stream.fileno())
    boundary('temporary')
    size = temporary.stat().st_size
    with Image.open(temporary) as saved:
        saved.load()
        if saved.format != 'JPEG' or saved.size != image.size or size <= 0:
            raise CaptureRecoveryRequired('Saved capture failed image validation')
    intent.update(state='STAGED', sha256=hashlib.sha256(temporary.read_bytes()).hexdigest(),
                  size_bytes=size, width=image.width, height=image.height)
    store._write_manifest(transaction)
    boundary('staged')
    # Atomic no-clobber publication. POSIX rename/replace could silently destroy
    # an orphan, so hardlink then unlink the private temp instead. Unsupported
    # filesystems fail closed and preserve STAGED evidence for operator review.
    os.link(temporary, target, follow_symlinks=False)
    sync_directory(target.parent)
    temporary.unlink()
    sync_directory(target.parent)
    boundary('published')
    record['status'] = 'CAPTURING'
    record['raw_photos'].append({'path': relative.as_posix(), 'role': role,
                                 'operation_id': operation, 'sha256': intent['sha256']})
    if role == 'retake':
        record.update(retake_used=True, selected_photo=selected)
        record.pop('pending_retake_index', None)
    latest['upload_files'][relative.as_posix()] = {
        'path': relative.as_posix(), 'content_version': operation,
        'status': 'PENDING_UPLOAD' if latest.get('drive_folder_id') or latest.get('drive_intent') else 'LOCAL_ONLY',
        'size_bytes': size, 'drive_file_id': None, 'md5_checksum': None, 'upload_session_url': None}
    intent['state'] = 'COMMITTED'
    store._write_manifest(transaction)
    boundary('committed')
    return target
