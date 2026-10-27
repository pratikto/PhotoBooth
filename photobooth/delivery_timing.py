"""Bounded delivery timing: identities and numeric counters, never payloads/URLs."""
from contextlib import contextmanager
import json
import logging
import re
import time

LOG = logging.getLogger('photobooth.delivery')
LOG.setLevel(logging.INFO)


def event(stage, transaction_id=None, **fields):
    identity = str(transaction_id or '')
    if not re.fullmatch(r'PB[0-9]+(?:V2(?:S2)?)?_[0-9]{8}', identity):
        identity = 'unknown'
    LOG.info('delivery_timing %s', json.dumps(dict(stage=stage, tx=identity,
             monotonic_ms=round(time.monotonic()*1000, 1), **fields), sort_keys=True))


@contextmanager
def span(stage, transaction_id=None, **fields):
    started = time.monotonic()
    try:
        yield
    except Exception as error:
        event(stage, transaction_id, elapsed_ms=round((time.monotonic()-started)*1000, 1),
              result='error', error=type(error).__name__,
              status_code=getattr(error, 'status_code', None), **fields)
        raise
    else:
        event(stage, transaction_id, elapsed_ms=round((time.monotonic()-started)*1000, 1),
              result='ok', **fields)
