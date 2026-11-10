"""Owned Windows normal-flow Sandbox acceptance; no production/fault release."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from photobooth.post_preview_acceptance import (AcceptanceHeld, CASES, RESULTS,
    preflight, save_session, validate_for_run, record_result, summary)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise AcceptanceHeld('Acceptance arguments held')  # Never echo a pasted secret.


def parser():
    p = Parser(description=__doc__)
    sub = p.add_subparsers(dest='action',required=True,parser_class=Parser)
    for name in ('preflight','validate-run','record','show'):
        item = sub.add_parser(name)
        if name in ('preflight','validate-run'):
            item.add_argument('--storage-root',type=Path,required=True)
            item.add_argument('--booth-id',default='PB001')
        if name != 'preflight': item.add_argument('--session',required=True)
        if name == 'record':
            item.add_argument('--case',choices=tuple(CASES),required=True)
            item.add_argument('--result',choices=RESULTS,required=True)
    return p


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        if args.action == 'preflight':
            report = preflight(ROOT,args.storage_root,args.booth_id)
            session = save_session(ROOT,report)
            for name,status in report['checks'].items(): print(status+' '+name)
            print('ACCEPTANCE_SESSION='+session)
            print('RESULT: '+report['status'])
            print('LOCAL ONLY. Actual protected startup, accounts and devices are NOT_CHECKED.')
            print('Interrupted recovery/remedy/full commercial acceptance remain BLOCKED.')
            return 0 if report['status']=='LOCAL_PREREQUISITES_PASS' else 2
        if args.action == 'validate-run':
            validate_for_run(ROOT,args.storage_root,args.booth_id,args.session)
            print('SESSION VALID. Original runtime guards and ALL external consents still required.')
        elif args.action == 'record':
            record_result(ROOT,args.session,args.case,args.result)
            print('OWNER_REPORTED observation appended. No commercial or backend authority.')
        else:
            print(json.dumps(summary(ROOT,args.session),indent=2))
        return 0
    except Exception:
        print('BLOCKED: acceptance held. Check local prerequisites/session; preserve original history.',file=sys.stderr)
        return 2


if __name__ == '__main__': raise SystemExit(main())
