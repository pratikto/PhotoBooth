"""Compatibility entrypoint for the QRIS main-GUI test flow.

Use tools/run_qris_mock.py for a credential-free, loopback-only automatic trial.
The previous standalone manual checkout preview is no longer a separate app.
"""
from main import main

if __name__ == '__main__':
    import os
    if os.environ.get('MEONG_PAYMENT_MODE') not in {'qris-mock', 'qris-sandbox'}:
        raise RuntimeError('Select qris-mock or qris-sandbox explicitly; see docs/QRIS_TRIAL.md')
    main()
