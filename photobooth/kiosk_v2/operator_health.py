"""Mount the original v1 operator panel; customer screens retain native v2 flow."""
from time import monotonic
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from photobooth.advertising import PROJECT_ROOT
from photobooth.ui_health import HealthPanelMixin
from photobooth.ui_kivy import PhotoBoothUI
from .branding import MeongLogo
from .demo_game import GameJobs
from .flow import ADVERT, SANDBOX_CHECKOUT
from .health_report import HealthReportStore
from .health_service import V2HealthController
from .theme import ArcadeButton


class MainThreadScheduler:
    """Adapt v1 root.after to the existing Kivy main loop, no extra poll thread."""
    def __init__(self, app):
        self.app = app

    def after(self, milliseconds, callback):
        def deliver(_dt):
            if not self.app._closed:
                callback()
        return Clock.schedule_once(deliver, milliseconds/1000)


class OperatorPanel(HealthPanelMixin):
    # Use the exact existing caption helper and the full original health GUI.
    _label = PhotoBoothUI._label

    def __init__(self, app, controller):
        self.app, self.controller = app, controller
        self._disposed = False
        self._health_popup = self._device_pick_popup = None
        self._health_request_serial = 0
        self._health_labels = {}
        self._health_inventory = ()
        self._health_platform = 'unknown'
        self._health_refresh_button = self._health_select_button = None
        self.snapshot = None
        # No selection callback: the original PILIH DEVICE stays disabled.
        self.callbacks = {'on_health_refresh':self._refresh}

    def _button(self, text, callback, enabled=True, secondary=False, **_kwargs):
        # The v1 helper owns AudioManager/screen revisions. Adapt this seam to
        # the existing v2 owner instead of instantiating a second legacy GUI.
        button = ArcadeButton(text, variant='tertiary' if secondary else 'secondary',height=48)
        button.font_size = dp(12)
        button.disabled = not enabled
        armed = False
        next_allowed = float('-inf')

        def available():
            return not (button.disabled or self._disposed or self._health_popup is None or
                        self.app._closed or self.app._suspended)

        def press(*_):
            nonlocal armed
            # Native releases can arrive after a disabled/held button becomes
            # enabled again. Only its own fresh, permitted press may act.
            armed = available() and monotonic() >= next_allowed

        def release(*_):
            nonlocal armed, next_allowed
            accepted, armed = armed, False
            if not accepted or not available() or monotonic() < next_allowed:
                return
            # Drop fast duplicates instead of scheduling them. Even an immediate
            # probe/file result must not allow an input burst to churn threads,
            # inventory widgets/files or native audio stop/play calls. This is
            # per button: TUTUP stays usable while another action is busy.
            next_allowed = monotonic() + .75
            self.app._activity()
            # Let the existing callback claim/disable its controls first. No
            # queued event can slip in while the native click provider runs.
            callback()
            self.app.audio_v2.cue('button')
        button.bind(on_press=press, on_release=release)
        return button

    def _refresh(self, callback):
        self.snapshot = None
        self.export_button.disabled = True
        self.report_message.text = ''
        popup, serial = self._health_popup, self._health_request_serial
        def completed(snapshot):
            if (self._disposed or self._health_popup is not popup or
                    self._health_request_serial != serial or self.app._suspended):
                return
            self.snapshot = snapshot
            callback(snapshot)
            self.export_button.disabled = snapshot is None or self.app._health_reports.busy
        self.controller.refresh(completed)

    def open(self):
        # These are created first because the unchanged panel refreshes on entry.
        self.export_button = self._button('SIMPAN LAPORAN LOKAL',self._export,enabled=False)
        self.report_message = self._label('',12,48)
        popup = self.show_health_settings()
        actions = BoxLayout(orientation='vertical',size_hint_y=None,height=dp(104),spacing=dp(6))
        actions.add_widget(self.export_button);actions.add_widget(self.report_message)
        popup.content.add_widget(actions)
        def closed(*_):
            self._disposed = True
            self.app._operator_closed(self)
        popup.bind(on_dismiss=closed)
        return popup

    def _export(self):
        if self.snapshot is None or self._health_refresh_button.disabled:
            return
        if self.app._health_reports.submit('save',self.app._operator_epoch,self.snapshot):
            self.export_button.disabled = True
            self._health_refresh_button.disabled = True
            self.report_message.text = 'Menyimpan metadata tanpa foto atau kredensial…'

    def exported(self, outcome):
        self._health_refresh_button.disabled = False
        self.export_button.disabled = self.snapshot is None
        self.report_message.text = ('Laporan belum tersimpan. Coba lagi.' if outcome.error else
                                    'Tersimpan di data/diagnostics:\n'+outcome.value['file'])

    def close(self):
        if self._health_popup is not None:
            self._health_popup.dismiss(animation=False)
        self._disposed = True


