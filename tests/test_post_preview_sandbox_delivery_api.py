"""Owner-scoped Sandbox delivery seam with fake provider/cloud/paper only."""
from dataclasses import replace
import threading
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from photobooth.booth_auth import BoothAuthenticator
from photobooth.post_preview_api import create_app
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_delivery_client import PostPreviewDeliveryClient
from photobooth.post_preview_sandbox_delivery import OriginalSandboxPaidDelivery
from photobooth.post_preview_store import DraftHeld


class SandboxDeliveryApiTests(unittest.TestCase):
    def setUp(self):
        from tests.test_post_preview_sandbox_delivery import SandboxPaidDeliveryTests
        self.f=SandboxPaidDeliveryTests(methodName='runTest');self.f.setUp()
        self.addCleanup(self.f.doCleanups);self.f.ticket()
        self.actor=OriginalSandboxPaidDelivery(self.f.binder,self.f.h.templates)
        self.addCleanup(self.actor.stop)
        self.queued=[]
        # Preserve the exact original worker identity; isolate external upload
        # scheduling here. An actual live-thread stop fence is tested below.
        self.actor.worker.start=lambda:None
        self.actor.worker.notify_transaction=self.queued.append
        self.app=create_app(self.f.payments,BoothAuthenticator({'PB001':self.f.h.token}),
            background_worker=False,ticket_presentation=self.f.presentation,paid_delivery=self.actor)
        self.http=TestClient(self.app);self.addCleanup(self.http.close)
        self.path='/api/postpay/groups/'+self.f.group+'/delivery/'
        self.owner=dict(visit_id=self.f.lease.visit_id,generation=self.f.lease.generation)

    def call(self,action,**extra):
        return self.http.post(self.path+action,json=dict(self.owner,**extra),headers=self.f.h.headers)

    def test_authenticated_prepare_status_print_retry_keep_original_output(self):
        prepared=self.call('prepare');self.assertEqual(200,prepared.status_code,prepared.text)
        self.assertEqual('no-store',prepared.headers['cache-control'])
        self.assertEqual('QUEUED',prepared.json()['delivery']['worker'])
        first=self.call('print-next');self.assertEqual(200,first.status_code,first.text)
        self.assertTrue(first.json()['delivery']['print_all_submitted'])
        self.assertEqual(2,self.f.sends)
        for _ in range(3):self.assertEqual(200,self.call('print-next').status_code)
        self.assertEqual(2,self.f.sends);self.assertEqual(1,self.f.h.remote.charges)
        status=self.call('status').json();self.assertFalse(status['delivery']['physical_paper_verified'])
        self.assertEqual('OWED',status['delivery']['service_status'])
        self.assertNotIn(str(self.f.h.fixture.root),str(status))

    def test_auth_owner_and_strict_body_precede_drive_or_paper_effect(self):
        self.assertEqual(401,self.http.post(self.path+'prepare',json=self.owner).status_code)
        for extra,code in (({'generation':2},409),({'visit_id':'visitor-B'},409),
                           ({'copies':9},422),({'amount':1},422),({'printer':'PRIVATE-PATH'},422)):
            response=self.call('prepare',**extra);self.assertEqual(code,response.status_code)
            self.assertNotIn('PRIVATE-PATH',response.text)
        self.assertEqual([],self.queued);self.assertEqual([],self.f.bind_requests)
        self.assertEqual(1,self.f.sends)

    def test_routes_absent_by_default_and_mock_actor_cannot_be_injected(self):
        self.assertEqual(404,self.f.h.http.post(self.path+'prepare',json=self.owner,headers=self.f.h.headers).status_code)
        with self.assertRaises(ValueError):
            create_app(self.f.payments,BoothAuthenticator({'PB001':self.f.h.token}),
                paid_delivery=object(),background_worker=False)
        self.assertFalse(self.http.get('/api/postpay/health').json()['fulfillment_enabled'])

    def test_trusted_factory_explicitly_assembles_only_exact_backend_chain(self):
        from photobooth.post_preview_server import build_sandbox_app
        with patch('photobooth.post_preview_server.platform_protector',return_value=self.f.h.protector):
            app=build_sandbox_app(self.f.h.checkout,self.f.h.templates,self.f.h.bridge,self.f.probe,
                **self.f.h.factory_args,receipt_printer=self.f.printer,printer_lane=self.f.lane,
                paid_delivery_enabled=True)
        self.addCleanup(app.state.paid_delivery.stop)
        self.assertIsInstance(app.state.paid_delivery,OriginalSandboxPaidDelivery)
        self.assertEqual([],self.f.bind_requests)
        self.assertIs(app.state.paid_delivery.binder.presentation._printer,self.f.printer)

    def test_original_partial_print_remains_uncertain_and_repeated_api_never_resends(self):
        self.assertEqual(200,self.call('prepare').status_code);self.f.uncertain=True
        first=self.call('print-next');self.assertEqual(200,first.status_code)
        self.assertEqual('UNCERTAIN',first.json()['delivery']['print_states']['template_a'])
        self.assertEqual(409,self.call('print-next').status_code);self.assertEqual(2,self.f.sends)

    def test_stopped_actor_cannot_accept_later_request_or_restart(self):
        self.assertTrue(self.actor.stop())
        self.assertEqual(409,self.call('prepare').status_code)
        self.assertEqual([],self.f.bind_requests)

    def test_blocked_original_bind_keeps_stop_false_until_request_finishes(self):
        entered=threading.Event();release=threading.Event();errors=[]
        original=self.f.probe.client.session.post
        def blocked(*args,**kwargs):
            entered.set();release.wait(5)
            return original(*args,**kwargs)
        def prepare():
            try:self.actor.prepare(self.f.group,self.f.lease)
            except DraftHeld:pass
            except Exception as error:errors.append(type(error).__name__)
        with patch.object(self.f.probe.client.session,'post',side_effect=blocked):
            thread=threading.Thread(target=prepare);thread.start()
            try:
                self.assertTrue(entered.wait(2));self.assertFalse(self.actor.stop())
                self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
            finally:release.set();thread.join(6)
        self.assertFalse(thread.is_alive());self.assertEqual([],errors)
        self.assertTrue(self.actor.stop());self.assertEqual([],self.queued)

    def test_live_uploader_thread_not_stop_return_value_controls_quiescence(self):
        entered=threading.Event();release=threading.Event()
        def blocked():entered.set();release.wait(5)
        self.actor.worker._thread=threading.Thread(target=blocked)
        self.actor.worker._thread.start()
        try:
            self.assertTrue(entered.wait(2));self.assertFalse(self.actor.stop())
            self.assertTrue(self.actor.worker._stop.is_set())
            self.assertEqual(0,self.f.ledger.db.execute('SELECT closed FROM pp_drafts').fetchone()[0])
        finally:release.set();self.actor.worker._thread.join(6)
        self.assertTrue(self.actor.stop())

    def test_api_lifespan_keeps_shutdown_callback_and_ledger_while_upload_is_active(self):
        entered=threading.Event();release=threading.Event();closed=[]
        def blocked():entered.set();release.wait(5)
        self.actor.worker._thread=threading.Thread(target=blocked)
        self.actor.worker._thread.start()
        app=create_app(self.f.payments,BoothAuthenticator({'PB001':self.f.h.token}),
            background_worker=False,ticket_presentation=self.f.presentation,
            paid_delivery=self.actor,on_shutdown=lambda:closed.append(True))
        try:
            self.assertTrue(entered.wait(2))
            with self.assertRaisesRegex(RuntimeError,'delivery worker remains active'):
                with TestClient(app):pass
            self.assertEqual([],closed)
            self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])
        finally:release.set();self.actor.worker._thread.join(6)
        self.assertTrue(self.actor.stop())

    def test_idle_original_uploader_gets_bounded_exit_time_before_normal_api_close(self):
        closed=[]
        self.actor.worker._thread=threading.Thread(target=self.actor.worker._stop.wait)
        self.actor.worker._thread.start()
        app=create_app(self.f.payments,BoothAuthenticator({'PB001':self.f.h.token}),
            background_worker=False,ticket_presentation=self.f.presentation,
            paid_delivery=self.actor,on_shutdown=lambda:closed.append(True))
        try:
            with TestClient(app):pass
            self.assertEqual([True],closed)
            self.assertFalse(self.actor.worker._thread.is_alive())
        finally:
            self.actor.worker.stop();self.actor.worker._thread.join(3)

    def test_actual_host_keeps_original_kernel_owner_until_its_delivery_thread_exits(self):
        from photobooth.post_preview_host import SandboxHostRuntime
        from photobooth.post_preview_server import build_sandbox_app
        from tests.test_post_preview_host import SandboxHostTests
        helper=SandboxHostTests(methodName='runTest');self.addCleanup(helper.doCleanups)
        def assemble(*args,**kwargs):return build_sandbox_app(*args,**kwargs,paid_delivery_enabled=True)
        with helper.temporary() as directory,patch(
                'photobooth.post_preview_server.platform_protector',return_value=self.f.h.protector),patch(
                'photobooth.post_preview_host.build_sandbox_app',side_effect=assemble):
            config=helper.config(directory)
            host=SandboxHostRuntime(config,helper.bridge());self.addCleanup(host.close)
            release=threading.Event();entered=threading.Event()
            def blocked():entered.set();release.wait(5)
            actor=host.app.state.paid_delivery
            actor.worker._thread=threading.Thread(target=blocked);actor.worker._thread.start()
            try:
                self.assertTrue(entered.wait(2));self.assertFalse(host.close())
                self.assertEqual(0,host.ledger.db.execute('SELECT count(*) FROM pp_drafts').fetchone()[0])
                with self.assertRaises((OSError,RuntimeError)):
                    SandboxHostRuntime(config,helper.bridge())
            finally:release.set();actor.worker._thread.join(6)
            self.assertTrue(host.close())
            successor=SandboxHostRuntime(config,helper.bridge());self.addCleanup(successor.close)
            self.assertTrue(successor.close())

    def native(self):
        client=PostPreviewClient('https://example.invalid','PB001',self.f.h.token,expected_mode='sandbox')
        self.addCleanup(client.close)
        def transport(method,path,*,payload):
            response=self.http.request(method,path,json=payload,headers=self.f.h.headers)
            if response.status_code!=200:raise RuntimeError('Original delivery held')
            return response.json()
        return client,PostPreviewDeliveryClient(client),transport

    def test_native_transport_adapter_reuses_original_authenticated_observations(self):
        client,native,transport=self.native()
        with patch.object(client._transport,'_call',side_effect=transport):
            first=native.prepare(self.f.group,self.f.lease)
            self.assertEqual('QUEUED',first['worker'])
            paid=native.print_next(self.f.group,self.f.lease)
            self.assertTrue(paid['print_all_submitted'])
            self.assertEqual(paid,native.inspect(self.f.group,self.f.lease))
        self.assertEqual(2,self.f.sends)

    def test_native_rejects_scope_grants_paths_and_inconsistent_status(self):
        self.call('prepare');response=self.call('status').json()
        client,native,_=self.native()
        changes=[{'generation':True},{'booth_id':'PB002'},{'mode':'mock'},
            {'fulfillment_authorized':True}]
        for change in changes:
            with patch.object(client._transport,'_call',return_value=dict(response,**change)):
                with self.assertRaises(DraftHeld):native.inspect(self.f.group,self.f.lease)
        for change in ({'physical_paper_verified':True},{'folder_url':'file:///private/photos'},
                       {'upload_total':True},{'output_path':'/private/photos'},
                       {'worker':{}},
                       {'print_all_submitted':True},{'safe_to_release_without_original_claim':True},
                       {'print_states':{'template_a':'UNCERTAIN'},'needs_operator_review':False}):
            view=dict(response['delivery'],**change)
            with patch.object(client._transport,'_call',return_value=dict(response,delivery=view)):
                with self.assertRaises(DraftHeld):native.inspect(self.f.group,self.f.lease)

    def test_native_late_reply_after_privacy_retirement_is_not_exposed(self):
        self.call('prepare');response=self.call('status').json()
        client,native,_=self.native()
        def late(*args,**kwargs):native.hide_private();return response
        with patch.object(client._transport,'_call',side_effect=late):
            with self.assertRaises(DraftHeld):native.inspect(self.f.group,self.f.lease)


if __name__=='__main__':unittest.main()
