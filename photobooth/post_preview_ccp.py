"""Original scoped Checkout Claim Proof: ciphertext, verifier and offer journal.

Trusted internal worker interface only. A verified CCP is not PAID, a machine
lease or private-media authority. The native checkout offer/claim route is not
mounted yet. Secrets never enter ordinary event/request/log fields.
"""
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import math
import re
import secrets
import time
import threading
import uuid

from photobooth.checkout_store import identifier
from photobooth.credential_vault import ProtectedCredential, VaultUnavailable
from photobooth.post_preview_checkout import canonical
from photobooth.post_preview_store import DraftHeld, ORDER_VERSION


@dataclass(frozen=True)
class ClaimProofPolicy:
    lifetime_seconds: int = 86400  # Versioned pilot default, not commercial policy.
    max_attempts: int = 8
    window_seconds: int = 60
    offer_permit_seconds: int = 60

    def __post_init__(self):
        if any(type(v) is not int or v < 1 for v in (
                self.lifetime_seconds, self.max_attempts, self.window_seconds, self.offer_permit_seconds)):
            raise ValueError('Positive bounded claim policy parameters required')
        if (self.lifetime_seconds > 15*86400 or self.max_attempts > 1000
                or self.window_seconds > 86400 or self.offer_permit_seconds > 300):
            raise ValueError('Claim policy exceeds nonproduction safety bounds')


@dataclass(frozen=True)
class PendingCCPOffer:
    presentation_id: str
    purchase_group_id: str
    generation: int
    qr_payload: str = field(repr=False)

    def __str__(self):
        return '<private Checkout Claim Proof>'


@dataclass(frozen=True)
class VerifiedCCPScope:
    purchase_group_id: str
    booth_id: str
    draft_id: str
    media_authorized: bool = field(default=False, init=False)
    payment_authorized: bool = field(default=False, init=False)


