"""Capture actual P3 widgets with synthetic camera pixels and an isolated store."""

import argparse
import hashlib
import json
import os
# Synthetic captures never inherit an operator's live delivery opt-ins.
os.environ['PHOTOBOOTH_V2_PRINT'] = '0'
os.environ['PHOTOBOOTH_V2_DRIVE'] = '0'
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from types import SimpleNamespace
from unittest.mock import Mock

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
parser.add_argument('--storage-layout', type=int, choices=(1,2), default=1, help='Capture layout 2 with temporary offline storage only')
parser.add_argument('--delivery', action='store_true', help='Capture automatic print/Drive with offline transports only')
args = parser.parse_args()
if args.storage_layout == 2 and (args.delivery or args.sensors):
    parser.error("Capture layout 2 separately from legacy delivery/sensor fixtures.")
if args.delivery and args.sensors:
    parser.error('Choose separate sensor or delivery fixture runs.')

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
        if args.delivery:
            self.actions=iter([
                lambda:(self._choose_photo(),self._complete_tutorial(),self._change_copies(2)),
                self.enter_delivery,
                lambda:self.capture_screen('delivery-01-drive-waiting'),
                self.ready_delivery,
                lambda:self.capture_screen('delivery-02-drive-ready'),
                self._admit_photo_test,self.shoot,self.shoot,self.shoot,
                lambda:self._photo_submit('compose'),
                lambda:self.run_delivery('offline'),
                lambda:self.capture_screen('delivery-04-offline-retry'),
                lambda:self.run_delivery('online'),
                lambda:self.capture_screen('delivery-05-upload-verified'),
                lambda:self._photo_submit('next'),
                lambda:(self._choose_photo(),self._complete_tutorial(),self._change_copies(1)),
                self._enter_photo_test,self._admit_photo_test,self.shoot,self.shoot,self.shoot,
                lambda:self._photo_submit('compose'),
                lambda:self.capture_screen('delivery-06-print-uncertain'),
                lambda:self._photo_submit('acknowledge_print'),
                lambda:self.run_delivery('retention'),
                lambda:self.capture_screen('delivery-07-retention-held'),
                self.stop])
            Clock.schedule_once(self.advance,.3)
            return
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
        printer = SimpleNamespace(print_image=lambda *a, **kw: SimpleNamespace(success=False))
        workspace = None
        if args.storage_layout == 2:
            from photobooth.booth_storage import BoothWorkspace
            from photobooth.printer import ThermalPrinter, PrinterConfig
            workspace = BoothWorkspace(Path(self.temp.name)/'Photobooth', 'PB001V2S2')
            printer.render_image = ThermalPrinter(PrinterConfig()).render_image
            printer.print_raster = lambda *a, **kw: SimpleNamespace(success=False)
        service = PhotoTest(self.temp.name, printer=printer, workspace=workspace, drive_requested=args.storage_layout==2)
        self._photo_jobs = PhotoJobs(service)
        self._photo_jobs.submit('prepare')
        self._show()

    def enter_delivery(self):
        from photobooth.drive_pool import DriveSlotPool
        from photobooth.drive_storage import RemoteDriveSlot
        from photobooth.retention import retention_metadata
        from photobooth.kiosk_v2.photo_drive import RetentionGuardedSync
        self.delivery_mode='offline';self.print_batches=[]
        client=self.delivery_client=Mock()
        client.ensure_folder_pool.return_value=[RemoteDriveSlot(
            f'fixture-folder-{n}',f'https://example.test/photos/PB001V2_{n:08d}/originals-and-strip',f'fixture-slot-{n}',
            'READY',f'PB001V2_{n:08d}',transaction_id=f'PB001V2_{n:08d}',verified=True) for n in (1,2)]
        client.register_retention.side_effect=lambda _folder,tx,started:(
            {} if self.delivery_mode=='retention' else retention_metadata(tx,started))
        def send(_path,*,copies):
            self.print_batches.append(copies)
            if len(self.print_batches)==1:
                # Capture an actual pending single-flight send on the GUI thread
                # after its busy/result widgets have reached a rendered frame.
                Clock.schedule_once(lambda _dt:self.capture_screen('delivery-03-print-sending'),.2)
                time.sleep(.9)
            return SimpleNamespace(success=len(self.print_batches)==1)
        service=PhotoTest(self.temp.name,printer=SimpleNamespace(print_image=send),drive_client=client,auto_print=True)
        service.pool=DriveSlotPool(service.store.photos_root,Path(self.temp.name)/'drive-pool.json','PB001V2',2)
        # Reuse the actual guarded sync pass, with injected local responses and
        # no daemon started. No credential/client/network provider is created.
        service.drive_worker=RetentionGuardedSync(service.store.photos_root,client,service.pool)
        def upload(_folder,_tx,relative,path,**_kw):
            from photobooth.drive_storage import DriveApiError
            if self.delivery_mode=='offline':raise DriveApiError('fixture offline',503)
            data=path.read_bytes()
            return {'id':relative,'size':len(data),'md5Checksum':hashlib.md5(data).hexdigest()}
        client.upload_file.side_effect=upload
        def sync():
            service.drive_worker._process_pending_assignments()
            service.drive_worker._process_pending_uploads()
            return service.snapshot()
        service.fixture_delivery=sync
        self.navigation.confirm_photo_test();self._photo_jobs=PhotoJobs(service)
        self._photo_jobs.submit('prepare');self._show()

    def ready_delivery(self):
        self._photo_jobs.service.pool.refresh(self.delivery_client)
        self._photo_submit('snapshot')

    def run_delivery(self,mode):
        self.delivery_mode=mode
        self._photo_submit('fixture_delivery')

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
        if name.startswith('delivery-'):
            view=self._photo_view
            if 'waiting' in name:assert not view['drive_ready']
            if 'drive-ready' in name:assert view['drive_ready']
            if 'print-sending' in name:assert self._photo_jobs.busy
            if 'offline-retry' in name:assert view['upload_status']=='UPLOAD_RETRY' and view['download_qr'] is None
            if 'upload-verified' in name:assert view['upload_status']=='UPLOAD_COMPLETE' and view['download_qr'] is not None
            if 'print-uncertain' in name:assert view['print_state']=='UNCERTAIN'
            if 'retention-held' in name:assert view['retention_error'] and view['download_qr'] is None
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
        expected = 7 if args.delivery else 12 if args.sensors else 8
        if len(app.evidence) != expected:
            raise SystemExit(f'Incomplete P3 evidence: {len(app.evidence)}/{expected}')
        report = {'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  'tracked_changes': bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT)),
                  'storage_layout':args.storage_layout, 'synthetic_only': True, 'synthetic_sensor_status': args.sensors, 'screenshots': app.evidence}
        if args.delivery:
            assert app.print_batches==[2,1]
            report.update(real_print=False,real_cloud=False,reused_v1_delivery=True,print_batches=app.print_batches,
                          verified_qr_url=app.delivery_client.ensure_folder_pool.return_value[0].folder_url)
        kind='delivery' if args.delivery else 'p3'
        (args.output_dir / f'{kind}-report-{args.width}x{args.height}.json').write_text(json.dumps(report, indent=2)+'\n')
    finally:
        if app._photo_jobs:
            app._photo_jobs.wait_closed()
        app.temp.cleanup()
