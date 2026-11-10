"""Stable, separately owned Sandbox host; no native/mock authority shortcuts.

Only a trusted backend process receives this private configuration. Construction
reopens the original ledger/media, not a replacement visitor or payment. This
module alone opens no listener and performs no provider/Drive/device operation.
"""
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import threading

from photobooth.booth_storage import BoothWorkspace, checked_path
from photobooth.booth_sync import BoothDriveClient
from photobooth.catalog import get_templates
from photobooth.drive_storage import AppsScriptDriveClient
from photobooth.kiosk_v2.recovery import LaunchLease
from photobooth.post_preview_checkout import PrivateDraftCheckout
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_readiness import ReadOnlyDriveReadiness
from photobooth.post_preview_readiness_bridge import WorkerReadinessClient
from photobooth.post_preview_server import build_sandbox_app
from photobooth.post_preview_store import ORDER_VERSION, PostPreviewStore
from photobooth.post_preview_host_fulfillment import SandboxHostFulfillment


@dataclass(frozen=True)
class SandboxHostConfig:
    storage_root: Path = field(repr=False)
    merchant_id: str
    booth_id: str
    server_key: str = field(repr=False)
    booth_token: str = field(repr=False)
    drive_url: str = field(repr=False)
    drive_token: str = field(repr=False)

    def __post_init__(self):
        # Reject identity/path substitution before creating any directories.
        if (type(self.merchant_id) is not str
                or re.fullmatch(r'[A-Za-z0-9_-]{1,64}', self.merchant_id) is None
                or self.merchant_id.casefold() == 'old'
                or type(self.booth_id) is not str
                or re.fullmatch(r'PB[0-9]{3,8}', self.booth_id) is None):
            raise ValueError('Original Sandbox merchant/booth identity required')
        root = Path(self.storage_root)
        if not root.is_absolute():
            raise ValueError('Explicit absolute Sandbox storage root required')
        object.__setattr__(self, 'storage_root', checked_path(root))
        if (type(self.server_key) is not str or len(self.server_key) > 512
                or re.fullmatch(r'(?:SB-)?Mid-server-[!-~]+', self.server_key) is None
                or type(self.booth_token) is not str
                or re.fullmatch(r'[!-~]{32,512}', self.booth_token) is None
                or type(self.drive_token) is not str
                or re.fullmatch(r'[!-~]{1,4096}', self.drive_token) is None
                or type(self.drive_url) is not str
                or re.fullmatch(r'https://script\.google\.com/macros/s/[A-Za-z0-9_-]{1,256}/exec',
                                self.drive_url) is None):
            raise ValueError('Private Sandbox backend configuration is invalid')

    @property
    def private_root(self):
        return checked_path(self.storage_root/'post-preview-sandbox'/self.merchant_id/self.booth_id)


def _original_context(root, config):
    """Persist no secret; a damaged/foreign original context is never replaced."""
    expected = {'version': 1, 'mode': 'sandbox', 'merchant_id': config.merchant_id,
                'booth_id': config.booth_id, 'order_version': ORDER_VERSION}
    path = checked_path(root/'host-context.json')
    try:
        with path.open('x', encoding='utf-8') as stream:
            json.dump(expected, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        with path.open('rb') as stream:
            raw = stream.read(4097)
        def unique(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise ValueError('Ambiguous original host context')
                value[key] = item
            return value
        saved = json.loads(raw, object_pairs_hook=unique) if len(raw) <= 4096 else None
        if (type(saved) is not dict or type(saved.get('version')) is not int
                or saved != expected):
            raise ValueError('Original Sandbox host context requires review')


class SandboxHostRuntime:
    """Own backend kernel lease until all original financial workers stop.

    The independent native worker/collector still needs its own fence/ACK.
    Closing this host never proves booth FREE, fulfilled or refunded.
    """
    def __init__(self, config, bridge, *, fulfillment=None):
        if (type(config) is not SandboxHostConfig or type(bridge) is not WorkerReadinessClient
                or fulfillment is not None and type(fulfillment) is not SandboxHostFulfillment):
            raise ValueError('Exact original host configuration and private bridge required')
        self._owner = self.ledger = self.drive = self.app = None
        self.bridge = bridge
        self._closed = False
        self.root = config.private_root
        try:
            self._owner = LaunchLease(self.root/'backend-owner')
            _original_context(self.root, config)
            self.ledger = PostPreviewStore(self.root/'drafts.sqlite3')
            self.checkout = PrivateDraftCheckout(PrivateDraftPhotos(self.ledger, self.root/'media'))
            self.templates = tuple(get_templates())
            workspace = BoothWorkspace(config.storage_root/'post-preview-sandbox'/config.merchant_id/'delivery',
                                       config.booth_id+'V2S2')
            self.drive = AppsScriptDriveClient(config.drive_url, config.drive_token)
            probe = ReadOnlyDriveReadiness(BoothDriveClient(self.drive, workspace.booth_id),
                                          workspace, now=self.ledger.now)
            delivery={}
            if fulfillment is not None:
                from photobooth.printer import ThermalPrinter
                delivery=dict(receipt_printer=ThermalPrinter(fulfillment.printer_config),
                    printer_lane=threading.Lock(),paid_delivery_enabled=True,
                    worker_fence_key=fulfillment.worker_key)
            self.app = build_sandbox_app(self.checkout, self.templates, bridge, probe,
                merchant_id=config.merchant_id, server_key=config.server_key,
                booth_id=config.booth_id, booth_token=config.booth_token,
                on_shutdown=self.close,**delivery)
        except BaseException:
            # Failed assembly has not started any worker or external effect.
            if self.drive is not None:
                self.drive.session.close()
            if self.ledger is not None:
                self.ledger.close()
            if self._owner is not None:
                self._owner.close()
            raise

    def close(self, *, timeout=0):
        if self._closed:
            return True
        delivery=getattr(self.app.state,'paid_delivery',None) if self.app is not None else None
        if delivery is not None and not delivery.stop(timeout=timeout):
            return False
        worker = self.app.state.lifecycle_worker if self.app is not None else None
        if worker is not None and not worker.stop(timeout=timeout):
            return False  # Retain the original DB/lock under unfinished I/O.
        self.bridge.close()
        if self.drive is not None:
            self.drive.session.close()
        self.ledger.close()
        self._owner.close()
        self._closed = True
        return True
