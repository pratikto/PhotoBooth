"""Run the existing credential-isolated merchant trial with the native v2 GUI."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.run_qris_sandbox import main as merchant_trial, trial_environments


def v2_environments(parent, merchant, key, booth, port, root=ROOT):
    backend, gui = trial_environments(parent, merchant, key, booth, port, root)
    directory = root/'data'/'kiosk-v2-sandbox'/merchant/booth
    for env in (backend, gui):
        env.update(MEONG_QRIS_DB_PATH=str(directory/'orders.sqlite'),
                   MEONG_QRIS_JOURNAL=str(directory/'visit.json'),
                   PHOTOBOOTH_V2_CHECKOUT_MOCK='0', PHOTOBOOTH_V2_CHECKOUT_SANDBOX='1',
                   PHOTOBOOTH_V2_PRINT='0', PHOTOBOOTH_V2_DRIVE='0')
    return backend, gui


def main(argv=None):
    return merchant_trial(argv, environment_factory=v2_environments,
                          gui_entry=('tools/run_portrait_v2.py',),
                          trial_notice='Native v2 Sandbox: printer and Drive off; photos use an isolated test profile.')


if __name__ == '__main__':
    sys.exit(main())
