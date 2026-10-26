"""Exercise real diagnostic/client boundaries with synthetic HTTP and local reports."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError
from photobooth.retention import RETENTION_MARKER
from photobooth.retention_readiness import check
from tools.check_drive_retention import main


def backend_status(**changes):
    return dict(protocol_version=1, managed_by=RETENTION_MARKER, retention_days=30,
                enabled=True, clock_trigger_count=1, drive_api_accessible=True,
                state='READY') | changes


class Session:
    def __init__(self, body):
        self.body, self.calls = body, []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs['json']))
        body = self.body
        class Response:
            status_code = 200
            def json(self):
                return body
        return Response()


def client(body):
    return AppsScriptDriveClient('https://example.test/private/exec', 'fixture-private-token',
                                 session=Session(body))


class RetentionReadinessTests(unittest.TestCase):
    def test_ready_uses_one_status_action_without_content_mutations_or_secret_export(self):
        status = backend_status(folder_id='private-parent-id', token='private-extra-token',
                                error='private-error-url')
        transport = client({'ok': True, 'retention_status': status})
        report = check(Path.cwd(), client_factory=lambda: transport)
        self.assertEqual(report['drive_retention']['state'], 'READY')
        self.assertEqual(transport.session.calls[0][1],
                         {'action': 'retention_status', 'token': 'fixture-private-token'})
        self.assertEqual(len(transport.session.calls), 1)
        self.assertFalse(report['drive_retention']['cloud_deletion_verified'])
        self.assertTrue(all(gate == 'NOT_RUN' for gate in report['acceptance'].values()))
        self.assertNotIn('private-', json.dumps(report))

    def test_missing_or_invalid_local_configuration_never_attempts_a_remote_action(self):
        report = check(Path.cwd(), client_factory=lambda: None)
        self.assertEqual(report['drive_retention']['state'], 'NOT_CONFIGURED')
        def invalid():
            raise ValueError('private-configuration-value')
        report = check(Path.cwd(), client_factory=invalid)
        self.assertEqual(report['drive_retention']['state'], 'LOCAL_CONFIGURATION_INVALID')
        self.assertNotIn('private-configuration-value', json.dumps(report))

    def test_all_activation_failures_remain_actionable_observations_not_deletion_passes(self):
        for state, changes in {
            'CONFIGURATION_REQUIRED': {}, 'SETUP_REQUIRED': {'enabled': False},
            'TRIGGER_MISSING': {'clock_trigger_count': 0},
            'DUPLICATE_TRIGGERS': {'clock_trigger_count': 2},
            'TRIGGER_ACCESS_REQUIRED': {'clock_trigger_count': None},
            'DRIVE_API_UNAVAILABLE': {'drive_api_accessible': False},
            'DRIVE_PARENT_INVALID': {},
        }.items():
            with self.subTest(state=state):
                transport = client({'ok': True, 'retention_status': backend_status(state=state, **changes)})
                report = check(Path.cwd(), client_factory=lambda: transport)
                self.assertEqual(report['drive_retention']['state'], state)
                self.assertTrue(report['drive_retention']['next_action'])
                self.assertFalse(report['drive_retention']['cloud_deletion_verified'])
                self.assertEqual(len(transport.session.calls), 1)

    def test_old_web_app_auth_access_and_network_errors_are_redacted_and_distinct(self):
        for code, state in ((400, 'WEB_APP_UPDATE_REQUIRED'), (401, 'AUTHENTICATION_FAILED'),
                            (403, 'WEB_APP_ACCESS_REQUIRED'), (503, 'NETWORK_UNAVAILABLE')):
            with self.subTest(code=code):
                transport = client({'ok': False, 'code': code, 'error': 'private-raw-response'})
                report = check(Path.cwd(), client_factory=lambda: transport)
                self.assertEqual(report['drive_retention']['state'], state)
                self.assertIsNone(report['drive_retention']['backend'])
                self.assertNotIn('private-', json.dumps(report))

    def test_malformed_policy_or_false_ready_cannot_be_reported_as_activated(self):
        invalid = [None, [], {}, backend_status(protocol_version=2),
                   backend_status(managed_by='other'), backend_status(retention_days=60),
                   backend_status(enabled='true'), backend_status(clock_trigger_count=True),
                   backend_status(clock_trigger_count=0), backend_status(drive_api_accessible=False),
                   backend_status(state=[])]
        for status in invalid:
            with self.subTest(status=status):
                transport = client({'ok': True, 'retention_status': status})
                with self.assertRaises(DriveApiError):
                    transport.retention_status()
                report = check(Path.cwd(), client_factory=lambda: transport)
                self.assertEqual(report['drive_retention']['state'], 'WEB_APP_UPDATE_REQUIRED')

    def test_actual_ignored_v1_configuration_is_reused_without_reading_or_creating_photos(self):
        from types import ModuleType
        settings = ModuleType('photobooth.local_settings')
        settings.WEB_APP_URL = 'https://example.test/private/exec'
        settings.UPLOAD_TOKEN = 'fixture-private-token'
        import os, sys
        with patch.dict(os.environ, {'PHOTOBOOTH_WEB_APP_URL': '', 'PHOTOBOOTH_UPLOAD_TOKEN': ''}), \
                patch.dict(sys.modules, {'photobooth.local_settings': settings}), \
                patch('requests.Session', return_value=Session({'ok': True,
                      'retention_status': backend_status()})):
            report = check(Path.cwd())
        self.assertEqual(report['drive_retention']['state'], 'READY')
        self.assertNotIn('private-', json.dumps(report))

    def test_cli_writes_only_safe_metadata_and_returns_attention_without_auto_activation(self):
        for ready in (False, True):
            with self.subTest(ready=ready), tempfile.TemporaryDirectory() as directory:
                transport = client({'ok': True, 'retention_status': backend_status()}) if ready else None
                target = Path(directory) / 'diagnostics' / 'report.json'
                output = io.StringIO()
                with patch('photobooth.retention_readiness.AppsScriptDriveClient.from_configuration',
                           return_value=transport), contextlib.redirect_stdout(output):
                    result = main(['--output', str(target)])
                self.assertEqual(result, 0 if ready else 1)
                report = json.loads(target.read_text())
                self.assertEqual(report['kind'], 'drive-retention-readiness')
                self.assertEqual(report['drive_retention']['state'], 'READY' if ready else 'NOT_CONFIGURED')
                self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ['diagnostics'])
                self.assertNotIn('private-', target.read_text() + output.getvalue())
                self.assertIn('NOT VERIFIED', output.getvalue())
