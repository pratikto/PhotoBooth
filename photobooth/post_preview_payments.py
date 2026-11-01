"""Server-side new-order QRIS attempt coordinator, never a GUI evidence writer.

Reuses original strict Midtrans evidence/QR URL validation and fixed Sandbox
transport. No provider idempotency header or production endpoint is invented.
An authenticated backend API must own this service before native payment is
mounted. Current customer GUI cannot call this module with provider evidence.
"""
import json
import math
import uuid

from photobooth.checkout_store import identifier
from photobooth.midtrans_sandbox import MidtransSandboxClient
from photobooth.post_preview_checkout import ChargeReadiness, digest
from photobooth.post_preview_readiness import ReadinessScope, TrustedChargeReadiness
from photobooth.post_preview_store import DraftHeld, quote_post_preview
from photobooth.qris_evidence import authenticated_notification, idr_amount, provider_evidence, qr_url_from_status


class PostPreviewPayments:
    def __init__(self, ledger, provider, merchant_id, *, readiness, server_key=None, poll_seconds=10):
        identifier(merchant_id)
        mode = 'sandbox' if isinstance(provider, MidtransSandboxClient) else getattr(provider, 'mode', None)
        if mode not in {'sandbox', 'mock'}:
            raise ValueError('Only isolated mock or fixed Midtrans Sandbox transport is supported')
        if type(poll_seconds) not in (int, float) or not math.isfinite(poll_seconds) or not 0 <= poll_seconds <= 60:
            raise ValueError('Bounded payment polling required')
        if mode != 'mock' and poll_seconds < 10:
            raise ValueError('Sandbox polling must retain provider-safe pacing')
        self.ledger, self.provider, self.merchant_id = ledger, provider, merchant_id
        self.mode, self.readiness, self.poll_seconds = mode, readiness, poll_seconds
        self._server_key = server_key

    def _now(self):
        value = self.ledger.now()
        if type(value) not in (int, float) or not math.isfinite(value):
            raise DraftHeld('Payment clock unavailable')
        return value

    def _audit(self, group, attempt, outcome):
        self.ledger.db.execute('INSERT INTO pp_payment_audit(purchase_group_id,attempt_id,outcome,created_at) VALUES(?,?,?,?)',
                               (group, attempt, outcome, self._now()))

    def _ccp_ready(self, intent, booth):
        ccp = self.ledger.db.execute('SELECT * FROM pp_ccp_credentials WHERE purchase_group_id=?',
                                      (intent['purchase_group_id'],)).fetchone()
        if (not ccp or ccp['merchant_id'] != self.merchant_id or ccp['booth_id'] != booth
                or ccp['revoked'] or ccp['offered_at'] is None
                or not ccp['issued_at'] <= self._now() < ccp['expires_at']):
            return False
        try: scope = json.loads(ccp['scope_json'])
        except (TypeError, ValueError): return False
        if not isinstance(scope, dict): return False
        return (scope.get('kind') == 'CCP' and scope.get('version') == 1
                and scope.get('merchant_id') == self.merchant_id and scope.get('booth_id') == booth
                and scope.get('purchase_group_id') == intent['purchase_group_id']
                and scope.get('draft_id') == intent['draft_id']
                and scope.get('contract_sha256') == intent['contract_sha256'])

    def _require_readiness(self, observation, intent, booth):
        if type(observation) is TrustedChargeReadiness:
            observation.require(ReadinessScope(intent['purchase_group_id'], booth,
                intent['contract_sha256'], intent['generation']), now=self._now())
        elif self.mode == 'mock' and type(observation) is ChargeReadiness:
            # Historical explicitly synthetic fixtures only. Sandbox admission
            # never accepts an unscoped, untimestamped set of booleans.
            observation.require()
        else:
            raise DraftHeld('Trusted fresh original-scope charge readiness required')

    def _group(self, group, booth):
        identifier(group); identifier(booth)
        intent = self.ledger.db.execute('''SELECT i.*,d.booth_id,d.visit_id,d.lifecycle,d.generation
            FROM pp_checkout_intents i JOIN pp_drafts d ON i.draft_id=d.draft_id
            WHERE i.purchase_group_id=? AND d.booth_id=?''', (group, booth)).fetchone()
        if not intent:
            raise DraftHeld('Original purchase group required')
        finance = self.ledger.db.execute('SELECT * FROM pp_purchase_finance WHERE purchase_group_id=?', (group,)).fetchone()
        if finance and (finance['merchant_id'] != self.merchant_id or finance['provider_mode'] != self.mode):
            raise DraftHeld('Original merchant/provider context changed')
        if finance:
            contract = json.loads(intent['contract_json'])
            if (digest(contract) != intent['contract_sha256'] or contract.get('booth_id') != booth
                    or contract.get('draft_id') != intent['draft_id']
                    or contract.get('amount') != finance['amount']):
                raise DraftHeld('Original payment/media binding changed')
        # Recover a cancellation intent even if a process died between the
        # original durable lifecycle event and its finance subjournal update.
        if finance and intent['lifecycle'] in {'USER_CANCEL', 'VISIT_ABANDONED'}:
            self.ledger.db.execute('UPDATE pp_purchase_finance SET cancel_requested=1 WHERE purchase_group_id=?', (group,))
            self.ledger.db.execute('''UPDATE pp_payment_attempts SET cancel_phase='PREPARED'
                WHERE attempt_id=(SELECT attempt_id FROM pp_payment_attempts WHERE purchase_group_id=?
                ORDER BY ordinal DESC LIMIT 1) AND cancel_phase='NONE' AND payment_state NOT IN
                ('PAID','CANCELLED_UNPAID','EXPIRED_UNPAID','TERMINAL_UNPAID','NOT_CREATED')''', (group,))
            finance = self.ledger.db.execute('SELECT * FROM pp_purchase_finance WHERE purchase_group_id=?', (group,)).fetchone()
        return intent, finance

    def _prepare(self, lease, *, renewal=False, expired_attempt=None, observation=None):
        with self.ledger.write():
            self.ledger._owned(lease)
            intent = self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?', (lease.draft_id,)).fetchone()
            if not intent: raise DraftHeld('Frozen original checkout required')
            group = intent['purchase_group_id']
            intent, finance = self._group(group, lease.booth_id)
            contract = json.loads(intent['contract_json'])
            if (digest(contract) != intent['contract_sha256'] or
                    quote_post_preview(contract['quantities']).total_amount != contract['amount']):
                raise DraftHeld('Original server quote or artifact contract changed')
            rows = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE purchase_group_id=? ORDER BY ordinal', (group,)).fetchall()
            if rows and not renewal:
                return group, dict(rows[-1])
            if finance and (finance['entitlement_id'] or finance['cancel_requested'] or finance['review_required']):
                raise DraftHeld('Original paid/cancelled/review purchase cannot create another charge')
            if renewal:
                if (not rows or rows[-1]['attempt_id'] != expired_attempt
                        or rows[-1]['payment_state'] != 'EXPIRED_UNPAID'
                        or rows[-1]['last_provider_state'] != 'expire' or len(rows) >= 3):
                    raise DraftHeld('Only verified original unpaid expiry may continue, maximum QR3')
            elif rows:
                return group, dict(rows[-1])
            elif self.ledger.db.execute("SELECT 1 FROM pp_events WHERE draft_id=? AND event='PAYMENT_ATTEMPT_PREPARED'", (lease.draft_id,)).fetchone():
                raise DraftHeld('Original payment attempt journal is missing')
            if not self._ccp_ready(intent, lease.booth_id):
                raise DraftHeld('Genuinely offered original CCP required before payment')
            self._require_readiness(observation, intent, lease.booth_id)
            if finance is None:
                self.ledger.db.execute('INSERT INTO pp_purchase_finance(purchase_group_id,merchant_id,provider_mode,amount) VALUES(?,?,?,?)',
                                       (group, self.merchant_id, self.mode, contract['amount']))
            attempt_id, order_id = uuid.uuid4().hex, 'PP'+uuid.uuid4().hex
            self.ledger.db.execute('''INSERT INTO pp_payment_attempts
                (attempt_id,purchase_group_id,ordinal,provider_order_id,create_phase)
                VALUES(?,?,?,?,'PREPARED')''', (attempt_id, group, len(rows)+1, order_id))
            self.ledger._event(lease.draft_id, 'PAYMENT_ATTEMPT_PREPARED')
            self._audit(group, attempt_id, 'CREATE_PREPARED')
            row = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
            return group, dict(row)

    def begin(self, lease):
        with self.ledger.write():
            self.ledger._owned(lease)
            intent = self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?', (lease.draft_id,)).fetchone()
            if not intent: raise DraftHeld('Original frozen checkout required')
            existing = self.ledger.db.execute('SELECT create_phase FROM pp_payment_attempts WHERE purchase_group_id=? ORDER BY ordinal DESC LIMIT 1', (intent['purchase_group_id'],)).fetchone()
        observation = (self.readiness(intent['purchase_group_id'])
                       if existing is None or existing['create_phase'] == 'PREPARED' else None)
        group, attempt = self._prepare(lease, observation=observation)
        self._send_original(group, lease.booth_id, attempt['attempt_id'], observation=observation)
        return self.reconcile(group, lease.booth_id, attempt_id=attempt['attempt_id'], force=True)

    def _send_original(self, group, booth, attempt_id, *, observation=None):
        with self.ledger.write():
            intent, finance = self._group(group, booth)
            attempt = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE attempt_id=? AND purchase_group_id=?',
                                              (attempt_id, group)).fetchone()
            if not attempt or attempt['create_phase'] != 'PREPARED':
                return
            if (finance['entitlement_id'] or intent['lifecycle'] != 'ACTIVE' or finance['cancel_requested']
                    or finance['review_required'] or not self._ccp_ready(intent, booth)):
                self.ledger.db.execute("UPDATE pp_payment_attempts SET create_phase='WITHHELD',payment_state='NOT_CREATED' WHERE attempt_id=?", (attempt_id,))
                self._audit(group, attempt_id, 'CREATE_WITHHELD')
                return
            self._require_readiness(observation, intent, booth)
            self.ledger.db.execute("UPDATE pp_payment_attempts SET create_phase='SENT' WHERE attempt_id=?", (attempt_id,))
            self._audit(group, attempt_id, 'CREATE_SENT')
            order = {'id': attempt['provider_order_id'], 'amount': finance['amount'], 'provider_ref': None}
        try:
            response = self.provider.create_qris(order['id'], order['amount'])
            # Preserve a verified v4 action from CREATE, but never grant PAID
            # from that response: independent GET status is mandatory below.
            evidence = provider_evidence(response, order, self.merchant_id)
            if evidence['transaction_status'] == 'pending':
                url = qr_url_from_status(response, evidence)
                with self.ledger.write():
                    current = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE attempt_id=?', (attempt_id,)).fetchone()
                    if current['provider_ref'] not in (None, evidence['transaction_id']):
                        self.ledger.db.execute('UPDATE pp_purchase_finance SET review_required=1 WHERE purchase_group_id=?', (group,))
                        self._audit(group, attempt_id, 'PROVIDER_REFERENCE_CONFLICT')
                    else:
                        self.ledger.db.execute('UPDATE pp_payment_attempts SET provider_ref=?,qr_url=? WHERE attempt_id=?',
                                               (evidence['transaction_id'], url, attempt_id))
        except Exception:
            with self.ledger.write():
                self.ledger.db.execute("UPDATE pp_payment_attempts SET create_phase='UNKNOWN' WHERE attempt_id=? AND create_phase='SENT'", (attempt_id,))
                self._audit(group, attempt_id, 'CREATE_UNKNOWN')
        # SENT/UNKNOWN are never POSTed again, including 404 and process restart.

    def reconcile(self, group, booth, *, attempt_id=None, force=False):
        with self.ledger.write():
            intent, finance = self._group(group, booth)
            if finance is None: raise DraftHeld('Original payment context required')
            if attempt_id is None:
                attempt = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE purchase_group_id=? ORDER BY ordinal DESC LIMIT 1', (group,)).fetchone()
            else:
                attempt = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE purchase_group_id=? AND attempt_id=?', (group, attempt_id)).fetchone()
            if not attempt: raise DraftHeld('Original provider attempt required')
            now = self._now()
            if (attempt['create_phase'] == 'WITHHELD' or attempt['reconcile_token'] and attempt['lease_until'] > now
                    or not force and attempt['next_check_at'] > now
                    or force and attempt['priority_after'] > now
                    or attempt['verified_at'] is not None and now < attempt['verified_at']):
                return self._view(group, booth)
            token = uuid.uuid4().hex
            self.ledger.db.execute('UPDATE pp_payment_attempts SET reconcile_token=?,lease_until=?,next_check_at=?,priority_after=? WHERE attempt_id=?',
                                   (token, now+45, now+self.poll_seconds, now+(1 if self.mode == 'sandbox' else 0), attempt['attempt_id']))
            original = dict(attempt)
            order = {'id': attempt['provider_order_id'], 'amount': finance['amount'], 'provider_ref': attempt['provider_ref']}
        evidence = None
        outcome = 'UNKNOWN'
        qr_url = None
        try:
            response = self.provider.get_status(order['id'])
            if isinstance(response, dict) and response.get('status_code') == '404':
                outcome = 'NOT_FOUND_UNPROVEN'
            else:
                evidence = provider_evidence(response, order, self.merchant_id)
                if evidence['transaction_status'] == 'pending':
                    qr_url = qr_url_from_status(response, evidence, existing_url=original['qr_url'])
                outcome = 'VERIFIED'
        except ValueError:
            outcome = 'PROVIDER_MISMATCH'
        except Exception:
            outcome = 'UNKNOWN'
        with self.ledger.write():
            intent, finance = self._group(group, booth)
            current = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE attempt_id=?', (original['attempt_id'],)).fetchone()
            now = self._now()
            if current['reconcile_token'] != token or current['lease_until'] < now:
                # A stale worker cannot grant live fulfillment, but verified
                # original money received must not disappear from OWED audit.
                if evidence and evidence['transaction_status'] == 'settlement':
                    if current['provider_ref'] in (None, evidence['transaction_id']):
                        other = self.ledger.db.execute('SELECT 1 FROM pp_payment_attempts WHERE provider_ref=? AND attempt_id!=?',
                            (evidence['transaction_id'], current['attempt_id'])).fetchone()
                        if not other:
                            self.ledger.db.execute("UPDATE pp_payment_attempts SET payment_state='PAID',provider_ref=? WHERE attempt_id=?",
                                                   (evidence['transaction_id'], current['attempt_id']))
                            self._paid_obligation(group, current['attempt_id'])
                            self._audit(group, current['attempt_id'], 'STALE_PAID_OWED')
                # Retain a different current reconciliation's reservation.
                return self._view(group, booth)
            self.ledger.db.execute('UPDATE pp_payment_attempts SET reconcile_token=NULL,lease_until=0 WHERE attempt_id=?', (current['attempt_id'],))
            self._audit(group, current['attempt_id'], outcome)
            if evidence is None:
                if outcome == 'PROVIDER_MISMATCH':
                    self.ledger.db.execute('UPDATE pp_purchase_finance SET review_required=1 WHERE purchase_group_id=?', (group,))
                return self._view(group, booth)
            state = evidence['transaction_status']
            other_reference = self.ledger.db.execute('SELECT attempt_id FROM pp_payment_attempts WHERE provider_ref=? AND attempt_id!=?',
                (evidence['transaction_id'], current['attempt_id'])).fetchone()
            if other_reference or current['provider_ref'] not in (None, evidence['transaction_id']):
                self.ledger.db.execute('UPDATE pp_purchase_finance SET review_required=1 WHERE purchase_group_id=?', (group,))
                self._audit(group, current['attempt_id'], 'PROVIDER_REFERENCE_CONFLICT')
                return self._view(group, booth)
            mapped = {'settlement': 'PAID', 'pending': 'PENDING', 'expire': 'EXPIRED_UNPAID',
                      'cancel': 'CANCELLED_UNPAID', 'deny': 'TERMINAL_UNPAID', 'failure': 'TERMINAL_UNPAID',
                      'refund': 'REVIEW', 'partial_refund': 'REVIEW'}[state]
            if current['payment_state'] == 'PAID': mapped = 'PAID'
            self.ledger.db.execute('''UPDATE pp_payment_attempts SET create_phase='VERIFIED',payment_state=?,
                last_provider_state=?,provider_ref=?,verified_at=?,expires_at=?,qr_url=COALESCE(?,qr_url) WHERE attempt_id=?''',
                (mapped, state, evidence['transaction_id'], now, evidence['expires_at'], qr_url, current['attempt_id']))
            if state == 'settlement' and finance['entitlement_id'] is None:
                self._paid_obligation(group, current['attempt_id'])
            if state in {'refund', 'partial_refund'}:
                self.ledger.db.execute('UPDATE pp_purchase_finance SET review_required=1 WHERE purchase_group_id=?', (group,))
            if state in {'expire', 'cancel', 'deny', 'failure', 'settlement'}:
                self.ledger.db.execute("UPDATE pp_payment_attempts SET cancel_phase='VERIFIED' WHERE attempt_id=? AND cancel_phase!='NONE'", (current['attempt_id'],))
            return self._view(group, booth, checked_attempt=current['attempt_id'], provider_state=state)

    def _paid_obligation(self, group, attempt_id):
        self.ledger.db.execute('UPDATE pp_purchase_finance SET entitlement_id=?,legitimate_paid_attempt=?,paid_first_observed_at=? WHERE purchase_group_id=? AND entitlement_id IS NULL',
                               (uuid.uuid4().hex, attempt_id, self._now(), group))

    def reconcile_all(self, group, booth, *, force=False):
        with self.ledger.write():
            self._group(group, booth)
            ids = [r[0] for r in self.ledger.db.execute('SELECT attempt_id FROM pp_payment_attempts WHERE purchase_group_id=? ORDER BY ordinal', (group,))]
        observed = []
        for attempt_id in ids:
            self._send_cancel(group, booth, attempt_id)
            observed.append(self.reconcile(group, booth, attempt_id=attempt_id, force=force))
        chosen = next((r for r in observed if r['paid_verified']),
                      next((r for r in reversed(observed) if r['fresh_checked']), None))
        with self.ledger.write():
            return self._view(group, booth, checked_attempt=chosen['checked_attempt_id'] if chosen else None,
                              provider_state=chosen['provider_state'] if chosen else None)

    def _view(self, group, booth, *, checked_attempt=None, provider_state=None):
        intent, finance = self._group(group, booth)
        if finance is None:
            contract = json.loads(intent['contract_json'])
            return {'purchase_group_id': group, 'booth_id': booth, 'amount': contract['amount'],
                    'state': 'NOT_CREATED', 'entitlement_id': None, 'obligation_state': 'NONE',
                    'excess_paid_attempts': [], 'fresh_checked': False, 'checked_attempt_id': None,
                    'provider_state': None, 'paid_verified': False, 'fulfillment_authorized': False,
                    'attempts': [], 'qr_url': None, 'retry_after': 0}
        attempts = [dict(r) for r in self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE purchase_group_id=? ORDER BY ordinal', (group,))]
        paid = [r for r in attempts if r['payment_state'] == 'PAID']
        live = intent['lifecycle'] == 'ACTIVE'
        state = ('REVIEW_REQUIRED' if finance['review_required'] else
                 'PAID_LIVE' if paid and live else 'PAID_UNCLAIMED' if paid else
                 attempts[-1]['payment_state'] if attempts else 'NOT_CREATED')
        current = attempts[-1] if attempts else None
        return {'purchase_group_id': group, 'booth_id': booth, 'amount': finance['amount'],
            'paid_first_observed_at': finance['paid_first_observed_at'],
            'state': state, 'entitlement_id': finance['entitlement_id'], 'obligation_state': 'OWED' if paid else 'NONE',
            'excess_paid_attempts': [r['attempt_id'] for r in paid if r['attempt_id'] != finance['legitimate_paid_attempt']],
            'fresh_checked': checked_attempt is not None, 'checked_attempt_id': checked_attempt,
            'provider_state': provider_state, 'paid_verified': provider_state == 'settlement',
            'fulfillment_authorized': False,  # PP-05/06 require independent owner/worker permits.
            'retry_after': max(0, current['next_check_at']-self._now()) if current else 0,
            'attempts': [{'attempt_id': r['attempt_id'], 'ordinal': r['ordinal'], 'provider_order_id': r['provider_order_id'],
                          'create_phase': r['create_phase'], 'state': r['payment_state']} for r in attempts],
            'qr_url': current['qr_url'] if current and live and not finance['cancel_requested'] and state == 'PENDING' else None}

    def inspect(self, group, booth):
        with self.ledger.write(): return self._view(group, booth)

    def continue_expired(self, lease, *, actively_continuing):
        if actively_continuing is not True:
            raise DraftHeld('Same original active customer must continue')
        with self.ledger.write():
            self.ledger._owned(lease)
            intent = self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?', (lease.draft_id,)).fetchone()
            if not intent: raise DraftHeld('Original purchase required')
            group = intent['purchase_group_id']
        fresh = self.reconcile(group, lease.booth_id, force=True)
        if not fresh['fresh_checked'] or fresh['provider_state'] != 'expire':
            raise DraftHeld('Fresh original provider unpaid expiry required')
        observation = self.readiness(group)
        group, attempt = self._prepare(lease, renewal=True, expired_attempt=fresh['checked_attempt_id'], observation=observation)
        self._send_original(group, lease.booth_id, attempt['attempt_id'], observation=observation)
        return self.reconcile(group, lease.booth_id, attempt_id=attempt['attempt_id'], force=True)

    def signal_lifecycle(self, lease, event):
        # Existing draft lifecycle semantics: suspend/inactivity warning are not
        # cancellation. No event here frees camera, printer or occupancy.
        try:
            self.ledger.lifecycle_event(lease, event)
        except DraftHeld:
            # Replay only the same exact original retirement; never revive it.
            with self.ledger.write():
                row = self.ledger.db.execute('SELECT * FROM pp_drafts WHERE draft_id=?', (lease.draft_id,)).fetchone()
                if (not row or row['booth_id'] != lease.booth_id or row['visit_id'] != lease.visit_id
                        or row['generation'] != lease.generation+1):
                    raise
                if event == 'VISIT_ABANDONED' and row['lifecycle'] == 'INACTIVITY_EXPIRED':
                    # Explicit second durable decision, not an alias for expiry
                    # or minimization. The already-fenced generation stays retired.
                    self.ledger.db.execute("UPDATE pp_drafts SET lifecycle='VISIT_ABANDONED',updated_at=? WHERE draft_id=?",
                                           (self._now(), lease.draft_id))
                    self.ledger._event(lease.draft_id, 'VISIT_ABANDONED')
                elif row['lifecycle'] != event:
                    raise
        with self.ledger.write():
            intent = self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?', (lease.draft_id,)).fetchone()
            if not intent: return
            group = intent['purchase_group_id']
            _, finance = self._group(group, lease.booth_id)
            if finance is None: return
            if event in {'USER_CANCEL', 'VISIT_ABANDONED'}:
                self.ledger.db.execute('UPDATE pp_purchase_finance SET cancel_requested=1 WHERE purchase_group_id=?', (group,))
                self._audit(group, None, event)
                attempt = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE purchase_group_id=? ORDER BY ordinal DESC LIMIT 1', (group,)).fetchone()
            else:
                return
        if attempt:
            self._send_cancel(group, lease.booth_id, attempt['attempt_id'])
            return self.reconcile(group, lease.booth_id, attempt_id=attempt['attempt_id'], force=True)

    def _send_cancel(self, group, booth, attempt_id):
        with self.ledger.write():
            self._group(group, booth)
            attempt = self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE attempt_id=? AND purchase_group_id=?', (attempt_id, group)).fetchone()
            if not attempt or attempt['cancel_phase'] != 'PREPARED': return
            if attempt['create_phase'] == 'PREPARED':
                self.ledger.db.execute("UPDATE pp_payment_attempts SET create_phase='WITHHELD',payment_state='NOT_CREATED',cancel_phase='VERIFIED' WHERE attempt_id=?", (attempt_id,))
                return
            self.ledger.db.execute("UPDATE pp_payment_attempts SET cancel_phase='SENT' WHERE attempt_id=?", (attempt_id,))
            self._audit(group, attempt_id, 'CANCEL_SENT')
        try:
            self.provider.cancel(attempt['provider_order_id'])
        except Exception:
            with self.ledger.write():
                self.ledger.db.execute("UPDATE pp_payment_attempts SET cancel_phase='UNKNOWN' WHERE attempt_id=? AND cancel_phase='SENT'", (attempt_id,))
                self._audit(group, attempt_id, 'CANCEL_UNKNOWN')

    def notification(self, data):
        order_id = authenticated_notification(data, self._server_key)
        with self.ledger.write():
            row = self.ledger.db.execute('''SELECT a.*,d.booth_id FROM pp_payment_attempts a
                JOIN pp_checkout_intents i ON a.purchase_group_id=i.purchase_group_id
                JOIN pp_drafts d ON i.draft_id=d.draft_id WHERE a.provider_order_id=?''', (order_id,)).fetchone()
        if row is None: return None
        with self.ledger.write():
            _, finance = self._group(row['purchase_group_id'], row['booth_id'])
            if idr_amount(data['gross_amount']) != finance['amount']:
                raise ValueError('Notification amount mismatch')
        # Notification status is never payment authority; GET original order.
        return self.reconcile(row['purchase_group_id'], row['booth_id'], attempt_id=row['attempt_id'], force=True)
