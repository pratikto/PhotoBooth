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


def validate_image(path, expected_hash, *, image_format=None, expected_size=None):
    from photobooth.booth_storage import checked_path
    path = checked_path(path)
    if not path.is_file() or not 0 < path.stat().st_size <= 64*1024*1024:
        raise CaptureRecoveryRequired('Saved media is missing or oversized')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise CaptureRecoveryRequired('Saved media hash mismatch')
    with Image.open(path) as image:
        if image.width <= 0 or image.height <= 0 or image.width*image.height > 40_000_000:
            raise CaptureRecoveryRequired('Saved media dimensions exceed the recovery limit')
        image.load()
        if (image_format and image.format != image_format) or (expected_size and image.size != tuple(expected_size)):
            raise CaptureRecoveryRequired('Saved media format/dimensions mismatch')


def publish_output(store, transaction, session, final_photos, render):
    from photobooth.booth_storage import checked_path
    transaction.manifest = json.loads(checked_path(transaction.manifest_path).read_text(encoding='utf-8'))
    manifest = transaction.manifest
    record = store._session_record(transaction, session.session_id)
    raw = {p['path']: p for p in record['raw_photos']}
    selected = [store._relative_path(transaction, p) for p in final_photos]
    for relative in selected:
        photo = raw.get(relative) or {}
        validate_image(transaction.folder_path/relative, photo.get('sha256'), image_format='JPEG')
    output = checked_path(store.output_path(transaction, session))
    if output.exists() or session.session_id in manifest.get('output_intents', {}):
        raise CaptureRecoveryRequired('Existing output requires exact recovery')
    output.parent.mkdir(parents=True, exist_ok=True)
    operation = uuid.uuid4().hex
    temporary = checked_path(output.with_name('.'+output.stem+'.'+operation+'.tmp.png'))
    intent = {'operation_id': operation, 'session_id': session.session_id,
              'path': output.relative_to(transaction.folder_path).as_posix(),
              'temporary_path': temporary.relative_to(transaction.folder_path).as_posix(),
              'final_photos': selected, 'state': 'INTENT'}
    manifest.setdefault('output_intents', {})[session.session_id] = intent
    store._write_manifest(transaction)
    boundary('output_intent')
    with temporary.open('xb'):
        pass
    render(temporary)
    # Windows CRT _commit/fsync requires a writable descriptor. Reopen without
    # truncation after the renderer has closed its writer; bytes stay unchanged.
    with temporary.open('r+b') as stream:
        os.fsync(stream.fileno())
    digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
    validate_image(temporary, digest, image_format='PNG', expected_size=(640,1920))
    intent.update(state='STAGED', sha256=digest, size_bytes=temporary.stat().st_size)
    store._write_manifest(transaction)
    boundary('output_staged')
    os.link(temporary, output, follow_symlinks=False)
    sync_directory(output.parent)
    temporary.unlink()
    sync_directory(output.parent)
    boundary('output_published')
    return output


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
    if target.exists() or any(i.get('path') == relative.as_posix() and i.get('state') != 'VOID_BEFORE_FRAME'
                               for i in latest.get('capture_intents', {}).values()):
        raise CaptureRecoveryRequired('Existing capture evidence must not be replaced')
    target.parent.mkdir(parents=True, exist_ok=True)
    operation = uuid.uuid4().hex
    temporary = checked_path(target.with_name('.'+target.stem+'.'+operation+'.tmp.jpg'))
    intent = {'operation_id': operation, 'session_id': session.session_id,
              'slot': slot, 'role': role,
              'attempt': 1+sum(i.get('path') == relative.as_posix() for i in latest.get('capture_intents',{}).values()),
              'path': relative.as_posix(),
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
    commit_capture(store, transaction, intent)
    boundary('committed')
    return target


def commit_capture(store, transaction, intent):
    latest = transaction.manifest
    record = store._session_record(transaction, intent['session_id'])
    record['status'] = 'CAPTURING'
    record['raw_photos'].append({'path': intent['path'], 'role': intent['role'],
                                 'operation_id': intent['operation_id'], 'sha256': intent['sha256']})
    if intent['role'] == 'retake':
        record.update(retake_used=True, selected_photo=intent['selected_photo'])
        record.pop('pending_retake_index', None)
    latest['upload_files'][intent['path']] = {
        'path': intent['path'], 'content_version': intent['operation_id'],
        'status': 'PENDING_UPLOAD' if latest.get('drive_folder_id') or latest.get('drive_intent') else 'LOCAL_ONLY',
        'size_bytes': intent['size_bytes'], 'drive_file_id': None, 'md5_checksum': None, 'upload_session_url': None}
    intent['state'] = 'COMMITTED'
    store._write_manifest(transaction)
