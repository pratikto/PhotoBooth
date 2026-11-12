"""Actual original Sandbox child case review; all provider effects are fake."""
import json
import sqlite3
import time
import unittest
import uuid
from unittest.mock import patch

from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_remedy_client import PostPreviewRemedyClient
from photobooth.post_preview_store import DraftHeld,ORDER_VERSION
from tests import test_post_preview_sandbox_visits as fixtures


class OriginalRemedyProcessTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.OriginalSandboxVisitTests(methodName='runTest');self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.manager=self.f.visits;self.service=self.f.binding.service
        self.group,self.proof=self.f.frozen(self.f.binding)
        (self.f.config.private_root/'fixture-keep-pending').touch()
        self.service.begin_payment()
        self.client=PostPreviewRemedyClient(self.manager._client)
        self.request=uuid.uuid4().hex

    def paid(self):
        marker=self.f.config.private_root/'fixture-keep-pending'
        if marker.exists():marker.unlink()
        def checked():
            value=self.service.check_payment('connectivity')
            if value['phase']!='paid_hold':raise DraftHeld('Original fixture status pacing')
            return value
        return self.f.retry(checked)

    def review(self,reason='TEMPORARY_SERVICE_OUTAGE',expected=None,request=None):
        def checked():
            value=self.client.review(request or self.request,self.group,self.proof,reason)
            if expected is not None and value['status']!=expected:raise DraftHeld('Original fixture status pacing')
            return value
        return self.f.retry(checked) if expected is not None else checked()

    def rows(self,table):
        return [tuple(row) for row in self.manager.ledger.db.execute('SELECT * FROM '+table)]

    def test_paid_case_has_truthful_nonbinding_status_and_no_private_record_contents(self):
        self.paid();lease=self.service.lease
        before=self.rows('pp_worker_retirements')
        value=self.review(expected='PAID_OWED_DELIVERY')
        self.assertFalse(value['can_issue_refund']);self.assertFalse(value['fulfillment_authorized'])
        self.assertEqual('NOT_REQUESTED',value['refund_state']);self.assertEqual('NOT_VERIFIED',value['refund_capability'])
        self.assertEqual(lease,self.service.lease);self.assertEqual(before,self.rows('pp_worker_retirements'))
        raw=str(self.rows('pp_remedy_cases')+self.rows('pp_remedy_requests')+self.rows('pp_remedy_observations'))
        self.assertNotIn(self.proof,raw);self.assertNotIn('https://',raw)
        self.assertNotIn(self.f.config.server_key,raw)
        self.assertFalse((self.f.config.private_root/'fixture-output-send-count').exists())

    def test_case_retries_and_new_request_keep_one_original_case_and_no_financial_replay(self):
        self.paid();first=self.review();second=self.review(request=uuid.uuid4().hex)
        self.assertEqual(first['case_id'],second['case_id'])
        self.assertEqual(1,len(self.rows('pp_remedy_cases')));self.assertEqual(2,len(self.rows('pp_remedy_requests')))
        self.assertEqual(1,len(self.rows('pp_payment_attempts')))
        with self.assertRaises(PermissionError):self.manager.recover_paid(first['case_id'])
        self.assertEqual(1,self.service.lease.generation)

    def test_lost_case_reply_reuses_request_identity_and_original_case(self):
        self.paid();transport=self.manager._client._transport;original=transport._call;calls=[]
        def lose(method,path,**kwargs):
            value=original(method,path,**kwargs)
            if path.endswith('/remedy'):
                calls.append(True)
                if len(calls)==1:raise OSError('Synthetic accepted support reply loss')
            return value
        with patch.object(transport,'_call',side_effect=lose):
            with self.assertRaises(DraftHeld):self.review()
            self.review()
        self.assertEqual(2,len(calls));self.assertEqual(1,len(self.rows('pp_remedy_cases')))
        self.assertEqual(1,len(self.rows('pp_remedy_requests')))

    def test_forged_proof_does_not_create_a_case_or_reacquire_old_photos(self):
        self.paid();changed=self.proof[:-1]+('a' if self.proof[-1]!='a' else 'b')
        with self.assertRaises(DraftHeld):self.client.review(self.request,self.group,changed,'TEMPORARY_SERVICE_OUTAGE')
        self.assertEqual([],self.rows('pp_remedy_cases'));self.assertEqual([],self.rows('pp_remedy_requests'))
        self.assertEqual(1,self.service.lease.generation)

    def test_http_accepts_no_merchant_flags_worker_claims_destinations_or_notes(self):
        transport=self.manager._client._transport
        payload=dict(request_id=self.request,proof=self.proof,reported_reason='IRRECOVERABLE_MERCHANT_SERVICE')
        for extra in ({'merchant_refund_feature_verified':True},{'all_external_workers_fenced':True},
                      {'service_irrecoverable':True},{'wallet':'fixture-destination'},{'notes':'private text'}):
            response=transport.session.post(transport.base_url+'/api/postpay/groups/'+self.group+'/remedy',
                json=dict(payload,**extra),headers=transport.headers,timeout=4)
            try:
                self.assertEqual(422,response.status_code);self.assertNotIn(self.proof,response.text)
                self.assertNotIn('private text',response.text)
            finally:response.close()
        self.assertEqual([],self.rows('pp_remedy_cases'))

    def test_same_request_cannot_switch_original_reason_or_scope(self):
        self.paid();self.review();before=self.rows('pp_remedy_requests')
        with self.assertRaises(DraftHeld):self.review(reason='EXCESS_SETTLED_ATTEMPTS')
        self.assertEqual(before,self.rows('pp_remedy_requests'));self.assertEqual(1,len(self.rows('pp_remedy_cases')))

    def test_provider_outage_keeps_paid_owed_and_waits_without_refund_claim(self):
        paid=self.paid();marker=self.f.config.private_root/'fixture-provider-outage';marker.touch()
        value=self.review(expected='WAITING_PROVIDER')
        self.assertFalse(value['financial_evidence_fresh']);self.assertEqual('NOT_REQUESTED',value['refund_state'])
        finance=self.manager.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0]
        self.assertEqual(paid['payment']['entitlement_id'],finance)
        marker.unlink();recovered=self.review(expected='PAID_OWED_DELIVERY')
        self.assertEqual(value['case_id'],recovered['case_id'])

    def test_amount_mismatch_get_never_becomes_refund_eligibility(self):
        self.paid();(self.f.config.private_root/'fixture-provider-wrong-amount').touch()
        value=self.review(expected='REFUND_REVIEW_REQUIRED')
        self.assertFalse(value['can_issue_refund']);self.assertFalse(value['financial_evidence_fresh'])
        self.assertEqual(1,self.manager.ledger.db.execute('SELECT review_required FROM pp_purchase_finance').fetchone()[0])

    def test_lost_proof_report_cannot_blame_missing_paid_ticket_opportunity(self):
        self.paid();value=self.review('PROOF_LOST_ONLY',expected='PAID_OWED_REMEDY')
        self.assertEqual('NOT_REQUESTED',value['refund_state'])
        self.assertEqual(0,self.manager.ledger.db.execute('SELECT COUNT(*) FROM pp_ticket_presentations').fetchone()[0])
        self.assertIsNotNone(self.manager.ledger.db.execute('SELECT entitlement_id FROM pp_purchase_finance').fetchone()[0])

    def test_offered_ticket_and_submitted_receipt_do_not_certify_purchased_photo_delivery(self):
        self.paid();ticket=self.service.prepare_ticket();self.service.ticket_visible(ticket['ticket_offer'])
        self.service.ticket_send_receipt();self.service.ticket_dismiss();count=self.f.output_count()
        value=self.review('PROOF_LOST_ONLY',expected='PAID_OWED_REMEDY')
        self.assertFalse(value['can_issue_refund']);self.assertEqual(count,self.f.output_count())
        self.assertEqual(1,self.manager.ledger.db.execute('SELECT COUNT(*) FROM pp_ticket_credentials').fetchone()[0])

    def test_uncertain_actual_fake_paper_requires_inspection_without_reprint_or_refund(self):
        self.paid();(self.f.config.private_root/'fixture-output-uncertain-after-send').touch()
        ticket=self.service.prepare_ticket();self.service.ticket_visible(ticket['ticket_offer']);self.service.ticket_send_receipt()
        count=self.f.output_count();value=self.review(expected='PRINT_INSPECTION_REQUIRED')
        self.assertFalse(value['can_issue_refund']);self.assertEqual(count,self.f.output_count())
        self.assertEqual('UNCERTAIN',self.manager.ledger.db.execute('SELECT receipt_state FROM pp_ticket_presentations').fetchone()[0])

    def test_reported_permanent_failure_is_not_trusted_irrecoverability_or_merchant_activation(self):
        self.paid();value=self.review('IRRECOVERABLE_MERCHANT_SERVICE',expected='REFUND_REVIEW_REQUIRED')
        self.assertFalse(value['can_issue_refund']);self.assertEqual('NOT_VERIFIED',value['refund_capability'])
        self.assertEqual(0,self.manager.ledger.db.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='pp_mock_refund_intents'").fetchone()[0])

    def test_fresh_independent_double_settlement_preserves_single_entitlement_and_both_charges(self):
        pending=self.service.snapshot()['payment'];first=pending['attempts'][0]['provider_order_id']
        statuses=self.f.config.private_root/'fixture-provider-statuses.json'
        statuses.write_text(json.dumps({first:'expire'}))
        def expired():
            value=self.service.check_payment('connectivity')
            if value['payment']['state']!='EXPIRED_UNPAID':raise DraftHeld('Original fixture status pacing')
            return value
        self.f.retry(expired)
        def renew():
            try:return self.service.continue_payment(True)
            except RuntimeError:raise DraftHeld('Original fixture expiry recheck pacing') from None
        renewed=self.f.retry(renew)
        second=renewed['payment']['attempts'][-1]['provider_order_id']
        statuses.write_text(json.dumps({first:'settlement',second:'settlement'}))
        value=self.review('EXCESS_SETTLED_ATTEMPTS',expected='REFUND_REVIEW_REQUIRED')
        def both():
            result=self.review('EXCESS_SETTLED_ATTEMPTS')
            if not result['financial_evidence_fresh']:raise DraftHeld('Original fixture status pacing')
            return result
        value=self.f.retry(both)
        self.assertFalse(value['can_issue_refund']);self.assertEqual('NOT_REQUESTED',value['refund_state'])
        self.assertEqual(2,self.manager.ledger.db.execute("SELECT COUNT(*) FROM pp_payment_attempts WHERE payment_state='PAID'").fetchone()[0])
        self.assertEqual(1,len(self.rows('pp_purchase_finance')));self.assertEqual(1,len(self.rows('pp_ccp_credentials')))

    def test_remedy_uses_only_original_provider_get_and_no_charge_cancel_or_refund(self):
        self.paid();root=self.f.config.private_root;(root/'fixture-trace-provider-methods').touch()
        self.review(expected='PAID_OWED_DELIVERY')
        methods=(root/'fixture-provider-methods').read_text().splitlines()
        self.assertTrue(methods);self.assertEqual({'GET'},set(methods))
        self.assertEqual(1,len(self.rows('pp_payment_attempts')))

    def test_case_request_and_observation_audit_cannot_update_delete_or_replace(self):
        self.paid();self.review()
        for table in ('pp_remedy_cases','pp_remedy_requests','pp_remedy_observations'):
            before=self.rows(table)
            for query in ('UPDATE '+table+' SET created_at=created_at','DELETE FROM '+table,
                          'INSERT OR REPLACE INTO '+table+' SELECT * FROM '+table):
                with self.manager.ledger.write(),self.assertRaises(sqlite3.IntegrityError):self.manager.ledger.db.execute(query)
            self.assertEqual(before,self.rows(table))


class RemedyClientProtocolTests(unittest.TestCase):
    def test_typed_status_rejects_refund_success_authority_extra_fields_or_wrong_scope(self):
        client=PostPreviewClient('https://fixture.invalid','PB001','b'*48);self.addCleanup(client.close)
        adapter=PostPreviewRemedyClient(client);request='a'*32;group='b'*32
        good=dict(kind='ORIGINAL_REMEDY_CASE',case_id='c'*32,request_id=request,purchase_group_id=group,
            booth_id='PB001',reported_reason='TEMPORARY_SERVICE_OUTAGE',mode='sandbox',order_version=ORDER_VERSION,
            status='PAID_OWED_DELIVERY',refund_state='NOT_REQUESTED',refund_capability='NOT_VERIFIED',
            financial_evidence_fresh=True,can_issue_refund=False,fulfillment_authorized=False)
        with patch.object(client._transport,'_call',return_value=good):self.assertEqual(good,adapter.review(
            request,group,'fixture-private-proof','TEMPORARY_SERVICE_OUTAGE'))
        for fields in ({'refund_state':'CONFIRMED'},{'status':'REFUND_CONFIRMED'},{'can_issue_refund':True},
                       {'financial_evidence_fresh':1},{'mode':'mock'},{'case_id':'../old'},
                       {'provider_ref':'must-not-appear'},{'fulfillment_authorized':True}):
            with patch.object(client._transport,'_call',return_value=dict(good,**fields)):
                with self.assertRaises(DraftHeld):adapter.review(request,group,'fixture-private-proof','TEMPORARY_SERVICE_OUTAGE')

    def test_untrusted_claim_like_object_cannot_mount_backend_review(self):
        from types import SimpleNamespace
        from photobooth.post_preview_remedy import OriginalSandboxRemedy
        with self.assertRaises(DraftHeld):OriginalSandboxRemedy(SimpleNamespace(payments=SimpleNamespace(mode='sandbox')))


if __name__=='__main__':unittest.main()
