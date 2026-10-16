# PhotoBooth source file
# Application controller connecting customer actions, camera capture, local transaction storage, Drive synchronization, and the Kivy screens.

"""Application controller for the procedure's capture and Drive workflow.

Payment and printing are left out until those integrations are ready. When
Drive credentials are configured, transactions use pre-verified folder slots,
show the cached folder QR, and synchronize files in the background.
"""

import os
import json
import time
from pathlib import Path
from kivy.clock import ClockEvent

import cv2
from PIL import Image

from photobooth.camera import Camera
from photobooth.catalog import PRICE_PER_SESSION, compose_result, get_templates
from photobooth.drive_pool import DriveSlotPool
from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError, GoogleDriveClient
from photobooth.drive_sync import DriveSyncWorker
from photobooth.palm_gesture import MAX_RESULT_AGE, PALM_CONFIDENCE, PalmGestureWorker, PalmHoldTrigger
from photobooth.qr_code import create_qr_image
from photobooth.retention import PhotoRetentionWorker
from photobooth.transaction_store import LocalTransaction, TransactionStore
from photobooth.ui_kivy import KivyHost, PhotoBoothUI
from photobooth.workflow import PhotoSession, SessionPlan, build_session_plans


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

        self.ui = PhotoBoothUI(
            root=self.root,
            templates=self.templates,
            on_home_start=self._open_template_selection,
            on_start=self._open_dummy_payment,
            on_capture=self._start_capture_countdown,
            on_select_photo=self._select_photo,
            on_retake=self._prepare_retake,
            on_accept_session=self._accept_current_session,
            on_next_session=self._start_next_session,
            on_finish=self._finish_transaction,
            on_close=self.close,
        )
        self.ui.show_welcome(False, "Kamera sedang diperiksa...")
        self.retention_worker = PhotoRetentionWorker(self.photos_root, self.drive_client)
        self.retention_worker.start()
        self.root.after(100, self._connect_camera)
        self._schedule_drive_status_update()

    def run(self) -> None:
        """Start Kivy's event loop."""
        self.root.mainloop()

    def _connect_camera(self) -> None:
        # Open the selected camera, read an initial frame to verify it works, and update the welcome
        # screen with the camera and storage status.
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
            self.ui.show_welcome(
                True,
                self._storage_status_message(),
            )
            self._update_preview()
        else:
            self.ui.show_welcome(
                False,
                "Kamera tidak terdeteksi. Periksa koneksi atau indeks kamera.",
            )

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

        self._preview_after_id = self.root.after(30, self._update_preview)

    def _update_palm_trigger(self, frame) -> None:
        """Accept only recent observations from this exact capture-page revision.

        A positive hold uses the same camera/selection/quota/countdown checks as
        the button. During a countdown we still observe hand release, but never
        accumulate the next hold. Missing frames invalidate all in-flight work.
        """
        if (frame is None or not self.camera_ready or self.ui.current_screen != "capture"
                or self.current_session is None or self.is_closing):
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
        if not self.camera_ready and self.ui.current_screen not in {"templates", "payment"}:
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
        # The agreed tariff is IDR 5,000 per quantity/session. Payment remains
        # simulated, but its displayed amount must match the real order tariff.
        unit_price = PRICE_PER_SESSION
        summary = "\n".join(
            f"{template.name} x {order.get(template.template_id, 0)}"
            for template in self.templates if order.get(template.template_id, 0)
        )
        self.ui.show_payment(
            order_summary=summary,
            session_count=len(plans),
            total_amount=len(plans) * unit_price,
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
        # Validate the selected quantities, create one plan per session, claim a preassigned Drive
        # folder when available, and persist the transaction locally before capturing any photos.
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
        self._show_capture_screen()

    def _session_label(self, plan: SessionPlan) -> str:
        # Build the customer-facing label that shows the order position and, when relevant, the
        # position among sessions using the same template.
        label = (
            f"Sesi {plan.order_number} dari {plan.total_sessions}"
            f" · {plan.template.name}"
        )
        if plan.template_session_count > 1:
            label += (
                f" · Sesi template {plan.template_session_number}"
                f" dari {plan.template_session_count}"
            )
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
        )

    def _accept_current_session(self) -> None:
        # Compose and save this session's digital result, record it in the manifest, show the folder
        # QR and upload status, and start the final-screen timer when this is the last session.
        session = self.current_session
        transaction = self.transaction
        # Prevent duplicate acceptance from a queued double tap. Once result is
        # visible, another accept callback must not rewrite output or restart timers.
        if self.ui.current_screen != "review":
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
        )
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

    def _start_completion_countdown(self) -> None:
        # Initialize the automatic return timer shown after the final session is accepted.
        self._completion_remaining = FINAL_SCREEN_SECONDS
        self._schedule_completion_tick()

    def _schedule_completion_tick(self) -> None:
        # Update the visible timer and schedule its next tick. When no time remains, return the booth
        # to the welcome screen.
        if self._completion_remaining <= 0:
            self._finish_transaction()
            return
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

        self.transaction = None
        self.sessions = []
        self.current_session = None
        self.session_index = 0
        self.ui.show_welcome(
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
        self.retention_worker.stop()
        if self.drive_worker is not None:
            self.drive_worker.stop()
        self.camera.close()
        try:
            self.root.destroy()
        except RuntimeError:
            pass

