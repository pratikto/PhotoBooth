"""Safe, explicit MOCK-only PAID original Drive binding (PP-05.c).

No public media upload or paid strip is produced here. The original immutable
service transaction is journaled BEFORE claiming a local reserve; crash recovery
uses the same workspace token and transaction ID, never a second paid folder.
The original BoothDriveClient independently verifies the exact remote folder.
"""
import json
import re
import threading
from datetime import datetime, timezone

from photobooth.booth_storage import BoothWorkspace
from photobooth.booth_sync import BoothDriveClient
from photobooth.post_preview_checkout import PrivateDraftCheckout
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_store import DraftHeld


class OriginalPaidDriveBinding:
    def __init__(self,payments,checkout,workspace,client,*,allow_incomplete_fixture=False):
        if (allow_incomplete_fixture is not True or
                not isinstance(payments,PostPreviewPayments) or payments.mode!='mock'
                or not isinstance(checkout,PrivateDraftCheckout) or
                checkout.ledger is not payments.ledger or
                not isinstance(workspace,BoothWorkspace) or
                not isinstance(client,BoothDriveClient) or
                client.booth_id!=workspace.booth_id):
            raise DraftHeld('Only exact original synthetic Drive binding is available')
        self.payments,self.checkout,self.workspace,self.client=payments,checkout,workspace,client
        self.ledger=payments.ledger
        self._lock=threading.RLock()

    def _record(self,lease,group):
        self.ledger._owned(lease)
        intent,finance=self.payments._group(group,lease.booth_id)
        service=self.ledger.db.execute(
            'SELECT * FROM pp_paid_services WHERE purchase_group_id=?',(group,)).fetchone()
        paid=(self.ledger.db.execute('SELECT * FROM pp_payment_attempts WHERE attempt_id=?',
              (finance['legitimate_paid_attempt'],)).fetchone() if finance and finance['legitimate_paid_attempt'] else None)
        if (not service or not finance or not paid
                or finance['entitlement_id'] is None or finance['review_required']
                or paid['payment_state']!='PAID' or not paid['provider_ref']
                or service['entitlement_id']!=finance['entitlement_id']
                or service['contract_sha256']!=intent['contract_sha256']
                or service['status']!='OWED'):
            raise DraftHeld('Original independently paid OWED service required')
        if (self.workspace.physical_id!=lease.booth_id
                or self.workspace.booth_id!=lease.booth_id+'V2S2'):
            raise DraftHeld('Exact booth storage namespace required')
        contract=json.loads(intent['contract_json'])
        if (not isinstance(contract.get('designs'),list)
                or not contract['designs']
                or len(contract['designs'])>12
                or any(type(design.get('copies')) is not int or design['copies']<1
                       for design in contract['designs'])):
            raise DraftHeld('Original approved design group required')
        return service,contract

    @staticmethod
    def _verified(bound,slot):
        fid=bound.get('folder_id')
        if (bound.get('link_verified') is not True
                or bound.get('photo_number_layout')!=1
                or bound.get('transaction_id')!=slot['transaction_id']
                or not isinstance(fid,str)
                or re.fullmatch(r'[A-Za-z0-9_-]+',fid) is None
                or bound.get('folder_url')!='https://drive.google.com/drive/folders/'+fid
                or slot.get('folder_id') not in (None,fid)):
            raise DraftHeld('Original individual Drive viewer URL is not verified')
        return fid,bound['folder_url']

    def bind(self,lease,group,templates):
        """Return a strictly verified URL or fail closed with the same OWED ID.

        The caller first has a fresh, verified PAID entitlement and must own
        the original private worker lease. A provider timeout never generates
        or claims a second transaction. This method performs *no* upload,
        photo printing, media publication, or customer screen rendering.
        """
        with self._lock:
            # Slow photo/artwork/file hashes outside SQL; recheck owner afterwards.
            self.checkout.verify_frozen(group,templates)
            with self.ledger.write():
                service,contract=self._record(lease,group)
                if service['drive_state'] in {'VERIFIED','UPLOADED'}:
                    if (not service['transaction_id'] or not service['folder_id']
                            or service['folder_url']!='https://drive.google.com/drive/folders/'+service['folder_id']):
                        raise DraftHeld('Original paid folder journal is inconsistent')
                    return {'transaction_id':service['transaction_id'],'folder_id':service['folder_id'],
                            'folder_url':service['folder_url'],'drive_state':'VERIFIED'}
                txid=service['transaction_id']
            if txid is None:
                candidates=self.workspace.ready_slots()
                if not candidates:
                    raise DraftHeld('Original READY Drive reserve is not available')
                selected=candidates[0]['transaction_id']
                with self.ledger.write():
                    service,_=self._record(lease,group)
                    txid=service['transaction_id']
                    if txid is None:
                        self.ledger.db.execute('''UPDATE pp_paid_services
                            SET transaction_id=?,drive_state='PREPARED'
                            WHERE purchase_group_id=? AND transaction_id IS NULL''',(selected,group))
                        self.ledger._event(lease.draft_id,'PAID_DRIVE_TRANSACTION_PREPARED')
                        txid=selected
            # This token only comes from the original per-booth local workspace.
            try:
                slot=self.workspace.original_slot(txid)
                claimed=self.workspace.claim_exact(txid,slot['claim_token'])
            except (ValueError,OSError) as error:
                raise DraftHeld('Original paid Drive reserve is unavailable') from error
            # The original selected transaction is not swapped even if the
            # provider is down, ACL changed, or an ACK was lost.
            try:
                bound=self.client.bind_transaction({
                    'transaction_id':txid,
                    'drive_claim_token':claimed['claim_token'],
                    'created_at':datetime.fromtimestamp(self._paid_anchor(group),timezone.utc).isoformat(),
                    'sessions':[None]*len(contract['designs']),
                })
                fid,url=self._verified(bound,claimed)
                self.workspace.remember_binding(txid,claimed['claim_token'],bound)
            except Exception:
                with self.ledger.write():
                    latest,_=self._record(lease,group)
                    if latest['transaction_id']==txid and latest['drive_state']!='VERIFIED':
                        self.ledger.db.execute("UPDATE pp_paid_services SET drive_state='UNKNOWN' WHERE purchase_group_id=?",(group,))
                raise DraftHeld('Original paid Drive binding must be verified') from None
            with self.ledger.write():
                latest,_=self._record(lease,group)
                if latest['transaction_id']!=txid:
                    raise DraftHeld('Original paid folder was changed during binding')
                if (latest['folder_id'] not in (None,fid) or
                        latest['folder_url'] not in (None,url)):
                    raise DraftHeld('Original paid folder already bound to a different identity')
                self.ledger.db.execute('''UPDATE pp_paid_services
                    SET folder_id=?,folder_url=?,drive_state='VERIFIED'
                    WHERE purchase_group_id=? AND transaction_id=?''',(fid,url,group,txid))
                self.ledger._event(lease.draft_id,'PAID_DRIVE_LINK_VERIFIED')
                return {'transaction_id':txid,'folder_id':fid,'folder_url':url,'drive_state':'VERIFIED'}

    def _paid_anchor(self,group):
        row=self.ledger.db.execute('SELECT retention_anchor FROM pp_paid_services WHERE purchase_group_id=?',(group,)).fetchone()
        if not row or row['retention_anchor'] is None:
            raise DraftHeld('Original PAID time anchor is unavailable')
        return row['retention_anchor']
