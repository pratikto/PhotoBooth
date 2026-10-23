"""Capture actual P3 widgets with synthetic camera pixels and an isolated store."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('KIVY_NO_ARGS', '1')
os.environ['PHOTOBOOTH_CAMERA'] = '0'
os.environ['PHOTOBOOTH_FACE_TRIGGER'] = '0'
os.environ['PHOTOBOOTH_PALM_TRIGGER'] = '0'
os.environ['PHOTOBOOTH_AD_VIDEO'] = '0'

parser = argparse.ArgumentParser()
parser.add_argument('--width', type=int, default=800)
parser.add_argument('--height', type=int, default=1280)
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--sensors', action='store_true', help='Add clearly synthetic face/palm status views')
args = parser.parse_args()

from kivy.config import Config
Config.set('graphics', 'width', str(args.width))
Config.set('graphics', 'height', str(args.height))
from kivy.clock import Clock
from kivy.core.window import Window
import numpy as np
from PIL import Image, ImageDraw
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.photos import PhotoJobs, PhotoTest
from photobooth.kiosk_v2.flow import PHOTO_CONFIRM


class SyntheticCamera:
    def __init__(self):
        image = Image.new('RGB', (640, 480), '#42648e')
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 155, 479), fill='#cd6c86')
        draw.rectangle((485, 0, 639, 479), fill='#61a5ac')
        draw.ellipse((228, 95, 412, 290), fill='#efc692')
        draw.arc((270, 202, 370, 255), 0, 180, fill='#3d315e', width=6)
        for x in (282, 355):
            draw.ellipse((x, 165, x + 10, 176), fill='#3d315e')
        draw.rounded_rectangle((155, 315, 485, 520), 90, fill='#7776bd')
        draw.text((18, 20), 'SYNTHETIC CAMERA / LEFT', fill='white')
        self.frame = np.array(image)[:, :, ::-1].copy()

    def read(self):
        return self.frame

    def start(self): pass
    def close(self): pass
    def set_active(self, active): pass


class SyntheticSensor:
    state = 'ready'
    progress = 0.0
    needs_release = False
    def update(self, *a, **kw): return False
    def pause(self): pass
    def close(self): pass
    def latch(self): self.progress = 0


class Recorder(PortraitKioskV2App):
    def __init__(self):
        self.temp = TemporaryDirectory()
        self.evidence = []
        self.fake_camera = SyntheticCamera()
        self.fake_face, self.fake_palm = SyntheticSensor(), SyntheticSensor()
        super().__init__(camera_device=self.fake_camera,
                         face_inviter=self.fake_face if args.sensors else None,
                         palm_shutter=self.fake_palm if args.sensors else None)

    def on_start(self):
        args.output_dir.mkdir(parents=True, exist_ok=True)
        actions = [
            lambda: (self._choose_photo(), self._complete_tutorial(), self._change_copies(2)),
            self.enter,
            lambda: self.capture_screen('01-photo-confirm'),
            self._admit_photo_test,
            lambda: self.capture_screen('02-camera-ready'),
            self._start_countdown,
            lambda: self.capture_screen('03-countdown'),
            self.shoot,
            self.shoot,
            self.shoot,
            lambda: self.capture_screen('04-review'),
            lambda: self._photo_submit('retake', 1),
            lambda: self.capture_screen('05-retake-ready'),
            self.shoot,
            lambda: self._photo_submit('compose'),
            lambda: self.capture_screen('06-local-result'),
            lambda: self._photo_submit('print_result'),
            lambda: self.capture_screen('07-print-uncertain'),
            lambda: self._photo_submit('acknowledge_print'),
            lambda: self._photo_submit('next'),
            lambda: (self._choose_photo(), self._complete_tutorial(), self._change_copies(1)),
            self._enter_photo_test,
            self._admit_photo_test,
            self.lose_camera,
            lambda: self.capture_screen('08-camera-unavailable'),
            self.stop,
        ]
        if args.sensors:
            actions[:0] = [lambda: setattr(self.fake_face, 'progress', .4),
                           lambda: self.capture_screen('09-face-hold')]
            index = actions.index(self._start_countdown)
            actions[index:index] = [
                lambda: setattr(self.fake_palm, 'progress', .5),
                lambda: self.capture_screen('10-palm-hold'),
                lambda: setattr(self.fake_palm, 'state', 'unavailable'),
                lambda: self.capture_screen('11-palm-unavailable'),
                lambda: (setattr(self.fake_palm, 'state', 'ready'),
                         setattr(self.fake_palm, 'needs_release', True)),
                lambda: self.capture_screen('12-palm-release'),
                lambda: setattr(self.fake_palm, 'needs_release', False),
            ]
        self.actions = iter(actions)
        Clock.schedule_once(self.advance, 1)

    def enter(self):
        self.navigation.confirm_photo_test()
        service = PhotoTest(self.temp.name, printer=SimpleNamespace(
            print_image=lambda *a, **kw: SimpleNamespace(success=False)))
        self._photo_jobs = PhotoJobs(service)
        self._photo_jobs.submit('prepare')
        self._show()

    def shoot(self):
        if self._countdown_event is None:
            self._start_countdown()
        self._countdown_deadline = time.monotonic() - 1
        self._countdown_tick(0)

    def lose_camera(self):
        self.fake_camera.frame = None
        self._start_countdown()

    def advance(self, _dt):
        if self._photo_jobs and self._photo_jobs.busy:
            Clock.schedule_once(self.advance, .1)
            return
        try:
            action = next(self.actions)
        except StopIteration:
            return
        action()
        Clock.schedule_once(self.advance, .45)

    def capture_screen(self, name):
        path = Path(Window.screenshot(name=str(args.output_dir / f'{name}-{args.width}x{args.height}.png')))
        with Image.open(path) as screenshot:
            if screenshot.size != (args.width, args.height) or screenshot.convert('RGB').getextrema() == ((0,0),)*3:
                raise RuntimeError('Invalid native screenshot')
        self.evidence.append({'state': name, 'page': self.navigation.page, 'file': path.name,
                              'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                              'width': args.width, 'height': args.height})


if __name__ == '__main__':
    app = Recorder()
    try:
        app.run()
        expected = 12 if args.sensors else 8
        if len(app.evidence) != expected:
            raise SystemExit(f'Incomplete P3 evidence: {len(app.evidence)}/{expected}')
        report = {'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  'tracked_changes': bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT)),
                  'synthetic_only': True, 'synthetic_sensor_status': args.sensors, 'screenshots': app.evidence}
        (args.output_dir / f'p3-report-{args.width}x{args.height}.json').write_text(json.dumps(report, indent=2)+'\n')
    finally:
        if app._photo_jobs:
            app._photo_jobs.wait_closed()
        app.temp.cleanup()
