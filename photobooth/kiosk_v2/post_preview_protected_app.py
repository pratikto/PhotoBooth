"""Protected backend client profile over the original native checkout views.

No launcher enables this incomplete profile. New visitor admission/recovery is
held until original protected worker/collector/claim release is fully mounted.
"""
from .flow import ADVERT
from .post_preview_checkout_app import _CheckoutAppBase
from .post_preview_protected_checkout import ProtectedCheckoutService
from .theme import GOLD, text_label


class ProtectedCheckoutApp(_CheckoutAppBase):
    _sandbox_transport = True

    def __init__(self, private_root, *, private_service, **kwargs):
        super().__init__(private_root, private_service=private_service,
                         synthetic_pay_callback=None, synthetic_drive_url=False, **kwargs)

    def _validate_checkout_service(self, service):
        if type(service) is not ProtectedCheckoutService:
            raise TypeError('Exact original protected native facade required')

    def attach_synthetic_pilot_admission(self, coordinator):
        raise TypeError('Synthetic admission cannot authorize protected visits')

    def _pilot_prepare_new(self):
        service = self._photo_jobs.service
        if service.lease is not None or service._hidden.is_set():
            self._pilot_note = 'Sesi sebelumnya dilindungi. Pelanggan baru belum dapat masuk.'
            if self.navigation.page == ADVERT:
                self._show()
            return False
        return True

    def _build_advert(self, canvas):
        super()._build_advert(canvas)
        if self._pilot_note:
            self._advert_host.parent.parent.add_widget(text_label(
                self._pilot_note, size=13, height=65, color=GOLD))

    def _private_hold(self):
        super()._private_hold()
        self._pilot_note = 'Sesi sebelumnya dilindungi. Pelanggan baru belum dapat masuk.'
        self.navigation.page = ADVERT
        self._reset_visit()
        self._show()

    def _photo_submit(self, action, *args):
        if action == 'ticket_visible':
            # Same serialized worker as receipt/other commands, but a genuine
            # native ticket remains dismissible during the backend ACK.
            if (not self._closed and not self._suspended and len(args) == 1
                    and self._ticket_current(args[0], visible_ack=True)):
                self._photo_jobs.submit(action, *args)
            return
        return super()._photo_submit(action, *args)

    def _sandbox_photo_outcome(self, outcome):
        if (outcome.action == 'ticket_visible' and not outcome.error
                and not self._photo_jobs.service._hidden.is_set()
                and not self._closed and not self._suspended):
            # The real rendering callback already started the clock. Its
            # start() is intentionally idempotent and returns False on ACK.
            self._ticket_receipt_pending = True
        result = super()._sandbox_photo_outcome(outcome)
        if self._ticket_dismiss_pending and self._ticket_next_button is not None:
            self._ticket_next_button.disabled = True
        return result

    def _ticket_rendered(self, offer):
        super()._ticket_rendered(offer)
        if self._ticket_pending is offer and self._ticket_window is not None:
            # The original card checks full on-window/stencil visibility.
            # No network/receipt acknowledgement may delay this deadline.
            self._ticket_window.start(genuine_visible=True)
            if self._ticket_next_button is not None:
                self._ticket_next_button.disabled = False
            self._update_ticket_countdown()

    def _poll_photos(self):
        if self._closed or self._suspended:
            return
        if self._photo_view.get('phase') == 'ticket_offer' and self._ticket_window is not None:
            self._update_ticket_countdown()
            if self._ticket_window.active and self._ticket_window.remaining() == 0:
                self._ticket_next(user=False)
        return super()._poll_photos()