class OriginalCCPService:
    def __init__(self, ledger, protector, merchant_id, *, policy=None,
                 allow_synthetic=False, monotonic=time.monotonic):
        identifier(merchant_id)
        if (not hasattr(protector, 'synthetic') or
                protector.synthetic and allow_synthetic is not True):
            raise VaultUnavailable('Approved original credential protector required')
        self.ledger, self.protector, self.merchant_id = ledger, protector, merchant_id
        self.policy = policy or ClaimProofPolicy()
        if not isinstance(self.policy, ClaimProofPolicy):
            raise ValueError('Versioned claim policy required')
        self.monotonic = monotonic
        self._offers = {}
        self._privacy_lock = threading.RLock()
        self._hidden = False

    def _now(self):
        value = self.ledger.now()
        if type(value) not in (int, float) or not math.isfinite(value):
            raise VaultUnavailable('Claim clock is unavailable')
        return value

    def _scope(self, lease):
        if self._hidden:
            raise VaultUnavailable('Original private presentation has retired')
        self.ledger._owned(lease)
        intent = self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?',
                                         (lease.draft_id,)).fetchone()
        if not intent or intent['phase'] != 'CREATE_PREPARED':
            raise DraftHeld('Original immutable checkout intent required')
        scope = {'kind': 'CCP', 'version': 1, 'order_version': ORDER_VERSION,
                 'merchant_id': self.merchant_id, 'booth_id': lease.booth_id,
                 'draft_id': lease.draft_id, 'purchase_group_id': intent['purchase_group_id'],
                 'contract_sha256': intent['contract_sha256']}
        return scope, intent

    @staticmethod
    def _verifier(scope_json, payload):
        return hashlib.sha256((scope_json+'\n'+payload).encode('utf-8')).hexdigest()

    def _live(self, row, now):
        if (not row or row['revoked'] or row['merchant_id'] != self.merchant_id
                or not row['issued_at'] <= now < row['expires_at']):
            raise VaultUnavailable('Original claim proof is unavailable')

    def issue_once(self, lease):
        """Persist original encrypted CCP once; never return its raw secret here."""
        with self.ledger.write():
            scope, intent = self._scope(lease)
            group = intent['purchase_group_id']
            now = self._now()
            scope_json = canonical(scope)
            row = self.ledger.db.execute('SELECT * FROM pp_ccp_credentials WHERE purchase_group_id=?',
                                          (group,)).fetchone()
            if row:
                self._live(row, now)
                if row['scope_json'] != scope_json:
                    raise VaultUnavailable('Original claim scope changed')
                return {'purchase_group_id': group, 'kind': 'CCP', 'expires_at': row['expires_at']}
            if self.ledger.db.execute("SELECT 1 FROM pp_events WHERE draft_id=? AND event='CCP_CREATED'",
                                       (lease.draft_id,)).fetchone():
                raise VaultUnavailable('Original claim escrow is missing; no reissue')
            expires = intent['prepared_at']+self.policy.lifetime_seconds
            if not intent['prepared_at'] <= now < expires:
                raise VaultUnavailable('Original claim issue window expired')
            payload = f"MEONG:CCP:1:{lease.booth_id}:{group}:"+secrets.token_urlsafe(32)
            protected = self.protector.protect(payload.encode('utf-8'), scope_json.encode('utf-8'))
            if (not isinstance(protected, ProtectedCredential)
                    or protected.protector_id != self.protector.protector_id
                    or not isinstance(protected.ciphertext, bytes) or not 0 < len(protected.ciphertext) <= 65536):
                raise VaultUnavailable('Original claim escrow could not be protected')
            self.ledger.db.execute('''INSERT INTO pp_ccp_credentials
                (purchase_group_id,booth_id,merchant_id,scope_json,verifier,protector_id,ciphertext,
                 issued_at,expires_at,policy_version,window_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
                (group, lease.booth_id, self.merchant_id, scope_json, self._verifier(scope_json, payload),
                 protected.protector_id, protected.ciphertext, now, expires, 'post-preview-ccp-pilot-v1', now))
            self.ledger._event(lease.draft_id, 'CCP_CREATED')
            return {'purchase_group_id': group, 'kind': 'CCP', 'expires_at': expires}

    def private_offer(self, lease):
        """Decrypt only for a live current checkout, with an in-memory render permit."""
        with self.ledger.write():
            scope, intent = self._scope(lease)
            row = self.ledger.db.execute('SELECT * FROM pp_ccp_credentials WHERE purchase_group_id=?',
                                          (intent['purchase_group_id'],)).fetchone()
            self._live(row, self._now())
            if row['scope_json'] != canonical(scope):
                raise VaultUnavailable('Original claim scope changed')
            protected = ProtectedCredential(row['protector_id'], bytes(row['ciphertext']))
            try:
                payload = self.protector.unprotect(protected, row['scope_json'].encode('utf-8')).decode('utf-8')
            except (UnicodeError, ValueError):
                raise VaultUnavailable('Original claim escrow is unavailable') from None
            if not hmac.compare_digest(row['verifier'], self._verifier(row['scope_json'], payload)):
                raise VaultUnavailable('Original claim verifier mismatch')
            offer = PendingCCPOffer(uuid.uuid4().hex, intent['purchase_group_id'], lease.generation, payload)
            with self._privacy_lock:
                if self._hidden:
                    raise VaultUnavailable('Original private presentation has retired')
                self._offers.clear()
                self._offers[offer.presentation_id] = (offer, self.monotonic(), None)
            return offer

    def mark_visible(self, lease, offer):
        """Trusted renderer callback only; creation/decryption never means offered."""
        with self.ledger.write():
            scope, intent = self._scope(lease)
            with self._privacy_lock:
                entry = self._offers.get(getattr(offer, 'presentation_id', None))
            if (not entry or entry[0] is not offer or offer.generation != lease.generation
                    or offer.purchase_group_id != intent['purchase_group_id']
                    or not 0 <= self.monotonic()-entry[1] <= self.policy.offer_permit_seconds):
                raise VaultUnavailable('Original private render permit expired or retired')
            row = self.ledger.db.execute('SELECT * FROM pp_ccp_credentials WHERE purchase_group_id=?',
                                          (intent['purchase_group_id'],)).fetchone()
            now = self._now()
            self._live(row, now)
            if row['scope_json'] != canonical(scope):
                raise VaultUnavailable('Original claim scope changed')
            if row['offered_at'] is None:
                self.ledger.db.execute('UPDATE pp_ccp_credentials SET offered_at=? WHERE purchase_group_id=?',
                                       (now, intent['purchase_group_id']))
                self.ledger._event(lease.draft_id, 'CCP_OFFERED')
            return row['offered_at'] if row['offered_at'] is not None else now

    def verify(self, purchase_group_id, booth_id, payload):
        """Hash verifier only, no decrypt/media/payment/booth-release authority."""
        identifier(purchase_group_id)
        identifier(booth_id)
        allowed = False
        scope = None
        with self.ledger.write():
            row = self.ledger.db.execute('SELECT * FROM pp_ccp_credentials WHERE purchase_group_id=?',
                                          (purchase_group_id,)).fetchone()
            now = self._now()
            if row:
                window, attempts = row['window_at'], row['attempts']
                if now-window >= self.policy.window_seconds:
                    window, attempts = now, 0
                shape = (isinstance(payload, str) and len(payload) <= 256 and
                         re.fullmatch(r'MEONG:CCP:1:[A-Za-z0-9_-]{1,64}:[a-f0-9]{32}:[A-Za-z0-9_-]{43}', payload))
                candidate = self._verifier(row['scope_json'], payload) if shape else '0'*64
                allowed = (row['booth_id'] == booth_id and row['merchant_id'] == self.merchant_id
                    and not row['revoked'] and row['issued_at'] <= now < row['expires_at']
                    and window <= now and attempts < self.policy.max_attempts
                    and hmac.compare_digest(row['verifier'], candidate))
                self.ledger.db.execute('UPDATE pp_ccp_credentials SET attempts=?,window_at=? WHERE purchase_group_id=?',
                    (attempts if allowed else attempts+1, window, purchase_group_id))
                if allowed: scope = json.loads(row['scope_json'])
        if not allowed:
            raise PermissionError('Original Checkout Claim Proof required')
        return VerifiedCCPScope(purchase_group_id, booth_id, scope['draft_id'])

    def revoke(self, lease):
        with self.ledger.write():
            scope, intent = self._scope(lease)
            self.ledger.db.execute('UPDATE pp_ccp_credentials SET revoked=1 WHERE purchase_group_id=?',
                                   (intent['purchase_group_id'],))
            self.ledger._event(lease.draft_id, 'CCP_REVOKED')
        self._offers.clear()

    def hide_private(self):
        with self._privacy_lock:
            self._hidden = True
            self._offers.clear()  # No future mark-visible from retired rendering.
