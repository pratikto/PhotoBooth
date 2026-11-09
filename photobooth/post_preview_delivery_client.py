"""Bounded paid-delivery observations; no provider key or local media paths."""
import re
import threading

from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_store import DraftHeld,DraftLease,ORDER_VERSION


class PostPreviewDeliveryClient:
    def __init__(self,payments):
        if type(payments) is not PostPreviewClient or payments.mode!='sandbox':
            raise ValueError('Exact original authenticated Sandbox client required')
        self._payments=payments
        self._hidden=threading.Event()

    def _call(self,group,lease,action):
        if (self._hidden.is_set() or type(lease) is not DraftLease
                or lease.booth_id!=self._payments.booth_id
                or type(group) is not str or re.fullmatch(r'[a-f0-9]{32}',group) is None):
            raise DraftHeld('Original private delivery scope required')
        try:
            response=self._payments._transport._call('POST',
                '/api/postpay/groups/'+group+'/delivery/'+action,
                payload=self._payments._owner(lease))
        except Exception:
            raise DraftHeld('Original paid delivery request held') from None
        base=dict(kind='PAID_DELIVERY',purchase_group_id=group,booth_id=lease.booth_id,
                  generation=lease.generation,action=action,mode='sandbox',order_version=ORDER_VERSION)
        if (type(response) is not dict or set(response)!=set(base)|{'delivery'}
                or any(type(response[k]) is not type(v) or response[k]!=v for k,v in base.items())):
            raise DraftHeld('Original delivery response scope changed')
        view=response['delivery']
        required={'transaction_id','folder_url','upload_status','upload_total','upload_verified',
            'drive_verified','print_states','print_all_submitted','physical_paper_verified',
            'service_status','safe_to_release_without_original_claim','needs_operator_review'}
        if (type(view) is not dict or not required<=set(view) or set(view)-required-{'worker'}
                or type(view['transaction_id']) is not str
                or re.fullmatch(re.escape(lease.booth_id)+r'V2S2_[0-9]{8,16}',view['transaction_id']) is None
                or type(view['folder_url']) is not str
                or re.fullmatch(r'https://drive\.google\.com/drive/folders/[A-Za-z0-9_-]+',view['folder_url']) is None
                or type(view['upload_status']) is not str or view['upload_status'] not in {
                    'PENDING_UPLOAD','UPLOAD_COMPLETE','UPLOADING','UPLOAD_RETRY','ACTION_REQUIRED',
                    'LOCAL_EXPIRED','PENDING_DRIVE_BINDING','LOCAL_ONLY'}
                or type(view['upload_total']) is not int or not 1<=view['upload_total']<=100
                or type(view['upload_verified']) is not int or not 0<=view['upload_verified']<=view['upload_total']
                or view['physical_paper_verified'] is not False
                or view['safe_to_release_without_original_claim'] is not False
                or view['service_status']!='OWED'
                or any(type(view[k]) is not bool for k in ('drive_verified','print_all_submitted','needs_operator_review'))
                or type(view['print_states']) is not dict or not 1<=len(view['print_states'])<=12
                or any(type(k) is not str or re.fullmatch(r'[A-Za-z0-9_-]{1,64}',k) is None
                       or type(v) is not str or v not in {'PREPARED','SENDING','SUBMITTED','NOT_SENT','UNCERTAIN'}
                       for k,v in view['print_states'].items())
                or 'worker' in view and (type(view['worker']) is not str
                                        or view['worker'] not in {'QUEUED','NOT_CONFIGURED'})):
            raise DraftHeld('Original paid delivery observation changed')
        if (view['print_all_submitted']!=all(v=='SUBMITTED' for v in view['print_states'].values())
                or view['drive_verified'] and (view['upload_verified']!=view['upload_total']
                                             or view['upload_status']!='UPLOAD_COMPLETE')
                or any(v in {'SENDING','UNCERTAIN'} for v in view['print_states'].values())
                    and not view['needs_operator_review'] or self._hidden.is_set()):
            raise DraftHeld('Original paid delivery outcome is inconsistent or retired')
        return dict(view,print_states=dict(view['print_states']))

    def prepare(self,group,lease):return self._call(group,lease,'prepare')
    def inspect(self,group,lease):return self._call(group,lease,'status')
    def print_next(self,group,lease):return self._call(group,lease,'print-next')
    def hide_private(self):self._hidden.set()
