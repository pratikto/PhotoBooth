"""Start loopback mock backend and the real main Kivy GUI; no merchant account.

Default: no physical printing. --allow-print explicitly enables the saved
printer configuration and can consume paper. Existing photo/Drive setup is
retained; use a development profile rather than a customer deployment.
"""
import argparse
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--allow-print', action='store_true')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--scenario', choices=['settlement','expire','deny','pending'], default='settlement')
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('port must be 1024..65535')
    env = dict(os.environ)
    booth = env.get('PHOTOBOOTH_ID', 'PB001')
    env.update(MEONG_PAYMENT_MODE='qris-mock', MEONG_QRIS_MODE='mock',
        MEONG_QRIS_API_URL=f'http://127.0.0.1:{args.port}', MEONG_QRIS_LOCAL_PREVIEW='1',
        MEONG_QRIS_BOOTH_ID=booth, MEONG_QRIS_BOOTH_TOKEN=secrets.token_urlsafe(36),
        MEONG_QRIS_DB_PATH=str(ROOT/'data'/'qris-mock.sqlite'),
        MEONG_QRIS_JOURNAL=str(ROOT/'data'/'qris-mock-visit.json'),
        MEONG_QRIS_MOCK_PRINT='1' if args.allow_print else '0',
        MEONG_QRIS_MOCK_SCENARIO=args.scenario, PHOTOBOOTH_LOCAL_ONLY='1')
    for name in ('MIDTRANS_SERVER_KEY', 'MIDTRANS_MERCHANT_ID'):
        env.pop(name, None)
    server = subprocess.Popen([sys.executable, '-m', 'uvicorn',
        'photobooth.qris_server:build_sandbox_app', '--factory', '--host', '127.0.0.1',
        '--port', str(args.port), '--no-access-log'], cwd=ROOT, env=env)
    try:
        ready = False
        for _ in range(50):
            if server.poll() is not None:
                raise RuntimeError('Mock backend could not start; check dependencies/port')
            try:
                with urllib.request.urlopen(env['MEONG_QRIS_API_URL'] + '/api/health', timeout=.5) as response:
                    import json
                    ready = json.load(response).get('mode') == 'mock'
                if ready: break
            except (OSError, ValueError): pass
            time.sleep(.2)
        if not ready:
            raise RuntimeError('Mock backend did not become ready')
        print('MEONG MOCK: no bank transfer; automatic simulated payment after 8 seconds.')
        return subprocess.call([sys.executable, 'main.py'], cwd=ROOT, env=env)
    finally:
        server.terminate()
        try: server.wait(timeout=10)
        except subprocess.TimeoutExpired: server.kill(); server.wait()


if __name__ == '__main__':
    sys.exit(main())