class OperatorMeongLogo(MeongLogo):
    """Touch-only operator entry without adding controls to the photo journey."""
    def __init__(self, *, operator_open, operator_allowed, **kwargs):
        self._operator_open, self._operator_allowed = operator_open, operator_allowed
        self._hold_event = self._hold_touch = None
        super().__init__(**kwargs)

    def _cancel_hold(self):
        if self._hold_event:
            self._hold_event.cancel();self._hold_event = None
        touch,self._hold_touch = self._hold_touch,None
        if touch is not None:
            touch.ungrab(self)

    def _held(self, _dt):
        allowed = self._hold_touch is not None and self.parent is not None and self._operator_allowed()
        self._cancel_hold()
        if allowed:
            self._operator_open()

    def on_touch_down(self,touch):
        if (self._hold_touch is None and getattr(touch,'button',None) in (None,'left') and
                self.collide_point(*touch.pos) and self._operator_allowed()):
            self._hold_touch = touch
            self._hold_origin = touch.pos
            touch.grab(self)
            self._hold_event = Clock.schedule_once(self._held,1.5)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self,touch):
        if touch is self._hold_touch:
            if ((touch.x-self._hold_origin[0])**2+(touch.y-self._hold_origin[1])**2)>dp(18)**2:
                self._cancel_hold()
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self,touch):
        if touch is self._hold_touch:
            self._cancel_hold();return True
        return super().on_touch_up(touch)

    def set_active(self,active):
        if not active:
            self._cancel_hold()
        super().set_active(active)

    def dispose(self):
        self._cancel_hold()
        super().dispose()


class OperatorViews:
    def _init_operator(self):
        self._operator_panel = None
        self._operator_epoch = 0
        self._operator_last_tick = None
        self._operator_controller = None
        self._health_reports = GameJobs(lambda:HealthReportStore(PROJECT_ROOT),actions={'save'})
        Window.bind(on_keyboard=self._operator_key)

    @property
    def _operator_active(self):
        return self._operator_panel is not None

    def _operator_allowed(self):
        if self._closed or self._suspended or self._operator_active:
            return False
        if self._photo_jobs and self._photo_jobs.busy:
            return False
        if self._game_jobs.busy or self._mock_jobs.busy or (self._sandbox_jobs and self._sandbox_jobs.busy):
            return False
        return ((self.navigation.page == ADVERT and self._invitation is None) or
                (self.navigation.page == SANDBOX_CHECKOUT and
                 (self._sandbox_view or {}).get('phase') == 'RECOVERY'))

    def _operator_key(self,_window,key,*_args):
        code = key[0] if isinstance(key,(tuple,list)) else key
        if code != 293:  # Kivy F12
            return False
        if self._operator_active:
            return True
        if self._operator_allowed():
            self._open_operator();return True
        return False

    def _open_operator(self):
        if not self._operator_allowed():
            return
        self._operator_epoch += 1
        self.face_inviter.pause();self.palm_shutter.pause()
        if self._operator_controller is None:
            self._operator_controller = V2HealthController(self,MainThreadScheduler(self),PROJECT_ROOT)
        self._operator_panel = OperatorPanel(self,self._operator_controller)
        self._operator_panel.open()

    def _operator_closed(self,panel):
        if self._operator_panel is panel:
            self._operator_panel = None
            self._operator_epoch += 1
            if not self._closed:
                self._activity()

    def _close_operator(self):
        panel = self._operator_panel
        if panel:
            panel.close()

    def _poll_operator(self):
        outcome = self._health_reports.poll()
        if outcome is not None and self._operator_panel and not self._suspended:
            if outcome.revision == self._operator_epoch and not self._operator_panel._disposed:
                self._operator_panel.exported(outcome)
        panel = self._operator_panel
        if panel and not panel._disposed and not self._suspended:
            # A report from a closed panel may finish while a fresh panel is
            # already open. Retire its message, but release the export affordance.
            panel.export_button.disabled = (panel.snapshot is None or self._health_reports.busy or
                                            panel._health_refresh_button.disabled)
