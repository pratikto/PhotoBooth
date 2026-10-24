"""Local merchant Sandbox trial; never a mock settlement or production launcher.

Prompt for credentials locally (no command-line key, file, or clipboard). The
GUI child receives a generated booth token, not the Midtrans server key. The
ordinary application camera/printing behavior is preserved. Transaction/visit
journals persist; stopping the launcher never cancels, pays, or deletes orders.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import time
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, ProxyHandler
import warnings

ROOT = Path(__file__).resolve().parent.parent
SIMULATOR_URL = 'https://simulator.sandbox.midtrans.com/v2/qris/index'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def trial_environments(parent: dict[str, str], merchant: str, key: str,
                       booth: str, port: int, root: Path = ROOT):
    """Separate backend credentials from kiosk environment; do not mutate parent."""
    if not isinstance(merchant, str) or re.fullmatch(r'[A-Za-z0-9_-]{1,64}', merchant) is None:
        raise ValueError('Invalid Sandbox Merchant ID')
    # A defensive operator guard, not proof that Midtrans accepts this key.
    if (not isinstance(key, str) or not key.startswith('SB-Mid-server-')
            or len(key) <= len('SB-Mid-server-') or len(key) > 512
            or any(c.isspace() for c in key) or not key.isascii()):
        raise ValueError('Use the Server Key from the Sandbox dashboard, not Client Key or Production')
    if not isinstance(booth, str) or re.fullmatch(r'PB[0-9]{3,8}', booth) is None:
        raise ValueError('Booth ID must be PB followed by 3 to 8 digits')
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError('Port must be 1024..65535')
    clean = {k: v for k, v in parent.items()
             if not k.startswith(('MIDTRANS_', 'MEONG_QRIS_')) and k != 'MEONG_PAYMENT_MODE'}
    directory = root / 'data' / 'qris-sandbox-trial' / merchant / booth
    common = dict(clean, MEONG_PAYMENT_MODE='qris-sandbox', MEONG_QRIS_MODE='sandbox',
                  PHOTOBOOTH_ID=booth, MEONG_QRIS_BOOTH_ID=booth,
                  MEONG_QRIS_BOOTH_TOKEN=secrets.token_urlsafe(36),
                  MEONG_QRIS_API_URL=f'http://127.0.0.1:{port}',
                  MEONG_QRIS_LOCAL_PREVIEW='1',
                  MEONG_QRIS_DB_PATH=str(directory / 'orders.sqlite'),
                  MEONG_QRIS_JOURNAL=str(directory / 'visit.json'),
                  PHOTOBOOTH_LOCAL_ONLY='1')
    backend = dict(common, MIDTRANS_SERVER_KEY=key, MIDTRANS_MERCHANT_ID=merchant)
    return backend, dict(common)


def current_simulator_qr(path: Path, endpoint: str, booth: str, *, after_ns: int = 0):
    """Read only a current verified Sandbox QR reference, never arbitrary journal data.

    This is operator convenience, NOT payment authority. Only the backend and
    existing kiosk grant protocol may authorize capture; this function cannot.
    """
    try:
        with path.open('rb') as stream:
            if os.fstat(stream.fileno()).st_mtime_ns <= after_ns:
                return None
            raw = stream.read(65537)
        if len(raw) > 65536:
            return None
        data = json.loads(raw)
        context = {'mode': 'sandbox', 'endpoint': endpoint, 'booth_id': booth}
        if (not isinstance(data, dict) or data.get('version') != 1
                or data.get('context') != context or data.get('phase') != 'WAITING'):
            return None
        order = data.get('order')
        if (not isinstance(order, dict) or order.get('state') != 'PENDING'
                or order.get('mode') != 'sandbox' or order.get('verification_pending')):
            return None
        order_id, url = order.get('order_id'), order.get('qr_url')
        if not isinstance(order_id, str) or re.fullmatch(r'[a-f0-9]{32}', order_id) is None:
            return None
        if not isinstance(url, str) or len(url) > 512:
            return None
        parsed = urlsplit(url)
        if (parsed.scheme != 'https' or parsed.hostname != 'api.sandbox.midtrans.com'
                or parsed.port not in (None, 443) or parsed.username or parsed.password
                or parsed.query or parsed.fragment
                or re.fullmatch(r'/v[24]/qris/[A-Za-z0-9_-]{1,128}/qr-code', parsed.path) is None):
            return None
        return order_id, url
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def wait_ready(server, endpoint: str, *, seconds: float = 15):
    """Only trust the spawned, still-running local Sandbox server's API v2 health."""
    opener = build_opener(ProxyHandler({}), NoRedirect())
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise RuntimeError('Sandbox backend stopped; check dependencies or local port')
        try:
            with opener.open(endpoint + '/api/health', timeout=.5) as response:
                data = json.loads(response.read(4097))
            if (isinstance(data, dict) and data.get('mode') == 'sandbox'
                    and data.get('api_version') == 2 and data.get('status') == 'ok'
                    and server.poll() is None):
                return
        except (OSError, ValueError):
            pass
        time.sleep(.2)
    raise RuntimeError('Sandbox backend did not become ready')


