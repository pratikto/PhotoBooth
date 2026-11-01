"""Fresh, original-scope backend observations; never client payment authority.

Probes are installed by the trusted backend, not deserialized from HTTP. Missing
or failed adapters stay UNKNOWN. Keeping a result cannot refresh its timestamp.
Two seconds is a conservative software pilot bound, not hardware acceptance.
"""
from dataclasses import dataclass
import math
import re

from photobooth.checkout_store import identifier
from photobooth.post_preview_store import DraftHeld


REQUIRED_CHECKS = frozenset({
    'camera', 'disk', 'media', 'artwork', 'printer_route', 'payment_authorization',
    'drive_api', 'drive_sharing', 'unclaimed_ready_capacity', 'worker_ownership',
})


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


@dataclass(frozen=True)
class ReadinessScope:
    purchase_group_id: str
    booth_id: str
    contract_sha256: str
    generation: int

    def __post_init__(self):
        identifier(self.purchase_group_id)
        identifier(self.booth_id)
        if (not isinstance(self.contract_sha256, str)
                or re.fullmatch(r'[a-f0-9]{64}', self.contract_sha256) is None
                or type(self.generation) is not int or self.generation < 1):
            raise ValueError('Original immutable readiness scope required')


@dataclass(frozen=True)
class CheckObservation:
    state: str
    observed_at: float | None

    def state_at(self, now, *, max_age):
        if (type(self.state) is not str or self.state not in {'READY', 'NOT_READY', 'UNKNOWN'}
                or not finite_number(now) or not finite_number(max_age) or not 0 < max_age <= 30
                or not finite_number(self.observed_at) or self.observed_at > now):
            return 'UNKNOWN'
        if now-self.observed_at > max_age:
            return 'STALE'
        return self.state


@dataclass(frozen=True)
class TrustedChargeReadiness:
    scope: ReadinessScope
    observations: tuple

    @classmethod
    def observe(cls, scope, probes):
        observations = []
        for name in sorted(REQUIRED_CHECKS):
            try:
                probe = probes.get(name)
                signal = probe(scope) if callable(probe) else None
            except Exception:
                signal = None
            if type(signal) is not CheckObservation:
                signal = CheckObservation('UNKNOWN', None)
            observations.append((name, signal))
        return cls(scope, tuple(observations))

    def require(self, scope, *, now, max_age=2):
        if type(self.scope) is not ReadinessScope or self.scope != scope:
            raise DraftHeld('Readiness belongs to another original purchase or worker')
        if (type(self.observations) is not tuple
                or len(self.observations) != len(REQUIRED_CHECKS)):
            raise DraftHeld('Complete independent readiness required')
        seen = set()
        for item in self.observations:
            if type(item) is not tuple or len(item) != 2:
                raise DraftHeld('Typed independent readiness required')
            name, signal = item
            if (type(name) is not str or name not in REQUIRED_CHECKS or name in seen or type(signal) is not CheckObservation
                    or signal.state_at(now, max_age=max_age) != 'READY'):
                raise DraftHeld('Fresh independent readiness is not established')
            seen.add(name)


class LocalChargeReadiness:
    """Trusted same-machine backend adapter over original media/device checks.

    External probes must independently observe authorized payment/Drive service,
    unclaimed remote capacity and original worker ownership. No configured probe
    means UNKNOWN; this adapter never calls reserve, bind, upload or print APIs.
    It does not implement remote media attestation for a hosted backend.
    """
    LOCAL_CHECKS = frozenset({'media', 'artwork', 'disk', 'camera', 'printer_route'})

    def __init__(self, checkout, templates, *, probes=None, camera=None, printer_config=None,
                 drive_probe=None):
        if self.LOCAL_CHECKS.intersection(probes or {}):
            raise ValueError('Local checks cannot be replaced by caller readiness flags')
        self.checkout, self.templates = checkout, tuple(templates)
        self.probes = dict(probes or {})
        self.camera, self.printer_config = camera, printer_config
        self.drive_probe = drive_probe

    def __call__(self, group):
        from photobooth.device_health import check_camera, check_printer
        from photobooth.booth_storage import checked_path
        ledger = self.checkout.ledger
        started = ledger.now()
        scope = self.checkout.verify_frozen(group, self.templates)
        with ledger.write():
            row = ledger.db.execute('SELECT draft_id FROM pp_checkout_intents WHERE purchase_group_id=?',
                                    (group,)).fetchone()
            if not row:
                raise DraftHeld('Original private storage required')
            private = checked_path(self.checkout.photos.root/row['draft_id'])
        # Only an exclusively created durability probe is written/removed. No
        # saved media, manifest, reserve, counter or payment journal is changed.
        self.checkout.photos.policy.inspect(private, probe=True)
        probes = dict(self.probes)
        if self.drive_probe is not None:
            for name, observation in self.drive_probe.observe(scope).items():
                if name not in {'drive_api', 'drive_sharing', 'unclaimed_ready_capacity'}:
                    raise ValueError('Drive readiness cannot replace other trusted checks')
                probes[name] = lambda _scope, value=observation: value
        for name in ('media', 'artwork', 'disk'):
            probes[name] = lambda _scope: CheckObservation('READY', started)

        def device(check, value):
            stamp = ledger.now()
            try:
                status = check(value).status
                state = ('READY' if status == 'ready' else 'NOT_READY'
                         if status in {'unavailable', 'warning'} else 'UNKNOWN')
                return CheckObservation(state, stamp)
            except Exception:
                return CheckObservation('UNKNOWN', None)

        probes['camera'] = lambda _scope: device(check_camera, self.camera)
        probes['printer_route'] = lambda _scope: device(check_printer, self.printer_config)
        return TrustedChargeReadiness.observe(scope, probes)


class ReadOnlyDriveReadiness:
    """One fresh authenticated layout-2 inspection, no folder consumption."""
    CHECKS = ('drive_api', 'drive_sharing', 'unclaimed_ready_capacity')

    def __init__(self, client, workspace, *, now):
        self.client, self.workspace, self.now = client, workspace, now

    def observe(self, scope):
        unknown = {name: CheckObservation('UNKNOWN', None) for name in self.CHECKS}
        try:
            if (scope.booth_id != self.workspace.physical_id
                    or self.client.booth_id != self.workspace.booth_id
                    or not self.workspace.state_path.is_file()):
                return unknown
            stamp = self.now()
            # Existing ready_slots reads original identities under the workspace
            # lock. It does not replenish, claim or change counter/pool state.
            status = self.client.storage_readiness(self.workspace.ready_slots())
            return {'drive_api': CheckObservation(status['drive_api'], stamp),
                    'drive_sharing': CheckObservation(status['drive_sharing'], stamp),
                    'unclaimed_ready_capacity': CheckObservation(status['capacity_state'], stamp)}
        except Exception:
            # Credentials/URLs and raw account failures never enter diagnostics.
            return unknown
