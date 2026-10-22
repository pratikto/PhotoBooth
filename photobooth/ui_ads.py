"""Main-thread media playback for the two advertising placements.

Only the mounted player owns a decoder. Page retirement unloads it, cancels
image/watchdog timers and records the actually displayed portion. A broken
creative is skipped once per player, preventing a corrupt-file retry loop.
Payment audio is forced to zero before a Video can begin loading.
"""

import logging
import os

os.environ.setdefault('KIVY_VIDEO', 'ffpyplayer')

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.video import Video

from photobooth.ui_brand import BLUE, GREY, BrandLockup


LOG = logging.getLogger(__name__)


class GuardedVideo(Video):
    """Turn decoder/provider failures on Kivy's scheduled load into a skip."""

    def __init__(self, failure, **kwargs):
        self.failure = failure
        self._retired = False
        super().__init__(**kwargs)

    def texture_update(self, *args):
        # Kivy 2.3.1's Video inherits Image and probes source as a still when
        # no preview is supplied. A movie belongs only to its video decoder.
        # The player already displays its separate poster/fallback while loading.
        if self._retired:
            return
        if self.preview:
            self.set_texture_from_resource(self.preview)
        else:
            self._clear_core_image()

    def _do_video_load(self, *args):
        if self._retired:
            return
        try:
            super()._do_video_load(*args)
        except Exception:
            LOG.warning('Advertising video could not be loaded', exc_info=True)
            self.failure(self)

    def retire(self):
        """Cancel a queued load as well as releasing an existing decoder.

        Video.unload() alone does not cancel Kivy's next-frame load event.
        A quick page change must not start an invisible decoder afterwards.
        """
        self._retired = True
        if self._video_load_event is not None:
            self._video_load_event.cancel()
        self.volume = 0
        self.state = 'stop'
        self.unload()


