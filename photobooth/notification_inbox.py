"""AR-11 unmounted Legacy Sandbox inbox prototype; no listener or worker startup."""
import hashlib,json,uuid
from photobooth.qris_evidence import authenticated_notification,idr_amount

FIELDS=frozenset({'order_id','status_code','gross_amount','signature_key','transaction_id',
    'transaction_status','merchant_id','currency','payment_type','fraud_status'})

class LegacyNotificationInbox:
    def __init__(self,backend,*,adapter='legacy-qris-sandbox',capacity=10000):
        if adapter!='legacy-qris-sandbox' or backend.provider_mode!='sandbox':
            raise ValueError('Explicit Legacy Sandbox adapter required')
        if type(capacity) is not int or not 1<=capacity<=10000:raise ValueError('Bounded inbox required')
        self.backend,self.store,self.capacity=backend,backend.store,capacity
        with self.store.write():
            self.store.db.execute('''CREATE TABLE IF NOT EXISTS checkout_notification_inbox (
                event_id TEXT PRIMARY KEY,payload TEXT NOT NULL,state TEXT NOT NULL,
                attempts INTEGER NOT NULL,next_at REAL NOT NULL,token TEXT,lease_until REAL NOT NULL,
                created_at REAL NOT NULL,updated_at REAL NOT NULL)''')

    def accept(self,notification):
        oid=authenticated_notification(notification,self.backend.server_key)
        order=self.store.get(oid)
        if idr_amount(notification['gross_amount'])!=order['amount']:
            raise ValueError('Notification amount mismatch')
        payload={k:v for k,v in notification.items() if k in FIELDS}
        if any(not isinstance(v,str) or len(v)>512 for v in payload.values()):
            raise ValueError('Bounded scalar notification fields required')
        raw=json.dumps(payload,sort_keys=True,separators=(',',':'))
        event=hashlib.sha256(raw.encode()).hexdigest()
        with self.store.write():
            if self.store.db.execute('SELECT 1 FROM checkout_notification_inbox WHERE event_id=?',(event,)).fetchone():
                return event
            if self.store.db.execute('SELECT count(*) FROM checkout_notification_inbox').fetchone()[0]>=self.capacity:
                raise RuntimeError('Inbox capacity requires review')
            now=self.store.now()
            self.store.db.execute("INSERT INTO checkout_notification_inbox VALUES (?,?,'NEW',0,?,NULL,0,?,?)",
                                  (event,raw,now,now,now))
        return event

    def claim(self):
        with self.store.write():
            now=self.store.now()
            row=self.store.db.execute('''SELECT * FROM checkout_notification_inbox WHERE
                (state IN ('NEW','RETRY') AND next_at<=?) OR (state='PROCESSING' AND lease_until<=?)
                ORDER BY created_at,event_id LIMIT 1''',(now,now)).fetchone()
            if not row:return None
            if row['attempts']>=5:
                self.store.db.execute("UPDATE checkout_notification_inbox SET state='QUARANTINED',token=NULL,lease_until=0,updated_at=? WHERE event_id=?",
                                      (now,row['event_id']))
                return None
            token=uuid.uuid4().hex
            self.store.db.execute("UPDATE checkout_notification_inbox SET state='PROCESSING',attempts=attempts+1,token=?,lease_until=?,updated_at=? WHERE event_id=?",
                                  (token,now+45,now,row['event_id']))
            return dict(row,event_id=row['event_id'],token=token,attempts=row['attempts']+1)

    def finish(self,job,success):
        with self.store.write():
            now=self.store.now()
            state='APPLIED' if success else 'QUARANTINED' if job['attempts']>=5 else 'RETRY'
            changed=self.store.db.execute('''UPDATE checkout_notification_inbox SET state=?,
                next_at=?,token=NULL,lease_until=0,updated_at=?
                WHERE event_id=? AND token=? AND state='PROCESSING' AND lease_until>?''',
                (state,now+min(60,10*2**min(3,job['attempts']-1)),now,job['event_id'],job['token'],now))
            return changed.rowcount==1

    def process_one(self):
        job=self.claim()
        if not job:return False
        try:success=self.backend.process_notification(json.loads(job['payload'])) is True
        except Exception:success=False
        self.finish(job,success)
        return True
