"""Native Sandbox view evidence over offline HTTP fixtures, never merchant acceptance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
os.environ.update(KIVY_NO_ARGS='1',PHOTOBOOTH_V2_CHECKOUT_SANDBOX='1',
                  PHOTOBOOTH_V2_CHECKOUT_MOCK='0',MEONG_QRIS_MODE='sandbox',
                  MIDTRANS_SERVER_KEY='',MIDTRANS_MERCHANT_ID='')
for key in ('CAMERA','FACE_TRIGGER','PALM_TRIGGER','AD_VIDEO','AUDIO'):
    os.environ['PHOTOBOOTH_'+key]='0'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--width',type=int,default=800);parser.add_argument('--height',type=int,default=1280)
parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
from kivy.config import Config
Config.set('graphics','width',str(args.width));Config.set('graphics','height',str(args.height))
from kivy.clock import Clock
from kivy.core.window import Window
from PIL import Image
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.flow import SANDBOX_CHECKOUT
from photobooth.kiosk_v2.photos import PhotoTest
from qris_v2_fixture import Fixture


class Recorder(PortraitKioskV2App):
    def __init__(self,fixture):
        self.fixture=fixture;self.evidence=[]
        super().__init__(sandbox_jobs=fixture.jobs)
    def gallery(self):
        self._choose_photo();self._complete_tutorial();self._change_copies(1)
        self._open_sandbox()
    def paid(self):
        self.fixture.paid();self._sandbox_retry()
    def recovery(self):
        self.fixture.service.recover();self._sandbox_view=self.fixture.service.view()
        self.navigation.page=SANDBOX_CHECKOUT;self._show()
    def capture(self,name):
        path=Path(Window.screenshot(name=str(args.output_dir/f'{name}-{args.width}x{args.height}.png')))
        with Image.open(path) as image:
            assert image.size==(args.width,args.height)
        self.evidence.append({'file':path.name,'page':self.navigation.page,
            'phase':(self._sandbox_view or {}).get('phase'),'width':args.width,'height':args.height,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    def on_start(self):
        args.output_dir.mkdir(parents=True,exist_ok=True)
        self.actions=iter([self.gallery,lambda:self.capture('01-quote'),self._sandbox_begin,
            lambda:self.capture('02-waiting-offline-fixture'),self.paid,
            lambda:self.capture('03-reserved'),self._sandbox_photo_consent,
            lambda:self.capture('04-consent'),self.recovery,
            lambda:self.capture('05-recovery'),self.stop])
        Clock.schedule_once(self.advance,.5)
    def advance(self,_dt):
        if self._sandbox_jobs.busy or (self._photo_jobs and self._photo_jobs.busy):
            Clock.schedule_once(self.advance,.1);return
        try:next(self.actions)()
        except StopIteration:return
        Clock.schedule_once(self.advance,.3)


if __name__=='__main__':
    with TemporaryDirectory() as temp:
        fixture=Fixture(Path(temp))
        with patch('photobooth.kiosk_v2.photos.configured_test',return_value=PhotoTest(Path(temp)/'photos')):
            app=Recorder(fixture)
            try:app.run()
            finally:
                fixture.jobs.close();fixture.jobs.wait_closed()
                if app._photo_jobs:app._photo_jobs.wait_closed()
                fixture.store.close()
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        (args.output_dir/f'evidence-{args.width}x{args.height}.json').write_text(json.dumps({
            'head':source,'fixture':'OFFLINE HTTP; NOT MERCHANT ACCEPTANCE',
            'screenshots':app.evidence},indent=2)+'\n')
