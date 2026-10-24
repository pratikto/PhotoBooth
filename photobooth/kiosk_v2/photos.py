"""P3 nonfinancial photo-test workflow over the existing booth services.

All methods run on PhotoJobs' single worker. Never instantiate the legacy GUI,
mark an order paid, or write to its counters, manifests or Drive pool.
"""

from dataclasses import dataclass
import json
import logging
from pathlib import Path
import queue
import threading

from PIL import Image

from photobooth.catalog import compose_result
from photobooth.manifest_io import manifest_lock, write_json_atomic
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import PhotoSession, build_session_plans

LOG = logging.getLogger(__name__)
PURPOSE = 'PORTRAIT_V2_PHOTO_TEST'


class PhotoTest:
    """Single admitted test run; originals, retake quota and copies remain v1 rules."""

    def __init__(self, root, *, booth_id='PB001V2', printer=None, drive_client=None):
        self.root = Path(root)
        self.store = TransactionStore(self.root / 'photos', self.root / 'counter.json', booth_id)
        self.printer = printer
        self.drive_client = drive_client
        self.pool = None
        self.drive_worker = None
        self.retention_worker = None
        self.transaction = None
        self.sessions = []
        self.index = 0
        self.phase = 'confirm'
        self._retake = False
        self._closed = threading.Event()
        self.recovered_prints = 0

    def prepare(self):
        """Called off the GUI; recover uncertain sends without replaying them."""
        from photobooth.retention import purge_local_photos
        purge_local_photos(self.store.photos_root)
        if self.retention_worker is None and not self._closed.is_set():
            from photobooth.retention import PhotoRetentionWorker
            # Isolated local cleanup only. Never invoke remote cleanup on legacy folders.
            self.retention_worker = PhotoRetentionWorker(self.store.photos_root, client=None)
            self.retention_worker.start()
        for path in self.store.photos_root.glob('*/manifest.json'):
            with manifest_lock(path):
                manifest = json.loads(path.read_text(encoding='utf-8'))
                if manifest.get('purpose') != PURPOSE:
                    continue
                changed = False
                for job in manifest.get('test_print_jobs', {}).values():
                    if job['state'] == 'SENDING':
                        job['state'] = 'UNCERTAIN'
                        job['reason'] = 'Restart interrupted the send; never replay automatically.'
                        changed = True
                        self.recovered_prints += 1
                if changed:
                    write_json_atomic(path, manifest)
        if self.drive_client is not None and self.drive_worker is None and not self._closed.is_set():
            from photobooth.drive_pool import DriveSlotPool
            from .photo_drive import RetentionGuardedSync
            self.pool = DriveSlotPool(self.store.photos_root, self.root / 'drive-pool.json',
                                      self.store.booth_id, target_ready=2)
            self.drive_worker = RetentionGuardedSync(self.store.photos_root, self.drive_client, self.pool)
            self.drive_worker.start()

    def reset(self):
        if self.phase not in {'confirm', 'done'}:
            raise ValueError('Finish the current photo test before starting another.')
        self.transaction = None
        self.sessions = []
        self.index = 0
        self._retake = False
        self.phase = 'confirm'
        return self.snapshot()

    @property
    def session(self):
        if not self.sessions:
            raise ValueError('No admitted photo test.')
        return self.sessions[self.index]

    def _edit(self, callback):
        path = self.transaction.manifest_path
        with manifest_lock(path):
            manifest = json.loads(path.read_text(encoding='utf-8'))
            callback(manifest)
            write_json_atomic(path, manifest)
            self.transaction.manifest = manifest

    def start(self, templates, quantities):
        if self.phase != 'confirm' or self._closed.is_set():
            raise ValueError('Photo test already started or closed.')
        known = {item.template_id for item in templates}
        if set(quantities) - known or any(isinstance(n, bool) or not isinstance(n, int) or
                                         not 0 <= n <= 9 for n in quantities.values()):
            raise ValueError('Choose 0–9 copies of known templates.')
        plans = build_session_plans(templates, quantities)
        if not plans:
            raise ValueError('Choose at least one template.')
        if self.pool is not None:
            if not self.pool.has_ready_slot():
                raise ValueError('Drive is enabled but no verified folder is ready; wait and retry.')
            slot = self.pool.claim()
            self.store.advance_counter_past(slot.transaction_id)
            tx = self.store.start_transaction(plans, transaction_id=slot.transaction_id,
                                             folder_path=Path(slot.staging_path), drive_slot=slot.to_manifest())
        else:
            tx = self.store.start_transaction(plans)
        self.transaction = tx
        self._edit(lambda m: m.update(purpose=PURPOSE, payment_enabled=False,
                                     financial_transaction=False, test_print_jobs={}))
        self.sessions = [PhotoSession(plan) for plan in plans]
        self.phase = 'capture'
        return self.snapshot()

    def capture(self, frame):
        if self.phase != 'capture' or frame is None:
            raise ValueError('A fresh camera frame is required in capture.')
        session = self.session
        if self._retake and not session.can_retake:
            raise ValueError('Retake allowance is unavailable.')
        # Camera frames are BGR and never mirrored. Own the RGB pixels on this worker.
        image = Image.fromarray(frame[:, :, ::-1].copy(), 'RGB')
        name = 'retake.jpg' if self._retake else f'photo_{len(session.initial_photo_paths) + 1:02d}.jpg'
        path = self.store.save_raw_photo(self.transaction, session.plan, image, name,
                                        'retake' if self._retake else 'capture')
        if self._retake:
            self.store.record_retake(self.transaction, session.plan.session_id,
                                     session.initial_photo_paths[session.selected_index])
            session.apply_retake(path)
            self._retake = False
        else:
            session.add_initial_photo(path)
        self.phase = 'review' if session.ready_for_review else 'capture'
        return self.snapshot()

    def retake(self, index):
        if self.phase != 'review':
            raise ValueError('Review all three photos before a retake.')
        self.session.select_photo(index)
        if not self.session.can_retake:
            raise ValueError('One retake per session has already been used.')
        self._retake = True
        self.phase = 'capture'
        return self.snapshot()

    def compose(self):
        if self.phase != 'review' or not self.session.ready_for_review:
            raise ValueError('Three reviewed photos are required.')
        session = self.session
        output = self.transaction.folder_path / 'output' / f'{session.plan.session_id}.png'
        with self.store.photo_write_lock(self.transaction):
            compose_result(session.final_photo_paths, session.plan.template, output,
                           self.transaction.transaction_id, session.plan.session_id,
                           self.transaction.manifest.get('drive_folder_url'))
            self.store.record_output(self.transaction, session.plan.session_id,
                                     session.final_photo_paths, output)
        session.output_path = output
        self.phase = 'result'
        if self.index == len(self.sessions) - 1:
            self.store.complete_transaction(self.transaction)
        if self.drive_worker:
            self.drive_worker.kick()
        return self.snapshot()

    def print_result(self):
        if self.phase != 'result' or self.printer is None:
            raise ValueError('Test printing is unavailable.')
        session = self.session
        key = session.plan.session_id
        def reserve(manifest):
            if key in manifest['test_print_jobs']:
                raise ValueError('This strip has already been submitted; inspect the printer.')
            manifest['test_print_jobs'][key] = {'state': 'SENDING',
                'copies': session.plan.print_copies, 'output': str(session.output_path.name)}
        # Fsync BEFORE the external side effect. Any uncertainty prevents a duplicate retry.
        self._edit(reserve)
        try:
            result = self.printer.print_image(session.output_path, copies=session.plan.print_copies)
            state = 'SUBMITTED' if result.success else 'UNCERTAIN'
        except Exception:
            LOG.warning('Photo test print outcome uncertain', exc_info=True)
            state = 'UNCERTAIN'
        self._edit(lambda m: m['test_print_jobs'][key].update(state=state))
        return self.snapshot()

    def acknowledge_print(self):
        if self.phase != 'result':
            raise ValueError('Print acknowledgement belongs to results.')
        key = self.session.plan.session_id
        self._edit(lambda m: m['test_print_jobs'][key].update(operator_checked=True))
        return self.snapshot()

    def next(self):
        if self.phase != 'result':
            raise ValueError('Finish the current composition first.')
        view = self.snapshot()
        if view['print_state'] == 'UNCERTAIN' and not view['print_checked']:
            raise ValueError('Inspect the printer and acknowledge its uncertain outcome first.')
        if self.index + 1 < len(self.sessions):
            self.index += 1
            self.phase = 'capture'
        else:
            self.phase = 'done'
        return self.snapshot()

    def abort(self):
        if self.phase not in {'capture', 'review', 'result'}:
            raise ValueError('No active photo test to finish.')
        view = self.snapshot()
        if view['print_state'] in {'SENDING', 'UNCERTAIN'} and not view['print_checked']:
            raise ValueError('Inspect the printer before leaving an uncertain job.')
        self._edit(lambda m: m.update(test_ended_early=True))
        self.phase = 'done'
        return self.snapshot()

    def snapshot(self):
        if self.transaction is None:
            return {'phase': self.phase}
        manifest = json.loads(self.transaction.manifest_path.read_text(encoding='utf-8'))
        session = self.session
        job = manifest.get('test_print_jobs', {}).get(session.plan.session_id, {})
        thumbnails = []
        for path in session.final_photo_paths:
            with Image.open(path) as photo:
                photo = photo.convert('RGB')
                photo.thumbnail((320, 240))
                thumbnails.append(photo.copy())
        strip = None
        if session.output_path:
            with Image.open(session.output_path) as photo:
                strip = photo.convert('RGB')
                strip.thumbnail((320, 960))
        return {'phase': self.phase, 'transaction_id': self.transaction.transaction_id,
                'session_number': self.index + 1, 'session_count': len(self.sessions),
                'template': session.plan.template.name, 'copies': session.plan.print_copies,
                'captured': len(session.initial_photo_paths), 'retake': self._retake,
                'retake_used': session.retake_used, 'thumbnails': thumbnails, 'strip': strip,
                'print_available': self.printer is not None, 'print_state': job.get('state', 'NOT_SENT'),
                'print_checked': job.get('operator_checked', False),
                'upload_status': manifest['upload_status'],
                'folder_url': manifest.get('drive_folder_url'),
                'folder': str(self.transaction.folder_path),
                'retention_error': bool(manifest.get('drive_retention_error'))}

    def close(self):
        self._closed.set()
        if self.drive_worker:
            self.drive_worker.stop()
        if self.retention_worker:
            self.retention_worker.stop()


