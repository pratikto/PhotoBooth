"""Capture actual opt-in MOCK widgets with isolated synthetic state, no provider."""

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
sys.path.insert(0,str(ROOT))
os.environ.setdefault('KIVY_NO_ARGS','1')
for key in ('CAMERA','FACE_TRIGGER','PALM_TRIGGER','AD_VIDEO','AUDIO'):
    os.environ['PHOTOBOOTH_'+key]='0'
os.environ['PHOTOBOOTH_V2_CHECKOUT_MOCK']='1'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--width',type=int,default=800)
parser.add_argument('--height',type=int,default=1280)
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()

from kivy.config import Config
Config.set('graphics','width',str(args.width))
Config.set('graphics','height',str(args.height))
from kivy.clock import Clock
from kivy.core.window import Window
from PIL import Image
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.demo_game import GameJobs
from photobooth.kiosk_v2.mock_checkout import MockCheckoutStore,MockCheckoutPresentation
from photobooth.kiosk_v2.photos import PhotoTest


class Recorder(PortraitKioskV2App):
    def __init__(self,root):
        self.ledger=MockCheckoutStore(root/'mock')
        super().__init__(checkout_jobs=GameJobs(lambda:MockCheckoutPresentation(self.ledger),
                                               actions={'open_checkout','status','transition','admit'}))
        self.evidence=[]

    def gallery(self):
        self._choose_photo();self._complete_tutorial();self._change_copies(1)

    def win_candidate(self):
        attempt=self.ledger.claim('DEMO-RENDER-CHECKOUT')['attempt_id']
        self._game_result=self.ledger.finish(attempt,'won',10)

    def expire(self):
        import time
        self.ledger.clock=lambda:time.time()+1000
        self._mock_status()

    def seed_recovery(self):
        import time
        self.ledger.clock=time.time
        self.ledger.create({self.templates[1].template_id:2},'render-recovery-00001')

    def capture(self,name):
        path=Path(Window.screenshot(name=str(args.output_dir/f'{name}-{args.width}x{args.height}.png')))
        with Image.open(path) as photo:
            if photo.size!=(args.width,args.height):raise RuntimeError('Wrong screenshot dimensions')
        self.evidence.append({'file':path.name,'page':self.navigation.page,
                              'mock_state':self._mock_view['state'] if self._mock_view else None,
                              'width':args.width,'height':args.height,
                              'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

    def on_start(self):
        args.output_dir.mkdir(parents=True,exist_ok=True)
        self.actions=iter([
            self.gallery,lambda:self.capture('01-mock-gallery'),self._open_mock_checkout,
            lambda:self.capture('02-regular-pending'),lambda:self._mock_transition('cancel'),
            lambda:self.capture('03-cancelled'),self._mock_leave,self._return_ad,
            self.win_candidate,self.gallery,lambda:self.capture('04-win-gallery'),
            self._open_mock_checkout,lambda:self.capture('05-win-pending'),
            lambda:self._mock_transition('unknown'),lambda:self.capture('06-unknown'),
            lambda:self._mock_transition('confirm'),lambda:self.capture('07-confirmed'),
            self._mock_admit,lambda:self.capture('08-photo-consent'),
            self._leave_photo_confirm,self._return_ad,self.gallery,self._open_mock_checkout,
            self.expire,lambda:self.capture('09-expired'),self._mock_leave,self._return_ad,
            self.seed_recovery,self.gallery,self._open_mock_checkout,
            lambda:self.capture('10-recovered'),self.stop,
        ])
        Clock.schedule_once(self.advance,.5)

    def advance(self,_dt):
        if self._mock_jobs.busy or (self._photo_jobs and self._photo_jobs.busy):
            Clock.schedule_once(self.advance,.1);return
        try:next(self.actions)()
        except StopIteration:return
        Clock.schedule_once(self.advance,.25)


if __name__=='__main__':
    with TemporaryDirectory() as temp:
        root=Path(temp)
        with patch('photobooth.kiosk_v2.photos.configured_test',return_value=PhotoTest(root/'photos')):
            app=Recorder(root)
            try:
                app.run()
                if len(app.evidence)!=10:raise RuntimeError('Incomplete MOCK screenshots')
                report={'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                        'tracked_changes':bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT)),
                        'synthetic_only':True,'game_result_injected':True,'recovery_seeded':True,
                        'real_provider':False,'screenshots':app.evidence}
                (args.output_dir/f'checkout-report-{args.width}x{args.height}.json').write_text(json.dumps(report,indent=2)+'\n')
            finally:
                app._mock_jobs.close();app._mock_jobs.wait_closed()
                if app._photo_jobs:app._photo_jobs.close();app._photo_jobs.wait_closed()
