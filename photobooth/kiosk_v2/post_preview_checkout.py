"""Serialized private capture -> original CCP -> authenticated payment seam.

Currently restricted to explicit incomplete mock fixtures. No Sandbox customer
can pay until original-ticket/paid-delivery/release integration is implemented.
Never constructs provider, printer or Drive transports in the kiosk process.
"""
from photobooth.post_preview_ccp import OriginalCCPService, render_private_ccp
from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_store import DraftHeld
from .post_preview_photos import PrivatePhotoService


CHECKOUT_PHASES = frozenset({'claim_proof', 'checkout_ready', 'payment_pending', 'payment_hold', 'paid_hold'})


class PrivateCheckoutService(PrivatePhotoService):
    def __init__(self, root, *, payment_client, protector, merchant_id, readiness,
                 qr_loader, allow_incomplete_fixture=False, **kwargs):
        if (not isinstance(payment_client, PostPreviewClient)
                or payment_client.mode != 'mock' or allow_incomplete_fixture is not True
                or not getattr(protector, 'synthetic', False)):
            raise DraftHeld('Incomplete checkout is restricted to explicit synthetic fixtures')
        if not callable(readiness) or not callable(qr_loader):
            raise TypeError('Trusted readiness and QR adapters required')
        self.client, self.readiness, self.qr_loader = payment_client, readiness, qr_loader
        self.group = self._offer = self._claim_qr = self._payment = self._payment_qr = None
        self._ccp = None
        super().__init__(root, booth_id=payment_client.booth_id, **kwargs)
        self._ccp = OriginalCCPService(self.ledger, protector, merchant_id, allow_synthetic=True)

    def freeze_checkout(self, revision, expected_amount):
        self._active()
        if self.phase != 'final_preview':
            raise DraftHeld('Approve all original designs before checkout')
        readiness = self.readiness()
        self._active()
        if not isinstance(readiness, ChargeReadiness):
            raise DraftHeld('Trusted readiness required')
        intent = self.checkout.freeze(self.lease, self.templates, revision=revision,
                                      readiness=readiness, expected_amount=expected_amount)
        self.group = intent['purchase_group_id']
        self.phase = 'claim_proof'
        return self.offer_claim()

    def offer_claim(self):
        self._active()
        if self.phase not in {'claim_proof', 'checkout_ready'}:
            raise DraftHeld('Original prepayment proof phase required')
        self.phase = 'claim_proof'
        self._ccp.issue_once(self.lease)
        offer = self._ccp.private_offer(self.lease)
        qr = render_private_ccp(offer)
        self._active()
        self._offer, self._claim_qr = offer, qr
        return self.snapshot()

    def ccp_visible(self, offer):
        self._active()
        if self.phase not in {'claim_proof', 'checkout_ready'} or offer is not self._offer:
            raise DraftHeld('Original private presentation required')
        self._ccp.mark_visible(self.lease, offer)
        self._active()
        self.phase = 'checkout_ready'
        return self.snapshot()

    def begin_payment(self):
        self._active()
        if self.phase not in {'checkout_ready', 'payment_pending', 'payment_hold'}:
            raise DraftHeld('Genuinely visible original proof required')
        # Move before I/O: lost response remains reconciliation, never editable.
        self.phase = 'payment_hold'
        self._ccp.hide_private()
        self._offer = self._claim_qr = None
        try:
            observation = self.client.begin(self.group, self.lease)
        except Exception:
            return self.snapshot()
        return self._observe(observation)

    def check_payment(self, trigger='poll'):
        self._active()
        if self.phase not in {'payment_pending', 'payment_hold', 'paid_hold'}:
            raise DraftHeld('Original payment attempt required')
        try:
            observation = self.client.reconcile(self.group, trigger=trigger)
        except Exception:
            self._payment_qr = None
            self.phase = 'paid_hold' if (self._payment or {}).get('obligation_state') == 'OWED' else 'payment_hold'
            return self.snapshot()
        return self._observe(observation)

    def continue_payment(self, actively_continuing):
        self._active()
        if self.phase not in {'payment_pending', 'payment_hold'}:
            raise DraftHeld('Original active unpaid checkout required')
        if actively_continuing is not True:
            raise DraftHeld('Explicit original continuation required')
        observation = self.client.continue_expired(self.group, self.lease, actively_continuing=True)
        return self._observe(observation)

    def _observe(self, observation):
        # Keep backend financial journal authoritative even if hide occurred
        # during HTTP. A late response cannot restore any private pixels.
        if self._hidden.is_set() or self._closed.is_set():
            return {'phase': 'hold'}
        self._payment = observation
        self._payment_qr = None
        if observation['obligation_state'] == 'OWED':
            self.phase = 'paid_hold'  # No fulfillment capability implemented yet.
        elif observation['state'] == 'PENDING' and observation['qr_url']:
            self.phase = 'payment_pending'
            try:
                qr = self.qr_loader(observation)
            except Exception:
                qr = None  # Original attempt remains; never create due to image failure.
            if not self._hidden.is_set() and not self._closed.is_set():
                self._payment_qr = qr
        else:
            self.phase = 'payment_hold'
        return self.snapshot()

    def hide_private(self):
        super().hide_private()
        if self._ccp is not None:
            self._ccp.hide_private()
        self._offer = self._claim_qr = self._payment_qr = None

    def retire(self, event):
        # Local durable event precedes HTTP; shared-ledger backend recovers this
        # intent even if the notification request is lost or server is offline.
        super().retire(event)
        if self.group:
            try:
                self.client.lifecycle(self.group, self.lease, event)
            except Exception:
                pass  # HOLD + original durable lifecycle; never fabricate release.
        return {'phase': 'hold'}

    def snapshot(self):
        if self._hidden.is_set() or self._closed.is_set():
            return {'phase': 'hold'}
        if self.phase not in CHECKOUT_PHASES:
            return super().snapshot()
        result = {'phase': self.phase, 'generation': self._generation,
                  'purchase_group_id': self.group, 'payment': self._payment,
                  'print_available': False, 'auto_print': False, 'drive_enabled': False,
                  'download_qr': None, 'folder_url': None, 'fulfillment_authorized': False}
        if self.phase in {'claim_proof', 'checkout_ready'}:
            result.update(ccp_offer=self._offer, ccp_qr=self._claim_qr)
        if self.phase == 'payment_pending':
            result['payment_qr'] = self._payment_qr
        if self._hidden.is_set() or self._closed.is_set():
            return {'phase': 'hold'}
        return result
