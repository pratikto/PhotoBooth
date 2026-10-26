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
    from photobooth.kiosk_v2.watchdog import (WatchdogMonitor, supervise,
                                             windows_startup_script, systemd_user_unit)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-startup', type=Path, metavar='FILE.cmd',
                        help='Generate a startup file; does not install or run it')
    parser.add_argument('--startup-format', choices=('windows', 'systemd'),
                        help='Default: Windows cmd on Windows, systemd user service on Linux')
    parser.add_argument('--target-root', help='Absolute checkout path on the Ubuntu mini PC')
    parser.add_argument('--target-python', help='Absolute venv Python path on the Ubuntu mini PC')
    parser.add_argument('--check-recovery', action='store_true',
                        help='Read local v2 journals and print a redacted startup review; no launch')
    args, delivery = parser.parse_known_args(argv)
    # Validate before writing a file or starting a child. No config changes here.
    configure_delivery(delivery, environ=dict(os.environ))
    if args.check_recovery:
        if args.write_startup:
            parser.error('Select recovery review or startup generation')
        import json
        from photobooth.kiosk_v2.recovery import review_recovery, RECOVERY_EXIT
        report = review_recovery(ROOT)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report['status'] == 'CLEAR_FOR_MANUAL_START' else RECOVERY_EXIT
    if os.environ.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX') == '1':
        parser.error('Use the dedicated merchant Sandbox launcher; supervision does not host its backend.')
    if args.write_startup:
        kind = args.startup_format or ('windows' if os.name == 'nt' else 'systemd')
        try:
            if kind == 'systemd':
                if (args.target_root is None) != (args.target_python is None):
                    parser.error('Supply both Ubuntu target paths')
                if os.name == 'nt' and not args.target_root:
                    parser.error('Windows development requires explicit Ubuntu target paths')
                script = systemd_user_unit(args.target_root or ROOT, args.target_python or sys.executable, delivery)
            else:
                if os.name != 'nt' or args.target_root or args.target_python:
                    parser.error('Generate Windows cmd on Windows without Ubuntu target paths')
                script = windows_startup_script(ROOT, sys.executable, delivery)
            # Never overwrite an existing operator script.
            with args.write_startup.open('x', encoding='utf-8',
                                         newline='\r\n' if kind == 'windows' else '\n') as stream:
                stream.write(script)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        print('Startup file generated; inspect paths and session settings before manual installation.')
        return 0

    if args.startup_format or args.target_root or args.target_python:
        parser.error('Startup format/target paths require --write-startup')

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
                       MEONG_WATCHDOG_RUN_ID=run_id, MEONG_WATCHDOG_RECOVERY_GATE='1')
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
