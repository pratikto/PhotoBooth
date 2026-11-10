"""Original protected views with bounded public visit control.

Explicit integration profile only. The trusted launcher retains the worker;
this app has no manager/config/key/provider handle. Complete customer launcher,
global launch ownership and supported boot remain separately gated.
"""
from kivy.metrics import dp

from photobooth.post_preview_visit_control import VisitControl
from .app import PortraitKioskV2App
from .flow import ADVERT, RESULT
from .photo_views import PhotoViews
from .post_preview_protected_app import ProtectedCheckoutApp
from .theme import ArcadeButton


class ProtectedVisitsApp(ProtectedCheckoutApp):
    def __init__(self, private_root, *, visit_control, **kwargs):
        if (type(visit_control) is not VisitControl or visit_control.binding is None
                or visit_control.busy or visit_control.state!='READY'):
            raise TypeError('Original accepted public visit binding required')
        self._visit_control=visit_control
        self._visit_ready=True
        self._visit_needs_ready=False
        self._visit_entry=None
        super().__init__(private_root,private_service=visit_control.binding.service,**kwargs)

    def _init_photos(self):
        # Initialize the original view state, but NEVER wrap the service in a
        # second PhotoJobs: its collector is bound to this exact original one.
        PhotoViews._init_photos(self)
        self._photo_jobs=self._visit_control.binding.jobs

    def _close_photo_jobs(self):
        # No ledger close on the GUI thread or under unfinished native I/O.
        # The separately retained trusted worker owns actual drain/shutdown.
        self._close_pilot_popup()
        self._visit_entry=None
        self._visit_control.request_stop()

    def on_stop(self):
        if not self._closed:self._queue_private_retirement('APP_SUSPENDED')
        return super().on_stop()

    def _show(self):
        result=super()._show()
        if self.navigation.page==ADVERT and self._visit_control.busy:
            for widget in self.stage.walk():
                if isinstance(widget,ArcadeButton):widget.disabled=True
        return result

    def _build_advert(self,canvas):
        super()._build_advert(canvas)
        self._advert_host.parent.parent.add_widget(self._photo_action(
            'PUNYA TIKET PEMULIHAN',self._pilot_open_claim,
            variant='tertiary',height=dp(44),disabled=self._visit_control.busy))

    def _entry_allowed(self,action,source):
        if self._closed or self._suspended or self._visit_control.busy:return False
        service=self._photo_jobs.service
        if (self._visit_ready and not service._hidden.is_set()
                and service.lease is None and not self._photo_jobs._closed):
            if self.navigation.page==ADVERT:
                self._reset_visit()
                self.navigation.tutorial_seen=False
                self.navigation.entry_source=None
            return True
        if self.navigation.page==ADVERT and self._visit_control.ready():
            self._visit_entry=(action,source)
            self._visit_ready=False;self._visit_needs_ready=False
            self._pilot_note='Mengamankan sesi sebelumnya. Mohon tunggu.'
            self._show()
        return False

    def _choose_photo(self,source='manual'):
        if self._entry_allowed('photo',source):
            return PortraitKioskV2App._choose_photo(self,source)

    def _choose_game(self,source='manual'):
        if self._entry_allowed('game',source):
            return PortraitKioskV2App._choose_game(self,source)

    def _pilot_open_claim(self):
        if (self.navigation.page!=ADVERT or self._closed or self._suspended
                or self._visit_control.busy):return
        self._open_private_claim_popup('PEMULIHAN PRIVAT • SANDBOX')

    def _pilot_submit_claim(self,payload):
        if (self.navigation.page!=ADVERT or self._closed or self._suspended
                or self._visit_control.busy):return
        self._close_pilot_popup()
        try:submitted=self._visit_control.claim(payload.strip() if type(payload) is str else '')
        except ValueError:submitted=False
        if submitted:
            self._visit_entry=None;self._visit_needs_ready=False
            self._visit_ready=False
            self._pilot_note='Memeriksa tiket asli. Mohon tunggu.'
        else:
            self._pilot_note='Tiket tidak dapat diverifikasi. Foto privat tetap terlindungi.'
        self._show()

    def _queue_private_retirement(self,event):
        self._visit_entry=None;self._visit_ready=False
        self._visit_needs_ready=True
        self._private_pending_event=None
        self._visit_control.hide_private(event)
        self._private_hold()

    def _sandbox_lock_customer(self):
        # Even an empty-looking UI can have a claim committing on the worker.
        self._queue_private_retirement('APP_SUSPENDED')

    def _return_ad(self):
        self._queue_private_retirement('VISIT_ABANDONED')

    def _apply_binding(self,outcome):
        binding=outcome.binding
        if binding is None or binding is not self._visit_control.binding:
            raise RuntimeError('Original accepted native binding required')
        self._close_pilot_popup()
        self._photo_jobs=binding.jobs
        self._private_service=binding.service
        self._photo_prepared=False
        self._photo_pending_action=None
        self._private_warning_at=None
        self._photo_error='';self._photo_view={'phase':'confirm'}
        self._ticket_window=self._ticket_pending=self._ticket_card=None
        self._claim_pending=self._claim_card=None
        self._ticket_receipt_pending=self._ticket_dismiss_pending=False
        self._paid_result_deadline=None
        self._reset_visit()
        self.navigation.tutorial_seen=False
        self.navigation.entry_source=None

    def _poll_visit_control(self):
        if self._closed or self._suspended:return
        control=self._visit_control
        outcome=control.poll()
        if outcome is not None:
            entry,self._visit_entry=self._visit_entry,None
            self._visit_needs_ready=False
            if outcome.state in {'READY','RESTORED'}:
                self._apply_binding(outcome)
                self._visit_ready=True;self._pilot_note=''
                if outcome.state=='RESTORED':
                    self._photo_view=outcome.snapshot
                    self.navigation.page=RESULT
                    self._show()
                    if not self._photo_view.get('ticket_dismissed'):
                        self._photo_submit('prepare_ticket')
                    elif self._photo_jobs.service.paid_delivery_enabled:
                        # Reopen the SAME original immutable bundle/status.
                        # Submitted/uncertain output remains protected by the
                        # original delivery ledger; no new payment or replay.
                        self._photo_submit('prepare_paid_delivery')
                else:
                    self.navigation.page=ADVERT
                    if entry is not None:
                        action,source=entry
                        if action=='photo':self._choose_photo(source)
                        else:self._choose_game(source)
                    else:self._show()
            else:
                self._visit_ready=False
                self._pilot_note={
                    'WAIT':'Photobooth sedang digunakan. Silakan coba lagi nanti.',
                    'DENIED':'Tiket tidak dapat diverifikasi. Foto privat tetap terlindungi.',
                }.get(outcome.state,'Sesi sebelumnya belum bisa diamankan. Pembayaran baru ditahan.')
                self.navigation.page=ADVERT;self._show()
        elif self._visit_needs_ready and not control.busy and self.navigation.page==ADVERT:
            if control.ready():
                self._visit_needs_ready=False
                self._pilot_note='Mengamankan sesi sebelumnya. Mohon tunggu.'
                self._show()

    def _poll_photos(self):
        self._poll_visit_control()
        if (not self._visit_ready or self._visit_control.busy
                or self._photo_jobs.service._hidden.is_set()):return
        return super()._poll_photos()

    def _photo_submit(self,action,*args):
        if action=='abort':return self._queue_private_retirement('USER_CANCEL')
        if not self._visit_ready or self._visit_control.busy:return
        return super()._photo_submit(action,*args)

    def _photo_capture_allowed(self):
        return (self._visit_ready and not self._visit_control.busy
                and super()._photo_capture_allowed())

    def _original_freeze_ready(self):
        binding=self._visit_control.binding
        return (not self._closed and not self._suspended and self._visit_ready
                and not self._visit_control.busy and self._visit_control.state=='READY'
                and binding is not None and binding.jobs is self._photo_jobs
                and binding.service is self._photo_jobs.service
                and binding.service.phase=='final_preview' and binding.service.group is None
                and not binding.service._hidden.is_set() and not self._photo_jobs._closed
                and not self._photo_jobs.busy and self.navigation.page==RESULT
                and self._photo_view.get('phase')=='final_preview')

    def _photo_action(self,title,callback,**kwargs):
        if title=='PEMBAYARAN BELUM TERHUBUNG':
            title,callback='LANJUT PEMBAYARAN QRIS',self._freeze_checkout
            kwargs['disabled']=not self._original_freeze_ready()
        return super()._photo_action(title,callback,**kwargs)

    def _freeze_checkout(self):
        # Button visibility is never authority. The exact original worker and
        # backend independently recheck scope/media/device/Drive before commit.
        if not self._original_freeze_ready():return
        return super()._freeze_checkout()
