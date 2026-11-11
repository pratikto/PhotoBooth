"""Private opt-in SAME original child/native lifecycle; fake external effects."""
from contextlib import nullcontext
from dataclasses import replace
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from photobooth.catalog import get_templates
from photobooth.post_preview_sandbox_visits import OriginalSandboxVisits
from photobooth.post_preview_store import DraftHeld
from tests import test_post_preview_sandbox_visits as original_tests


class DurableOriginalWorkerTests(unittest.TestCase):
    def setUp(self):
        context = nullcontext() if os.name == 'nt' else patch(
            'photobooth.linux_credential_vault._read_key', return_value=b'k'*32)
        context.__enter__(); self.addCleanup(context.__exit__, None, None, None)
        self.f = original_tests.OriginalSandboxVisitTests(methodName='runTest')
        self.addCleanup(self.f.doCleanups)
        original = OriginalSandboxVisits.__init__
        def advanced(manager, *args, **kwargs):
            kwargs['durable_worker_epochs'] = True
            original(manager, *args, **kwargs)
        with patch.object(OriginalSandboxVisits, '__init__', advanced): self.f.setUp()
        self.manager = self.f.visits; self.service = self.f.binding.service

    def bindings(self):
        return [dict(row) for row in self.manager.ledger.db.execute('SELECT * FROM pp_worker_generations')]

    def test_actual_child_custody_and_binding_precede_first_original_photo_prepare(self):
        original = self.service.photos.prepare; observed = []
        def prepared(lease):
            rows = self.bindings()
            self.assertEqual(1, len(rows)); self.assertEqual(lease.draft_id, rows[0]['draft_id'])
            self.assertEqual(self.manager._key.key_id, rows[0]['key_id'])
            observed.append(True)
            return original(lease)
        with patch.object(self.service.photos, 'prepare', side_effect=prepared):
            self.service.start(get_templates(), {'template_a': 1})
        self.assertEqual([True], observed)
        self.assertFalse(hasattr(self.service, '_key')); self.assertFalse(hasattr(self.service, '_worker_generations'))
        self.assertTrue((self.f.config.private_root/'worker-custody'/
                         (self.manager._key.key_id+'.json')).is_file())

    def test_lost_binding_reply_retries_same_draft_without_photo_or_new_epoch(self):
        transport = self.manager._client._transport; original = transport._call; calls = []
        def lose(method, path, **kwargs):
            result = original(method, path, **kwargs)
            if path.endswith('/worker-binding'):
                calls.append(True)
                if len(calls) == 1: raise OSError('synthetic lost binding reply')
            return result
        with patch.object(transport, '_call', side_effect=lose):
            with self.assertRaises(OSError): self.service.start(get_templates(), {'template_a': 1})
            lease = self.service.lease
            self.assertEqual('confirm', self.service.phase)
            self.assertFalse((self.f.config.private_root/'media'/lease.draft_id).exists())
            before = self.bindings()
            self.service.start(get_templates(), {'template_a': 1})
        self.assertEqual(2, len(calls)); self.assertEqual(lease, self.service.lease)
        self.assertEqual(before, self.bindings())
        self.assertEqual(1, self.manager.ledger.db.execute('SELECT COUNT(*) FROM pp_drafts').fetchone()[0])
        self.assertEqual(0, self.manager.ledger.db.execute('SELECT COUNT(*) FROM pp_payment_attempts').fetchone()[0])

    def test_http_binding_accepts_no_key_pid_readiness_or_foreign_generation(self):
        self.service.start(get_templates(), {'template_a': 1}); before = self.bindings()
        transport = self.manager._client._transport; lease = self.service.lease
        url = transport.base_url+'/api/postpay/drafts/'+lease.draft_id+'/worker-binding'
        owner = dict(visit_id=lease.visit_id, generation=lease.generation)
        for extra in ({'key_id':'a'*32}, {'pid':os.getpid()}, {'ready':True}, {'generation':True}):
            response = transport.session.post(url, json=dict(owner, **extra), headers=transport.headers, timeout=5)
            self.assertEqual(422, response.status_code); response.close()
        response = transport.session.post(url, json=owner, timeout=5)
        self.assertEqual(401, response.status_code); response.close()
        self.assertEqual(before, self.bindings())
        health = transport.session.get(transport.base_url+'/api/postpay/health', timeout=5)
        self.assertFalse(health.json()['fulfillment_enabled']); health.close()

    def test_native_flag_cannot_bypass_backend_binding_before_freeze(self):
        # Deliberate untrusted-native bypass fixture; no provider or key injected.
        self.service._requires_worker_binding = False
        self.service.start(get_templates(), {'template_a': 1})
        for _ in range(3):
            view = self.service.snapshot()
            self.service.capture(self.f.frame, view['capture_slot'], view['revision'], view['retake'], view['generation'])
        self.service.compose(); view = self.service.next()
        with self.assertRaises(RuntimeError): self.service.freeze_checkout(view['revision'], view['amount'])
        self.assertEqual([], self.bindings())
        self.assertEqual(0, self.manager.ledger.db.execute('SELECT COUNT(*) FROM pp_checkout_intents').fetchone()[0])

    def paid_then_rotate(self):
        group, proof = self.f.paid(self.f.binding)
        self.service.retire('RESULT_TIMEOUT')
        self.f.retry(self.manager.ensure_new_visitor_ready)
        return group, proof

    def test_original_private_proof_claim_binds_atomically_before_native_media_adoption(self):
        group, proof = self.paid_then_rotate()
        service = self.manager._service; original = service.recover_original_owed; observed = []
        def adopted(grant):
            rows = self.bindings(); self.assertEqual(2, len(rows))
            self.assertTrue(any(row['generation'] == grant.lease.generation
                and row['key_id'] == self.manager._key.key_id for row in rows))
            observed.append(True)
            return original(grant)
        with patch.object(service, 'recover_original_owed', side_effect=adopted):
            restored = self.f.retry(lambda: self.manager.recover_paid(proof))
        self.assertEqual('RESTORED', restored['state']); self.assertEqual([True], observed)
        self.assertEqual(group, restored['purchase_group_id'])

    def test_claim_binding_failure_rolls_back_original_generation_without_tokenless_restore(self):
        _, proof = self.paid_then_rotate(); ledger = self.manager.ledger
        old = dict(ledger.db.execute('SELECT * FROM pp_drafts').fetchone()); bindings = self.bindings()
        with ledger.write(): ledger.db.execute('''CREATE TRIGGER fixture_binding_io_failure
            BEFORE INSERT ON pp_worker_generations WHEN NEW.generation>1
            BEGIN SELECT RAISE(ABORT,'Synthetic binding fault'); END''')
        trace=self.f.config.private_root/'fixture-trace-binding'; trace.touch()
        entered=self.f.config.private_root/'fixture-binding-entered'
        deadline=time.monotonic()+12
        while not entered.exists():
            with self.assertRaises(DraftHeld): self.manager.recover_paid(proof)
            if time.monotonic()>deadline: self.fail('Actual child never reached original claim binding')
            time.sleep(.05)
        self.assertEqual(old, dict(ledger.db.execute('SELECT * FROM pp_drafts').fetchone()))
        self.assertEqual(bindings, self.bindings()); self.assertIsNone(self.manager._service.lease)
        with ledger.write(): ledger.db.execute('DROP TRIGGER fixture_binding_io_failure')
        self.assertEqual('RESTORED', self.f.retry(lambda:self.manager.recover_paid(proof))['state'])
        self.assertEqual(2, len(self.bindings()))

    def test_existing_original_A_B_A_journey_preserves_advanced_epoch_bindings(self):
        self.f.test_actual_A_to_B_to_A_uses_new_children_workers_and_same_original_output()
        rows = self.bindings()
        self.assertEqual(3, len(rows)); self.assertEqual(3, len({row['key_id'] for row in rows}))

    def test_original_durable_root_cannot_downgrade_to_ephemeral_default(self):
        from photobooth.post_preview_worker_fence import WorkerFenceKey
        self.f.shutdown(self.manager)
        default=self.f.manager(); self.addCleanup(self.f.shutdown,default)
        with patch.object(WorkerFenceKey,'create',side_effect=AssertionError('No downgrade key')) as mint:
            with self.assertRaises(DraftHeld): default.start()
        self.assertEqual(0,mint.call_count); self.assertIsNone(default._backend)


