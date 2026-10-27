"""Serve the existing v2 Sandbox backend for a separately configured Android client.

Run locally with your own TLS certificate, or on loopback behind existing HTTPS
ingress. This helper never deploys a server or embeds merchant credentials in APKs.
"""
import argparse
import getpass
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.run_qris_sandbox import trial_environments, SIMULATOR_URL
from photobooth.kiosk_v2.android_settings import validated, DEFAULTS
from photobooth.manifest_io import write_json_atomic


def backend_profile(parent, merchant, key, booth, port, public_url, *, root=ROOT):
    backend, gui=trial_environments(parent,merchant,key,booth,port,Path(root))
    settings=validated({**DEFAULTS,'sandbox_enabled':True,'api_url':public_url,
                        'booth_id':booth,'booth_token':gui['MEONG_QRIS_BOOTH_TOKEN']})
    directory=Path(root)/'data/android-sandbox-backend'/merchant/booth
    directory.mkdir(parents=True,exist_ok=True)
    credentials=directory/'booth-auth.json'
    if credentials.is_symlink():
        raise ValueError('Linked booth credentials are not allowed')
    if credentials.exists():
        if credentials.stat().st_size>8192:
            raise ValueError('Invalid saved booth credentials')
        data=json.loads(credentials.read_text(encoding='utf-8'))
        if data.get('booth_id')!=booth or data.get('api_url')!=public_url:
            raise ValueError('Preserve the existing backend/booth identity')
        settings=validated({**settings,'booth_token':data.get('booth_token')})
    else:
        write_json_atomic(credentials,{'booth_id':booth,'api_url':public_url,'booth_token':settings['booth_token']})
    credentials.chmod(0o600)
    export=directory/'mobile-settings.json'
    write_json_atomic(export,settings);export.chmod(0o600)
    backend.update(MEONG_QRIS_DB_PATH=str(directory/'orders.sqlite'),
                   MEONG_QRIS_BOOTH_TOKEN=settings['booth_token'],
                   PHOTOBOOTH_V2_PRINT='0',PHOTOBOOTH_V2_DRIVE='0')
    return backend,export


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-url',required=True,help='HTTPS base URL reachable from the Android device')
    parser.add_argument('--booth',default='PB001')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--tls-cert',type=Path)
    parser.add_argument('--tls-key',type=Path)
    args=parser.parse_args(argv)
    if bool(args.tls_cert)!=bool(args.tls_key) or (args.host not in {'127.0.0.1','localhost'} and not args.tls_cert):
        parser.error('LAN binding requires both TLS certificate/key; loopback can use existing HTTPS ingress')
    merchant=input('Sandbox Merchant ID: ').strip()
    key=getpass.getpass('Sandbox Server Key (hidden, backend only): ')
    try:
        backend,export=backend_profile(dict(os.environ),merchant,key,args.booth,args.port,args.public_url)
    except (ValueError,OSError):
        print('Invalid or conflicting Sandbox configuration; no server was started.',file=sys.stderr)
        return 2
    print('Private Android booth configuration saved at:',export)
    print('Transfer only booth settings locally. Never share this file or merchant keys in chat/Git.')
    print('Official simulator:',SIMULATOR_URL)
    command=[sys.executable,'-m','uvicorn','photobooth.qris_server:build_sandbox_app','--factory',
             '--host',args.host,'--port',str(args.port),'--no-access-log']
    if args.tls_cert:
        command.extend(['--ssl-certfile',str(args.tls_cert),'--ssl-keyfile',str(args.tls_key)])
    return subprocess.call(command,cwd=ROOT,env=backend)


if __name__=='__main__':
    sys.exit(main())
