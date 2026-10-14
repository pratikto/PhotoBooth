"""Persistent local ledger for pre-created Google Drive transaction folders."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import threading
from typing import Any

from photobooth.drive_storage import DriveApiError, GoogleDriveClient, RemoteDriveSlot


@dataclass
class DriveSlot:
    folder_id: str
    folder_url: str
    slot_key: str
    status: str
    folder_name: str
    staging_path: str
    transaction_id: str | None = None
    rename_pending: bool = False
    claim_pending: bool = False
    issue: str | None = None

    def to_manifest(self) -> dict[str, Any]:
        return {
            "folder_id": self.folder_id,
            "folder_url": self.folder_url,
            "slot_key": self.slot_key,
            "status": self.status,
            "folder_name": self.folder_name,
            "staging_path": self.staging_path,
            "transaction_id": self.transaction_id,
            "rename_pending": self.rename_pending,
            "claim_pending": self.claim_pending,
        }


class DriveSlotPool:
    """Cache, validate, and assign a never-reused pool of Drive folders."""

    def __init__(
        self,
        photos_root: Path,
        state_path: Path,
        booth_id: str,
        target_ready: int = 25,
    ) -> None:
        self.photos_root = Path(photos_root)
        self.state_path = Path(state_path)
        self.booth_id = booth_id
        self.target_ready = target_ready
        self._lock = threading.RLock()
        self._slots: list[DriveSlot] = []
        self.last_error: str | None = None
        self._load()

    @property
    def ready_count(self) -> int:
        with self._lock:
            return sum(slot.status == "READY" for slot in self._slots)

    @property
    def assigned_count(self) -> int:
        with self._lock:
            return sum(slot.status == "ASSIGNED" for slot in self._slots)

    def refresh(self, client: GoogleDriveClient) -> None:
        """Reconcile cached slots with Drive and top the ready pool back up."""
        remote_slots = client.ensure_folder_pool(self.booth_id, self.target_ready)
        remote_by_id = {slot.folder_id: slot for slot in remote_slots}
        with self._lock:
            existing_by_id = {slot.folder_id: slot for slot in self._slots}
            merged: dict[str, DriveSlot] = {}

            for folder_id, current in existing_by_id.items():
                remote = remote_by_id.get(folder_id)
                if current.status in {"ASSIGNED", "CLAIMING"} or (
                    current.status == "ACTION_REQUIRED" and current.transaction_id
                ):
                    # Local assignment survives offline use and remote sync.
                    merged[folder_id] = current
                    continue
                if remote is not None and remote.verified and remote.status == "READY":
                    stage_path = Path(current.staging_path)
                    try:
                        stage_path.parent.mkdir(parents=True, exist_ok=True)
                        stage_path.mkdir(parents=True, exist_ok=True)
                        if any(stage_path.iterdir()):
                            raise OSError("Local staging folder is not empty.")
                        merged[folder_id] = self._from_remote(remote, current.staging_path)
                    except OSError as error:
                        merged[folder_id] = DriveSlot(
                            **{
                                **asdict(current),
                                "status": "ACTION_REQUIRED",
                                "issue": str(error),
                            }
                        )
                    continue
                else:
                    merged[folder_id] = DriveSlot(
                        **{
                            **asdict(current),
                            "status": "ACTION_REQUIRED",
                            "issue": remote.issue if remote else "Cached folder could not be verified in Drive.",
                        }
                    )

            for folder_id, remote in remote_by_id.items():
                if folder_id in merged:
                    continue
                stage_path = self.photos_root / ".pool" / folder_id
                if remote.status == "READY" and remote.verified:
                    try:
                        stage_path.parent.mkdir(parents=True, exist_ok=True)
                        stage_path.mkdir(parents=False, exist_ok=True)
                        if any(stage_path.iterdir()):
                            raise OSError("Local staging folder is not empty.")
                        merged[folder_id] = self._from_remote(remote, str(stage_path))
                    except OSError as error:
                        merged[folder_id] = DriveSlot(
                            folder_id=remote.folder_id,
                            folder_url=remote.folder_url,
                            slot_key=remote.slot_key,
                            status="ACTION_REQUIRED",
                            folder_name=remote.folder_name,
                            staging_path=str(stage_path),
                            issue=str(error),
                        )
                else:
                    merged[folder_id] = DriveSlot(
                        folder_id=remote.folder_id,
                        folder_url=remote.folder_url,
                        slot_key=remote.slot_key,
                        status="ACTION_REQUIRED",
                        folder_name=remote.folder_name,
                        staging_path=str(stage_path),
                        transaction_id=remote.transaction_id,
                        issue=remote.issue or f"Remote slot status is {remote.status}.",
                    )

            self._slots = sorted(merged.values(), key=lambda slot: (slot.status != "READY", slot.folder_id))
            issues = [slot.issue for slot in self._slots if slot.status == "ACTION_REQUIRED" and slot.issue]
            ready_count = sum(slot.status == "READY" for slot in self._slots)
            self.last_error = issues[0] if issues and ready_count < self.target_ready else None
            self._save()

    def has_ready_slot(self) -> bool:
        return self.ready_count > 0

    def claim(self) -> DriveSlot:
        """Consume a ready slot whose final transaction ID is already assigned."""
        with self._lock:
            slot = next((candidate for candidate in self._slots if candidate.status == "READY"), None)
            if slot is None:
                raise DriveApiError("No verified Drive folder slots are available.")
            transaction_id = slot.transaction_id
            if not transaction_id or slot.folder_name != transaction_id:
                slot.status = "ACTION_REQUIRED"
                slot.issue = "Drive slot has no preassigned final transaction ID."
                self._save()
                raise DriveApiError(slot.issue)
            source = Path(slot.staging_path)
            target = self.photos_root / transaction_id
            if target.exists():
                raise DriveApiError(f"Transaction folder already exists: {target}")
            try:
                if not source.is_dir() or any(source.iterdir()):
                    raise OSError("The local staging folder is missing or not empty.")
                slot.status = "CLAIMING"
                slot.claim_pending = True
                slot.rename_pending = False
                self._save()
                os.replace(source, target)
                slot.staging_path = str(target)
                slot.status = "ASSIGNED"
                slot.issue = None
                self._save()
                return DriveSlot(**asdict(slot))
            except OSError as error:
                slot.status = "ACTION_REQUIRED"
                slot.issue = str(error)
                self._save()
                raise DriveApiError(f"Could not prepare the local transaction folder: {error}") from error

    def recover_incomplete_claims(self) -> None:
        with self._lock:
            recovered = False
            for slot in self._slots:
                if slot.status != "CLAIMING" or not slot.transaction_id:
                    continue
                source = Path(slot.staging_path)
                target = self.photos_root / slot.transaction_id
                try:
                    if not target.exists() and source.is_dir():
                        os.replace(source, target)
                    if target.is_dir():
                        slot.staging_path = str(target)
                        slot.status = "ASSIGNED"
                        slot.rename_pending = False
                        slot.claim_pending = True
                    else:
                        slot.status = "ACTION_REQUIRED"
                        slot.issue = "A folder slot was claimed before restart and needs staff review."
                except OSError as error:
                    slot.status = "ACTION_REQUIRED"
                    slot.issue = str(error)
                recovered = True
            if recovered:
                self._save()

    def pending_assignments(self) -> list[DriveSlot]:
        with self._lock:
            return [
                DriveSlot(**asdict(slot))
                for slot in self._slots
                if slot.status == "ASSIGNED" and slot.claim_pending
            ]

    def mark_assigned(self, folder_id: str) -> None:
        with self._lock:
            slot = self._get(folder_id)
            slot.claim_pending = False
            slot.issue = None
            self._save()

    def record_refresh_error(self, error: Exception) -> None:
        with self._lock:
            self.last_error = str(error)
            self._save()

    def _get(self, folder_id: str) -> DriveSlot:
        for slot in self._slots:
            if slot.folder_id == folder_id:
                return slot
        raise KeyError(f"Drive folder slot not found: {folder_id}")

    @staticmethod
    def _from_remote(remote: RemoteDriveSlot, staging_path: str) -> DriveSlot:
        return DriveSlot(
            folder_id=remote.folder_id,
            folder_url=remote.folder_url,
            slot_key=remote.slot_key,
            status=remote.status,
            folder_name=remote.folder_name,
            staging_path=staging_path,
            transaction_id=remote.transaction_id,
            issue=remote.issue,
        )

    def _load(self) -> None:
        if not self.state_path.exists():
            return
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
            if payload.get("booth_id") != self.booth_id:
                raise ValueError("Drive slot cache belongs to another booth ID.")
            self._slots = [DriveSlot(**entry) for entry in payload.get("slots", [])]
            self.last_error = payload.get("last_error")
        except (OSError, json.JSONDecodeError, TypeError, ValueError, KeyError) as error:
            self.last_error = f"Drive slot cache needs repair: {error}"
            self._slots = []

    def _save(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "booth_id": self.booth_id,
            "target_ready": self.target_ready,
            "last_error": self.last_error,
            "slots": [asdict(slot) for slot in self._slots],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.state_path.name}.",
            suffix=".tmp",
            dir=self.state_path.parent,
            text=True,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, self.state_path)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
