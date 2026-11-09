"""Protected original handoff RPC: no caller worker/payment/grant authority."""
import unittest
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from photobooth.booth_auth import BoothAuthenticator
from photobooth.post_preview_api import create_app
from photobooth.post_preview_presentation import OriginalCCPPresentation
from tests.post_preview_handoff_fixture import ProtectedHandoffHarness


class ProtectedHandoffApiTests(unittest.TestCase):
    def setUp(self):
        self.h=ProtectedHandoffHarness(self)
        self.f=self.h.f
        self.args=dict(background_worker=False,
            ccp_presentation=OriginalCCPPresentation(self.h.claim.ccp),
            ticket_presentation=self.f.actor.binder.presentation,paid_delivery=self.f.actor)
        self.auth=BoothAuthenticator({'PB001':'x'*48})
        self.app=create_app(self.h.payments,self.auth,**self.args,
            protected_isolation=self.h.isolation,protected_claim=self.h.claim)
        self.http=TestClient(self.app);self.addCleanup(self.http.close)
        self.headers={'X-Booth-ID':'PB001','Authorization':'Bearer '+'x'*48}
        self.owner=dict(visit_id=self.f.lease.visit_id,generation=self.f.lease.generation+1)
        self.prepare='/api/postpay/drafts/'+self.f.lease.draft_id+'/isolation/prepare'
        self.claim='/api/postpay/groups/'+self.f.group+'/claim'
        self.command=dict(request_id=uuid.uuid4().hex,proof=self.h.proof)

    def post(self,path,body=None):
        self.f.clock[0]+=2
        return self.http.post(path,json=self.owner if body is None else body,headers=self.headers)

    def release(self):
        response=self.post(self.prepare)
        self.assertEqual(200,response.status_code,response.text)
        operation=response.json()['operation_id']
        self.h.native.publish(operation,timeout=1)
        ack='/api/postpay/isolation/'+operation+'/ack'
        response=self.post(ack);self.assertEqual(200,response.status_code,response.text)
        return ack,response.json()

    def test_original_prepare_receipt_ack_claim_and_lost_responses_are_idempotent(self):
        response=self.post(self.prepare);self.assertEqual(200,response.status_code,response.text)
        original=response.json();self.assertEqual('PREPARED',original['state'])
        self.assertEqual(original,self.post(self.prepare).json())
        ack='/api/postpay/isolation/'+original['operation_id']+'/ack'
        self.assertEqual(409,self.post(ack).status_code)
        self.assertEqual(0,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        self.h.native.publish(original['operation_id'],timeout=1)
        accepted=self.post(ack);self.assertEqual(200,accepted.status_code,accepted.text)
        self.assertEqual('ACKED',accepted.json()['state'])
        self.assertEqual(accepted.json(),self.post(ack).json())
        first=self.post(self.claim,self.command);self.assertEqual(200,first.status_code,first.text)
        self.assertEqual('REACQUIRED',first.json()['state'])
        self.assertEqual(4,first.json()['lease']['generation'])
        self.assertEqual(first.json(),self.post(self.claim,self.command).json())
        self.assertEqual(accepted.json(),self.post(ack).json())
        self.assertEqual(1,self.f.remote.charges);self.assertEqual(1,len(self.f.sends))
        self.assertEqual('no-store',first.headers['cache-control'])
        self.assertEqual('no-referrer',first.headers['referrer-policy'])
        for private in (self.h.proof,self.h.ticket_proof,str(self.f.root),self.h.key.secret.hex()):
            self.assertNotIn(private,first.text+accepted.text)

    def test_busy_claim_wait_does_not_read_provider_or_reveal_lease(self):
        reads=self.f.remote.reads
        response=self.post(self.claim,self.command)
        self.assertEqual(200,response.status_code,response.text)
        self.assertEqual('WAIT',response.json()['state']);self.assertNotIn('lease',response.json())
        self.assertEqual(reads,self.f.remote.reads)
        self.release()
        self.assertEqual('REACQUIRED',self.post(self.claim,self.command).json()['state'])

    def test_auth_wrong_proof_and_strict_body_cannot_create_release_or_grant(self):
        reads=self.f.remote.reads
        self.assertEqual(401,self.http.post(self.prepare,json=self.owner).status_code)
        self.assertEqual(401,self.http.post(self.claim,json=self.command).status_code)
        for extra in ('worker_ready','worker_fence_key','paid_verified','lease','amount'):
            for path,body in ((self.prepare,self.owner),(self.claim,self.command)):
                response=self.post(path,dict(body,**{extra:'private-marker'}))
                self.assertEqual(422,response.status_code,response.text)
                self.assertNotIn('private-marker',response.text)
                self.assertNotIn(self.h.proof,response.text)
        self.assertEqual(403,self.post(self.claim,dict(self.command,proof='MEONG:QRIS:1:fake')).status_code)
        self.assertEqual(reads,self.f.remote.reads)
        self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_isolation_ops').fetchone()[0])
        self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])

    def test_wrong_retired_owner_rejected_before_provider_get(self):
        reads=self.f.remote.reads
        for body in (dict(self.owner,generation=1),dict(self.owner,visit_id='other')):
            self.assertEqual(409,self.post(self.prepare,body).status_code)
        self.assertEqual(409,self.post(self.prepare.replace(self.f.lease.draft_id,'other')).status_code)
        self.assertEqual(reads,self.f.remote.reads)
        ack,_=self.release()
        self.assertEqual(409,self.post(ack,dict(self.owner,generation=3)).status_code)

    def test_provider_failure_is_redacted_and_same_request_can_recover(self):
        self.release();self.f.remote.outage=True
        failed=self.post(self.claim,self.command)
        self.assertEqual(409,failed.status_code,failed.text)
        self.assertNotIn(self.h.proof,failed.text)
        self.assertEqual('PREPARED',self.f.ledger.db.execute('SELECT state FROM pp_protected_claim_ops').fetchone()[0])
        self.f.remote.outage=False
        self.assertEqual('REACQUIRED',self.post(self.claim,self.command).json()['state'])

    def test_duplicate_and_oversize_bodies_never_echo_private_proof(self):
        for raw in ('{"request_id":"'+self.command['request_id']+'","proof":"a","proof":"'+self.h.proof+'"}',
                    '{"proof":"'+'x'*17000+'"}'):
            response=self.http.post(self.claim,content=raw,headers=dict(self.headers,**{'Content-Type':'application/json'}))
            self.assertIn(response.status_code,(400,413,422))
            self.assertNotIn(self.h.proof,response.text)
        self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])

    def test_handoff_routes_absent_without_exact_trusted_pair(self):
        default=TestClient(create_app(self.h.payments,self.auth,**self.args));self.addCleanup(default.close)
        self.assertEqual(404,default.post(self.prepare,json=self.owner,headers=self.headers).status_code)
        self.assertEqual(404,default.post(self.claim,json=self.command,headers=self.headers).status_code)
        self.assertFalse(self.http.get('/api/postpay/health').json()['fulfillment_enabled'])
        for pair in (dict(protected_isolation=self.h.isolation),dict(protected_claim=self.h.claim),
                     dict(protected_isolation=object(),protected_claim=self.h.claim)):
            with self.assertRaises(ValueError):create_app(self.h.payments,self.auth,**self.args,**pair)

    def test_factory_mount_requires_private_typed_key_and_original_paid_dependencies(self):
        from tests.test_post_preview_sandbox_delivery import SandboxPaidDeliveryTests
        from photobooth.post_preview_server import build_sandbox_app
        from photobooth.post_preview_worker_fence import WorkerFenceKey
        fixture=SandboxPaidDeliveryTests(methodName='runTest');fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        def build(**extra):
            return build_sandbox_app(fixture.h.checkout,fixture.h.templates,
                fixture.h.bridge,fixture.probe,**fixture.h.factory_args,
                receipt_printer=fixture.printer,printer_lane=fixture.lane,**extra)
        key=WorkerFenceKey.create()
        with patch('photobooth.post_preview_server.platform_protector',return_value=fixture.h.protector):
            for args in (dict(worker_fence_key=key),
                         dict(worker_fence_key=True,paid_delivery_enabled=True)):
                with self.assertRaises(ValueError):build(**args)
            app=build(worker_fence_key=key,paid_delivery_enabled=True)
        self.addCleanup(app.state.paid_delivery.stop)
        paths={route.path for route in app.routes}
        self.assertIn('/api/postpay/groups/{group}/claim',paths)
        self.assertIn('/api/postpay/isolation/{operation}/ack',paths)
        self.assertEqual([],fixture.bind_requests);self.assertEqual(0,fixture.sends)


if __name__=='__main__':unittest.main()
