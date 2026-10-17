"""Payment attempt lifecycle, deliberately using a non-payable demo gateway.

No merchant, provider credentials or live money API are configured in this
project. Demo QR payloads and printed slips therefore say DEMO explicitly.
The coordinator separates a UI timeout from provider expiry and refuses to
replace a paid or unknown attempt. A future gateway must implement the same
status/cancel contracts on a background worker, with authoritative server
verification; a successful print is never evidence of payment.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
import uuid


@dataclass
class PaymentAttempt:
    attempt_id: str
    amount: int
    payload: str
    created_at: datetime
    expires_at: datetime
    state: str = 'pending'
    demo: bool = True

    def remaining(self, now=None):
        return max(0, (self.expires_at - (now or datetime.now(timezone.utc))).total_seconds())

    def snapshot(self):
        """Freeze job inputs so edits/renewal cannot mutate an in-flight slip."""
        return replace(self)


class DemoPaymentGateway:
    """An offline development adapter; it never charges or contacts a provider."""

    def __init__(self, validity=900, now=None):
        self.validity = validity
        self.now = now or (lambda: datetime.now(timezone.utc))

    def create(self, amount):
        current = self.now()
        attempt_id = 'DEMO-' + uuid.uuid4().hex[:12].upper()
        return PaymentAttempt(attempt_id, amount,
                              f'PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR {amount} - {attempt_id}',
                              current, current + timedelta(seconds=self.validity))

    def status(self, attempt):
        if attempt.state == 'pending' and attempt.remaining(self.now()) <= 0:
            attempt.state = 'expired'
        return attempt.state

    def cancel(self, attempt):
        if self.status(attempt) == 'pending':
            attempt.state = 'cancelled'
        return attempt.state

    def simulate_success(self, attempt):
        if self.status(attempt) == 'pending':
            attempt.state = 'paid'
        return attempt.state == 'paid'


class PaymentCoordinator:
    """Preserve one payable attempt until its terminal status is confirmed."""

    def __init__(self, gateway=None):
        self.gateway = gateway or DemoPaymentGateway()
        self.current = None

    def check(self):
        if self.current is None:
            return 'none'
        try:
            state = self.gateway.status(self.current)
        except (OSError, TimeoutError):
            return 'unknown'
        return state if state in {'pending', 'paid', 'expired', 'cancelled', 'failed'} else 'unknown'

    def begin(self, amount):
        if self.current is not None and not self.release():
            raise RuntimeError('Previous payment is paid or its final status is not confirmed.')
        self.current = self.gateway.create(amount)
        return self.current

    def renew(self):
        """Renew only a confirmed expired/failed/cancelled QR, never a timeout."""
        if self.current is None or self.check() not in {'expired', 'cancelled', 'failed'}:
            raise RuntimeError('The current QR is still active or its status is unknown.')
        amount = self.current.amount
        self.current = self.gateway.create(amount)
        return self.current

    def release(self):
        """Return to browsing only after the old attempt can no longer be paid."""
        state = self.check()
        if state == 'pending':
            try:
                state = self.gateway.cancel(self.current)
            except (OSError, TimeoutError):
                return False
        if state in {'none', 'expired', 'cancelled', 'failed'}:
            self.current = None
            return True
        return False
