"""Timed synthetic journey/fault qualification; never owner/device acceptance.

Uses original executable tests in one persistent Python process. Each cycle
owns fresh disposable fixture roots; the 12-visit case shares its journal
within that batch. This is not one continuously growing booth database, a
native GUI endurance test, actual OS reboot or real provider/device traffic.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
TESTS = [
    'tests.test_post_preview_journey_matrix.CustomerJourneyMatrixTests.'
    'test_j21_twelve_paid_visits_complete_without_folder_or_payment_contamination',
    'tests.test_post_preview_refund_simulation.MockRefundProcessTests',
    'tests.test_post_preview_refund_simulation.MockRefundWorkerFenceTests',
    'tests.test_post_preview_refund_simulation.MockRefundLifecycleTests.'
    'test_lost_reply_and_repeated_notifications_reconcile_same_key_without_second_request',
]


def fingerprint():
    files = subprocess.check_output(['git', 'ls-files', '-z', 'photobooth', 'tests',
                                     'tools', '.github/workflows'], cwd=ROOT).split(b'\0')
    digest = hashlib.sha256()
    for filename in sorted(x for x in files if x):
        digest.update(filename + b'\0')
        digest.update(hashlib.sha256((ROOT / os.fsdecode(filename)).read_bytes()).digest())
    return digest.hexdigest()


def resources():
    sample = {'threads': threading.active_count()}
    proc = Path('/proc/self')
    if proc.is_dir():
        sample['file_descriptors'] = len(list((proc/'fd').iterdir()))
        for line in (proc/'status').read_text().splitlines():
            if line.startswith('VmRSS:'):
                sample['rss_bytes'] = int(line.split()[1]) * 1024
    return sample


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--duration-seconds', type=int, required=True)
    parser.add_argument('--output-directory', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.duration_seconds <= 28800:
        parser.error('Duration must be 1..28800 seconds; short runs are smoke only')
    out = args.output_directory.resolve()
    # No arbitrary existing directory, runtime root or tracked artifact writes.
    if out.exists():
        parser.error('A new output directory is required')
    if out == ROOT or ROOT in out.parents and not str(out.relative_to(ROOT)).startswith('work/postpay-'):
        parser.error('Output must be outside source or inside ignored work/postpay-*')
    out.mkdir(parents=True)
    sys.path.insert(0, str(ROOT))
    os.environ.update(PHOTOBOOTH_V2_PRINT='0', PHOTOBOOTH_V2_DRIVE='0',
                      PHOTOBOOTH_CAMERA='0', PHOTOBOOTH_AUDIO='0',
                      PHOTOBOOTH_FACE_TRIGGER='0', PHOTOBOOTH_PALM_TRIGGER='0')
    started = time.monotonic()
    record = dict(source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  runtime_sha256=fingerprint(), target_seconds=args.duration_seconds,
                  started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  scope='SYNTHETIC_BATCH_JOURNEYS_AND_CRASH_FAULTS',
                  resource_budget_status='NOT_SPECIFIED_NO_PERFORMANCE_ACCEPTANCE',
                  cycles=[], functional_pass=False, complete=False, tests=TESTS,
                  initial_resources=resources())
    with (out/'cycles.log').open('x', encoding='utf-8') as log:
        while time.monotonic() - started < args.duration_seconds:
            report = io.StringIO()
            suite = unittest.defaultTestLoader.loadTestsFromNames(TESTS)
            result = unittest.TextTestRunner(stream=report, verbosity=2).run(suite)
            log.write(report.getvalue()); log.flush(); os.fsync(log.fileno())
            record['cycles'].append(dict(cycle=len(record['cycles'])+1, elapsed_seconds=round(time.monotonic()-started,3),
                run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                skipped=len(result.skipped), resources=resources()))
            record['elapsed_seconds'] = round(time.monotonic()-started,3)
            (out/'progress.tmp').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
            os.replace(out/'progress.tmp',out/'progress.json')
            print(json.dumps(record['cycles'][-1]),flush=True)
            if not result.wasSuccessful() or result.skipped or result.testsRun != 7:
                break
    record['elapsed_seconds'] = round(time.monotonic()-started,3)
    record['runtime_unchanged'] = fingerprint() == record['runtime_sha256']
    record['complete'] = True
    record['functional_pass'] = (record['runtime_unchanged'] and bool(record['cycles'])
        and record['elapsed_seconds'] >= args.duration_seconds
        and all(x['run']==7 and not (x['failures'] or x['errors'] or x['skipped']) for x in record['cycles']))
    record['multi_hour_duration_observed'] = record['elapsed_seconds'] >= 7200
    record['completed_paid_visits'] = 12 * sum(x['failures']==0 and x['errors']==0 for x in record['cycles'])
    record['log_sha256'] = hashlib.sha256((out/'cycles.log').read_bytes()).hexdigest()
    record['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return 0 if record['functional_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
