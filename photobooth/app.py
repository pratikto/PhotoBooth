# PhotoBooth source file
# Application controller connecting customer actions, camera capture, local transaction storage, Drive synchronization, and the Kivy screens.

"""Application controller for the procedure's capture and Drive workflow.

The kiosk opens with scheduled local advertisements and uses an explicitly
non-payable demo payment flow. Optional LAN output prints the active QR slip;
photograph printing is developed separately. When Drive is configured,
transactions use pre-verified folder slots, show the cached folder QR, and
synchronize files in the background.
"""

import os
import json
import time
import threading
from pathlib import Path
from kivy.clock import ClockEvent

import cv2
from PIL import Image

from photobooth.background_studio import BackgroundStudio, BackgroundProcessingError, ORIGINAL, CLEAN_STUDIO
from photobooth.audio import AudioManager
from photobooth.camera import Camera
from photobooth.catalog import PRICE_PER_PRINT_COPY, PRICE_PER_SESSION, compose_result, get_templates
from photobooth.drive_pool import DriveSlotPool
from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError, GoogleDriveClient
from photobooth.drive_sync import DriveSyncWorker
from photobooth.face_presence import FacePresenceTrigger, FacePresenceWorker
from photobooth.palm_gesture import MAX_RESULT_AGE, PALM_CONFIDENCE, PalmGestureWorker, PalmHoldTrigger
from photobooth.qr_code import create_qr_image
from photobooth.printer import PrintResult, ThermalPrinter
from photobooth.retention import PhotoRetentionWorker
from photobooth.transaction_store import LocalTransaction, TransactionStore
from photobooth.ui_kivy import KivyHost, PhotoBoothUI
from photobooth.workflow import PhotoSession, SessionPlan, build_session_plans, quote_order


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOTH_ID = os.environ.get("PHOTOBOOTH_ID", "PB001")
CAMERA_INDEX = int(os.environ.get("PHOTOBOOTH_CAMERA_INDEX", "0"))
CAPTURE_COUNTDOWN_SECONDS = 5
FINAL_SCREEN_SECONDS = 60


