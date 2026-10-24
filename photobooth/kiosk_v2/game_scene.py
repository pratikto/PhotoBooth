"""Thin v2 host for the unchanged latest MeongFlyStage and MeongFlyFlow.

All painting, camera/film composition, animation and physics come from the
original modules. Only input, async ledger and kiosk lifecycle are adapted.
"""

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle

from photobooth.meong_fly_flow import MeongFlyFlow
from photobooth.meong_fly_gui import MeongFlyStage
from photobooth.meong_fly_painter import ACTIONS


class ClaimedAttempt:
    """Bridge original flow callbacks to the already durable v2 claim/result."""

    def __init__(self, host):
        self.host = host

    def claim(self, code):
        attempt = self.host._game_attempt
        return bool(attempt and attempt['token'] == code and attempt['result'] == 'started')

    def finish(self, code, won):
        attempt = self.host._game_attempt
        if attempt and attempt['token'] == code:
            self.host._finish_game_demo('won' if won else 'lost')


class KioskGameFlow(MeongFlyFlow):
    def __init__(self, host):
        self.host = host
        super().__init__(ClaimedAttempt(host), tutorial_seen=host.navigation.tutorial_seen)

    def flap(self):
        stage = self.host._game_field
        if stage is None or not stage.input_allowed():
            return False
        accepted = super().flap()
        if accepted:
            self.host.audio_v2.cue('button')
        return accepted

    def tick(self, dt):
        if self.host._closed or self.host._suspended or self.host._game_jobs.busy:
            return
        # Original tick owns physics, score and terminal transition. The ledger
        # callback queues persistence; v2 blocks result CTA until it is acked.
        super().tick(dt)


class KioskGameStage(MeongFlyStage):
    def __init__(self, host, flow, **kwargs):
        self.host = host
        self._mounted = self._disposed = False
        self._mount_revision = -1
        super().__init__(flow, scanner=None, **kwargs)
        self.detach()

    def input_allowed(self):
        return (not self._disposed and self._mounted and not self.host._closed and
                not self.host._suspended and not self.host._game_jobs.busy and
                self.host._game_field is self and self._mount_revision == self.host._view_revision)

    def mount(self):
        if self._disposed:
            raise RuntimeError('Cannot mount a retired Meong Fly stage.')
        self._mounted = True
        self._mount_revision = self.host._view_revision
        if self._update_event is None:
            self._update_event = Clock.schedule_interval(self.update, 1/30)
            Window.bind(mouse_pos=self._mouse_moved)
        self._refresh()

    def detach(self):
        self._mounted = False
        if self._update_event is not None:
            self._update_event.cancel()
            self._update_event = None
        Window.unbind(mouse_pos=self._mouse_moved)
        self.receipt.focus = False
        self.receipt.disabled = True
        if self.parent is not None:
            self.parent.remove_widget(self)

    def dispose(self):
        self.detach()
        self._disposed = True
        super().dispose()

    def update(self, dt):
        if self._mounted and not self._disposed and not self.host._closed and not self.host._suspended:
            super().update(dt)

    def _refresh(self):
        super()._refresh()
        # Keep the original scene/sprites at their correct aspect ratio while
        # the existing full-window Starfield shows through its unused margins.
        # Only remove the standalone's opaque letterbox plate, not its art.
        plate = next((item for item in self.canvas.before.children if isinstance(item, Rectangle)), None)
        if (plate is not None and tuple(plate.pos) == tuple(self.pos) and
                tuple(plate.size) == tuple(self.size)):
            plate.size = (0, 0)

    def _sync_overlays(self):
        super()._sync_overlays()
        self.receipt.disabled = self.receipt.disabled or self.host._game_jobs.busy or not self._mounted
        if self.flow.screen == 'scan':
            self.notice.text = (self.host._game_error or
                                ('Memeriksa kode DEMO…' if self.host._game_jobs.busy else
                                 'Scanner nonaktif. Ketik kode DEMO baru.'))

    def validate_receipt(self):
        if self.input_allowed():
            self.host._claim_game_demo()
            self._refresh()

    def _handle_action(self, action):
        if not self.input_allowed() or action not in ACTIONS.get(self.flow.screen, {}):
            return
        callbacks = {
            'game': self.host._open_game_demo,
            'photo': lambda:self.host._choose_photo('skip_game'),
            'back': self.host._back_game_intro,
            'validate': self.validate_receipt,
            'pause': self.host._toggle_game_pause,
            'continue': self.host._continue_game_photo,
        }
        callback = callbacks.get(action)
        if callback is not None:
            self.host.audio_v2.cue('button')
            callback()

    def _mouse_moved(self, window, position):
        if self.input_allowed():
            super()._mouse_moved(window, self.to_widget(*position))

    def on_touch_down(self, touch):
        if (not self.input_allowed() or getattr(touch, 'is_mouse_scrolling', False) or
                getattr(touch, 'button', 'left') in {'right', 'middle'}):
            return False
        if self.collide_point(*touch.pos) and self.flow.screen == 'game':
            # The responsive side areas are also valid flight input. The actual
            # playfield/physics and original pause hitbox stay unchanged.
            ox, oy, scale = self._viewport()
            if not (ox <= touch.x <= ox+360*scale and oy <= touch.y <= oy+720*scale):
                return self.flow.flap()
        return super().on_touch_down(touch)
