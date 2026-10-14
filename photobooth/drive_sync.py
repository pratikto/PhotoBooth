"""Resumable background sync for assigned Drive folders and local manifests."""

from __future__ import annotations

import json
from pathlib import Path
import threading
from typing import Any

from photobooth.drive_pool import DriveSlotPool
from photobooth.drive_storage import DriveApiError, GoogleDriveClient
from photobooth.manifest_io import manifest_lock, write_json_atomic


def sync_manifest(manifest_path: Path, client: GoogleDriveClient) -> dict[str, Any]:
    """Upload pending files for one transaction and persist verification per file."""
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    folder_id = manifest.get("drive_folder_id")
    transaction_id = manifest.get("transaction_id")
    upload_files: dict[str, dict[str, Any]] = manifest.get("upload_files", {})
    if not folder_id or not transaction_id or not upload_files:
        return manifest

    for relative_path in list(upload_files):
        record = upload_files[relative_path]
        if record.get("status") == "VERIFIED":
            continue
        if record.get("status") == "ACTION_REQUIRED":
            continue

        local_path = (manifest_path.parent / relative_path).resolve()
        try:
            local_path.relative_to(manifest_path.parent.resolve())
        except ValueError:
            record["status"] = "ACTION_REQUIRED"
            record["error"] = "Upload path is outside the transaction folder."
            _persist_upload_progress(manifest_path, manifest)
            continue

        if not local_path.is_file():
            record["status"] = "ACTION_REQUIRED"
            record["error"] = "Local transaction file is missing."
            _persist_upload_progress(manifest_path, manifest)
            continue

        record["status"] = "UPLOADING"
        record.pop("error", None)
        manifest["upload_status"] = "UPLOADING"
        _persist_upload_progress(manifest_path, manifest)

        def save_session_url(value: str | None) -> None:
            record["upload_session_url"] = value
            _persist_upload_progress(manifest_path, manifest)

        try:
            remote_file = client.upload_file(
                folder_id,
                transaction_id,
                relative_path,
                local_path,
                resume_url=record.get("upload_session_url"),
                on_session_url=save_session_url,
            )
            record.update(
                {
                    "status": "VERIFIED",
                    "drive_file_id": remote_file["id"],
                    "size_bytes": int(remote_file["size"]),
                    "md5_checksum": remote_file["md5Checksum"],
                    "upload_session_url": None,
                    "verified": True,
                }
            )
        except DriveApiError as error:
            record["status"] = "UPLOAD_RETRY" if error.transient else "ACTION_REQUIRED"
            record["error"] = str(error)
        _refresh_upload_status(manifest)
        _persist_upload_progress(manifest_path, manifest)

    _refresh_upload_status(manifest)
    _persist_upload_progress(manifest_path, manifest)
    return manifest


def _refresh_upload_status(manifest: dict[str, Any]) -> None:
    records = list(manifest.get("upload_files", {}).values())
    if any(record.get("status") == "ACTION_REQUIRED" for record in records):
        manifest["upload_status"] = "ACTION_REQUIRED"
    elif records and all(record.get("status") == "VERIFIED" for record in records):
        manifest["upload_status"] = (
            "UPLOAD_COMPLETE" if manifest.get("status") == "COMPLETED" else "PENDING_UPLOAD"
        )
    elif any(record.get("status") == "UPLOADING" for record in records):
        manifest["upload_status"] = "UPLOADING"
    elif records:
        manifest["upload_status"] = "UPLOAD_RETRY" if any(
            record.get("status") == "UPLOAD_RETRY" for record in records
        ) else "PENDING_UPLOAD"


def _persist_upload_progress(path: Path, working: dict[str, Any]) -> None:
    """Merge worker progress into the latest transaction manifest under a shared lock."""
    path = Path(path)
    with manifest_lock(path):
        latest = json.loads(path.read_text(encoding="utf-8"))
        working_files: dict[str, dict[str, Any]] = working.setdefault("upload_files", {})
        latest_files: dict[str, dict[str, Any]] = latest.setdefault("upload_files", {})

        for relative_path, persisted_record in latest_files.items():
            working_files.setdefault(relative_path, dict(persisted_record))

        for relative_path, progress_record in working_files.items():
            persisted_record = latest_files.setdefault(relative_path, {})
            if persisted_record.get("status") == "VERIFIED" and progress_record.get("status") != "VERIFIED":
                progress_record.update(persisted_record)
            else:
                persisted_record.update(progress_record)

        working["status"] = latest.get("status", working.get("status"))
        _refresh_upload_status(latest)
        working["upload_status"] = latest.get("upload_status")
        write_json_atomic(path, latest)


class DriveSyncWorker:
    """Run Drive pool maintenance and upload retries away from Tk's event loop."""

    def __init__(
        self,
        photos_root: Path,
        client: GoogleDriveClient,
        pool: DriveSlotPool,
        interval_seconds: int = 8,
    ) -> None:
        self.photos_root = Path(photos_root)
        self.client = client
        self.pool = pool
        self.interval_seconds = interval_seconds
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            name="photobooth-drive-sync",
            daemon=True,
        )

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def kick(self) -> None:
        self._wake.set()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()

    def _run(self) -> None:
        while not self._stop.is_set():
            self.pool.recover_incomplete_claims()
            self._process_pending_assignments()
            self._process_pending_uploads()
            if self.pool.ready_count < self.pool.target_ready:
                try:
                    self.pool.refresh(self.client)
                except (DriveApiError, OSError, ValueError) as error:
                    self.pool.record_refresh_error(error)
            self._wake.wait(self.interval_seconds)
            self._wake.clear()

    def _process_pending_assignments(self) -> None:
        for slot in self.pool.pending_assignments():
            if not slot.transaction_id:
                continue
            try:
                self.client.assign_slot(
                    slot.folder_id,
                    slot.transaction_id,
                    self.pool.booth_id,
                    slot.slot_key,
                )
                self.pool.mark_assigned(slot.folder_id)
            except DriveApiError as error:
                self.pool.record_refresh_error(error)

    def _process_pending_uploads(self) -> None:
        try:
            manifests = list(self.photos_root.glob("*/manifest.json"))
        except OSError:
            return
        for manifest_path in manifests:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                upload_status = manifest.get("upload_status")
                if upload_status in {"UPLOAD_COMPLETE", "LOCAL_ONLY", "ACTION_REQUIRED"}:
                    continue
                if manifest.get("drive_folder_id"):
                    sync_manifest(manifest_path, self.client)
            except (DriveApiError, OSError, ValueError, TypeError, json.JSONDecodeError):
                continue
