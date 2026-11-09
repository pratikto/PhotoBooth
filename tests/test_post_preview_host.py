"""Stable Sandbox child-host ownership; no device/provider/Drive requests."""
import tempfile
import unittest
from pathlib import Path


class SandboxHostTests(unittest.TestCase):
    def test_config_retains_same_original_root_and_hides_secrets(self):
        from photobooth.post_preview_host import SandboxHostConfig
        with tempfile.TemporaryDirectory() as directory:
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
        with tempfile.TemporaryDirectory() as directory:
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
        with tempfile.TemporaryDirectory() as directory,patch(
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
        with tempfile.TemporaryDirectory() as directory,patch(
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
        with tempfile.TemporaryDirectory() as directory,patch(
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
        with tempfile.TemporaryDirectory() as directory:
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
        with tempfile.TemporaryDirectory() as directory,patch(
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
        with tempfile.TemporaryDirectory() as directory,custody,patch(
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
