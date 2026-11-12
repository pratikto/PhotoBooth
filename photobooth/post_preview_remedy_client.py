"""Typed redacted CASE status only; no refund/media/worker capability."""
import re

from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_remedy_contract import STATUSES
from photobooth.post_preview_refund_assessment import REFUND_REASONS
from photobooth.post_preview_store import DraftHeld,ORDER_VERSION


def _id(value):return type(value) is str and re.fullmatch(r'[a-f0-9]{32}',value) is not None


class PostPreviewRemedyClient:
    def __init__(self,payments):
        if type(payments) is not PostPreviewClient or payments.mode!='sandbox':
            raise DraftHeld('Exact original Sandbox review client required')
        self._payments=payments

    def review(self,request,group,proof,reported_reason):
        if (not _id(request) or not _id(group) or type(proof) is not str or not 1<=len(proof)<=256
                or type(reported_reason) is not str or reported_reason not in REFUND_REASONS):
            raise DraftHeld('Exact original remedy request required')
        try:
            value=self._payments._transport._call('POST','/api/postpay/groups/'+group+'/remedy',
                payload=dict(request_id=request,proof=proof,reported_reason=reported_reason))
        except Exception:raise DraftHeld('Original remedy review request held') from None
        expected=dict(kind='ORIGINAL_REMEDY_CASE',request_id=request,purchase_group_id=group,
            booth_id=self._payments.booth_id,reported_reason=reported_reason,mode='sandbox',order_version=ORDER_VERSION,
            refund_state='NOT_REQUESTED',refund_capability='NOT_VERIFIED',can_issue_refund=False,fulfillment_authorized=False)
        if (type(value) is not dict or set(value)!=set(expected)|{'case_id','status','financial_evidence_fresh'}
                or any(type(value[k]) is not type(v) or value[k]!=v for k,v in expected.items())
                or not _id(value['case_id']) or type(value['status']) is not str or value['status'] not in STATUSES
                or type(value['financial_evidence_fresh']) is not bool):
            raise DraftHeld('Original remedy response scope changed')
        return value
