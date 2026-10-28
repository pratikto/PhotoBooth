"""Ephemeral in-process permit issued only after trusted backend claim validation.

Not a customer credential or payment proof: the checkout controller owns the
factory, and no HTTP request/view/journal can deserialize one. Restarts discard
all permits. Real customer authorization is implemented at the backend in AR-06.
"""
import hashlib
import json
import threading
import time

_ISSUER = object()


def binding_hash(binding):
    return hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class ResumePermit:
    def __init__(self, issuer, binding, ttl, now, validator):
        if issuer is not _ISSUER:
            raise RuntimeError('Trusted resume authorization required')
        self._digest, self._deadline, self._now = binding_hash(binding), now()+ttl, now
        self._used = False
        self._validator = validator
        self._lock = threading.Lock()

    def consume(self, binding):
        with self._lock:
            if (self._used or self._now() >= self._deadline or binding_hash(binding) != self._digest
                    or (self._validator is not None and not self._validator())):
                raise RuntimeError('Resume authorization expired, consumed or mismatched')
            self._used = True


def trusted_resume_permit(binding, *, ttl=60, now=time.monotonic, validator=None):
    """Trusted controller seam, never expose as an unauthenticated API action."""
    if type(ttl) is not int or not 1 <= ttl <= 60:
        raise ValueError('Bounded resume permit lifetime required')
    return ResumePermit(_ISSUER, binding, ttl, now, validator)
