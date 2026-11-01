"""Abrupt-exit synthetic private-draft fixture, never a device/provider route."""
import os
from pathlib import Path
import sys
from unittest.mock import patch

from PIL import Image

from photobooth.catalog import get_templates
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_store import PostPreviewStore


def main():
    root, stage, retake = Path(sys.argv[1]), sys.argv[2], bool(int(sys.argv[3]))
    ledger = PostPreviewStore(root/'drafts.db')
    lease = ledger.create('PB001', 'visitA', {'template_a': 2})
    photos = PrivateDraftPhotos(ledger, root/'private')
    template = get_templates()[0]
    image = Image.new('RGB', (48, 32), (30, 90, 150))
    def revision(): return ledger.inspect(lease)['revision']
    if retake:
        for slot in range(3): photos.capture(lease, template, image, slot=slot, revision=revision())
        photos.request_retake(lease, template, 1, revision=revision())
    def fault(name):
        if name == stage: os._exit(73)
    with patch('photobooth.capture_journal.boundary', side_effect=fault):
        photos.capture(lease, template, image, slot=1 if retake else 0,
                       revision=revision(), retake=retake)
    raise RuntimeError('Crash boundary did not run')


if __name__ == '__main__': main()
