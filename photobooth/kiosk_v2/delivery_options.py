"""Explicit operator launch options over existing P3 printer/Drive adapters."""
import argparse
import os


def sandbox_print_enabled(env=None):
    env=os.environ if env is None else env
    return (env.get('PHOTOBOOTH_V2_SANDBOX_PRINT')=='1'
            and env.get('PHOTOBOOTH_V2_PRINT')=='1'
            and env.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX')=='1'
            and env.get('PHOTOBOOTH_V2_CHECKOUT_MOCK')!='1'
            and env.get('MEONG_QRIS_MODE')=='sandbox'
            and env.get('PHOTOBOOTH_V2_DRIVE')!='1'
            and not env.get('MIDTRANS_SERVER_KEY') and not env.get('MIDTRANS_MERCHANT_ID'))


def forbidden_sandbox_delivery(env=None):
    env=os.environ if env is None else env
    return (env.get('PHOTOBOOTH_V2_DRIVE')=='1'
            or (env.get('PHOTOBOOTH_V2_PRINT')=='1' and not sandbox_print_enabled(env)))


def configure_delivery(argv=(), *, environ=None):
    """No credentials, network, settings writes or native imports on this path."""
    env = os.environ if environ is None else environ
    parser = argparse.ArgumentParser(description='Meong portrait v2 local photo launcher')
    parser.add_argument('--print', dest='printing', action='store_true',
                        help='Use saved v1 printer settings; auto-print each approved strip once')
    parser.add_argument('--drive', action='store_true',
                        help='Use existing v1 Drive credentials and isolated v2 upload queue')
    parser.add_argument('--manual-print', action='store_true',
                        help='Keep an explicit print button instead of automatic printing')
    args = parser.parse_args(argv)
    updates = {}
    if args.printing:
        updates.update(PHOTOBOOTH_V2_PRINT='1', PHOTOBOOTH_V2_AUTO_PRINT='1')
    if args.drive:
        updates['PHOTOBOOTH_V2_DRIVE'] = '1'
    if args.manual_print:
        if updates.get('PHOTOBOOTH_V2_PRINT', env.get('PHOTOBOOTH_V2_PRINT')) != '1':
            parser.error('--manual-print requires --print or PHOTOBOOTH_V2_PRINT=1')
        updates['PHOTOBOOTH_V2_AUTO_PRINT'] = '0'
    selected = {**env, **updates}
    if selected.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX') == '1' and forbidden_sandbox_delivery(selected):
        parser.error('Sandbox printing needs its dedicated profile; Drive stays disabled.')
    env.update(updates)
    return args
