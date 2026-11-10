"""Explicit owned-acceptance F8 handoff; no payment or customer-proof authority.

Only current original accepted Sandbox payment metadata reaches local clipboard.
No DB/network call, logs, report field, fake PAID or provider/config/key handle.
"""
from photobooth.qris_evidence import sandbox_qr_url
from photobooth.post_preview_store import ORDER_VERSION


class OwnedSandboxSimulatorClipboard:
    def __init__(self, app):
        from .post_preview_visits_app import ProtectedVisitsApp
        if type(app) is not ProtectedVisitsApp:
            raise TypeError('Original accepted owned Sandbox app required')
        self._app = app
        self._last = None
        self._installed = False

    def __repr__(self): return '<OwnedSandboxSimulatorClipboard: private local handoff>'

    def install(self):
        from kivy.core.window import Window
        if not self._installed:
            Window.bind(on_key_down=self._key_down); self._installed=True

    def _url(self):
        from .flow import RESULT
        app = self._app
        if (app is None or app._closed or app._suspended or app._photo_error
                or app.navigation.page!=RESULT or not app._visit_ready): return None
        control = app._visit_control; binding = control.binding
        if (control.busy or control.state!='READY' or binding is None
                or binding.jobs is not app._photo_jobs
                or binding.service is not app._photo_jobs.service): return None
        service = binding.service; view = app._photo_view
        if (service.client.mode!='sandbox' or service._hidden.is_set() or service._closed.is_set()
                or service.lease is None or service.phase!='payment_pending'
                or view.get('phase')!='payment_pending' or view.get('payment_qr') is None
                or type(view.get('generation')) is not int or view['generation']!=service._generation
                or view.get('purchase_group_id')!=service.group): return None
        payment = view.get('payment')
        if (type(payment) is not dict or payment is not service._payment
                or payment.get('mode')!='sandbox' or payment.get('order_version')!=ORDER_VERSION
                or payment.get('purchase_group_id')!=service.group
                or payment.get('booth_id')!=service.booth_id or payment.get('state')!='PENDING'
                or payment.get('paid_verified') is not False or payment.get('entitlement_id') is not None): return None
        attempts = payment.get('attempts')
        if (type(attempts) is not list or not attempts or type(attempts[-1]) is not dict
                or attempts[-1].get('state')!='PENDING'): return None
        return sandbox_qr_url(payment.get('qr_url'))

    def copy_current(self):
        try:
            url = self._url()
            if url is None: return False
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(url)
            if self._url()!=url:
                if Clipboard.paste()==url: Clipboard.copy('')
                self._last=None
                return False
            self._last=url
            return True
        except Exception:
            return False  # No private clipboard/URL/OS exception in logs.

    def _key_down(self, window, key, scancode, codepoint, modifiers):
        from kivy.core.window import Keyboard
        if key!=Keyboard.keycodes['f8']: return False
        copied=self.copy_current()
        print('SANDBOX_SIMULATOR_QR_COPIED' if copied else 'SANDBOX_SIMULATOR_COPY_HELD',flush=True)
        return True

    def close(self):
        try:
            from kivy.core.window import Window
            if self._installed: Window.unbind(on_key_down=self._key_down)
        except Exception: pass
        self._installed=False
        try:
            from kivy.core.clipboard import Clipboard
            if self._last is not None and Clipboard.paste()==self._last: Clipboard.copy('')
        except Exception: pass
        self._last=None; self._app=None
