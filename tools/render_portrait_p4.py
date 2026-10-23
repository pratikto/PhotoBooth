"""Capture actual P4 widgets with isolated DEMO codes and injected game states."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('KIVY_NO_ARGS', '1')
for key in ('CAMERA', 'FACE_TRIGGER', 'PALM_TRIGGER', 'AD_VIDEO', 'AUDIO'):
    os.environ['PHOTOBOOTH_'+key] = '0'

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--width', type=int, default=800)
parser.add_argument('--height', type=int, default=1280)
parser.add_argument('--output-dir', required=True, type=Path)
args = parser.parse_args()

from kivy.config import Config
Config.set('graphics','width',str(args.width))
Config.set('graphics','height',str(args.height))
from kivy.clock import Clock
from kivy.core.window import Window
from PIL import Image
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.demo_game import DemoGameStore, GameJobs
from photobooth.kiosk_v2.game_engine import Pipe


class Recorder(PortraitKioskV2App):
    def __init__(self):
        self.temp = TemporaryDirectory()
        super().__init__(game_jobs=GameJobs(lambda:DemoGameStore(self.temp.name)))
        self.evidence=[]

    def enter_code(self, code):
        self._demo_code.text=code
        self._claim_game_demo()

    def sample_game(self):
        self._game_engine.start()
        self._game_engine.y=320
        self._game_engine.score=3
        self._game_engine.pipes=[Pipe(300,320),Pipe(470,260)]
        self._toggle_game_pause()
        self._game_score.text='03 / 10 POIN'
        self._game_field.draw()

    def outcome(self, won):
        self._game_paused=False
        self._game_engine.status='won' if won else 'lost'
        self._game_engine.score=10 if won else 2
        self._game_tick(0)

    def capture(self, name):
        path=Path(Window.screenshot(name=str(args.output_dir/f'{name}-{args.width}x{args.height}.png')))
        with Image.open(path) as photo:
            if photo.size!=(args.width,args.height):raise RuntimeError('Wrong screenshot dimensions')
        self.evidence.append({'file':path.name,'page':self.navigation.page,
                              'width':args.width,'height':args.height,
                              'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

    def on_start(self):
        args.output_dir.mkdir(parents=True,exist_ok=True)
        self.actions=iter([
            self._choose_game,
            lambda:self.capture('01-intro'),
            self._open_game_demo,
            lambda:self.capture('02-code-entry'),
            lambda:self.enter_code('CAFE-INVALID'),
            lambda:self.capture('03-invalid'),
            lambda:self.enter_code('DEMO-RENDER-1'),
            lambda:self.capture('04-ready'),
            self.sample_game,
            lambda:self.capture('05-paused-game'),
            lambda:self.outcome(True),
            lambda:self.capture('06-win'),
            self._continue_game_photo,
            lambda:self.capture('07-required-tutorial'),
            self._complete_tutorial,
            lambda:self.capture('08-win-gallery'),
            self._return_ad,self._choose_game,self._open_game_demo,
            lambda:self.enter_code('DEMO-RENDER-2'),
            lambda:self.outcome(False),
            lambda:self.capture('09-loss'),
            self._continue_game_photo,self._complete_tutorial,
            lambda:self.capture('10-loss-gallery'),
            self._return_ad,self._choose_game,self._open_game_demo,
            lambda:self.enter_code('DEMO-RENDER-1'),
            lambda:self.capture('11-used-code'),
            self.stop,
        ])
        Clock.schedule_once(self.advance,.5)

    def advance(self,_dt):
        if self._game_jobs.busy:
            Clock.schedule_once(self.advance,.1)
            return
        try:next(self.actions)()
        except StopIteration:return
        Clock.schedule_once(self.advance,.25)


if __name__=='__main__':
    app=Recorder()
    try:
        app.run()
        if len(app.evidence)!=11:raise RuntimeError('Incomplete P4 screenshots')
        report={'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'tracked_changes':bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT)),
                'synthetic_only':True,'game_states_injected':True,'screenshots':app.evidence}
        (args.output_dir/f'p4-report-{args.width}x{args.height}.json').write_text(json.dumps(report,indent=2)+'\n')
    finally:
        app._game_jobs.wait_closed()
        app.temp.cleanup()
