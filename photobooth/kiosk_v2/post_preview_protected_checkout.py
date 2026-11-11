"""Protected native continuation of the SAME original frozen photo visit.

No provider, custody or Drive transport belongs here. This is not a customer
launcher or admission authority. Original proof recovery requires our exact
typed backend claim result and durable evidence. Freeze requires the original
protected backend/worker profile; a complete customer launcher remains gated.
An existing frozen visit is never inferred from a reopened database or
reconstructed at startup.
"""
import re

from photobooth.post_preview_ccp import render_private_ccp
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_delivery_client import PostPreviewDeliveryClient
from photobooth.post_preview_handoff_client import PostPreviewHandoffClient,ProtectedClaimGrant
from photobooth.post_preview_proof_client import PostPreviewCCPClient, PostPreviewRecoveryClient
from photobooth.post_preview_store import DraftHeld
from .post_preview_checkout import CHECKOUT_PHASES, TICKET_PHASES
from .post_preview_photos import PrivatePhotoService


class ProtectedCheckoutService(PrivatePhotoService):
    def __init__(self, root, *, payment_client, qr_loader, require_worker_binding=False, **kwargs):
        if type(require_worker_binding) is not bool:
            raise DraftHeld('Exact original worker-binding selection required')
        self._requires_worker_binding=require_worker_binding
        if type(payment_client) is not PostPreviewClient or payment_client.mode != 'sandbox':
            raise DraftHeld('Exact original Sandbox client required')
        if not callable(qr_loader):
            raise TypeError('Original payment image loader required')
        self.client, self.qr_loader = payment_client, qr_loader
        self._ccp = PostPreviewCCPClient(payment_client)
        self._ticket = PostPreviewRecoveryClient(payment_client)
        self._delivery = PostPreviewDeliveryClient(payment_client)
        self._handoff = PostPreviewHandoffClient(payment_client)
        self.group = self._offer = self._claim_qr = self._payment = self._payment_qr = None
        self._ticket_offer = self._ticket_qr = self._ticket_receipt = None
        self._ticket_was_dismissed = False
        self._delivery_state = None
        super().__init__(root, booth_id=payment_client.booth_id, **kwargs)

    def _before_private_work(self):
        if self._requires_worker_binding:
            self.client.bind_worker_generation(self.lease)
            self._active()

    paid_ticket_enabled = property(lambda self: True)
    paid_delivery_enabled = property(lambda self: True)

    def prepare(self):
        if self.lease is None:
            return super().prepare()
        self._active()
        with self.ledger.write():
            self.ledger._owned(self.lease)
        return self.snapshot()

    def accept_frozen_checkout(self, group):
        """Worker-only continuation of our live capture, never a restore API.

        The trusted checkout orchestrator must already have frozen this exact
        draft. A new/reopened facade has no lease and cannot take over old media.
        Called only after protected backend freeze or explicit isolated fixtures.
        """
        self._active()
        if self.phase != 'final_preview' or self.lease is None or self.group is not None:
            raise DraftHeld('Original live all-design preview required')
        with self.ledger.write():
            row = self.ledger.db.execute('SELECT draft_id FROM pp_checkout_intents '
                'WHERE purchase_group_id=?', (group,)).fetchone()
            if (type(group) is not str or re.fullmatch(r'[a-f0-9]{32}', group) is None
                    or not row or row['draft_id'] != self.lease.draft_id):
                raise DraftHeld('Exact original frozen visit required')
            self.ledger._owned(self.lease)
        scope = self.checkout.verify_frozen(group, self.templates)
        if scope.booth_id != self.booth_id or scope.generation != self.lease.generation:
            raise DraftHeld('Exact original frozen generation required')
        self._active()
        self.group = group
        self.phase = 'claim_proof'
        return self.offer_claim()

    def freeze_checkout(self,revision,expected_amount):
        self._active()
        if self.phase!='final_preview' or self.lease is None or self.group is not None:
            raise DraftHeld('Original live all-design preview required')
        frozen=self.client.freeze_checkout(self.lease,revision=revision,expected_amount=expected_amount)
        self._active()  # A late HTTP response cannot offer CCP over private Ads.
        with self.ledger.write():
            self.ledger._owned(self.lease,revision=revision)
            intent=self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?',
                                          (self.lease.draft_id,)).fetchone()
            if (not intent or intent['purchase_group_id']!=frozen['purchase_group_id']
                    or intent['contract_sha256']!=frozen['contract_sha256']):
                raise DraftHeld('Exact durable original frozen candidate required')
        return self.accept_frozen_checkout(frozen['purchase_group_id'])

    def claim_original(self,group,proof,request_id):
        """Off-UI-thread proof claim; a busy result never changes private views."""
        self._active()
        if self.lease is not None or self.group is not None or self.phase!='confirm':
            raise DraftHeld('Fresh protected claimant facade required')
        grant=self._handoff.claim(group,proof,request_id)
        if grant is None:
            return {'state':'WAIT','reason':'BOOTH_BUSY'}
        return self.recover_original_owed(grant)

    def _original_claim_grant(self,grant):
        from photobooth.post_preview_sandbox_handoff import require_acked_worker_receipt
        with self.ledger.write():
            self.ledger._owned(grant.lease)
            request=self.ledger.db.execute('SELECT * FROM pp_protected_claim_ops WHERE request_id=?',
                                          (grant.request_id,)).fetchone()
            expected=dict(state='REACQUIRED',purchase_group_id=grant.purchase_group_id,
                booth_id=grant.lease.booth_id,draft_id=grant.lease.draft_id,visit_id=grant.lease.visit_id,
                generation=grant.lease.generation,entitlement_id=grant.entitlement_id,
                proof_sha256=grant.proof_sha256)
            if not request or any(request[k]!=v for k,v in expected.items()):
                raise DraftHeld('Original durable claim grant changed')
            receipt=self.ledger.db.execute('SELECT * FROM pp_isolation_ops WHERE operation_id=?',
                                           (request['release_operation'],)).fetchone()
            if (not receipt or receipt['draft_id']!=grant.lease.draft_id
                    or receipt['booth_id']!=grant.lease.booth_id
                    or receipt['original_generation']+2!=grant.lease.generation):
                raise DraftHeld('Original claimed worker generation changed')
            require_acked_worker_receipt(self.ledger,receipt)
            finance=self.ledger.db.execute('SELECT * FROM pp_purchase_finance WHERE purchase_group_id=?',
                                           (grant.purchase_group_id,)).fetchone()
            paid=self.ledger.db.execute('SELECT status FROM pp_paid_services WHERE purchase_group_id=?',
                                        (grant.purchase_group_id,)).fetchone()
            if (not finance or finance['review_required'] or finance['entitlement_id']!=grant.entitlement_id
                    or paid and paid['status']!='OWED'):
                raise DraftHeld('Original claimed paid obligation changed')

    def recover_original_owed(self,grant):
        """No bare lease/DB boot adoption; consume our typed backend result once."""
        self._active()
        if (type(grant) is not ProtectedClaimGrant or self.lease is not None
                or self.group is not None or self.phase!='confirm'):
            raise DraftHeld('Fresh protected original claim facade required')
        def restore(original):
            from .post_preview_checkout import PrivateCheckoutService
            self._original_claim_grant(original)
            # Reuse frozen-hash validation and original ticket visibility policy;
            # do not construct a mock service or attach local proof/provider keys.
            PrivateCheckoutService.recover_original_owed(self,original.lease,original.purchase_group_id)
            self._original_claim_grant(original)
            self._active()
            return self.snapshot()
        try:return self._handoff.consume(grant,restore)
        except Exception:
            self.hide_private()
            raise DraftHeld('Original private claim restoration held') from None

    def offer_claim(self):
        self._active()
        if self.phase not in {'claim_proof', 'checkout_ready'}:
            raise DraftHeld('Original prepayment proof phase required')
        offer = self._ccp.private_offer(self.group, self.lease)
        qr = render_private_ccp(offer)
        self._active()
        self._offer, self._claim_qr = offer, qr
        self.phase = 'claim_proof'
        return self.snapshot()

    def ccp_visible(self, offer):
        self._active()
        if self.phase != 'claim_proof' or offer is not self._offer:
            raise DraftHeld('Original genuinely rendered proof required')
        self._ccp.mark_visible(self.lease, offer)
        self._active()
        self.phase = 'checkout_ready'
        return self.snapshot()

    # Reuse original payment state/QR handling without calling its mock-only
    # constructor or attaching any in-process financial/proof authority.
    from .post_preview_checkout import PrivateCheckoutService as _Original
    begin_payment = _Original.begin_payment
    check_payment = _Original.check_payment
    continue_payment = _Original.continue_payment
    _observe = _Original._observe
    del _Original

    def prepare_ticket(self):
        self._active()
        if self.phase != 'paid_hold' or self._ticket_was_dismissed:
            raise DraftHeld('Original paid ticket opportunity required')
        offer = self._ticket.private_offer(self.group, self.lease)
        qr = render_private_ccp(offer)
        self._active()
        self._ticket_offer, self._ticket_qr = offer, qr
        self.phase = 'ticket_offer'
        return self.snapshot()

    def ticket_visible(self, offer):
        self._active()
        if self.phase != 'ticket_offer' or offer is not self._ticket_offer:
            raise DraftHeld('Original genuinely rendered ticket required')
        self._ticket.mark_visible(self.lease, offer)
        self._active()
        self.phase = 'ticket_visible'
        return self.snapshot()

    def ticket_send_receipt(self):
        self._active()
        if self.phase != 'ticket_visible' or self._ticket_offer is None:
            raise DraftHeld('Original visible ticket required')
        receipt = self._ticket.send_receipt_once(self.lease, self._ticket_offer)
        self._active()
        self._ticket_receipt = receipt
        return self.snapshot()

    def ticket_dismiss(self):
        self._active()
        if self.phase != 'ticket_visible' or self._ticket_offer is None:
            raise DraftHeld('Original visible ticket required')
        self._ticket.dismiss(self.lease, self._ticket_offer)
        self._active()
        self._ticket_offer = self._ticket_qr = None
        self._ticket.hide_private()
        self._ticket_was_dismissed = True
        self.phase = 'paid_hold'
        return self.snapshot()

    def _delivery_action(self, action, phases):
        self._active()
        if self.phase not in phases or not self._ticket_was_dismissed:
            raise DraftHeld('Original ticket must finish before purchased delivery')
        result = action(self.group, self.lease)
        self._active()
        self._delivery_state = result
        self.phase = 'paid_delivery'
        return self.snapshot()

    def prepare_paid_delivery(self):
        return self._delivery_action(self._delivery.prepare, {'paid_hold'})

    def paid_delivery_status(self):
        return self._delivery_action(self._delivery.inspect, {'paid_delivery'})

    def paid_print_next(self):
        return self._delivery_action(self._delivery.print_next, {'paid_delivery'})

    def hide_private(self):
        super().hide_private()
        for client in (self._ccp, self._ticket, self._delivery, self._handoff):
            client.hide_private()
        self._offer = self._claim_qr = self._payment = self._payment_qr = None
        self._ticket_offer = self._ticket_qr = self._ticket_receipt = None
        self._delivery_state = None

    def snapshot(self):
        if self._hidden.is_set() or self._closed.is_set():
            return {'phase': 'hold'}
        if self.phase not in CHECKOUT_PHASES:
            return super().snapshot()
        result = dict(phase=self.phase, generation=self._generation,
            purchase_group_id=self.group, payment=self._payment,
            print_available=False, auto_print=False, drive_enabled=False,
            download_qr=None, folder_url=None, fulfillment_authorized=False)
        if self.phase in {'claim_proof', 'checkout_ready'}:
            result.update(ccp_offer=self._offer, ccp_qr=self._claim_qr)
        if self.phase == 'payment_pending':
            result['payment_qr'] = self._payment_qr
        if self.phase in TICKET_PHASES:
            result.update(ticket_offer=self._ticket_offer, ticket_qr=self._ticket_qr,
                          ticket_receipt=self._ticket_receipt)
        if self.phase in {'paid_hold', 'paid_delivery'}:
            result['ticket_dismissed'] = self._ticket_was_dismissed
        if self.phase == 'paid_delivery':
            result['delivery'] = self._delivery_state
        if self._hidden.is_set() or self._closed.is_set():
            return {'phase': 'hold'}
        return result
