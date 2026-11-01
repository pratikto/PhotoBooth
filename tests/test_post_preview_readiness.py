"""Fresh backend evidence and immutable private bytes; no external services."""
from dataclasses import replace
import hashlib
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

from photobooth.post_preview_checkout import PrivateDraftCheckout
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_readiness import (
    CheckObservation, LocalChargeReadiness, ReadinessScope, TrustedChargeReadiness, REQUIRED_CHECKS,
)
from photobooth.post_preview_store import DraftHeld
from tests import test_post_preview_payments as payment_fixtures


class TrustedReadinessTests(unittest.TestCase):
    def setUp(self):
        self.fixture = payment_fixtures.PostPreviewPaymentTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.service, self.ledger = self.fixture.service, self.fixture.ledger
        self.lease, self.group = self.fixture.lease, self.fixture.group
        self.clock = self.fixture.fixture.clock
        self.intent = self.fixture.fixture.intent
        self.scope = ReadinessScope(self.group, self.lease.booth_id,
                                   self.intent['contract_sha256'], self.lease.generation)
        self.probes = {name: lambda scope: CheckObservation('READY', self.clock[0])
                       for name in REQUIRED_CHECKS}

    def observe(self):
        return TrustedChargeReadiness.observe(self.scope, self.probes)

    def require(self, report):
        report.require(self.scope, now=self.clock[0])

    def test_missing_unknown_false_client_boolean_and_failed_probes_hold(self):
        for name in REQUIRED_CHECKS:
            original = self.probes.pop(name)
            with self.subTest(name=name), self.assertRaises(DraftHeld): self.require(self.observe())
            self.probes[name] = original
        for value in (True, {'ready': True}, CheckObservation('UNKNOWN', None),
                      CheckObservation('NOT_READY', self.clock[0])):
            self.probes['drive_sharing'] = lambda _: value
            with self.subTest(kind=type(value).__name__), self.assertRaises(DraftHeld): self.require(self.observe())
        def failed(_): raise OSError('private driver detail')
        self.probes['drive_sharing'] = failed
        report = self.observe()
        with self.assertRaises(DraftHeld): self.require(report)
        self.assertNotIn('private driver detail', repr(report))

    def test_original_scope_and_freshness_are_rechecked_at_admission(self):
        report = self.observe()
        self.require(report)
        for scope in (replace(self.scope, purchase_group_id='another'),
                      replace(self.scope, booth_id='PB002'),
                      replace(self.scope, contract_sha256='0'*64),
                      replace(self.scope, generation=2)):
            with self.subTest(scope=scope), self.assertRaises(DraftHeld):
                report.require(scope, now=self.clock[0])
        self.clock[0] += 3
        with self.assertRaises(DraftHeld): self.require(report)

    def test_stale_is_distinct_from_unknown_and_clock_rollback(self):
        old = CheckObservation('READY', self.clock[0]-3)
        self.assertEqual('STALE', old.state_at(self.clock[0], max_age=2))
        self.assertEqual('UNKNOWN', CheckObservation('UNKNOWN', None).state_at(self.clock[0], max_age=2))
        self.assertEqual('UNKNOWN', CheckObservation('READY', self.clock[0]+1).state_at(self.clock[0], max_age=2))
        for bad in (True, float('nan'), float('inf')):
            self.assertEqual('UNKNOWN', CheckObservation('READY', bad).state_at(self.clock[0], max_age=2))

    def test_cached_server_report_cannot_charge_when_stale_or_for_other_group(self):
        self.fixture.offered()
        report = self.observe()
        self.service.readiness = lambda _: report
        self.clock[0] += 3
        with self.assertRaises(DraftHeld): self.service.begin(self.lease)
        self.assertEqual(0, self.fixture.provider.charges)
        self.service.readiness = lambda _: self.observe()
        self.service.begin(self.lease)
        self.assertEqual(1, self.fixture.provider.charges)

    def test_original_prepared_restart_requires_new_independent_readiness(self):
        self.fixture.offered()
        self.service._prepare(self.lease, observation=self.fixture.ready)
        original = self.service.inspect(self.group, 'PB001')['attempts']
        self.fixture.ready = replace(self.fixture.ready, drive_sharing=False)
        with self.assertRaises(DraftHeld): self.service.begin(self.lease)
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertEqual(original, self.service.inspect(self.group, 'PB001')['attempts'])

    def test_sent_original_reconciles_even_when_all_current_readiness_is_unknown(self):
        self.fixture.begin()
        self.service.readiness = lambda _: self.fail('Reconciliation must not require new-charge readiness')
        self.service.begin(self.lease)
        self.assertEqual(1, self.fixture.provider.charges)

    def test_sandbox_rejects_untimestamped_fixture_flags_before_any_provider_io(self):
        from photobooth.midtrans_sandbox import MidtransSandboxClient
        from photobooth.post_preview_payments import PostPreviewPayments
        def forbidden(*args, **kwargs): self.fail('No merchant request is permitted')
        service = PostPreviewPayments(self.ledger, MidtransSandboxClient('SYNTHETIC', transport=forbidden),
                                     'MTEST', readiness=lambda _: self.fixture.ready)
        self.fixture.offered()
        with self.assertRaises(DraftHeld): service.begin(self.lease)
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_payment_attempts').fetchone()[0])

    def test_expiry_between_prepare_and_send_holds_same_original_attempt_for_retry(self):
        self.fixture.offered()
        self.service.readiness = lambda _: self.observe()
        prepare = self.service._prepare
        def delayed(*args, **kwargs):
            result = prepare(*args, **kwargs)
            self.clock[0] += 3
            return result
        with patch.object(self.service, '_prepare', side_effect=delayed), self.assertRaises(DraftHeld):
            self.service.begin(self.lease)
        original = self.service.inspect(self.group, 'PB001')['attempts']
        self.assertEqual('PREPARED', original[0]['create_phase'])
        self.assertEqual(0, self.fixture.provider.charges)
        result = self.service.begin(self.lease)
        self.assertEqual(original[0]['attempt_id'], result['attempts'][0]['attempt_id'])
        self.assertEqual(1, self.fixture.provider.charges)

    def test_frozen_purchase_verification_is_read_only_and_binds_exact_bytes(self):
        from photobooth.catalog import get_templates
        photos = PrivateDraftPhotos(self.ledger, self.fixture.fixture.root/'private')
        checkout = PrivateDraftCheckout(photos)
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in photos.root.rglob('*') if p.is_file()}
        self.assertEqual(self.scope, checkout.verify_frozen(self.group, get_templates()))
        after = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in photos.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(0, self.fixture.provider.charges)

    def test_frozen_media_corruption_is_not_repaired_or_reapproved(self):
        from photobooth.catalog import get_templates
        photos = PrivateDraftPhotos(self.ledger, self.fixture.fixture.root/'private')
        checkout = PrivateDraftCheckout(photos)
        image = next(photos.root.rglob('photo_01.jpg'))
        image.write_bytes(b'corrupt synthetic media')
        with self.assertRaises((DraftHeld, ValueError, RuntimeError)):
            checkout.verify_frozen(self.group, get_templates())
        self.assertEqual(b'corrupt synthetic media', image.read_bytes())
        self.assertEqual(0, self.fixture.provider.charges)

    def test_missing_media_never_allocates_a_replacement_lineage(self):
        from photobooth.catalog import get_templates
        photos = PrivateDraftPhotos(self.ledger, self.fixture.fixture.root/'private')
        checkout = PrivateDraftCheckout(photos)
        manifest = next(photos.root.rglob('manifest.json'))
        original = manifest.read_bytes()
        manifest.unlink()
        with self.assertRaises((DraftHeld, ValueError, RuntimeError)):
            checkout.verify_frozen(self.group, get_templates())
        self.assertFalse(manifest.exists())
        self.assertTrue(original)

    def test_frozen_artwork_change_is_held_without_touching_original_assets(self):
        from photobooth.catalog import get_templates
        templates = get_templates()
        original = templates[0]
        artwork = self.fixture.fixture.root/'synthetic-artwork.png'
        artwork.write_bytes(original.artwork_path.read_bytes())
        replacement = replace(original, artwork_path=artwork)
        checkout = PrivateDraftCheckout(PrivateDraftPhotos(self.ledger, self.fixture.fixture.root/'private'))
        self.assertEqual(self.scope, checkout.verify_frozen(self.group, [replacement]))
        artwork.write_bytes(b'corrupt synthetic artwork')
        with self.assertRaises((DraftHeld, ValueError, RuntimeError)):
            checkout.verify_frozen(self.group, [replacement])

    def test_actual_local_media_disk_camera_and_route_recheck_before_charge(self):
        from photobooth.catalog import get_templates
        from photobooth.printer import PrinterConfig
        photos = PrivateDraftPhotos(self.ledger, self.fixture.fixture.root/'private')
        camera = Mock()
        camera.capture.isOpened.return_value = True
        camera.read.return_value = object()
        external = {name: probe for name, probe in self.probes.items()
                    if name not in LocalChargeReadiness.LOCAL_CHECKS}
        adapter = LocalChargeReadiness(PrivateDraftCheckout(photos), get_templates(),
                    probes=external, camera=camera, printer_config=PrinterConfig(lan_host='synthetic-fixture'))
        self.service.readiness = adapter
        self.fixture.offered()
        before = {p: p.read_bytes() for p in photos.root.rglob('*') if p.is_file()}
        with patch('photobooth.device_health._network_dial') as dial:
            self.service.begin(self.lease)
            dial.assert_called_once()
        camera.capture.isOpened.assert_called_once()
        camera.read.assert_called_once()
        self.assertEqual(before, {p: p.read_bytes() for p in photos.root.rglob('*') if p.is_file()})
        self.assertEqual(1, self.fixture.provider.charges)

    def test_local_adapter_missing_external_services_stays_unknown_and_holds(self):
        from photobooth.catalog import get_templates
        checkout = PrivateDraftCheckout(PrivateDraftPhotos(self.ledger, self.fixture.fixture.root/'private'))
        report = LocalChargeReadiness(checkout, get_templates())(self.group)
        states = {name: signal.state_at(self.clock[0], max_age=2) for name, signal in report.observations}
        self.assertEqual('READY', states['media'])
        self.assertEqual('READY', states['disk'])
        for name in ('camera', 'printer_route', 'payment_authorization', 'drive_api',
                     'drive_sharing', 'unclaimed_ready_capacity', 'worker_ownership'):
            self.assertEqual('UNKNOWN', states[name])
        with self.assertRaises(DraftHeld): self.require(report)

    def test_disk_reserve_and_fsync_failure_prevent_attempt_and_preserve_private_bytes(self):
        from photobooth.catalog import get_templates
        photos = PrivateDraftPhotos(self.ledger, self.fixture.fixture.root/'private')
        self.service.readiness = LocalChargeReadiness(PrivateDraftCheckout(photos), get_templates())
        self.fixture.offered()
        before = {p: p.read_bytes() for p in photos.root.rglob('*') if p.is_file()}
        with patch('photobooth.post_preview_resources.shutil.disk_usage', return_value=SimpleNamespace(free=0)), \
                self.assertRaises(DraftHeld):
            self.service.begin(self.lease)
        with patch('photobooth.post_preview_resources.os.fsync', side_effect=OSError('synthetic fsync failure')), \
                self.assertRaises(OSError):
            self.service.begin(self.lease)
        self.assertEqual(before, {p: p.read_bytes() for p in photos.root.rglob('*') if p.is_file()})
        self.assertEqual(0, self.fixture.provider.charges)
        self.assertEqual(0, self.ledger.db.execute('SELECT count(*) FROM pp_payment_attempts').fetchone()[0])

    def test_read_only_check_never_repairs_an_unresolved_capture_journal(self):
        import json
        from photobooth.catalog import get_templates
        photos = PrivateDraftPhotos(self.ledger, self.fixture.fixture.root/'private')
        manifest = next(photos.root.rglob('manifest.json'))
        data = json.loads(manifest.read_text())
        next(iter(data['capture_intents'].values()))['state'] = 'STAGED'
        manifest.write_text(json.dumps(data))
        before = manifest.read_bytes()
        with self.assertRaises((DraftHeld, ValueError, RuntimeError)):
            PrivateDraftCheckout(photos).verify_frozen(self.group, get_templates())
        self.assertEqual(before, manifest.read_bytes())


if __name__ == '__main__': unittest.main()
