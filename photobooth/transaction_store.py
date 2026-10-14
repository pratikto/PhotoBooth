"""Local transaction folders, persistent IDs, and manifests for the MVP."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Sequence

from PIL import Image

from photobooth.manifest_io import manifest_lock
from photobooth.workflow import SessionPlan


@dataclass
class LocalTransaction:
    transaction_id: str
    folder_path: Path
    manifest_path: Path
    manifest: dict[str, Any]


class TransactionStore:
    """Persist transaction counters and session files on local storage.

    The counter is advanced before the transaction folder is created. A crash
    or cancellation can leave a gap, but an allocated ID is never reused.
    """

    def __init__(
        self,
        photos_root: Path,
        state_path: Path,
        booth_id: str = "PB001",
    ) -> None:
        self.photos_root = Path(photos_root)
        self.state_path = Path(state_path)
        self.booth_id = booth_id
        if not re.fullmatch(r"[A-Za-z0-9]+", self.booth_id):
            raise ValueError("Booth ID may contain letters and numbers only.")

    def reserve_transaction_id(self) -> str:
        """Persist and return the next ID before a Drive folder is assigned."""
        return self._reserve_transaction_id()

    def advance_counter_past(self, transaction_id: str) -> None:
        """Keep local-only IDs ahead of IDs already preallocated to Drive slots."""
        prefix = f"{self.booth_id}_"
        if not transaction_id.startswith(prefix):
            raise ValueError("Transaction ID belongs to another booth.")
        suffix = transaction_id[len(prefix):]
        if not suffix.isdigit() or len(suffix) != 8:
            raise ValueError("Transaction ID must end with an eight-digit sequence.")
        minimum_next = int(suffix) + 1
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if self.state_path.exists():
            try:
                state = json.loads(self.state_path.read_text(encoding="utf-8"))
                if state.get("booth_id") != self.booth_id:
                    raise ValueError("The saved transaction counter belongs to another booth.")
                next_sequence = int(state["next_sequence"])
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                raise RuntimeError(
                    f"Transaction counter is invalid at {self.state_path}. "
                    "Stop new sessions and restore the counter before continuing."
                ) from error
        else:
            next_sequence = 1
        if next_sequence < 1:
            raise RuntimeError("The next transaction sequence must be positive.")
        if next_sequence < minimum_next:
            self._atomic_write_json(
                self.state_path,
                {"booth_id": self.booth_id, "next_sequence": minimum_next},
            )

    def start_transaction(
        self,
        plans: Sequence[SessionPlan],
        *,
        transaction_id: str | None = None,
        folder_path: Path | None = None,
        drive_slot: dict[str, Any] | None = None,
    ) -> LocalTransaction:
        if not plans:
            raise ValueError("Select at least one template session first.")

        self.photos_root.mkdir(parents=True, exist_ok=True)
        if transaction_id is None:
            transaction_id = self._reserve_transaction_id()
        folder_path = Path(folder_path) if folder_path is not None else self.photos_root / transaction_id
        if folder_path.resolve().parent != self.photos_root.resolve():
            raise ValueError("Transaction folders must be direct children of the photo storage root.")
        if folder_path.exists():
            if not folder_path.is_dir() or any(folder_path.iterdir()):
                raise FileExistsError(f"Transaction folder is not empty: {folder_path}")
        else:
            folder_path.mkdir(parents=False, exist_ok=False)

        manifest_path = folder_path / "manifest.json"
        sessions = [
            {
                "session_id": plan.session_id,
                "template_id": plan.template.template_id,
                "template_name": plan.template.name,
                "order_number": plan.order_number,
                "total_sessions": plan.total_sessions,
                "template_session_number": plan.template_session_number,
                "template_session_count": plan.template_session_count,
                "status": "PENDING",
                "raw_photos": [],
                "retake_used": False,
                "selected_photo": None,
                "final_photos": [],
                "output_path": None,
            }
            for plan in plans
        ]

        manifest: dict[str, Any] = {
            "schema_version": 1,
            "transaction_id": transaction_id,
            "booth_id": self.booth_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "IN_PROGRESS",
            "drive_folder_id": drive_slot.get("folder_id") if drive_slot else None,
            "drive_folder_url": drive_slot.get("folder_url") if drive_slot else None,
            "drive_slot_key": drive_slot.get("slot_key") if drive_slot else None,
            "upload_status": "ASSIGNED" if drive_slot else "LOCAL_ONLY",
            "upload_files": {},
            "sessions": sessions,
        }
        transaction = LocalTransaction(
            transaction_id=transaction_id,
            folder_path=folder_path,
            manifest_path=manifest_path,
            manifest=manifest,
        )
        self._write_manifest(transaction)
        return transaction

    def save_raw_photo(
        self,
        transaction: LocalTransaction,
        session: SessionPlan,
        image: Image.Image,
        filename: str,
        role: str,
    ) -> Path:
        """Save one camera capture and immediately record it in the manifest."""
        if Path(filename).name != filename or not filename.lower().endswith(".jpg"):
            raise ValueError("Photo filename must be a simple .jpg filename.")
        if role not in {"capture", "retake"}:
            raise ValueError("Photo role must be capture or retake.")

        relative_path = Path("raw") / session.session_id / filename
        photo_path = transaction.folder_path / relative_path
        photo_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = photo_path.with_name(f".{photo_path.stem}.tmp.jpg")

        image.convert("RGB").save(temporary_path, format="JPEG", quality=95)
        os.replace(temporary_path, photo_path)

        session_record = self._session_record(transaction, session.session_id)
        session_record["status"] = "CAPTURING"
        photo_record = {"path": relative_path.as_posix(), "role": role}
        session_record["raw_photos"] = [
            existing
            for existing in session_record["raw_photos"]
            if existing["path"] != relative_path.as_posix()
        ]
        session_record["raw_photos"].append(photo_record)
        relative_string = relative_path.as_posix()
        transaction.manifest["upload_files"][relative_string] = {
            "path": relative_string,
            "status": "PENDING_UPLOAD" if transaction.manifest.get("drive_folder_id") else "LOCAL_ONLY",
            "size_bytes": photo_path.stat().st_size,
            "drive_file_id": None,
            "md5_checksum": None,
            "upload_session_url": None,
        }
        self._write_manifest(transaction)
        return photo_path

    def record_retake(
        self,
        transaction: LocalTransaction,
        session_id: str,
        selected_photo: Path,
    ) -> None:
        """Record the selected initial photo replaced by this session's retake."""
        session_record = self._session_record(transaction, session_id)
        session_record["retake_used"] = True
        session_record["selected_photo"] = self._relative_path(
            transaction, selected_photo
        )
        self._write_manifest(transaction)

    def record_output(
        self,
        transaction: LocalTransaction,
        session_id: str,
        final_photos: Sequence[Path],
        output_path: Path,
    ) -> None:
        """Record the final digital composition and photos used to create it."""
        if len(final_photos) != 3:
            raise ValueError("A session output must use exactly three photos.")
        output_path = Path(output_path)
        if not output_path.is_file():
            raise FileNotFoundError(f"Output image was not found: {output_path}")

        session_record = self._session_record(transaction, session_id)
        session_record["final_photos"] = [
            self._relative_path(transaction, path) for path in final_photos
        ]
        output_relative = self._relative_path(transaction, output_path)
        session_record["output_path"] = output_relative
        session_record["status"] = "COMPLETED"
        transaction.manifest["upload_files"][output_relative] = {
            "path": output_relative,
            "status": "PENDING_UPLOAD" if transaction.manifest.get("drive_folder_id") else "LOCAL_ONLY",
            "size_bytes": output_path.stat().st_size,
            "drive_file_id": None,
            "md5_checksum": None,
            "upload_session_url": None,
        }
        self._write_manifest(transaction)

    def complete_transaction(self, transaction: LocalTransaction) -> None:
        transaction.manifest["status"] = "COMPLETED"
        transaction.manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        if transaction.manifest.get("drive_folder_id") and transaction.manifest.get("upload_status") not in {
            "UPLOAD_COMPLETE",
            "ACTION_REQUIRED",
        }:
            transaction.manifest["upload_status"] = "PENDING_UPLOAD"
        self._write_manifest(transaction)

    def _reserve_transaction_id(self) -> str:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if self.state_path.exists():
            try:
                state = json.loads(self.state_path.read_text(encoding="utf-8"))
                if state.get("booth_id") != self.booth_id:
                    raise ValueError("The saved transaction counter belongs to another booth.")
                next_sequence = int(state["next_sequence"])
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                raise RuntimeError(
                    f"Transaction counter is invalid at {self.state_path}. "
                    "Stop new sessions and restore the counter before continuing."
                ) from error
        else:
            next_sequence = 1

        if next_sequence < 1:
            raise RuntimeError("The next transaction sequence must be positive.")

        state = {
            "booth_id": self.booth_id,
            "next_sequence": next_sequence + 1,
        }
        self._atomic_write_json(self.state_path, state)
        return f"{self.booth_id}_{next_sequence:08d}"

    def _session_record(
        self,
        transaction: LocalTransaction,
        session_id: str,
    ) -> dict[str, Any]:
        for record in transaction.manifest["sessions"]:
            if record["session_id"] == session_id:
                return record
        raise KeyError(f"Session not found in transaction: {session_id}")

    def _relative_path(self, transaction: LocalTransaction, path: Path) -> str:
        try:
            return Path(path).resolve().relative_to(
                transaction.folder_path.resolve()
            ).as_posix()
        except ValueError as error:
            raise ValueError("Transaction files must remain inside their transaction folder.") from error

    def _write_manifest(self, transaction: LocalTransaction) -> None:
        with manifest_lock(transaction.manifest_path):
            if transaction.manifest_path.exists():
                try:
                    persisted = json.loads(
                        transaction.manifest_path.read_text(encoding="utf-8")
                    )
                    if persisted.get("transaction_id") == transaction.transaction_id:
                        persisted_files = persisted.get("upload_files", {})
                        current_files = transaction.manifest.setdefault("upload_files", {})
                        for relative_path, record in persisted_files.items():
                            current = current_files.setdefault(relative_path, {})
                            current.update(record)
                        statuses = [
                            record.get("status")
                            for record in current_files.values()
                        ]
                        if "ACTION_REQUIRED" in statuses:
                            transaction.manifest["upload_status"] = "ACTION_REQUIRED"
                        elif statuses and all(status == "VERIFIED" for status in statuses):
                            transaction.manifest["upload_status"] = (
                                "UPLOAD_COMPLETE"
                                if transaction.manifest.get("status") == "COMPLETED"
                                else "PENDING_UPLOAD"
                            )
                        elif "UPLOADING" in statuses:
                            transaction.manifest["upload_status"] = "UPLOADING"
                        elif "UPLOAD_RETRY" in statuses:
                            transaction.manifest["upload_status"] = "UPLOAD_RETRY"
                        elif transaction.manifest.get("drive_folder_id"):
                            transaction.manifest["upload_status"] = "PENDING_UPLOAD"
                except (OSError, json.JSONDecodeError, TypeError):
                    # The current in-memory transaction remains the source if the
                    # last atomic manifest write cannot be read.
                    pass
            self._atomic_write_json(transaction.manifest_path, transaction.manifest)

    @staticmethod
    def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            text=True,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, path)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