class DurableWorkerProtocolTests(unittest.TestCase):
    def test_private_opt_in_is_strict_and_default_protocol_stays_unchanged(self):
        from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment
        from photobooth.post_preview_worker_fence import WorkerFenceKey
        from photobooth.printer import PrinterConfig
        bundle=SandboxHostFulfillment(PrinterConfig(lan_host='fixture-printer'),WorkerFenceKey.create())
        self.assertNotIn('durable_worker_epochs',bundle.to_private_startup())
        advanced=replace(bundle,durable_worker_epochs=True)
        self.assertTrue(SandboxHostFulfillment.from_private_startup(advanced.to_private_startup()).durable_worker_epochs)
        for invalid in (0,1,'true',None):
            with self.assertRaises(ValueError): replace(bundle,durable_worker_epochs=invalid)
            with self.assertRaises(ValueError): SandboxHostFulfillment.from_private_startup(
                dict(bundle.to_private_startup(),durable_worker_epochs=invalid))

    def test_client_rejects_forged_binding_role_generation_or_authority_fields(self):
        from photobooth.post_preview_client import PostPreviewClient
        from photobooth.post_preview_store import DraftLease,ORDER_VERSION
        client=PostPreviewClient('https://fixture.invalid','PB001','b'*48)
        self.addCleanup(client.close)
        lease=DraftLease('a'*32,'PB001','fixture-visit',1)
        expected=dict(kind='ORIGINAL_WORKER_BOUND',draft_id=lease.draft_id,booth_id=lease.booth_id,
            visit_id=lease.visit_id,generation=1,mode='sandbox',order_version=ORDER_VERSION,
            fulfillment_authorized=False)
        with patch.object(client._transport,'_call',return_value=expected) as call:
            self.assertEqual(expected,client.bind_worker_generation(lease))
        self.assertEqual({'visit_id':lease.visit_id,'generation':1},call.call_args.kwargs['payload'])
        for changes in ({'generation':True},{'mode':'mock'},{'fulfillment_authorized':True},
                        {'kind':'ORIGINAL_WORKER_RETIRED'},{'key_id':'a'*32}):
            with patch.object(client._transport,'_call',return_value=dict(expected,**changes)):
                with self.assertRaises(ValueError): client.bind_worker_generation(lease)

    def test_native_opt_in_cannot_be_an_untyped_truthy_value(self):
        from photobooth.kiosk_v2.post_preview_protected_checkout import ProtectedCheckoutService
        from photobooth.post_preview_client import PostPreviewClient
        client=PostPreviewClient('https://fixture.invalid','PB001','b'*48); self.addCleanup(client.close)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'private'
            for invalid in (0,1,'true',None):
                with self.assertRaises(DraftHeld): ProtectedCheckoutService(root,payment_client=client,
                    qr_loader=lambda _:None,require_worker_binding=invalid)
            self.assertFalse(root.exists())


