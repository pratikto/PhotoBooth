"""Trusted assembly of the post-preview Sandbox backend, separate from the GUI.

Constructing this factory opens no listener and makes no provider/Drive request.
The launcher must supply its original private checkout, connected worker bridge
and read-only Drive probe inside the backend child process. Native admission,
paid delivery/claim/release and production are not enabled by this assembly.
"""
from photobooth.booth_auth import BoothAuthenticator
from photobooth.credential_vault import WindowsDPAPIProtector, platform_protector
from photobooth.midtrans_sandbox import MidtransSandboxClient
from photobooth.post_preview_api import create_app
from photobooth.post_preview_ccp import OriginalCCPService
from photobooth.post_preview_checkout import PrivateDraftCheckout
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_readiness import ReadOnlyDriveReadiness
from photobooth.post_preview_readiness_bridge import BackendChargeReadiness, WorkerReadinessClient
from photobooth.post_preview_store import DraftHeld, DraftLease


def build_sandbox_app(checkout, templates, bridge, drive_probe, *, merchant_id,
                      server_key, booth_id, booth_token, provider_transport=None,
                      on_shutdown=None, background_worker=True):
    """Install server-owned authority; never accept readiness/PAID from callers.

    The original ledger remains owned by the backend host. On successful assembly
    the API lifespan owns bridge shutdown; its caller's optional shutdown callback
    may then close the ledger. Failed assembly leaves caller resources intact.
    provider_transport is trusted dependency injection for offline HTTP tests.
    """
    if (type(checkout) is not PrivateDraftCheckout
            or type(bridge) is not WorkerReadinessClient
            or type(drive_probe) is not ReadOnlyDriveReadiness
            or drive_probe.workspace.physical_id != booth_id
            or type(background_worker) is not bool
            or on_shutdown is not None and not callable(on_shutdown)):
        raise ValueError('Original isolated backend dependencies required')
    if (not isinstance(server_key, str) or not server_key.strip() or len(server_key) > 512
            or not isinstance(booth_token, str) or not 32 <= len(booth_token) <= 512
            or booth_token != booth_token.strip()):
        raise ValueError('Sandbox backend credentials required')
    auth = BoothAuthenticator({booth_id: booth_token})
    # Missing/unsupported OS custody fails before constructing provider authority.
    protector = platform_protector()
    if type(protector) is not WindowsDPAPIProtector:
        raise ValueError('Supported original OS credential protection required')
    ledger = checkout.ledger
    with ledger.write():
        foreign = (ledger.db.execute('SELECT 1 FROM pp_drafts WHERE booth_id!=? LIMIT 1',
                                     (booth_id,)).fetchone()
            or ledger.db.execute('''SELECT 1 FROM pp_purchase_finance
                WHERE merchant_id!=? OR provider_mode!='sandbox' LIMIT 1''', (merchant_id,)).fetchone()
            or ledger.db.execute('''SELECT 1 FROM pp_ccp_credentials WHERE booth_id!=?
                OR merchant_id!=? OR protector_id!=? LIMIT 1''',
                (booth_id, merchant_id, protector.protector_id)).fetchone())
        if foreign:
            raise DraftHeld('Original isolated merchant/booth/protected Sandbox ledger required')
    credentials = OriginalCCPService(ledger, protector, merchant_id)
    readiness = BackendChargeReadiness(checkout, templates, bridge, drive_probe=drive_probe)

    def charge_readiness(group):
        # Validate the SAME original protected credential, without minting a new
        # render permit or treating this backend check as a customer offer.
        with ledger.write():
            row = ledger.db.execute('''SELECT i.draft_id,d.visit_id,d.generation
                FROM pp_checkout_intents i JOIN pp_drafts d ON d.draft_id=i.draft_id
                WHERE i.purchase_group_id=? AND d.booth_id=?''', (group, booth_id)).fetchone()
            if not row:
                raise DraftHeld('Original booth checkout required')
            lease = DraftLease(row['draft_id'], booth_id, row['visit_id'], row['generation'])
        credentials.validate_escrow(lease)
        return readiness(group)

    provider = MidtransSandboxClient(server_key, transport=provider_transport)
    payments = PostPreviewPayments(ledger, provider, merchant_id,
                                   readiness=charge_readiness, server_key=server_key)

    def close():
        bridge.close()
        if on_shutdown is not None:
            on_shutdown()

    return create_app(payments, auth, on_shutdown=close, background_worker=background_worker)
