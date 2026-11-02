"""Opt-in Meong real-camera, optional real-printer *synthetic payment* pilot."""
import argparse
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def build_parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--private-root',type=Path,required=True,
                   help='New dedicated, unoccupied local test folder')
    p.add_argument('--synthetic-payment-only',action='store_true',required=True,
                   help='Mandatory opt-in: NO live Midtrans or downloadable Drive folder')
    p.add_argument('--enable-real-printer',action='store_true',
                   help='Opt-in physical printer, consumes real paper')
    p.add_argument('--accept-real-paper',action='store_true',
                   help='Second confirmation required for physical output')
    p.add_argument('--enable-real-drive',action='store_true',
                   help='Connect existing deployed Apps Script and upload test photographs')
    p.add_argument('--accept-public-test-upload',action='store_true',
                   help='Explicitly allow own test photos to be shared in real Drive folder')
    return p


def validate_private_root(selected, *, project_root=ROOT):
    """Reject every reused/personal/occupied test folder before camera or I/O.

    A prior paid fixture may contain encrypted original credentials, owed
    service and immutable print jobs. It must NEVER be reopened as a new
    customer's pilot or reset to make the welcome page work.
    """
    path=Path(selected).expanduser()
    # A parent symlink is as unsafe as a symlink at the selected leaf:
    # resolving it could redirect a "fresh" test into unrelated storage.
    candidate=path.absolute()
    if any(parent.is_symlink() for parent in (candidate, *candidate.parents)):
        raise ValueError('Pilot private root or ancestor must not be a symlink')
    root=path.resolve()
    project=Path(project_root).resolve()
    if (root==project or root in project.parents or root==Path.home().resolve()
            or root==root.parent or any(part.casefold()=='old' for part in root.parts)):
        raise ValueError('Select a dedicated new pilot root, never an archive or parent directory')
    if root.exists():
        if not root.is_dir() or any(root.iterdir()):
            raise ValueError('Pilot root is already occupied: choose a new empty folder')
    return root


def validate_printer(args,env):
    if args.enable_real_printer!=args.accept_real_paper:
        raise ValueError('Both --enable-real-printer and --accept-real-paper are required')
    if args.enable_real_printer and not any(env.get(k) for k in (
            'PHOTOBOOTH_PRINTER_LAN_HOST','PHOTOBOOTH_PRINTER_WIFI_HOST',
            'PHOTOBOOTH_PRINTER_WINDOWS_NAME','PHOTOBOOTH_PRINTER_USB_VENDOR_ID')):
        raise ValueError('Explicit POS80 network/Windows/USB settings are required')



def validate_drive(args,env):
    if args.enable_real_drive!=args.accept_public_test_upload:
        raise ValueError('Both --enable-real-drive and --accept-public-test-upload are required')
    if not args.enable_real_drive:
        return
    from urllib.parse import urlparse
    url=env.get('PHOTOBOOTH_WEB_APP_URL','')
    token=env.get('PHOTOBOOTH_UPLOAD_TOKEN','')
    parsed=urlparse(url)
    if (parsed.scheme!='https' or parsed.netloc!='script.google.com'
            or not parsed.path.startswith('/macros/s/') or
            not parsed.path.endswith('/exec') or not token
            or 'PASTE_' in token):
        raise ValueError('Explicit deployed Apps Script WEB_APP_URL and UPLOAD_TOKEN required')

