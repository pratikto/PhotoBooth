"""Test-only pipe fixture; ciphertext in, non-release MAC evidence out.

Windows uses actual current-user DPAPI. Linux explicitly patches original vault
lookup and makes no OS acceptance claim. No plaintext key pipe/file/env/argv.
"""
from contextlib import nullcontext
import json
import os
import sys
from unittest.mock import patch

from photobooth.post_preview_worker_custody import (
    ProtectedWorkerKey, WorkerCustodyScope, restore_worker_key)


def main():
    try:
        raw = sys.stdin.buffer.read(100001)
        if len(raw) > 100000:
            raise ValueError
        record = json.loads(raw)
        context = (nullcontext() if os.name == 'nt' else
                   patch('photobooth.linux_credential_vault._read_key', return_value=b'k'*32))
        with context:
            key = restore_worker_key(ProtectedWorkerKey.from_record(record['envelope']),
                                     WorkerCustodyScope.from_record(record['scope']))
            print(json.dumps(dict(state='RESTORED_TEST_VECTOR_ONLY', key_id=key.key_id,
                                  mac=key.sign({'kind': 'CUSTODY_TEST_NO_RELEASE_AUTHORITY'}),
                                  kivy_loaded='kivy' in sys.modules)))
        return 0
    except Exception:
        print('{"state":"CUSTODY_HELD"}')
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
