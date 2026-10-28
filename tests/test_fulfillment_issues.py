"""AR-08 durable paid fault audit; never a refund, grant or completion."""
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
import unittest
from photobooth.checkout_store import CheckoutStore,CheckoutConflict,CheckoutMissing
import tests.test_checkout_fulfillment as fixture

class FulfillmentIssueTests(unittest.TestCase):
    def setUp(self):fixture.FulfillmentTests.setUp(self)
    def paid(self):fixture.FulfillmentTests.paid(self)

    def test_paid_issue_survives_restart_and_does_not_change_financial_or_service_rights(self):
        self.paid();before=self.store.get(self.oid)
        result=self.backend.report_fulfillment_issue(self.oid,'PB001','a'*32,'PHOTO_STATE_UNAVAILABLE')
        issue=result['fulfillment_issue']
        self.assertEqual(issue['status'],'PAID_UNFULFILLED')
        self.assertEqual(self.store.get(self.oid),before)
        self.assertEqual(result['fulfillment']['obligation_state'],'OWED')
        with closing(CheckoutStore(self.path)) as reopened:
            self.assertEqual(reopened.fulfillment_issue(self.oid,'PB001'),issue)

    def test_concurrent_lost_ack_retry_creates_one_issue_and_one_operation(self):
        self.paid()
        with closing(CheckoutStore(self.path)) as second,ThreadPoolExecutor(max_workers=2) as pool:
            rows=list(pool.map(lambda s:s.report_fulfillment_issue(self.oid,'PB001','a'*32,'CAPTURE_FAILED'),[self.store,second]))
        self.assertEqual(rows[0],rows[1])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkout_fulfillment_issue_events').fetchone()[0],1)
        with self.assertRaises(CheckoutConflict):
            self.store.report_fulfillment_issue(self.oid,'PB001','a'*32,'PHOTO_STATE_UNAVAILABLE')

    def test_unpaid_wrong_booth_and_freeform_sensitive_reason_cannot_create_remedy(self):
        with self.assertRaises(CheckoutMissing):
            self.store.report_fulfillment_issue(self.oid,'PB001','a'*32,'CAPTURE_FAILED')
        self.paid()
        with self.assertRaises(CheckoutMissing):
            self.store.report_fulfillment_issue(self.oid,'PB002','a'*32,'CAPTURE_FAILED')
        with self.assertRaises(ValueError):
            self.store.report_fulfillment_issue(self.oid,'PB001','a'*32,'customer@example.invalid')

    def test_upgrade_adds_empty_issue_ledger_without_mutating_order_or_fulfillment(self):
        self.paid();before=self.store.get(self.oid);rights=self.store.fulfillment(self.oid,'PB001')
        self.store.db.execute('DROP TABLE checkout_fulfillment_issue_events')
        self.store.db.execute('DROP TABLE checkout_fulfillment_issues')
        with closing(CheckoutStore(self.path)) as reopened:
            self.assertEqual(reopened.get(self.oid),before)
            self.assertEqual(reopened.fulfillment(self.oid,'PB001'),rights)
            self.assertIsNone(reopened.fulfillment_issue(self.oid,'PB001'))

    def test_http_issue_requires_booth_auth_and_strict_reason_operation(self):
        from fastapi.testclient import TestClient
        from photobooth.qris_api import create_app
        from photobooth.booth_auth import BoothAuthenticator
        self.paid();http=TestClient(create_app(self.backend,BoothAuthenticator({'PB001':'x'*48})))
        self.addCleanup(http.close)
        url='/api/orders/'+self.oid+'/fulfillment-issue'
        body={'operation_id':'a'*32,'reason':'CAPTURE_FAILED'}
        self.assertEqual(http.post(url,json=body).status_code,401)
        headers={'x-booth-id':'PB001','authorization':'Bearer '+'x'*48}
        self.assertEqual(http.post(url,json=dict(body,reason='PII text'),headers=headers).status_code,422)
        first=http.post(url,json=body,headers=headers)
        self.assertEqual(first.status_code,200)
        again=http.post(url,json=body,headers=headers)
        self.assertEqual(first.json()['fulfillment_issue'],again.json()['fulfillment_issue'])
