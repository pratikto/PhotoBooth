"""Render the reused v1 operator panel in v2 with offline observations only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('KIVY_NO_ARGS','1')
for key in ('CAMERA','FACE_TRIGGER','PALM_TRIGGER','AD_VIDEO','AUDIO'):
    os.environ['PHOTOBOOTH_'+key]='0'
os.environ.update(PHOTOBOOTH_V2_CHECKOUT_SANDBOX='0',PHOTOBOOTH_V2_CHECKOUT_MOCK='0')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--width',type=int,default=800);parser.add_argument('--height',type=int,default=1280)
parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
from kivy.config import Config
Config.set('graphics','width',str(args.width));Config.set('graphics','height',str(args.height))
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from PIL import Image
from photobooth.device_health import HealthCheck,HealthSnapshot
from photobooth.hardware_adapters import DeviceDescriptor
from photobooth.kiosk_v2.app import PortraitKioskV2App


def observation(mode):
    if mode=='slow':time.sleep(1.2)
    if mode=='error':raise OSError('Synthetic provider-independent probe failure')
    values=[('camera','unknown','Belum ada frame kamera pada fixture; tidak membuka kamera.'),
            ('printer','ready','Queue uji teramati; kertas dan hasil fisik belum diperiksa.'),
            ('disk','warning','Contoh peringatan penyimpanan, bukan kapasitas perangkat ini.'),
            ('network','unknown','Koneksi/provider tidak diakses pada screenshot fixture.'),
            ('media','ready','Contoh aset lokal tersedia; decoder belum diuji.'),
            ('heartbeat','ready','Main loop aktif selama pemeriksaan background.')]
    return HealthSnapshot('2026-10-25T05:00:00+00:00',tuple(HealthCheck(*x) for x in values),
        platform='windows',devices=(DeviceDescriptor('printer','fixture-queue','Queue UJI (fixture)',
            'windows-spooler','windows','queue-name','queue-detected',(),
            'Not a physical device or printer acceptance'),))


class Recorder(PortraitKioskV2App):
    def __init__(self):
        self.mode='normal';self.evidence=[];self.capturing=False
        super().__init__()
    def capture(self,name):
        # Window readback otherwise sees the preceding swapped frame after a
        # fast worker result. Keep the next state idle until the UI has painted.
        self.capturing=True
        Clock.schedule_once(lambda _dt:self.capture_ready(name),.12)
    def capture_ready(self,name):
        panel=self._operator_panel
        if name=='03-local-report-saved':assert 'Tersimpan' in panel.report_message.text
        if name=='01-health-overview':assert panel.snapshot is not None
        if name=='04-background-probe':assert panel._health_refresh_button.disabled
        if name=='05-probe-unavailable':assert panel.snapshot is None and not panel._health_refresh_button.disabled
        path=Path(Window.screenshot(name=str(args.output_dir/f'{name}-{args.width}x{args.height}.png')))
        with Image.open(path) as picture:assert picture.size==(args.width,args.height)
        self.evidence.append({'file':path.name,'page':self.navigation.page,'width':args.width,
            'height':args.height,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        self.capturing=False
    def inventory(self):
        scroll=next(w for w in self._operator_panel._health_popup.walk() if isinstance(w,ScrollView))
        scroll.scroll_y=0
    def refresh(self,mode):
        self.mode=mode;self._operator_panel._health_refresh_button.dispatch('on_release')
    def on_start(self):
        args.output_dir.mkdir(parents=True,exist_ok=True)
        self.steps=iter([
            (self._open_operator,False),(lambda:self.capture('01-health-overview'),True),
            (self.inventory,True),(lambda:self.capture('02-health-inventory'),True),
            (lambda:self._operator_panel.export_button.dispatch('on_release'),True),
            (lambda:self.capture('03-local-report-saved'),True),(lambda:self.refresh('slow'),True),
            (lambda:self.capture('04-background-probe'),False),(lambda:self.refresh('error'),True),
            (lambda:self.capture('05-probe-unavailable'),True),(self.stop,True)])
        self.pending=None;Clock.schedule_once(self.advance,.3)
    def advance(self,_dt):
        if self.capturing:
            Clock.schedule_once(self.advance,.1);return
        if self.pending is None:
            try:self.pending=next(self.steps)
            except StopIteration:return
        action,wait=self.pending;panel=self._operator_panel
        if wait and (self._health_reports.busy or (panel and panel._health_refresh_button.disabled)):
            Clock.schedule_once(self.advance,.1);return
        self.pending=None;action();Clock.schedule_once(self.advance,.2)


if __name__=='__main__':
    with TemporaryDirectory() as temp:
        with patch('photobooth.kiosk_v2.operator_health.PROJECT_ROOT',Path(temp)):
            app=Recorder()
            with patch('photobooth.v1_health_controller.collect_health_snapshot',side_effect=lambda **_:observation(app.mode)):
                try:app.run()
                finally:app._health_reports.wait_closed()
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        dirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True))
        (args.output_dir/f'health-report-{args.width}x{args.height}.json').write_text(json.dumps({
            'source_sha':source,'tracked_changes':dirty,'synthetic_only':True,
            'original_panel_reused':True,'real_probe':False,'screenshots':app.evidence},indent=2)+'\n')