class DurableWorkerLaunchTests(unittest.TestCase):
    def test_original_global_launch_persists_custody_before_actual_child_start(self):
        from tests import test_post_preview_launch as original_launch
        from photobooth.post_preview_bootstrap import SandboxBackendProcess
        helper=original_launch.ProtectedLaunchTests(methodName='runTest'); self.addCleanup(helper.doCleanups)
        context=nullcontext() if os.name=='nt' else patch(
            'photobooth.linux_credential_vault._read_key',return_value=b'k'*32)
        with context,helper.fixture() as (launch,config,legacy):
            original=SandboxBackendProcess.start; observed=[]
            def started(backend,*args,**kwargs):
                key=backend._fulfillment.worker_key
                self.assertTrue((config.private_root/'worker-custody'/(key.key_id+'.json')).is_file())
                helper.locked(launch); observed.append(True)
                return original(backend,*args,**kwargs)
            with patch.object(SandboxBackendProcess,'start',started):
                control=helper.start(launch,config,legacy,durable_worker_epochs=True)
            self.assertEqual('READY',control.state); self.assertEqual([True],observed)
            self.assertFalse(hasattr(control.binding.service,'_key'))

    def test_original_global_owner_retained_on_os_custody_failure_before_child_or_camera_io(self):
        from tests import test_post_preview_launch as original_launch
        from photobooth.post_preview_launch import ProtectedLaunchHeld
        helper=original_launch.ProtectedLaunchTests(methodName='runTest'); self.addCleanup(helper.doCleanups)
        with helper.fixture() as (launch,config,legacy), patch(
                'photobooth.post_preview_worker_custody.platform_protector',side_effect=RuntimeError('PRIVATE OS ERROR')):
            with self.assertRaises(ProtectedLaunchHeld): helper.start(launch,config,legacy,durable_worker_epochs=True)
            helper.locked(launch)
            self.assertIsNone(launch._visits._backend)
            self.assertFalse((config.private_root/'worker-custody').exists())
            self.assertIsNone(launch._camera._thread)


if __name__ == '__main__': unittest.main()
