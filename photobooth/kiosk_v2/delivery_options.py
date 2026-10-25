"""Explicit operator launch options over existing P3 printer/Drive adapters."""
import argparse
import os


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
    if selected.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX') == '1' and any(
            selected.get(key) == '1' for key in ('PHOTOBOOTH_V2_PRINT', 'PHOTOBOOTH_V2_DRIVE')):
        parser.error('The isolated merchant Sandbox trial keeps printer and Drive disabled.')
    env.update(updates)
    return args
