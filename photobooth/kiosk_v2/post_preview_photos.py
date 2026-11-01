"""Private post-preview worker facade for the original PhotoJobs/PhotoViews.

Not mounted in the application yet. Snapshot generation/slot/revision are
mandatory capture-command inputs; existing legacy service behavior is unchanged.
"""
import threading
import uuid

from PIL import Image, ImageOps

from photobooth.booth_storage import checked_path
from photobooth.post_preview_checkout import PrivateDraftCheckout
from photobooth.post_preview_photos import PrivateDraftPhotos
from photobooth.post_preview_store import DraftHeld, PostPreviewStore


class PrivatePhotoService:
    def __init__(self, root, *, booth_id='PB001', policy=None):
        self.root = checked_path(root)
        self.ledger = PostPreviewStore(self.root/'drafts.sqlite3')
        self.photos = PrivateDraftPhotos(self.ledger, self.root/'media', policy=policy)
        self.checkout = PrivateDraftCheckout(self.photos)
        self.booth_id = booth_id
        self.lease = None
        self.templates = []
        self.selected = []
        self.index = 0
        self.phase = 'confirm'
        self._hidden = threading.Event()
        self._closed = threading.Event()
        self._cleanup_thread = None
        self._generation = 1
        self._preview = None

    def _active(self):
        if self._hidden.is_set() or self._closed.is_set():
            raise DraftHeld('Private visitor visibility has retired')

    def prepare(self):
        self._active()
        self.photos.policy.inspect(self.root)
        # A restart never reconstructs/displays prior customer media or silently
        # admits B. Returning-customer proof and exact release arrive in PP-06.
        with self.ledger.write():
            if self.ledger.db.execute('SELECT 1 FROM pp_drafts WHERE booth_id=? AND closed=0',
                                      (self.booth_id,)).fetchone():
                self.phase = 'hold'
        return self.snapshot()

    def start(self, templates, quantities):
        self._active()
        if self.phase != 'confirm':
            raise DraftHeld('Original visitor must finish or safely isolate first')
        known = {t.template_id for t in templates}
        if (set(quantities)-known or any(type(v) is not int or not 0 <= v <= 9 for v in quantities.values())):
            raise ValueError('Select known templates and zero to nine copies')
        cart = {key: value for key, value in quantities.items() if value > 0}
        if self.lease is None:
            self.lease = self.ledger.create(self.booth_id, uuid.uuid4().hex, cart)
        else:
            self.ledger.edit(self.lease, cart, revision=self._revision())
        self.photos.prepare(self.lease)
        self.templates = list(templates)
        self.selected = [t for t in templates if t.template_id in cart]
        self.index = 0
        self._preview = None
        self.phase = self._phase_for_current()
        return self.snapshot()

    def _revision(self):
        return self.ledger.inspect(self.lease)['revision']

    def reset(self):
        self._active()
        if self.phase != 'confirm':
            raise DraftHeld('A private draft cannot be reset')
        return self.snapshot()

    def abort(self):
        return self.retire('USER_CANCEL')

    def warn(self):
        self._active()
        if self.lease is not None:
            self.ledger.lifecycle_event(self.lease, 'INACTIVITY_WARNING')
        return self.snapshot()

    @property
    def template(self):
        return self.selected[self.index]

    def _phase_for_current(self):
        view = self.photos.inspect(self.lease, self.template)
        return ('capture' if view['original_count'] < 3 or
                view['retake_consumed'] and not view['retake_saved'] else 'review')

    def capture(self, frame, slot, revision, retake, generation):
        self._active()
        if self.phase != 'capture' or generation != self._generation:
            raise DraftHeld('Original camera command has retired')
        if (getattr(frame, 'ndim', None) != 3 or frame.shape[2] != 3
                or str(frame.dtype) != 'uint8'):
            raise ValueError('Fresh three-channel BGR camera frame required')
        # Same original BGR -> RGB conversion as PhotoTest.capture; no mirroring.
        image = Image.fromarray(frame[:, :, ::-1].copy(), 'RGB')
        self.photos.capture(self.lease, self.template, image, slot=slot,
                            revision=revision, retake=retake)
        self._preview = None
        self.phase = self._phase_for_current()
        return self.snapshot()

    def retake(self, slot):
        self._active()
        if self.phase != 'review':
            raise DraftHeld('Original trio review required')
        self.photos.request_retake(self.lease, self.template, slot, revision=self._revision())
        self._preview = None
        self.phase = 'capture'
        return self.snapshot()

    def compose(self):
        self._active()
        if self.phase != 'review':
            raise DraftHeld('Explicit final trio approval required')
        self._preview = self.checkout.approve(self.lease, self.template, revision=self._revision())
        self.phase = 'result'
        return self.snapshot()

    def next(self):
        self._active()
        if self.phase != 'result':
            raise DraftHeld('Approve original preview before continuing')
        self._preview = None
        if self.index+1 < len(self.selected):
            self.index += 1
            self.phase = self._phase_for_current()
        else:
            self.phase = 'final_preview'
        return self.snapshot()

    def review(self, template_id):
        self._active()
        if self.phase not in {'result', 'final_preview'}:
            raise DraftHeld('Final preview required before revisiting a design')
        matches = [i for i, t in enumerate(self.selected) if t.template_id == template_id]
        if len(matches) != 1:
            raise DraftHeld('Original selected design required')
        self.index = matches[0]
        self._preview = None
        self.phase = self._phase_for_current()
        return self.snapshot()

    def edit(self):
        self._active()
        if self.phase != 'final_preview':
            raise DraftHeld('All-design final preview required before cart edits')
        self.phase = 'confirm'
        self._preview = None
        return self.snapshot()

    def hide_private(self):
        """Immediate nonblocking GUI privacy barrier, independent of disk I/O."""
        self._hidden.set()
        self._generation += 1
        self._preview = None

    def retire(self, event):
        # Execute on the serialized worker after the GUI has hidden pixels.
        self.hide_private()
        if self.lease is not None:
            self.ledger.lifecycle_event(self.lease, event)
        self.phase = 'hold'
        return {'phase': 'hold'}

    def snapshot(self):
        if self._hidden.is_set() or self._closed.is_set():
            return {'phase': 'hold'}
        generation = self._generation
        configuration = {'phase': self.phase, 'generation': generation,
                         'print_available': False, 'auto_print': False,
                         'drive_enabled': False, 'drive_ready': True, 'drive_error': False,
                         'storage_layout': 2, 'recovered_prints': 0,
                         'download_qr': None, 'folder_url': None, 'upload_status': 'LOCAL_ONLY',
                         'print_state': 'NOT_SENT', 'print_checked': False}
        if self.lease is None or self.phase in {'confirm', 'hold'}:
            return configuration
        state = self.ledger.inspect(self.lease)
        if self.phase == 'final_preview':
            designs = []
            for template in self.selected:
                preview = self.checkout.preview(self.lease, template, revision=state['revision'])
                with Image.open(preview['preview_path']) as source:
                    strip = source.convert('RGB')
                    strip.thumbnail((160, 480))
                designs.append({'template_id': template.template_id, 'name': template.name,
                                'copies': state['quantities'][template.template_id], 'strip': strip})
            result = {**configuration, 'designs': designs, 'amount': state['amount'],
                      'revision': state['revision']}
        else:
            media = self.photos.inspect(self.lease, self.template)
            row = next(r for r in state['templates'] if r['template_id'] == self.template.template_id)
            thumbnails = []
            for path in media['final_paths']:
                with Image.open(path) as source:
                    photo = source.convert('RGB')
                    photo.thumbnail((320, 240))
                    thumbnails.append(ImageOps.mirror(photo))
            strip = None
            if self._preview:
                with Image.open(self._preview['preview_path']) as source:
                    strip = source.convert('RGB')
                    strip.thumbnail((320, 960))
            pending = media['retake_consumed'] and not media['retake_saved']
            result = {**configuration, 'revision': state['revision'],
                      'template_id': self.template.template_id, 'template': self.template.name,
                      'copies': row['copies'], 'session_number': self.index+1,
                      'session_count': len(self.selected), 'captured': media['original_count'],
                      'retake': pending, 'retake_used': media['retake_consumed'],
                      'capture_slot': row['retake_slot'] if pending else media['original_count'],
                      'thumbnails': thumbnails, 'strip': strip}
        if self._hidden.is_set() or self._closed.is_set() or generation != self._generation:
            return {'phase': 'hold'}
        return result

    def close(self):
        self.hide_private()
        self._closed.set()
        if self._cleanup_thread is None:
            self._cleanup_thread = threading.Thread(target=self.ledger.close,
                name='private-draft-close', daemon=True)
            self._cleanup_thread.start()

    def wait_closed(self, timeout=3):
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout)
