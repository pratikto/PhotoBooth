"""Application controller for the procedure's capture and Drive workflow.

Payment and printing are left out until those integrations are ready. When
Drive credentials are configured, transactions use pre-verified folder slots,
show the cached folder QR, and synchronize files in the background.
"""

import os
import json
from pathlib import Path
import tkinter as tk

import cv2
from PIL import Image

from photobooth.camera import Camera
from photobooth.catalog import compose_result, get_templates
from photobooth.drive_pool import DriveSlotPool
from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError, GoogleDriveClient
from photobooth.drive_sync import DriveSyncWorker
from photobooth.qr_code import create_qr_image
from photobooth.transaction_store import LocalTransaction, TransactionStore
from photobooth.ui_tkinter import PhotoBoothUI
from photobooth.workflow import PhotoSession, SessionPlan, build_session_plans


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOTH_ID = os.environ.get("PHOTOBOOTH_ID", "PB001")
CAMERA_INDEX = int(os.environ.get("PHOTOBOOTH_CAMERA_INDEX", "0"))
CAPTURE_COUNTDOWN_SECONDS = 5
FINAL_SCREEN_SECONDS = 60


class PhotoBoothApp:
    """Coordinate the camera, GUI workflow, and local transaction files."""

    def __init__(self) -> None:
        self.root = tk.Tk()
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
        self.is_closing = False
        self.transaction: LocalTransaction | None = None
        self.sessions: list[PhotoSession] = []
        self.session_index = 0
        self.current_session: PhotoSession | None = None

        self._countdown_remaining = 0
        self._countdown_is_retake = False
        self._countdown_after_id: str | None = None
        self._completion_remaining = 0
        self._completion_after_id: str | None = None
        self._preview_after_id: str | None = None
        self._drive_status_after_id: str | None = None

        self.ui = PhotoBoothUI(
            root=self.root,
            templates=self.templates,
            on_home_start=self._open_template_selection,
            on_start=self._start_transaction,
            on_capture=self._start_capture_countdown,
            on_select_photo=self._select_photo,
            on_retake=self._start_retake_countdown,
            on_accept_session=self._accept_current_session,
            on_next_session=self._start_next_session,
            on_finish=self._finish_transaction,
            on_close=self.close,
        )
        self.ui.show_welcome(False, "Kamera sedang diperiksa...")
        self.root.after(100, self._connect_camera)
        self._schedule_drive_status_update()

    def run(self) -> None:
        """Start Tkinter's event loop."""
        self.root.mainloop()

    def _connect_camera(self) -> None:
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
        if self.is_closing:
            return

        frame = self.camera.read()
        if frame is None:
            self.current_frame = None
            self.ui.set_status("Menunggu gambar dari kamera...")
            if self.ui.current_screen == "capture":
                self.ui.set_capture_enabled(False)
            self._preview_after_id = self.root.after(120, self._update_preview)
            return

        self.current_frame = frame
        if self.ui.current_screen == "capture":
            self.ui.update_live_preview(self._frame_to_image(frame))
            session = self.current_session
            if (
                session is not None
                and self._countdown_after_id is None
                and len(session.initial_photo_paths) < 3
            ):
                self.ui.set_capture_enabled(True)

        self._preview_after_id = self.root.after(30, self._update_preview)

    def _open_template_selection(self) -> None:
        if not self.camera_ready:
            self.ui.show_error(
                "Kamera belum siap",
                "Sambungkan kamera sebelum memulai sesi foto.",
            )
            return
        self.ui.show_template_selection(
            camera_ready=True,
            storage_ready=(self.drive_pool.has_ready_slot() or self.local_only_mode),
            status_message=self._storage_status_message(),
        )

    def _start_transaction(self, quantities: dict[str, int]) -> None:
        if not self.camera_ready:
            self.ui.show_error("Kamera belum siap", "Sesi foto belum dapat dimulai.")
            return

        try:
            plans = build_session_plans(self.templates, quantities)
            if not plans:
                self.ui.show_error(
                    "Template belum dipilih",
                    "Pilih minimal satu sesi template untuk melanjutkan.",
                )
                return
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
            self._open_template_selection()
            return

        self.sessions = [PhotoSession(plan=plan) for plan in plans]
        self.session_index = 0
        self._begin_current_session()

    def _begin_current_session(self) -> None:
        if not self.sessions:
            return
        self.current_session = self.sessions[self.session_index]
        self._show_capture_screen()

    def _session_label(self, plan: SessionPlan) -> str:
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
        session = self.current_session
        if session is None:
            return
        count = len(session.initial_photo_paths)
        self.ui.show_capture(
            session_label=self._session_label(session.plan),
            capture_count=count,
            preview_image=(
                self._frame_to_image(self.current_frame)
                if self.current_frame is not None
                else None
            ),
            action_label=f"AMBIL FOTO {min(count + 1, 3)}",
            can_capture=(
                self.camera_ready
                and self.current_frame is not None
                and count < 3
            ),
        )

    def _start_capture_countdown(self) -> None:
        session = self.current_session
        if (
            session is None
            or len(session.initial_photo_paths) >= 3
            or self._countdown_after_id is not None
        ):
            return
        self._start_countdown(is_retake=False)

    def _start_retake_countdown(self) -> None:
        session = self.current_session
        if session is None or not session.can_retake or self._countdown_after_id is not None:
            return
        self._start_countdown(is_retake=True)

    def _start_countdown(self, is_retake: bool) -> None:
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
        )

    def _accept_current_session(self) -> None:
        session = self.current_session
        transaction = self.transaction
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
            compose_result(
                photo_paths=session.final_photo_paths,
                template=session.plan.template,
                output_path=output_path,
                transaction_id=transaction.transaction_id,
                session_id=session.plan.session_id,
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
        self._cancel_completion_countdown()
        if self.session_index + 1 >= len(self.sessions):
            self._finish_transaction()
            return
        self.session_index += 1
        self._begin_current_session()

    def _start_completion_countdown(self) -> None:
        self._completion_remaining = FINAL_SCREEN_SECONDS
        self._schedule_completion_tick()

    def _schedule_completion_tick(self) -> None:
        if self._completion_remaining <= 0:
            self._finish_transaction()
            return
        self.ui.set_completion_countdown(self._completion_remaining)
        self._completion_after_id = self.root.after(
            1000,
            self._completion_countdown_tick,
        )

    def _completion_countdown_tick(self) -> None:
        self._completion_after_id = None
        if self.is_closing:
            return
        self._completion_remaining -= 1
        self._schedule_completion_tick()

    def _finish_transaction(self) -> None:
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
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_frame)

    def _storage_status_message(self) -> str:
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
        transaction = self.transaction
        session = self.current_session
        if transaction is None or session is None:
            return False
        manifest = transaction.manifest
        if not manifest.get("drive_folder_url"):
            return False
        if self.drive_client is None or self.drive_pool.last_error:
            return True
        if manifest.get("upload_status") in {
            "UPLOAD_RETRY",
            "ACTION_REQUIRED",
            "UPLOAD_COMPLETE",
        }:
            return True
        return self._current_session_upload_verified()

    def _current_session_upload_verified(self) -> bool:
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

    def _cancel_after(self, after_id: str | None) -> None:
        if after_id is not None:
            try:
                self.root.after_cancel(after_id)
            except tk.TclError:
                pass

    def _cancel_completion_countdown(self) -> None:
        self._cancel_after(self._completion_after_id)
        self._completion_after_id = None
        self._completion_remaining = 0

    def close(self) -> None:
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
        if self.drive_worker is not None:
            self.drive_worker.stop()
        self.camera.close()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

