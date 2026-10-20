"""Mandatory offline backend suites; a skipped test fails this quality gate."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))

SUITES = (
    'test_payment_ledger', 'test_payment_quote', 'test_payment_orders',
    'test_payment_concurrency', 'test_midtrans_verify', 'test_midtrans_sandbox',
    'test_checkout_service', 'test_booth_auth', 'test_qris_api',
    'test_qris_kiosk_client', 'test_checkout_durability', 'test_checkout_backend',
    'test_qris_http_v2', 'test_qris_session',
)

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromNames(SUITES)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.skipped:
        print('ERROR: mandatory backend tests must not be skipped')
    sys.exit(0 if result.wasSuccessful() and not result.skipped and result.testsRun else 1)
