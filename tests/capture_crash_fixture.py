"""AR-04 abrupt-exit worker with tiny generated image, no camera/customer data."""
import os
from pathlib import Path
import sys
from unittest.mock import patch

from PIL import Image
from photobooth.catalog import get_templates
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import build_session_plans


def main(root, stage):
    root=Path(root)
    store=TransactionStore(root/'photos',root/'counter.json',capture_protocol=1)
    plan=build_session_plans(get_templates(),{'template_a':1})[0]
    tx=store.start_transaction([plan])
    if stage.startswith('output_'):
        from photobooth.capture_journal import publish_output
        paths=[store.save_raw_photo(tx,plan,Image.new('RGB',(32,24),(17,83,201)),
               f'photo_{i+1:02d}.jpg','capture') for i in range(3)]
        def stop_output(boundary):
            if boundary==stage:os._exit(71)
        with patch('photobooth.capture_journal.boundary',side_effect=stop_output):
            output=publish_output(store,tx,plan,paths,
                lambda target:Image.new('RGB',(640,1920),(17,83,201)).save(target,format='PNG'))
            store.record_output(tx,plan.session_id,paths,output)
        if stage=='output_committed':os._exit(71)
        raise AssertionError('Requested output boundary not reached')
    def stop(boundary):
        if boundary==stage:os._exit(71)
    with patch('photobooth.capture_journal.boundary',side_effect=stop):
        store.save_raw_photo(tx,plan,Image.new('RGB',(32,24),(17,83,201)),'photo_01.jpg','capture')
    raise AssertionError('Requested boundary not reached')


if __name__=='__main__':main(*sys.argv[1:])
