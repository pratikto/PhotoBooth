"""UI-only visible Recovery Ticket deadline; never payment or media authority.

The 30 seconds start after a genuine visible-callback acknowledgement, not at
QR construction, screen navigation or printer submission. Rebuilding a widget,
polling the provider or receiving a late printer ACK must not restart it.
"""
import math
import time


class VisibleTicketWindow:
    def __init__(self, *, monotonic=time.monotonic):
        if not callable(monotonic):
            raise TypeError('Clock source required')
        self._clock = monotonic
        self._started_at = None
        self._retired = False
        self._finished = False

    @property
    def active(self):
        return self._started_at is not None and not self._retired and not self._finished

    def start(self, *, genuine_visible):
        if genuine_visible is not True:
            raise ValueError('Genuine original ticket visibility required')
        if self._retired or self._finished or self._started_at is not None:
            return False
        now = self._clock()
        if (type(now) not in (float,int) or not math.isfinite(now)
                or not math.isfinite(now+30) or now+30 <= now):
            raise ValueError('Monotonic screen clock unavailable')
        self._started_at = now
        return True

    def remaining(self):
        if self._started_at is None:
            return None
        if self._retired or self._finished:
            return 0
        now = self._clock()
        if type(now) not in (float,int) or not math.isfinite(now):
            return None
        # Subtract from the same absolute deadline used by a monotonic timer.
        # (now-start) can round below 30 when start+30 crosses a float exponent
        # boundary, leaving a private QR visible at its exact deadline.
        return math.ceil(min(30, max(0, (self._started_at+30)-now)))

    def dismiss(self, *, next_pressed=False):
        if not self.active:
            return False
        if next_pressed is not True and self.remaining() != 0:
            return False
        self._finished = True
        return True

    def retire(self):
        self._retired = True
