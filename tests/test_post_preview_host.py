"""Stable Sandbox child-host ownership; no device/provider/Drive requests."""
import tempfile
import unittest
from pathlib import Path
from contextlib import contextmanager


class SandboxHostTests(unittest.TestCase):
    @contextmanager
    def temporary(self):
        # Unittest cleanup is LIFO: stop child/DB owners before removing files,
        # including assertion failures on Windows with locked SQLite handles.
        directory=tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        yield directory.name

    def test_config_retains_same_original_root_and_hides_secrets(self):
        from photobooth.post_preview_host import SandboxHostConfig
        with self.temporary() as directory:
            config=SandboxHostConfig(Path(directory),'MTEST','PB001',
                'Mid-server-HOST-PRIVATE-SECRET','b'*48,
                'https://script.google.com/macros/s/HOST_FIXTURE/exec','drive-private-token')
            self.assertEqual(Path(directory)/'post-preview-sandbox'/'MTEST'/'PB001',config.private_root)
            for secret in (config.server_key,config.booth_token,config.drive_token,config.drive_url):
                self.assertNotIn(secret,repr(config))

    def config(self, directory, **changes):
        from photobooth.post_preview_host import SandboxHostConfig
        values=dict(storage_root=Path(directory),merchant_id='MTEST',booth_id='PB001',
            server_key='Mid-server-HOST-PRIVATE-SECRET',booth_token='b'*48,
            drive_url='https://script.google.com/macros/s/HOST_FIXTURE/exec',
            drive_token='drive-private-token')
        values.update(changes)
        return SandboxHostConfig(**values)

    def bridge(self):
        import socket
        from photobooth.post_preview_readiness_bridge import WorkerReadinessClient
        peer,child=socket.socketpair()
        self.addCleanup(peer.close)
        client=WorkerReadinessClient(child)
        self.addCleanup(client.close)
        return client

    def fake_app(self, *args, **kwargs):
        from types import SimpleNamespace
        return SimpleNamespace(state=SimpleNamespace(lifecycle_worker=None))

    def test_invalid_config_and_archive_paths_create_no_storage(self):
        from dataclasses import replace
        with self.temporary() as directory:
            config=self.config(directory)
            for changes in ({'merchant_id':'../bad'}, {'merchant_id':'old'},
                            {'booth_id':'PB001V2'}, {'server_key':'bad\nkey'},
                            {'booth_token':'short'}, {'drive_url':'https://other.invalid/exec'},
                            {'drive_token':'a\nb'}, {'storage_root':Path(directory)/'old'/'data'},
                            {'storage_root':Path('relative')}):
                with self.subTest(changes=tuple(changes)),self.assertRaises(ValueError):
                    replace(config,**changes)
            self.assertFalse(config.private_root.exists())

    def test_original_ledger_media_and_visit_survive_host_reopen(self):
        from unittest.mock import patch
        from photobooth.post_preview_host import SandboxHostRuntime
        with self.temporary() as directory,patch(
                'photobooth.post_preview_host.build_sandbox_app',side_effect=self.fake_app):
            config=self.config(directory)
            first=SandboxHostRuntime(config,self.bridge())
            self.addCleanup(first.close)
            lease=first.ledger.create('PB001','original-visit',{'template_a':2})
            self.assertEqual(config.private_root/'media',first.checkout.photos.root)
            self.assertTrue(first.close())
            second=SandboxHostRuntime(config,self.bridge())
            self.addCleanup(second.close)
            saved=second.ledger.inspect(lease)
            self.assertEqual('original-visit',saved['visit_id'])
            self.assertEqual(1,second.ledger.db.execute('SELECT COUNT(*) FROM pp_drafts').fetchone()[0])
            marker=(config.private_root/'host-context.json').read_text()
            for secret in (config.server_key,config.booth_token,config.drive_token):
                self.assertNotIn(secret,marker)

    def test_only_one_backend_owner_and_no_lock_file_removal(self):
        from unittest.mock import patch
        from photobooth.post_preview_host import SandboxHostRuntime
        with self.temporary() as directory,patch(
                'photobooth.post_preview_host.build_sandbox_app',side_effect=self.fake_app):
            config=self.config(directory)
            host=SandboxHostRuntime(config,self.bridge());self.addCleanup(host.close)
            with self.assertRaises((OSError,RuntimeError)):
                SandboxHostRuntime(config,self.bridge())
            self.assertTrue(host.close())
            lock=config.private_root/'backend-owner'/'data'/'kiosk-v2-launch.lock'
            self.assertTrue(lock.is_file())
            again=SandboxHostRuntime(config,self.bridge());self.addCleanup(again.close)
            self.assertEqual(host.root,again.root)

    def test_partial_or_foreign_context_is_preserved_and_refused(self):
        import json
        from unittest.mock import patch
        from photobooth.post_preview_host import SandboxHostRuntime
        with self.temporary() as directory,patch(
                'photobooth.post_preview_host.build_sandbox_app',side_effect=self.fake_app):
            config=self.config(directory)
            host=SandboxHostRuntime(config,self.bridge());host.close()
            path=config.private_root/'host-context.json'
            valid=json.loads(path.read_text())
            for damaged in (b'{',json.dumps({'mode':'mock'}).encode(),b'x'*4097,
                            json.dumps(dict(valid,version=True)).encode(),
                            ('{"mode":"mock",'+json.dumps(valid)[1:]).encode()):
                path.write_bytes(damaged)
                with self.assertRaises(ValueError):SandboxHostRuntime(config,self.bridge())
                self.assertEqual(damaged,path.read_bytes())

    def test_failed_assembly_closes_only_its_resources_and_keeps_ledger(self):
        from unittest.mock import patch
        from photobooth.post_preview_host import SandboxHostRuntime
        with self.temporary() as directory:
            config=self.config(directory)
            with patch('photobooth.post_preview_host.build_sandbox_app',side_effect=RuntimeError('fixture')):
                with self.assertRaises(RuntimeError):SandboxHostRuntime(config,self.bridge())
            self.assertTrue((config.private_root/'drafts.sqlite3').is_file())
            with patch('photobooth.post_preview_host.build_sandbox_app',side_effect=self.fake_app):
                host=SandboxHostRuntime(config,self.bridge());self.addCleanup(host.close)
                self.assertTrue(host.close())

    def test_unfinished_financial_worker_retains_ledger_and_backend_lock(self):
        from unittest.mock import Mock,patch
        from photobooth.post_preview_host import SandboxHostRuntime
        with self.temporary() as directory,patch(
                'photobooth.post_preview_host.build_sandbox_app',side_effect=self.fake_app):
            config=self.config(directory)
            host=SandboxHostRuntime(config,self.bridge())
            worker=Mock();worker.stop.return_value=False
            host.app.state.lifecycle_worker=worker
            self.assertFalse(host.close(timeout=0))
            self.assertEqual(0,host.ledger.db.execute('SELECT COUNT(*) FROM pp_drafts').fetchone()[0])
            with self.assertRaises((OSError,RuntimeError)):SandboxHostRuntime(config,self.bridge())
            worker.stop.return_value=True
            self.assertTrue(host.close(timeout=0))
            self.assertTrue(host.close())

    def test_original_factory_health_is_sandbox_and_not_a_mock_or_legacy_route(self):
        import os
        from contextlib import nullcontext
        from unittest.mock import patch
        from fastapi.testclient import TestClient
        from photobooth.post_preview_host import SandboxHostRuntime
        # Linux control-flow fixture; actual Secret Service evidence is separate.
        custody=patch('photobooth.linux_credential_vault._read_key',return_value=b'k'*32) if os.name!='nt' else nullcontext()
        with self.temporary() as directory,custody,patch(
                'photobooth.midtrans_sandbox.MidtransSandboxClient._request',side_effect=AssertionError('No provider I/O')) as io:
            host=SandboxHostRuntime(self.config(directory),self.bridge())
            self.addCleanup(host.close)
            with TestClient(host.app) as http:
                health=http.get('/api/postpay/health')
                self.assertEqual('sandbox',health.json()['mode'])
                self.assertFalse(health.json()['fulfillment_enabled'])
                self.assertEqual(404,http.post('/api/postpay/simulate-paid').status_code)
                self.assertEqual(404,http.post('/api/orders').status_code)
                self.assertEqual(401,http.get('/api/postpay/groups/original').status_code)
            io.assert_not_called()
            self.assertTrue(host._closed)

    def test_backend_bootstrap_environment_does_not_inherit_account_secrets(self):
        from photobooth.post_preview_bootstrap import backend_environment
        clean=backend_environment({'PATH':'/bin','MIDTRANS_SERVER_KEY':'private',
            'PHOTOBOOTH_UPLOAD_TOKEN':'drive-private','DBUS_SESSION_BUS_ADDRESS':'unix:path=/fixture/bus',
            'PYTHONPATH':'/untrusted','UNRELATED_SECRET':'hidden','HTTPS_PROXY':'http://proxy:8080'})
        self.assertEqual({'PATH','DBUS_SESSION_BUS_ADDRESS','HTTPS_PROXY'},set(clean))

    def launch(self, config):
        import socket,time
        from unittest.mock import patch
        from photobooth.post_preview_bootstrap import SandboxBackendProcess
        from photobooth.post_preview_readiness_bridge import WorkerReadinessServer
        from tests.test_post_preview_readiness import _bridge_ready
        worker,child=socket.socketpair()
        collector=WorkerReadinessServer(worker,lambda scope:_bridge_ready(scope,time.time()))
        collector.start()
        self.addCleanup(collector.stop)
        process=SandboxBackendProcess(config)
        def close():
            if not process.stop(timeout=3):
                (config.private_root/'fixture-release').write_text('fixture released')
                if not process.stop(timeout=5):
                    # Test-only isolated fake-HTTP child, never an operational process.
                    process.process.kill();process.process.wait(timeout=5)
        self.addCleanup(close)
        with patch('photobooth.post_preview_bootstrap.CHILD_MODULE','tests.post_preview_host_process_fixture'):
            process.start(child,timeout=20)
        return process

    def test_actual_child_owns_stable_root_and_only_loopback_sandbox_health(self):
        import json
        from urllib.request import build_opener,ProxyHandler
        with self.temporary() as directory:
            config=self.config(directory)
            process=self.launch(config)
            self.assertTrue(process.endpoint.startswith('http://127.0.0.1:'))
            with build_opener(ProxyHandler({})).open(process.endpoint+'/api/postpay/health',timeout=2) as r:
                health=json.load(r)
            self.assertEqual('sandbox',health['mode'])
            self.assertFalse(health['fulfillment_enabled'])
            for secret in (config.server_key,config.booth_token,config.drive_token):
                self.assertNotIn(secret,repr(process))
                self.assertNotIn(secret,' '.join(process.process.args))
            self.assertTrue(process.stop())
            self.assertTrue((config.private_root/'drafts.sqlite3').is_file())

    def test_actual_failed_child_start_is_redacted_and_preserves_root(self):
        from photobooth.post_preview_bootstrap import BackendStartupHeld
        with self.temporary() as directory:
            config=self.config(directory,server_key='Mid-server-FAIL-FIXTURE')
            with self.assertRaises(BackendStartupHeld) as error:self.launch(config)
            self.assertNotIn(config.server_key,str(error.exception))
            self.assertTrue((config.private_root/'host-context.json').is_file())
            # Original root/identity is retained, not a fallback trial root.
            live=self.launch(self.config(directory))
            self.assertTrue(live.stop())

    def test_actual_slow_shutdown_retains_backend_lock_until_worker_stops(self):
        from photobooth.post_preview_bootstrap import BackendStartupHeld
        with self.temporary() as directory:
            config=self.config(directory,server_key='Mid-server-HOLD-FIXTURE')
            original=self.launch(config)
            self.assertFalse(original.stop(timeout=.1))
            self.assertIsNone(original.endpoint)
            with self.assertRaises(BackendStartupHeld):self.launch(config)
            (config.private_root/'fixture-release').write_text('fixture released')
            self.assertTrue(original.stop(timeout=5))
            later=self.launch(self.config(directory))
            self.assertTrue(later.stop())

    def test_actual_parent_control_disconnect_gracefully_stops_original_child(self):
        with self.temporary() as directory:
            process=self.launch(self.config(directory))
            process._control.close()
            process.process.wait(timeout=5)
            self.assertEqual(0,process.process.returncode)
            self.assertTrue(process.stop())

    def test_actual_crash_reopens_original_visit_without_new_ledger_or_media(self):
        from photobooth.post_preview_store import PostPreviewStore
        with self.temporary() as directory:
            config=self.config(directory)
            process=self.launch(config)
            ledger=PostPreviewStore(config.private_root/'drafts.sqlite3')
            lease=ledger.create('PB001','original-A',{'template_a':1})
            ledger.close()
            media=config.private_root/'media';media.mkdir()
            sentinel=media/'fixture-original';sentinel.write_bytes(b'original media evidence')
            process.process.kill();process.process.wait(timeout=5)
            again=self.launch(config)
            ledger=PostPreviewStore(config.private_root/'drafts.sqlite3')
            try:
                self.assertEqual('original-A',ledger.inspect(lease)['visit_id'])
                self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_drafts').fetchone()[0])
                self.assertEqual(b'original media evidence',sentinel.read_bytes())
            finally:ledger.close()
            self.assertTrue(again.stop())

    def prepare_original_checkout(self, config, *, offered=True):
        import os
        from contextlib import nullcontext
        from unittest.mock import patch
        from PIL import Image
        from photobooth.booth_storage import BoothWorkspace
        from photobooth.catalog import get_templates
        from photobooth.credential_vault import platform_protector
        from photobooth.post_preview_ccp import OriginalCCPService
        from photobooth.post_preview_checkout import ChargeReadiness,PrivateDraftCheckout
        from photobooth.post_preview_photos import PrivateDraftPhotos
        from photobooth.post_preview_store import PostPreviewStore
        ledger=PostPreviewStore(config.private_root/'drafts.sqlite3')
        self.addCleanup(ledger.close)
        lease=ledger.create('PB001','original-paid-A',{'template_a':1})
        photos=PrivateDraftPhotos(ledger,config.private_root/'media')
        template=get_templates()[0]
        for slot in range(3):
            photos.capture(lease,template,Image.new('RGB',(32,24),'blue'),
                           slot=slot,revision=ledger.inspect(lease)['revision'])
        checkout=PrivateDraftCheckout(photos)
        checkout.approve(lease,template,revision=ledger.inspect(lease)['revision'])
        intent=checkout.freeze(lease,[template],revision=ledger.inspect(lease)['revision'],
            readiness=ChargeReadiness(True,True,True,True,True,True,True,25),expected_amount=10000)
        custody=patch('photobooth.linux_credential_vault._read_key',return_value=b'k'*32) if os.name!='nt' else nullcontext()
        with custody:
            ccp=OriginalCCPService(ledger,platform_protector(),'MTEST')
            if offered:
                ccp.issue_once(lease)
                offer=ccp.private_offer(lease);ccp.mark_visible(lease,offer)
        BoothWorkspace(config.storage_root/'post-preview-sandbox'/'MTEST'/'delivery','PB001V2S2').prepare()
        return ledger,lease,intent['purchase_group_id']

    def test_actual_child_owns_original_ccp_and_rejects_old_permit_after_restart(self):
        import requests
        from photobooth.post_preview_client import PostPreviewClient
        from photobooth.post_preview_proof_client import PostPreviewCCPClient
        from photobooth.post_preview_store import DraftHeld
        with self.temporary() as directory:
            config=self.config(directory)
            process=self.launch(config)
            ledger,lease,group=self.prepare_original_checkout(config,offered=False)
            def client(endpoint):
                session=requests.Session();session.trust_env=False
                value=PostPreviewClient(endpoint,'PB001',config.booth_token,
                    allow_local_http=True,session=session)
                self.addCleanup(value.close)
                return value
            original=client(process.endpoint)
            proof=PostPreviewCCPClient(original)
            with self.assertRaises(RuntimeError):original.begin(group,lease)
            offer=proof.private_offer(group,lease)
            before=dict(ledger.db.execute('SELECT * FROM pp_ccp_credentials').fetchone())
            self.assertIsNone(before['offered_at'])
            with self.assertRaises(RuntimeError):original.begin(group,lease)
            self.assertTrue(process.stop())
            again=self.launch(config)
            later=client(again.endpoint)
            restored=PostPreviewCCPClient(later)
            with self.assertRaises(RuntimeError):
                later._transport._call('POST','/api/postpay/groups/'+group+'/ccp/visible',
                    payload=dict(later._owner(lease),presentation_id=offer.presentation_id))
            returned=restored.private_offer(group,lease)
            self.assertEqual(offer.qr_payload,returned.qr_payload)
            self.assertNotEqual(offer.presentation_id,returned.presentation_id)
            after=dict(ledger.db.execute('SELECT * FROM pp_ccp_credentials').fetchone())
            self.assertEqual(before,after)
            restored.mark_visible(lease,returned)
            paid=later.begin(group,lease)
            self.assertIn(paid['state'],{'PENDING','PAID_LIVE'})
            self.assertTrue(self.fresh_paid(later,group,'connectivity')['paid_verified'])
            with self.assertRaises(DraftHeld):restored.private_offer(group,lease)
            self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_ccp_credentials').fetchone()[0])
            self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
            self.assertTrue(again.stop())

    def test_actual_private_bridge_api_and_client_preserve_paid_once_across_child_restart(self):
        import requests
        from photobooth.post_preview_client import PostPreviewClient
        with self.temporary() as directory:
            config=self.config(directory)
            original=self.launch(config)
            ledger,lease,group=self.prepare_original_checkout(config)
            session=requests.Session();session.trust_env=False
            client=PostPreviewClient(original.endpoint,'PB001',config.booth_token,
                                     allow_local_http=True,session=session)
            self.addCleanup(client.close)
            first=client.begin(group,lease)
            self.assertIn(first['state'],{'PENDING','PAID_LIVE'})
            paid=self.fresh_paid(client,group,'connectivity')
            self.assertTrue(paid['paid_verified'])
            self.assertEqual(('PAID_LIVE','OWED'),(paid['state'],paid['obligation_state']))
            entitlement=paid['entitlement_id']
            self.assertFalse(paid['fulfillment_authorized'])
            self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
            self.assertTrue(original.stop())
            again=self.launch(config)
            second_session=requests.Session();second_session.trust_env=False
            second=PostPreviewClient(again.endpoint,'PB001',config.booth_token,
                                    allow_local_http=True,session=second_session)
            self.addCleanup(second.close)
            resumed=self.fresh_paid(second,group,'restart')
            self.assertTrue(resumed['paid_verified'])
            self.assertEqual(entitlement,resumed['entitlement_id'])
            self.assertEqual('OWED',resumed['obligation_state'])
            self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
            self.assertEqual(3,len(list((config.private_root/'media').rglob('*.jpg'))))
            self.assertTrue(again.stop())

    def test_actual_lost_create_reply_reconciles_original_attempt_after_child_restart(self):
        import requests
        from photobooth.post_preview_client import PostPreviewClient
        with self.temporary() as directory:
            config=self.config(directory,server_key='Mid-server-LOST-FIXTURE')
            original=self.launch(config)
            ledger,lease,group=self.prepare_original_checkout(config)
            session=requests.Session();session.trust_env=False
            client=PostPreviewClient(original.endpoint,'PB001',config.booth_token,
                                     allow_local_http=True,session=session)
            self.addCleanup(client.close)
            first=client.begin(group,lease)
            self.assertIn(first['state'],{'UNKNOWN','PAID_LIVE'})
            attempt=first['attempts'][0]['provider_order_id']
            self.assertTrue(original.stop())
            again=self.launch(config)
            later_session=requests.Session();later_session.trust_env=False
            later=PostPreviewClient(again.endpoint,'PB001',config.booth_token,
                                   allow_local_http=True,session=later_session)
            self.addCleanup(later.close)
            paid=self.fresh_paid(later,group,'restart')
            self.assertTrue(paid['paid_verified'])
            self.assertEqual(attempt,paid['attempts'][0]['provider_order_id'])
            self.assertEqual(1,len(paid['attempts']))
            self.assertEqual('OWED',paid['obligation_state'])
            self.assertTrue(again.stop())

    def fresh_paid(self, client, group, trigger):
        import time
        deadline=time.monotonic()+5
        while True:
            view=client.reconcile(group,trigger=trigger)
            if view['paid_verified'] or time.monotonic()>=deadline:
                return view
            # Preserve the original Sandbox one-second priority/freshness pace;
            # a cached/background observation cannot count as fresh settlement.
            time.sleep(.1)

    def test_actual_inflight_http_thread_keeps_original_db_and_owner_during_shutdown(self):
        import requests,threading,time
        from photobooth.post_preview_bootstrap import BackendStartupHeld
        from photobooth.post_preview_client import PostPreviewClient
        with self.temporary() as directory:
            config=self.config(directory,server_key='Mid-server-HTTP-HOLD-FIXTURE')
            original=self.launch(config)
            ledger,lease,group=self.prepare_original_checkout(config)
            session=requests.Session();session.trust_env=False
            client=PostPreviewClient(original.endpoint,'PB001',config.booth_token,
                allow_local_http=True,session=session,timeout=25)
            self.addCleanup(client.close)
            result=[];errors=[]
            def request():
                try:result.append(client.begin(group,lease))
                except Exception as error:errors.append(type(error).__name__)
            thread=threading.Thread(target=request,daemon=True)
            thread.start()
            release=config.private_root/'fixture-http-release'
            try:
                deadline=time.monotonic()+10
                while not (config.private_root/'fixture-http-entered').exists() and time.monotonic()<deadline:
                    time.sleep(.02)
                self.assertTrue((config.private_root/'fixture-http-entered').exists())
                self.assertFalse(original.stop(timeout=.1))
                # Exceed the formerly proposed 5s HTTP cancellation boundary.
                # No DB/lease may close while its real thread is still running.
                time.sleep(6)
                self.assertIsNone(original.process.poll())
                with self.assertRaises(BackendStartupHeld):self.launch(config)
            finally:
                release.write_text('fixture HTTP released')
                thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
            self.assertEqual([],errors)
            self.assertTrue(result[0]['paid_verified'])
            self.assertEqual('OWED',result[0]['obligation_state'])
            self.assertTrue(original.stop(timeout=5))
            self.assertEqual(1,ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])
