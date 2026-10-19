"""FEAT-008 Stage B: operator-only health panel for the existing Kivy Settings menu.

No device probing happens in this presentation mixin. The controller supplies
an asynchronous callback that marshals results back onto the Kivy main thread.
A closed popup cannot be updated by an old worker result.
"""

from datetime import datetime

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from photobooth.ui_brand import BLUE, EDGE, GREY, INK, PAPER, ROSE, WHITE, Panel


CHECK_NAMES = (
    ("camera", "KAMERA"),
    ("printer", "PRINTER THERMAL"),
    ("disk", "PENYIMPANAN FOTO"),
    ("network", "KONEKSI"),
    ("media", "MEDIA IKLAN"),
    ("heartbeat", "RESPONS APLIKASI"),
)
STATUS_LABELS = {
    "ready": "READY",
    "warning": "PERHATIAN",
    "unavailable": "TIDAK TERSEDIA",
    "unknown": "BELUM DIKETAHUI",
}


class HealthPanelMixin:
    """Settings-only diagnostic view; never changes any customer session state."""

    def show_health_settings(self):
        if self._disposed:
            return None
        if self._health_popup is not None:
            return self._health_popup

        body = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        summary = self._label(
            "Belum diperiksa. Tekan REFRESH untuk memeriksa kondisi saat ini.",
            13, 52, color=GREY,
        )
        body.add_widget(summary)
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(6))
        entries = BoxLayout(orientation="vertical", size_hint_y=None,
                            padding=(dp(2), dp(2)), spacing=dp(7))
        entries.bind(minimum_height=entries.setter("height"))
        scroll.add_widget(entries)
        body.add_widget(scroll)

        labels = {}
        for key, caption in CHECK_NAMES:
            row = Panel(
                orientation="vertical", fill=WHITE, border=True, radius=12,
                padding=(dp(12), dp(6)), spacing=dp(2),
                size_hint_y=None, height=dp(86),
            )
            heading = self._label(f"{caption}: BELUM DIPERIKSA", 14, 27, bold=True)
            details = self._label("Belum ada pembacaan perangkat.", 12, 43, color=GREY)
            row.add_widget(heading)
            row.add_widget(details)
            entries.add_widget(row)
            labels[key] = (heading, details)

        note = self._label(
            "READY hanya berarti pemeriksaan terbatas berhasil. "
            "Status kertas, hasil cetak, video decoder, dan Google Drive "
            "tidak diverifikasi.",
            11, 58, color=GREY,
        )
        body.add_widget(note)
        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        popup = Popup(
            title="Device Health | Meong",
            content=body,
            size_hint=(None, None),
            auto_dismiss=False,
            background="", background_color=PAPER,
            title_color=INK, separator_color=EDGE,
        )

        def fit_popup(*_args):
            popup.size = (
                min(dp(640), max(dp(300), Window.width - dp(24))),
                min(dp(710), max(dp(340), Window.height - dp(24))),
            )

        def dismissed(_popup):
            Window.unbind(size=fit_popup)
            # A request made before closing cannot paint a reopened dialog.
            self._health_request_serial += 1
            if self._health_popup is popup:
                self._health_popup = None
                self._health_refresh_button = None
                self._health_labels = {}

        def refresh():
            if self._health_popup is not popup or refresh_button.disabled:
                return
            self._health_request_serial += 1
            serial = self._health_request_serial
            refresh_button.disabled = True
            summary.text = "Memeriksa perangkat di background..."
            for key, caption in CHECK_NAMES:
                heading, details = labels[key]
                heading.text = f"{caption}: MEMERIKSA..."
                heading.color = GREY
                details.text = "Menunggu hasil pemeriksaan."

            handler = self.callbacks.get("on_health_refresh")
            if handler is None:
                completed(None, serial)
                return
            try:
                handler(lambda snapshot: completed(snapshot, serial))
            except Exception:
                # Do not expose tokens, IP addresses or driver exception text.
                completed(None, serial)

        def completed(snapshot, serial):
            if self._disposed or self._health_popup is not popup:
                return
            if serial != self._health_request_serial:
                return
            refresh_button.disabled = False
            if snapshot is None:
                summary.text = "Pemeriksaan belum dapat diselesaikan. Coba REFRESH lagi."
                for key, caption in CHECK_NAMES:
                    heading, details = labels[key]
                    heading.text = f"{caption}: BELUM DIKETAHUI"
                    heading.color = GREY
                    details.text = "Tidak ada hasil dari controller."
                return
            try:
                checks = {check.name: check for check in snapshot.checks}
                instant = datetime.fromisoformat(snapshot.checked_at)
                stamp = instant.astimezone().strftime("%d-%m-%Y %H:%M:%S")
            except (AttributeError, TypeError, ValueError):
                summary.text = "Format laporan tidak dikenali. Coba REFRESH lagi."
                return

            caution = False
            for key, caption in CHECK_NAMES:
                heading, details = labels[key]
                check = checks.get(key)
                state = getattr(check, "status", "unknown")
                if state not in STATUS_LABELS:
                    state = "unknown"
                heading.text = f"{caption}: {STATUS_LABELS[state]}"
                heading.color = (BLUE if state == "ready" else
                                 ROSE if state in ("warning", "unavailable") else GREY)
                details.text = str(getattr(check, "message", "Tidak ada data.")) if check else "Tidak ada data."
                caution |= state != "ready"
            summary.text = (
                f"Diperiksa: {stamp} (waktu lokal). "
                + ("Ada hal yang perlu diperhatikan." if caution
                   else "Semua probe terbatas berhasil.")
            )

        refresh_button = self._button("REFRESH STATUS", refresh, screen_bound=False)
        close_button = self._button(
            "TUTUP", popup.dismiss, secondary=True, screen_bound=False,
        )
        buttons.add_widget(refresh_button)
        buttons.add_widget(close_button)
        body.add_widget(buttons)
        self._health_popup = popup
        self._health_labels = labels
        self._health_refresh_button = refresh_button
        popup.bind(on_dismiss=dismissed)
        fit_popup()
        Window.bind(size=fit_popup)
        popup.open()
        # One operator-initiated refresh upon entering the panel. No timer,
        # no polling, no print payload and no auto-recovery.
        refresh()
        return popup
