"""Owned acceptance metadata only; fake account/device effects in fixtures."""
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from photobooth import post_preview_acceptance as acceptance
from photobooth.kiosk_v2.recovery import LaunchLease
from tests import test_post_preview_launch_settings as fixtures
from tools import run_post_preview_acceptance as entry


class OwnedAcceptanceTests(unittest.TestCase):
    @contextmanager
    def fixture(self):
        helper = fixtures.ProtectedLaunchSettingsTests(methodName='runTest')
        with helper.fixture() as (owner,root,local,history):
            owner.stop(timeout=0)
            with patch.object(acceptance,'_windows_host',return_value=True), \
                 patch.object(acceptance,'_dependencies',return_value=True), \
                 patch.object(acceptance,'_source',return_value=('a'*40,True)), \
                 patch.object(acceptance,'_dpapi_self_test',return_value=True), \
                 patch.object(entry,'ROOT',root):
                yield root,local,history

    def report(self, root): return acceptance.preflight(root,root/'protected','PB001')

    def session(self, root): return acceptance.save_session(root,self.report(root))

    def test_passive_checks_preserve_history_and_open_no_native_backend_or_worker_key(self):
        with self.fixture() as (root,local,history):
            before = hashlib.sha256(history.read_bytes()).hexdigest()
            with patch('photobooth.post_preview_launch.ProtectedSandboxLaunch.start',side_effect=AssertionError('No native')), \
                 patch('photobooth.post_preview_worker_fence.WorkerFenceKey.create',side_effect=AssertionError('No worker key')):
                report = self.report(root)
            self.assertEqual('LOCAL_PREREQUISITES_PASS',report['status'])
            self.assertTrue(all(value=='NOT_RUN' for value in report['owner_cases'].values()))
            self.assertFalse(report['commercial_ready']); self.assertFalse((root/'protected').exists())
            self.assertEqual(before,hashlib.sha256(history.read_bytes()).hexdigest())
            with LaunchLease(root): pass

    def test_nonwindows_or_missing_dependency_blocks_before_private_reads(self):
        with self.fixture() as (root,local,history):
            for name in ('_windows_host','_dependencies'):
                with patch.object(acceptance,name,return_value=False), patch(
                        'photobooth.post_preview_launch_settings.load_settings',side_effect=AssertionError('No private read')):
                    report = self.report(root)
                self.assertEqual('BLOCKED',report['status'])
                self.assertEqual('NOT_CHECKED',report['checks']['original_configuration_history'])

    def test_actual_current_platform_dpapi_probe_never_provisions_or_claims_backup(self):
        self.assertEqual(os.name=='nt',acceptance._dpapi_self_test())

    def test_original_history_or_custody_failure_is_fixed_and_redacted(self):
        with self.fixture() as (root,local,history):
            with patch('photobooth.post_preview_launch_settings.load_settings',side_effect=RuntimeError('PRIVATE SECRET /photo/ MEONG:CCP')):
                report = self.report(root)
            text = json.dumps(report)
            self.assertEqual('BLOCKED',report['status'])
            for private in ('PRIVATE SECRET','MEONG:CCP',str(root),'SETTINGS-FIXTURE','synthetic-settings-token'):
                self.assertNotIn(private,text)
            with patch.object(acceptance,'_dpapi_self_test',return_value=False):
                self.assertEqual('BLOCKED',self.report(root)['checks']['current_account_dpapi'])

    def test_original_profile_conflict_is_not_silently_disabled(self):
        with self.fixture() as (root,local,history),patch.dict(os.environ,PHOTOBOOTH_V2_CHECKOUT_MOCK='1'):
            self.assertEqual('BLOCKED',self.report(root)['checks']['isolated_profile'])
            self.assertEqual('1',os.environ['PHOTOBOOTH_V2_CHECKOUT_MOCK'])

    def test_session_run_validation_binds_original_root_account_and_source(self):
        with self.fixture() as (root,local,history):
            session = self.session(root)
            self.assertTrue(acceptance.validate_for_run(root,root/'protected','PB001',session))
            with self.assertRaises(acceptance.AcceptanceHeld):
                acceptance.validate_for_run(root,root/'another','PB001',session)
            with patch.object(acceptance,'_source',return_value=('b'*40,True)):
                with self.assertRaises(acceptance.AcceptanceHeld):
                    acceptance.validate_for_run(root,root/'protected','PB001',session)
                with self.assertRaises(acceptance.AcceptanceHeld):
                    acceptance.record_result(root,session,'WN02','PASS')
                self.assertEqual('SOURCE_CHANGED_RETEST_NEEDED',acceptance.summary(root,session)['normal_flow'])

    def test_runtime_handoff_requires_same_original_prestart_owner_and_scope(self):
        from photobooth.post_preview_launch import ProtectedSandboxLaunch
        from photobooth.post_preview_launch_settings import load_settings
        with self.fixture() as (root,local,history):
            session=self.session(root)
            owner=ProtectedSandboxLaunch(root)
            try:
                settings=load_settings(owner,storage_root=root/'protected',booth_id='PB001')
                acceptance.validate_runtime_session(owner,settings,session)
                owner._started=True
                with self.assertRaises(acceptance.AcceptanceHeld):
                    acceptance.validate_runtime_session(owner,settings,session)
            finally: self.assertTrue(owner.stop(timeout=0))

    def test_owner_results_append_and_never_claim_commercial_or_backend_authority(self):
        with self.fixture() as (root,local,history):
            session = self.session(root)
            manifest = root/'data'/'post-preview-acceptance'/session/'session.json'
            before = manifest.read_bytes()
            acceptance.record_result(root,session,'WN02','FAIL')
            for case in acceptance.CASES: acceptance.record_result(root,session,case,'PASS')
            report = acceptance.summary(root,session)
            self.assertEqual('PASS_OWNER_REPORTED',report['normal_flow'])
            self.assertEqual(11,report['observation_count'])
            self.assertFalse(report['commercial_ready'])
            self.assertIn('NOT_INDEPENDENTLY_VERIFIED',report['evidence_origin'])
            self.assertEqual(before,manifest.read_bytes())
            self.assertFalse((root/'protected').exists())

    def test_unknown_blocked_or_free_text_observations_do_not_create_a_session(self):
        with self.fixture() as (root,local,history):
            folder = root/'data'/'post-preview-acceptance'
            with self.assertRaises(acceptance.AcceptanceHeld): acceptance.record_result(root,'0'*32,'WN02','PASS')
            self.assertFalse(folder.exists())
            session = self.session(root)
            for case,result in (('MEONG:CCP:SECRET','PASS'),('WN02','secret-token')):
                with self.assertRaises(acceptance.AcceptanceHeld): acceptance.record_result(root,session,case,result)
            report = self.report(root); report['checks']['windows']='BLOCKED'; report['status']='BLOCKED'
            blocked = acceptance.save_session(root,report)
            with self.assertRaises(acceptance.AcceptanceHeld): acceptance.record_result(root,blocked,'WN02','PASS')

    def test_malformed_extra_private_fields_and_linked_manifest_are_held_without_echo(self):
        with self.fixture() as (root,local,history):
            session = self.session(root)
            path = root/'data'/'post-preview-acceptance'/session/'session.json'
            raw = path.read_bytes(); value=json.loads(raw); value['token']='PRIVATE-NEVER-PRINT'
            path.write_bytes(acceptance._raw(value))
            with self.assertRaises(acceptance.AcceptanceHeld) as caught: acceptance.summary(root,session)
            self.assertNotIn('PRIVATE-NEVER-PRINT',str(caught.exception))
            path.write_bytes(raw); os.link(path,path.with_suffix('.alias'))
            with self.assertRaises(acceptance.AcceptanceHeld): acceptance.load_session(root,session)
            self.assertEqual(raw,path.read_bytes())

    def test_cli_preflight_record_show_are_redacted_and_bad_arguments_never_echo_proofs(self):
        with self.fixture() as (root,local,history),patch('sys.stdout',new_callable=io.StringIO) as output, \
                patch('sys.stderr',new_callable=io.StringIO) as error:
            self.assertEqual(0,entry.main(['preflight','--storage-root',str(root/'protected')]))
            line=next(s for s in output.getvalue().splitlines() if s.startswith('ACCEPTANCE_SESSION='))
            session=line.split('=',1)[1]
            self.assertEqual(0,entry.main(['record','--session',session,'--case','WN02','--result','PASS']))
            self.assertEqual(0,entry.main(['show','--session',session]))
            self.assertEqual(2,entry.main(['record','--session',session,'--case','MEONG:CCP:PRIVATE','--result','PASS']))
            for private in ('MEONG:CCP:PRIVATE','SETTINGS-FIXTURE','synthetic-settings-token',str(root)):
                self.assertNotIn(private,output.getvalue()+error.getvalue())

    def test_source_checks_allow_documentation_changes_but_hold_runtime_changes(self):
        root=Path.cwd()
        for changed,clean in (('docs/owner.json\nAGENTS.md',True),('photobooth/a.py',False)):
            values=[SimpleNamespace(returncode=0,stdout='a'*40),SimpleNamespace(returncode=0,stdout=changed),
                    SimpleNamespace(returncode=0,stdout=acceptance.BRANCH)]
            with patch.object(acceptance.subprocess,'run',side_effect=values):
                self.assertEqual(('a'*40,clean),acceptance._source(root))

    def test_failed_report_sync_keeps_partial_bytes_and_never_replaces_original(self):
        with self.fixture() as (root,local,history):
            report=self.report(root)
            with patch.object(acceptance.os,'fsync',side_effect=OSError('PRIVATE IO')):
                with self.assertRaises(acceptance.AcceptanceHeld): acceptance.save_session(root,report)
            path=root/'data'/'post-preview-acceptance'/report['session_id']/'session.json'
            original=path.read_bytes()
            with self.assertRaises(acceptance.AcceptanceHeld): acceptance.save_session(root,report)
            self.assertEqual(original,path.read_bytes())