class AdvertisementPlayer(FloatLayout):
    """Fit local photos/videos and rotate at image duration or video EOS.

    A preview poster is visible while a video loads. Preview-only renders are
    available with PHOTOBOOTH_AD_VIDEO=0, but do not count as video playback.
    Missing/empty playlists always show a usable branded poster.
    """

    def __init__(self, catalog, placement, events, volume=.5, on_media_change=None, **kwargs):
        super().__init__(**kwargs)
        self.catalog, self.placement, self.events = catalog, placement, events
        # Optional consumer notification; legacy callers retain their audio policy.
        self._media_changed = on_media_change
        self._media_kind = None
        self.volume = 0 if placement == 'payment' else volume
        self.current = self.video = None
        self._index = -1
        self._seconds = self._last_position = 0.0
        self._unreported_wall = self._stalled_for = 0.0
        self._ready = self._paused = self._closed = False
        self._failed = set()
        self._scheduled = []
        self._tick_event = None
        self._fallback = FloatLayout(pos_hint={'x': 0, 'y': 0})
        logo = BrandLockup(size_hint=(.65, None), height=dp(140),
                           pos_hint={'center_x': .5, 'center_y': .57})
        self._fallback.add_widget(logo)
        caption = Label(text='Bikin kenangan bersama Meong', color=BLUE,
                        font_size=dp(20), bold=True, size_hint=(1, None),
                        height=dp(40), pos_hint={'center_y': .34})
        self._fallback.add_widget(caption)
        self.add_widget(self._fallback)
        self.image = Image(fit_mode='contain', opacity=0, pos_hint={'x': 0, 'y': 0})
        self.add_widget(self.image)
        self.bind(parent=self._mounted)

    @property
    def ad_id(self):
        return self.current.ad_id if self.current else 'meong-fallback'

    def _mounted(self, *_args):
        if self.parent is not None and self._tick_event is None and not self._closed:
            self._tick_event = Clock.schedule_interval(self._tick, .1)
            self._later(lambda: self.next(), 0)

    def _later(self, callback, delay):
        event = Clock.schedule_once(lambda _dt: callback() if not self._closed else None, delay)
        self._scheduled.append(event)
        return event

    def _clear_media(self, completed=False):
        """Retire callbacks before releasing decoder handles and visible pixels."""
        for event in self._scheduled:
            event.cancel()
        self._scheduled.clear()
        if self.current is not None and self._seconds > 0:
            self.events.write('playback', ad_id=self.current.ad_id, placement=self.placement,
                              seconds=round(self._seconds, 3), completed=bool(completed))
        self._seconds = self._last_position = 0
        self._unreported_wall = self._stalled_for = 0.0
        self._ready = False
        previous, self.video = self.video, None
        if previous is not None:
            previous.retire()
            self.remove_widget(previous)
        self.current = None
        self.image.source = ''
        self.image.opacity = 0
        self._fallback.opacity = 1

    def _notify_media(self, kind):
        if kind != self._media_kind:
            self._media_kind = kind
            if self._media_changed is not None and not self._closed:
                self._media_changed(kind)

    def next(self, completed=False):
        if self._closed:
            return
        self._clear_media(completed)
        choices = [item for item in self.catalog.available(self.placement)
                   if item.path not in self._failed]
        if not choices:
            self._notify_media("fallback")
            self._later(self.next, 30)
            return
        eligible_indices = [index for index, item in enumerate(self.catalog.items) if item in choices]
        self._index = next((index for index in eligible_indices if index > self._index), eligible_indices[0])
        self.current = item = self.catalog.items[self._index]
        try:
            if item.video:
                # Retire GUI music before any native decoder can begin audio.
                self._notify_media("video")
                if item.poster and item.poster.is_file():
                    self.image.source = str(item.poster)
                    self.image.opacity = 1
                    self._fallback.opacity = 0
                if os.environ.get('PHOTOBOOTH_AD_VIDEO', '1') == '0':
                    # Synthetic GUI evidence never pretends a still is a view.
                    self._later(self.next, 30)
                    return
                video = GuardedVideo(self._failed_video, source=str(item.path),
                                     state='pause' if self._paused else 'play',
                                     volume=0 if self._paused else self.volume,
                                     fit_mode='contain', options={'eos': 'stop'}, pos_hint={'x': 0, 'y': 0})
                self.video = video
                video.bind(texture=self._texture_ready, eos=self._ended)
                self.add_widget(video)
                self._later(lambda: self._failed_video(video) if not self._ready else None, 10)
            else:
                # Pillow verifies files off the critical frame loop only when
                # a new creative starts; a corrupt image is skipped like video.
                from PIL import Image as PillowImage
                with PillowImage.open(item.path) as source:
                    source.verify()
                self.image.source = str(item.path)
                self.image.opacity = 1
                self._fallback.opacity = 0
                self._ready = True
                self._notify_media("image")
        except Exception:
            LOG.warning('Skipping unplayable advertising asset %s', item.path, exc_info=True)
            self._failed.add(item.path)
            self._later(self.next, 0)

    def _texture_ready(self, video, texture):
        if video is self.video and texture is not None and not self._closed:
            self._ready = True
            self._fallback.opacity = self.image.opacity = 0

    def _ended(self, video, ended):
        if ended and video is self.video and not self._closed:
            self._measure_video(0, ended=True)
            self._later(lambda: self.next(completed=True), 0)

    def _failed_video(self, video):
        if video is self.video and self.current is not None and not self._closed:
            self._failed.add(self.current.path)
            self._later(self.next, 0)

    def _tick(self, dt):
        if self._closed:
            return False
        # Detached/unmounted roots and a backgrounded/enlarged view do not
        # contribute exposure time. A missed schedule boundary replaces media.
        if self._paused or self.get_root_window() is None or self.current is None:
            return
        from datetime import datetime
        if not self.current.eligible(self.placement, datetime.now(self.catalog.zone)):
            self.next()
            return
        if self._ready:
            if self.video is not None:
                self._measure_video(dt)
                # A provider can load the first frame and then hang without
                # raising or emitting EOS. Skip it instead of freezing ads.
                if self._stalled_for >= 12:
                    self._failed_video(self.video)
            else:
                self._seconds += dt
                if self._seconds >= self.current.seconds:
                    self.next(completed=True)

    def _measure_video(self, dt, ended=False):
        """Account decoded progress across coarse provider position updates.

        Some providers report position less often than our 100 ms UI tick.
        Keep the wall time since the last advance, so a 200 ms position jump
        counts up to 200 ms rather than being truncated to a single tick.
        No progress, background time or paused time contributes exposure.
        """
        if self.video is None or self._paused:
            return
        if self.video.state != 'play' and not ended:
            self._stalled_for += dt
            return
        self._unreported_wall += max(0, dt)
        self._stalled_for += max(0, dt)
        position = max(0, self.video.position)
        advance = position - self._last_position
        if advance > 0:
            self._seconds += min(advance, self._unreported_wall)
            self._last_position = position
            self._unreported_wall = self._stalled_for = 0.0

    def set_volume(self, value):
        """Payment stays muted even when the advertising slider is moved."""
        self.volume = 0 if self.placement == 'payment' else value
        if self.video is not None:
            self.video.volume = 0 if self._paused else self.volume

    def pause(self):
        self._paused = True
        self._unreported_wall = self._stalled_for = 0.0
        if self.video is not None:
            self.video.volume = 0
            self.video.state = 'pause'

    def resume(self):
        if self._closed:
            return
        self._paused = False
        if self.video is not None:
            self.video.volume = self.volume
            self.video.state = 'play'

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._tick_event is not None:
            self._tick_event.cancel()
            self._tick_event = None
        self._clear_media()
