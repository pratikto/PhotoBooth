"""Bounded durable PP webhook ACK; provider GET runs only in a leased worker.

Uses the original LegacyNotificationInbox lease/backoff pattern with new-order
foreign keys. Stores authenticated scope only, never signature/key/status payload.
"""
import hashlib
import json
import uuid

from photobooth.qris_evidence import authenticated_notification, idr_amount


class PostPreviewNotificationInbox:
    def __init__(self, payments, *, capacity=10000):
        if type(capacity) is not int or not 1 <= capacity <= 10000:
            raise ValueError('Bounded inbox required')
        self.payments, self.ledger, self.capacity = payments, payments.ledger, capacity

    def accept(self, data):
        order = authenticated_notification(data, self.payments._server_key)
        # Authenticate before allocating disk; notification status is not evidence.
        fields = ('order_id', 'status_code', 'gross_amount', 'transaction_status', 'transaction_id')
        identity = {k: data[k] for k in fields if k in data}
        if any(not isinstance(v, str) or len(v) > 512 for v in identity.values()):
            raise ValueError('Bounded notification required')
        event = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        with self.ledger.write():
            row = self.ledger.db.execute('''SELECT a.*,d.booth_id FROM pp_payment_attempts a
                JOIN pp_checkout_intents i ON a.purchase_group_id=i.purchase_group_id
                JOIN pp_drafts d ON i.draft_id=d.draft_id WHERE a.provider_order_id=?''', (order,)).fetchone()
            if row is None:
                return {'accepted': True, 'known_order': False}
            _, finance = self.payments._group(row['purchase_group_id'], row['booth_id'])
            if idr_amount(data['gross_amount']) != finance['amount']:
                raise ValueError('Notification amount mismatch')
            if self.ledger.db.execute('SELECT 1 FROM pp_notification_inbox WHERE event_id=?', (event,)).fetchone():
                return {'accepted': True, 'known_order': True}
            if self.ledger.db.execute('SELECT count(*) FROM pp_notification_inbox').fetchone()[0] >= self.capacity:
                raise RuntimeError('Inbox capacity requires review')
            now = self.ledger.now()
            self.ledger.db.execute('''INSERT INTO pp_notification_inbox
                (event_id,purchase_group_id,attempt_id,booth_id,state,next_at,created_at,updated_at)
                VALUES(?,?,?,?,'NEW',?,?,?)''',
                (event, row['purchase_group_id'], row['attempt_id'], row['booth_id'], now, now, now))
        return {'accepted': True, 'known_order': True}

    def claim(self):
        with self.ledger.write():
            now = self.ledger.now()
            row = self.ledger.db.execute('''SELECT * FROM pp_notification_inbox WHERE
                (state IN ('NEW','RETRY') AND next_at<=?) OR (state='PROCESSING' AND lease_until<=?)
                ORDER BY created_at,event_id LIMIT 1''', (now, now)).fetchone()
            if not row:
                return None
            if row['attempts'] >= 5:
                self.ledger.db.execute("UPDATE pp_notification_inbox SET state='QUARANTINED',token=NULL,lease_until=0,updated_at=? WHERE event_id=?", (now, row['event_id']))
                return None
            token = uuid.uuid4().hex
            self.ledger.db.execute("UPDATE pp_notification_inbox SET state='PROCESSING',attempts=attempts+1,token=?,lease_until=?,updated_at=? WHERE event_id=?", (token, now+45, now, row['event_id']))
            return dict(row, token=token, attempts=row['attempts']+1)

    def finish(self, job, success):
        with self.ledger.write():
            now = self.ledger.now()
            state = 'APPLIED' if success else 'QUARANTINED' if job['attempts'] >= 5 else 'RETRY'
            changed = self.ledger.db.execute('''UPDATE pp_notification_inbox SET state=?,next_at=?,
                token=NULL,lease_until=0,updated_at=? WHERE event_id=? AND token=?
                AND state='PROCESSING' AND lease_until>?''',
                (state, now+min(60, 10*2**min(3, job['attempts']-1)), now, job['event_id'], job['token'], now))
            return changed.rowcount == 1

    def process_one(self):
        job = self.claim()
        if not job:
            return False
        try:
            view = self.payments.reconcile(job['purchase_group_id'], job['booth_id'], attempt_id=job['attempt_id'], force=True)
            success = view['fresh_checked'] and view['provider_state'] is not None
        except Exception:
            success = False
        self.finish(job, success)
        return True