def stop(child):
    """Reap child processes, but never remove payment state or refund/cancel a charge."""
    if child is not None and child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()


def main(argv=None, *, environment_factory=trial_environments, gui_entry=('main.py',),
         trial_notice=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--booth-id', default=os.environ.get('PHOTOBOOTH_ID', 'PB001'))
    args = parser.parse_args(argv)
    server = gui = None
    backend_env = gui_env = None
    key = ''
    try:
        if sys.version_info < (3, 11):
            raise RuntimeError('Python 3.11+ required')
        # Fail before asking for secrets or launching a partially configured GUI.
        from importlib.util import find_spec
        if any(find_spec(module) is None for module in ('uvicorn', 'fastapi', 'pydantic', 'requests', 'kivy')):
            raise RuntimeError('Install requirements.txt and requirements-qris.txt in your Kivy environment')
        print('MIDTRANS SANDBOX ONLY. Do NOT scan/pay using a real banking or wallet app.', flush=True)
        print('Payment is NOT automatic after 8 seconds; use the official simulator.', flush=True)
        print(trial_notice or 'The existing photo/printer configuration is retained: completing a session may print.', flush=True)
        merchant = os.environ.get('MIDTRANS_MERCHANT_ID') or input('Sandbox Merchant ID: ').strip()
        key = os.environ.get('MIDTRANS_SERVER_KEY', '')
        if not key:
            # Never silently fall back to echoing a password in an unsupported terminal.
            with warnings.catch_warnings():
                warnings.simplefilter('error', getpass.GetPassWarning)
                key = getpass.getpass('Sandbox Server Key (hidden): ')
        backend_env, gui_env = environment_factory(dict(os.environ), merchant, key,
                                                args.booth_id, args.port)
        # Refuse an occupied port instead of accidentally connecting to another service.
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', args.port))
        server = subprocess.Popen([sys.executable, '-m', 'uvicorn',
            'photobooth.qris_server:build_sandbox_app', '--factory', '--host', '127.0.0.1',
            '--port', str(args.port), '--no-access-log'], cwd=ROOT, env=backend_env)
        backend_env.pop('MIDTRANS_SERVER_KEY', None)
        key = ''
        endpoint = gui_env['MEONG_QRIS_API_URL']
        wait_ready(server, endpoint)
        print('Local backend ready; this does NOT yet verify merchant credentials.', flush=True)
        print('Official QRIS simulator: ' + SIMULATOR_URL, flush=True)
        print('Choose a template in the GUI; its current Sandbox QR image URL will appear here.', flush=True)
        launch_ns = time.time_ns()
        gui = subprocess.Popen([sys.executable, *gui_entry], cwd=ROOT, env=gui_env)
        shown = None
        while gui.poll() is None:
            if server.poll() is not None:
                raise RuntimeError('Backend stopped. Preserve the journal; do not pay again')
            current = current_simulator_qr(Path(gui_env['MEONG_QRIS_JOURNAL']), endpoint, args.booth_id, after_ns=launch_ns)
            if current and current != shown:
                shown = current
                print('\nSandbox order: ' + current[0], flush=True)
                print('Paste this QR image URL into the official simulator, then Scan QR:\n' + current[1], flush=True)
                print('Check the simulator amount; the GUI should advance only after simulated payment.', flush=True)
            time.sleep(1)
        return gui.returncode
    except KeyboardInterrupt:
        print('\nStopped. Persistent orders/journals retained; no automatic cancel or replay.', flush=True)
        return 130
    except (EOFError, getpass.GetPassWarning):
        print('Use an interactive terminal with hidden password input. Never paste a key in chat.', file=sys.stderr)
        return 2
    except (ValueError, OSError, RuntimeError):
        # No exception repr, URLs with credentials, environment dumps, or secret values.
        print('Sandbox setup stopped. Check Python/dependencies, Sandbox credentials, booth ID and free port. '
              'Do not delete payment journals to bypass recovery.', file=sys.stderr)
        return 2
    finally:
        stop(gui)
        stop(server)
        if backend_env is not None:
            backend_env.clear()
        if gui_env is not None:
            gui_env.clear()
        key = ''


if __name__ == '__main__':
    sys.exit(main())
