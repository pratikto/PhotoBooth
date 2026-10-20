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
from kivy.uix.spinner import Spinner

from photobooth.device_recovery import selected_device_observation
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

    def show_device_selection_settings(self):
        """Stage a primary device for next launch; do not hot-swap anything.

        Windows cameras are entered as explicit OpenCV indices (not stable
        hardware IDs); Linux cameras need a discovered V4L by-id alias.
        Only enumerated Windows spooler queues are eligible printer choices.
        We never offer unimplemented CUPS/Android transports as working routes.
        """
        if (self._health_popup is None or self._device_pick_popup is not None
                or self._disposed):
            return self._device_pick_popup
        handler = self.callbacks.get("on_device_stage")
        if handler is None:
            return None

        platform = self._health_platform
        inventory = self._health_inventory
        skip = "TIDAK DIUBAH"
        reset = "KEMBALI KE DEFAULT"
        camera_options = {skip: None, reset: ("", "")}
        printer_options = {skip: None, reset: ("", "")}
        if platform == "windows":
            for index in range(16):
                camera_options[f"Kamera OpenCV indeks {index} (manual)"] = (
                    "opencv-index", str(index))
            for item in inventory:
                if (item.kind == "printer" and item.presence == "queue-detected"
                        and item.device_id.startswith("win-queue:")):
                    queue = item.device_id[len("win-queue:"):]
                    printer_options[f"Windows queue: {queue}"] = (
                        "windows-spooler", queue)
        elif platform == "linux":
            for item in inventory:
                if (item.kind == "camera" and item.presence == "node-detected"
                        and item.device_id.startswith("v4l:by-id:")):
                    alias = item.device_id[len("v4l:by-id:"):]
                    camera_options[f"V4L by-id: {alias}"] = (
                        "linux-v4l-by-id", alias)

        body = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14))
        body.add_widget(self._label(
            "Pilihan baru hanya aktif setelah Meong direstart. Tidak ada "
            "perubahan kamera/printer selama sesi berjalan.",
            13, 72, color=GREY))
        body.add_widget(self._label("KAMERA UTAMA", 15, 28, bold=True))
        camera_input = Spinner(text=skip, values=list(camera_options),
                               size_hint_y=None, height=dp(49))
        body.add_widget(camera_input)
        body.add_widget(self._label("PRINTER UTAMA", 15, 28, bold=True))
        printer_input = Spinner(text=skip, values=list(printer_options),
                                size_hint_y=None, height=dp(49))
        body.add_widget(printer_input)
        caption = self._label(
            "Index kamera Windows dapat berubah setelah cabut/pasang USB. "
            "CUPS/Android belum tersedia sebagai backend printer aktif.",
            12, 60, color=GREY)
        body.add_widget(caption)
        saved = self.callbacks.get("get_device_selection")
        state = saved() if saved else None
        state_label = self._label(
            ("Tersimpan: kamera=" + (state.camera_value or "default")
             + ", printer=" + (state.printer_value or "default")) if state else
            "Belum ada konfigurasi yang tersimpan.",
            12, 50, color=GREY,
        )
        body.add_widget(state_label)

        popup = Popup(
            title="Pilih hardware untuk restart berikutnya",
            content=body, size_hint=(None, None), auto_dismiss=False,
            background="", background_color=PAPER,
            title_color=INK, separator_color=EDGE,
        )
        def fit_popup(*_args):
            popup.size = (
                min(dp(600), Window.width - dp(24)),
                min(dp(565), Window.height - dp(24)),
            )
        Window.bind(size=fit_popup)
        fit_popup()

        def save():
            camera = camera_options[camera_input.text]
            printer = printer_options[printer_input.text]
            if camera is None and printer is None:
                state_label.text = "Pilih kamera atau printer terlebih dahulu."
                return
            try:
                state_label.text = str(handler(camera=camera, printer=printer))
                state_label.color = BLUE
            except (ValueError, OSError) as error:
                state_label.text = str(error)
                state_label.color = ROSE

        actions = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        save_button = self._button("SIMPAN UNTUK RESTART", save, screen_bound=False)
        actions.add_widget(save_button)
        actions.add_widget(self._button("TUTUP", popup.dismiss,
                                        secondary=True, screen_bound=False))
        body.add_widget(actions)

        def dismissed(_popup):
            Window.unbind(size=fit_popup)
            if self._device_pick_popup is popup:
                self._device_pick_popup = None
        self._device_pick_popup = popup
        popup.bind(on_dismiss=dismissed)
        popup.open()
        return popup

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
        # Adapter identity reports configuration, not verified physical presence.
        hardware_info = self._label("Adapter: belum diperiksa.", 11, 54, color=GREY)
        body.add_widget(hardware_info)
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

        entries.add_widget(self._label("DAFTAR PERANGKAT / ADAPTER", 13, 30, bold=True))
        inventory_rows = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(5))
        inventory_rows.bind(minimum_height=inventory_rows.setter("height"))
        entries.add_widget(inventory_rows)
        inventory_rows.add_widget(self._label("Belum ada enumerasi perangkat.", 12, 40, color=GREY))
        self._selection_observations = {}

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
                if self._device_pick_popup is not None:
                    self._device_pick_popup.dismiss(animation=False)
                self._health_popup = None
                self._health_refresh_button = None
                self._health_select_button = None
                self._health_labels = {}
                self._health_inventory = ()
                self._health_platform = "unknown"

        def refresh():
            if self._health_popup is not popup or refresh_button.disabled:
                return
            self._health_request_serial += 1
            serial = self._health_request_serial
            refresh_button.disabled = True
            choose_button.disabled = True
            summary.text = "Memeriksa perangkat di background..."
            hardware_info.text = "Meninjau adapter dan perangkat yang dipilih..."
            inventory_rows.clear_widgets()
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
                choose_button.disabled = True
                hardware_info.text = "Identitas perangkat belum tersedia."
                inventory_rows.clear_widgets()
                inventory_rows.add_widget(self._label("Discovery tidak tersedia.", 12, 40, color=GREY))
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

            family = str(getattr(snapshot, "platform", "unknown")).upper()
            inventory = getattr(snapshot, "devices", ())
            self._health_platform = family.lower()
            self._health_inventory = inventory
            choose_button.disabled = self.callbacks.get("on_device_stage") is None
            configured = [item for item in inventory
                          if item.kind in ("camera", "printer")
                          and item.presence not in ("node-detected", "queue-detected")]
            names = ", ".join(item.name for item in configured[:2])
            detected = [item for item in inventory
                        if item.presence in ("node-detected", "queue-detected")]
            hardware_info.text = (
                f"Platform adapter: {family} (belum tersertifikasi).\n"
                + f"{len(configured)} entri konfigurasi; {len(detected)} kandidat OS ditemukan."
            )
            inventory_rows.clear_widgets()
            if not inventory:
                inventory_rows.add_widget(self._label(
                    "Tidak ada identitas perangkat yang bisa ditampilkan.",
                    12, 48, color=GREY))
            for item in inventory[:20]:
                text = (f"{item.kind.upper()}: {item.name} [{item.presence}]\n"
                        f"Identitas: {item.identity_quality}; akses fisik belum dipastikan.")
                inventory_rows.add_widget(self._label(text, 12, 68, color=GREY))
            # Observations never imply physical operability or auto-reconnect.
            # A matching OS identity is a candidate; absence cannot prove
            # disconnection when the discovery API itself may have failed.
            get_selection = self.callbacks.get("get_device_selection")
            if get_selection is not None:
                try:
                    selection = get_selection()
                    for kind, caption in (("camera", "KAMERA PILIHAN"),
                                          ("printer", "PRINTER PILIHAN")):
                        old = self._selection_observations.get(kind)
                        # There is no discovery-completeness signal from B.2:
                        # only assert a candidate on positive evidence.
                        candidate = selected_device_observation(
                            selection, kind, platform=self._health_platform,
                            detected=inventory, previous=old,
                            discovery_complete=True,
                        )
                        if candidate.state == "missing":
                            observation = selected_device_observation(
                                selection, kind, platform=self._health_platform,
                                detected=inventory, previous=old,
                                discovery_complete=False,
                            )
                        else:
                            observation = candidate
                        self._selection_observations[kind] = observation
                        inventory_rows.add_widget(self._label(
                            f"{caption}: {observation.state.upper()} "
                            "(bukan verifikasi fisik)", 11, 36, color=GREY,
                        ))
                except (ValueError, TypeError, AttributeError):
                    # Corrupt selection is handled by startup's strict loader.
                    inventory_rows.add_widget(self._label(
                        "Status pilihan perangkat belum dapat dibaca.",
                        11, 36, color=GREY,
                    ))
            if len(inventory) > 20:
                inventory_rows.add_widget(self._label(
                    f"+{len(inventory) - 20} entri lain tidak ditampilkan.",
                    12, 34, color=GREY))
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
        choose_button = self._button(
            "PILIH DEVICE", self.show_device_selection_settings,
            secondary=True, screen_bound=False, enabled=False,
        )
        close_button = self._button(
            "TUTUP", popup.dismiss, secondary=True, screen_bound=False,
        )
        buttons.add_widget(refresh_button)
        buttons.add_widget(choose_button)
        buttons.add_widget(close_button)
        body.add_widget(buttons)
        self._health_popup = popup
        self._health_labels = labels
        self._health_refresh_button = refresh_button
        self._health_select_button = choose_button
        popup.bind(on_dismiss=dismissed)
        fit_popup()
        Window.bind(size=fit_popup)
        popup.open()
        # One operator-initiated refresh upon entering the panel. No timer,
        # no polling, no print payload and no auto-recovery.
        refresh()
        return popup
