"""Save a P5 readiness report without opening devices or contacting a provider."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from photobooth.kiosk_v2.readiness import inventory
from photobooth.manifest_io import write_json_atomic


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'data'/'diagnostics'/'windows-readiness.json')
    args=parser.parse_args(argv)
    report=inventory(ROOT)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    write_json_atomic(args.output,report)
    print('HEAD: '+report['source']['head'])
    print('Preflight: '+report['preflight']['status'])
    print('Report: '+str(args.output))
    print('Physical/provider acceptance: NOT RUN. Import the report into the Windows checklist.')
    return 0 if report['preflight']['status']=='READY_FOR_MANUAL_TEST' else 1


if __name__=='__main__':sys.exit(main())
