"""CAP-11–13 real exit worker using original ownership and saved tiny frames."""
import json
import os
import sys
from unittest.mock import patch

import numpy as np
from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoTest
from tests.fulfillment_crash_fixture import AllocationHarness


def crash_retake(root, stage):
    harness = AllocationHarness(root)
    harness.forbid_new_charge()
    ticket = sys.stdin.read(201)
    harness.flow.customer_claim(ticket)
    photo = PhotoTest(harness.photo_root)
    view = photo.restore(get_templates(), harness.flow.resume_binding(), harness.flow.resume_permit())
    assert view['phase'] == 'review' and view['captured'] == 3
    harness.flow.confirm_resume(view['transaction_id'], view['phase'])
    photo.retake(1)
    saved = json.loads(photo.transaction.manifest_path.read_text())
    assert saved['sessions'][0]['pending_retake_index'] == 1
    assert saved['sessions'][0]['retake_used'] is False
    if stage == 'selection':
        assert len(saved['capture_intents']) == 3
        os._exit(100)
    codes = {'intent': 101, 'temporary': 102, 'staged': 103, 'published': 104, 'committed': 105}
    if stage not in codes:
        raise ValueError('Unknown retake crash boundary')
    def stop(boundary):
        if boundary == stage:
            latest = json.loads(photo.transaction.manifest_path.read_text())
            intent = next(i for i in latest['capture_intents'].values() if i['role'] == 'retake')
            record = latest['sessions'][0]
            assert intent['slot'] == 1 and intent['selected_photo'] == record['raw_photos'][1]['path']
            expected = 'COMMITTED' if stage == 'committed' else 'STAGED' if stage in {'staged', 'published'} else 'INTENT'
            assert intent['state'] == expected
            assert (photo.transaction.folder_path / intent['path']).exists() == (stage in {'published', 'committed'})
            assert (photo.transaction.folder_path / intent['temporary_path']).exists() == (stage in {'temporary', 'staged'})
            assert record['retake_used'] == (stage == 'committed')
            assert sum(p['role'] == 'retake' for p in record['raw_photos']) == (1 if stage == 'committed' else 0)
            if stage == 'committed':
                assert 'pending_retake_index' not in record
            else:
                assert record['pending_retake_index'] == 1
            os._exit(codes[stage])
    with patch('photobooth.capture_journal.boundary', side_effect=stop):
        photo.capture(np.full((24, 32, 3), 247, dtype=np.uint8))
    raise AssertionError('Retake crash boundary was not reached')


if __name__ == '__main__':
    crash_retake(*sys.argv[1:])
