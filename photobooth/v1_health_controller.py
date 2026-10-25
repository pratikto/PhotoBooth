"""Verbatim v1 read-only worker method, extracted for the native v2 host.

Source: feature/device-health dbbe055, PhotoBoothApp._refresh_device_health.
The v1 controller itself is not imported or instantiated. v2 supplies its
existing camera observation, scheduling/heartbeat and lifecycle through adapters.
"""
import threading
from photobooth.device_health import collect_health_snapshot


class V1HealthController:
    def _refresh_device_health(self, callback) -> None:
        """Read-only probes run on a daemon worker, never on Kivy's UI thread.

        Camera/playlist/printer references and the latest UI heartbeat are
        captured on the main thread. The worker only performs Stage A probes;
        it cannot reopen a camera, send print bytes or access Drive. The UI
        rejects responses from dialogs already closed or superseded.
        """
        if self.is_closing:
            return
        if not self._health_probe_lock.acquire(blocking=False):
            # A previous dialog can close while its worker is still running.
            # Do not stack probes; the new panel can retry with REFRESH.
            self.root.after(0, lambda: callback(None))
            return

        camera = self.camera
        printer_config = self.printer.config
        photos_root = self.photos_root
        ad_catalog = self.ui.ad_catalog
        last_heartbeat = self.ui._health_last_tick
        with self._print_lock:
            printer_busy = bool(self._print_jobs_in_flight)

        def worker():
            try:
                snapshot = collect_health_snapshot(
                    camera=camera,
                    printer_config=printer_config,
                    photo_directory=photos_root,
                    ad_catalog=ad_catalog,
                    last_heartbeat=last_heartbeat,
                    printer_busy=printer_busy,
                    include_discovery=True,
                )
            except Exception:
                # No low-level exception text (paths / hosts / device names)
                # is surfaced to the operator or written to customer files.
                snapshot = None
            finally:
                self._health_probe_lock.release()
            if not self.is_closing:
                def deliver():
                    if not self.is_closing:
                        self._latest_health_snapshot = snapshot
                        callback(snapshot)
                self.root.after(0, deliver)

        threading.Thread(
            target=worker, name="meong-device-health", daemon=True,
        ).start()
