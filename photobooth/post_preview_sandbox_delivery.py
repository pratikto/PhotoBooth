"""Original protected Sandbox backend delivery core, not a native mode switch.

Construction performs no financial/Drive/device I/O and mounts no customer
route. Exact backend-owned components replace neither provider nor OS custody.
"""
from photobooth.booth_storage import BoothWorkspace
from photobooth.booth_sync import BoothDriveClient
from photobooth.credential_vault import WindowsDPAPIProtector
from photobooth.linux_credential_vault import LinuxSecretServiceProtector
from photobooth.midtrans_sandbox import MidtransSandboxClient
from photobooth.post_preview_checkout import PrivateDraftCheckout
from photobooth.post_preview_paid_drive import OriginalPaidDriveBinding
from photobooth.post_preview_payments import PostPreviewPayments
from photobooth.post_preview_readiness import ReadOnlyDriveReadiness
from photobooth.post_preview_store import DraftHeld
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_ticket_presentation import OriginalRecoveryPresentation


class OriginalSandboxPaidDriveBinding(OriginalPaidDriveBinding):
    """Reuse original paid files/folder authority under the protected backend."""
    def __init__(self,payments,checkout,drive_probe,presentation):
        if (type(payments) is not PostPreviewPayments
                or type(checkout) is not PrivateDraftCheckout
                or type(drive_probe) is not ReadOnlyDriveReadiness
                or type(drive_probe.workspace) is not BoothWorkspace
                or type(drive_probe.client) is not BoothDriveClient
                or type(presentation) is not OriginalRecoveryPresentation):
            raise DraftHeld('Exact original protected backend delivery dependencies required')
        self.presentation=presentation
        self._initialize(payments,checkout,drive_probe.workspace,drive_probe.client)
        self._backend_context()

    def _backend_context(self):
        ticket=self.presentation.credentials
        if (type(self.payments) is not PostPreviewPayments
                or type(self.checkout) is not PrivateDraftCheckout
                or type(ticket) is not OriginalRecoveryTicketService
                or self.payments.mode!='sandbox'
                or type(self.payments.provider) is not MidtransSandboxClient
                or ticket.payments is not self.payments
                or ticket.ledger is not self.ledger
                or self.checkout.ledger is not self.ledger
                or type(ticket.protector) not in {WindowsDPAPIProtector,LinuxSecretServiceProtector}
                or ticket.merchant_id!=self.payments.merchant_id):
            raise DraftHeld('Original Sandbox provider, protected ticket and ledger required')

    def _record(self,lease,group):
        self._backend_context()
        service,contract=super()._record(lease,group)
        row=self.ledger.db.execute('''SELECT screen_state,receipt_state FROM pp_ticket_presentations
            WHERE purchase_group_id=?''',(group,)).fetchone()
        if (not row or row['screen_state']!='DISMISSED'
                or row['receipt_state'] not in {'SUBMITTED','NOT_SENT'}):
            raise DraftHeld('Original ticket and receipt opportunity must finish safely')
        return service,contract

    def bind(self,lease,group,templates):
        with self._lock:
            with self.ledger.write():
                self._record(lease,group)
                _,finance=self.payments._group(group,lease.booth_id)
                attempt=finance['legitimate_paid_attempt']
                paid=self.ledger.db.execute('SELECT verified_at,last_provider_state FROM pp_payment_attempts WHERE attempt_id=?',
                                            (attempt,)).fetchone()
                # Reuse the ticket service's existing 30-second independent
                # settlement window; do not defeat the Sandbox polling floor
                # immediately after genuine PAID/early NEXT.
                recent=(paid['verified_at'] is not None and paid['last_provider_state']=='settlement'
                        and 0<=self.payments._now()-paid['verified_at']<=30)
            if not recent:
                verified=self.payments.reconcile(group,lease.booth_id,attempt_id=attempt,force=True)
                if not verified['fresh_checked'] or not verified['paid_verified']:
                    raise DraftHeld('Fresh independent original paid settlement required')
            return super().bind(lease,group,templates)

    def require_printer_lane(self,printer,lane):
        self._backend_context()
        if (printer is not self.presentation._printer
                or lane is not self.presentation._printer_lane):
            raise DraftHeld('Paid strips must share the original backend receipt printer lane')


def original_paid_core_allowed(binder,allow_incomplete_fixture):
    """Only the unchanged mock opt-in or exact protected backend chain."""
    if type(binder) is OriginalPaidDriveBinding:
        return allow_incomplete_fixture is True and binder.payments.mode=='mock'
    if type(binder) is OriginalSandboxPaidDriveBinding and allow_incomplete_fixture is False:
        binder._backend_context()
        return True
    return False
