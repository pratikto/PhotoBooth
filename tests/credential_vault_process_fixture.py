"""Independent OS-vault probe using random nonredeemable bytes, no raw output.

Only protected ciphertext reaches disk. The digest is the sole success evidence
crossing the process pipe; no key, credential plaintext or OS error is printed.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

from photobooth.credential_vault import ProtectedCredential, VaultUnavailable, platform_protector


SCOPE = b'fixture-merchant/PB001/original-purchase/CCP/v1'


def main(path, action):
    try:
        protector = platform_protector()
        if action == 'seal':
            plaintext = os.urandom(32)
            protected = protector.protect(plaintext, SCOPE)
            # Exclusive creation prevents a fixture from overwriting old data.
            with Path(path).open('xb') as stream:
                stream.write(protected.ciphertext)
        elif action in {'open', 'wrong-scope'}:
            scope = SCOPE if action == 'open' else b'fixture-merchant/PB002/foreign-purchase/CCP/v1'
            protected = ProtectedCredential(protector.protector_id, Path(path).read_bytes())
            plaintext = protector.unprotect(protected, scope)
        else:
            raise ValueError('Unsupported fixture action')
    except VaultUnavailable:
        print(json.dumps({'state': 'VAULT_UNAVAILABLE'}))
        return 78
    print(json.dumps({'state': 'PROTECTED', 'digest': hashlib.sha256(plaintext).hexdigest()}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
