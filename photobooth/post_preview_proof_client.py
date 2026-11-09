"""Native original-CCP display adapter, with booth credentials only.

No OS protector, merchant key or financial/media capability enters this object.
Invoke off the UI thread; mark_visible only from the genuine renderer callback.
"""
import re
import threading

from photobooth.post_preview_ccp import PendingCCPOffer
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_store import DraftHeld, ORDER_VERSION
from photobooth.post_preview_ticket import PendingRecoveryOffer


class PostPreviewCCPClient:
    KIND = 'CCP'
    ROUTE = 'ccp'
    OFFER_TYPE = PendingCCPOffer

    def __init__(self, payments):
        if type(payments) is not PostPreviewClient:
            raise ValueError('Exact authenticated original payment client required')
        self._payments = payments
        self._lock = threading.RLock()
        self._pending = None
        self._hidden = threading.Event()

    def _call(self, group, lease, action, presentation_id=None):
        if (type(group) is not str or re.fullmatch(r'[a-f0-9]{32}', group) is None
                or lease.booth_id != self._payments.booth_id):
            raise DraftHeld('Exact original checkout display scope required')
        payload = self._payments._owner(lease)
        if presentation_id is not None:
            payload['presentation_id'] = presentation_id
        try:
            result = self._payments._transport._call('POST',
                '/api/postpay/groups/'+group+'/'+self.ROUTE+'/'+action, payload=payload)
        except Exception:
            raise DraftHeld('Original private proof request held') from None
        base = dict(kind=self.KIND, purchase_group_id=group, booth_id=lease.booth_id,
                    generation=lease.generation, mode=self._payments.mode,
                    order_version=ORDER_VERSION)
        if any(type(result.get(k)) is not type(v) or result[k] != v for k,v in base.items()):
            raise DraftHeld('Original private proof response scope changed')
        if action != 'offer':
            if result != dict(base, action=action, presentation_id=presentation_id):
                raise DraftHeld('Original private display acknowledgement changed')
        elif (set(result) != set(base)|{'presentation_id','qr_payload'}
                or type(result['presentation_id']) is not str
                or re.fullmatch(r'[a-f0-9]{32}', result['presentation_id']) is None
                or type(result['qr_payload']) is not str
                or re.fullmatch(r'MEONG:'+self.KIND+r':1:'+re.escape(lease.booth_id)+':'+group
                    +r':[A-Za-z0-9_-]{43}', result['qr_payload']) is None):
            raise DraftHeld('Original private display permit required')
        return result

    def private_offer(self, group, lease):
        with self._lock:
            if self._hidden.is_set():
                raise DraftHeld('Original private display retired')
            result = self._call(group, lease, 'offer')
            offer = self.OFFER_TYPE(result['presentation_id'], group,
                                    lease.generation, result['qr_payload'])
            self._pending = (lease, offer)
            if self._hidden.is_set():
                self._pending = None
                raise DraftHeld('Original private display retired')
            return offer

    def _original(self, lease, offer):
        if (self._hidden.is_set() or self._pending is None
                or self._pending[0] != lease or self._pending[1] is not offer):
            raise DraftHeld('Exact live original private display required')

    def mark_visible(self, lease, offer):
        with self._lock:
            self._original(lease, offer)
            self._call(offer.purchase_group_id, lease, 'visible', offer.presentation_id)
            if self._hidden.is_set():
                raise DraftHeld('Original private display retired')

    def retire_offer(self, lease, offer):
        with self._lock:
            self._original(lease, offer)
            self._pending = None  # Retire callbacks even if network response is lost.
            self._call(offer.purchase_group_id, lease, 'retire', offer.presentation_id)

    def hide_private(self):
        # Immediate privacy fence, including in-flight offer/visible responses.
        # Backend lifecycle/permit retirement remains a separate worker action.
        self._hidden.set()
        self._pending = None


class PostPreviewRecoveryClient(PostPreviewCCPClient):
    """Fixed paid-ticket role, using the same authenticated bounded transport."""
    KIND = 'RECOVERY'
    ROUTE = 'ticket'
    OFFER_TYPE = PendingRecoveryOffer

    def dismiss(self, lease, offer):
        with self._lock:
            self._original(lease, offer)
            self._call(offer.purchase_group_id, lease, 'dismiss', offer.presentation_id)