def main(argv=None):
    p=build_parser()
    args=p.parse_args(argv)
    try:
        validate_printer(args,os.environ)
        validate_drive(args,os.environ)
    except ValueError as e:p.error(str(e))
    if any(os.environ.get(k)=='1' for k in (
            'PHOTOBOOTH_V2_CHECKOUT_SANDBOX','PHOTOBOOTH_V2_CHECKOUT_MOCK',
            'PHOTOBOOTH_V2_PRINT','PHOTOBOOTH_V2_DRIVE')):
        p.error('Disable all merchant/paid-first/Drive launch profiles')
    # Reject unsafe or reused data roots before importing the Kivy runtime.
    # Neither a camera nor a printer/cloud fixture can be initialized here.
    try:
        root=validate_private_root(args.private_root)
    except ValueError as error:
        p.error(str(error))
    os.environ.setdefault('KIVY_NO_ARGS','1')
    os.environ.setdefault('KIVY_LOG_MODE','MIXED')
    from photobooth.kiosk_v2.recovery import LaunchLease
    from tools.run_portrait_v2 import configure_kivy
    from kivy.config import Config
    from tests.post_preview_checkout_fixture import CheckoutFixture
    from photobooth.kiosk_v2.post_preview_checkout_app import PrivateCheckoutFixtureApp
    try: launch=LaunchLease(ROOT)
    except (OSError,ValueError):
        print('Startup blocked: another kiosk is active.',file=sys.stderr)
        return 2
    with launch:
        configure_kivy(Config)
        fixture=CheckoutFixture(root)
        fixture.enable_paid_ticket()
        if args.enable_real_drive:
            from photobooth.drive_storage import AppsScriptDriveClient
            from photobooth.booth_sync import BoothDriveClient
            existing=AppsScriptDriveClient(
                os.environ['PHOTOBOOTH_WEB_APP_URL'],
                os.environ['PHOTOBOOTH_UPLOAD_TOKEN'])
            fixture.drive=BoothDriveClient(existing,fixture.workspace.booth_id)
        fixture.enable_paid_delivery(real_drive=args.enable_real_drive)
        if args.enable_real_drive:
            # Prepare the original READY reserve pool ahead of PAID, but the
            # existing backend readiness will still fail closed until the
            # remote script independently confirms folder sharing.
            fixture.paid_monitor.worker.start()
        if args.enable_real_printer:
            from photobooth.printer import ThermalPrinter,PrinterConfig
            device=ThermalPrinter(PrinterConfig.from_environment())
            fixture.service._receipt_printer=device
            fixture.service._paid_printer=device
            print('REAL POS80 output enabled. Inspect the printer before a second pilot.')
        else:
            print('VIRTUAL printer only, no paper used.')
        print('PAYMENT IS SYNTHETIC: no real Midtrans transaction.')
        print('REAL DRIVE TEST PHOTO UPLOAD ENABLED.' if args.enable_real_drive
              else 'DRIVE URL IS A NONDOWNLOADABLE SYNTHETIC FIXTURE.')
        def mark_synthetic_paid(payment):
            attempts=payment.get('attempts',[])
            if not attempts:raise ValueError('No original synthetic order')
            fixture.provider.state(attempts[-1]['provider_order_id'],'settlement')
        class BoundPilotApp(PrivateCheckoutFixtureApp):
            def build(self):
                stage=super().build()
                # This must run at native build, not against fixture camera
                # and worker objects before the real App constructs its owner.
                fixture.bind_app(self)
                from photobooth.post_preview_isolation import OriginalMockIsolation
                from photobooth.post_preview_claim import OriginalMockClaim
                from photobooth.post_preview_ccp import OriginalCCPService
                from photobooth.post_preview_ticket import OriginalRecoveryTicketService
                from photobooth.post_preview_pilot_admission import OriginalPilotAdmission
                isolation=OriginalMockIsolation(
                    fixture.service.ledger,fixture.backend,self._photo_jobs,
                    fixture.launch_lease,printer_lane=fixture.service._receipt_lane,
                    delivery=fixture.paid_monitor,allow_incomplete_fixture=True)
                claim=OriginalMockClaim(
                    fixture.backend,
                    OriginalCCPService(fixture.service.ledger,fixture.protector,'MTEST',
                                       allow_synthetic=True),
                    OriginalRecoveryTicketService(fixture.backend,fixture.protector,
                                                  allow_synthetic=True),
                    allow_incomplete_fixture=True)
                self.attach_synthetic_pilot_admission(
                    OriginalPilotAdmission(isolation,claim,allow_synthetic_pilot=True))
                return stage

        app=BoundPilotApp(
            root,private_service=fixture.service,
            synthetic_pay_callback=mark_synthetic_paid)
        try:app.run()
        finally:
            if getattr(app,'_photo_jobs',None):
                app._photo_jobs.close()
                app._photo_jobs.wait_closed(10)
            if getattr(app,'camera_device',None):
                app.camera_device.close()
                app.camera_device.wait_closed(10)
            fixture.close()
    return 0


if __name__=='__main__':sys.exit(main())
