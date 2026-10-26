"""Run v2 with an external liveness observer, or generate a Windows startup cmd.

No automatic restart/kill, Sandbox backend launch or startup installation.
Existing default/local and explicitly selected print/Drive settings are reused.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main(argv=None):
    from photobooth.kiosk_v2.delivery_options import configure_delivery
    from photobooth.kiosk_v2.watchdog import WatchdogMonitor, supervise, windows_startup_script

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-startup', type=Path, metavar='FILE.cmd',
                        help='Generate a Windows launcher; does not install or run it')
    args, delivery = parser.parse_known_args(argv)
    # Validate before writing a file or starting a child. No config changes here.
    configure_delivery(delivery, environ=dict(os.environ))
    if os.environ.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX') == '1':
        parser.error('Use the dedicated merchant Sandbox launcher; supervision does not host its backend.')
    if args.write_startup:
        if os.name != 'nt':
            parser.error('Generate the startup launcher on the Windows kiosk, using its own paths/Python.')
        try:
            script = windows_startup_script(ROOT, sys.executable, delivery)
            # Never overwrite an existing operator script.
            with args.write_startup.open('x', encoding='utf-8', newline='\r\n') as stream:
                stream.write(script)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        print('Startup launcher generated; inspect it before copying a shortcut to shell:startup.')
        return 0

    folder = ROOT / 'data' / 'diagnostics' / 'watchdog'
    folder.mkdir(parents=True, exist_ok=True)
    from photobooth.qris_session import KioskLease
    try:
        lease = KioskLease(folder / 'supervisor.lock')
    except RuntimeError:
        print('Another Meong supervisor is running. Close its kiosk normally.', file=sys.stderr)
        return 2
    try:
        with tempfile.TemporaryDirectory(prefix='meong-watchdog-') as temporary:
            run_id = uuid.uuid4().hex
            heartbeat = Path(temporary) / 'heartbeat.json'
            env = dict(os.environ, MEONG_WATCHDOG_HEARTBEAT=str(heartbeat),
                       MEONG_WATCHDOG_RUN_ID=run_id)
            command = [sys.executable, str(ROOT / 'tools' / 'run_portrait_v2.py'), *delivery]
            options = ({'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt'
                       else {'start_new_session': True})
            child = subprocess.Popen(command, cwd=ROOT, env=env, **options)
            report = folder / f'{run_id}.json'
            print(f'Watchdog report: {report}', flush=True)
            return supervise(child, heartbeat, report, WatchdogMonitor(run_id, child.pid))
    finally:
        lease.close()


if __name__ == '__main__':
    sys.exit(main())
