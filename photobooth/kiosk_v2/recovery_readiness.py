"""AR-08 bounded, offline readiness gate before native Sandbox order creation."""
import math
import os
from pathlib import Path
import tempfile
import time

from photobooth.booth_storage import checked_path
from photobooth.device_health import check_disk, READY
from photobooth.fulfillment_contract import frozen_contract
from photobooth.capture_journal import validate_image


def prepayment_readiness(root, templates, quantities, camera_valid, observed_at, *,
                         now=time.monotonic, delivery_enabled=False):
    # AsyncCamera.read already rejects frames older than one second. The UI
    # supplies only a boolean observation, never a customer frame to this worker.
    current=now()
    if (camera_valid is not True or type(observed_at) not in (int,float)
            or not math.isfinite(observed_at) or not 0 <= current-observed_at <= 2
            or delivery_enabled):
        raise RuntimeError('Fresh camera observation and isolated Sandbox required')
    try:
        root=checked_path(Path(root))
        if check_disk(root).status != READY:
            raise RuntimeError('Photo storage capacity not ready')
        contract=frozen_contract(quantities,templates=templates)
        if {t['template_id'] for t in contract['templates']} != set(quantities):
            raise RuntimeError('Selected template unavailable')
        selected={t.template_id:t for t in templates if t.template_id in quantities}
        for record in contract['templates']:
            template=selected[record['template_id']]
            validate_image(template.artwork_path,record['artwork_sha256'])
            for aperture,frozen in zip(template.apertures,record['apertures']):
                validate_image(aperture.mask_path,frozen['mask_sha256'])
        root.mkdir(parents=True,exist_ok=True)
        # Delete only our own exclusive synthetic probe, never scan or remove
        # existing transaction files. NamedTemporaryFile is portable to Windows.
        with tempfile.NamedTemporaryFile(prefix='.meong-readiness-',dir=root) as probe:
            probe.write(b'MEONG SYNTHETIC READINESS\n');probe.flush();os.fsync(probe.fileno())
        if not 0 <= now()-observed_at <= 2:
            raise RuntimeError('Camera observation expired during readiness checks')
    except (OSError,ValueError,KeyError,TypeError) as error:
        raise RuntimeError('Photo readiness requires attention') from error
    return {'ready':True,'checked_at':now(),'delivery':'SANDBOX_OFF'}
