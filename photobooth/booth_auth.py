"""FEAT-020 server-side booth authentication primitives.

Never embed the shared booth secret in publicly distributed kiosk builds.
The HTTP layer must enforce TLS, request size limits and rate limiting.
"""
import hashlib
import hmac
import re


_BOOTH_ID = re.compile(r"PB[0-9]{3,8}")


class BoothAuthenticator:
    """Map a verified bearer credential to a single configured booth."""

    def __init__(self, booth_secrets):
        if not isinstance(booth_secrets, dict) or not booth_secrets:
            raise ValueError("At least one booth must be configured")
        self._digests = {}
        for booth_id, secret in booth_secrets.items():
            if (not isinstance(booth_id, str) or not _BOOTH_ID.fullmatch(booth_id)
                    or not isinstance(secret, str) or len(secret) < 32):
                raise ValueError("Invalid booth configuration")
            self._digests[booth_id] = hashlib.sha256(secret.encode("utf-8")).digest()

    def authenticate(self, booth_id, authorization):
        """Return booth ID only after a constant-time credential comparison."""
        if not isinstance(booth_id, str) or not isinstance(authorization, str):
            return None
        if not authorization.startswith("Bearer "):
            return None
        candidate = authorization[len("Bearer "):]
        if not candidate or len(candidate) > 512 or candidate != candidate.strip():
            return None
        expected = self._digests.get(booth_id)
        if expected is None:
            return None
        supplied = hashlib.sha256(candidate.encode("utf-8")).digest()
        return booth_id if hmac.compare_digest(expected, supplied) else None
