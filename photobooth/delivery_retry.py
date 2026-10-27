"""Local scheduling metadata; these deadlines never alter photo retention clocks."""
import math
import time


class DeliveryRetries:
    BASE_SECONDS = 30
    MAX_SECONDS = 300
    RECOVERY_SECONDS = 30

    def __init__(self):
        self.states = {}
        self.recovery_after = 0

    def state(self, transaction, manifest):
        if transaction not in self.states:
            saved = manifest.get('drive_delivery_retry')
            if isinstance(saved, dict):
                failures = saved.get('failures', 0)
                deadline = saved.get('not_before_unix', 0)
                failures = min(failures, 31) if type(failures) is int and failures > 0 else 0
                delay = (max(0, min(self.MAX_SECONDS, deadline-time.time()))
                         if type(deadline) in (float, int) and math.isfinite(deadline) else 0)
                self.states[transaction] = {'failures': failures, 'due': time.monotonic()+delay}
            elif (manifest.get('drive_binding_error') or manifest.get('drive_retention_error')
                  or any(r.get('status') == 'UPLOAD_RETRY' for r in manifest.get('upload_files', {}).values())):
                # Import pre-update failures into bounded recovery without changing identities.
                self.states[transaction] = {'failures': 0, 'due': 0}
        return self.states.get(transaction)

    def failed(self, transaction, code, phase):
        failures = min(self.states.get(transaction, {}).get('failures', 0)+1, 31)
        delay = min(self.MAX_SECONDS, self.BASE_SECONDS * 2**min(failures-1, 4))
        self.states[transaction] = {'failures': failures, 'due': time.monotonic()+delay}
        return {'error_code': code, 'phase': phase, 'failures': failures,
                'delay_seconds': delay, 'not_before_unix': time.time()+delay}

    def recovered(self, transaction):
        self.states.pop(transaction, None)

    def choose(self, candidates):
        """Oldest due retry gets one turn even with continuous healthy arrivals."""
        now = time.monotonic()
        if now < self.recovery_after:
            return None
        ready = [(self.states[tx]['due'], tx, path) for tx, path in candidates
                 if self.states[tx]['due'] <= now]
        if not ready:
            return None
        _, tx, path = min(ready)
        return tx, path

    def finish_turn(self):
        self.recovery_after = time.monotonic()+self.RECOVERY_SECONDS
