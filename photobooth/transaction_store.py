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

    def start_transaction(self, plans: Sequence[SessionPlan]) -> LocalTransaction:
        if not plans:
            raise ValueError("Select at least one template session first.")

        self.photos_root.mkdir(parents=True, exist_ok=True)

        while True:
            transaction_id = self._reserve_transaction_id()
            folder_path = self.photos_root / transaction_id
            try:
                folder_path.mkdir(parents=False, exist_ok=False)
                break
            except FileExistsError:
                # Treat an unexpected folder as already allocated and skip it.
                continue

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
        session_record["output_path"] = self._relative_path(transaction, output_path)
        session_record["status"] = "COMPLETED"
        self._write_manifest(transaction)

    def complete_transaction(self, transaction: LocalTransaction) -> None:
        transaction.manifest["status"] = "COMPLETED"
        transaction.manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
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
