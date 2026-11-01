"""Read-only Drive protocol fixtures; no Google account or customer media."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from photobooth.booth_storage import BoothWorkspace
from photobooth.booth_sync import BoothDriveClient
from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError
from photobooth.post_preview_readiness import (CheckObservation, LocalChargeReadiness,
                                             ReadinessScope, ReadOnlyDriveReadiness)


class ReadOnlyDriveReadinessTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock()
        self.session.post.return_value.status_code = 200
        existing = AppsScriptDriveClient('https://script.google.com/macros/s/SYNTHETIC/exec',
                                        'synthetic-not-deployed', session=self.session)
        self.client = BoothDriveClient(existing, 'PB001V2S2')
        self.slot = {'transaction_id': 'PB001V2S2_00000001', 'claim_token': 'a'*32}
        self.status = dict(protocol_version=1, booth_id='PB001V2S2', read_only=True,
                           drive_api='READY', drive_sharing='READY', capacity_state='READY',
                           ready_count=1, checked_count=1)
        self.respond(self.status)

    def respond(self, status):
        self.session.post.return_value.json.return_value = dict(ok=True, storage_layout=2, readiness=status)

    def test_client_requests_only_exact_readiness_and_filters_response_fields(self):
        self.respond(dict(self.status, private_account='must-not-export'))
        result = self.client.storage_readiness([dict(self.slot, folder_url='must-not-send')])
        body = self.session.post.call_args.kwargs['json']
        self.assertEqual('storage_readiness', body['action'])
        self.assertEqual('PB001V2S2', body['booth_id'])
        self.assertEqual(2, body['storage_layout'])
        self.assertEqual([self.slot], body['slots'])
        self.assertEqual(self.status, result)

    def test_malformed_scope_capacity_and_fake_success_are_rejected(self):
        for changes in ({'protocol_version': True}, {'booth_id': 'PB002V2S2'}, {'read_only': False},
                        {'ready_count': True}, {'ready_count': 2}, {'checked_count': 2},
                        {'drive_api': 'UNKNOWN'}, {'drive_sharing': 'UNKNOWN'},
                        {'capacity_state': 'NOT_READY'}, {'drive_api': True}):
            self.respond(dict(self.status, **changes))
            with self.subTest(changes=changes), self.assertRaises(DriveApiError):
                self.client.storage_readiness([self.slot])

    def test_duplicate_foreign_and_oversized_candidates_fail_before_network(self):
        for slots in ([self.slot]*2, [self.slot]*101,
                      [dict(self.slot, transaction_id='PB002V2S2_00000001')],
                      [dict(self.slot, claim_token='bad')]):
            with self.assertRaises(ValueError): self.client.storage_readiness(slots)
        self.session.post.assert_not_called()

    def test_nonconsuming_workspace_probe_preserves_original_pool_counter_and_empty_slots(self):
        with TemporaryDirectory() as folder:
            workspace = BoothWorkspace(Path(folder)/'Photobooth', 'PB001V2S2')
            workspace.prepare()
            before = workspace.state_path.read_bytes(), workspace.counter_path.read_bytes()
            self.status.update(ready_count=25, checked_count=25)
            self.respond(self.status)
            probe = ReadOnlyDriveReadiness(self.client, workspace, now=lambda: 1000.0)
            scope = ReadinessScope('group', 'PB001', 'a'*64, 1)
            signals = probe.observe(scope)
            self.assertEqual({'drive_api', 'drive_sharing', 'unclaimed_ready_capacity'}, set(signals))
            self.assertTrue(all(s.state_at(1000, max_age=2) == 'READY' for s in signals.values()))
            self.assertEqual(before, (workspace.state_path.read_bytes(), workspace.counter_path.read_bytes()))
            self.assertEqual(25, len(workspace.ready_slots()))
            self.assertTrue(all(not any((workspace.root/s['transaction_id']).iterdir()) for s in workspace.ready_slots()))
            self.assertEqual(1, self.session.post.call_count)

    def test_missing_deployment_wrong_booth_and_provider_outage_stay_unknown(self):
        with TemporaryDirectory() as folder:
            workspace = BoothWorkspace(folder, 'PB001V2S2')
            workspace.prepare()
            probe = ReadOnlyDriveReadiness(self.client, workspace, now=lambda: 1000.0)
            scope = ReadinessScope('group', 'PB002', 'a'*64, 1)
            self.assertTrue(all(s.state == 'UNKNOWN' for s in probe.observe(scope).values()))
            self.session.post.assert_not_called()
            self.session.post.side_effect = OSError('private-account-token')
            signals = probe.observe(ReadinessScope('group', 'PB001', 'a'*64, 1))
            self.assertTrue(all(s.state == 'UNKNOWN' for s in signals.values()))
            self.assertNotIn('private-account-token', repr(signals))

    def test_slow_response_cannot_refresh_its_original_observation_time(self):
        with TemporaryDirectory() as folder:
            workspace = BoothWorkspace(folder, 'PB001V2S2'); workspace.prepare()
            self.status.update(ready_count=25, checked_count=25)
            clock = [1000.0]
            def delayed():
                clock[0] += 3
                return dict(ok=True, storage_layout=2, readiness=self.status)
            self.session.post.return_value.json.side_effect = delayed
            signals = ReadOnlyDriveReadiness(self.client, workspace, now=lambda: clock[0]).observe(
                ReadinessScope('group', 'PB001', 'a'*64, 1))
            self.assertTrue(all(s.state_at(clock[0], max_age=2) == 'STALE' for s in signals.values()))

    def test_authenticated_backend_rechecks_real_read_only_adapter_before_attempt_and_safe_retry(self):
        from photobooth.catalog import get_templates
        from photobooth.post_preview_checkout import PrivateDraftCheckout
        from photobooth.post_preview_photos import PrivateDraftPhotos
        from photobooth.printer import PrinterConfig
        from tests import test_post_preview_api as api_fixtures
        api = api_fixtures.PostPreviewApiTests(); api.setUp()
        self.addCleanup(api.doCleanups)
        original = api.fixture.fixture
        workspace = BoothWorkspace(original.root/'workspace', 'PB001V2S2'); workspace.prepare()
        camera = Mock(); camera.capture.isOpened.return_value = True; camera.read.return_value = object()
        probes = {name: lambda scope: CheckObservation('READY', original.clock[0])
                  for name in ('payment_authorization', 'worker_ownership')}
        api.service.readiness = LocalChargeReadiness(
            PrivateDraftCheckout(PrivateDraftPhotos(api.ledger, original.root/'private')),
            get_templates(), probes=probes, camera=camera, printer_config=PrinterConfig(lan_host='synthetic'),
            drive_probe=ReadOnlyDriveReadiness(self.client, workspace, now=lambda: original.clock[0]))
        before = workspace.state_path.read_bytes(), workspace.counter_path.read_bytes()
        api.fixture.offered()
        self.respond(dict(self.status, drive_sharing='NOT_READY', capacity_state='UNKNOWN', ready_count=0))
        with patch('photobooth.device_health._network_dial'):
            self.assertEqual(409, api.post('begin').status_code)
            self.assertEqual(0, api.fixture.provider.charges)
            self.status.update(ready_count=25, checked_count=25)
            self.respond(self.status)
            self.assertEqual(200, api.post('begin').status_code)
        self.assertEqual(1, api.fixture.provider.charges)
        self.assertEqual(before, (workspace.state_path.read_bytes(), workspace.counter_path.read_bytes()))
        self.assertEqual(25, len(workspace.ready_slots()))


if __name__ == '__main__': unittest.main()
