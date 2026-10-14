"""Application controller for the first local PhotoBooth workflow.

This milestone implements template quantities, independent photo sessions,
three captures, one retake per session, local compositions, and transaction
folders. QRIS payment, printing, and Google Drive synchronization are not part
of this runnable stage.
"""

import os
from pathlib import Path
import tkinter as tk

import cv2
from PIL import Image

from photobooth.camera import Camera
from photobooth.catalog import compose_result, get_templates
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
        self.store = TransactionStore(
            photos_root=PROJECT_ROOT / "photos",
            state_path=PROJECT_ROOT / "data" / "booth_state.json",
            booth_id=BOOTH_ID,
        )

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
                "Kamera terhubung. Hasil sesi akan disimpan di perangkat.",
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
            status_message="Kamera siap. Pembayaran dan cetak belum digunakan pada tahap ini.",
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
            self.transaction = self.store.start_transaction(plans)
        except (OSError, RuntimeError, ValueError) as error:
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
        )
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
            "Kamera siap. Hasil foto disimpan di perangkat.",
        )

    def _frame_to_image(self, frame) -> Image.Image:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_frame)

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
        self._countdown_after_id = None
        self._completion_after_id = None
        self._preview_after_id = None
        self.camera.close()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

