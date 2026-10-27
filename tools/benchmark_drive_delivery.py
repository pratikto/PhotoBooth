"""Deterministic offline comparison of actual baseline/current worker and cache.

No network, Drive configuration, customer data or sleep. Times are virtual
request costs, not measured Google Drive throughput. Run from any directory.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image
from photobooth.booth_storage import BoothWorkspace
from photobooth.booth_sync import BoothDriveWorker
from photobooth.content_cache import ContentCache
from photobooth.catalog import get_templates
from photobooth.retention import retention_metadata
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import build_session_plans

BASE = 'fcabfbb8559778055631ff3a066f14108392ef71'


def baseline_class(path, name):
    source = subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE+':'+path], text=True)
    namespace = {'__name__': 'offline_baseline'}
    exec(compile(source, BASE+':'+path, 'exec'), namespace)
    return namespace[name]


class Client:
    def __init__(self, clock):
        self.clock = clock
        self.files = {'Global_Advertisement/large.mp4': b'x'*(8*512*1024)}
        self.chunk_hook = None
        self.reserves = []
        self.chunk_requests = 0
        self.download_bytes = 0
        self.bound_at = None

    def reserve_transactions(self, slots):
        self.reserves.append(len(slots));self.clock[0] += .1*len(slots)
        return [{**s, 'folder_id':s['transaction_id'],
                 'folder_url':'https://drive.google.com/drive/folders/'+s['transaction_id'],
                 'link_verified':True,'photo_number_layout':1} for s in slots]

    def asset_manifest(self):
        self.clock[0] += .2
        entries=[{'id':path,'path':path,'size':len(data),'md5':hashlib.md5(data).hexdigest()}
                 for path,data in self.files.items()]
        return {'version':hashlib.md5(json.dumps(entries).encode()).hexdigest(),'files':entries}

    def asset_chunk(self, entry, offset, length):
        self.clock[0] += 1;self.chunk_requests += 1;self.download_bytes += length
        if self.chunk_hook:
            hook=self.chunk_hook;self.chunk_hook=None;hook()
        return self.files[entry['path']][offset:offset+length]

    def bind_transaction(self, manifest):
        self.bound_at=self.clock[0];self.clock[0] += .3
        return {'folder_id':manifest['transaction_id'],
                'folder_url':'https://drive.google.com/drive/folders/'+manifest['transaction_id']}

    def register_retention(self, folder, tx, started):
        self.clock[0] += .2;return retention_metadata(tx,started)

    def upload_file(self, folder, tx, relative, path, **kwargs):
        self.clock[0] += .5
        return {'id':'fixture-file','size':path.stat().st_size,'md5Checksum':hashlib.md5(path.read_bytes()).hexdigest()}


def run(worker_type, cache_type):
    clock=[100.0]
    with TemporaryDirectory() as folder, patch('time.monotonic',side_effect=lambda:clock[0]):
        w=BoothWorkspace(folder);w.prepare();cache=cache_type(w);cache.load()
        client=Client(clock);worker=worker_type(w,client,cache);queued=[]
        def arrival():
            slot=w.claim();store=TransactionStore(w.root,w.counter_path,w.booth_id,layout_version=2)
            plan=build_session_plans(get_templates(),{'template_a':1})[0]
            tx=store.start_transaction([plan],transaction_id=slot['transaction_id'],folder_path=slot['staging_path'])
            tx.manifest.update(drive_intent=True,drive_claim_token=slot['claim_token']);store._write_manifest(tx)
            store.save_raw_photo(tx,plan,Image.new('RGB',(8,8)), 'photo.jpg','capture');store.complete_transaction(tx)
            queued.append(clock[0]);worker.kick()
        client.chunk_hook=arrival
        worker.run_once();worker._wake.clear();worker.run_once()
        wait=round(client.bound_at-queued[0],3)
        # Finish content before measuring a one-slot replenishment independently.
        if getattr(cache,'pending',False):cache.sync(client)
        client.reserves.clear();w.claim();worker.run_once()
        reserve_sizes=list(client.reserves)
        client.files['Local/Advertisement/new.mp4']=b'new'
        before=(client.chunk_requests,client.download_bytes)
        cache.sync(client)
        return {'customer_wait_after_arrival_seconds':wait,
                'reserve_request_sizes_after_one_claim':reserve_sizes,
                'reserve_slots_revalidated_after_one_claim':sum(reserve_sizes),
                'content_requests_new_generation':client.chunk_requests-before[0],
                'content_bytes_new_generation':client.download_bytes-before[1]}


def main():
    before=run(baseline_class('photobooth/booth_sync.py','BoothDriveWorker'),
               baseline_class('photobooth/content_cache.py','ContentCache'))
    after=run(BoothDriveWorker,ContentCache)
    print(json.dumps({'baseline':BASE,'kind':'deterministic offline simulation',
                     'assumptions':{'chunk_seconds':1,'manifest_seconds':.2,'reserve_slot_seconds':.1},
                     'before':before,'after':after,
                     'limits':'Virtual request costs; no evidence of production Drive speed or five-minute root cause.'},indent=2))


if __name__ == '__main__':main()
