"""Explicit Windows-first protected post-preview Midtrans SANDBOX entry.

Old synthetic pilot/default main.py unchanged. No production payment endpoint.
Use the official Sandbox simulator, never a real banking/wallet transfer.
"""
import argparse
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--storage-root',type=Path,required=True)
    p.add_argument('--booth-id',default='PB001')
    p.add_argument('--size',choices=('452x900','800x1280'),default='452x900')
    p.add_argument('--camera-index',type=int,choices=range(33),default=0)
    p.add_argument('--check-only',action='store_true')
    p.add_argument('--setup-only',action='store_true')
    p.add_argument('--enroll-new-booth',action='store_true')
    p.add_argument('--sandbox-only',action='store_true')
    p.add_argument('--owned-acceptance-session')
    for flag in ('enable-real-printer','accept-real-paper','enable-real-drive','accept-public-test-upload'):
        p.add_argument('--'+flag,action='store_true')
    return p


def native_app(control,camera,private_root,size):
    # Validate accepted public binding BEFORE importing a native provider.
    from photobooth.post_preview_visit_control import VisitControl
    from photobooth.post_preview_launch import ProtectedLaunchHeld
    if type(control) is not VisitControl or control.busy or control.state!='READY' or control.binding is None:
        raise ProtectedLaunchHeld('Original accepted native binding required')
    os.environ.setdefault('KIVY_NO_ARGS','1');os.environ.setdefault('KIVY_LOG_MODE','MIXED')
    from tools.run_portrait_v2 import configure_kivy
    from kivy.config import Config
    configure_kivy(Config)
    width,height=size.split('x');Config.set('graphics','width',width);Config.set('graphics','height',height)
    from photobooth.kiosk_v2.post_preview_visits_app import ProtectedVisitsApp
    return ProtectedVisitsApp(private_root,visit_control=control,camera_device=camera)


def main(argv=None):
    args=parser().parse_args(argv)
    setup=args.setup_only or args.enroll_new_booth
    external=(args.enable_real_printer,args.accept_real_paper,args.enable_real_drive,args.accept_public_test_upload)
    if args.owned_acceptance_session and (setup or args.check_only):
        print('BLOCKED: owned acceptance handoff requires the original explicitly consented run.',file=sys.stderr)
        return 2
    if setup and (not args.setup_only or not args.enroll_new_booth or not args.sandbox_only
                  or args.check_only or any(external)):
        print('BLOCKED: local setup requires --setup-only --enroll-new-booth --sandbox-only, without run/check flags.',file=sys.stderr)
        return 2
    if not args.check_only and not setup and not all((args.sandbox_only,args.enable_real_printer,
            args.accept_real_paper,args.enable_real_drive,args.accept_public_test_upload)):
        print('BLOCKED: explicit Sandbox and both original paper/Drive consent pairs required.',file=sys.stderr)
        return 2
    if any(os.environ.get(k)=='1' for k in ('PHOTOBOOTH_V2_CHECKOUT_SANDBOX',
            'PHOTOBOOTH_V2_CHECKOUT_MOCK','PHOTOBOOTH_V2_PRINT','PHOTOBOOTH_V2_DRIVE')):
        print('BLOCKED: close/disable the other checkout profiles.',file=sys.stderr);return 2
    from photobooth.post_preview_launch import ProtectedSandboxLaunch
    from photobooth.post_preview_launch_settings import load_settings
    owner=app=simulator=None
    try:
        owner=ProtectedSandboxLaunch(ROOT)
        if setup:
            from photobooth.post_preview_enrollment import enroll_new_booth
            enroll_new_booth(owner,storage_root=args.storage_root,booth_id=args.booth_id)
            print('NEW BOOTH ENROLLED LOCALLY. No payment/device/cloud operation. Custody and original protected boot: NOT_CHECKED.')
            return 0
        settings=load_settings(owner,storage_root=args.storage_root,booth_id=args.booth_id)
        if args.check_only:
            print('LOCAL CONFIGURATION/HISTORY VALID. Custody, merchant, Drive sharing, printer, camera: NOT_CHECKED.')
            return 0
        if args.owned_acceptance_session:
            from photobooth.post_preview_acceptance import validate_runtime_session
            validate_runtime_session(owner,settings,args.owned_acceptance_session)
        # Native-only profile values. Backend private environment is independently
        # allowlisted by the original process host, never passed a GUI fixture.
        from tools.start_post_preview_device_test import child_environment
        environment=child_environment(dict(os.environ),args.camera_index)
        for name in ('SDL_VIDEODRIVER','SDL_AUDIODRIVER'):
            if name not in environment:os.environ.pop(name,None)
        os.environ.update(environment)
        from photobooth.kiosk_v2.qr_branding import branded_sandbox_qr_image
        control=owner.start(settings.config,settings.printer_config,legacy_path=settings.legacy_path,
                            qr_loader=branded_sandbox_qr_image,camera_index=args.camera_index,finish_on_stop=True)
        print('MIDTRANS SANDBOX ONLY: use official simulator; never pay with a real banking/wallet app.')
        print('Owned test printer and public test Drive enabled by explicit consents. Preserve original journals.')
        app=native_app(control,owner.camera,settings.config.private_root,args.size)
        if args.owned_acceptance_session:
            from photobooth.kiosk_v2.owned_sandbox_simulator import OwnedSandboxSimulatorClipboard
            simulator=OwnedSandboxSimulatorClipboard(app); simulator.install()
            print('OWNED SANDBOX: F8 copies ONLY the current QRIS image URL to local clipboard.')
            print('Paste into the official Sandbox simulator. Keep clipboard data out of shared reports.')
        app.run()
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception:
        print('BLOCKED: protected startup held. Preserve original history/custody; check local configuration.',file=sys.stderr)
        return 2
    finally:
        if simulator is not None:
            try: simulator.close()
            except (Exception,KeyboardInterrupt):
                pass  # Optional clipboard cleanup must NEVER bypass original drain.
        if owner is not None:
            from photobooth.post_preview_native_exit import drain_native_app
            noted=False
            while True:
                try:
                    if drain_native_app(app,timeout=.2) and owner.stop(timeout=.2):break
                    if not noted:
                        print('SHUTDOWN HELD: waiting for original workers; booth ownership retained.',flush=True);noted=True
                    time.sleep(.05)
                except KeyboardInterrupt:
                    print('SHUTDOWN HELD: original workers must finish; no force kill.',flush=True)


if __name__=='__main__':raise SystemExit(main())
