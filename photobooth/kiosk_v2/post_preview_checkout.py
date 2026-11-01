"""Serialized private capture -> original CCP -> authenticated payment seam.

Currently restricted to explicit incomplete mock fixtures. No Sandbox customer
can pay until original-ticket/paid-delivery/release integration is implemented.
Never constructs provider, printer or Drive transports in the kiosk process.
"""
from photobooth.post_preview_ccp import OriginalCCPService, render_private_ccp
from photobooth.post_preview_checkout import ChargeReadiness
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_paid_delivery import OriginalPaidDeliveryMonitor
from photobooth.post_preview_paid_print import OriginalPaidPrintDispatcher
from .post_preview_photos import PrivatePhotoService


TICKET_PHASES = frozenset({'ticket_offer', 'ticket_visible', 'paid_delivery'})
CHECKOUT_PHASES = frozenset({'claim_proof', 'checkout_ready', 'payment_pending', 'payment_hold', 'paid_hold'}) | TICKET_PHASES


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
        self._paid_ticket = self._receipt_printer = self._receipt_lane = None
        self._ticket_offer = self._ticket_qr = self._ticket_receipt = None
        self._ticket_was_dismissed = False
        self._paid_delivery = self._paid_print = self._paid_printer = None
        self._paid_printer_lane = self._delivery_state = None
        super().__init__(root, booth_id=payment_client.booth_id, **kwargs)
        self._ccp = OriginalCCPService(self.ledger, protector, merchant_id, allow_synthetic=True)


    @property
    def paid_ticket_enabled(self):
        return self._paid_ticket is not None

    def attach_paid_ticket(self, service, *, printer=None, shared_lane=None):
        """Explicit synthetic-only injection until paid-delivery/claim is complete.

        No customer/Sandbox launch can attach a money or printer transport here.
        The service must use our original backend payment ledger and merchant.
        """
        if (self._paid_ticket is not None or not isinstance(service, OriginalRecoveryTicketService)
                or service.ledger is not self.ledger or service.merchant_id != self._ccp.merchant_id
                or not getattr(service.protector, 'synthetic', False)
                or self.phase not in {'confirm', 'final_preview'}):
            raise DraftHeld('Exact original fixture ticket authority required')
        self._paid_ticket, self._receipt_printer, self._receipt_lane = (
            service, printer, shared_lane)

    def prepare_ticket(self):
        self._active()
        if (self.phase != 'paid_hold' or self._paid_ticket is None
                or self._ticket_was_dismissed or
                (self._payment or {}).get('obligation_state') != 'OWED'):
            raise DraftHeld('Fresh original paid obligation required for ticket')
        self._paid_ticket.prepare(self.lease)
        offer = self._paid_ticket.private_offer(self.lease)
        qr = render_private_ccp(offer)
        self._active()
        self._ticket_offer, self._ticket_qr = offer, qr
        self.phase = 'ticket_offer'
        return self.snapshot()

    def ticket_visible(self, offer):
        self._active()
        if (self.phase != 'ticket_offer' or offer is not self._ticket_offer
                or not self._paid_ticket):
            raise DraftHeld('Genuinely visible original Recovery Ticket required')
        self._paid_ticket.mark_visible(self.lease, offer)
        self._active()
        self.phase = 'ticket_visible'
        return self.snapshot()

    def ticket_send_receipt(self):
        self._active()
        if (self.phase != 'ticket_visible' or self._ticket_offer is None
                or self._paid_ticket is None):
            raise DraftHeld('Original ticket must be genuinely visible before receipt')
        self._ticket_receipt = self._paid_ticket.send_receipt_once(
            self.lease, self._ticket_offer, self._receipt_printer,
            send_lock=self._receipt_lane)
        return self.snapshot()

    def ticket_dismiss(self):
        self._active()
        if (self.phase != 'ticket_visible' or self._ticket_offer is None
                or self._paid_ticket is None):
            raise DraftHeld('Original visible ticket must precede dismissal')
        self._paid_ticket.dismiss(self.lease, self._ticket_offer)
        self._ticket_offer = self._ticket_qr = None
        self._ticket_was_dismissed = True
        self.phase = 'paid_hold'  # Paid strips and Drive remain OWED until PP-05.c/d.
        return self.snapshot()


    @property
    def paid_delivery_enabled(self):
        return self._paid_delivery is not None and self._paid_print is not None

    def attach_paid_delivery(self, monitor, dispatcher, *, printer=None, shared_lane=None):
        """Bind exact *synthetic* paid delivery only before checkout admission.

        A real Sandbox/merchant launcher must use a separately verified adapter
        and cannot accidentally select the incomplete fixture-only path.
        """
        if (not isinstance(monitor,OriginalPaidDeliveryMonitor)
                or not isinstance(dispatcher,OriginalPaidPrintDispatcher)
                or monitor.binder.ledger is not self.ledger
                or dispatcher.binder is not monitor.binder
                or dispatcher.preparer is not monitor.preparer
                or self._paid_ticket is None
                or shared_lane is None or shared_lane is not self._receipt_lane
                or self._paid_delivery is not None
                or self.phase not in {'confirm','final_preview'}):
            raise DraftHeld('Exact original synthetic paid delivery/receipt lane required')
        self._paid_delivery, self._paid_print = monitor, dispatcher
        self._paid_printer, self._paid_printer_lane = printer, shared_lane

    def prepare_paid_delivery(self):
        """Resolve one original PAID folder and stage its saved approved photos."""
        self._active()
        if (self.phase!='paid_hold' or not self.paid_delivery_enabled
                or self._ticket_was_dismissed is not True):
            raise DraftHeld('Original paid ticket must precede purchased photo fulfillment')
        self._paid_delivery.binder.bind(self.lease,self.group,self.templates)
        view=self._paid_delivery.enqueue(self.lease,self.group,self.templates)
        self._active()
        self._delivery_state=view
        self.phase='paid_delivery'
        return self.snapshot()

    def paid_delivery_status(self):
        self._active()
        if self.phase!='paid_delivery' or not self.paid_delivery_enabled:
            raise DraftHeld('Original paid delivery session not available')
        self._delivery_state=self._paid_delivery.inspect(self.lease,self.group)
        return self.snapshot()

    def paid_print_next(self):
        """Send the next PREPARED *purchased* strip once on the shared lane."""
        self._active()
        if self.phase!='paid_delivery' or not self.paid_delivery_enabled:
            raise DraftHeld('Original paid strip is unavailable')
        before=self._paid_delivery.inspect(self.lease,self.group)
        if self._paid_printer is None:
            raise DraftHeld('No configured photo printer; preserve all original print jobs')
        pending=[t.template_id for t in self.templates
                 if before['print_states'].get(t.template_id)=='PREPARED']
        if not pending:
            return self.snapshot()
        result=self._paid_print.send_once(
            self.lease,self.group,pending[0],self._paid_printer,
            shared_lane=self._paid_printer_lane)
        self._active()
        self._delivery_state=self._paid_delivery.inspect(self.lease,self.group)
        return self.snapshot()

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

    def close(self):
        if self._paid_delivery is not None and self._paid_delivery.worker is not None:
            self._paid_delivery.worker.stop()
        super().close()

    def hide_private(self):
        super().hide_private()
        if self._ccp is not None:
            self._ccp.hide_private()
        if self._paid_ticket is not None:
            self._paid_ticket.hide_private()
        self._offer = self._claim_qr = self._payment_qr = None
        self._ticket_offer = self._ticket_qr = None

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
        if self.phase in TICKET_PHASES:
            result.update(ticket_offer=self._ticket_offer, ticket_qr=self._ticket_qr,
                          ticket_receipt=self._ticket_receipt)
        if self.phase == 'paid_hold':
            result['ticket_dismissed'] = self._ticket_was_dismissed
        if self.phase == 'paid_delivery':
            result['delivery'] = self._delivery_state
            result['ticket_dismissed'] = True
        if self._hidden.is_set() or self._closed.is_set():
            return {'phase': 'hold'}
        return result
