"""Actual baseline/current scheduling with failed old claims and virtual requests.

Uses temporary synthetic photos and fake monotonic/wall clocks. No credentials,
network, sleep, real printer, deletion or changes to an operator's data.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image
from photobooth.booth_storage import BoothWorkspace
from photobooth.booth_sync import BoothDriveWorker
from photobooth.catalog import get_templates
from photobooth.retention import retention_metadata
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import build_session_plans

BASE = 'e3ac0f94af1402ae4eec1de0295fa43e6bc8c19e'


def transaction(workspace, files, failed=False):
    slot=workspace.claim()
    store=TransactionStore(workspace.root,workspace.counter_path,workspace.booth_id,layout_version=2)
    plan=build_session_plans(get_templates(),{'template_a':1})[0]
    tx=store.start_transaction([plan],transaction_id=slot['transaction_id'],folder_path=slot['staging_path'])
    tx.manifest.update(drive_intent=True,drive_claim_token=slot['claim_token'])
    if failed:
        tx.manifest.update(drive_folder_id='original-reserved',drive_binding_error='DRIVE_RETRY')
    store._write_manifest(tx)
    for n in range(files):store.save_raw_photo(tx,plan,Image.new('RGB',(8,8)),f'photo_{n}.jpg','capture')
    store.complete_transaction(tx)
    return tx


def simulate(worker_type):
    now=[100.0];calls=[];finished=[]
    with TemporaryDirectory() as folder,patch('time.monotonic',side_effect=lambda:now[0]),patch('time.time',side_effect=lambda:1000000+now[0]):
        w=BoothWorkspace(folder);w.prepare()
        bad=[transaction(w,1,failed=True) for _ in range(3)];good=transaction(w,5)
        client=Mock();client.reserve_transactions.return_value=[]
        def bind(manifest):
            tx=manifest['transaction_id'];calls.append(('bind',tx))
            if tx!=good.transaction_id:now[0]+=5  # The returned different folder triggers the actual guard.
            return {'folder_id':tx,'folder_url':'https://drive.google.com/drive/folders/'+tx}
        def upload(folder,tx,relative,path,**kw):
            calls.append(('upload',tx));now[0]+=8
            if sum(action=='upload' for action,_ in calls)==5:finished.append(now[0])
            return {'id':relative,'size':path.stat().st_size,'md5Checksum':hashlib.md5(path.read_bytes()).hexdigest()}
        client.bind_transaction.side_effect=bind;client.upload_file.side_effect=upload
        client.register_retention.side_effect=lambda folder,tx,started:retention_metadata(tx,started)
        worker=worker_type(w,client)
        for _ in range(5):worker.run_once()
        manifest=json.loads(good.manifest_path.read_text())
        assert manifest['upload_status']=='UPLOAD_COMPLETE'
        assert all(json.loads(tx.manifest_path.read_text())['drive_folder_id']=='original-reserved' for tx in bad)
        return {'queued_to_upload_complete_virtual_seconds':finished[0]-100,
                'failed_old_bind_requests':sum(a=='bind' and tx!=good.transaction_id for a,tx in calls),
                'healthy_file_uploads':sum(a=='upload' for a,_ in calls),
                'first_network_action_lane':'healthy' if calls[0][1]==good.transaction_id else 'failed_old',
                'original_reserved_folders_preserved':True}


def main():
    path='photobooth/booth_sync.py'
    source=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+path],text=True)
    namespace={'__name__':'baseline_retry'};exec(compile(source,BASE+':'+path,'exec'),namespace)
    print(json.dumps({'baseline':BASE,'kind':'offline deterministic retry simulation',
        'assumptions':{'failed_old_transactions':3,'healthy_files':5,'failed_bind_virtual_seconds':5,'file_upload_virtual_seconds':8},
        'before':simulate(namespace['BoothDriveWorker']),'after':simulate(BoothDriveWorker),
        'limits':'Synthetic scheduling evidence; not a forecast or measurement of Google Drive speed.'},indent=2))


if __name__=='__main__':main()
