"""Prepare a fresh supervised device trial; all payments remain synthetic.

Check-only is read-only. Device acquisition and separately consented physical
paper/cloud effects belong to the unchanged child pilot, never this preflight.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.check_post_preview_pilot import CONFLICTING_PROFILES, inspect
from tools.run_post_preview_checkout_pilot import validate_private_root, validate_printer, validate_drive


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check-only', action='store_true', help='No camera, printer, cloud or filesystem writes')
    p.add_argument('--private-root', type=Path, help='Optional unused dedicated folder; otherwise generated')
    p.add_argument('--size', choices=('452x900', '800x1280'), default='452x900')
    p.add_argument('--camera-index', type=int, default=0)
    p.add_argument('--enable-real-printer', action='store_true')
    p.add_argument('--accept-real-paper', action='store_true')
    p.add_argument('--enable-real-drive', action='store_true')
    p.add_argument('--accept-public-test-upload', action='store_true')
    return p


def child_environment(environ, camera_index):
    child = dict(environ)
    # A previous offscreen/dummy test must not silently hide the physical UI
    # or mute the speaker trial. Preserve explicitly configured real drivers.
    if child.get('SDL_VIDEODRIVER') in {'offscreen', 'dummy'}:
        child.pop('SDL_VIDEODRIVER')
    if child.get('SDL_AUDIODRIVER') == 'dummy':
        child.pop('SDL_AUDIODRIVER')
    child.update({name: '0' for name in CONFLICTING_PROFILES})
    child.update(PHOTOBOOTH_LOCAL_ONLY='1', PHOTOBOOTH_CAMERA='1',
                 PHOTOBOOTH_CAMERA_INDEX=str(camera_index), PHOTOBOOTH_AUDIO='1',
                 PHOTOBOOTH_FACE_TRIGGER='0', PHOTOBOOTH_PALM_TRIGGER='0')
    return child


def source_head(root):
    try:
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                capture_output=True, text=True, timeout=8, check=True)
        value = result.stdout.strip()
        return value if len(value) == 40 and all(c in '0123456789abcdef' for c in value) else 'unknown'
    except (OSError, subprocess.SubprocessError):
        return 'unknown'


def main(argv=None):
    args = parser().parse_args(argv)
    if not 0 <= args.camera_index <= 32:
        print('BLOCKED: camera index must be between 0 and 32.', file=sys.stderr)
        return 2
    environment = child_environment(os.environ, args.camera_index)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:12]
    try:
        validate_printer(args, environment)
        validate_drive(args, environment)
        selected = args.private_root or ROOT/'work'/('postpay-device-'+stamp)
        if not selected.is_absolute():
            selected = ROOT/selected
        private_root = validate_private_root(selected, project_root=ROOT)
        report_root = validate_private_root(ROOT/'work'/'postpay-device-reports'/stamp, project_root=ROOT)
    except ValueError as error:
        print('BLOCKED: '+str(error), file=sys.stderr)
        return 2
    result = inspect(ROOT, environment=environment)
    for check in result['checks']:
        print(f"{check['status']:7} {check['name']}: {check['detail']}")
    print('RESULT: '+result['status'], flush=True)
    if result['status'] != 'READY_FOR_SUPERVISED_SYNTHETIC_PILOT':
        print('Use the same interpreter for setup and launch; resolve BLOCKED checks first.')
        return 2
    if args.check_only:
        print('Check-only complete: no devices opened and no files created. Hardware acceptance is NOT_RUN.')
        return 0
    command = [sys.executable, str(ROOT/'tools'/'run_post_preview_checkout_pilot.py'),
               '--synthetic-payment-only', '--private-root', str(private_root), '--size', args.size]
    for name in ('enable_real_printer', 'accept_real_paper', 'enable_real_drive', 'accept_public_test_upload'):
        if getattr(args, name):
            command.append('--'+name.replace('_', '-'))
    # The report is a sibling, never inside the child's still-empty private
    # root: otherwise the original occupied-root safety guard would reject it.
    report_root.mkdir(parents=True, exist_ok=False)
    metadata = dict(schema_version=1, source_sha=source_head(ROOT),
                    started_at_utc=datetime.now(timezone.utc).isoformat(),
                    python=platform.python_version(), platform=platform.system(),
                    private_root_name=private_root.name, size=args.size, camera_index=args.camera_index,
                    payment='SYNTHETIC_ONLY', printer='REAL_OPT_IN' if args.enable_real_printer else 'VIRTUAL',
                    drive='REAL_TEST_OPT_IN' if args.enable_real_drive else 'SYNTHETIC_NONDOWNLOADABLE',
                    hardware_acceptance='NOT_RUN',
                    source_integrity='HEAD_ONLY_NOT_A_CLEAN_TREE_ATTESTATION', state='STARTING')
    report = report_root/'session.json'
    with report.open('x', encoding='utf-8') as stream:
        json.dump(metadata, stream, indent=2)
        stream.write('\n')
    print('Test folder: '+str(private_root))
    print('Local session record: '+str(report))
    print('Synthetic payment only. Manual capture buttons; no automatic face/palm triggers.', flush=True)
    try:
        code = subprocess.run(command, cwd=ROOT, env=environment, check=False).returncode
        metadata.update(exit_code=code, state='CLOSED_NOT_ACCEPTED' if code == 0 else 'EXIT_ERROR')
    except KeyboardInterrupt:
        code = 130
        metadata.update(exit_code=code, state='INTERRUPTED_PRESERVE_ORIGINAL_ROOT')
    except OSError:
        code = 2
        metadata.update(exit_code=code, state='LAUNCH_ERROR')
        print('Launch failed; preserve the trial folder and inspect the terminal error.', file=sys.stderr)
    metadata['ended_at_utc'] = datetime.now(timezone.utc).isoformat()
    report.write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    print('Session closed. Exit status is not hardware PASS; record observations in the owner worksheet.')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
