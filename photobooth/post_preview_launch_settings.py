"""Trusted Windows-first protected configuration, never native/payment authority.

No device/network/native import or fresh legacy-history creation. Call only
after L1 acquires the same global owner as the original Windows launchers.
"""
from contextlib import closing
from dataclasses import dataclass,field
import os
from pathlib import Path
import secrets
import sqlite3

from photobooth.kiosk_v2.recovery import checked_path,review_recovery
from photobooth.post_preview_launch import ProtectedSandboxLaunch,ProtectedLaunchHeld


@dataclass(frozen=True,repr=False)
class ProtectedLaunchSettings:
    config: object=field(repr=False)
    printer_config: object=field(repr=False)
    legacy_path: Path=field(repr=False)

    def __repr__(self):
        return '<ProtectedLaunchSettings: private trusted Sandbox dependencies>'


def _configuration(owner,*,storage_root,booth_id):
    """Trusted local configuration only, not a history/admission assertion."""
    if (type(owner) is not ProtectedSandboxLaunch or owner._closed or owner._stopping
            or owner._started or owner._global.stream.closed):
        raise ProtectedLaunchHeld('Original active pre-device global owner required')
    try:
        from tools.run_qris_sandbox import local_sandbox_credentials,local_literal_fields
        from photobooth.post_preview_host import SandboxHostConfig
        from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment
        from photobooth.post_preview_worker_fence import WorkerFenceKey
        from photobooth.printer_settings import load_printer_config
        local=checked_path(owner.project_root/'photobooth'/'local_settings.py')
        def pair(names,reader):
            values=tuple(os.environ.get(name,'') for name in names)
            if any(values):
                if not all(values):raise ValueError
                return values
            return reader()
        merchant,key=pair(('MIDTRANS_MERCHANT_ID','MIDTRANS_SERVER_KEY'),
                          lambda:local_sandbox_credentials(local))
        drive_url,drive_token=pair(('PHOTOBOOTH_WEB_APP_URL','PHOTOBOOTH_UPLOAD_TOKEN'),
                                  lambda:local_literal_fields(local,('WEB_APP_URL','UPLOAD_TOKEN')))
        if 'PASTE_' in drive_url or 'PASTE_' in drive_token:raise ValueError
        config=SandboxHostConfig(storage_root,merchant,booth_id,key,secrets.token_urlsafe(36),
                                 drive_url,drive_token)
        printer=load_printer_config(checked_path(owner.project_root/'data'/'printer_settings.json'))
        # No implicit Linux /dev/usb/lp0 fallback in this Windows-first profile.
        if not (printer.windows_printer_name or printer.lan_host or printer.wifi_host
                or printer.usb_vendor_id is not None and printer.usb_product_id is not None):
            raise ValueError
        SandboxHostFulfillment(printer,WorkerFenceKey.create())  # Original strict pure validation.
        history=checked_path(owner.project_root/'data'/'kiosk-v2-sandbox'/merchant/booth_id/'orders.sqlite')
        return ProtectedLaunchSettings(config,printer,history)
    except Exception:
        raise ProtectedLaunchHeld('Protected settings/history held; verify original local configuration') from None


def load_settings(owner,*,storage_root,booth_id):
    """No fallback account mixing or original-history replacement on failure."""
    settings=_configuration(owner,storage_root=storage_root,booth_id=booth_id)
    try:
        from photobooth.post_preview_legacy_history import legacy_history_clear
        if review_recovery(owner.project_root)['status']!='CLEAR_FOR_MANUAL_START':raise ValueError
        # Never choose a convenient foreign/empty ledger instead of the exact
        # original Windows v2 merchant trial for THIS account and booth.
        history=settings.legacy_path
        if (owner.project_root/'data'/'post-preview-enrollment').exists():
            from photobooth.post_preview_enrollment import enrolled_history
            history=enrolled_history(owner,settings)
        for suffix in ('-wal','-shm'):checked_path(str(history)+suffix)
        with closing(sqlite3.connect(history.as_uri()+'?mode=ro',uri=True,timeout=.2)) as db:
            db.row_factory=sqlite3.Row
            db.execute('SELECT id,booth_id,checkout_key,state FROM checkouts LIMIT 0')
            if not legacy_history_clear(db,booth_id):raise ValueError
        # The older v1 trial is outside the original v2 review. Do not silently
        # replace/adopt that history until its separate reconciliation exists.
        older=checked_path(owner.project_root/'data'/'qris-sandbox-trial'/settings.config.merchant_id/booth_id)
        if older.exists():raise ValueError
        return ProtectedLaunchSettings(settings.config,settings.printer_config,history)
    except Exception:
        raise ProtectedLaunchHeld('Protected settings/history held; verify original local configuration') from None
