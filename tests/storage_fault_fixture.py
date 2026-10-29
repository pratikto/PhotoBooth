"""CAP-20 injected OS write failures in disposable real paid-photo processes."""
from contextlib import ExitStack
import errno
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np
from PIL import Image
from photobooth.catalog import get_templates
from photobooth.manifest_io import write_json_atomic
from photobooth.kiosk_v2.photos import PhotoTest
from tests.fulfillment_crash_fixture import AllocationHarness


class StorageFault:
    def __init__(self, photo, manifest_path, stage, error_number, kind='capture'):
        self.photo, self.path, self.stage, self.number = photo, manifest_path, stage, error_number
        self.kind = kind
        self.image_format = 'PNG' if kind == 'output' else 'JPEG'
        self.image_suffix = '.tmp.png' if kind == 'output' else '.tmp.jpg'
        self.stack = ExitStack()
        self.fired = False
        self.manifest_armed = False
        self.image_armed = False

    def fail(self):
        assert not self.fired
        self.fired = True
        raise OSError(self.number, 'Synthetic targeted storage fault')

    def __enter__(self):
        original_write = self.photo.store._write_manifest
        def manifest_write(transaction):
            intents = (list(transaction.manifest.get('output_intents', {}).values()) if self.kind == 'output'
                       else list(transaction.manifest.get('capture_intents', {}).values()))
            state = intents[-1]['state'] if intents else None
            selected = {'intent_manifest': 'INTENT', 'staged_manifest': 'STAGED',
                        'commit_manifest': 'COMMITTED'}.get(self.stage)
            self.manifest_armed = (self.stage == 'initial_manifest'
                or self.stage == 'complete_manifest' and transaction.manifest['status'] == 'COMPLETED'
                or selected is not None and state == selected)
            try:
                return original_write(transaction)
            finally:
                self.manifest_armed = False
        self.stack.enter_context(patch.object(self.photo.store, '_write_manifest', side_effect=manifest_write))
        original_replace = os.replace
        def replace(source, destination, *args, **options):
            if Path(destination) == self.path and (self.manifest_armed or self.stage == 'selection_manifest'):
                self.fail()
            return original_replace(source, destination, *args, **options)
        self.stack.enter_context(patch('os.replace', side_effect=replace))
        original_open = Path.open
        def open_path(path, mode='r', *args, **options):
            if self.stage == 'image_open' and mode == 'xb' and path.name.endswith(self.image_suffix):
                self.fail()
            return original_open(path, mode, *args, **options)
        self.stack.enter_context(patch.object(Path, 'open', new=open_path))
        original_save = Image.Image.save
        def save(image, target, *args, **options):
            if self.stage == 'image_write' and options.get('format') == self.image_format:
                if hasattr(target, 'write'):
                    target.write(b'SYNTHETIC PARTIAL IMAGE')
                else:
                    Path(target).write_bytes(b'SYNTHETIC PARTIAL IMAGE')
                self.fail()
            return original_save(image, target, *args, **options)
        self.stack.enter_context(patch.object(Image.Image, 'save', new=save))
        def boundary(name):
            if name == ('output_intent' if self.kind == 'output' else 'intent'):
                self.image_armed = True
        self.stack.enter_context(patch('photobooth.capture_journal.boundary', side_effect=boundary))
        original_fsync = os.fsync
        def fsync(descriptor):
            if self.stage == 'image_fsync' and self.image_armed:
                self.fail()
            return original_fsync(descriptor)
        self.stack.enter_context(patch('os.fsync', side_effect=fsync))
        original_link = os.link
        def link(*args, **options):
            if self.stage == 'publish':
                self.fail()
            return original_link(*args, **options)
        self.stack.enter_context(patch('os.link', side_effect=link))
        return self

    def __exit__(self, *exception):
        return self.stack.__exit__(*exception)


def main(root, kind, stage, error_number):
    number = int(error_number)
    assert number in {errno.ENOSPC, errno.EACCES} and kind in {'capture', 'retake', 'output', 'initial'}
    harness = AllocationHarness(root)
    harness.forbid_new_charge()
    ticket = sys.stdin.read(201)
    harness.flow.customer_claim(ticket)
    binding = harness.flow.resume_binding()
    photo = PhotoTest(harness.photo_root)
    if kind != 'initial':
        view = photo.restore(get_templates(), binding, harness.flow.resume_permit())
        harness.flow.confirm_resume(binding['transaction_id'], view['phase'])
    if kind == 'retake' and stage != 'selection_manifest':
        photo.retake(1)
    manifest_path = harness.photo_root / 'photos' / binding['transaction_id'] / 'manifest.json'
    fault = StorageFault(photo, manifest_path, stage, number, kind)
    try:
        with fault:
            if kind == 'initial':
                photo.restore_allocated(get_templates(), {'template_a': 2}, binding,
                                        harness.flow.resume_permit(), 'RESERVED')
            elif kind == 'output':
                photo.compose()
            elif stage == 'selection_manifest':
                photo.retake(1)
            else:
                photo.capture(np.full((24, 32, 3), 247, dtype=np.uint8))
    except OSError as error:
        assert error.errno == number and fault.fired
        photo.hide_private()
        assert photo.snapshot() == {'phase': 'claim_required'}
        harness.flow.lock_customer()
        reason = ('COMPOSITION_FAILED' if kind == 'output' else 'PHOTO_STATE_UNAVAILABLE'
                  if kind == 'initial' or stage == 'selection_manifest' else 'CAPTURE_FAILED')
        harness.flow.report_fulfillment_issue(reason)
        write_json_atomic(Path(root) / 'fault.json',
                          {'kind': kind, 'stage': stage, 'errno': number, 'acknowledged': False})
        os._exit(120)
    raise AssertionError('Injected write fault did not prevent operation ACK')


if __name__ == '__main__':
    main(*sys.argv[1:])
