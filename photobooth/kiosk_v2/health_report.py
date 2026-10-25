"""Local diagnostic metadata only: never export device identities, keys or photos."""
from datetime import datetime, timezone
from pathlib import Path

from photobooth.manifest_io import write_json_atomic
from .readiness import inventory

NAMES = frozenset({'camera','printer','disk','network','media','heartbeat'})
STATES = frozenset({'ready','warning','unavailable','unknown'})


def safe_health_report(root, snapshot):
    if snapshot is None:
        raise ValueError('Run an operator observation first')
    report = inventory(root)
    report['report_kind'] = 'portrait-v2-operator-health'
    # Do not include driver messages, addresses, queue/serial names, raw logs,
    # QR/order references, journals or the original camera frame in a report.
    report['health'] = {
        'checked_at':datetime.fromisoformat(snapshot.checked_at).isoformat(),
        'checks':[{'name':check.name,'status':check.status if check.status in STATES else 'unknown'}
                  for check in snapshot.checks if check.name in NAMES],
        'scope':'manual read-only observations; no provider, Drive, paper or codec certification',
    }
    report['notes'] = [
        'Operator observed the existing camera mailbox; no competing camera was opened.',
        'Route/queue discovery sent no print payload; paper and motor status remain unknown.',
        'Connectivity is a bounded TCP observation, not a merchant/Drive check.',
        'No photos, raw logs, device identities, network addresses or secrets are exported.',
        'Primary display metadata may differ from the kiosk monitor; verify it manually.',
    ]
    return report


class HealthReportStore:
    def __init__(self, root):
        self.root = Path(root)

    def save(self, snapshot):
        report = safe_health_report(self.root, snapshot)
        name = 'device-health-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json'
        path = self.root/'data'/'diagnostics'/name
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(path, report)
        return {'file':name,'head':report['source']['head']}
