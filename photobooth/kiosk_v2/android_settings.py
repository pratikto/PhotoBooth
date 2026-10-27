"""Validated app-private mobile configuration; merchant keys are never accepted."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

DEFAULTS = {'camera_facing': 0, 'print_enabled': False, 'usb_vendor': 0x4838,
            'usb_product': 0x3830, 'print_width': 576, 'dither': 'floyd-steinberg',
            'sandbox_enabled': False, 'api_url': '', 'booth_id': 'PB001',
            'booth_token': '', 'audio_enabled': True, 'face_enabled': True,
            'palm_enabled': True, 'video_enabled': True,
            'drive_enabled': False, 'web_app_url': '', 'upload_token': ''}


def validated(data):
    if not isinstance(data, dict) or set(data)-set(DEFAULTS):
        raise ValueError('Use mobile booth settings only; merchant credentials belong on the backend')
    settings = {**DEFAULTS, **data}
    for key in ('print_enabled', 'sandbox_enabled', 'audio_enabled', 'face_enabled', 'palm_enabled', 'video_enabled','drive_enabled'):
        if type(settings[key]) is not bool:
            raise ValueError('Invalid enabled setting')
    for key, values in (('camera_facing', (0, 1)), ('print_width', (384, 576))):
        if type(settings[key]) is not int or settings[key] not in values:
            raise ValueError('Invalid camera or paper setting')
    for key in ('usb_vendor', 'usb_product'):
        if type(settings[key]) is not int or not 1 <= settings[key] <= 65535:
            raise ValueError('Invalid USB VID/PID')
    if settings['dither'] not in ('floyd-steinberg','bayer','threshold'):
        raise ValueError('Invalid printer dithering')
    if not isinstance(settings['booth_id'], str) or re.fullmatch(r'PB[0-9]{3,8}', settings['booth_id']) is None:
        raise ValueError('Invalid booth identity')
    token = settings['booth_token']
    if not isinstance(token, str) or len(token) > 512 or any(c.isspace() or not 33 <= ord(c) <= 126 for c in token):
        raise ValueError('Invalid booth token')
    url = settings['api_url']
    if not isinstance(url, str) or len(url)>2048:
        raise ValueError('Invalid backend URL')
    try:
        p = urlsplit(url)
        port = p.port
        if url and (p.scheme != 'https' or not p.hostname or p.username or p.password or p.query or p.fragment
                    or any(c.isspace() or ord(c)<33 for c in url)):
            raise ValueError()
    except ValueError:
        raise ValueError('Use an HTTPS booth backend URL') from None
    if settings['sandbox_enabled'] and (not url or len(token) < 32):
        raise ValueError('Sandbox needs an HTTPS backend and a booth token')
    script, upload = settings['web_app_url'], settings['upload_token']
    if (not isinstance(script,str) or len(script)>2048 or not isinstance(upload,str) or len(upload)>512
            or any(c.isspace() or ord(c)<33 for c in upload)):
        raise ValueError('Invalid Drive configuration')
    if script and re.fullmatch(r'https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec',script) is None:
        raise ValueError('Use the existing Apps Script deployment URL')
    if settings['drive_enabled'] and (not script or not upload):
        raise ValueError('Drive needs its existing deployment URL and upload token')
    if settings['drive_enabled'] and settings['sandbox_enabled']:
        raise ValueError('Dedicated Sandbox keeps Drive off, as in v2')
    return settings


def load_settings(root):
    path = Path(root)/'mobile-settings.json'
    if path.is_symlink():
        raise ValueError('Linked mobile configuration is not allowed')
    if not path.exists():
        return dict(DEFAULTS)
    if path.stat().st_size>8192:
        raise ValueError('Mobile configuration is too large')
    try:
        return validated(json.loads(path.read_text(encoding='utf-8')))
    except (TypeError, json.JSONDecodeError):
        raise ValueError('Invalid private mobile configuration') from None


def save_settings(root, data):
    from photobooth.manifest_io import write_json_atomic
    settings = validated(data)
    root = Path(root)
    journal = root/'data/kiosk-v2-sandbox/android/visit.json'
    current = load_settings(root)
    identity = ('sandbox_enabled','api_url','booth_id')
    if journal.exists() and any(settings[k] != current[k] for k in identity):
        try:
            state = json.loads(journal.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            raise ValueError('Preserve the payment profile for operator recovery') from None
        if state.get('phase') not in {'COMPLETED','CANCELLED'}:
            raise ValueError('Finish or reconcile the existing payment before changing its profile')
        # Even terminal journals bind context. Keep the endpoint/booth immutable
        # rather than deleting/renaming a journal to configure another profile.
        if any(settings[k] != current[k] for k in ('api_url','booth_id')):
            raise ValueError('Existing payment journal belongs to this backend and booth')
    path = root/'mobile-settings.json'
    if path.is_symlink():
        raise ValueError('Linked mobile configuration is not allowed')
    write_json_atomic(path, settings)
    path.chmod(0o600)
    return settings


def configure_mobile(root, settings, *, environ=None):
    import os
    from .android_preview import configure_preview
    env = os.environ if environ is None else environ
    root = configure_preview(root, environ=env)
    settings = validated(settings)
    journal = root/'data/kiosk-v2-sandbox/android/visit.json'
    if journal.exists():
        if journal.is_symlink() or journal.stat().st_size>65536:
            raise ValueError('Payment profile needs operator recovery')
        try:
            state = json.loads(journal.read_text(encoding='utf-8'))
            context = state.get('context', {})
            if (state.get('phase') not in {'COMPLETED','CANCELLED'} and
                    (not settings['sandbox_enabled'] or context != {'mode':'sandbox',
                     'booth_id':settings['booth_id'],'endpoint':settings['api_url'].rstrip('/')})):
                raise ValueError('Preserve the active payment profile for operator recovery')
        except (TypeError, AttributeError, json.JSONDecodeError):
            raise ValueError('Payment profile needs operator recovery') from None
    # No inherited desktop account, storage root or device configuration.
    for key in list(env):
        if key.startswith(('MIDTRANS_', 'MEONG_QRIS_', 'PHOTOBOOTH_PRINTER_', 'PHOTOBOOTH_DRIVE_', 'GOOGLE_OAUTH_')):
            env.pop(key, None)
    for key in ('PHOTOBOOTH_V2_STORAGE_ROOT','PHOTOBOOTH_WEB_APP_URL','PHOTOBOOTH_UPLOAD_TOKEN'):
        env.pop(key, None)
    env.update(PHOTOBOOTH_CAMERA='1', PHOTOBOOTH_V2_STORAGE='2',
               PHOTOBOOTH_V2_BOOTH_ID=settings['booth_id']+'V2',
               PHOTOBOOTH_AUDIO='1' if settings['audio_enabled'] else '0',
               PHOTOBOOTH_V2_PRINT='1' if settings['print_enabled'] else '0',
               PHOTOBOOTH_V2_AUTO_PRINT='1')
    env.update(PHOTOBOOTH_FACE_TRIGGER='1' if settings['face_enabled'] else '0',
               PHOTOBOOTH_PALM_TRIGGER='1' if settings['palm_enabled'] else '0',
               PHOTOBOOTH_AD_VIDEO='1' if settings['video_enabled'] else '0',
               KIVY_VIDEO='ffpyplayer' if settings['video_enabled'] else 'null')
    if settings['drive_enabled']:
        env.update(PHOTOBOOTH_V2_DRIVE='1',PHOTOBOOTH_WEB_APP_URL=settings['web_app_url'],
                   PHOTOBOOTH_UPLOAD_TOKEN=settings['upload_token'])
    if settings['sandbox_enabled']:
        env.update(PHOTOBOOTH_V2_CHECKOUT_SANDBOX='1', MEONG_QRIS_MODE='sandbox',
                   MEONG_QRIS_API_URL=settings['api_url'], MEONG_QRIS_BOOTH_ID=settings['booth_id'],
                   MEONG_QRIS_BOOTH_TOKEN=settings['booth_token'],
                   MEONG_QRIS_JOURNAL=str(root/'data/kiosk-v2-sandbox/android/visit.json'))
    return root
