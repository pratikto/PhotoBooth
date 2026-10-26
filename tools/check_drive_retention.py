"""Read BUG-009 activation status; never deploy, set up, upload or delete photos."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from photobooth.manifest_io import write_json_atomic
from photobooth.retention_readiness import check


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'data' / 'diagnostics' / 'drive-retention-readiness.json')
    args = parser.parse_args(argv)
    report = check(ROOT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(args.output, report)
    status = report['drive_retention']
    print('HEAD: ' + str(report['source']['head']))
    print('Retention: ' + status['state'])
    print('Next: ' + status['next_action'])
    print('Report: ' + str(args.output))
    print('Read-only check. Actual cloud deletion: NOT VERIFIED.')
    return 0 if status['state'] == 'READY' else 1


if __name__ == '__main__':
    sys.exit(main())