@dataclass
class PhotoOutcome:
    action: str
    value: dict | None = None
    error: str | None = None


class PhotoJobs:
    """One in-flight command, no queued repeated taps and no GUI worker callbacks."""

    def __init__(self, service=None, *, factory=None):
        self.service = service
        self._factory = factory
        self._results = queue.Queue(maxsize=1)
        self._thread = None
        self._closed = False
        self.busy = False

    def submit(self, action, *args):
        if self.busy or self._closed:
            return False
        self.busy = True
        def run():
            try:
                if self.service is None:
                    self.service = self._factory()
                    if self._closed:
                        self.service.close()
                        return
                value = getattr(self.service, action)(*args)
                result = PhotoOutcome(action, value)
            except Exception as error:
                LOG.warning('Photo test action failed: %s', action, exc_info=True)
                result = PhotoOutcome(action, error=type(error).__name__)
                try:
                    if self.service is not None:
                        result.value = self.service.snapshot()
                except Exception:
                    pass
            if not self._closed:
                self._results.put(result)
        self._thread = threading.Thread(target=run, name='portrait-v2-photo-io', daemon=True)
        self._thread.start()
        return True

    def poll(self):
        try:
            result = self._results.get_nowait()
        except queue.Empty:
            return None
        self.busy = False
        return result

    def close(self):
        self._closed = True
        if self.service is not None:
            self.service.close()

    def wait_closed(self, timeout=3):
        if self._thread:
            self._thread.join(timeout=timeout)


def configured_test(root, *, configuration_root=None):
    """Operator opt-ins affect only P3 photo tests, never payment admission."""
    import os
    printer = client = None
    configuration_root = Path(configuration_root) if configuration_root else Path(root).parents[1]
    if os.environ.get('PHOTOBOOTH_V2_PRINT') == '1':
        from photobooth.printer import ThermalPrinter
        from photobooth.printer_settings import load_printer_config
        printer = ThermalPrinter(load_printer_config(configuration_root / 'data' / 'printer_settings.json'))
    if os.environ.get('PHOTOBOOTH_V2_DRIVE') == '1':
        from photobooth.drive_storage import AppsScriptDriveClient, GoogleDriveClient
        client = AppsScriptDriveClient.from_configuration() or GoogleDriveClient.from_environment()
        if client is None:
            raise ValueError('Drive opt-in requires configured credentials; no fake download QR.')
    booth_id = os.environ.get('PHOTOBOOTH_V2_BOOTH_ID', 'PB001V2')
    if not booth_id.endswith('V2'):
        raise ValueError('P3 booth IDs must end in V2 to isolate the remote pool from v1.')
    return PhotoTest(root, booth_id=booth_id,
                     printer=printer, drive_client=client)
