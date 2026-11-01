"""Original post-PAID recovery capability, reusing protected CCP primitives.

CCP and Recovery Ticket have different fixed profiles, tables and verifiers.
Neither credential by itself authorizes media, printing or booth admission.
"""
from dataclasses import dataclass
import uuid

from photobooth.credential_vault import VaultUnavailable
from photobooth.post_preview_ccp import OriginalCCPService, PendingCCPOffer, VerifiedCCPScope
from photobooth.post_preview_store import DraftHeld


@dataclass(frozen=True)
class PendingRecoveryOffer(PendingCCPOffer):
    def __str__(self):
        return '<private original Recovery Ticket>'


@dataclass(frozen=True)
class VerifiedRecoveryScope(VerifiedCCPScope):
    pass


class OriginalRecoveryTicketService(OriginalCCPService):
    KIND = 'RECOVERY'
    OFFER_TYPE = PendingRecoveryOffer
    VERIFIED_TYPE = VerifiedRecoveryScope
    POLICY_VERSION = 'post-preview-ticket-paid-anchor-pilot-v1'

    def __init__(self, payments, protector, **kwargs):
        self.payments = payments
        super().__init__(payments.ledger, protector, payments.merchant_id, **kwargs)

    def _scope(self, lease):
        scope, _ = super()._scope(lease)
        intent, finance = self.payments._group(scope['purchase_group_id'], lease.booth_id)
        if not finance or not finance['entitlement_id'] or finance['review_required']:
            raise DraftHeld('Original verified paid entitlement required')
        attempt = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE attempt_id=?',
                                         (finance['legitimate_paid_attempt'],)).fetchone()
        if not attempt or attempt['payment_state'] != 'PAID' or not attempt['provider_ref']:
            raise DraftHeld('Independent original settlement required')
        scope.update(entitlement_id=finance['entitlement_id'], paid_attempt_id=attempt['attempt_id'],
                     amount=finance['amount'], currency='IDR')
        return scope, dict(intent, paid_anchor=finance['paid_first_observed_at'],
                          settlement_at=attempt['verified_at'], provider_state=attempt['last_provider_state'])

    def _anchor(self, intent):
        return intent['paid_anchor']

    def _recent(self, intent):
        if (intent['settlement_at'] is None or intent['provider_state'] != 'settlement'
                or not 0 <= self._now()-intent['settlement_at'] <= 30):
            raise DraftHeld('Fresh independently verified original settlement required')

    def issue_once(self, lease):
        with self.ledger.write():
            _, intent = self._scope(lease)
            self._recent(intent)
        return super().issue_once(lease)

    def prepare(self, lease):
        """Persist original paid identity and one screen/receipt intent, no I/O."""
        info = self.issue_once(lease)
        with self.ledger.write():
            scope, intent = self._scope(lease)
            self._recent(intent)
            group = scope['purchase_group_id']
            row = self.ledger.db.execute('SELECT * FROM pp_paid_services WHERE purchase_group_id=?', (group,)).fetchone()
            if row is None:
                if self.ledger.db.execute("SELECT 1 FROM pp_events WHERE draft_id=? AND event='PAID_SERVICE_BOUND'",
                                           (lease.draft_id,)).fetchone():
                    raise VaultUnavailable('Original paid service journal is missing')
                self.ledger.db.execute('''INSERT INTO pp_paid_services
                    (purchase_group_id,service_id,entitlement_id,contract_sha256,retention_anchor)
                    VALUES(?,?,?,?,?)''', (group, uuid.uuid4().hex, scope['entitlement_id'],
                                           scope['contract_sha256'], intent['paid_anchor']))
                self.ledger._event(lease.draft_id,'PAID_SERVICE_BOUND')
                row = self.ledger.db.execute('SELECT * FROM pp_paid_services WHERE purchase_group_id=?',(group,)).fetchone()
            if row['entitlement_id'] != scope['entitlement_id'] or row['contract_sha256'] != scope['contract_sha256']:
                raise DraftHeld('Original paid service binding changed')
            presentation = self.ledger.db.execute('SELECT * FROM pp_ticket_presentations WHERE purchase_group_id=?',(group,)).fetchone()
            if presentation is None:
                if self.ledger.db.execute("SELECT 1 FROM pp_events WHERE draft_id=? AND event='TICKET_PRESENTATION_PREPARED'",
                                           (lease.draft_id,)).fetchone():
                    raise VaultUnavailable('Original ticket presentation journal is missing')
                self.ledger.db.execute('''INSERT INTO pp_ticket_presentations
                    (purchase_group_id,presentation_id,receipt_job_id) VALUES(?,?,?)''',
                    (group, uuid.uuid4().hex, uuid.uuid4().hex))
                self.ledger._event(lease.draft_id,'TICKET_PRESENTATION_PREPARED')
                presentation = self.ledger.db.execute('SELECT * FROM pp_ticket_presentations WHERE purchase_group_id=?',(group,)).fetchone()
            return dict(info, service_id=row['service_id'], presentation_id=presentation['presentation_id'],
                        receipt_job_id=presentation['receipt_job_id'])

    def private_offer(self, lease):
        with self.ledger.write():
            scope, intent = self._scope(lease)
            self._recent(intent)
            row = self.ledger.db.execute('''SELECT p.screen_state,c.offered_at FROM pp_ticket_presentations p
                JOIN pp_ticket_credentials c USING(purchase_group_id) WHERE purchase_group_id=?''',
                (scope['purchase_group_id'],)).fetchone()
            if not row or row['screen_state'] != 'NOT_OFFERED' or row['offered_at'] is not None:
                raise VaultUnavailable('Original ticket opportunity cannot be replayed')
        return super().private_offer(lease)

    def _after_visible_locked(self, lease, offer, now):
        row = self.ledger.db.execute('SELECT * FROM pp_ticket_presentations WHERE purchase_group_id=?',
                                     (offer.purchase_group_id,)).fetchone()
        if not row or row['screen_state'] == 'DISMISSED':
            raise VaultUnavailable('Original ticket presentation is unavailable')
        if row['screen_state'] == 'VISIBLE':
            if row['render_permit_id'] != offer.presentation_id:
                raise VaultUnavailable('Original ticket render permit changed')
            return
        self.ledger.db.execute('''UPDATE pp_ticket_presentations SET screen_state='VISIBLE',
            shown_at=?,render_permit_id=? WHERE purchase_group_id=?''',
            (now,offer.presentation_id,offer.purchase_group_id))

    def dismiss(self, lease, offer):
        with self.ledger.write():
            scope, _ = self._scope(lease)
            with self._privacy_lock:
                entry = self._offers.get(getattr(offer,'presentation_id',None))
            row = self.ledger.db.execute('SELECT * FROM pp_ticket_presentations WHERE purchase_group_id=?',
                                         (scope['purchase_group_id'],)).fetchone()
            if row and row['screen_state'] == 'DISMISSED' and row['render_permit_id'] == offer.presentation_id:
                return False
            if (not entry or entry[0] is not offer or not row or row['screen_state'] != 'VISIBLE'
                    or row['render_permit_id'] != offer.presentation_id):
                raise VaultUnavailable('Original visible ticket required')
            self.ledger.db.execute("UPDATE pp_ticket_presentations SET screen_state='DISMISSED',dismissed_at=? WHERE purchase_group_id=?",
                                   (self._now(),scope['purchase_group_id']))
            self.ledger._event(lease.draft_id,'TICKET_DISMISSED')
        with self._privacy_lock:
            self._offers.clear()
        return True