class PhotoBoothApp:
    """Coordinate the camera, GUI workflow, and local transaction files."""

    def __init__(self) -> None:
        # Build the main application state: camera, local transaction store, cached Drive folder pool,
        # optional sync worker, and GUI callbacks. Kivy timers are scheduled on the UI thread;
        # network synchronization runs in a background worker.
        # KivyHost owns the event loop. Its small timer adapter preserves this
        # controller's millisecond timing while returning cancellable ClockEvents.
        # ui_tkinter.py remains untouched as a historical implementation only.
        self.root = KivyHost(on_close=self.close)
        self.templates = get_templates()
        self.camera = Camera(camera_index=CAMERA_INDEX)
        self.photos_root = PROJECT_ROOT / "photos"
        self.store = TransactionStore(
            photos_root=self.photos_root,
            state_path=PROJECT_ROOT / "data" / "booth_state.json",
            booth_id=BOOTH_ID,
        )
        self.drive_pool = DriveSlotPool(
            photos_root=self.photos_root,
            state_path=PROJECT_ROOT / "data" / "drive_pool.json",
            booth_id=BOOTH_ID,
        )
        # Reuse the Apps Script URL/token configured for the existing booth.
        # OAuth remains available as a fallback for installations that use it.
        self.drive_client = (
            AppsScriptDriveClient.from_configuration()
            or GoogleDriveClient.from_environment()
        )
        self.local_only_mode = os.environ.get("PHOTOBOOTH_LOCAL_ONLY", "0").lower() in {
            "1",
            "true",
            "yes",
        }
        self.drive_worker = (
            DriveSyncWorker(self.photos_root, self.drive_client, self.drive_pool)
            if self.drive_client is not None
            else None
        )
        if self.drive_worker is not None:
            self.drive_worker.start()

        self.current_frame = None
        self.camera_ready = False
        self._camera_wait_status: tuple[str, str] | None = None
        self.is_closing = False
        self.transaction: LocalTransaction | None = None
        self.sessions: list[PhotoSession] = []
        self.session_index = 0
        self.current_session: PhotoSession | None = None
        self.background_studio = BackgroundStudio()
        self._background_style = ORIGINAL
        self._background_images = None
        self._background_pending = False
        self._background_generation = 0

        # Palm recognition is an optional second shutter. Initialize its native
        # model on a worker after the camera connects, without delaying Kivy.
        # A disabled/missing detector leaves the existing button path intact.
        self.palm_worker = PalmGestureWorker(
            PROJECT_ROOT / "data" / "models" / "gesture_recognizer.task",
            enabled=os.environ.get("PHOTOBOOTH_PALM_TRIGGER", "1").lower() not in {"0", "false", "no"},
        )
        self.palm_trigger = PalmHoldTrigger()

        self._countdown_remaining = 0
        self._countdown_is_retake = False
        self._countdown_after_id: ClockEvent | None = None
        self._completion_remaining = 0
        self._completion_after_id: ClockEvent | None = None
        self._preview_after_id: ClockEvent | None = None
        self._drive_status_after_id: ClockEvent | None = None

        from photobooth.printer_settings import load_printer_config, save_printer_config
        self._printer_settings_file = PROJECT_ROOT / 'data' / 'printer_settings.json'
        self._save_printer_config = save_printer_config
        self.printer = ThermalPrinter(load_printer_config(self._printer_settings_file))
        self._print_lock = threading.Lock()
        self._print_jobs_in_flight: set[str] = set()
        # Only one thermal transport may send bytes at a time, even when
        # different completed template sessions have pending print batches.
        # This is intentionally independent of the short bookkeeping lock.
        self._print_device_lock = threading.Lock()


        self.ui = PhotoBoothUI(
            root=self.root,
            templates=self.templates,
            audio_manager=AudioManager(PROJECT_ROOT / 'data' / 'audio'),
            kiosk_data_dir=PROJECT_ROOT / 'data',
            on_home_start=self._open_template_selection,
            on_start=self._open_dummy_payment,
            on_capture=self._start_capture_countdown,
            on_select_photo=self._select_photo,
            on_retake=self._prepare_retake,
            on_accept_session=self._accept_current_session,
            on_background_style=self._choose_background_style,
            on_next_session=self._start_next_session,
            on_finish=self._finish_transaction,
            on_print=self._retry_current_print,
            get_printer_config=lambda: self.printer.config,
            on_printer_save=self._configure_printer,
            on_printer_test=self._test_printer,
            on_close=self.close,
            on_idle=self._return_to_advertisements,
        )
        self.face_worker = FacePresenceWorker(
            enabled=os.environ.get('PHOTOBOOTH_FACE_TRIGGER', '1').lower() not in {'0', 'false', 'no'})
        self.face_trigger = FacePresenceTrigger(self.ui.kiosk_timing.face_hold,
                                               self.ui.kiosk_timing.face_cooldown)
        self.ui.show_advertisement(False, "Kamera sedang diperiksa...")
        self.retention_worker = PhotoRetentionWorker(self.photos_root, self.drive_client)
        self.retention_worker.start()
        self.root.after(100, self._connect_camera)
        self._schedule_drive_status_update()

    def _configure_printer(self, config):
        """Apply validated operator settings to subsequent print jobs."""
        self._save_printer_config(self._printer_settings_file, config)
        self.printer = ThermalPrinter(config)

    def _test_printer(self, callback):
        """Send a short test receipt from a worker to avoid freezing the GUI.

        The operator explicitly triggers this action. Never retry automatically,
        because a submitted RAW job may have printed despite driver errors.
        """
        def work():
            data = (b"\x1b\x40\x1b\x61\x01"
                    b"MEONG PHOTOBOOTH\nUSB/LAN/WIFI TEST\n\n\n"
                    b"\x1d\x56\x42\x00")
            try:
                config = self.printer.config
                if config.lan_host:
                    self.printer._send_network(config.lan_host, config.lan_port, data)
                elif config.wifi_host:
                    self.printer._send_network(config.wifi_host, config.wifi_port, data)
                else:
                    self.printer._send_usb(data)
                message = "Job terkirim; periksa hasil cetakan fisik."
            except Exception as error:
                message = f"Test print gagal: {error}"
            self.root.after(0, lambda: callback(message))
        threading.Thread(target=work, daemon=True, name="meong-printer-test").start()

    def run(self) -> None:
        """Start Kivy's event loop."""
        self.root.mainloop()

    def _connect_camera(self) -> None:
        # Open the selected camera and verify one initial frame, then update
        # readiness without replacing the advertisement already on screen.
        if self.is_closing:
            return

        self.ui.set_status("Menghubungkan ke kamera...")
        self.camera_ready = self.camera.open()
        first_frame = self.camera.read() if self.camera_ready else None
        if first_frame is None:
            self.camera.close()
            self.camera_ready = False
        else:
            self.current_frame = first_frame
        self.ui.set_camera_status(self.camera_ready)

        if self.camera_ready:
            self.palm_worker.start()
            self.face_worker.start()
            # The opening advertisement starts immediately and is not rebuilt
            # when camera/Drive readiness arrives a little later.
            self.ui.set_status(self._storage_status_message())
            self._update_preview()
        else:
            self.ui.set_status("Kamera tidak terdeteksi. Periksa koneksi atau indeks kamera.")

    def _update_preview(self) -> None:
        # Poll the camera repeatedly and refresh the live preview. This callback also enables capture
        # only when a fresh frame is available, then schedules itself again with Kivy.
        if self.is_closing:
            return

        frame = self.camera.read()
        ready = frame is not None
        if ready != self.camera_ready:
            self.camera_ready = ready
            self.ui.set_camera_status(ready)
        if frame is None:
            self.current_frame = None
            self._update_palm_trigger(None)
            self._update_face_presence(None)
            # Preserve the screen's own feedback while reporting a temporary
            # loss of frames. Recovery restores it rather than leaving a stale
            # "waiting for camera" notice on an otherwise live screen.
            if (self._camera_wait_status is None or
                    self._camera_wait_status[0] != self.ui.current_screen):
                self._camera_wait_status = (self.ui.current_screen, self.ui.status.text)
            self.ui.set_status("Menunggu gambar dari kamera...")
            if self.ui.current_screen == "capture":
                self.ui.set_capture_enabled(False)
            self._preview_after_id = self.root.after(120, self._update_preview)
            return

        self.current_frame = frame
        if self._camera_wait_status is not None:
            screen, message = self._camera_wait_status
            if self.ui.status.text == "Menunggu gambar dari kamera...":
                self.ui.set_status(message if screen == self.ui.current_screen else "")
            self._camera_wait_status = None
        if self.ui.current_screen == "capture":
            # The camera mailbox is nonblocking. Upload a small preview directly
            # from BGR pixels instead of constructing several Pillow copies.
            self.ui.update_live_frame(frame)
            session = self.current_session
            if (
                session is not None
                and self._countdown_after_id is None
                and (len(session.initial_photo_paths) < 3 or session.can_retake)
            ):
                self.ui.set_capture_enabled(True)

        # Recognition reads a mailbox and submits work only; no model inference
        # or download occurs on this GUI callback. Every screen, including
        # review/payment/result, explicitly gates the second shutter.
        self._update_palm_trigger(frame)
        self._update_face_presence(frame)

        self._preview_after_id = self.root.after(30, self._update_preview)

    def _update_face_presence(self, frame) -> None:
        """Observe one existing camera stream only while idle advertising is visible."""
        if (frame is None or not self.camera_ready or self.ui.current_screen != 'advert'
                or self.is_closing or self.ui.audio_settings_open or self.ui._media_paused):
            self.face_worker.pause()
            self.face_trigger.pause()
            return
        self.face_worker.start()
        self.face_trigger.hold_seconds = self.ui.kiosk_timing.face_hold
        self.face_trigger.cooldown_seconds = self.ui.kiosk_timing.face_cooldown
        self.face_worker.submit(frame, self.ui.screen_revision)
        result = self.face_worker.poll()
        now = time.monotonic()
        if (result is not None and result.context == self.ui.screen_revision
                and 0 <= now - result.captured_at <= MAX_RESULT_AGE):
            if self.face_trigger.observe(result.score >= .5, result.captured_at):
                self.ui.show_face_invitation()

    def _return_to_advertisements(self) -> None:
        """Landing inactivity cannot interrupt payment, capture, saving or a result."""
        if self.transaction is not None or self.ui.current_screen not in {'welcome', 'templates'}:
            return
        self.face_trigger.pause()
        self.face_worker.pause()
        self.ui.show_advertisement(self.camera_ready, self._storage_status_message())

    def _update_palm_trigger(self, frame) -> None:
        """Accept only recent observations from this exact capture-page revision.

        A positive hold uses the same camera/selection/quota/countdown checks as
        the button. During a countdown we still observe hand release, but never
        accumulate the next hold. Missing frames invalidate all in-flight work.
        """
        if (frame is None or not self.camera_ready or self.ui.current_screen != "capture"
                or self.current_session is None or self.is_closing
                or self.ui.audio_settings_open):
            self.palm_worker.pause()
            self.palm_trigger.pause()
            return
        state = self.palm_worker.state
        if state != "ready":
            self.palm_trigger.pause()
            self.ui.set_palm_status(state, needs_release=self.palm_trigger.needs_release)
            return
        context = self.ui.screen_revision
        self.palm_worker.submit(frame, context)
        result = self.palm_worker.poll()
        now = time.monotonic()
        # Compare hold continuity using source timestamps, allowing for the
        # accepted inference latency. Expiring at delivery time would reset
        # every hold on a slower (but still sufficiently fresh) CPU detector.
        self.palm_trigger.expire(now - MAX_RESULT_AGE)
        if (result is not None and result.context == context
                and 0 <= now - result.captured_at <= MAX_RESULT_AGE):
            if self.palm_trigger.observe(
                result.score >= PALM_CONFIDENCE,
                result.captured_at,
                allow_trigger=self._countdown_after_id is None and not self.ui.capture_button.disabled,
            ):
                self._start_capture_countdown()
        if self.palm_worker.state != "ready":
            self.palm_trigger.pause()
        self.ui.set_palm_status(self.palm_worker.state, self.palm_trigger.progress,
                                self.palm_trigger.needs_release)

    def _open_template_selection(self, quantities: dict[str, int] | None = None) -> None:
        # Open a new or previously unpaid cart and pass live camera/Drive gates
        # to the UI. Never replace the screen of an active customer transaction.
        if self.transaction is not None:
            return
        # Editing an unpaid order does not require a live camera. Keep its
        # quantities visible while disabling payment until frames resume.
        if not self.camera_ready and self.ui.current_screen not in {"advert", "templates", "payment"}:
            self.ui.show_error(
                "Kamera belum siap",
                "Sambungkan kamera sebelum memulai sesi foto.",
            )
            return
        self.ui.show_template_selection(
            camera_ready=self.camera_ready,
            storage_ready=(self.drive_pool.has_ready_slot() or self.local_only_mode),
            status_message=self._storage_status_message(),
            quantities=quantities,
        )

    def _open_dummy_payment(self, quantities: dict[str, int]) -> None:
        """Preview a simulated payment before allocating any customer transaction.

        No payment provider is connected. The confirmation button is an explicit
        development action, never evidence that real money has been received.
        The order is copied so later widget edits cannot change the paid amount.
        Camera and storage are checked again by _start_transaction on confirmation.
        """
        if self.ui.current_screen != "templates" or self.transaction is not None:
            return
        plans = build_session_plans(self.templates, quantities)
        if not plans:
            self.ui.show_error("Template belum dipilih", "Pilih minimal satu sesi.")
            return
        order = dict(quantities)
        # FEAT-001: each chosen template incurs one capture/session fee;
        # the quantity now counts identical physical prints of that session.
        # The displayed QR remains DEMO-only regardless of the amount.
        quote = quote_order(self.templates, order)
        summary = "\n".join(
            f"{template.name}: {order[template.template_id]} lembar "
            f"(Rp{PRICE_PER_SESSION:,} + "
            f"Rp{order[template.template_id] * PRICE_PER_PRINT_COPY:,})"
            for template in self.templates if order.get(template.template_id, 0)
        ).replace(",", ".")
        self.ui.show_payment(
            order_summary=summary,
            session_count=quote.session_count,
            total_amount=quote.total_amount,
            on_confirm=lambda: self._start_transaction(order),
            # Going back is an edit of this order, not a new customer cart.
            # Capture a copy so the next payment is priced from the edited cart.
            on_back=lambda: self._open_template_selection(order),
        )

    def _start_transaction(self, quantities: dict[str, int]) -> bool:
        """Return True only after storage and the first session are prepared.

        False lets the payment UI release its submission lock after a rejected
        confirmation. It is not a payment-provider status; QRIS remains a demo.
        """
        # Validate print-copy quantities, create one capture session per
        # selected template, and persist the complete planned order before
        # capture. Extra copies must not create extra camera sessions.
        # Ignore stale payment callbacks after the screen has advanced. The
        # explicit simulation action is the only current path into capture.
        if self.ui.current_screen != "payment" or self.transaction is not None:
            return False
        if not self.camera_ready or self.current_frame is None:
            self.camera_ready = False
            self.ui.set_camera_status(False)
            self.ui.show_error("Kamera belum siap", "Sesi foto belum dapat dimulai.")
            return False

        try:
            plans = build_session_plans(self.templates, quantities)
            if not plans:
                self.ui.show_error(
                    "Template belum dipilih",
                    "Pilih minimal satu sesi template untuk melanjutkan.",
                )
                return False
            if self.drive_pool.has_ready_slot():
                slot = self.drive_pool.claim()
                transaction_id = slot.transaction_id
                if not transaction_id:
                    raise DriveApiError("Drive slot has no preassigned transaction ID.")
                self.store.advance_counter_past(transaction_id)
                self.transaction = self.store.start_transaction(
                    plans,
                    transaction_id=transaction_id,
                    folder_path=Path(slot.staging_path),
                    drive_slot=slot.to_manifest(),
                )
                if self.drive_worker is not None:
                    self.drive_worker.kick()
            elif self.local_only_mode:
                self.transaction = self.store.start_transaction(plans)
            else:
                raise DriveApiError(
                    "Tidak ada slot folder Google Drive yang siap. Transaksi baru dihentikan."
                )
        except (DriveApiError, OSError, RuntimeError, ValueError) as error:
            self.ui.show_error(
                "Transaksi tidak dapat dimulai",
                f"Data transaksi tidak dapat disiapkan.\n\n{error}",
            )
            self._open_template_selection(quantities)
            return False

        self.sessions = [PhotoSession(plan=plan) for plan in plans]
        self.session_index = 0
        self._begin_current_session()
        return True

    def _begin_current_session(self) -> None:
        # Select the session at session_index and display its capture screen. Each session owns a
        # separate retake allowance.
        if not self.sessions:
            return
        self.current_session = self.sessions[self.session_index]
        self._background_generation += 1
        self._background_style = ORIGINAL
        self._background_images = None
        self._background_pending = False
        self._show_capture_screen()

    def _session_label(self, plan: SessionPlan) -> str:
        # Build the customer-facing label that shows the order position and, when relevant, the
        # position among sessions using the same template.
        label = (
            f"Sesi {plan.order_number} dari {plan.total_sessions}"
            f" · {plan.template.name}"
        )
        label += f" · {plan.print_copies} lembar"
        return label

    def _show_capture_screen(self) -> None:
        # Show the ready state without scheduling a countdown. Three initial
        # photos identify a pending replacement; its selected target and quota
        # remain unchanged until the customer presses the shutter and saving
        # succeeds. Camera recovery can re-enable this same ready-state button.
        session = self.current_session
        if session is None:
            return
        count = len(session.initial_photo_paths)
        is_retake = session.ready_for_review
        self.ui.show_capture(
            session_label=self._session_label(session.plan),
            capture_count=count,
            preview_image=(
                self._frame_to_image(self.current_frame)
                if self.current_frame is not None
                else None
            ),
            action_label="AMBIL FOTO PENGGANTI" if is_retake else f"AMBIL FOTO {count + 1}",
            can_capture=(
                self.camera_ready
                and self.current_frame is not None
                and (count < 3 or session.can_retake)
            ),
            is_retake=is_retake,
        )
        self.palm_worker.pause()
        self.palm_trigger.pause()
        self.ui.set_palm_status(self.palm_worker.state, needs_release=self.palm_trigger.needs_release)

    def _start_capture_countdown(self) -> None:
        # Button presses and confirmed palm holds share this one countdown gate.
        # Once all three originals exist, recheck selection and the session quota.
        session = self.current_session
        if (
            self.ui.current_screen != "capture"
            or not self.camera_ready
            or self.current_frame is None
            or session is None
            or (session.ready_for_review and not session.can_retake)
            or self._countdown_after_id is not None
            or self.ui.audio_settings_open
        ):
            return
        # A button press also invalidates a half-completed palm hold. Keeping a
        # hand raised through capture must not immediately trigger the next photo.
        self.palm_trigger.latch()
        self.palm_worker.pause()
        self._start_countdown(is_retake=session.ready_for_review)

    def _prepare_retake(self) -> None:
        # Review's retake action opens the live camera so the customer has time
        # to pose. It must not start a timer, save a photo, or consume the quota.
        session = self.current_session
        if (self.ui.current_screen != "review" or not self.camera_ready or self.current_frame is None
                or session is None or not session.can_retake or self._countdown_after_id is not None):
            return
        self._show_capture_screen()

    def _start_countdown(self, is_retake: bool) -> None:
        # Prepare the shared countdown UI for either an initial capture or a retake, then schedule the
        # first one-second timer tick.
        session = self.current_session
        if session is None:
            return

        self._countdown_is_retake = is_retake
        self._countdown_remaining = CAPTURE_COUNTDOWN_SECONDS
        self.ui.show_capture(
            session_label=self._session_label(session.plan),
            capture_count=len(session.initial_photo_paths),
            preview_image=(
                self._frame_to_image(self.current_frame)
                if self.current_frame is not None
                else None
            ),
            action_label="RETAKE FOTO TERPILIH" if is_retake else "MENGAMBIL FOTO",
            can_capture=False,
            is_retake=is_retake,
        )
        self.ui.set_countdown(self._countdown_remaining, is_retake=is_retake)
        self._countdown_after_id = self.root.after(1000, self._countdown_tick)

    def _countdown_tick(self) -> None:
        # Advance the countdown one second at a time. When it reaches zero, save the latest camera
        # frame instead of blocking the UI with a sleep call.
        self._countdown_after_id = None
        if self.is_closing:
            return

        if self._countdown_remaining <= 1:
            is_retake = self._countdown_is_retake
            self._countdown_remaining = 0
            self._save_current_frame(is_retake=is_retake)
            return

        self._countdown_remaining -= 1
        self.ui.set_countdown(
            self._countdown_remaining,
            is_retake=self._countdown_is_retake,
        )
        self._countdown_after_id = self.root.after(1000, self._countdown_tick)

    def _save_current_frame(self, is_retake: bool) -> None:
        # Persist the captured image and update the session and transaction manifest. A retake
        # replaces the selected photo in the final result while the original remains in the raw-photo
        # record.
        session = self.current_session
        transaction = self.transaction
        if session is None or transaction is None or self.current_frame is None:
            self.ui.show_error(
                "Foto belum tersedia",
                "Kamera belum menghasilkan gambar. Periksa kamera lalu coba lagi.",
            )
            if is_retake:
                self._show_review()
            else:
                self._show_capture_screen()
            return

        image = self._frame_to_image(self.current_frame)
        try:
            if is_retake:
                if not session.can_retake or session.selected_index is None:
                    self._show_review()
                    return
                photo_path = self.store.save_raw_photo(
                    transaction,
                    session.plan,
                    image,
                    filename="retake_01.jpg",
                    role="retake",
                )
                selected_path = session.initial_photo_paths[session.selected_index]
                self.store.record_retake(
                    transaction,
                    session.plan.session_id,
                    selected_path,
                )
                session.apply_retake(photo_path)
                self._background_generation += 1
                self._background_style = ORIGINAL
                self._background_images = None
                self._background_pending = False
                # Cue only a successfully saved replacement, never a failed attempt.
                self.ui.notify_photo_captured()
                self._show_review(
                    status_message="Retake digunakan. Sisa kuota sesi ini: 0.",
                )
                return

            capture_number = len(session.initial_photo_paths) + 1
            photo_path = self.store.save_raw_photo(
                transaction,
                session.plan,
                image,
                filename=f"capture_{capture_number:02d}.jpg",
                role="capture",
            )
            session.add_initial_photo(photo_path)
            self.ui.notify_photo_captured()
        except (OSError, RuntimeError, ValueError) as error:
            self.ui.show_error(
                "Foto gagal disimpan",
                "Sesi dihentikan karena foto atau manifest tidak berhasil disimpan.\n\n"
                f"Periksa ruang penyimpanan lalu hubungi petugas.\n\n{error}",
            )
            if is_retake:
                self._show_review()
            else:
                self._show_capture_screen()
            return

        if session.ready_for_review:
            self._show_review()
        else:
            self._show_capture_screen()

    def _select_photo(self, index: int) -> None:
        # Record the customer's selected photo for this session and refresh the review screen;
        # selection is locked after the retake has been used.
        session = self.current_session
        if session is None or session.retake_used:
            return
        try:
            session.select_photo(index)
        except (IndexError, ValueError) as error:
            self.ui.show_error("Pilihan foto tidak valid", str(error))
            return
        self._show_review()

    def _show_review(self, status_message: str = "") -> None:
        # Display the final three-photo selection and the current retake status. After a retake, the
        # replacement occupies the selected photo's original position.
        session = self.current_session
        if session is None:
            return
        selected_index = (
            session.retake_target_index
            if session.retake_used
            else session.selected_index
        )
        if not status_message:
            status_message = (
                "Retake belum digunakan. Pilih satu foto untuk mengaktifkannya."
                if not session.retake_used
                else "Retake digunakan. Tiga foto awal dan foto pengganti tetap tersimpan."
            )
        self.ui.show_review(
            photo_paths=session.final_photo_paths,
            session_label=self._session_label(session.plan),
            selected_index=selected_index,
            retake_available=not session.retake_used,
            status_message=status_message,
            # Each approved design has different aperture sizes and clipping
            # shapes. Review must use this session's actual template, including
            # the frame containing a replacement photo after a retake.
            template=session.plan.template,
            background_style=self._background_style,
            background_images=self._background_images,
            background_busy=self._background_pending,
            background_available=self.background_studio.available_offline(),
        )

    def _choose_background_style(self, style: str) -> None:
        """Apply offline AI after capture; no inference on the Kivy UI thread.

        A pending job blocks accepting/retaking. Its finished callback also
        checks generation, session, transaction, page and source-photo paths.
        """
        session, transaction = self.current_session, self.transaction
        if (self.is_closing or self.ui.current_screen != "review"
                or session is None or transaction is None or self._background_pending):
            return
        if style == ORIGINAL:
            self._background_generation += 1
            self._background_style = ORIGINAL
            self._background_images = None
            self._show_review(status_message="Foto asli digunakan tanpa pengolahan AI.")
            return
        if style != CLEAN_STUDIO:
            return
        if not self.background_studio.available_offline():
            self._show_review(status_message="Model AI belum tersedia offline. Gunakan Original.")
            return
        self._background_generation += 1
        generation = self._background_generation
        raw_paths = tuple(session.final_photo_paths)
        self._background_pending = True
        self._show_review(status_message="Sedang membuat latar Clean Studio...")
        def work():
            images = None
            failure = ""
            try:
                images = self.background_studio.process_three(raw_paths)
            except (BackgroundProcessingError, OSError, ValueError) as error:
                failure = str(error)
            except Exception:
                failure = "Model AI gagal memproses foto."
            def finish():
                if (self.is_closing or self._background_generation != generation
                        or self.current_session is not session
                        or self.transaction is not transaction
                        or tuple(session.final_photo_paths) != raw_paths
                        or self.ui.current_screen != "review"):
                    return
                self._background_pending = False
                self._background_images = images
                self._background_style = CLEAN_STUDIO if images is not None else ORIGINAL
                self._show_review(status_message=(
                    "Clean Studio siap. Periksa tepi rambut dan wajah."
                    if images is not None else
                    f"{failure} Foto Original dipulihkan."))
            self.root.after(0, finish)
        try:
            threading.Thread(target=work, daemon=True, name="meong-background-ai").start()
        except RuntimeError:
            self._background_pending = False
            self._background_style = ORIGINAL
            self._show_review(status_message="Gagal menjalankan AI. Foto Original tetap aman.")

    def _accept_current_session(self) -> None:
        # Compose and save this session's digital result, record it in the manifest, show the folder
        # QR and upload status, and start the final-screen timer when this is the last session.
        session = self.current_session
        transaction = self.transaction
        # Prevent duplicate acceptance from a queued double tap. Once result is
        # visible, another accept callback must not rewrite output or restart timers.
        if self.ui.current_screen != "review" or self._background_pending:
            return
        if session is None or transaction is None or not session.ready_for_review:
            self.ui.show_error(
                "Foto belum lengkap",
                "Ambil tiga foto terlebih dahulu sebelum melanjutkan.",
            )
            return

        output_path = (
            transaction.folder_path
            / "output"
            / session.plan.session_id
            / f"{session.plan.template.template_id}.png"
        )
        try:
            with self.store.photo_write_lock(transaction):
                compose_result(
                    photo_paths=session.final_photo_paths,
                    background_images=(self._background_images if self._background_style == CLEAN_STUDIO else None),
                    template=session.plan.template,
                    output_path=output_path,
                    transaction_id=transaction.transaction_id,
                    session_id=session.plan.session_id,
                    # Embed exactly the same folder destination used by the on-screen
                    # QR, including while offline. No payment QR belongs on this image.
                    folder_url=transaction.manifest.get("drive_folder_url"),
                )
                self.store.record_output(
                    transaction=transaction,
                    session_id=session.plan.session_id,
                    final_photos=session.final_photo_paths,
                    output_path=output_path,
                    background_style=self._background_style,
                )
            session.output_path = output_path
        except (OSError, RuntimeError, ValueError) as error:
            self.ui.show_error(
                "Hasil tidak dapat disimpan",
                f"Komposisi digital belum berhasil disimpan.\n\n{error}",
            )
            return

        has_next = self.session_index < len(self.sessions) - 1
        seconds_remaining = None if has_next else FINAL_SCREEN_SECONDS
        self.ui.show_result(
            image_path=output_path,
            session_label=self._session_label(session.plan),
            transaction_id=transaction.transaction_id,
            has_next_session=has_next,
            seconds_remaining=seconds_remaining,
            qr_image=(
                create_qr_image(transaction.manifest["drive_folder_url"])
                if self._should_show_result_qr()
                else None
            ),
            qr_pending=bool(
                transaction.manifest.get("drive_folder_url")
                and not self._should_show_result_qr()
            ),
            upload_message=self._upload_status_message(),
            print_message=f'Menyiapkan {session.plan.print_copies} lembar hasil yang sama...',
            print_busy=True,
        )
        self._start_print_job(output_path, copies=session.plan.print_copies)
        if self.drive_worker is not None:
            self.drive_worker.kick()
        if not has_next:
            self._start_completion_countdown()

    def _start_next_session(self) -> None:
        # Cancel the final-session timer and advance to the next planned session, or finish the
        # transaction if there is no next session.
        if self.ui.current_screen != "result":
            return
        self._cancel_completion_countdown()
        if self.session_index + 1 >= len(self.sessions):
            self._finish_transaction()
            return
        self.session_index += 1
        self._begin_current_session()

    def _retry_current_print(self) -> None:
        """Deliberately resend the current saved image after an automatic job."""
        session = self.current_session
        if (
            self.ui.current_screen != "result"
            or session is None
            or session.output_path is None
        ):
            return
        # Manual retry is always ONE explicitly requested sheet, not another
        # paid batch. Never retry an uncertain multi-copy job automatically.
        self._start_print_job(session.output_path, copies=1)

    def _start_print_job(self, image_path: Path, copies: int = 1) -> None:
        """Start one RAW transport submission containing N identical strips."""
        if self.is_closing:
            return
        if isinstance(copies, bool) or not isinstance(copies, int) or copies < 1:
            raise ValueError("A print batch must contain at least one copy.")
        path = Path(image_path)
        job_key = str(path.resolve())
        with self._print_lock:
            if job_key in self._print_jobs_in_flight:
                return
            self._print_jobs_in_flight.add(job_key)

        self.ui.set_print_status(
            f"Mengirim satu batch berisi {copies} lembar; periksa jumlah kertas...",
            busy=True,
        )
        worker = threading.Thread(
            target=self._print_in_background,
            args=(path, job_key, copies),
            name="thermal-printer",
            daemon=True,
        )
        try:
            worker.start()
        except RuntimeError as error:
            with self._print_lock:
                self._print_jobs_in_flight.discard(job_key)
            self.ui.set_print_status(f"Gagal memulai pencetakan ({error}).", busy=False)

    def _print_in_background(self, image_path: Path, job_key: str, copies: int = 1) -> None:
        """Submit one ESC/POS job containing N complete image-and-cut sequences.

        On Windows, a series of separately spooled RAW jobs can be accepted
        before the physical thermal printer catches up. Send the entire paid-
        copy *DEMO* batch in one RAW document, rather than opening/closing a
        spooler job for every copy. ThermalPrinter renders the saved photo once
        and repeats the resulting image + cut commands. Every strip therefore
        uses identical pixels and the current Floyd printer profile.

        A successful sender result means only that the batch was accepted by
        its transport, NOT that N physical sheets definitely came out. Never
        automatically retry an uncertain batch: the printer may already have
        printed part of it, which would produce duplicate paper.
        """
        result = PrintResult(False, "printer", "Batch cetak belum dimulai.")
        try:
            with self._print_device_lock:
                try:
                    result = self.printer.print_image(image_path, copies=copies)
                except Exception as error:
                    result = PrintResult(
                        False, "printer",
                        f"Pengiriman batch {copies} lembar gagal/tidak pasti "
                        f"({error}). Periksa kertas sebelum cetak ulang manual.",
                    )
                if result.success:
                    result = PrintResult(
                        True, result.transport,
                        f"Batch {copies} lembar diterima oleh {result.transport}. "
                        "Tunggu seluruh cetakan keluar dan periksa jumlah kertas.",
                        fell_back=result.fell_back,
                    )
                else:
                    result = PrintResult(
                        False, result.transport,
                        f"Batch {copies} lembar gagal/tidak pasti; sebagian mungkin "
                        f"sudah tercetak. Periksa kertas sebelum cetak ulang manual. "
                        f"{result.message}",
                        fell_back=result.fell_back,
                    )
        finally:
            with self._print_lock:
                self._print_jobs_in_flight.discard(job_key)

        if self.is_closing:
            return
        try:
            self.root.after(
                0,
                lambda: self._finish_print_job(image_path, result),
            )
        except Exception:
            # Kivy may already be closing, but no unverified batch is resent.
            return

    def _finish_print_job(self, image_path: Path, result: PrintResult) -> None:
        """Update only the result screen that still owns this output file."""
        session = self.current_session
        if (
            self.is_closing
            or self.ui.current_screen != "result"
            or session is None
            or session.output_path is None
            or session.output_path.resolve() != image_path.resolve()
        ):
            return
        self.ui.set_print_status(result.user_message, busy=False)

    def _start_next_session(self) -> None:
        # Cancel the final-session timer and advance to the next planned session, or finish the
        # transaction if there is no next session.
        if self.ui.current_screen != "result":
            return
        self._cancel_completion_countdown()
        if self.session_index + 1 >= len(self.sessions):
            self._finish_transaction()
            return
        self.session_index += 1
        self._begin_current_session()

    def _start_completion_countdown(self) -> None:
        # Initialize the automatic return timer shown after the final session is accepted.
        self._completion_remaining = FINAL_SCREEN_SECONDS
        self._schedule_completion_tick()

    def _schedule_completion_tick(self) -> None:
        # Update the visible timer and schedule its next tick. When no time remains, return the booth
        # to the welcome screen.
        if self._completion_remaining <= 0:
            # Allow the final print batch to finish before the result page
            # disappears. Sending two sheets may take longer than one,
            # and closing during a daemon print would risk missing copies.
            with self._print_lock:
                print_pending = bool(self._print_jobs_in_flight)
            if not print_pending:
                self._finish_transaction()
                return
            self._completion_remaining = 1
        self.ui.set_completion_countdown(self._completion_remaining)
        self._completion_after_id = self.root.after(
            1000,
            self._completion_countdown_tick,
        )

    def _completion_countdown_tick(self) -> None:
        # Handle one second of the result-screen timer, then schedule the next tick unless the app is
        # closing.
        self._completion_after_id = None
        if self.is_closing:
            return
        self._completion_remaining -= 1
        self._schedule_completion_tick()

    def _finish_transaction(self) -> None:
        # Mark the transaction complete in the local manifest, clear active session state, and return
        # to the welcome screen without deleting local files.
        # A delayed timer or retired result callback is not permission to end a
        # new order. Completion belongs to the final accepted result only; local
        # outputs may still be queued for Drive, so verified upload is not a gate.
        if (self.transaction is None or self.ui.current_screen != "result" or not self.sessions
                or self.session_index != len(self.sessions) - 1
                or self.current_session is not self.sessions[-1]
                or any(session.output_path is None for session in self.sessions)):
            return
        self._cancel_completion_countdown()
        if self.transaction is not None:
            try:
                self.store.complete_transaction(self.transaction)
            except OSError as error:
                self.ui.show_error(
                    "Status transaksi belum tersimpan",
                    f"Transaksi tetap berada di perangkat, tetapi manifest gagal diperbarui.\n\n{error}",
                )
                return

        self._background_generation += 1
        self._background_style = ORIGINAL
        self._background_images = None
        self._background_pending = False
        self.transaction = None
        self.sessions = []
        self.current_session = None
        self.session_index = 0
        self.ui.show_advertisement(
            self.camera_ready,
            self._storage_status_message(),
        )

    def _frame_to_image(self, frame) -> Image.Image:
        # Convert OpenCV's BGR camera frame into a Pillow RGB image, which the GUI and image-
        # composition code can display.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_frame)

    def _storage_status_message(self) -> str:
        # Translate the cached Drive-pool and local-only state into a short message for the customer
        # or booth operator.
        ready = self.drive_pool.ready_count
        if self.local_only_mode and ready == 0:
            return "Mode lokal aktif untuk pengembangan. Hasil hanya tersimpan di perangkat."
        if ready:
            if self.drive_pool.last_error or self.drive_client is None:
                return f"Offline. {ready} slot folder tersimpan dan siap dipakai."
            return f"Drive siap · {ready} slot folder tersedia. QR folder tersedia saat offline."
        if self.drive_pool.last_error:
            return f"Slot Drive perlu diperiksa: {self.drive_pool.last_error}"
        if self.drive_client is None:
            return "Apps Script Web App atau OAuth Drive belum dikonfigurasi. Periksa konfigurasi lokal."
        return "Menyiapkan folder transaksi Google Drive. Tombol aktif setelah slot tersedia."

    def _upload_status_message(self) -> str:
        # Summarize this transaction's upload state, including verified uploads, retries, offline
        # operation, and cases that need staff attention.
        transaction = self.transaction
        if transaction is None or not transaction.manifest.get("drive_folder_id"):
            return "Hasil digital tersimpan di perangkat ini."
        status = transaction.manifest.get("upload_status")
        if status == "UPLOAD_COMPLETE":
            return "Foto sudah diunggah dan diverifikasi di Google Drive."
        if status == "ACTION_REQUIRED":
            return "Unggahan perlu bantuan petugas. Salinan foto tetap tersimpan di perangkat."
        if self._current_session_upload_verified():
            return "Foto sesi ini sudah diunggah dan diverifikasi di folder transaksi."
        if status == "UPLOAD_RETRY" or self.drive_pool.last_error or self.drive_client is None:
            return "Internet terputus. QR membuka folder tujuan; foto akan muncul setelah upload dilanjutkan."
        if status == "UPLOADING":
            return "Foto sedang diunggah ke folder transaksi."
        return "Foto tersimpan di perangkat dan menunggu upload ke folder transaksi."

    def _schedule_drive_status_update(self) -> None:
        # Poll the latest manifest and Drive-pool state without blocking the UI, refresh storage or
        # result messages, and schedule the next poll.
        if self.is_closing:
            return
        if self.ui.current_screen == "templates":
            self.ui.set_storage_status(
                self.drive_pool.has_ready_slot() or self.local_only_mode,
                self._storage_status_message(),
            )
        elif self.ui.current_screen == "result":
            if self.transaction is not None:
                try:
                    self.transaction.manifest = json.loads(
                        self.transaction.manifest_path.read_text(encoding="utf-8")
                    )
                except (OSError, json.JSONDecodeError):
                    pass
            self.ui.set_result_upload_status(self._upload_status_message())
            if self.transaction is not None:
                folder_url = self.transaction.manifest.get("drive_folder_url")
                show_qr = bool(folder_url and self._should_show_result_qr())
                self.ui.set_result_qr(
                    create_qr_image(folder_url) if show_qr else None,
                    pending=bool(folder_url and not show_qr),
                )
        self._drive_status_after_id = self.root.after(1500, self._schedule_drive_status_update)

    def _should_show_result_qr(self) -> bool:
        """Expose the cached destination independently of network upload state."""
        # A reserved folder URL is stable before any files are uploaded. Encoding
        # that URL is entirely local and must not wait for upload verification:
        # a slow connection used to leave the result screen without a QR code.
        # The separate upload-status label explains when the folder is incomplete.
        # Local-only transactions have no real Drive destination; never invent one.
        return bool(
            self.transaction is not None
            and self.transaction.manifest.get("drive_folder_url")
        )

    def _current_session_upload_verified(self) -> bool:
        # Check the manifest records for every raw photo and the composed output in the current
        # session; return true only when each file is marked VERIFIED.
        transaction = self.transaction
        session = self.current_session
        if transaction is None or session is None:
            return False
        record = next(
            (
                item
                for item in transaction.manifest.get("sessions", [])
                if item.get("session_id") == session.plan.session_id
            ),
            None,
        )
        if record is None:
            return False
        paths = [photo["path"] for photo in record.get("raw_photos", [])]
        if record.get("output_path"):
            paths.append(record["output_path"])
        upload_files = transaction.manifest.get("upload_files", {})
        return bool(paths) and all(
            upload_files.get(path, {}).get("status") == "VERIFIED" for path in paths
        )

    def _cancel_after(self, after_id: ClockEvent | None) -> None:
        # Safely cancel a Kivy timer callback if it is still registered; the window may already
        # have closed between scheduling and cancellation.
        if after_id is not None:
            try:
                self.root.after_cancel(after_id)
            except RuntimeError:
                pass

    def _cancel_completion_countdown(self) -> None:
        # Cancel and reset the final-screen timer so it cannot finish a transaction after the customer
        # has moved to another screen.
        self._cancel_after(self._completion_after_id)
        self._completion_after_id = None
        self._completion_remaining = 0

    def close(self) -> None:
        # Shut down cleanly by cancelling pending UI timers, stopping background Drive sync, releasing
        # the camera, and destroying the Kivy window.
        if self.is_closing:
            return
        self.is_closing = True
        self._cancel_after(self._countdown_after_id)
        self._cancel_after(self._completion_after_id)
        self._cancel_after(self._preview_after_id)
        self._cancel_after(self._drive_status_after_id)
        self._countdown_after_id = None
        self._completion_after_id = None
        self._preview_after_id = None
        self._drive_status_after_id = None
        self.palm_worker.close()
        self.face_worker.close()
        self.retention_worker.stop()
        if self.drive_worker is not None:
            self.drive_worker.stop()
        self.camera.close()
        self.ui.dispose()
        try:
            self.root.destroy()
        except RuntimeError:
            pass

