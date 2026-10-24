"""Read-only P5 inventory, never a device/payment certification or secret dump."""
from datetime import datetime, timezone
import importlib.metadata
import os
from pathlib import Path
import platform
import subprocess
import sys

from .diagnostics import source_head

BRANCH = 'feature/portrait-kiosk-v2-next'


def git_value(root, *args):
    try:
        return subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,
                              check=True,timeout=3).stdout.strip()
    except (OSError,subprocess.SubprocessError):
        return None


def windows_display():
    """Primary display physical pixels/scaling, without launching Kivy/camera."""
    if platform.system() != 'Windows':
        return {'resolution':None,'scaling_percent':None,'scope':'primary display; not measured on this OS'}
    import ctypes
    from ctypes import wintypes
    result={'resolution':None,'scaling_percent':None,'scope':'primary display; verify kiosk monitor in Windows Settings'}
    try:
        user=ctypes.windll.user32;gdi=ctypes.windll.gdi32
        user.GetDC.restype=wintypes.HDC
        user.ReleaseDC.argtypes=[wintypes.HWND,wintypes.HDC]
        gdi.GetDeviceCaps.argtypes=[wintypes.HDC,ctypes.c_int]
        dc=user.GetDC(None)
        try:
            width,height=gdi.GetDeviceCaps(dc,118),gdi.GetDeviceCaps(dc,117)
            if width>0 and height>0:result['resolution']=[width,height]
        finally:user.ReleaseDC(None,dc)
        user.MonitorFromPoint.argtypes=[wintypes.POINT,wintypes.DWORD]
        user.MonitorFromPoint.restype=wintypes.HANDLE
        monitor=user.MonitorFromPoint(wintypes.POINT(0,0),1)
        scale=ctypes.c_int()
        shcore=ctypes.windll.shcore
        shcore.GetScaleFactorForMonitor.argtypes=[wintypes.HANDLE,ctypes.POINTER(ctypes.c_int)]
        if shcore.GetScaleFactorForMonitor(monitor,ctypes.byref(scale))==0:
            result['scaling_percent']=scale.value
    except (OSError,AttributeError,ValueError):
        pass
    return result


def inventory(root, *, env=None, display=None):
    root=Path(root);env=os.environ if env is None else env
    modules={'Kivy':'kivy','Pillow':'PIL','opencv-python':'cv2','ffpyplayer':'ffpyplayer',
             'requests':'requests','qrcode':'qrcode','fastapi':'fastapi','pydantic':'pydantic',
             'httpx':'httpx','uvicorn':'uvicorn'}
    dependencies={}
    for package,module in modules.items():
        try:version=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            if package=='opencv-python':
                version=None
                for alternate in ('opencv-python-headless','opencv-contrib-python','opencv-contrib-python-headless'):
                    try:version=importlib.metadata.version(alternate);break
                    except importlib.metadata.PackageNotFoundError:pass
            else:version=None
        dependencies[package]=version
    sandbox=env.get('PHOTOBOOTH_V2_CHECKOUT_SANDBOX')=='1'
    mock=env.get('PHOTOBOOTH_V2_CHECKOUT_MOCK')=='1'
    try:index=int(env.get('PHOTOBOOTH_CAMERA_INDEX','0'))
    except ValueError:index=None
    branch=git_value(root,'branch','--show-current')
    dirty=git_value(root,'status','--porcelain')
    checks={
        'required_branch':branch==BRANCH,
        'source_clean':dirty=='',
        'python_311_or_newer':sys.version_info>=(3,11),
        'core_dependencies_present':all(dependencies[k] for k in ('Kivy','Pillow','opencv-python','ffpyplayer','requests','qrcode')),
        'checkout_mode_exclusive':not (sandbox and mock),
        'sandbox_mode_selected_if_enabled':not sandbox or env.get('MEONG_QRIS_MODE')=='sandbox',
        'gui_merchant_credentials_absent':not (env.get('MIDTRANS_SERVER_KEY') or env.get('MIDTRANS_MERCHANT_ID')),
        'sandbox_dependencies_present_if_enabled':not sandbox or all(dependencies[k] for k in ('fastapi','pydantic','httpx','uvicorn')),
        'camera_index_valid':index is not None and index>=0,
    }
    return {'schema_version':1,'generated_at':datetime.now(timezone.utc).isoformat(),
        'source':{'head':git_value(root,'rev-parse','HEAD') or source_head(root),
                  'branch':branch,'dirty':None if dirty is None else bool(dirty)},
        'device':{'os':platform.system(),'os_release':platform.release(),
                  'python':platform.python_version(),'display':windows_display() if display is None else display,
                  'camera_index':index,'camera_model':None,'speaker_output':None},
        'dependencies':dependencies,'configuration':{
            'sandbox_selected':sandbox,'mock_selected':mock,
            'test_printer_opt_in':env.get('PHOTOBOOTH_V2_PRINT')=='1',
            'test_drive_opt_in':env.get('PHOTOBOOTH_V2_DRIVE')=='1',
            'booth_token_present':bool(env.get('MEONG_QRIS_BOOTH_TOKEN'))},
        'preflight':{'checks':checks,'status':'READY_FOR_MANUAL_TEST' if all(checks.values()) else 'NEEDS_ATTENTION'},
        'acceptance':{gate:'NOT_RUN' for gate in ('windows_touch_camera_audio','merchant_sandbox_simulator',
            'physical_print_output','drive_download_and_30_day_retention','privacy_operator_signoff','release_approval')},
        'notes':['No camera, microphone, speaker, printer, merchant or cloud network was accessed.',
                 'Primary display may differ from kiosk monitor; verify actual resolution/scaling.',
                 'Configuration presence is not provider authentication or hardware acceptance.',
                 'No secrets, tokens, provider URLs or customer photo paths are included.']}
