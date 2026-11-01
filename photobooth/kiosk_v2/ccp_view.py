"""Private CCP render component, not payment or entitlement authority.

The owning checkout must render this privately and queue the visible callback
on its worker. Never screenshot, persist or include its payload in diagnostics.
"""
import time

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from photobooth.post_preview_ccp import PendingCCPOffer, render_private_ccp
from .photo_views import image_texture
from .theme import GOLD, MUTED, text_label



class PrivateCCPCard(BoxLayout):
    def __init__(self, offer, qr_image, on_visible, *, is_current,
                 heading='SIMPAN CHECKOUT CLAIM PROOF',
                 description='Bukti klaim privat • bukan QR pembayaran', **kwargs):
        if not isinstance(offer, PendingCCPOffer):
            raise TypeError('Original private offer required')
        super().__init__(orientation='vertical', spacing=dp(8), padding=dp(12), **kwargs)
        self._offer = offer
        self._on_visible = on_visible
        self._is_current = is_current
        self._retired = False
        self._ever_attached = False
        self._notified = False
        self._clock = None
        self._ready_at = time.monotonic()+.1
        self.add_widget(text_label(heading, size=18, height=50, color=GOLD))
        self.add_widget(text_label(description, size=13, height=42, color=MUTED))
        texture = image_texture(qr_image)
        texture.mag_filter = texture.min_filter = 'nearest'
        self.qr_image = Image(texture=texture, fit_mode='contain')
        self.add_widget(self.qr_image)
        self.code = text_label(offer.qr_payload, size=11, height=96, color=GOLD)
        # Measure unconstrained text height; a height-constrained texture could
        # silently clip the full capability yet appear to fit its own box.
        self.code.bind(size=lambda widget, bounds: setattr(widget, 'text_size',
                         (max(10, bounds[0]-dp(8)), None)))
        self.add_widget(self.code)
        self._clock = Clock.schedule_interval(self._rendered, .05)

    def on_parent(self, _instance, parent):
        if parent is not None:
            self._ever_attached = True
        elif getattr(self, '_ever_attached', False):
            self.retire()

    def _rendered(self, _dt):
        if self._retired or not self._is_current():
            self.retire()
            return False
        if self._notified:
            return False
        if time.monotonic() < self._ready_at:
            return
        window = self.get_root_window()
        if window is None or self.qr_image.texture is None or not self.code.texture:
            return
        for widget in (self, self.qr_image, self.code):
            x, y = widget.to_window(0, 0, relative=True)
            if (widget.opacity < 1 or widget.width < 1 or widget.height < 1
                    or x < -.5 or y < -.5 or x+widget.width > window.width+.5
                    or y+widget.height > window.height+.5):
                return
            parent = widget.parent
            seen = set()
            while parent is not None and parent is not window:
                if id(parent) in seen:
                    return  # A malformed hierarchy cannot prove presentation.
                seen.add(id(parent))
                if getattr(parent, 'opacity', 1) < 1:
                    return
                parent = parent.parent
        # Full text must fit; generating a QR or owning a texture is not an offer.
        if self.code.texture_size[1] > self.code.height or min(self.qr_image.size) < dp(160):
            return
        self._notified = True
        self._on_visible(self._offer)
        return False

    def retire(self):
        self._retired = True
        if self._clock is not None:
            self._clock.cancel()
            self._clock = None
        self.qr_image.texture = None
        self.qr_image.opacity = 0
        self.code.text = ''
        self._offer = None
        self._on_visible = lambda *_: None

class PrivateRecoveryTicketCard(PrivateCCPCard):
    """Same native QR visibility/redaction gate, with the PAID ticket identity.

    Countdown and NEXT are owned by the checkout's lifetime controller, not
    the card; reattachment cannot reset an original ticket presentation.
    """
    def __init__(self, offer, qr_image, on_visible, *, is_current, **kwargs):
        from photobooth.post_preview_ticket import PendingRecoveryOffer
        if not isinstance(offer, PendingRecoveryOffer):
            raise TypeError('Only the original verified PAID ticket can be displayed')
        super().__init__(
            offer, qr_image, on_visible, is_current=is_current,
            heading='SIMPAN RECOVERY TICKET',
            description='QR ini privat • simpan sebelum menekan LANJUT',
            **kwargs)
